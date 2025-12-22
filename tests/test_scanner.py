"""Scanner unit tests."""

import pytest
from pathlib import Path

from deepsweep_ai.scanner import Scanner, ScanResult, Severity
from deepsweep_ai.config import Config, Mode


class TestScanner:
    """Test Scanner class."""

    def test_scan_empty_directory(self, temp_dir, default_config):
        """Test scanning empty directory."""
        scanner = Scanner(default_config)
        result = scanner.scan(str(temp_dir))

        assert isinstance(result, ScanResult)
        assert result.safe == True
        assert result.score == 100
        assert len(result.findings) == 0

    def test_scan_with_findings(self, temp_dir, malicious_cursorrules, default_config):
        """Test scanning directory with malicious content."""
        scanner = Scanner(default_config)
        result = scanner.scan(str(temp_dir))

        assert result.safe == False
        assert result.score < 100
        assert len(result.findings) > 0

        # Should find critical issues
        critical_findings = [f for f in result.findings if f.severity == Severity.CRITICAL]
        assert len(critical_findings) > 0

    def test_scan_result_to_dict(self, temp_dir, malicious_cursorrules, default_config):
        """Test ScanResult serialization."""
        scanner = Scanner(default_config)
        result = scanner.scan(str(temp_dir))

        data = result.to_dict()

        assert "scan_id" in data
        assert "timestamp" in data
        assert "safe" in data
        assert "score" in data
        assert "findings" in data
        assert isinstance(data["findings"], list)

    def test_scan_result_to_sarif(self, temp_dir, malicious_cursorrules, default_config):
        """Test SARIF conversion."""
        scanner = Scanner(default_config)
        result = scanner.scan(str(temp_dir))

        sarif = result.to_sarif()

        assert sarif["$schema"] == "https://json.schemastore.org/sarif-2.1.0.json"
        assert sarif["version"] == "2.1.0"
        assert len(sarif["runs"]) == 1
        assert "tool" in sarif["runs"][0]
        assert "results" in sarif["runs"][0]

    def test_scan_status_passing(self, temp_dir, safe_cursorrules, default_config):
        """Test status is 'passing' for safe content."""
        scanner = Scanner(default_config)
        result = scanner.scan(str(temp_dir))

        assert result.status == "passing"

    def test_scan_status_critical(self, temp_dir, malicious_cursorrules, default_config):
        """Test status reflects severity."""
        scanner = Scanner(default_config)
        result = scanner.scan(str(temp_dir))

        assert result.status in ("critical", "warning")


class TestScannerConfig:
    """Test Scanner with different configurations."""

    def test_scanner_observe_mode(self, temp_dir, malicious_cursorrules):
        """Test scanner in observe mode."""
        config = Config()
        config.mode = Mode.OBSERVE
        scanner = Scanner(config)

        result = scanner.scan(str(temp_dir))

        assert len(result.findings) > 0
        assert result.mode == Mode.OBSERVE

    def test_scanner_enforce_mode(self, temp_dir, malicious_cursorrules):
        """Test scanner in enforce mode."""
        config = Config()
        config.mode = Mode.ENFORCE
        scanner = Scanner(config)

        result = scanner.scan(str(temp_dir))

        assert result.mode == Mode.ENFORCE
        assert len(result.findings) > 0
