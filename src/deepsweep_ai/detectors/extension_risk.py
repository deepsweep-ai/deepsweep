"""
Extension/Plugin Risk Detector

Detects risky patterns in IDE extension configurations and AI assistant rules.
Covers Amazon Q extension compromise (CVE-2025-8217) and similar attacks.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

from deepsweep_ai.detectors.base import BaseDetector
from deepsweep_ai.scanner import Finding, Severity


class ExtensionRiskDetector(BaseDetector):
    """Detect extension and plugin security risks."""

    PATTERNS = [
        # CRITICAL: Extension auto-update from external source
        {
            "id": "DS-EXT-001",
            "pattern": r"(?i)(auto.?update|self.?update).{0,30}(https?://|from|url)",
            "title": "Extension Auto-Update from External Source",
            "description": "Extension configured to auto-update from external URL. This is how the Amazon Q attack worked.",
            "severity": Severity.CRITICAL,
            "cves": ["CVE-2025-8217"],
            "tools": ["Amazon Q", "All extensions"],
            "remediation": "Disable auto-updates from external sources. Use marketplace updates only.",
        },
        # CRITICAL: Extension requests excessive permissions
        {
            "id": "DS-EXT-002",
            "pattern": r"(?i)(all.?permissions|full.?access|\*\.\*|admin|root|sudo)",
            "title": "Excessive Permission Request",
            "description": "Configuration requests excessive or all permissions.",
            "severity": Severity.HIGH,
            "cves": [],
            "tools": ["All extensions"],
            "remediation": "Follow principle of least privilege. Request only necessary permissions.",
        },
        # HIGH: Network access configuration
        {
            "id": "DS-EXT-003",
            "pattern": r"(?i)(network.?access|internet.?permission|allow.?all.?hosts)",
            "title": "Unrestricted Network Access",
            "description": "Extension configured with unrestricted network access.",
            "severity": Severity.HIGH,
            "cves": [],
            "tools": ["All extensions"],
            "remediation": "Restrict network access to required hosts only.",
        },
        # HIGH: File system access patterns
        {
            "id": "DS-EXT-004",
            "pattern": r"(?i)(access.?all.?files|full.?fs|read.?write.?all|/\*\*|\$HOME|\$USERPROFILE)",
            "title": "Broad File System Access",
            "description": "Extension configured with broad file system access.",
            "severity": Severity.HIGH,
            "cves": [],
            "tools": ["All extensions"],
            "remediation": "Restrict file access to project directories only.",
        },
        # MEDIUM: Telemetry/analytics configuration
        {
            "id": "DS-EXT-005",
            "pattern": r"(?i)(telemetry|analytics|tracking).{0,20}(enabled|true|on)",
            "title": "Telemetry Enabled",
            "description": "Extension has telemetry/analytics enabled. Could leak code or usage data.",
            "severity": Severity.MEDIUM,
            "cves": [],
            "tools": ["All extensions"],
            "remediation": "Disable telemetry or audit what data is collected.",
        },
        # MEDIUM: Remote code execution capability
        {
            "id": "DS-EXT-006",
            "pattern": r"(?i)(remote.?exec|rce|code.?injection|eval|exec)",
            "title": "Remote Code Execution Capability",
            "description": "Configuration suggests remote code execution capability.",
            "severity": Severity.HIGH,
            "cves": [],
            "tools": ["All extensions"],
            "remediation": "Remove or audit remote execution capabilities.",
        },
    ]

    def scan_file(self, path: Path) -> List[Finding]:
        """Scan file for extension risk patterns."""
        content = self._read_file(path)
        if not content:
            return []

        findings: List[Finding] = []
        lines = content.split("\n")

        for pattern_def in self.PATTERNS:
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
                        cve_ids=pattern_def["cves"],
                        affected_tools=pattern_def["tools"],
                        remediation=pattern_def["remediation"],
                        references=[
                            "https://deepsweep.ai/vulnerabilities/extension-security",
                        ],
                    ))

        return findings
