"""Output formatters for evaluation results."""

import json
from dataclasses import asdict
from datetime import datetime
from typing import Any

from .models import (
    EvaluationReport,
    Severity,
)


def format_markdown(report: EvaluationReport) -> str:
    """Format evaluation report as markdown.

    Args:
        report: The evaluation report.

    Returns:
        Markdown formatted string.
    """
    eval_result = report.evaluation
    lines = [
        "# Prompt Evaluation Report",
        "",
        f"**Date:** {eval_result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Model:** {eval_result.model_used}",
        f"**Score:** {eval_result.total_score:.1f}/{eval_result.max_score:.1f} ({eval_result.grade})",
        "",
        "---",
        "",
        "## Original Prompt",
        "",
        "```",
        eval_result.original_prompt,
        "```",
        "",
        "---",
        "",
        "## Dimension Scores",
        "",
        "| Dimension | Score | Points | Max |",
        "|-----------|-------|--------|-----|",
    ]

    for ds in eval_result.dimension_scores:
        lines.append(f"| {ds.dimension} | {ds.raw_score}/10 | {ds.points:.1f} | {ds.max_points} |")

    lines.extend(["", "---", "", "## Issues Found", ""])

    if eval_result.all_issues:
        for issue in eval_result.all_issues:
            severity_emoji = {
                Severity.CRITICAL: "🔴",
                Severity.HIGH: "🟠",
                Severity.MEDIUM: "🟡",
                Severity.LOW: "🟢",
            }.get(issue.severity, "⚪")
            lines.append(
                f'- {severity_emoji} **[{issue.dimension}]** `"{issue.quote}"` - {issue.problem}'
            )
    else:
        lines.append("*No issues found.*")

    # Recommendations
    lines.extend(["", "---", "", "## Recommendations", ""])
    has_recommendations = False
    for ds in eval_result.dimension_scores:
        if ds.recommendations:
            has_recommendations = True
            lines.append(f"### {ds.dimension}")
            for rec in ds.recommendations:
                lines.append(f"- {rec}")
            lines.append("")

    if not has_recommendations:
        lines.append("*No specific recommendations.*")

    # Improved prompt
    if report.improved:
        lines.extend(
            [
                "",
                "---",
                "",
                "## Improved Prompt",
                "",
                "```",
                report.improved.improved_text,
                "```",
                "",
            ]
        )

        if report.improved.changes_made:
            lines.extend(["### Changes Made", ""])
            for change in report.improved.changes_made:
                lines.append(f"- {change}")
            lines.append("")

        if report.improved.priority_alignment:
            lines.extend(["### Priority Alignment", ""])
            for priority, changes in report.improved.priority_alignment.items():
                if changes:
                    lines.append(f"**{priority}:**")
                    for change in changes:
                        lines.append(f"  - {change}")
            lines.append("")

        if report.improved.explanation:
            lines.extend(
                [
                    "### Summary",
                    "",
                    report.improved.explanation,
                ]
            )

    return "\n".join(lines)


def format_json(report: EvaluationReport, indent: int = 2) -> str:
    """Format evaluation report as JSON.

    Args:
        report: The evaluation report.
        indent: JSON indentation level.

    Returns:
        JSON formatted string.
    """

    def serialize(obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Severity):
            return obj.value
        if hasattr(obj, "__dataclass_fields__"):
            return {k: serialize(v) for k, v in asdict(obj).items()}
        if isinstance(obj, list):
            return [serialize(item) for item in obj]
        if isinstance(obj, dict):
            return {k: serialize(v) for k, v in obj.items()}
        return obj

    data = serialize(report)
    return json.dumps(data, indent=indent)


def format_html(report: EvaluationReport) -> str:
    """Format evaluation report as standalone HTML.

    Args:
        report: The evaluation report.

    Returns:
        HTML formatted string.
    """
    eval_result = report.evaluation

    # Build dimension rows
    dimension_rows = []
    for ds in eval_result.dimension_scores:
        percentage = (ds.raw_score / 10) * 100
        bar_color = _score_color(ds.raw_score)
        dimension_rows.append(f"""
        <tr>
            <td>{ds.dimension}</td>
            <td>{ds.raw_score}/10</td>
            <td>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {percentage}%; background: {bar_color};"></div>
                </div>
            </td>
            <td>{ds.points:.1f}/{ds.max_points}</td>
        </tr>""")

    # Build issues list
    issues_html = ""
    if eval_result.all_issues:
        issue_items = []
        for issue in eval_result.all_issues:
            severity_class = issue.severity.value
            issue_items.append(f"""
            <li class="issue {severity_class}">
                <span class="badge">{issue.dimension}</span>
                <code>"{_escape_html(issue.quote)}"</code>
                <span class="problem">{_escape_html(issue.problem)}</span>
            </li>""")
        issues_html = f"<ul class='issues-list'>{''.join(issue_items)}</ul>"
    else:
        issues_html = "<p class='no-issues'>No issues found.</p>"

    # Build improved prompt section
    improved_html = ""
    if report.improved:
        changes_html = ""
        if report.improved.changes_made:
            changes_items = "".join(
                f"<li>{_escape_html(c)}</li>" for c in report.improved.changes_made
            )
            changes_html = f"<h3>Changes Made</h3><ul>{changes_items}</ul>"

        improved_html = f"""
        <section class="improved-prompt">
            <h2>Improved Prompt</h2>
            <pre class="prompt-text">{_escape_html(report.improved.improved_text)}</pre>
            {changes_html}
            {f'<p class="explanation">{_escape_html(report.improved.explanation)}</p>' if report.improved.explanation else ""}
        </section>"""

    grade_color = _grade_color(eval_result.grade)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prompt Evaluation Report</title>
    <style>
        :root {{
            --bg: #1a1a2e;
            --surface: #16213e;
            --text: #eaeaea;
            --text-muted: #a0a0a0;
            --border: #0f3460;
            --accent: #e94560;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 2rem;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1, h2, h3 {{ margin: 1.5rem 0 1rem; }}
        h1 {{ color: var(--accent); }}
        .meta {{ color: var(--text-muted); margin-bottom: 1rem; }}
        .score-badge {{
            display: inline-block;
            font-size: 2rem;
            font-weight: bold;
            padding: 0.5rem 1.5rem;
            border-radius: 8px;
            background: {grade_color};
            color: white;
            margin: 1rem 0;
        }}
        section {{
            background: var(--surface);
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1.5rem 0;
            border: 1px solid var(--border);
        }}
        pre.prompt-text {{
            background: var(--bg);
            padding: 1rem;
            border-radius: 4px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }}
        th, td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        th {{ color: var(--text-muted); font-weight: 600; }}
        .progress-bar {{
            background: var(--bg);
            border-radius: 4px;
            height: 8px;
            width: 100px;
            overflow: hidden;
        }}
        .progress-fill {{ height: 100%; transition: width 0.3s; }}
        .issues-list {{ list-style: none; }}
        .issue {{
            padding: 0.75rem;
            margin: 0.5rem 0;
            border-radius: 4px;
            border-left: 4px solid;
        }}
        .issue.critical {{ border-color: #e74c3c; background: rgba(231,76,60,0.1); }}
        .issue.high {{ border-color: #e67e22; background: rgba(230,126,34,0.1); }}
        .issue.medium {{ border-color: #f1c40f; background: rgba(241,196,15,0.1); }}
        .issue.low {{ border-color: #2ecc71; background: rgba(46,204,113,0.1); }}
        .badge {{
            display: inline-block;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            background: var(--border);
            margin-right: 0.5rem;
        }}
        code {{ background: var(--bg); padding: 0.2rem 0.4rem; border-radius: 3px; }}
        .no-issues {{ color: #2ecc71; font-style: italic; }}
        ul {{ margin: 1rem 0; padding-left: 1.5rem; }}
        li {{ margin: 0.5rem 0; }}
        .explanation {{ font-style: italic; color: var(--text-muted); margin-top: 1rem; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Prompt Evaluation Report</h1>
        <p class="meta">
            {eval_result.timestamp.strftime("%Y-%m-%d %H:%M:%S")} | Model: {eval_result.model_used}
        </p>
        <div class="score-badge">{eval_result.grade} - {eval_result.total_score:.1f}/{eval_result.max_score:.1f}</div>

        <section>
            <h2>Original Prompt</h2>
            <pre class="prompt-text">{_escape_html(eval_result.original_prompt)}</pre>
        </section>

        <section>
            <h2>Dimension Scores</h2>
            <table>
                <thead>
                    <tr><th>Dimension</th><th>Score</th><th>Progress</th><th>Points</th></tr>
                </thead>
                <tbody>
                    {"".join(dimension_rows)}
                </tbody>
            </table>
        </section>

        <section>
            <h2>Issues Found</h2>
            {issues_html}
        </section>

        {improved_html}
    </div>
</body>
</html>"""


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _score_color(score: int) -> str:
    """Get color for score value."""
    if score >= 8:
        return "#2ecc71"
    elif score >= 6:
        return "#f1c40f"
    elif score >= 4:
        return "#e67e22"
    else:
        return "#e74c3c"


def _grade_color(grade: str) -> str:
    """Get color for letter grade."""
    colors = {
        "A": "#2ecc71",
        "B": "#3498db",
        "C": "#f1c40f",
        "D": "#e67e22",
        "F": "#e74c3c",
    }
    return colors.get(grade, "#95a5a6")
