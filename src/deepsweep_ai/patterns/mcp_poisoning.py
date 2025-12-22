"""
MCP (Model Context Protocol) Poisoning Detection

Covers:
- Auto-start servers
- Suspicious server configurations
- Tool shadowing
- Rug pull patterns
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Pattern:
    id: str
    title: str
    description: str
    severity: str
    category: str
    regex: str
    file_patterns: List[str]
    cve_ids: List[str]
    remediation: str


MCP_POISONING_PATTERNS: List[Pattern] = [
    Pattern(
        id="DS-MCP-001",
        title="MCP Auto-Start Enabled",
        description="MCP server configured to start automatically without user approval",
        severity="critical",
        category="mcp_poisoning",
        regex=r'"autoStart"\s*:\s*true|autoStart:\s*true',
        file_patterns=["mcp.json", "mcp-config.json", ".cursor/mcp.json", "claude_desktop_config.json"],
        cve_ids=["CVE-2025-54135"],
        remediation="Set autoStart to false for all MCP servers",
    ),
    Pattern(
        id="DS-MCP-002",
        title="Suspicious MCP Server Name",
        description="MCP server with name suggesting malicious intent",
        severity="high",
        category="mcp_poisoning",
        regex=r'"(mcpServers|servers)"\s*:\s*\{[^}]*"(shell|exec|cmd|system|eval|hack|exploit|backdoor|payload)',
        file_patterns=["mcp.json", "mcp-config.json", ".cursor/mcp.json"],
        cve_ids=["CVE-2025-54135"],
        remediation="Review and remove suspicious MCP server configurations",
    ),
    Pattern(
        id="DS-MCP-003",
        title="MCP Shell Command Execution",
        description="MCP server configured to execute shell commands",
        severity="critical",
        category="mcp_poisoning",
        regex=r'"command"\s*:\s*"(bash|sh|cmd|powershell|zsh|/bin/)',
        file_patterns=["mcp.json", "mcp-config.json", ".cursor/mcp.json"],
        cve_ids=["CVE-2025-6514"],
        remediation="Avoid MCP servers that execute shell commands directly",
    ),
    Pattern(
        id="DS-MCP-004",
        title="External MCP Server URL",
        description="MCP server connecting to external/untrusted URL",
        severity="high",
        category="mcp_poisoning",
        regex=r'"(url|endpoint|server)"\s*:\s*"https?://(?!localhost|127\.0\.0\.1)',
        file_patterns=["mcp.json", "mcp-config.json", ".cursor/mcp.json"],
        cve_ids=["CVE-2025-6514"],
        remediation="Only use trusted, local MCP servers or verified remote endpoints",
    ),
    Pattern(
        id="DS-MCP-005",
        title="MCP npx/uvx Execution",
        description="MCP server using npx or uvx which can execute arbitrary packages",
        severity="high",
        category="mcp_poisoning",
        regex=r'"command"\s*:\s*"(npx|uvx|pnpx)',
        file_patterns=["mcp.json", "mcp-config.json", ".cursor/mcp.json"],
        cve_ids=["CVE-2025-49596"],
        remediation="Pin MCP server packages to specific versions instead of using npx/uvx",
    ),
    Pattern(
        id="DS-MCP-006",
        title="MCP Environment Variable Injection",
        description="MCP server with suspicious environment variable configuration",
        severity="medium",
        category="mcp_poisoning",
        regex=r'"env"\s*:\s*\{[^}]*(SECRET|KEY|TOKEN|PASSWORD|CREDENTIAL)[^}]*\}',
        file_patterns=["mcp.json", "mcp-config.json", ".cursor/mcp.json"],
        cve_ids=["CVE-2025-53776"],
        remediation="Review environment variables passed to MCP servers",
    ),
    Pattern(
        id="DS-MCP-007",
        title="Tool Shadowing Pattern",
        description="MCP configuration that may shadow legitimate tools",
        severity="high",
        category="mcp_poisoning",
        regex=r'"(read_file|write_file|execute|run_command|shell|terminal)"',
        file_patterns=["mcp.json", "mcp-config.json"],
        cve_ids=[],
        remediation="Verify MCP tools don't shadow built-in IDE functionality",
    ),
]
