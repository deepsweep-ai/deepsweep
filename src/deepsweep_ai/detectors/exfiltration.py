"""
Data Exfiltration Detector

Detects patterns that could enable data exfiltration from AI coding assistants.
Covers DNS exfiltration (CVE-2025-55284), HTTP callbacks, and more.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

from deepsweep_ai.detectors.base import BaseDetector
from deepsweep_ai.scanner import Finding, Severity


class ExfiltrationDetector(BaseDetector):
    """Detect data exfiltration vulnerabilities."""

    PATTERNS = [
        # CRITICAL: DNS exfiltration
        {
            "id": "DS-EX-001",
            "pattern": r"(?i)(dns|nslookup|dig|host).{0,50}(\$|`|env|secret|key|token|password)",
            "title": "DNS Exfiltration Pattern",
            "description": "DNS-based data exfiltration pattern detected. Secrets can be leaked via DNS queries.",
            "severity": Severity.CRITICAL,
            "cves": ["CVE-2025-55284"],
            "tools": ["Claude Code"],
            "remediation": "Remove DNS-based data transmission. Audit all DNS-related commands.",
        },
        # CRITICAL: HTTP callback with secrets
        {
            "id": "DS-EX-002",
            "pattern": r"(?i)(curl|wget|fetch|http|request).{0,100}(\$|env|secret|key|token|api.?key)",
            "title": "HTTP Exfiltration Pattern",
            "description": "HTTP request with potential secret data. Could leak credentials to external servers.",
            "severity": Severity.CRITICAL,
            "cves": [],
            "tools": ["All IDEs"],
            "remediation": "Remove HTTP requests containing secrets. Use secure secret management.",
        },
        # CRITICAL: Webhook/callback URLs
        {
            "id": "DS-EX-003",
            "pattern": r"(?i)(webhook|callback|notify|ping).{0,30}(https?://|//)",
            "title": "External Callback URL",
            "description": "External callback URL detected. Could be used to exfiltrate data or trigger external actions.",
            "severity": Severity.HIGH,
            "cves": [],
            "tools": ["All IDEs"],
            "remediation": "Allowlist external URLs. Remove unauthorized callback endpoints.",
        },
        # HIGH: Environment variable access
        {
            "id": "DS-EX-004",
            "pattern": r"(?i)(print|echo|cat|output|log).{0,30}(\$\{?[A-Z_]+\}?|process\.env|os\.environ)",
            "title": "Environment Variable Exposure",
            "description": "Environment variable being output. Could leak secrets in logs or output.",
            "severity": Severity.HIGH,
            "cves": [],
            "tools": ["All IDEs"],
            "remediation": "Never output environment variables. Use secret masking.",
        },
        # HIGH: File read and send
        {
            "id": "DS-EX-005",
            "pattern": r"(?i)(read|cat|type|get-content).{0,50}(send|post|upload|transmit)",
            "title": "File Read and Transmit",
            "description": "Pattern suggests reading file and transmitting contents externally.",
            "severity": Severity.HIGH,
            "cves": [],
            "tools": ["All IDEs"],
            "remediation": "Remove file read + transmit patterns. Audit data flows.",
        },
        # MEDIUM: Clipboard access
        {
            "id": "DS-EX-006",
            "pattern": r"(?i)(clipboard|pbcopy|pbpaste|xclip|xsel)",
            "title": "Clipboard Access",
            "description": "Clipboard access detected. Could be used to capture or inject sensitive data.",
            "severity": Severity.MEDIUM,
            "cves": [],
            "tools": ["All IDEs"],
            "remediation": "Audit clipboard access. Ensure no sensitive data is accessed.",
        },
    ]

    def scan_file(self, path: Path) -> List[Finding]:
        """Scan file for exfiltration patterns."""
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
                            "https://deepsweep.ai/vulnerabilities/data-exfiltration",
                        ],
                    ))

        return findings
