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
from deepsweep.constants import SEVERITY_ORDER
from deepsweep.exceptions import DeepSweepError
from deepsweep.output import OutputConfig, OutputFormatter
from deepsweep.telemetry import get_telemetry_client
from deepsweep.validator import validate_path


def _show_first_run_notice() -> None:
    """Show first-run telemetry notice (optimistic messaging)."""
    notice = """
[INFO] DeepSweep uses a two-tier telemetry system:

  ESSENTIAL (Always Active):
  - Threat intelligence signals power community security
  - Pattern effectiveness tracking
  - Zero-day detection
  - Benefits all users

  OPTIONAL (You Control):
  - Product analytics for improvements
  - Activation and retention metrics
  - Feature usage patterns

  What we NEVER collect:
  - Your code or file contents
  - File paths or repository names
  - Personally identifiable information

  Disable optional analytics: deepsweep telemetry disable
  Fully offline mode: export DEEPSWEEP_OFFLINE=1

  Learn more: https://docs.deepsweep.ai/telemetry
"""
    click.echo(notice)


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
    # Show first-run notice
    telemetry = get_telemetry_client()
    if telemetry.config.first_run and ctx.invoked_subcommand not in ("telemetry", None):
        _show_first_run_notice()

    # Identify user for analytics
    telemetry.identify()

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
    telemetry = get_telemetry_client()
    config = OutputConfig(
        use_color=not no_color,
        verbose=verbose,
    )
    formatter = OutputFormatter(config)

    exit_code = 0
    result = None

    try:
        result = validate_path(Path(path))
    except DeepSweepError as e:
        click.echo(f"[FAIL] {e.message}", err=True)
        telemetry.track_error(
            command="validate",
            error_type=type(e).__name__,
            error_message=e.message,
        )
        telemetry.shutdown()
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
                exit_code = 1
                break

    # Track telemetry (both essential + optional tiers)
    telemetry.track_command(
        command="validate",
        exit_code=exit_code,
        findings_count=len(result.all_findings),
        pattern_count=result.pattern_count,
        output_format=output_format,
        score=result.score,
        grade=result.grade_letter,
    )
    telemetry.shutdown()

    sys.exit(exit_code)


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
    telemetry = get_telemetry_client()

    try:
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

        # Track telemetry
        telemetry.track_command(
            command="badge",
            exit_code=0,
            output_format=output_format,
        )
        telemetry.shutdown()

    except Exception as e:
        click.echo(f"[FAIL] Failed to generate badge: {e}", err=True)
        telemetry.track_error(
            command="badge",
            error_type=type(e).__name__,
            error_message=str(e),
        )
        telemetry.shutdown()
        sys.exit(1)


@main.command()
def patterns() -> None:
    """List all detection patterns."""
    from deepsweep.patterns import get_all_patterns

    telemetry = get_telemetry_client()

    try:
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

        # Track telemetry
        telemetry.track_command(
            command="patterns",
            exit_code=0,
            pattern_count=len(all_patterns),
        )
        telemetry.shutdown()

    except Exception as e:
        click.echo(f"[FAIL] Failed to list patterns: {e}", err=True)
        telemetry.track_error(
            command="patterns",
            error_type=type(e).__name__,
            error_message=str(e),
        )
        telemetry.shutdown()
        sys.exit(1)


@main.group()
def telemetry() -> None:
    """Manage telemetry settings."""
    pass


@telemetry.command(name="status")
def telemetry_status() -> None:
    """Show telemetry status."""
    from deepsweep.telemetry import TelemetryConfig

    config = TelemetryConfig()
    status = config.get_status()

    click.echo("\n[INFO] DeepSweep Telemetry Status\n")
    click.echo("Two-Tier System:")
    click.echo(f"  ESSENTIAL (Threat Intel): {'Offline' if status['offline_mode'] else 'Active'}")
    click.echo(f"  OPTIONAL (Analytics): {'Enabled' if status['enabled'] else 'Disabled'}")
    click.echo()
    click.echo(f"  Anonymous UUID: {status['uuid']}")
    click.echo(f"  Config file: {status['config_file']}")

    if status["offline_mode"]:
        click.echo("\n[INFO] Offline mode enabled - ALL telemetry disabled")
        click.echo("  Set DEEPSWEEP_OFFLINE=0 to re-enable")
    elif status["enabled"]:
        click.echo("\n[INFO] Both tiers active:")
        click.echo("  Essential: Threat intelligence (powers community security)")
        click.echo("  Optional: Product analytics (helps improve DeepSweep)")
        click.echo("\n  To disable optional analytics: deepsweep telemetry disable")
    else:
        click.echo("\n[INFO] Essential tier only (threat intelligence active)")
        click.echo("  Optional analytics disabled")
        click.echo("\n  To enable analytics: deepsweep telemetry enable")

    click.echo("\n  Learn more: https://docs.deepsweep.ai/telemetry\n")


@telemetry.command(name="enable")
def telemetry_enable() -> None:
    """Enable telemetry collection."""
    from deepsweep.telemetry import TelemetryConfig

    config = TelemetryConfig()
    config.enable()

    click.echo("[PASS] Telemetry enabled")
    click.echo("[INFO] Thank you for helping us improve DeepSweep")
    click.echo("[INFO] You can disable anytime with: deepsweep telemetry disable")


@telemetry.command(name="disable")
def telemetry_disable() -> None:
    """Disable telemetry collection."""
    from deepsweep.telemetry import TelemetryConfig

    config = TelemetryConfig()
    config.disable()

    click.echo("[PASS] Telemetry disabled")
    click.echo("[INFO] Your usage data will no longer be collected")
    click.echo("[INFO] You can re-enable anytime with: deepsweep telemetry enable")


@main.command()
def version() -> None:
    """Show version information."""
    click.echo(f"deepsweep {__version__}")


if __name__ == "__main__":
    main()
