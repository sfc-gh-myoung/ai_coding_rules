"""Browser verification of the compliance report's sort engine and tabs.

Run with playwright isolated (it imports no project code):
    uvx --with playwright python scripts/verify_report_browser.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# playwright is intentionally NOT a project dependency: this script imports no
# project code, so it runs isolated per 200b-python-environment-tooling.md.
from playwright.sync_api import sync_playwright  # ty: ignore[unresolved-import]

REPORT = Path(__file__).resolve().parent.parent / "reports" / "llm-protocol-compliance-report.html"

failures: list[str] = []


def check(name: str, got: object, want: object) -> None:
    if got == want:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}\n        got  {got!r}\n        want {want!r}")
        failures.append(name)


def check_true(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}{'  ' + detail if detail else ''}")
        failures.append(name)


def main() -> int:
    if not REPORT.exists():
        print(f"report not found: {REPORT}")
        return 1

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on(
            "console",
            lambda m: errors.append(f"console.{m.type}: {m.text}") if m.type == "error" else None,
        )
        page.goto(REPORT.as_uri())
        page.wait_for_load_state("load")
        page.wait_for_timeout(1200)  # Alpine init + vega embeds

        print("\n-- 1. page loads without JS errors --")
        check_true("no pageerror / console.error", not errors, "; ".join(errors[:3]))

        print("\n-- 2. all eight tabs render when selected --")
        tabs = [
            "overview",
            "protocol",
            "taxonomy",
            "results",
            "fixtures",
            "performance",
            "model-effort",
            "model-selection",
        ]
        for tab in tabs:
            page.evaluate(f"document.querySelector('a[href=\"#{tab}\"]').click()")
            page.wait_for_timeout(120)
            visible = page.evaluate(
                f"(() => {{ const el = document.getElementById('{tab}');"
                " return !!el && el.offsetParent !== null; })()"
            )
            check_true(f"tab '{tab}' visible after click", visible)

        print("\n-- 3. Model Selection sub-tabs --")
        page.evaluate("document.querySelector('a[href=\"#model-selection\"]').click()")
        page.wait_for_timeout(200)
        for sub in ["selection-guidance", "selection-families", "selection-ai-analysis"]:
            shown = page.evaluate(
                f"(() => {{ const el = document.getElementById('{sub}'); return !!el; }})()"
            )
            check_true(f"sub-panel '{sub}' present", shown)

        print("\n-- 4. legacy hash aliases resolve to merged tab --")
        for legacy, sub in [
            ("sovereignty", "selection-families"),
            ("recommendations", "selection-guidance"),
            ("ai-insights", "selection-ai-analysis"),
        ]:
            page.evaluate(f"window.location.hash = '#{legacy}'")
            page.wait_for_timeout(250)
            state = page.evaluate(
                "(() => { const el = document.getElementById('model-selection');"
                " return el && el.offsetParent !== null; })()"
            )
            sub_visible = page.evaluate(
                f"(() => {{ const el = document.getElementById('{sub}');"
                " return !!el && el.offsetParent !== null; })()"
            )
            check_true(f"#{legacy} -> model-selection visible", state)
            check_true(f"#{legacy} -> {sub} visible", sub_visible)

        print("\n-- 5. tie-breaker subscript arrows actually render --")
        page.evaluate("document.querySelector('a[href=\"#performance\"]').click()")
        page.wait_for_timeout(200)
        # Click Pass Rate (a numeric column) on the Performance table.
        page.evaluate(
            "(() => { const t = document.getElementById('perf-table');"
            " const th = t.querySelectorAll('th[data-sort-type]')[1]; th.click(); })()"
        )
        page.wait_for_timeout(200)
        ranks = page.evaluate(
            "(() => Array.from(document.querySelectorAll('#perf-table th[data-sort-rank]'))"
            ".map(th => th.getAttribute('data-sort-rank')))()"
        )
        check_true("perf table emits data-sort-rank after click", len(ranks) > 0, f"ranks={ranks}")

        arrow = page.evaluate(
            "(() => { const th = document.querySelector('#perf-table th[data-sort-rank=\"2\"]');"
            " if (!th) return null;"
            " return getComputedStyle(th, '::after').content; })()"
        )
        check_true(
            "rank-2 header renders a subscript arrow glyph",
            bool(arrow) and arrow not in ("none", "normal") and ("\u2082" in arrow),
            f"content={arrow!r}",
        )

        primary_arrow = page.evaluate(
            "(() => { const th = document.querySelector("
            "'#perf-table th.sorted-asc:not([data-sort-rank]),"
            " #perf-table th.sorted-desc:not([data-sort-rank])');"
            " if (!th) return null; return getComputedStyle(th, '::after').content; })()"
        )
        check_true(
            "primary header renders plain full-size arrow",
            bool(primary_arrow)
            and ("\u2191" in (primary_arrow or "") or "\u2193" in (primary_arrow or ""))
            and "\u2082" not in (primary_arrow or ""),
            f"content={primary_arrow!r}",
        )

        print("\n-- 6. chain genuinely breaks ties in the live DOM --")
        # Build a synthetic table carrying a chain, insert it, init it, and sort.
        result = page.evaluate("""
        (() => {
          const host = document.createElement('div');
          host.innerHTML = `
            <table id="tie-probe" class="data-table sortable-table compact" data-sort-fallback="2:asc,0:asc">
              <thead><tr>
                <th data-sort-type="text">Model</th>
                <th data-sort-type="number">Pass</th>
                <th data-sort-type="number">Turns</th>
              </tr></thead>
              <tbody>
                <tr><td>zeta</td><td>100</td><td>9</td></tr>
                <tr><td>alpha</td><td>100</td><td>4</td></tr>
                <tr><td>mid</td><td>100</td><td>4</td></tr>
                <tr><td>beta</td><td>95</td><td>1</td></tr>
              </tbody>
            </table>`;
          document.body.appendChild(host);
          const t = document.getElementById('tie-probe');
          initSortableTable(t);
          t.querySelectorAll('th[data-sort-type]')[1].click();
          const order = Array.from(t.tBodies[0].rows).map(r => r.cells[0].textContent);
          const ranks = Array.from(t.querySelectorAll('th[data-sort-rank]'))
            .map(th => th.cellIndex + ':' + th.getAttribute('data-sort-rank'));
          return {order, ranks};
        })()
        """)
        check(
            "ties broken by turns asc then model asc",
            result["order"],
            ["alpha", "mid", "zeta", "beta"],
        )
        check("tie-breaker ranks assigned to cols 2 then 0", result["ranks"], ["0:3", "2:2"])

        print("\n-- 7. numeric columns sort numerically, not lexically --")
        num = page.evaluate("""
        (() => {
          const host = document.createElement('div');
          host.innerHTML = `
            <table id="num-probe" class="data-table sortable-table compact">
              <thead><tr><th data-sort-type="text">M</th><th data-sort-type="number">V</th></tr></thead>
              <tbody>
                <tr><td>a</td><td>9</td></tr>
                <tr><td>b</td><td>10</td></tr>
                <tr><td>c</td><td>100</td></tr>
                <tr><td>d</td><td>2</td></tr>
              </tbody>
            </table>`;
          document.body.appendChild(host);
          const t = document.getElementById('num-probe');
          initSortableTable(t);
          t.querySelectorAll('th[data-sort-type]')[1].click();
          return Array.from(t.tBodies[0].rows).map(r => r.cells[1].textContent);
        })()
        """)
        check("first click on number col sorts descending", num, ["100", "10", "9", "2"])

        print("\n-- 8. charts rendered --")
        # Real container ids: passRateChart (Overview), scatter-chart (Performance),
        # effort-pareto-chart (Model Effort).
        painted = page.evaluate(
            "(() => ['passRateChart','scatter-chart','effort-pareto-chart'].map(id => {"
            " const el = document.getElementById(id);"
            " if (!el) return id + ':MISSING';"
            " return id + ':' + (el.querySelectorAll('svg, canvas').length ? 'painted' : 'empty');"
            "}))()"
        )
        for entry in painted:
            name, _, state = entry.partition(":")
            check(f"chart '{name}' painted", state, "painted")

        browser.close()

    print(
        f"\n{'ALL BROWSER CHECKS PASSED' if not failures else str(len(failures)) + ' CHECK(S) FAILED'}"
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
