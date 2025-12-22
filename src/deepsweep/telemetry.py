"""
DeepSweep Two-Tier Telemetry System

TIER 1 - Essential (Always On):
  Threat Intelligence - Powers the community security flywheel
  - Pattern effectiveness data
  - Attack trend signals
  - Zero-day detection
  - Network effect moat

TIER 2 - Optional (Can Disable):
  Product Analytics - PostHog for funnel optimization
  - Activation metrics
  - Retention tracking
  - Feature usage
  - Performance data

Privacy Guarantees:
- NO source code, file paths, or file contents
- NO repository names or user identities
- NO API keys, tokens, or secrets
- Anonymized machine ID only (UUID v4)

Design Standards:
- NO EMOJIS
- Optimistic messaging
- Async, non-blocking
- Never crashes on error
"""

import hashlib
import json
import os
import platform
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final
from urllib.request import Request, urlopen

import posthog

from deepsweep.constants import VERSION

# =============================================================================
# CONFIGURATION
# =============================================================================

# Threat Intelligence endpoint (Essential tier)
THREAT_INTEL_ENDPOINT: Final[str] = os.environ.get(
    "DEEPSWEEP_INTEL_ENDPOINT",
    "https://intel.deepsweep.ai/v1/signal"
)

# PostHog configuration (Optional tier)
POSTHOG_API_KEY: Final[str] = "phc_2KxJqV5jZ9nY8wH3pL7mT6sN4vR1cX0bQ9dE8fG7hI6jK5lM4n"
POSTHOG_HOST: Final[str] = "https://us.i.posthog.com"

# Config paths
CONFIG_DIR: Final[Path] = Path.home() / ".deepsweep"
CONFIG_FILE: Final[Path] = CONFIG_DIR / "config.json"

# Request timeout (never block CLI)
REQUEST_TIMEOUT: Final[float] = 2.0

# Default config
DEFAULT_CONFIG: Final[dict[str, Any]] = {
    "telemetry_enabled": True,  # Optional tier (PostHog)
    "offline_mode": False,      # Disables ALL telemetry
    "uuid": None,
    "first_run": True,
}


# =============================================================================
# THREAT INTELLIGENCE SIGNAL (ESSENTIAL TIER - THE FLYWHEEL)
# =============================================================================

@dataclass
class ThreatSignal:
    """
    Anonymized threat intelligence signal.

    This powers the DeepSweep flywheel - the core moat:
    - Every validation contributes anonymous pattern data
    - Pattern database grows stronger with adoption
    - All users benefit from collective intelligence
    - Network effects compound value over time

    NEVER includes: file paths, code, repo names, user identity
    """

    # Pattern intelligence (THE MOAT)
    pattern_ids: list[str] = field(default_factory=list)
    cve_matches: list[str] = field(default_factory=list)
    severity_counts: dict[str, int] = field(default_factory=dict)

    # Tool context (aggregate risk profiles)
    tool_context: list[str] = field(default_factory=list)
    file_types: list[str] = field(default_factory=list)

    # Validation metadata
    score: int = 0
    grade: str = ""
    finding_count: int = 0
    file_count: int = 0
    duration_ms: int = 0

    # Environment
    cli_version: str = ""
    python_version: str = ""
    os_type: str = ""
    is_ci: bool = False
    ci_provider: str | None = None

    # Temporal
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Anonymized identity (for deduplication only)
    install_id: str = field(default_factory=lambda: _get_install_id())
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])


# =============================================================================
# IDENTITY (ANONYMIZED)
# =============================================================================

_install_id_cache: str | None = None


def _get_install_id() -> str:
    """
    Get anonymized install ID (SHA-256 hash of machine identifiers).

    Used only for:
    - Deduplication in analytics
    - Cohort analysis (not individual tracking)

    Cannot be reversed to identify user or machine.
    """
    global _install_id_cache

    if _install_id_cache is not None:
        return _install_id_cache

    # Collect machine-specific but non-identifying data
    components = [
        platform.node(),
        platform.machine(),
        platform.processor(),
        str(uuid.getnode()),
    ]

    # Create irreversible hash
    raw = "|".join(components).encode()
    _install_id_cache = hashlib.sha256(raw).hexdigest()[:32]

    return _install_id_cache


# =============================================================================
# CI DETECTION
# =============================================================================

def _detect_ci() -> tuple[bool, str | None]:
    """Detect if running in CI environment."""
    ci_indicators = {
        "GITHUB_ACTIONS": "github",
        "GITLAB_CI": "gitlab",
        "CIRCLECI": "circleci",
        "JENKINS_URL": "jenkins",
        "TRAVIS": "travis",
        "BUILDKITE": "buildkite",
        "AZURE_PIPELINES": "azure",
        "BITBUCKET_PIPELINES": "bitbucket",
        "CI": None,
    }

    for env_var, provider in ci_indicators.items():
        if os.environ.get(env_var):
            return True, provider

    return False, None


# =============================================================================
# TELEMETRY CONFIG
# =============================================================================

class TelemetryConfig:
    """Manages telemetry configuration and preferences."""

    def __init__(self) -> None:
        """Initialize telemetry config."""
        self._config: dict[str, Any] = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load config from disk or create default."""
        if not CONFIG_FILE.exists():
            config = DEFAULT_CONFIG.copy()
            config["uuid"] = str(uuid.uuid4())
            self._save_config(config)
            return config

        try:
            with CONFIG_FILE.open("r") as f:
                loaded = json.load(f)
                return {**DEFAULT_CONFIG, **loaded}
        except (json.JSONDecodeError, OSError):
            config = DEFAULT_CONFIG.copy()
            config["uuid"] = str(uuid.uuid4())
            self._save_config(config)
            return config

    def _save_config(self, config: dict[str, Any]) -> None:
        """Save config to disk."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with CONFIG_FILE.open("w") as f:
            json.dump(config, f, indent=2)

    @property
    def enabled(self) -> bool:
        """Check if optional telemetry (PostHog) is enabled."""
        return self._config.get("telemetry_enabled", True)

    @property
    def offline_mode(self) -> bool:
        """Check if fully offline (disables ALL telemetry)."""
        return self._config.get("offline_mode", False) or os.environ.get("DEEPSWEEP_OFFLINE") == "1"

    @property
    def uuid(self) -> str:
        """Get anonymous user UUID."""
        return self._config.get("uuid", "unknown")

    @property
    def first_run(self) -> bool:
        """Check if this is first run."""
        return self._config.get("first_run", False)

    def enable(self) -> None:
        """Enable optional telemetry (PostHog)."""
        self._config["telemetry_enabled"] = True
        self._save_config(self._config)

    def disable(self) -> None:
        """Disable optional telemetry (PostHog). Threat signals still send."""
        self._config["telemetry_enabled"] = False
        self._save_config(self._config)

    def mark_not_first_run(self) -> None:
        """Mark that first run has completed."""
        self._config["first_run"] = False
        self._save_config(self._config)

    def get_status(self) -> dict[str, Any]:
        """Get current telemetry status."""
        return {
            "enabled": self.enabled,
            "offline_mode": self.offline_mode,
            "uuid": self.uuid,
            "config_file": str(CONFIG_FILE),
        }


# =============================================================================
# ASYNC SENDING
# =============================================================================

def _send_async(url: str, data: dict[str, Any], timeout: float = REQUEST_TIMEOUT) -> None:
    """Send data asynchronously (fire and forget)."""
    def _do_send() -> None:
        try:
            request = Request(
                url,
                data=json.dumps(data).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": f"deepsweep-cli/{VERSION}",
                },
                method="POST",
            )
            with urlopen(request, timeout=timeout):
                pass  # Fire and forget
        except Exception:
            pass  # Never fail, never block

    thread = threading.Thread(target=_do_send, daemon=True)
    thread.start()


# =============================================================================
# THREAT INTELLIGENCE (ESSENTIAL TIER)
# =============================================================================

def send_threat_signal(signal: ThreatSignal, offline_mode: bool = False) -> None:
    """
    Send threat intelligence signal to the flywheel.

    ESSENTIAL TIER - Always sent unless fully offline.
    Powers the community threat intelligence network.

    Args:
        signal: Threat signal data
        offline_mode: If True, don't send (for air-gapped environments)
    """
    if offline_mode:
        return

    # Always send threat signals (essential tier)
    _send_async(THREAT_INTEL_ENDPOINT, {
        "event": "threat_signal",
        "version": "1",
        **asdict(signal),
    })


def create_threat_signal(
    findings_count: int = 0,
    pattern_count: int = 0,
    score: int = 0,
    grade: str = "",
    duration_ms: int = 0,
    pattern_ids: list[str] | None = None,
    cve_matches: list[str] | None = None,
    severity_counts: dict[str, int] | None = None,
) -> ThreatSignal:
    """Create a threat signal from validation results."""
    is_ci, ci_provider = _detect_ci()

    return ThreatSignal(
        pattern_ids=pattern_ids or [],
        cve_matches=cve_matches or [],
        severity_counts=severity_counts or {},
        tool_context=[],  # Inferred from file types
        file_types=[],
        score=score,
        grade=grade,
        finding_count=findings_count,
        file_count=0,
        duration_ms=duration_ms,
        cli_version=VERSION,
        python_version=platform.python_version(),
        os_type=platform.system().lower(),
        is_ci=is_ci,
        ci_provider=ci_provider,
    )


# =============================================================================
# PRODUCT ANALYTICS (OPTIONAL TIER)
# =============================================================================

class TelemetryClient:
    """PostHog telemetry client (OPTIONAL TIER)."""

    def __init__(self) -> None:
        """Initialize telemetry client."""
        self.config = TelemetryConfig()
        self._start_time: float = time.time()

        # Initialize PostHog
        posthog.project_api_key = POSTHOG_API_KEY
        posthog.host = POSTHOG_HOST

    def track_command(
        self,
        command: str,
        exit_code: int = 0,
        findings_count: int | None = None,
        pattern_count: int | None = None,
        output_format: str | None = None,
        score: int | None = None,
        grade: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Track command execution (OPTIONAL TIER).

        This is PostHog product analytics - user can disable.
        Also sends threat signal (ESSENTIAL TIER) if validation command.
        """
        # Calculate duration
        duration_ms = int((time.time() - self._start_time) * 1000)

        # ESSENTIAL TIER: Send threat signal for validate commands
        if command == "validate" and not self.config.offline_mode:
            signal = create_threat_signal(
                findings_count=findings_count or 0,
                pattern_count=pattern_count or 0,
                score=score or 0,
                grade=grade or "",
                duration_ms=duration_ms,
            )
            send_threat_signal(signal, offline_mode=self.config.offline_mode)

        # OPTIONAL TIER: PostHog analytics (respects user preference)
        if not self.config.enabled or self.config.offline_mode:
            return

        properties: dict[str, Any] = {
            "command": command,
            "version": VERSION,
            "os": platform.system(),
            "os_version": platform.release(),
            "python_version": platform.python_version(),
            "duration_ms": duration_ms,
            "exit_code": exit_code,
            "first_run": self.config.first_run,
        }

        if findings_count is not None:
            properties["findings_count"] = findings_count
        if pattern_count is not None:
            properties["pattern_count"] = pattern_count
        if output_format is not None:
            properties["output_format"] = output_format
        if score is not None:
            properties["score"] = score
        if grade is not None:
            properties["grade"] = grade

        properties.update(kwargs)

        try:
            posthog.capture(
                distinct_id=self.config.uuid,
                event=f"deepsweep_{command}",
                properties=properties,
            )

            if self.config.first_run:
                self.config.mark_not_first_run()
        except Exception:
            pass

    def track_error(
        self,
        command: str,
        error_type: str,
        error_message: str | None = None,
    ) -> None:
        """Track error occurrence (OPTIONAL TIER)."""
        if not self.config.enabled or self.config.offline_mode:
            return

        properties: dict[str, Any] = {
            "command": command,
            "error_type": error_type,
            "version": VERSION,
            "os": platform.system(),
        }

        if error_message:
            sanitized = error_message.replace(str(Path.home()), "~")
            properties["error_message"] = sanitized[:200]

        try:
            posthog.capture(
                distinct_id=self.config.uuid,
                event="deepsweep_error",
                properties=properties,
            )
        except Exception:
            pass

    def identify(self) -> None:
        """Identify user with PostHog (OPTIONAL TIER)."""
        if not self.config.enabled or self.config.offline_mode:
            return

        try:
            posthog.identify(
                distinct_id=self.config.uuid,
                properties={
                    "version": VERSION,
                    "os": platform.system(),
                    "os_version": platform.release(),
                    "python_version": platform.python_version(),
                },
            )
        except Exception:
            pass

    def shutdown(self) -> None:
        """Shutdown telemetry client and flush events."""
        try:
            posthog.shutdown()
        except Exception:
            pass


# Global telemetry client
_client: TelemetryClient | None = None


def get_telemetry_client() -> TelemetryClient:
    """Get or create global telemetry client."""
    global _client
    if _client is None:
        _client = TelemetryClient()
    return _client
