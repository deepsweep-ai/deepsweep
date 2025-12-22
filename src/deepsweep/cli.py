"""
DeepSweep CLI - Security Gateway for AI Coding Assistants.

Design Standards:
- NO EMOJIS
- Optimistic messaging
- Vibe coding hooks in visible text
"""

import sys
from pathlib import Path

import click

from deepsweep import __version__
from deepsweep.constants import DOCS_URL, SEVERITY_ORDER
from deepsweep.exceptions import DeepSweepError
from deepsweep.output import OutputConfig, OutputFormatter
from deepsweep.validator import validate_path


@click.group(invoke_without_command=True)
@click.version_option(__version__, prog_name="deepsweep")
@click.pass_context
def main(ctx: click.Context) -> None:
    """
    DeepSweep - Security for the vibe coding era.

    Validate AI coding assistant configurations before execution.
    Covers Cursor, Copilot, Claude Code, Windsurf, and MCP servers.

    "Vibe coding" is Collins' Word of the Year 2025. 25% of YC W25
    startups have 95% AI-generated codebases. DeepSweep ensures
    your AI assistant setup is secure.

    Quick start:

    \b
        deepsweep validate .

    Learn more: https://docs.deepsweep.ai
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option(
    "--format", "-f", "output_format",
    type=click.Choice(["text", "json", "sarif"]),
    default="text",
    help="Output format",
)
@click.option(
    "--output", "-o", "output_file",
    type=click.Path(),
    default=None,
    help="Output file (default: stdout)",
)
@click.option(
    "--no-color",
    is_flag=True,
    help="Disable colored output",
)
@click.option(
    "--fail-on",
    type=click.Choice(["critical", "high", "medium", "low"]),
    default="high",
    help="Exit non-zero if findings at or above this severity",
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Show verbose output",
)
def validate(
    path: str,
    output_format: str,
    output_file: str | None,
    no_color: bool,
    fail_on: str,
    verbose: bool,
) -> None:
    """
    Validate AI assistant configurations in PATH.

    Examples:

    \b
        deepsweep validate .
        deepsweep validate ./my-project --fail-on critical
        deepsweep validate . --format sarif --output report.sarif
    """
    config = OutputConfig(
        use_color=not no_color,
        verbose=verbose,
    )
    formatter = OutputFormatter(config)

    try:
        result = validate_path(Path(path))
    except DeepSweepError as e:
        click.echo(f"[FAIL] {e.message}", err=True)
        sys.exit(1)

    # Generate output
    if output_format == "json":
        output = formatter.format_json_output(result)
    elif output_format == "sarif":
        output = formatter.format_sarif_output(result)
    else:
        # Text format
        lines = [formatter.format_header(__version__)]
        lines.append(formatter.format_validation_start(path, result.pattern_count))

        # File results
        for file_result in result.files:
            if file_result.skipped:
                lines.append(formatter.format_file_skip(
                    file_result.path,
                    file_result.skip_reason or "unknown"
                ))
            elif file_result.has_findings:
                for finding in file_result.findings:
                    lines.append(formatter.format_finding(finding))
            else:
                lines.append(formatter.format_file_pass(file_result.path))

        lines.append(formatter.format_summary(result))
        lines.append(formatter.format_next_steps(result))

        output = "\n".join(lines)

    # Write output
    if output_file:
        Path(output_file).write_text(output)
        click.echo(f"[PASS] Results written to {output_file}")
    else:
        click.echo(output)

    # Exit code based on --fail-on
    if result.has_findings:
        threshold = SEVERITY_ORDER.index(fail_on)
        for finding in result.all_findings:
            finding_level = SEVERITY_ORDER.index(finding.severity.value.lower())
            if finding_level >= threshold:
                sys.exit(1)

    sys.exit(0)


@main.command()
@click.option(
    "--output", "-o",
    default="badge.svg",
    help="Output file path",
)
@click.option(
    "--format", "-f", "output_format",
    type=click.Choice(["svg", "json", "markdown"]),
    default="svg",
    help="Output format",
)
def badge(output: str, output_format: str) -> None:
    """
    Generate security badge for README.

    Examples:

    \b
        deepsweep badge
        deepsweep badge --output my-badge.svg
        deepsweep badge --format markdown
    """
    result = validate_path(Path("."))
    score = result.score
    grade = result.grade_letter

    # Determine color
    if score >= 90:
        color = "4ade80"
    elif score >= 70:
        color = "f59e0b"
    else:
        color = "ef4444"

    if output_format == "json":
        import json
        content = json.dumps({
            "schemaVersion": 1,
            "label": "DeepSweep",
            "message": f"{score}/100 ({grade})",
            "color": color,
        }, indent=2)
    elif output_format == "markdown":
        url = f"https://img.shields.io/badge/DeepSweep-{score}%2F100%20({grade})-{color}"
        content = f"[![DeepSweep]({url})](https://deepsweep.ai)"
    else:
        # SVG - fetch from shields.io
        import urllib.request
        url = f"https://img.shields.io/badge/DeepSweep-{score}%2F100%20({grade})-{color}"
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                content = response.read().decode("utf-8")
        except Exception:
            # Fallback to simple SVG
            content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="120" height="20">
  <rect width="120" height="20" fill="#{color}"/>
  <text x="60" y="14" text-anchor="middle" fill="white" font-size="11">DeepSweep {score}/100</text>
</svg>"""

    Path(output).write_text(content)
    click.echo(f"[PASS] Badge saved to {output}")
    click.echo(f"[INFO] Score: {score}/100 ({grade})")


@main.command()
def patterns() -> None:
    """List all detection patterns."""
    from deepsweep.patterns import get_all_patterns

    all_patterns = get_all_patterns()

    click.echo(f"\nDeepSweep Detection Patterns ({len(all_patterns)} total)\n")
    click.echo("-" * 60)

    for pattern in all_patterns:
        cve = f" ({pattern.cve})" if pattern.cve else ""
        click.echo(f"\n{pattern.id}: {pattern.name}{cve}")
        click.echo(f"  Severity: {pattern.severity.value}")
        click.echo(f"  Files: {', '.join(pattern.file_types)}")
        if pattern.owasp:
            click.echo(f"  OWASP: {pattern.owasp}")


@main.command()
def version() -> None:
    """Show version information."""
    click.echo(f"deepsweep {__version__}")


if __name__ == "__main__":
    main()
