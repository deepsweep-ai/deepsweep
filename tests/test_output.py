"""Tests for CLI output formatting."""

import os
import re

import pytest

from deepsweep.models import Finding, FileResult, Severity, ValidationResult
from deepsweep.output import OutputConfig, OutputFormatter, supports_color


@pytest.fixture
def formatter():
    """Create a no-color formatter for consistent testing."""
    config = OutputConfig(use_color=False)
    return OutputFormatter(config)


@pytest.fixture
def sample_result():
    """Create a sample validation result."""
    finding = Finding(
        severity=Severity.HIGH,
        file_path=".cursorrules",
        line=5,
        message="Prompt injection detected",
        pattern_id="CURSOR-RULES-001",
        cve="CVE-2025-43570",
        remediation="Remove instruction override patterns",
    )
    file_result = FileResult(
        path=".cursorrules",
        findings=(finding,),
    )
    return ValidationResult(
        files=(file_result,),
        pattern_count=20,
    )


class TestNoEmojis:
    """Verify no emojis appear anywhere in output."""

    EMOJI_PATTERN = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "]+"
    )

    def test_header_no_emojis(self, formatter: OutputFormatter):
        header = formatter.format_header("1.0.0")
        assert not self.EMOJI_PATTERN.search(header)

    def test_summary_no_emojis(self, formatter: OutputFormatter, sample_result: ValidationResult):
        summary = formatter.format_summary(sample_result)
        assert not self.EMOJI_PATTERN.search(summary)

    def test_finding_no_emojis(self, formatter: OutputFormatter):
        finding = Finding(
            severity=Severity.CRITICAL,
            file_path="test.txt",
            line=1,
            message="Test finding",
            pattern_id="TEST-001",
            remediation="Fix it",
        )
        output = formatter.format_finding(finding)
        assert not self.EMOJI_PATTERN.search(output)


class TestOptimisticMessaging:
    """Verify optimistic (Wiz-style) messaging."""

    def test_uses_items_to_review(self, formatter: OutputFormatter, sample_result: ValidationResult):
        summary = formatter.format_summary(sample_result)

        assert "vulnerabilities" not in summary.lower()
        assert "item" in summary.lower()

    def test_uses_how_to_address(self, formatter: OutputFormatter):
        finding = Finding(
            severity=Severity.HIGH,
            file_path="test.txt",
            line=1,
            message="Test",
            pattern_id="TEST-001",
            remediation="Do the thing",
        )
        output = formatter.format_finding(finding)

        assert "How to address" in output
        assert "Fix this vulnerability" not in output

    def test_encouraging_next_steps(self, formatter: OutputFormatter, sample_result: ValidationResult):
        next_steps = formatter.format_next_steps(sample_result)

        # Should be encouraging, not scary
        assert "fix" not in next_steps.lower() or "let's" in next_steps.lower()
        assert "critical failure" not in next_steps.lower()


class TestASCIISymbols:
    """Verify ASCII symbols are used."""

    def test_pass_symbol(self, formatter: OutputFormatter):
        output = formatter.format_file_pass("test.txt")
        assert "[PASS]" in output

    def test_fail_symbol(self, formatter: OutputFormatter):
        finding = Finding(
            severity=Severity.CRITICAL,
            file_path="test.txt",
            line=1,
            message="Test",
            pattern_id="TEST-001",
        )
        output = formatter.format_finding(finding)
        assert "[FAIL]" in output

    def test_warn_symbol(self, formatter: OutputFormatter):
        finding = Finding(
            severity=Severity.MEDIUM,
            file_path="test.txt",
            line=1,
            message="Test",
            pattern_id="TEST-001",
        )
        output = formatter.format_finding(finding)
        assert "[WARN]" in output


class TestNoColorSupport:
    """Verify NO_COLOR environment variable support."""

    def test_no_color_env_disables_color(self, monkeypatch):
        monkeypatch.setenv("NO_COLOR", "1")
        assert not supports_color()

    def test_deepsweep_no_color_env(self, monkeypatch):
        monkeypatch.setenv("DEEPSWEEP_NO_COLOR", "1")
        assert not supports_color()

    def test_no_ansi_when_color_disabled(self, formatter: OutputFormatter):
        output = formatter.format_file_pass("test.txt")
        assert "\033[" not in output
