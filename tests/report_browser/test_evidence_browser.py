"""Opt-in offline viewer acceptance; normal validation does not launch browsers."""

import json

import pytest

from ai_rules.rule_loader_eval.evidence_report import (
    build_payload,
    create_selection,
    write_generation,
)

pytestmark = pytest.mark.browser


@pytest.fixture
def generation(tmp_path):
    from tests.rule_loader_eval.test_evidence_report import make_run

    first = make_run(tmp_path)
    second = make_run(tmp_path, model="openai-gpt-6-luna", outcomes=("pass", "pass", "agent-miss"))
    return write_generation(build_payload(create_selection([first, second])), tmp_path / "reports")


@pytest.mark.parametrize("width", [360, 1440])
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_offline_selection_sort_drilldown_print(generation, width, theme):
    playwright = pytest.importorskip("playwright.sync_api")
    with playwright.sync_playwright() as manager:
        browser = manager.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": 900}, color_scheme=theme)
        errors, requests = [], []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.route("http://**/*", lambda route: (requests.append(route.request.url), route.abort()))
        page.route(
            "https://**/*", lambda route: (requests.append(route.request.url), route.abort())
        )
        page.goto((generation / "report.html").as_uri())
        assert page.locator("#summary-table tbody tr").count() == 2
        page.locator("#summary-table button", has_text="Mean AI Credits").click()
        assert page.locator("#summary-table th[aria-sort]").count() == 1
        assert page.locator("#summary-table tbody tr").count() == 2
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
        original = page.locator("#report-data").text_content()
        page.select_option("#model-filter", "openai-gpt-6-luna")
        assert page.locator("#summary-table tbody tr").count() == 1
        page.locator("#fixture-table button").first.click()
        assert page.locator("dialog").is_visible()
        assert page.locator("#dialog-content details").count() == 3
        page.click("#close-dialog")
        page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        assert page.locator("#summary-table tbody tr").count() == 2
        assert page.locator("#print-evidence details").count() == 6
        page.evaluate("window.dispatchEvent(new Event('afterprint'))")
        assert page.locator("#summary-table tbody tr").count() == 1
        assert page.locator("#report-data").text_content() == original
        assert json.loads(original)["totals"]["observed"] == 6
        page.check("#select-all")
        page.uncheck("#select-all")
        assert page.locator("#summary-table tbody tr").count() == 0
        assert "No measurements" in page.locator("#charts").text_content()
        assert not requests and not errors
        browser.close()


def test_print_table_words_do_not_split(generation):
    playwright = pytest.importorskip("playwright.sync_api")
    with playwright.sync_playwright() as manager:
        browser = manager.chromium.launch()
        page = browser.new_page(viewport={"width": 1031, "height": 900})
        page.goto((generation / "report.html").as_uri())
        page.emulate_media(media="print")
        assert page.evaluate(
            "Array.from(document.querySelectorAll('table')).every(table => table.getBoundingClientRect().right <= innerWidth + 1)"
        )
        broken = page.evaluate("""() => {
            const broken = [];
            for (const cell of document.querySelectorAll('th,td')) {
                const walker = document.createTreeWalker(cell, NodeFilter.SHOW_TEXT);
                for (let node; (node=walker.nextNode());) {
                    const words = node.parentElement.closest('code') ? /\\S+/g : /[^\\s\\-:]+/g;
                    for (const match of node.data.matchAll(words)) {
                        const range=document.createRange();
                        range.setStart(node,match.index); range.setEnd(node,match.index+match[0].length);
                        if (new Set([...range.getClientRects()].filter(r=>r.width>0).map(r=>Math.round(r.top))).size>1) broken.push(match[0]);
                    }
                }
            }
            return broken;
        }""")
        assert not broken, broken
        browser.close()
