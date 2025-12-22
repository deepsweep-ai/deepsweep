"""
DeepSweep Telemetry Module

Collects anonymous usage data to improve detection patterns.
No source code, file contents, or PII is ever collected.

Opt-out:
  - CLI: deepsweep config set telemetry false
  - Env: export DEEPSWEEP_TELEMETRY=false
  - Config: ~/.deepsweep/config.json {"telemetry": false}
"""

import os
import json
import uuid
import platform
import sys
import hashlib
import threading
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

import urllib.request
import urllib.error

# Telemetry endpoint
TELEMETRY_ENDPOINT = "https://telemetry.deepsweep.ai/v1/events"
TELEMETRY_TIMEOUT = 2  # seconds - never block CLI

# Config location
CONFIG_DIR = Path.home() / ".deepsweep"
CONFIG_FILE = CONFIG_DIR / "config.json"


def _get_config() -> Dict[str, Any]:
    """Load config from ~/.deepsweep/config.json"""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def _save_config(config: Dict[str, Any]) -> None:
    """Save config to ~/.deepsweep/config.json"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def _get_installation_id() -> str:
    """
    Get or create a persistent installation ID (UUID v4).
    This ID is unique per machine and persists across CLI runs.
    Similar to Snyk's approach.
    """
    config = _get_config()

    if "installation_id" not in config:
        config["installation_id"] = str(uuid.uuid4())
        _save_config(config)

    return config["installation_id"]


def _generate_session_id() -> str:
    """Generate a new session ID for this CLI run."""
    return str(uuid.uuid4())


def _is_ci_environment() -> bool:
    """Detect if running in a CI environment."""
    ci_env_vars = [
        "CI",
        "GITHUB_ACTIONS",
        "GITLAB_CI",
        "CIRCLECI",
        "TRAVIS",
        "JENKINS_URL",
        "BUILDKITE",
        "AZURE_PIPELINES",
        "TEAMCITY_VERSION",
    ]
    return any(os.getenv(var) for var in ci_env_vars)


def is_telemetry_enabled() -> bool:
    """
    Check if telemetry is enabled.

    Disabled by:
    1. Environment variable: DEEPSWEEP_TELEMETRY=false
    2. Config file: {"telemetry": false}
    """
    # Check environment variable first
    env_value = os.getenv("DEEPSWEEP_TELEMETRY", "").lower()
    if env_value in ("false", "0", "no", "off"):
        return False

    # Check offline mode
    if os.environ.get("DEEPSWEEP_OFFLINE"):
        return False

    # Check config file
    config = _get_config()
    if config.get("telemetry") is False:
        return False

    return True


def set_telemetry_enabled(enabled: bool) -> None:
    """Enable or disable telemetry via config file."""
    config = _get_config()
    config["telemetry"] = enabled
    _save_config(config)


class TelemetryEvent:
    """
    Telemetry event structure following Snyk's pattern.

    Contains:
    - Event metadata (type, timestamp, IDs)
    - Environment info (OS, Python, CLI version)
    - Scan results (counts, patterns, score)

    Never contains:
    - Source code or file contents
    - File paths
    - Secrets or credentials
    - Repository names
    """

    def __init__(
        self,
        event_type: str,
        cli_version: str,
        scan_duration_ms: Optional[int] = None,
        files_scanned: Optional[int] = None,
        patterns_matched: Optional[List[str]] = None,
        severity_counts: Optional[Dict[str, int]] = None,
        score: Optional[int] = None,
        output_format: Optional[str] = None,
        exit_code: Optional[int] = None,
    ):
        self.event_type = event_type
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.installation_id = _get_installation_id()
        self.session_id = _generate_session_id()

        self.properties = {
            "cli_version": cli_version,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "os": platform.system().lower(),
            "os_version": platform.release(),
            "arch": platform.machine(),
            "ci": _is_ci_environment(),
        }

        # Add optional scan properties
        if scan_duration_ms is not None:
            self.properties["scan_duration_ms"] = scan_duration_ms
        if files_scanned is not None:
            self.properties["files_scanned"] = files_scanned
        if patterns_matched is not None:
            # Only pattern IDs, never content
            self.properties["patterns_matched"] = patterns_matched
        if severity_counts is not None:
            self.properties["severity_counts"] = severity_counts
        if score is not None:
            self.properties["score"] = score
        if output_format is not None:
            self.properties["output_format"] = output_format
        if exit_code is not None:
            self.properties["exit_code"] = exit_code

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "installation_id": self.installation_id,
            "session_id": self.session_id,
            "properties": self.properties,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


def _send_event_async(event: TelemetryEvent) -> None:
    """
    Send telemetry event asynchronously.
    Never blocks the CLI - fires and forgets with timeout.
    """
    def _send():
        try:
            data = event.to_json().encode("utf-8")
            req = urllib.request.Request(
                TELEMETRY_ENDPOINT,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": f"deepsweep-cli/{event.properties.get('cli_version', 'unknown')}",
                },
                method="POST",
            )
            urllib.request.urlopen(req, timeout=TELEMETRY_TIMEOUT)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError):
            # Silently fail - telemetry should never impact user experience
            pass

    # Fire and forget in background thread
    thread = threading.Thread(target=_send, daemon=True)
    thread.start()


def track_scan_completed(
    cli_version: str,
    scan_duration_ms: int,
    files_scanned: int,
    patterns_matched: List[str],
    severity_counts: Dict[str, int],
    score: int,
    output_format: str,
    exit_code: int,
) -> None:
    """
    Track a completed scan event.

    Args:
        cli_version: DeepSweep CLI version
        scan_duration_ms: Scan duration in milliseconds
        files_scanned: Number of files scanned
        patterns_matched: List of pattern IDs that matched (not content)
        severity_counts: Dict of severity -> count
        score: Security score 0-100
        output_format: Output format used (text, json, sarif)
        exit_code: CLI exit code
    """
    if not is_telemetry_enabled():
        return

    event = TelemetryEvent(
        event_type="scan_completed",
        cli_version=cli_version,
        scan_duration_ms=scan_duration_ms,
        files_scanned=files_scanned,
        patterns_matched=patterns_matched,
        severity_counts=severity_counts,
        score=score,
        output_format=output_format,
        exit_code=exit_code,
    )

    _send_event_async(event)


def track_cli_invoked(cli_version: str, command: str) -> None:
    """Track CLI invocation (which command was run)."""
    if not is_telemetry_enabled():
        return

    event = TelemetryEvent(
        event_type="cli_invoked",
        cli_version=cli_version,
    )
    event.properties["command"] = command

    _send_event_async(event)


def track_error(cli_version: str, error_type: str) -> None:
    """
    Track an error occurrence.
    Only tracks error type, never error messages or stack traces.
    """
    if not is_telemetry_enabled():
        return

    event = TelemetryEvent(
        event_type="error_occurred",
        cli_version=cli_version,
    )
    event.properties["error_type"] = error_type

    _send_event_async(event)
