"""
DeepSweep Telemetry Module - Industry Standard Implementation

Implements telemetry following patterns used by Vercel CLI, GitHub CLI,
Fly.io, Stripe CLI, and LangChain CLI.

Collects anonymous usage data to improve detection patterns.
No source code, file contents, or PII is ever collected.

Opt-out:
  - CLI: deepsweep config set telemetry false
  - Env: export DEEPSWEEP_TELEMETRY=false
  - Config: ~/.deepsweep/telemetry.json {"enabled": false}

Telemetry Format (~/.deepsweep/telemetry.json):
{
  "id": "uuidv4",
  "created": "2025-12-18T00:00:00Z",
  "enabled": true,
  "first_success_at": null,
  "last_command_at": null,
  "session_count": 0
}
"""

from __future__ import annotations

import os
import json
import uuid
import platform
import sys
import hashlib
import threading
import traceback
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from enum import Enum

import urllib.request
import urllib.error

# PostHog configuration
POSTHOG_API_KEY = "phc_yaXDgwcs2rJS84fyVQJg0QVlWdqEaFgpjiG47kLzL1l"  # Replace with actual key
POSTHOG_HOST = "https://app.posthog.com"
POSTHOG_BATCH_ENDPOINT = f"{POSTHOG_HOST}/batch/"
POSTHOG_CAPTURE_ENDPOINT = f"{POSTHOG_HOST}/capture/"

# Fallback custom endpoint (for redundancy)
CUSTOM_TELEMETRY_ENDPOINT = "https://telemetry.deepsweep.ai/v1/events"

# Timeouts (never block CLI)
TELEMETRY_TIMEOUT = 2  # seconds

# Config location (following spec: ~/.deepsweep/telemetry.json)
TELEMETRY_DIR = Path.home() / ".deepsweep"
TELEMETRY_FILE = TELEMETRY_DIR / "telemetry.json"
CONFIG_FILE = TELEMETRY_DIR / "config.json"  # Legacy config location


class EventType(str, Enum):
    """Telemetry event types - following industry patterns."""
    # Core activation events
    CLI_INSTALLED = "cli_installed"
    CLI_INVOKED = "cli_invoked"
    CLI_SESSION_START = "cli_session_start"
    CLI_SESSION_END = "cli_session_end"

    # Scan events
    SCAN_STARTED = "scan_started"
    SCAN_COMPLETED = "scan_completed"
    SCAN_FAILED = "scan_failed"

    # Success metrics
    FIRST_SUCCESSFUL_OUTPUT = "first_successful_output"  # TTFSO

    # Error events
    ERROR_OCCURRED = "error_occurred"

    # Feature usage
    FEATURE_USED = "feature_used"

    # Auth events
    AUTH_STARTED = "auth_started"
    AUTH_COMPLETED = "auth_completed"


@dataclass
class TelemetryConfig:
    """
    Persistent telemetry configuration stored at ~/.deepsweep/telemetry.json
    Following spec: anonymous machine fingerprint with minimal data.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    enabled: bool = True

    # Strong signal metrics (investor-grade)
    first_success_at: Optional[str] = None  # Time to First Successful Output
    last_command_at: Optional[str] = None   # For time between commands
    session_count: int = 0                   # Sessions per developer
    total_scans: int = 0
    successful_scans: int = 0
    failed_scans: int = 0

    # Opt-in error tracking
    error_reporting: bool = False  # Stack traces require opt-in

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TelemetryConfig":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class TelemetryEvent:
    """
    Telemetry event structure following PostHog + industry patterns.

    Designed for ~100-300 bytes per event (lightweight, privacy-first).
    """
    event: str  # Event name (PostHog standard)
    distinct_id: str  # User ID (installation UUID)
    timestamp: str

    # Properties (all optional, privacy-safe)
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_posthog_dict(self) -> Dict[str, Any]:
        """Format for PostHog API."""
        return {
            "event": self.event,
            "distinct_id": self.distinct_id,
            "timestamp": self.timestamp,
            "properties": {
                **self.properties,
                "$lib": "deepsweep-telemetry",
                "$lib_version": self.properties.get("cli_version", "unknown"),
            }
        }

    def to_custom_dict(self) -> Dict[str, Any]:
        """Format for custom endpoint (backwards compatible)."""
        return {
            "event_type": self.event,
            "installation_id": self.distinct_id,
            "session_id": self.properties.get("session_id", ""),
            "timestamp": self.timestamp,
            "properties": self.properties,
        }


# =============================================================================
# TELEMETRY CONFIG MANAGEMENT
# =============================================================================

def _ensure_telemetry_dir() -> None:
    """Ensure ~/.deepsweep directory exists."""
    TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)


def _load_telemetry_config() -> TelemetryConfig:
    """Load telemetry config from ~/.deepsweep/telemetry.json"""
    if TELEMETRY_FILE.exists():
        try:
            data = json.loads(TELEMETRY_FILE.read_text())
            return TelemetryConfig.from_dict(data)
        except (json.JSONDecodeError, IOError, TypeError):
            pass

    # Migration: check legacy config.json
    if CONFIG_FILE.exists():
        try:
            legacy = json.loads(CONFIG_FILE.read_text())
            config = TelemetryConfig()
            if "installation_id" in legacy:
                config.id = legacy["installation_id"]
            if "telemetry" in legacy:
                config.enabled = legacy["telemetry"]
            _save_telemetry_config(config)
            return config
        except (json.JSONDecodeError, IOError):
            pass

    # Create new config
    config = TelemetryConfig()
    _save_telemetry_config(config)
    return config


def _save_telemetry_config(config: TelemetryConfig) -> None:
    """Save telemetry config to ~/.deepsweep/telemetry.json"""
    _ensure_telemetry_dir()
    TELEMETRY_FILE.write_text(json.dumps(config.to_dict(), indent=2))


def _get_config() -> Dict[str, Any]:
    """Legacy API: Get config as dict (backwards compatible)."""
    config = _load_telemetry_config()
    return {
        "installation_id": config.id,
        "telemetry": config.enabled,
        **config.to_dict()
    }


def _save_config(data: Dict[str, Any]) -> None:
    """Legacy API: Save config from dict (backwards compatible)."""
    config = _load_telemetry_config()
    if "installation_id" in data:
        config.id = data["installation_id"]
    if "telemetry" in data:
        config.enabled = data["telemetry"]
    _save_telemetry_config(config)


# =============================================================================
# TELEMETRY STATE
# =============================================================================

# Global session state (per-run)
_session_id: Optional[str] = None
_session_start_time: Optional[float] = None
_command_start_time: Optional[float] = None


def _get_session_id() -> str:
    """Get or create session ID for this CLI run."""
    global _session_id, _session_start_time
    if _session_id is None:
        _session_id = str(uuid.uuid4())
        _session_start_time = time.time()
    return _session_id


def _get_installation_id() -> str:
    """Get persistent installation ID (UUID v4)."""
    return _load_telemetry_config().id


# =============================================================================
# ENVIRONMENT & SYSTEM INFO
# =============================================================================

def _is_ci_environment() -> bool:
    """Detect if running in a CI environment."""
    ci_env_vars = [
        "CI", "GITHUB_ACTIONS", "GITLAB_CI", "CIRCLECI",
        "TRAVIS", "JENKINS_URL", "BUILDKITE", "AZURE_PIPELINES",
        "TEAMCITY_VERSION", "BITBUCKET_PIPELINES", "CODEBUILD_BUILD_ID",
    ]
    return any(os.getenv(var) for var in ci_env_vars)


def _get_ci_provider() -> Optional[str]:
    """Get CI provider name if in CI."""
    providers = {
        "GITHUB_ACTIONS": "github_actions",
        "GITLAB_CI": "gitlab_ci",
        "CIRCLECI": "circleci",
        "TRAVIS": "travis",
        "JENKINS_URL": "jenkins",
        "BUILDKITE": "buildkite",
        "AZURE_PIPELINES": "azure_pipelines",
        "BITBUCKET_PIPELINES": "bitbucket_pipelines",
        "CODEBUILD_BUILD_ID": "aws_codebuild",
    }
    for env_var, name in providers.items():
        if os.getenv(env_var):
            return name
    if os.getenv("CI"):
        return "unknown_ci"
    return None


def _get_os_info() -> Dict[str, str]:
    """Get OS information (privacy-safe)."""
    system = platform.system().lower()
    # Normalize to mac/linux/windows
    os_name = {
        "darwin": "mac",
        "linux": "linux",
        "windows": "windows",
    }.get(system, system)

    return {
        "os": os_name,
        "os_version": platform.release(),
        "arch": platform.machine(),
    }


def _get_base_properties(cli_version: str) -> Dict[str, Any]:
    """Get base properties included in all events."""
    os_info = _get_os_info()
    return {
        "cli_version": cli_version,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "session_id": _get_session_id(),
        **os_info,
        "ci": _is_ci_environment(),
        "ci_provider": _get_ci_provider(),
    }


# =============================================================================
# TELEMETRY ENABLED CHECK
# =============================================================================

def is_telemetry_enabled() -> bool:
    """
    Check if telemetry is enabled.

    Disabled by:
    1. Environment variable: DEEPSWEEP_TELEMETRY=false
    2. Environment variable: DEEPSWEEP_OFFLINE=1
    3. Config file: ~/.deepsweep/telemetry.json {"enabled": false}
    """
    # Check environment variable first
    env_value = os.getenv("DEEPSWEEP_TELEMETRY", "").lower()
    if env_value in ("false", "0", "no", "off"):
        return False

    # Check offline mode
    if os.environ.get("DEEPSWEEP_OFFLINE"):
        return False

    # Check DO_NOT_TRACK (privacy standard)
    if os.environ.get("DO_NOT_TRACK"):
        return False

    # Check config file
    config = _load_telemetry_config()
    return config.enabled


def set_telemetry_enabled(enabled: bool) -> None:
    """Enable or disable telemetry."""
    config = _load_telemetry_config()
    config.enabled = enabled
    _save_telemetry_config(config)


def set_error_reporting_enabled(enabled: bool) -> None:
    """Enable or disable stack trace collection (opt-in)."""
    config = _load_telemetry_config()
    config.error_reporting = enabled
    _save_telemetry_config(config)


def is_error_reporting_enabled() -> bool:
    """Check if stack trace collection is enabled (opt-in)."""
    if not is_telemetry_enabled():
        return False
    config = _load_telemetry_config()
    return config.error_reporting


# =============================================================================
# EVENT SENDING
# =============================================================================

def _send_to_posthog(events: List[TelemetryEvent]) -> bool:
    """Send events to PostHog batch API."""
    try:
        payload = {
            "api_key": POSTHOG_API_KEY,
            "batch": [e.to_posthog_dict() for e in events],
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            POSTHOG_BATCH_ENDPOINT,
            data=data,
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )
        urllib.request.urlopen(req, timeout=TELEMETRY_TIMEOUT)
        return True
    except Exception:
        return False


def _send_to_custom_endpoint(event: TelemetryEvent) -> bool:
    """Send event to custom telemetry endpoint (fallback)."""
    try:
        data = json.dumps(event.to_custom_dict()).encode("utf-8")
        req = urllib.request.Request(
            CUSTOM_TELEMETRY_ENDPOINT,
            data=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": f"deepsweep-cli/{event.properties.get('cli_version', 'unknown')}",
            },
            method="POST",
        )
        urllib.request.urlopen(req, timeout=TELEMETRY_TIMEOUT)
        return True
    except Exception:
        return False


def _send_event_async(event: TelemetryEvent) -> None:
    """
    Send telemetry event asynchronously.
    Never blocks the CLI - fires and forgets with timeout.
    """
    def _send():
        # Try PostHog first, fallback to custom endpoint
        if not _send_to_posthog([event]):
            _send_to_custom_endpoint(event)

    # Fire and forget in background thread
    thread = threading.Thread(target=_send, daemon=True)
    thread.start()


# =============================================================================
# LATENCY TRACKING
# =============================================================================

@contextmanager
def track_latency():
    """
    Context manager for tracking operation latency.

    Usage:
        with track_latency() as timer:
            do_something()
        duration_ms = timer.duration_ms
    """
    class Timer:
        def __init__(self):
            self.start_time = time.time()
            self.end_time: Optional[float] = None

        @property
        def duration_ms(self) -> int:
            end = self.end_time or time.time()
            return int((end - self.start_time) * 1000)

    timer = Timer()
    try:
        yield timer
    finally:
        timer.end_time = time.time()


def start_command_timer() -> None:
    """Start timing a command execution."""
    global _command_start_time
    _command_start_time = time.time()


def get_command_duration_ms() -> int:
    """Get duration since command timer started."""
    if _command_start_time is None:
        return 0
    return int((time.time() - _command_start_time) * 1000)


# =============================================================================
# CORE TRACKING FUNCTIONS
# =============================================================================

def track_cli_installed(cli_version: str) -> None:
    """
    Track CLI installation.
    Called on first run when telemetry.json is created.
    """
    if not is_telemetry_enabled():
        return

    event = TelemetryEvent(
        event=EventType.CLI_INSTALLED.value,
        distinct_id=_get_installation_id(),
        timestamp=datetime.now(timezone.utc).isoformat(),
        properties={
            **_get_base_properties(cli_version),
            "install_method": os.getenv("DEEPSWEEP_INSTALL_METHOD", "pip"),
        }
    )
    _send_event_async(event)


def track_cli_invoked(cli_version: str, command: str) -> None:
    """
    Track CLI command invocation.

    Args:
        cli_version: DeepSweep CLI version
        command: Command name (scan, config, auth, etc.)
    """
    if not is_telemetry_enabled():
        return

    # Start command timer
    start_command_timer()

    # Update last command time for retention tracking
    config = _load_telemetry_config()
    now = datetime.now(timezone.utc).isoformat()

    # Calculate time since last command
    time_since_last_ms: Optional[int] = None
    if config.last_command_at:
        try:
            last = datetime.fromisoformat(config.last_command_at.replace('Z', '+00:00'))
            time_since_last_ms = int((datetime.now(timezone.utc) - last).total_seconds() * 1000)
        except (ValueError, TypeError):
            pass

    config.last_command_at = now
    config.session_count += 1
    _save_telemetry_config(config)

    event = TelemetryEvent(
        event=EventType.CLI_INVOKED.value,
        distinct_id=_get_installation_id(),
        timestamp=now,
        properties={
            **_get_base_properties(cli_version),
            "command": command,
            "time_since_last_command_ms": time_since_last_ms,
            "session_number": config.session_count,
        }
    )
    _send_event_async(event)


def track_session_start(cli_version: str) -> None:
    """Track CLI session start (for Sessions per Developer per Day)."""
    if not is_telemetry_enabled():
        return

    event = TelemetryEvent(
        event=EventType.CLI_SESSION_START.value,
        distinct_id=_get_installation_id(),
        timestamp=datetime.now(timezone.utc).isoformat(),
        properties=_get_base_properties(cli_version),
    )
    _send_event_async(event)


def track_session_end(cli_version: str, exit_code: int) -> None:
    """Track CLI session end with exit code."""
    if not is_telemetry_enabled():
        return

    session_duration_ms = 0
    if _session_start_time:
        session_duration_ms = int((time.time() - _session_start_time) * 1000)

    event = TelemetryEvent(
        event=EventType.CLI_SESSION_END.value,
        distinct_id=_get_installation_id(),
        timestamp=datetime.now(timezone.utc).isoformat(),
        properties={
            **_get_base_properties(cli_version),
            "exit_code": exit_code,
            "session_duration_ms": session_duration_ms,
        }
    )
    _send_event_async(event)


def track_scan_started(cli_version: str, mode: str) -> None:
    """Track scan start (for funnel analysis)."""
    if not is_telemetry_enabled():
        return

    event = TelemetryEvent(
        event=EventType.SCAN_STARTED.value,
        distinct_id=_get_installation_id(),
        timestamp=datetime.now(timezone.utc).isoformat(),
        properties={
            **_get_base_properties(cli_version),
            "mode": mode,
        }
    )
    _send_event_async(event)


def track_scan_completed(
    cli_version: str,
    scan_duration_ms: int,
    files_scanned: int,
    patterns_matched: List[str],
    severity_counts: Dict[str, int],
    score: int,
    output_format: str,
    exit_code: int,
    mode: str = "observe",
    success: bool = True,
) -> None:
    """
    Track a completed scan event.

    Args:
        cli_version: DeepSweep CLI version
        scan_duration_ms: Scan duration in milliseconds (LATENCY)
        files_scanned: Number of files scanned
        patterns_matched: List of pattern IDs that matched (not content)
        severity_counts: Dict of severity -> count
        score: Security score 0-100
        output_format: Output format used (text, json, sarif)
        exit_code: CLI exit code
        mode: observe or enforce
        success: Whether scan completed successfully
    """
    if not is_telemetry_enabled():
        return

    # Update success/failure metrics
    config = _load_telemetry_config()
    config.total_scans += 1
    if success:
        config.successful_scans += 1

        # Track Time to First Successful Output
        if config.first_success_at is None:
            config.first_success_at = datetime.now(timezone.utc).isoformat()
            _save_telemetry_config(config)

            # Fire TTFSO event
            ttfso_event = TelemetryEvent(
                event=EventType.FIRST_SUCCESSFUL_OUTPUT.value,
                distinct_id=_get_installation_id(),
                timestamp=config.first_success_at,
                properties={
                    **_get_base_properties(cli_version),
                    "scans_until_success": config.total_scans,
                    "time_to_first_success_ms": scan_duration_ms,
                }
            )
            _send_event_async(ttfso_event)
    else:
        config.failed_scans += 1

    _save_telemetry_config(config)

    # Calculate success rate
    success_rate = (config.successful_scans / config.total_scans * 100) if config.total_scans > 0 else 0

    event = TelemetryEvent(
        event=EventType.SCAN_COMPLETED.value,
        distinct_id=_get_installation_id(),
        timestamp=datetime.now(timezone.utc).isoformat(),
        properties={
            **_get_base_properties(cli_version),
            # Core metrics
            "scan_duration_ms": scan_duration_ms,  # LATENCY
            "files_scanned": files_scanned,
            "patterns_matched": patterns_matched,  # IDs only, never content
            "severity_counts": severity_counts,
            "score": score,
            "output_format": output_format,
            "exit_code": exit_code,  # EXIT CODE tracking
            "mode": mode,
            "success": success,

            # Strong signal metrics
            "total_scans": config.total_scans,
            "successful_scans": config.successful_scans,
            "failed_scans": config.failed_scans,
            "success_rate_pct": round(success_rate, 2),

            # Finding metrics
            "has_critical": severity_counts.get("critical", 0) > 0,
            "has_high": severity_counts.get("high", 0) > 0,
            "total_findings": sum(severity_counts.values()),
        }
    )
    _send_event_async(event)


def track_scan_failed(
    cli_version: str,
    error_type: str,
    duration_ms: int,
    mode: str = "observe",
) -> None:
    """Track a failed scan."""
    if not is_telemetry_enabled():
        return

    # Update failure count
    config = _load_telemetry_config()
    config.total_scans += 1
    config.failed_scans += 1
    _save_telemetry_config(config)

    event = TelemetryEvent(
        event=EventType.SCAN_FAILED.value,
        distinct_id=_get_installation_id(),
        timestamp=datetime.now(timezone.utc).isoformat(),
        properties={
            **_get_base_properties(cli_version),
            "error_type": error_type,
            "duration_ms": duration_ms,
            "mode": mode,
            "total_scans": config.total_scans,
            "failed_scans": config.failed_scans,
        }
    )
    _send_event_async(event)


def track_error(
    cli_version: str,
    error_type: str,
    command: Optional[str] = None,
    stack_trace: Optional[str] = None,
    exit_code: int = 1,
) -> None:
    """
    Track an error occurrence.

    Stack traces are only included if error_reporting is opt-in enabled.
    """
    if not is_telemetry_enabled():
        return

    properties: Dict[str, Any] = {
        **_get_base_properties(cli_version),
        "error_type": error_type,
        "exit_code": exit_code,
        "command_duration_ms": get_command_duration_ms(),
    }

    if command:
        properties["command"] = command

    # Only include stack trace if explicitly opted in
    if stack_trace and is_error_reporting_enabled():
        # Sanitize stack trace (remove paths, keep structure)
        sanitized = _sanitize_stack_trace(stack_trace)
        properties["stack_trace"] = sanitized

    event = TelemetryEvent(
        event=EventType.ERROR_OCCURRED.value,
        distinct_id=_get_installation_id(),
        timestamp=datetime.now(timezone.utc).isoformat(),
        properties=properties,
    )
    _send_event_async(event)


def _sanitize_stack_trace(trace: str) -> str:
    """
    Sanitize stack trace to remove potentially sensitive paths.
    Keep only file names, line numbers, and function names.
    """
    lines = []
    for line in trace.split('\n'):
        # Remove home directory paths
        home = str(Path.home())
        if home in line:
            line = line.replace(home, '~')
        # Remove other potentially sensitive paths
        if '/site-packages/' in line:
            # Keep only package/module part
            idx = line.find('/site-packages/')
            line = line[idx:]
        lines.append(line)
    return '\n'.join(lines)


def track_feature_used(
    cli_version: str,
    feature: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Track feature usage for understanding what features matter."""
    if not is_telemetry_enabled():
        return

    properties = {
        **_get_base_properties(cli_version),
        "feature": feature,
    }
    if metadata:
        properties.update(metadata)

    event = TelemetryEvent(
        event=EventType.FEATURE_USED.value,
        distinct_id=_get_installation_id(),
        timestamp=datetime.now(timezone.utc).isoformat(),
        properties=properties,
    )
    _send_event_async(event)


def track_auth_flow(cli_version: str, step: str, success: bool = True) -> None:
    """Track authentication flow steps."""
    if not is_telemetry_enabled():
        return

    event_type = EventType.AUTH_COMPLETED if step == "completed" else EventType.AUTH_STARTED

    event = TelemetryEvent(
        event=event_type.value,
        distinct_id=_get_installation_id(),
        timestamp=datetime.now(timezone.utc).isoformat(),
        properties={
            **_get_base_properties(cli_version),
            "step": step,
            "success": success,
        }
    )
    _send_event_async(event)


# =============================================================================
# ANALYTICS HELPERS
# =============================================================================

def get_telemetry_stats() -> Dict[str, Any]:
    """
    Get telemetry statistics for the current installation.
    Useful for debugging and transparency.
    """
    config = _load_telemetry_config()

    success_rate = 0
    if config.total_scans > 0:
        success_rate = round(config.successful_scans / config.total_scans * 100, 2)

    # Calculate days since install
    days_since_install = 0
    try:
        created = datetime.fromisoformat(config.created.replace('Z', '+00:00'))
        days_since_install = (datetime.now(timezone.utc) - created).days
    except (ValueError, TypeError):
        pass

    return {
        "installation_id": config.id[:8] + "...",  # Partial for privacy
        "enabled": config.enabled,
        "error_reporting": config.error_reporting,
        "days_since_install": days_since_install,
        "session_count": config.session_count,
        "total_scans": config.total_scans,
        "successful_scans": config.successful_scans,
        "failed_scans": config.failed_scans,
        "success_rate_pct": success_rate,
        "first_success_achieved": config.first_success_at is not None,
    }


def reset_telemetry() -> None:
    """Reset telemetry configuration (for testing)."""
    if TELEMETRY_FILE.exists():
        TELEMETRY_FILE.unlink()

    global _session_id, _session_start_time, _command_start_time
    _session_id = None
    _session_start_time = None
    _command_start_time = None


# =============================================================================
# INITIALIZATION
# =============================================================================

def initialize_telemetry(cli_version: str) -> None:
    """
    Initialize telemetry on CLI startup.
    Creates telemetry.json if first run and fires install event.
    """
    is_first_run = not TELEMETRY_FILE.exists()

    # Load/create config
    config = _load_telemetry_config()

    # Track install on first run
    if is_first_run and is_telemetry_enabled():
        track_cli_installed(cli_version)

    # Start session tracking
    _get_session_id()
