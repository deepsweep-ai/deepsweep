"""
Report generation utilities.

Supports multiple output formats:
- Text (terminal output)
- JSON (structured data)
- SARIF (GitHub Security integration)
- GitHub Actions job summary
"""

from __future__ import annotations

import json
from typing import Dict, Any

from deepsweep_ai.scanner import ScanResult, Severity


def to_json(result: ScanResult, pretty: bool = True) -> str:
    """Convert scan result to JSON."""
    indent = 2 if pretty else None
    return json.dumps(result.to_dict(), indent=indent)


def to_sarif(result: ScanResult) -> str:
    """Convert scan result to SARIF format for GitHub Security."""
    return json.dumps(result.to_sarif(), indent=2)


def to_github_summary(result: ScanResult) -> str:
    """Generate GitHub Actions job summary markdown - professional format."""
    status = "PASS" if result.safe else "FAIL"
    status_text = "No issues" if result.safe else f"{result.blocked_count} issue(s) found"

    critical = sum(1 for f in result.findings if f.severity == Severity.CRITICAL)
    high = sum(1 for f in result.findings if f.severity == Severity.HIGH)
    medium = sum(1 for f in result.findings if f.severity == Severity.MEDIUM)
    low = sum(1 for f in result.findings if f.severity == Severity.LOW)

    summary = f"""## DeepSweep Security Gateway

**Status:** {status}

| Metric | Value |
|--------|-------|
| Score | {result.score}/100 |
| Files Validated | {result.files_scanned} |
| Critical | {critical} |
| High | {high} |
| Medium | {medium} |
| Low | {low} |
| Duration | {result.duration_ms}ms |

"""

    if result.findings:
        summary += "### Findings\n\n"
        summary += "| Severity | ID | Title | File |\n"
        summary += "|----------|-----|-------|------|\n"

        for finding in result.findings[:10]:  # Limit to 10
            sev = finding.severity.value.upper()
            summary += f"| {sev} | {finding.id} | {finding.title} | {finding.file_path} |\n"

        if len(result.findings) > 10:
            summary += f"\n*...and {len(result.findings) - 10} more findings*\n"

    summary += """
---
*Validated by [DeepSweep](https://deepsweep.ai)*
"""

    return summary


def to_slack_message(result: ScanResult, channel: str = None) -> Dict[str, Any]:
    """Generate Slack Block Kit message - professional styling."""
    status = "passed" if result.safe else "failed"
    color = "#22C55E" if result.safe else "#EF4444"

    critical = sum(1 for f in result.findings if f.severity == Severity.CRITICAL)
    high = sum(1 for f in result.findings if f.severity == Severity.HIGH)

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "DeepSweep Security Gateway",
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Status:* {status.upper()}"},
                {"type": "mrkdwn", "text": f"*Score:* {result.score}/100"},
                {"type": "mrkdwn", "text": f"*Critical:* {critical}"},
                {"type": "mrkdwn", "text": f"*High:* {high}"},
                {"type": "mrkdwn", "text": f"*Files:* {result.files_scanned}"},
                {"type": "mrkdwn", "text": f"*Duration:* {result.duration_ms}ms"},
            ]
        },
    ]

    if result.findings:
        findings_text = []
        for finding in result.findings[:5]:
            findings_text.append(
                f"[{finding.severity.value.upper()}] {finding.id}: {finding.title}"
            )
        if len(result.findings) > 5:
            findings_text.append(f"...and {len(result.findings) - 5} more")

        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Findings:*\n" + "\n".join(findings_text)
            }
        })

    blocks.append({
        "type": "context",
        "elements": [
            {"type": "mrkdwn", "text": "<https://deepsweep.ai|DeepSweep>"}
        ]
    })

    message = {
        "attachments": [{
            "color": color,
            "blocks": blocks
        }]
    }

    if channel:
        message["channel"] = channel

    return message
