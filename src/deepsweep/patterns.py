"""
Pattern matching engine for DeepSweep.

Loads and applies detection patterns to content.
"""

import re
from dataclasses import dataclass, field
from typing import Callable

from deepsweep.models import Finding, Severity


@dataclass(frozen=True)
class Pattern:
    """A detection pattern."""

    id: str
    name: str
    severity: Severity
    description: str
    regex: str
    file_types: tuple[str, ...]
    remediation: str
    cve: str | None = None
    owasp: str | None = None

    def matches(self, content: str, file_path: str) -> list[tuple[int, str]]:
        """
        Check if pattern matches content.

        Returns list of (line_number, matched_text) tuples.
        """
        # Check if file type matches
        if not any(file_path.endswith(ft) or ft in file_path for ft in self.file_types):
            return []

        matches: list[tuple[int, str]] = []
        try:
            compiled = re.compile(self.regex, re.IGNORECASE | re.MULTILINE)
            lines = content.split("\n")

            for line_num, line in enumerate(lines, start=1):
                if compiled.search(line):
                    matches.append((line_num, line.strip()[:100]))
        except re.error:
            # Invalid regex - skip this pattern
            pass

        return matches

    def to_finding(self, file_path: str, line: int, matched_text: str) -> Finding:
        """Create a Finding from this pattern match."""
        return Finding(
            severity=self.severity,
            file_path=file_path,
            line=line,
            message=f"{self.description}: {matched_text[:50]}..." if len(matched_text) > 50 else f"{self.description}: {matched_text}",
            pattern_id=self.id,
            cve=self.cve,
            owasp=self.owasp,
            remediation=self.remediation,
        )


# Core detection patterns
PATTERNS: tuple[Pattern, ...] = (
    # Cursor patterns
    Pattern(
        id="CURSOR-RULES-001",
        name="Instruction Override",
        severity=Severity.CRITICAL,
        description="Prompt injection detected",
        regex=r"(?i)(ignore|disregard|forget|override)\s+(all\s+)?(previous|prior|above|earlier)\s+(instruction|rule|guideline)",
        file_types=(".cursorrules", "cursor.rules", ".cursor/rules"),
        remediation="Remove instruction override patterns from rules file",
        cve="CVE-2025-43570",
        owasp="ASI01",
    ),
    Pattern(
        id="CURSOR-RULES-002",
        name="Role Hijacking",
        severity=Severity.HIGH,
        description="Role hijack attempt detected",
        regex=r"(?i)you\s+are\s+(now|actually|really)\s+(a|an|the)",
        file_types=(".cursorrules", "cursor.rules", ".cursor/rules"),
        remediation="Remove role reassignment instructions",
        cve="CVE-2025-43570",
        owasp="ASI01",
    ),
    Pattern(
        id="CURSOR-RULES-003",
        name="Data Exfiltration",
        severity=Severity.CRITICAL,
        description="Data exfiltration pattern detected",
        regex=r"(?i)(send|post|transmit|upload|exfiltrate)\s+.*(to|toward)\s+(http|https|ftp|wss?)://",
        file_types=(".cursorrules", "cursor.rules", ".cursor/rules"),
        remediation="Remove external URL references from rules",
        cve="CVE-2025-43570",
        owasp="ASI09",
    ),
    Pattern(
        id="CURSOR-RULES-004",
        name="Hidden Unicode",
        severity=Severity.MEDIUM,
        description="Hidden Unicode characters detected",
        regex=r"[\u200B-\u200D\uFEFF\u2060]",
        file_types=(".cursorrules", "cursor.rules", ".cursor/rules"),
        remediation="Remove invisible Unicode characters (use hex editor to inspect)",
        owasp="ASI01",
    ),

    # Copilot patterns
    Pattern(
        id="COPILOT-INJ-001",
        name="Safety Override",
        severity=Severity.HIGH,
        description="Safety override instruction detected",
        regex=r"(?i)(ignore|override|bypass|disregard)\s+(safety|security|previous|all)",
        file_types=("copilot-instructions.md", ".github/copilot-instructions.md"),
        remediation="Remove safety override instructions",
        cve="CVE-2025-43102",
        owasp="ASI01",
    ),
    Pattern(
        id="COPILOT-INJ-002",
        name="Code Injection Instruction",
        severity=Severity.CRITICAL,
        description="Dangerous code injection instruction",
        regex=r"(?i)always\s+(include|add|insert|embed)\s+.*(eval|exec|system|\$\()",
        file_types=("copilot-instructions.md", ".github/copilot-instructions.md"),
        remediation="Remove instructions to include dangerous functions",
        cve="CVE-2025-43102",
        owasp="ASI01",
    ),
    Pattern(
        id="COPILOT-INJ-003",
        name="Known Jailbreak",
        severity=Severity.HIGH,
        description="Known jailbreak pattern detected",
        regex=r"(?i)\bDAN\b|\bjailbreak\b|\bunrestricted\b",
        file_types=("copilot-instructions.md", ".github/copilot-instructions.md"),
        remediation="Remove jailbreak terminology",
        cve="CVE-2025-43102",
        owasp="ASI01",
    ),

    # Claude patterns
    Pattern(
        id="CLAUDE-WS-001",
        name="Auth Disabled",
        severity=Severity.CRITICAL,
        description="WebSocket authentication disabled",
        regex=r'"auth"\s*:\s*(false|"false"|0)',
        file_types=("claude_desktop_config.json", ".claude/config.json"),
        remediation="Enable authentication: set auth to true",
        cve="CVE-2025-52882",
        owasp="ASI07",
    ),
    Pattern(
        id="CLAUDE-WS-002",
        name="Public Bind",
        severity=Severity.HIGH,
        description="WebSocket bound to public interface",
        regex=r'"bind"\s*:\s*"0\.0\.0\.0"',
        file_types=("claude_desktop_config.json", ".claude/config.json"),
        remediation='Bind to localhost: set bind to "127.0.0.1"',
        cve="CVE-2025-52882",
        owasp="ASI07",
    ),
    Pattern(
        id="CLAUDE-WS-003",
        name="Wildcard CORS",
        severity=Severity.MEDIUM,
        description="Wildcard CORS origin allowed",
        regex=r'"allowedOrigins"\s*:\s*\[\s*"\*"\s*\]',
        file_types=("claude_desktop_config.json", ".claude/config.json"),
        remediation="Specify explicit allowed origins instead of wildcard",
        owasp="ASI07",
    ),

    # MCP patterns
    Pattern(
        id="MCP-POISON-001",
        name="Dynamic Package Execution",
        severity=Severity.HIGH,
        description="MCP server uses dynamic package execution",
        regex=r'"command"\s*:\s*"(npx|npm\s+exec|bunx|pnpm\s+dlx)"',
        file_types=("mcp.json", ".mcp/config.json", "claude_desktop_config.json"),
        remediation="Pin MCP server to specific version or use local binary",
        cve="CVE-2025-54135",
        owasp="ASI03",
    ),
    Pattern(
        id="MCP-POISON-002",
        name="Remote MCP Server",
        severity=Severity.MEDIUM,
        description="MCP server connects to remote URL",
        regex=r'"url"\s*:\s*"https?://(?!localhost|127\.0\.0\.1)',
        file_types=("mcp.json", ".mcp/config.json", "claude_desktop_config.json"),
        remediation="Verify remote MCP server is from trusted source",
        cve="CVE-2025-54135",
        owasp="ASI03",
    ),
    Pattern(
        id="MCP-POISON-003",
        name="Permissive Deno Args",
        severity=Severity.MEDIUM,
        description="MCP server has permissive Deno arguments",
        regex=r'"args"\s*:\s*\[[^\]]*"--allow-(read|write|net|run|all)"',
        file_types=("mcp.json", ".mcp/config.json", "claude_desktop_config.json"),
        remediation="Minimize --allow-* permissions to only what is required",
        owasp="ASI03",
    ),
    Pattern(
        id="MCP-POISON-004",
        name="Sensitive Env Vars",
        severity=Severity.LOW,
        description="MCP server configuration exposes sensitive environment variables",
        regex=r'"env"\s*:\s*\{[^}]*"(API_KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)"',
        file_types=("mcp.json", ".mcp/config.json", "claude_desktop_config.json"),
        remediation="Move sensitive values to secure credential storage",
        owasp="ASI09",
    ),

    # Windsurf patterns
    Pattern(
        id="WINDSURF-EXFIL-001",
        name="Data Exfiltration",
        severity=Severity.CRITICAL,
        description="Data exfiltration pattern detected",
        regex=r"(?i)(send|post|upload|transmit|forward)\s+.*(code|context|secrets?|env|credentials?)",
        file_types=(".windsurfrules", ".windsurf/rules"),
        remediation="Remove data transmission instructions",
        cve="CVE-2025-55284",
        owasp="ASI09",
    ),
    Pattern(
        id="WINDSURF-EXFIL-002",
        name="External Webhook",
        severity=Severity.HIGH,
        description="External webhook configuration detected",
        regex=r"(?i)(webhook|callback|endpoint).*https?://",
        file_types=(".windsurfrules", ".windsurf/rules"),
        remediation="Remove or verify external webhook configurations",
        cve="CVE-2025-55284",
        owasp="ASI09",
    ),
)


def get_all_patterns() -> tuple[Pattern, ...]:
    """Get all registered detection patterns."""
    return PATTERNS


def get_pattern_count() -> int:
    """Get total number of patterns."""
    return len(PATTERNS)
