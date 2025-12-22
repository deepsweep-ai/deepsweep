"""
Tests for telemetry system.

Design Standards:
- NO EMOJIS
- Test privacy guarantees
- Test opt-out functionality
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from deepsweep.telemetry import (
    TelemetryClient,
    TelemetryConfig,
)


@pytest.fixture
def temp_config_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """Create temporary config directory."""
    config_dir = tmp_path / ".deepsweep"
    config_file = config_dir / "config.json"

    # Patch module-level constants
    monkeypatch.setattr("deepsweep.telemetry.CONFIG_DIR", config_dir)
    monkeypatch.setattr("deepsweep.telemetry.CONFIG_FILE", config_file)

    return config_dir


class TestTelemetryConfig:
    """Test telemetry configuration management."""

    def test_creates_config_on_first_run(self, temp_config_dir: Path) -> None:
        """Test config file is created on first run."""
        config = TelemetryConfig()

        assert config.enabled is True
        assert config.first_run is True
        assert len(config.uuid) == 36  # UUID format

        # Check file exists
        config_file = temp_config_dir / "config.json"
        assert config_file.exists()

        # Check file contents
        with config_file.open() as f:
            data = json.load(f)
            assert data["telemetry_enabled"] is True
            assert data["first_run"] is True
            assert "uuid" in data

    def test_loads_existing_config(self, temp_config_dir: Path) -> None:
        """Test loading existing config from disk."""
        # Create config file
        config_file = temp_config_dir / "config.json"
        config_dir = temp_config_dir
        config_dir.mkdir(parents=True, exist_ok=True)

        existing_data = {
            "telemetry_enabled": False,
            "uuid": "test-uuid-1234",
            "first_run": False,
        }
        with config_file.open("w") as f:
            json.dump(existing_data, f)

        # Load config
        config = TelemetryConfig()

        assert config.enabled is False
        assert config.uuid == "test-uuid-1234"
        assert config.first_run is False

    def test_enable_telemetry(self, temp_config_dir: Path) -> None:
        """Test enabling telemetry."""
        config = TelemetryConfig()
        config.disable()
        assert config.enabled is False

        config.enable()
        assert config.enabled is True

        # Check file was updated
        config_file = temp_config_dir / "config.json"
        with config_file.open() as f:
            data = json.load(f)
            assert data["telemetry_enabled"] is True

    def test_disable_telemetry(self, temp_config_dir: Path) -> None:
        """Test disabling telemetry."""
        config = TelemetryConfig()
        assert config.enabled is True

        config.disable()
        assert config.enabled is False

        # Check file was updated
        config_file = temp_config_dir / "config.json"
        with config_file.open() as f:
            data = json.load(f)
            assert data["telemetry_enabled"] is False

    def test_mark_not_first_run(self, temp_config_dir: Path) -> None:
        """Test marking first run as complete."""
        config = TelemetryConfig()
        assert config.first_run is True

        config.mark_not_first_run()
        assert config.first_run is False

        # Check file was updated
        config_file = temp_config_dir / "config.json"
        with config_file.open() as f:
            data = json.load(f)
            assert data["first_run"] is False

    def test_get_status(self, temp_config_dir: Path) -> None:
        """Test getting telemetry status."""
        config = TelemetryConfig()
        status = config.get_status()

        assert "enabled" in status
        assert "uuid" in status
        assert "config_file" in status
        assert status["enabled"] is True
        assert len(status["uuid"]) == 36

    def test_handles_corrupted_config(self, temp_config_dir: Path) -> None:
        """Test handling corrupted config file."""
        config_dir = temp_config_dir
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "config.json"

        # Write corrupted JSON
        config_file.write_text("{ invalid json }")

        # Should create new config
        config = TelemetryConfig()
        assert config.enabled is True
        assert len(config.uuid) == 36


class TestTelemetryClient:
    """Test telemetry client."""

    @patch("deepsweep.telemetry.posthog")
    def test_track_command_when_enabled(
        self, mock_posthog: MagicMock, temp_config_dir: Path
    ) -> None:
        """Test tracking command when telemetry is enabled."""
        client = TelemetryClient()

        client.track_command(
            command="validate",
            exit_code=0,
            findings_count=5,
            pattern_count=16,
            output_format="json",
        )

        # Verify PostHog was called
        mock_posthog.capture.assert_called_once()
        call_args = mock_posthog.capture.call_args

        assert call_args[1]["event"] == "deepsweep_validate"
        assert call_args[1]["properties"]["command"] == "validate"
        assert call_args[1]["properties"]["exit_code"] == 0
        assert call_args[1]["properties"]["findings_count"] == 5
        assert call_args[1]["properties"]["pattern_count"] == 16
        assert call_args[1]["properties"]["output_format"] == "json"

    @patch("deepsweep.telemetry.posthog")
    def test_track_command_when_disabled(
        self, mock_posthog: MagicMock, temp_config_dir: Path
    ) -> None:
        """Test tracking command when telemetry is disabled."""
        client = TelemetryClient()
        client.config.disable()

        client.track_command(command="validate", exit_code=0)

        # Verify PostHog was NOT called
        mock_posthog.capture.assert_not_called()

    @patch("deepsweep.telemetry.posthog")
    def test_track_error(self, mock_posthog: MagicMock, temp_config_dir: Path) -> None:
        """Test tracking errors."""
        client = TelemetryClient()

        client.track_error(
            command="validate",
            error_type="ValidationError",
            error_message="File not found",
        )

        # Verify PostHog was called
        mock_posthog.capture.assert_called_once()
        call_args = mock_posthog.capture.call_args

        assert call_args[1]["event"] == "deepsweep_error"
        assert call_args[1]["properties"]["command"] == "validate"
        assert call_args[1]["properties"]["error_type"] == "ValidationError"
        assert call_args[1]["properties"]["error_message"] == "File not found"

    @patch("deepsweep.telemetry.posthog")
    def test_identify(self, mock_posthog: MagicMock, temp_config_dir: Path) -> None:
        """Test user identification."""
        client = TelemetryClient()
        client.identify()

        # Verify PostHog identify was called
        mock_posthog.identify.assert_called_once()
        call_args = mock_posthog.identify.call_args

        assert "distinct_id" in call_args[1]
        assert "properties" in call_args[1]
        assert "version" in call_args[1]["properties"]
        assert "os" in call_args[1]["properties"]

    @patch("deepsweep.telemetry.posthog")
    def test_shutdown(self, mock_posthog: MagicMock, temp_config_dir: Path) -> None:
        """Test shutdown flushes events."""
        client = TelemetryClient()
        client.shutdown()

        # Verify PostHog shutdown was called
        mock_posthog.shutdown.assert_called_once()

    @patch("deepsweep.telemetry.posthog")
    def test_marks_first_run_complete(self, mock_posthog: MagicMock, temp_config_dir: Path) -> None:
        """Test first run is marked complete after tracking."""
        client = TelemetryClient()
        assert client.config.first_run is True

        client.track_command(command="validate", exit_code=0)

        assert client.config.first_run is False

    @patch("deepsweep.telemetry.posthog")
    def test_sanitizes_error_messages(self, mock_posthog: MagicMock, temp_config_dir: Path) -> None:
        """Test error messages are sanitized to remove PII."""
        client = TelemetryClient()

        # Error with home directory path
        error_msg = f"File not found: {Path.home()}/my-secret-project/file.txt"
        client.track_error(
            command="validate",
            error_type="ValidationError",
            error_message=error_msg,
        )

        call_args = mock_posthog.capture.call_args
        sanitized = call_args[1]["properties"]["error_message"]

        # Should replace home directory with ~
        assert str(Path.home()) not in sanitized
        assert "~" in sanitized

    @patch("deepsweep.telemetry.posthog")
    def test_never_fails_on_telemetry_errors(
        self, mock_posthog: MagicMock, temp_config_dir: Path
    ) -> None:
        """Test telemetry errors don't crash the application."""
        # Make PostHog raise an exception
        mock_posthog.capture.side_effect = Exception("Network error")

        client = TelemetryClient()

        # Should not raise exception
        client.track_command(command="validate", exit_code=0)
        client.track_error(
            command="validate",
            error_type="ValidationError",
            error_message="Test",
        )
        client.identify()
        client.shutdown()


class TestTelemetryPrivacy:
    """Test telemetry privacy guarantees."""

    @patch("deepsweep.telemetry.posthog")
    def test_no_file_paths_in_telemetry(
        self, mock_posthog: MagicMock, temp_config_dir: Path
    ) -> None:
        """Test file paths are not included in telemetry."""
        client = TelemetryClient()

        client.track_command(
            command="validate",
            exit_code=0,
            findings_count=5,
        )

        call_args = mock_posthog.capture.call_args
        properties = call_args[1]["properties"]

        # Should not contain file paths
        assert "path" not in properties
        assert "file" not in properties
        assert "directory" not in properties

    @patch("deepsweep.telemetry.posthog")
    def test_no_code_content_in_telemetry(
        self, mock_posthog: MagicMock, temp_config_dir: Path
    ) -> None:
        """Test code content is not included in telemetry."""
        client = TelemetryClient()

        client.track_command(
            command="validate",
            exit_code=0,
            findings_count=5,
        )

        call_args = mock_posthog.capture.call_args
        properties = call_args[1]["properties"]

        # Should not contain code or finding details
        assert "code" not in properties
        assert "content" not in properties
        assert "finding" not in properties
        assert "pattern" not in properties

    @patch("deepsweep.telemetry.posthog")
    def test_only_aggregated_metrics(self, mock_posthog: MagicMock, temp_config_dir: Path) -> None:
        """Test only aggregated metrics are collected."""
        client = TelemetryClient()

        client.track_command(
            command="validate",
            exit_code=0,
            findings_count=5,
            pattern_count=16,
        )

        call_args = mock_posthog.capture.call_args
        properties = call_args[1]["properties"]

        # Should only have counts, not details
        assert "findings_count" in properties
        assert properties["findings_count"] == 5
        assert "pattern_count" in properties
        assert properties["pattern_count"] == 16
