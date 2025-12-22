"""
Prompt Injection Detection Patterns

Covers:
- Instruction override attempts
- Hidden Unicode characters
- YOLO/auto-accept mode
- Jailbreak patterns
- Encoded payloads
"""

from dataclasses import dataclass
from typing import List
import re


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

    def compile(self) -> re.Pattern:
        return re.compile(self.regex, re.IGNORECASE | re.MULTILINE)


PROMPT_INJECTION_PATTERNS: List[Pattern] = [
    Pattern(
        id="DS-PI-001",
        title="Instruction Override Pattern",
        description="Detects attempts to override previous instructions given to AI assistants",
        severity="critical",
        category="prompt_injection",
        regex=r"(ignore|disregard|forget|override).{0,30}(previous|prior|above|earlier|all).{0,30}(instruction|rule|directive|command|prompt)",
        file_patterns=[".cursorrules", ".cursor/rules/*", "CLAUDE.md", "AGENTS.md", ".github/copilot-instructions.md"],
        cve_ids=["CVE-2025-53773"],
        remediation="Remove instruction override patterns from configuration files",
    ),
    Pattern(
        id="DS-PI-002",
        title="YOLO Mode Activation",
        description="Detects attempts to enable automatic execution without confirmation",
        severity="critical",
        category="prompt_injection",
        regex=r"(yolo|auto.?accept|auto.?approve|auto.?execute|no.?confirm|skip.?confirm|always.?yes|--yes|-y\s|--force)",
        file_patterns=[".cursorrules", ".cursor/rules/*", "CLAUDE.md", "AGENTS.md"],
        cve_ids=["CVE-2025-53773"],
        remediation="Remove YOLO mode or auto-accept configurations",
    ),
    Pattern(
        id="DS-PI-003",
        title="Zero-Width Character Injection",
        description="Detects hidden zero-width Unicode characters that can hide malicious content",
        severity="high",
        category="prompt_injection",
        regex=r"[\u200B\u200C\u200D\u2060\uFEFF]",
        file_patterns=["*"],
        cve_ids=["CVE-2025-53774"],
        remediation="Remove zero-width characters from files",
    ),
    Pattern(
        id="DS-PI-004",
        title="RTL Override Character",
        description="Detects right-to-left override characters that can disguise text direction",
        severity="high",
        category="prompt_injection",
        regex=r"[\u202A-\u202E\u2066-\u2069]",
        file_patterns=["*"],
        cve_ids=["CVE-2025-53774"],
        remediation="Remove bidirectional text override characters",
    ),
    Pattern(
        id="DS-PI-005",
        title="Jailbreak Pattern - DAN",
        description="Detects Do Anything Now (DAN) jailbreak attempts",
        severity="critical",
        category="prompt_injection",
        regex=r"(DAN|do anything now|jailbreak|bypass.{0,20}(filter|safety|restriction)|pretend.{0,20}(no|without).{0,20}(rule|limit|restrict))",
        file_patterns=[".cursorrules", "CLAUDE.md", "AGENTS.md"],
        cve_ids=[],
        remediation="Remove jailbreak patterns from configuration files",
    ),
    Pattern(
        id="DS-PI-006",
        title="Role Impersonation",
        description="Detects attempts to make AI assume a different identity or role to bypass restrictions",
        severity="high",
        category="prompt_injection",
        regex=r"(you are now|act as|pretend to be|roleplay as|assume the role|from now on you).{0,30}(unrestricted|unlimited|without limit|no filter|evil|malicious|hacker)",
        file_patterns=[".cursorrules", "CLAUDE.md", "AGENTS.md"],
        cve_ids=[],
        remediation="Remove role impersonation instructions",
    ),
    Pattern(
        id="DS-PI-007",
        title="Prompt Leaking Attempt",
        description="Detects attempts to extract or reveal system prompts",
        severity="medium",
        category="prompt_injection",
        regex=r"(reveal|show|print|display|output|repeat).{0,20}(system prompt|initial instruction|original prompt|hidden instruction)",
        file_patterns=[".cursorrules", "CLAUDE.md", "AGENTS.md"],
        cve_ids=[],
        remediation="Remove system prompt extraction attempts",
    ),
    Pattern(
        id="DS-PI-008",
        title="Base64 Encoded Instructions",
        description="Detects base64 encoded content that may hide malicious instructions",
        severity="medium",
        category="prompt_injection",
        regex=r"(execute|run|eval|decode).{0,20}base64|base64.{0,10}(decode|execute)|[A-Za-z0-9+/]{50,}={0,2}",
        file_patterns=[".cursorrules", "CLAUDE.md", "AGENTS.md"],
        cve_ids=[],
        remediation="Review and remove base64 encoded content",
    ),
]
