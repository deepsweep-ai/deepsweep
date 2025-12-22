"""CLI tests."""

from click.testing import CliRunner
from deepsweep_ai.cli import main
from deepsweep_ai import __version__
import json


def test_version():
    """Test version output."""
    r = CliRunner().invoke(main, ["--version"])
    assert r.exit_code == 0
    assert __version__ in r.output


def test_scan_safe(safe_repo):
    """Test scanning a safe directory."""
    r = CliRunner().invoke(main, ["scan", str(safe_repo), "--format", "json"])
    assert r.exit_code == 0
    data = json.loads(r.output)
    assert data["safe"] == True


def test_scan_malicious(malicious_cursor):
    """Test scanning a directory with malicious content."""
    r = CliRunner().invoke(main, ["scan", str(malicious_cursor), "--format", "json"])
    # Should exit 0 in observe mode (default)
    assert r.exit_code == 0
    data = json.loads(r.output)
    assert data["safe"] == False
    assert data["findings_count"] > 0


def test_scan_enforce_fails(malicious_cursor):
    """Test that enforce mode fails on malicious content."""
    r = CliRunner().invoke(main, ["scan", str(malicious_cursor), "--enforce", "--format", "json"])
    # Should exit 1 in enforce mode with findings
    assert r.exit_code == 1


def test_scan_sarif_output(malicious_cursor):
    """Test SARIF output format."""
    r = CliRunner().invoke(main, ["scan", str(malicious_cursor), "--format", "sarif"])
    assert r.exit_code == 0
    data = json.loads(r.output)
    assert "$schema" in data
    assert data["version"] == "2.1.0"
    assert "runs" in data
