"""MCP poisoning detector tests."""

import pytest
import json
from pathlib import Path

from deepsweep_ai.detectors.mcp_poisoning import MCPPoisoningDetector
from deepsweep_ai.scanner import Severity


class TestMCPPoisoningDetector:
    """Test MCPPoisoningDetector."""

    @pytest.fixture
    def detector(self):
        return MCPPoisoningDetector()

    def test_detect_auto_start(self, temp_dir, detector):
        """Test detection of auto-start servers."""
        config = {
            "mcpServers": {
                "malicious": {
                    "command": "node",
                    "autoStart": True
                }
            }
        }
        filepath = temp_dir / "mcp.json"
        filepath.write_text(json.dumps(config))

        findings = detector.scan_file(filepath)

        assert len(findings) > 0
        assert any(f.id == "DS-MCP-001" for f in findings)
        assert any(f.severity == Severity.CRITICAL for f in findings)

    def test_detect_suspicious_server_name(self, temp_dir, detector):
        """Test detection of suspicious server names."""
        config = {
            "mcpServers": {
                "shell-executor": {
                    "command": "node"
                },
                "admin-access": {
                    "command": "python"
                }
            }
        }
        filepath = temp_dir / "mcp.json"
        filepath.write_text(json.dumps(config))

        findings = detector.scan_file(filepath)

        assert len(findings) > 0
        assert any(f.id == "DS-MCP-002" for f in findings)

    def test_detect_external_url(self, temp_dir, detector):
        """Test detection of external MCP server URLs."""
        config = {
            "mcpServers": {
                "remote": {
                    "url": "https://attacker.com/mcp"
                }
            }
        }
        filepath = temp_dir / "mcp.json"
        filepath.write_text(json.dumps(config))

        findings = detector.scan_file(filepath)

        assert len(findings) > 0
        assert any(f.id == "DS-MCP-004" for f in findings)

    def test_safe_local_server(self, temp_dir, detector):
        """Test that safe local servers produce no critical findings."""
        config = {
            "mcpServers": {
                "filesystem": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem"]
                }
            }
        }
        filepath = temp_dir / "mcp.json"
        filepath.write_text(json.dumps(config))

        findings = detector.scan_file(filepath)

        # Should be empty or only low severity
        critical_high = [f for f in findings if f.severity in (Severity.CRITICAL, Severity.HIGH)]
        assert len(critical_high) == 0
