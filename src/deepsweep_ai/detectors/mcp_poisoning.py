"""
MCP (Model Context Protocol) Poisoning Detector

Detects malicious MCP server configurations and tool poisoning attacks.
Covers CVE-2025-54135 (Cursor MCP auto-start) and related vulnerabilities.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Dict, Any

from deepsweep_ai.detectors.base import BaseDetector
from deepsweep_ai.scanner import Finding, Severity


class MCPPoisoningDetector(BaseDetector):
    """Detect MCP poisoning vulnerabilities."""

    # Known safe MCP server names (official Model Context Protocol servers)
    SAFE_SERVERS = [
        "filesystem", "github", "gitlab", "slack", "google-drive", "postgres",
        "sqlite", "redis", "mongodb", "puppeteer", "brave-search", "fetch",
        "memory", "everart", "sequential-thinking", "aws-kb-retrieval",
        "sentry", "raygun", "axiom", "time", "docker", "kubernetes",
    ]

    # Known suspicious MCP server patterns
    SUSPICIOUS_SERVERS = [
        "shell", "exec", "command", "terminal", "bash", "system",
        "admin", "root", "sudo",
    ]

    # File patterns that are MCP configs
    MCP_CONFIG_PATTERNS = [
        "mcp.json", "mcp-config.json", "claude_desktop_config.json",
        "mcp.yaml", "mcp.yml",
    ]

    def scan_file(self, path: Path) -> List[Finding]:
        """Scan file for MCP poisoning patterns."""
        findings: List[Finding] = []

        # Check if this is an MCP config file
        if not any(pattern in path.name.lower() for pattern in self.MCP_CONFIG_PATTERNS):
            # Also check content for MCP patterns
            content = self._read_file(path)
            if "mcpServers" not in content and "mcp_servers" not in content:
                return findings

        content = self._read_file(path)
        if not content:
            return findings

        # Try to parse as JSON
        try:
            if path.suffix in (".json",):
                config = json.loads(content)
                findings.extend(self._analyze_mcp_config(path, config))
        except json.JSONDecodeError:
            pass

        # Pattern-based detection
        findings.extend(self._pattern_scan(path, content))

        return findings

    def _analyze_mcp_config(self, path: Path, config: Dict[str, Any]) -> List[Finding]:
        """Analyze parsed MCP configuration."""
        findings: List[Finding] = []

        servers = config.get("mcpServers", config.get("mcp_servers", {}))

        for server_name, server_config in servers.items():
            # Check for auto-start (CVE-2025-54135)
            if server_config.get("autoStart", server_config.get("auto_start", False)):
                findings.append(Finding(
                    id="DS-MCP-001",
                    title="MCP Server Auto-Start Enabled",
                    description=f"MCP server '{server_name}' has auto-start enabled. This can execute code without user consent.",
                    severity=Severity.CRITICAL,
                    file_path=str(path),
                    line_number=None,
                    code_snippet=f"Server: {server_name}",
                    cve_ids=["CVE-2025-54135"],
                    affected_tools=["Cursor"],
                    remediation="Disable auto-start for all MCP servers. Require explicit user approval.",
                ))

            # Check for suspicious server names (skip known-safe servers)
            server_lower = server_name.lower()
            if server_lower not in self.SAFE_SERVERS:
                for suspicious in self.SUSPICIOUS_SERVERS:
                    if suspicious in server_lower:
                        findings.append(Finding(
                            id="DS-MCP-002",
                            title="Suspicious MCP Server Name",
                            description=f"MCP server '{server_name}' has suspicious name suggesting elevated privileges.",
                            severity=Severity.HIGH,
                            file_path=str(path),
                            line_number=None,
                            code_snippet=f"Server: {server_name}",
                            cve_ids=[],
                            affected_tools=["All MCP clients"],
                            remediation="Audit server purpose. Remove or rename suspicious servers.",
                        ))
                        break

            # Check for command execution in config
            command = server_config.get("command", "")
            args = server_config.get("args", [])

            if isinstance(command, str) and any(x in command.lower() for x in ["sh", "bash", "cmd", "powershell"]):
                findings.append(Finding(
                    id="DS-MCP-003",
                    title="MCP Server Executes Shell",
                    description=f"MCP server '{server_name}' executes shell commands directly.",
                    severity=Severity.HIGH,
                    file_path=str(path),
                    line_number=None,
                    code_snippet=f"Command: {command}",
                    cve_ids=[],
                    affected_tools=["All MCP clients"],
                    remediation="Use specific executables instead of shell wrappers.",
                ))

            # Check for external URLs
            url = server_config.get("url", server_config.get("endpoint", ""))
            if url and not url.startswith(("localhost", "127.0.0.1", "::1")):
                if url.startswith(("http://", "https://", "ws://", "wss://")):
                    findings.append(Finding(
                        id="DS-MCP-004",
                        title="External MCP Server URL",
                        description=f"MCP server '{server_name}' connects to external URL: {url}",
                        severity=Severity.HIGH,
                        file_path=str(path),
                        line_number=None,
                        code_snippet=f"URL: {url}",
                        cve_ids=[],
                        affected_tools=["All MCP clients"],
                        remediation="Use local MCP servers. Audit and allowlist external connections.",
                    ))

        return findings

    def _pattern_scan(self, path: Path, content: str) -> List[Finding]:
        """Pattern-based scanning for MCP issues."""
        findings: List[Finding] = []
        lines = content.split("\n")

        patterns = [
            {
                "id": "DS-MCP-005",
                "pattern": r"(?i)\"?auto.?start\"?\s*:\s*true",
                "title": "MCP Auto-Start Detected",
                "description": "Auto-start configuration found in MCP config.",
                "severity": Severity.CRITICAL,
            },
            {
                "id": "DS-MCP-006",
                "pattern": r"(?i)\"?trusted\"?\s*:\s*true",
                "title": "MCP Server Marked Trusted",
                "description": "Server explicitly marked as trusted. This bypasses security checks.",
                "severity": Severity.HIGH,
            },
            {
                "id": "DS-MCP-007",
                "pattern": r"(?i)\"?skipVerification\"?\s*:\s*true",
                "title": "MCP Verification Skipped",
                "description": "Server verification is disabled. This allows unsigned/unverified servers.",
                "severity": Severity.HIGH,
            },
        ]

        for pattern_def in patterns:
            pattern = re.compile(pattern_def["pattern"])
            for line_num, line in enumerate(lines, 1):
                if pattern.search(line):
                    findings.append(Finding(
                        id=pattern_def["id"],
                        title=pattern_def["title"],
                        description=pattern_def["description"],
                        severity=pattern_def["severity"],
                        file_path=str(path),
                        line_number=line_num,
                        code_snippet=line.strip()[:200],
                        cve_ids=["CVE-2025-54135"] if "auto" in pattern_def["id"].lower() else [],
                        affected_tools=["Cursor", "Claude Desktop", "All MCP clients"],
                        remediation="Review and disable auto-trust settings.",
                    ))

        return findings
