"""CLI integration tests."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from deepsweep.cli import main


@pytest.fixture
def runner():
    return CliRunner()


class TestValidateCommand:
    """Tests for 'deepsweep validate' command."""

    def test_validate_clean_directory(self, runner: CliRunner, temp_dir: Path):
        result = runner.invoke(main, ["validate", str(temp_dir)])

        assert result.exit_code == 0
        assert "Ship with vibes" in result.output

    def test_validate_with_malicious_file(self, runner: CliRunner, malicious_cursorrules: Path):
        result = runner.invoke(main, ["validate", str(malicious_cursorrules.parent)])

        assert "CURSOR-RULES-001" in result.output
        assert "[FAIL]" in result.output

    def test_no_color_flag(self, runner: CliRunner, temp_dir: Path):
        result = runner.invoke(main, ["validate", str(temp_dir), "--no-color"])

        assert "\033[" not in result.output

    def test_json_output(self, runner: CliRunner, temp_dir: Path):
        result = runner.invoke(main, ["validate", str(temp_dir), "--format", "json"])

        assert result.exit_code == 0
        assert '"score"' in result.output
        assert '"findings"' in result.output

    def test_fail_on_critical(self, runner: CliRunner, malicious_cursorrules: Path):
        result = runner.invoke(main, [
            "validate",
            str(malicious_cursorrules.parent),
            "--fail-on", "critical"
        ])

        # CURSOR-RULES-001 is CRITICAL, should fail
        assert result.exit_code == 1


class TestHelpCommand:
    """Tests for help output."""

    def test_help_includes_vibe_coding(self, runner: CliRunner):
        result = runner.invoke(main, ["--help"])

        assert "vibe coding" in result.output.lower()

    def test_version(self, runner: CliRunner):
        result = runner.invoke(main, ["--version"])

        assert "1.2.0" in result.output


class TestBadgeCommand:
    """Tests for 'deepsweep badge' command."""

    def test_badge_creates_file(self, runner: CliRunner, temp_dir: Path):
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(main, ["badge", "--format", "json"])

            assert result.exit_code == 0
            assert Path("badge.svg").exists() or "[PASS]" in result.output


class TestPatternsCommand:
    """Tests for 'deepsweep patterns' command."""

    def test_lists_patterns(self, runner: CliRunner):
        result = runner.invoke(main, ["patterns"])

        assert result.exit_code == 0
        assert "CURSOR-RULES-001" in result.output
        assert "MCP-POISON-001" in result.output
