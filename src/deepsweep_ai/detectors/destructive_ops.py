"""
Destructive Operations Detector

Detects patterns that could cause destructive operations (file deletion,
infrastructure damage, etc.). Covers Amazon Q wiper-style attacks.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

from deepsweep_ai.detectors.base import BaseDetector
from deepsweep_ai.scanner import Finding, Severity


class DestructiveOpsDetector(BaseDetector):
    """Detect destructive operation vulnerabilities."""

    PATTERNS = [
        # CRITICAL: Mass file deletion
        {
            "id": "DS-DO-001",
            "pattern": r"(?i)(rm\s+-rf|rmdir\s+/s|del\s+/[sfq]|remove-item.*-recurse.*-force)",
            "title": "Mass File Deletion Command",
            "description": "Recursive/forced file deletion detected. This is the pattern used in the Amazon Q wiper attack.",
            "severity": Severity.CRITICAL,
            "cves": ["CVE-2025-8217"],
            "tools": ["Amazon Q", "All IDEs"],
            "remediation": "Remove mass deletion commands. Use targeted, audited deletions only.",
        },
        # CRITICAL: Format/wipe operations
        {
            "id": "DS-DO-002",
            "pattern": r"(?i)(format|mkfs|dd\s+if=|diskpart|clean\s+all)",
            "title": "Disk Format/Wipe Operation",
            "description": "Disk formatting or wiping operation detected. Could destroy all data.",
            "severity": Severity.CRITICAL,
            "cves": [],
            "tools": ["All IDEs"],
            "remediation": "Remove disk formatting commands. These should never be in AI instructions.",
        },
        # CRITICAL: AWS destructive operations
        {
            "id": "DS-DO-003",
            "pattern": r"(?i)aws\s+(iam\s+delete|ec2\s+terminate|s3\s+rb|rds\s+delete|lambda\s+delete)",
            "title": "AWS Destructive Operation",
            "description": "AWS resource deletion command detected. Could destroy cloud infrastructure.",
            "severity": Severity.CRITICAL,
            "cves": ["CVE-2025-8217"],
            "tools": ["Amazon Q"],
            "remediation": "Remove AWS deletion commands. Use IAM policies to restrict destructive actions.",
        },
        # CRITICAL: Kubernetes destructive operations
        {
            "id": "DS-DO-004",
            "pattern": r"(?i)kubectl\s+(delete\s+(namespace|ns|deployment|pod)|drain|cordon)",
            "title": "Kubernetes Destructive Operation",
            "description": "Kubernetes resource deletion or node drain detected.",
            "severity": Severity.CRITICAL,
            "cves": [],
            "tools": ["All IDEs"],
            "remediation": "Remove Kubernetes deletion commands from AI instructions.",
        },
        # HIGH: Git destructive operations
        {
            "id": "DS-DO-005",
            "pattern": r"(?i)git\s+(push\s+.*--force|reset\s+--hard|clean\s+-fd)",
            "title": "Git Destructive Operation",
            "description": "Git force push or hard reset detected. Could destroy repository history.",
            "severity": Severity.HIGH,
            "cves": [],
            "tools": ["All IDEs"],
            "remediation": "Remove force push and hard reset from AI instructions.",
        },
        # HIGH: Database destructive operations
        {
            "id": "DS-DO-006",
            "pattern": r"(?i)(drop\s+(database|table|schema)|truncate\s+table|delete\s+from\s+\w+\s*$)",
            "title": "Database Destructive Operation",
            "description": "Database drop/truncate/mass delete detected.",
            "severity": Severity.HIGH,
            "cves": [],
            "tools": ["All IDEs"],
            "remediation": "Remove database destruction commands. Use migrations for schema changes.",
        },
        # HIGH: Terraform destroy
        {
            "id": "DS-DO-007",
            "pattern": r"(?i)terraform\s+(destroy|apply\s+-auto-approve)",
            "title": "Terraform Destructive Operation",
            "description": "Terraform destroy or auto-approve apply detected. Could destroy infrastructure.",
            "severity": Severity.HIGH,
            "cves": [],
            "tools": ["All IDEs"],
            "remediation": "Never auto-approve Terraform. Require manual review for infrastructure changes.",
        },
    ]

    def scan_file(self, path: Path) -> List[Finding]:
        """Scan file for destructive operation patterns."""
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
                            "https://deepsweep.ai/vulnerabilities/destructive-operations",
                        ],
                    ))

        return findings
