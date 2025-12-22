"""
Telemetry system for DeepSweep.

Industry-standard opt-out telemetry following best practices from:
- Snyk CLI
- Vercel CLI
- GitHub CLI

Design Standards:
- NO EMOJIS
- Optimistic messaging
- Privacy-first (no PII, no code content)
- Async, non-blocking
- Respects user preferences
"""

import json
import platform
import time
import uuid
from pathlib import Path
from typing import Any, Final

import posthog

from deepsweep.constants import VERSION

# PostHog configuration
POSTHOG_API_KEY: Final[str] = "phc_2KxJqV5jZ9nY8wH3pL7mT6sN4vR1cX0bQ9dE8fG7hI6jK5lM4n"
POSTHOG_HOST: Final[str] = "https://us.i.posthog.com"

# Config paths
CONFIG_DIR: Final[Path] = Path.home() / ".deepsweep"
CONFIG_FILE: Final[Path] = CONFIG_DIR / "config.json"

# Default config
DEFAULT_CONFIG: Final[dict[str, Any]] = {
    "telemetry_enabled": True,
    "uuid": None,
    "first_run": True,
}


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
                # Merge with defaults for any missing keys
                return {**DEFAULT_CONFIG, **loaded}
        except (json.JSONDecodeError, OSError):
            # Corrupted config, recreate
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
        """Check if telemetry is enabled."""
        return self._config.get("telemetry_enabled", True)

    @property
    def uuid(self) -> str:
        """Get anonymous user UUID."""
        return self._config.get("uuid", "unknown")

    @property
    def first_run(self) -> bool:
        """Check if this is first run."""
        return self._config.get("first_run", False)

    def enable(self) -> None:
        """Enable telemetry."""
        self._config["telemetry_enabled"] = True
        self._save_config(self._config)

    def disable(self) -> None:
        """Disable telemetry."""
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
            "uuid": self.uuid,
            "config_file": str(CONFIG_FILE),
        }


class TelemetryClient:
    """PostHog telemetry client."""

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
        **kwargs: Any,
    ) -> None:
        """
        Track command execution.

        Args:
            command: Command name (e.g., "validate", "badge", "patterns")
            exit_code: Command exit code
            findings_count: Number of findings (for validate command)
            pattern_count: Number of patterns loaded
            output_format: Output format used (text, json, sarif)
            **kwargs: Additional event properties
        """
        if not self.config.enabled:
            return

        # Calculate duration
        duration_ms = int((time.time() - self._start_time) * 1000)

        # Build event properties
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

        # Add optional properties
        if findings_count is not None:
            properties["findings_count"] = findings_count

        if pattern_count is not None:
            properties["pattern_count"] = pattern_count

        if output_format is not None:
            properties["output_format"] = output_format

        # Add any extra kwargs
        properties.update(kwargs)

        try:
            # Track event
            posthog.capture(
                distinct_id=self.config.uuid,
                event=f"deepsweep_{command}",
                properties=properties,
            )

            # Mark first run as complete
            if self.config.first_run:
                self.config.mark_not_first_run()
        except Exception:
            # Never fail on telemetry errors
            pass

    def track_error(
        self,
        command: str,
        error_type: str,
        error_message: str | None = None,
    ) -> None:
        """
        Track error occurrence.

        Args:
            command: Command that errored
            error_type: Type of error (e.g., "ValidationError", "PatternError")
            error_message: Optional sanitized error message (no PII)
        """
        if not self.config.enabled:
            return

        properties: dict[str, Any] = {
            "command": command,
            "error_type": error_type,
            "version": VERSION,
            "os": platform.system(),
        }

        if error_message:
            # Sanitize error message (remove paths, etc.)
            sanitized = error_message.replace(str(Path.home()), "~")
            properties["error_message"] = sanitized[:200]  # Limit length

        try:
            posthog.capture(
                distinct_id=self.config.uuid,
                event="deepsweep_error",
                properties=properties,
            )
        except Exception:
            # Never fail on telemetry errors
            pass

    def identify(self) -> None:
        """
        Identify user with PostHog.

        This sets user properties for analytics segmentation.
        """
        if not self.config.enabled:
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
            # Never fail on telemetry errors
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
