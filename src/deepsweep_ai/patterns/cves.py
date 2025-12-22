"""
CVE Database - December 2025 AI IDE Vulnerabilities

Sources:
- IDEsaster research (December 2025)
- OWASP Top 10 for Agentic Applications
- Vendor security advisories
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CVE:
    id: str
    cvss: float
    severity: str  # critical, high, medium, low
    title: str
    description: str
    affected_tools: List[str]
    attack_vector: str
    pattern_ids: List[str]  # DeepSweep pattern IDs that detect this
    references: List[str]
    published: str  # ISO date


CVE_DATABASE: List[CVE] = [
    CVE(
        id="CVE-2025-53773",
        cvss=7.8,
        severity="high",
        title="Rule File Backdoor - YOLO Mode Activation",
        description="AI coding assistants can be manipulated via .cursorrules or similar files to enable automatic code execution without user confirmation (YOLO mode), allowing arbitrary command execution.",
        affected_tools=["GitHub Copilot", "Cursor", "Windsurf"],
        attack_vector="Malicious repository with crafted rules file",
        pattern_ids=["DS-PI-001", "DS-PI-002", "DS-PI-007"],
        references=["https://www.securityweek.com/idesaster-research"],
        published="2025-12-10",
    ),
    CVE(
        id="CVE-2025-54135",
        cvss=8.6,
        severity="high",
        title="MCP Server Auto-Execution",
        description="Model Context Protocol servers configured with autoStart can execute arbitrary code when a project is opened, without user interaction or approval.",
        affected_tools=["Cursor", "Claude Code", "VS Code + MCP"],
        attack_vector="Malicious mcp.json with autoStart enabled",
        pattern_ids=["DS-MCP-001", "DS-MCP-002"],
        references=["https://www.bitsight.com/mcp-security-research"],
        published="2025-12-11",
    ),
    CVE(
        id="CVE-2025-55284",
        cvss=7.5,
        severity="high",
        title="DNS Exfiltration via AI Prompts",
        description="AI assistants can be prompted to exfiltrate sensitive data (environment variables, API keys) via DNS lookups to attacker-controlled domains.",
        affected_tools=["Claude Code", "GitHub Copilot", "Amazon Q"],
        attack_vector="Prompt injection in rules file triggering DNS lookup",
        pattern_ids=["DS-EX-001", "DS-EX-002"],
        references=["https://anthropic.com/news/disrupting-AI-espionage"],
        published="2025-11-13",
    ),
    CVE(
        id="CVE-2025-8217",
        cvss=9.1,
        severity="critical",
        title="Amazon Q Extension Compromise Chain",
        description="Malicious VS Code extensions can compromise Amazon Q's trust boundary, enabling credential theft, code injection, and persistent backdoors.",
        affected_tools=["Amazon Q", "VS Code"],
        attack_vector="Malicious extension with excessive permissions",
        pattern_ids=["DS-EXT-001", "DS-EXT-002", "DS-EXT-003"],
        references=["https://aws.amazon.com/security/security-bulletins/"],
        published="2025-12-05",
    ),
    CVE(
        id="CVE-2025-6514",
        cvss=9.6,
        severity="critical",
        title="mcp-remote Remote Code Execution",
        description="Critical vulnerability in mcp-remote package allows remote code execution affecting 437,000+ developer environments.",
        affected_tools=["All MCP clients", "Claude Desktop", "Cursor"],
        attack_vector="Malicious MCP server connection",
        pattern_ids=["DS-MCP-003", "DS-MCP-004"],
        references=["https://jfrog.com/blog/mcp-remote-rce"],
        published="2025-12-08",
    ),
    CVE(
        id="CVE-2025-49596",
        cvss=9.4,
        severity="critical",
        title="MCP Inspector RCE",
        description="Remote code execution vulnerability in MCP Inspector tool allowing arbitrary command execution.",
        affected_tools=["MCP Inspector", "MCP development tools"],
        attack_vector="Crafted MCP server response",
        pattern_ids=["DS-MCP-005"],
        references=["https://qualys.com/research/mcp-inspector"],
        published="2025-12-01",
    ),
    CVE(
        id="CVE-2025-64439",
        cvss=8.5,
        severity="high",
        title="LangGraph Checkpoint Deserialization RCE",
        description="Insecure deserialization in LangGraph checkpoint mechanism allows remote code execution in 100,000+ applications.",
        affected_tools=["LangGraph", "LangChain applications"],
        attack_vector="Malicious serialized checkpoint data",
        pattern_ids=["DS-SC-005"],
        references=["https://cybersecuritynews.com/langgraph-rce"],
        published="2025-12-12",
    ),
    CVE(
        id="CVE-2025-53774",
        cvss=7.2,
        severity="high",
        title="Hidden Unicode Character Injection",
        description="Zero-width characters and RTL override can hide malicious instructions in seemingly benign configuration files.",
        affected_tools=["All AI IDEs"],
        attack_vector="Unicode obfuscation in rules files",
        pattern_ids=["DS-PI-003", "DS-PI-004"],
        references=["https://www.securityweek.com/idesaster-research"],
        published="2025-12-10",
    ),
    CVE(
        id="CVE-2025-53775",
        cvss=6.8,
        severity="medium",
        title="Instruction Override via Comment Blocks",
        description="AI assistants may follow instructions hidden in comment blocks that appear inactive to human reviewers.",
        affected_tools=["GitHub Copilot", "Cursor", "Claude Code"],
        attack_vector="Commented instruction blocks in source files",
        pattern_ids=["DS-PI-005"],
        references=["https://www.securityweek.com/idesaster-research"],
        published="2025-12-10",
    ),
    CVE(
        id="CVE-2025-53776",
        cvss=8.1,
        severity="high",
        title="Cross-Context Memory Poisoning",
        description="AI assistants with persistent memory can have their memory poisoned to affect future sessions and projects.",
        affected_tools=["Claude Code", "Cursor with memory"],
        attack_vector="Crafted prompts that persist malicious instructions",
        pattern_ids=["DS-MCP-006"],
        references=["https://owasp.org/agentic-ai-top-10"],
        published="2025-12-10",
    ),
]


def get_cve(cve_id: str) -> Optional[CVE]:
    """Get CVE by ID."""
    for cve in CVE_DATABASE:
        if cve.id == cve_id:
            return cve
    return None


def get_cves_by_severity(severity: str) -> List[CVE]:
    """Get all CVEs of a given severity."""
    return [c for c in CVE_DATABASE if c.severity == severity]


def get_cves_by_tool(tool: str) -> List[CVE]:
    """Get all CVEs affecting a specific tool."""
    return [c for c in CVE_DATABASE if tool in c.affected_tools]
