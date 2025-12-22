"""
DeepSweep CLI - The #1 Security Gateway for Agentic AI Code Assistants

Usage:
    deepsweep scan [PATH]              # Validate directory (default: observe mode)
    deepsweep scan --enforce           # Validate and fail on critical findings
    deepsweep config                   # Show current configuration
    deepsweep config set KEY VALUE     # Set config value (telemetry, mode, api_key)
    deepsweep config get [KEY]         # Get config value(s)
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Optional, List, Tuple

import click

from deepsweep_ai import __version__
from deepsweep_ai.config import Config, Mode, Tier
from deepsweep_ai.scanner import Scanner, ScanResult, Severity, Finding
from deepsweep_ai.api_client import APIClient
from deepsweep_ai.pricing import check_tier_limits, get_upgrade_message
<<<<<<< HEAD
from deepsweep_ai.telemetry import (
    track_scan_completed,
    track_cli_invoked,
    track_scan_started,
    track_scan_failed,
    track_error,
    track_session_end,
    track_feature_used,
    track_auth_flow,
    initialize_telemetry,
    get_telemetry_stats,
    set_error_reporting_enabled,
    is_error_reporting_enabled,
    track_latency,
)
import traceback
import atexit
=======
from deepsweep_ai.telemetry import track_scan_completed, track_cli_invoked
>>>>>>> origin


# ============================================================================
# OUTPUT FORMATTING
# ============================================================================

# Check terminal capabilities
_isatty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
_no_color = os.environ.get('NO_COLOR') is not None
COLOR_ENABLED = _isatty and not _no_color


class Color:
    """ANSI color codes."""
    CRITICAL = "\033[91m" if COLOR_ENABLED else ""  # Bright red
    HIGH = "\033[31m" if COLOR_ENABLED else ""       # Red
    MEDIUM = "\033[33m" if COLOR_ENABLED else ""     # Yellow
    LOW = "\033[34m" if COLOR_ENABLED else ""        # Blue
    INFO = "\033[90m" if COLOR_ENABLED else ""       # Gray
    PASS = "\033[32m" if COLOR_ENABLED else ""       # Green
    FAIL = "\033[31m" if COLOR_ENABLED else ""       # Red
    BOLD = "\033[1m" if COLOR_ENABLED else ""
    DIM = "\033[2m" if COLOR_ENABLED else ""
    RESET = "\033[0m" if COLOR_ENABLED else ""


class Box:
    """Unicode box-drawing characters."""
    TL = "┌"  # Top-left
    TR = "┐"  # Top-right
    BL = "└"  # Bottom-left
    BR = "┘"  # Bottom-right
    H = "─"   # Horizontal
    V = "│"   # Vertical
    TT = "┬"  # Top-tee
    BT = "┴"  # Bottom-tee


def severity_color(severity: Severity) -> str:
    """Get ANSI color for severity level."""
    colors = {
        Severity.CRITICAL: Color.CRITICAL,
        Severity.HIGH: Color.HIGH,
        Severity.MEDIUM: Color.MEDIUM,
        Severity.LOW: Color.LOW,
        Severity.INFO: Color.INFO,
    }
    return colors.get(severity, Color.RESET)


def header(version: str) -> str:
    """Display gateway header."""
    lines = [
        f"{Color.BOLD}DeepSweep{Color.RESET} v{version}",
        f"{Color.DIM}Security Gateway for Agentic AI{Color.RESET}",
    ]
    return "\n".join(lines)


def divider(width: int = 72) -> str:
    """Horizontal divider line."""
    return Box.H * width


def format_finding(finding: Finding) -> str:
    """Format a single finding with colored bullet."""
    lines = []

    color = severity_color(finding.severity)
    sev_label = finding.severity.value.upper()

    # Bullet character (U+25CF) - NOT emoji
    bullet = "●"
    lines.append(f"{color}{bullet} {sev_label:8}{Color.RESET}  {finding.id}  {finding.title}")

    # File location (dimmed)
    location = finding.file_path
    if finding.line_number:
        location += f":{finding.line_number}"
    lines.append(f"{Color.DIM}            {location}{Color.RESET}")

    # Code snippet (dimmed, quoted)
    if finding.code_snippet:
        snippet = finding.code_snippet[:53] + "..." if len(finding.code_snippet) > 56 else finding.code_snippet
        lines.append(f'{Color.DIM}            "{snippet}"{Color.RESET}')

    # CVE references
    if finding.cve_ids:
        lines.append(f"            {', '.join(finding.cve_ids)}")

    return "\n".join(lines)


def key_value_box(pairs: List[Tuple[str, str]], width: int = 72) -> str:
    """Format key-value pairs in a box."""
    lines = []
    key_width = 10
    value_width = width - key_width - 5

    b = Box

    # Top border
    lines.append(f"{b.TL}{b.H * (key_width + 2)}{b.TT}{b.H * (value_width + 2)}{b.TR}")

    # Key-value rows
    for key, value in pairs:
        lines.append(f"{b.V} {key:<{key_width}} {b.V} {str(value):<{value_width}} {b.V}")

    # Bottom border
    lines.append(f"{b.BL}{b.H * (key_width + 2)}{b.BT}{b.H * (value_width + 2)}{b.BR}")

    return "\n".join(lines)


def status_label(passed: bool) -> str:
    """Format pass/fail status with color."""
    if passed:
        return f"{Color.PASS}PASS{Color.RESET}"
    return f"{Color.FAIL}FAIL{Color.RESET}"


def format_text_result(result: ScanResult, config: Config) -> str:
    """Format scan result as enterprise text output."""
    lines = []

    # Header
    lines.append(header(__version__))
    lines.append("")

    # Scan metadata
    lines.append(f"Target     {result.path_scanned}")
    lines.append(f"Mode       {result.mode.value.upper()}")
    lines.append("")

    # Findings section
    if result.findings:
        lines.append(divider())
        lines.append("")
        lines.append("FINDINGS")
        lines.append("")

        for finding in result.findings:
            lines.append(format_finding(finding))
            lines.append("")

    lines.append(divider())
    lines.append("")

    # Summary box
    critical = sum(1 for f in result.findings if f.severity == Severity.CRITICAL)
    high = sum(1 for f in result.findings if f.severity == Severity.HIGH)

    if result.findings:
        findings_detail = f"{len(result.findings)} ({critical} critical, {high} high)"
    else:
        findings_detail = "0"

    summary_pairs = [
        ("Status", status_label(result.safe)),
        ("Score", f"{result.score}/100"),
        ("Findings", findings_detail),
        ("Files", f"{result.files_scanned} validated"),
        ("Duration", f"{result.duration_ms}ms"),
    ]

    lines.append(key_value_box(summary_pairs))
    lines.append("")

    # Mode-specific footer
    if config.mode == Mode.OBSERVE:
        if result.safe:
            lines.append("OBSERVE MODE: No threats detected. Configuration validated.")
        else:
            lines.append("OBSERVE MODE: Findings reported, exit code 0.")
            lines.append("Use --enforce to exit 1 on critical/high findings.")
    else:
        if result.safe:
            lines.append("ENFORCE MODE: Validation passed.")
        else:
            lines.append(f"{Color.FAIL}ENFORCE MODE: Validation failed, exit code 1.{Color.RESET}")

    # Pro upsell (subtle, dimmed)
    if config.tier == Tier.FREE and result.findings:
        lines.append("")
        lines.append(f"{Color.DIM}Pro: Unlimited scans, SARIF export, API access.")
        lines.append(f"https://deepsweep.ai/pro{Color.RESET}")

    return "\n".join(lines)


# ============================================================================
# CLI COMMANDS
# ============================================================================

<<<<<<< HEAD
# Global exit code for session tracking
_exit_code = 0


def _on_exit():
    """Track session end on CLI exit."""
    track_session_end(__version__, _exit_code)


=======
>>>>>>> origin
@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version")
@click.pass_context
def main(ctx, version):
    """DeepSweep - The #1 Security Gateway for Agentic AI Code Assistants

    Intercept and validate AI assistant configurations before execution.
    Aligned with OWASP Top 10 for Agentic AI Applications.
    """
<<<<<<< HEAD
    # Initialize telemetry (tracks install on first run)
    initialize_telemetry(__version__)

    # Register exit handler for session tracking
    atexit.register(_on_exit)

    if version:
        track_cli_invoked(__version__, "version")
=======
    if version:
>>>>>>> origin
        print(f"DeepSweep v{__version__}")
        return

    if ctx.invoked_subcommand is None:
<<<<<<< HEAD
        track_cli_invoked(__version__, "help")
=======
>>>>>>> origin
        print(header(__version__))
        print()
        print("Run 'deepsweep scan' to validate current directory")
        print("Run 'deepsweep --help' for all commands")


@main.command()
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("--enforce", is_flag=True, help="Enable enforce mode (exit 1 on critical/high)")
@click.option("--format", "output_format", type=click.Choice(["text", "json", "sarif"]), default="text")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--quiet", "-q", is_flag=True, help="Minimal output")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--api-key", envvar="DEEPSWEEP_API_KEY", help="API key for Pro features")
def scan(path: str, enforce: bool, output_format: str, output: Optional[str],
         quiet: bool, verbose: bool, api_key: Optional[str]):
    """
    Validate directory for AI coding assistant security issues.

    By default runs in OBSERVE mode (report only, exit 0).
    Use --enforce to exit 1 on critical/high severity findings.

    Examples:

        deepsweep scan                    # Validate current directory
        deepsweep scan ./my-project       # Validate specific directory
        deepsweep scan --enforce          # Fail on critical findings
        deepsweep scan --format json      # JSON output
        deepsweep scan --format sarif -o results.sarif  # SARIF for GitHub
    """
<<<<<<< HEAD
    global _exit_code

    # Track command invocation
    track_cli_invoked(__version__, "scan")

=======
>>>>>>> origin
    # Load config
    config = Config.load()
    config.mode = Mode.ENFORCE if enforce else Mode.OBSERVE
    config.output_format = output_format
    config.verbose = verbose
    config.quiet = quiet
<<<<<<< HEAD
    mode_str = "enforce" if enforce else "observe"
=======
>>>>>>> origin

    if api_key:
        config.api_key = api_key

    # Check tier limits
    tier_ok, tier_msg = check_tier_limits(config)
    if not tier_ok:
        print(f"Warning: {tier_msg}")
        print(get_upgrade_message())
<<<<<<< HEAD
        _exit_code = 1
=======
>>>>>>> origin
        sys.exit(1)

    # Print header for text mode
    if not quiet and output_format == "text":
        print(header(__version__))
        print()
        mode_label = "ENFORCE" if enforce else "OBSERVE"
        print(f"Validating {path} in {mode_label} mode")
        print()

<<<<<<< HEAD
    # Track scan started (for funnel analysis)
    track_scan_started(__version__, mode_str)

    # Track feature usage
    if output_format != "text":
        track_feature_used(__version__, f"output_format_{output_format}")
    if enforce:
        track_feature_used(__version__, "enforce_mode")

    # Run scan with latency tracking
    try:
        with track_latency() as timer:
            scanner = Scanner(config)
            result = scanner.scan(path)
        scan_success = True
    except Exception as e:
        # Track scan failure
        track_scan_failed(
            cli_version=__version__,
            error_type=type(e).__name__,
            duration_ms=0,
            mode=mode_str,
        )
        track_error(
            cli_version=__version__,
            error_type=type(e).__name__,
            command="scan",
            stack_trace=traceback.format_exc(),
            exit_code=1,
        )
        if verbose:
            print(f"Scan error: {e}")
        _exit_code = 1
        sys.exit(1)
=======
    # Run scan
    scanner = Scanner(config)
    result = scanner.scan(path)
>>>>>>> origin

    # Output results
    if output_format == "json":
        output_text = json.dumps(result.to_dict(), indent=2)
    elif output_format == "sarif":
        output_text = json.dumps(result.to_sarif(), indent=2)
    else:
        output_text = format_text_result(result, config)

    # Write output
    if output:
        Path(output).write_text(output_text)
        if not quiet:
            print(f"Results written to {output}")
    else:
        print(output_text)

    # Report to API (if key provided)
    if config.api_key:
        try:
            client = APIClient(config)
            client.report_scan(result)
        except Exception as e:
            if verbose:
                print(f"API report failed: {e}")

<<<<<<< HEAD
    # Calculate exit code
    exit_code = 1 if (enforce and not result.safe) else 0
    _exit_code = exit_code

    # Track telemetry with enhanced metrics (async, non-blocking)
    severity_counts = {
        "critical": sum(1 for f in result.findings if f.severity == Severity.CRITICAL),
        "high": sum(1 for f in result.findings if f.severity == Severity.HIGH),
        "medium": sum(1 for f in result.findings if f.severity == Severity.MEDIUM),
        "low": sum(1 for f in result.findings if f.severity == Severity.LOW),
    }

=======
    # Track telemetry (async, non-blocking)
    exit_code = 1 if (enforce and not result.safe) else 0
>>>>>>> origin
    track_scan_completed(
        cli_version=__version__,
        scan_duration_ms=result.duration_ms,
        files_scanned=result.files_scanned,
        patterns_matched=[f.id for f in result.findings],
<<<<<<< HEAD
        severity_counts=severity_counts,
        score=result.score,
        output_format=output_format,
        exit_code=exit_code,
        mode=mode_str,
        success=scan_success,
=======
        severity_counts={
            "critical": sum(1 for f in result.findings if f.severity == Severity.CRITICAL),
            "high": sum(1 for f in result.findings if f.severity == Severity.HIGH),
            "medium": sum(1 for f in result.findings if f.severity == Severity.MEDIUM),
            "low": sum(1 for f in result.findings if f.severity == Severity.LOW),
        },
        score=result.score,
        output_format=output_format,
        exit_code=exit_code,
>>>>>>> origin
    )

    # Exit code based on mode and findings
    sys.exit(exit_code)


@main.group(invoke_without_command=True)
@click.pass_context
def config(ctx):
    """Manage DeepSweep configuration."""
    if ctx.invoked_subcommand is None:
        # Show config by default if no subcommand
        from deepsweep_ai.telemetry import _get_config as get_telemetry_config

<<<<<<< HEAD
        track_cli_invoked(__version__, "config")

=======
>>>>>>> origin
        config_path = Path.home() / ".config" / "deepsweep" / "config.yaml"
        cfg = Config.load()
        tel_cfg = get_telemetry_config()

        api_display = f"{'*' * 8}{cfg.api_key[-4:]}" if cfg.api_key else "Not set"
        telemetry_status = "enabled" if tel_cfg.get("telemetry", True) else "disabled"
<<<<<<< HEAD
        error_reporting_status = "enabled" if tel_cfg.get("error_reporting", False) else "disabled"

        print("DeepSweep Configuration")
        print(divider(40))
        print(f"API Key:         {api_display}")
        print(f"Mode:            {cfg.mode.value}")
        print(f"Tier:            {cfg.tier.value}")
        print(f"Telemetry:       {telemetry_status}")
        print(f"Error reports:   {error_reporting_status}")
        print(f"Config:          {config_path}")
=======

        print("DeepSweep Configuration")
        print(divider(40))
        print(f"API Key:    {api_display}")
        print(f"Mode:       {cfg.mode.value}")
        print(f"Tier:       {cfg.tier.value}")
        print(f"Telemetry:  {telemetry_status}")
        print(f"Config:     {config_path}")
>>>>>>> origin


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """Set a configuration value.

    Examples:
        deepsweep config set telemetry false
<<<<<<< HEAD
        deepsweep config set error_reporting true
=======
>>>>>>> origin
        deepsweep config set mode enforce
        deepsweep config set api_key YOUR_KEY
    """
    from deepsweep_ai.telemetry import set_telemetry_enabled, _get_config, _save_config

<<<<<<< HEAD
    track_cli_invoked(__version__, "config_set")
    track_feature_used(__version__, "config_set", {"key": key})

=======
>>>>>>> origin
    if key == "telemetry":
        enabled = value.lower() in ("true", "1", "yes", "on")
        set_telemetry_enabled(enabled)
        status = "enabled" if enabled else "disabled"
        click.echo(f"Telemetry {status}")
<<<<<<< HEAD
    elif key == "error_reporting":
        # Opt-in stack trace collection
        enabled = value.lower() in ("true", "1", "yes", "on")
        set_error_reporting_enabled(enabled)
        status = "enabled" if enabled else "disabled"
        click.echo(f"Error reporting (stack traces) {status}")
        if enabled:
            click.echo("Stack traces will now be included in error telemetry.")
=======
>>>>>>> origin
    elif key == "mode":
        config_path = Path.home() / ".config" / "deepsweep" / "config.yaml"
        cfg = Config.load()
        cfg.mode = Mode(value.lower())
        cfg.save(config_path)
        click.echo(f"Mode set to {value}")
    elif key == "api_key":
        config_path = Path.home() / ".config" / "deepsweep" / "config.yaml"
        cfg = Config.load()
        cfg.api_key = value
        cfg.save(config_path)
        click.echo("API key set")
    else:
        tel_cfg = _get_config()
        tel_cfg[key] = value
        _save_config(tel_cfg)
        click.echo(f"Set {key} = {value}")


@config.command("get")
@click.argument("key", required=False)
def config_get(key: Optional[str] = None):
    """Get configuration value(s).

    Examples:
        deepsweep config get           # Show all
        deepsweep config get telemetry # Show specific key
    """
    from deepsweep_ai.telemetry import _get_config

<<<<<<< HEAD
    track_cli_invoked(__version__, "config_get")

=======
>>>>>>> origin
    tel_cfg = _get_config()
    cfg = Config.load()

    # Merge configs for display
    all_config = {
        "telemetry": tel_cfg.get("telemetry", True),
<<<<<<< HEAD
        "error_reporting": tel_cfg.get("error_reporting", False),
        "mode": cfg.mode.value,
        "tier": cfg.tier.value,
        "api_key": f"{'*' * 8}{cfg.api_key[-4:]}" if cfg.api_key else "not set",
=======
        "mode": cfg.mode.value,
        "tier": cfg.tier.value,
        "api_key": f"{'*' * 8}{cfg.api_key[-4:]}" if cfg.api_key else "not set",
        **{k: v for k, v in tel_cfg.items() if k not in ("telemetry", "installation_id")},
>>>>>>> origin
    }

    if key:
        value = all_config.get(key, "not set")
        click.echo(f"{key} = {value}")
    else:
        for k, v in all_config.items():
            click.echo(f"{k} = {v}")


<<<<<<< HEAD
@config.command("stats")
def config_stats():
    """Show telemetry statistics for this installation.

    Shows anonymized usage statistics collected locally.
    No data is sent when running this command.

    Examples:
        deepsweep config stats
    """
    track_cli_invoked(__version__, "config_stats")

    stats = get_telemetry_stats()

    print("DeepSweep Telemetry Statistics")
    print(divider(40))
    print(f"Installation:     {stats['installation_id']}")
    print(f"Days active:      {stats['days_since_install']}")
    print(f"Sessions:         {stats['session_count']}")
    print(f"Total scans:      {stats['total_scans']}")
    print(f"Successful:       {stats['successful_scans']}")
    print(f"Failed:           {stats['failed_scans']}")
    print(f"Success rate:     {stats['success_rate_pct']}%")
    print(f"First success:    {'Yes' if stats['first_success_achieved'] else 'Not yet'}")
    print(divider(40))
    print(f"Telemetry:        {'enabled' if stats['enabled'] else 'disabled'}")
    print(f"Error reporting:  {'enabled' if stats['error_reporting'] else 'disabled'}")


@main.command()
def auth():
    """Authenticate with DeepSweep for Pro features."""
    track_cli_invoked(__version__, "auth")
    track_auth_flow(__version__, "started")

=======
@main.command()
def auth():
    """Authenticate with DeepSweep for Pro features."""
>>>>>>> origin
    print("DeepSweep Authentication")
    print(divider(40))
    print()
    print("To get your API key:")
    print()
    print("1. Visit https://deepsweep.ai/pro")
    print("2. Sign up or log in")
    print("3. Copy your API key")
    print("4. Run: deepsweep config set api_key YOUR_KEY")
    print()
    print("Or set DEEPSWEEP_API_KEY environment variable")


@main.command()
def version():
    """Show version information."""
<<<<<<< HEAD
    track_cli_invoked(__version__, "version_cmd")
=======
>>>>>>> origin
    print(f"DeepSweep v{__version__}")
    print("The #1 Security Gateway for Agentic AI Code Assistants")
    print("https://deepsweep.ai")


if __name__ == "__main__":
    main()
