"""
Prompt Injection Detector

Detects prompt injection patterns across AI coding assistant configuration files.
Covers CVE-2025-53773 (Copilot YOLO mode), CVE-2025-54135 (Cursor), and more.

CRITICAL: These patterns can enable RCE, data exfiltration, and system compromise.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

from deepsweep_ai.detectors.base import BaseDetector
from deepsweep_ai.scanner import Finding, Severity


class PromptInjectionDetector(BaseDetector):
    """Detect prompt injection vulnerabilities in AI assistant configs."""

    # Pattern categories with severity and metadata
    PATTERNS = [
        # CRITICAL: Instruction override / system prompt manipulation
        {
            "id": "DS-PI-001",
            "pattern": r"(?i)(ignore|disregard|forget|override).{0,30}(previous|prior|above|system|instructions?)",
            "title": "Instruction Override Pattern",
            "description": "Detected attempt to override system instructions. This is the primary prompt injection technique.",
            "severity": Severity.CRITICAL,
            "cves": ["CVE-2025-53773"],
            "tools": ["GitHub Copilot", "Cursor", "Claude Code", "Amazon Q"],
            "remediation": "Remove or sanitize instruction override patterns. Use allowlisted prompts only.",
        },
        # CRITICAL: Hidden Unicode characters (invisible instructions)
        {
            "id": "DS-PI-002",
            "pattern": r"[\u200b-\u200f\u2028-\u202f\u2060-\u206f\ufeff]",
            "title": "Hidden Unicode Characters",
            "description": "Invisible Unicode characters detected. These can hide malicious instructions from human review.",
            "severity": Severity.CRITICAL,
            "cves": ["CVE-2025-8217"],
            "tools": ["Amazon Q", "All IDEs"],
            "remediation": "Remove all invisible Unicode characters. Use only printable ASCII/UTF-8.",
        },
        # CRITICAL: YOLO mode activation (Copilot-specific)
        {
            "id": "DS-PI-003",
            "pattern": r"(?i)(yolo|auto.?accept|no.?confirm|skip.?confirm|always.?approve|disable.?prompt)",
            "title": "Auto-Accept Mode Activation",
            "description": "Attempt to enable auto-accept/YOLO mode detected. This bypasses user confirmation for dangerous actions.",
            "severity": Severity.CRITICAL,
            "cves": ["CVE-2025-53773"],
            "tools": ["GitHub Copilot"],
            "remediation": "Never enable auto-accept modes. Always require user confirmation for shell commands.",
        },
        # HIGH: Role impersonation
        {
            "id": "DS-PI-004",
            "pattern": r"(?i)(you are|act as|pretend|behave as|roleplay).{0,20}(admin|root|system|developer|user)",
            "title": "Role Impersonation Attempt",
            "description": "Attempt to make AI assume elevated role or identity.",
            "severity": Severity.HIGH,
            "cves": [],
            "tools": ["All IDEs"],
            "remediation": "Remove role impersonation instructions. AI should not assume privileged identities.",
        },
        # HIGH: Jailbreak patterns
        {
            "id": "DS-PI-005",
            "pattern": r"(?i)(DAN|do anything now|jailbreak|uncensored|no.?restrictions|bypass.?safety)",
            "title": "Jailbreak Pattern Detected",
            "description": "Known jailbreak pattern detected. This attempts to bypass AI safety measures.",
            "severity": Severity.HIGH,
            "cves": [],
            "tools": ["All IDEs"],
            "remediation": "Remove jailbreak patterns. These violate terms of service and enable dangerous behavior.",
        },
        # HIGH: Base64/encoded payloads
        {
            "id": "DS-PI-006",
            "pattern": r"(?i)(decode|base64|eval|exec).{0,30}(this|following|payload|string)",
            "title": "Encoded Payload Execution",
            "description": "Instruction to decode and execute payload. Common obfuscation technique.",
            "severity": Severity.HIGH,
            "cves": [],
            "tools": ["All IDEs"],
            "remediation": "Remove encoded payload instructions. All code should be human-readable.",
        },
        # MEDIUM: Prompt leaking
        {
            "id": "DS-PI-007",
            "pattern": r"(?i)(print|output|show|reveal|display).{0,20}(system|prompt|instructions?|config)",
            "title": "Prompt Leaking Attempt",
            "description": "Attempt to extract system prompt or configuration.",
            "severity": Severity.MEDIUM,
            "cves": [],
            "tools": ["All IDEs"],
            "remediation": "Remove prompt extraction instructions. System prompts should remain confidential.",
        },
        # MEDIUM: Context manipulation
        {
            "id": "DS-PI-008",
            "pattern": r"(?i)(from now on|going forward|for all future|always|never).{0,30}(do|execute|run|perform)",
            "title": "Persistent Context Manipulation",
            "description": "Attempt to persistently modify AI behavior for future interactions.",
            "severity": Severity.MEDIUM,
            "cves": [],
            "tools": ["All IDEs"],
            "remediation": "Avoid persistent behavioral modifications. Use session-scoped instructions.",
        },
    ]

    def scan_file(self, path: Path) -> List[Finding]:
        """Scan file for prompt injection patterns."""
        content = self._read_file(path)
        if not content:
            return []

        findings: List[Finding] = []
        lines = content.split("\n")

        for pattern_def in self.PATTERNS:
            pattern = re.compile(pattern_def["pattern"])

            for line_num, line in enumerate(lines, 1):
                if match := pattern.search(line):
                    findings.append(Finding(
                        id=pattern_def["id"],
                        title=pattern_def["title"],
                        description=pattern_def["description"],
                        severity=pattern_def["severity"],
                        file_path=str(path),
                        line_number=line_num,
                        code_snippet=line.strip()[:200],
                        cve_ids=pattern_def["cves"],
                        affected_tools=pattern_def["tools"],
                        remediation=pattern_def["remediation"],
                        references=[
                            "https://deepsweep.ai/vulnerabilities/prompt-injection",
                            "https://owasp.org/www-project-top-10-for-large-language-model-applications/",
                        ],
                    ))

        return findings
