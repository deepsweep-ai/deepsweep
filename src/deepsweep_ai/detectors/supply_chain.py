"""
Supply Chain Attack Detector

Detects patterns related to supply chain attacks, dependency confusion,
and package tampering.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

from deepsweep_ai.detectors.base import BaseDetector
from deepsweep_ai.scanner import Finding, Severity


class SupplyChainDetector(BaseDetector):
    """Detect supply chain attack vulnerabilities."""

    PATTERNS = [
        # CRITICAL: Install from arbitrary URL
        {
            "id": "DS-SC-001",
            "pattern": r"(?i)(pip\s+install|npm\s+install|gem\s+install).{0,20}(https?://|git\+)",
            "title": "Package Install from URL",
            "description": "Package installation from arbitrary URL detected. Could install malicious code.",
            "severity": Severity.CRITICAL,
            "cves": [],
            "tools": ["All IDEs"],
            "remediation": "Only install packages from official registries. Pin versions.",
        },
        # CRITICAL: Curl pipe to shell
        {
            "id": "DS-SC-002",
            "pattern": r"(?i)(curl|wget).{0,50}\|\s*(bash|sh|zsh|python|node)",
            "title": "Curl Pipe to Shell",
            "description": "Remote script execution via curl pipe. Classic supply chain attack vector.",
            "severity": Severity.CRITICAL,
            "cves": [],
            "tools": ["All IDEs"],
            "remediation": "Never pipe remote content to shell. Download, verify, then execute.",
        },
        # HIGH: Postinstall scripts
        {
            "id": "DS-SC-003",
            "pattern": r"(?i)(postinstall|preinstall|prepare)\s*[\"']?\s*:\s*[\"']?[^\"'\n]+",
            "title": "Package Install Script",
            "description": "Package install script detected. These run automatically and can be malicious.",
            "severity": Severity.HIGH,
            "cves": [],
            "tools": ["All IDEs"],
            "remediation": "Audit all install scripts. Use --ignore-scripts when possible.",
        },
        # HIGH: Private registry override
        {
            "id": "DS-SC-004",
            "pattern": r"(?i)(registry\s*=|--registry)\s*https?://(?!registry\.npmjs\.org|pypi\.org)",
            "title": "Custom Package Registry",
            "description": "Non-standard package registry detected. Could serve malicious packages.",
            "severity": Severity.HIGH,
            "cves": [],
            "tools": ["All IDEs"],
            "remediation": "Use official registries only. Audit custom registries carefully.",
        },
        # MEDIUM: Unpinned dependencies
        {
            "id": "DS-SC-005",
            "pattern": r"(?i)(install|add)\s+[\w-]+(?!\s*[@=])",
            "title": "Unpinned Dependency",
            "description": "Package installation without version pin. Vulnerable to dependency confusion.",
            "severity": Severity.MEDIUM,
            "cves": [],
            "tools": ["All IDEs"],
            "remediation": "Always pin dependency versions. Use lock files.",
        },
    ]

    def scan_file(self, path: Path) -> List[Finding]:
        """Scan file for supply chain attack patterns."""
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
                            "https://deepsweep.ai/vulnerabilities/supply-chain",
                        ],
                    ))

        return findings
