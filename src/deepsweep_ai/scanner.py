"""
Core scanning engine for DeepSweep.

Orchestrates all detectors and aggregates findings.
"""

from __future__ import annotations

import fnmatch
import hashlib
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any, Iterator

from deepsweep_ai.config import Config, Mode


class Severity(Enum):
    """Finding severity levels."""
    CRITICAL = "critical"  # Immediate action required (RCE, wiper)
    HIGH = "high"          # Serious security issue
    MEDIUM = "medium"      # Potential security issue
    LOW = "low"            # Informational / best practice
    INFO = "info"          # Purely informational

    def __lt__(self, other: "Severity") -> bool:
        order = [Severity.INFO, Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
        return order.index(self) < order.index(other)

    def __ge__(self, other: "Severity") -> bool:
        return not self < other


@dataclass
class Finding:
    """A security finding from a scan."""

    id: str                          # Unique finding ID (e.g., "DS-PI-001")
    title: str                       # Short title
    description: str                 # Detailed description
    severity: Severity
    file_path: str                   # File where found
    line_number: Optional[int]       # Line number if applicable
    code_snippet: Optional[str]      # Relevant code snippet
    cve_ids: List[str] = field(default_factory=list)  # Related CVEs
    affected_tools: List[str] = field(default_factory=list)  # Copilot, Cursor, etc.
    remediation: str = ""            # How to fix
    references: List[str] = field(default_factory=list)  # Links

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON output."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "code_snippet": self.code_snippet,
            "cve_ids": self.cve_ids,
            "affected_tools": self.affected_tools,
            "remediation": self.remediation,
            "references": self.references,
        }

    def to_sarif(self) -> Dict[str, Any]:
        """Convert to SARIF format for GitHub Security."""
        severity_map = {
            Severity.CRITICAL: "error",
            Severity.HIGH: "error",
            Severity.MEDIUM: "warning",
            Severity.LOW: "note",
            Severity.INFO: "note",
        }
        return {
            "ruleId": self.id,
            "level": severity_map[self.severity],
            "message": {"text": f"{self.title}: {self.description}"},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": self.file_path},
                    "region": {"startLine": self.line_number or 1}
                }
            }],
        }


@dataclass
class ScanResult:
    """Complete scan result."""

    scan_id: str
    timestamp: str
    duration_ms: int
    mode: Mode
    path_scanned: str
    files_scanned: int
    findings: List[Finding]

    @property
    def safe(self) -> bool:
        """True if no critical or high severity findings."""
        return not any(
            f.severity in (Severity.CRITICAL, Severity.HIGH)
            for f in self.findings
        )

    @property
    def score(self) -> int:
        """Security score 0-100 (100 = perfect)."""
        if not self.findings:
            return 100

        deductions = {
            Severity.CRITICAL: 25,
            Severity.HIGH: 15,
            Severity.MEDIUM: 5,
            Severity.LOW: 2,
            Severity.INFO: 0,
        }

        total_deduction = sum(
            deductions[f.severity] for f in self.findings
        )

        return max(0, 100 - total_deduction)

    @property
    def status(self) -> str:
        """Status string for badges."""
        critical = sum(1 for f in self.findings if f.severity == Severity.CRITICAL)
        high = sum(1 for f in self.findings if f.severity == Severity.HIGH)

        if critical > 0:
            return "critical"
        elif high > 0:
            return "warning"
        else:
            return "passing"

    @property
    def blocked_count(self) -> int:
        """Number of findings that would be blocked in enforce mode."""
        return sum(
            1 for f in self.findings
            if f.severity in (Severity.CRITICAL, Severity.HIGH)
        )

    @property
    def findings_count(self) -> int:
        """Total number of findings."""
        return len(self.findings)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        from deepsweep_ai import __version__
        return {
            "version": __version__,
            "scan_id": self.scan_id,
            "timestamp": self.timestamp,
            "duration_ms": self.duration_ms,
            "mode": self.mode.value,
            "path_scanned": self.path_scanned,
            "files_scanned": self.files_scanned,
            "safe": self.safe,
            "score": self.score,
            "status": self.status,
            "blocked_count": self.blocked_count,
            "findings_count": len(self.findings),
            "findings": [f.to_dict() for f in self.findings],
        }

    def to_sarif(self) -> Dict[str, Any]:
        """Convert to SARIF format."""
        from deepsweep_ai import __version__
        return {
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "version": "2.1.0",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "DeepSweep",
                        "version": __version__,
                        "informationUri": "https://deepsweep.ai",
                        "rules": self._sarif_rules(),
                    }
                },
                "results": [f.to_sarif() for f in self.findings],
            }]
        }

    def _sarif_rules(self) -> List[Dict[str, Any]]:
        """Generate SARIF rule definitions."""
        rules = {}
        for f in self.findings:
            if f.id not in rules:
                rules[f.id] = {
                    "id": f.id,
                    "name": f.title,
                    "shortDescription": {"text": f.title},
                    "fullDescription": {"text": f.description},
                    "help": {"text": f.remediation},
                    "properties": {"security-severity": self._cvss_score(f.severity)},
                }
        return list(rules.values())

    def _cvss_score(self, severity: Severity) -> str:
        """Map severity to CVSS-like score for SARIF."""
        scores = {
            Severity.CRITICAL: "9.0",
            Severity.HIGH: "7.0",
            Severity.MEDIUM: "4.0",
            Severity.LOW: "2.0",
            Severity.INFO: "0.0",
        }
        return scores[severity]


class Scanner:
    """Main scanner orchestrating all detectors."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.load()
        self._detectors = self._init_detectors()

    def _init_detectors(self) -> List:
        """Initialize enabled detectors."""
        from deepsweep_ai.detectors import prompt_injection, exfiltration, destructive_ops
        from deepsweep_ai.detectors import supply_chain, mcp_poisoning, extension_risk

        detectors = []

        if self.config.enable_prompt_injection:
            detectors.append(prompt_injection.PromptInjectionDetector())
        if self.config.enable_exfiltration:
            detectors.append(exfiltration.ExfiltrationDetector())
        if self.config.enable_destructive_ops:
            detectors.append(destructive_ops.DestructiveOpsDetector())
        if self.config.enable_supply_chain:
            detectors.append(supply_chain.SupplyChainDetector())
        if self.config.enable_mcp_poisoning:
            detectors.append(mcp_poisoning.MCPPoisoningDetector())
        if self.config.enable_extension_risk:
            detectors.append(extension_risk.ExtensionRiskDetector())

        return detectors

    def scan(self, path: str = ".") -> ScanResult:
        """
        Scan a directory for AI coding assistant security issues.

        Args:
            path: Directory to scan (default: current directory)

        Returns:
            ScanResult with all findings
        """
        start_time = time.time()
        scan_path = Path(path).resolve()

        # Generate scan ID
        scan_id = hashlib.sha256(
            f"{scan_path}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        # Find files to scan
        files = list(self._find_files(scan_path))

        # Run all detectors
        all_findings: List[Finding] = []
        for file_path in files:
            for detector in self._detectors:
                try:
                    findings = detector.scan_file(file_path)
                    all_findings.extend(findings)
                except Exception as e:
                    if self.config.verbose:
                        print(f"Warning: Error scanning {file_path} with {detector}: {e}")

        # Sort by severity
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFO: 4,
        }
        all_findings.sort(key=lambda f: severity_order[f.severity])

        duration_ms = int((time.time() - start_time) * 1000)

        return ScanResult(
            scan_id=scan_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            duration_ms=duration_ms,
            mode=self.config.mode,
            path_scanned=str(scan_path),
            files_scanned=len(files),
            findings=all_findings,
        )

    def _find_files(self, root: Path) -> Iterator[Path]:
        """Find files matching include patterns, excluding exclude patterns."""
        for include_pattern in self.config.include_patterns:
            # Handle glob patterns
            if "*" in include_pattern:
                for match in root.rglob(include_pattern.lstrip("*")):
                    if self._should_include(match):
                        yield match
            else:
                # Direct path
                target = root / include_pattern
                if target.exists():
                    if target.is_file():
                        yield target
                    elif target.is_dir():
                        for f in target.rglob("*"):
                            if f.is_file() and self._should_include(f):
                                yield f

    def _should_include(self, path: Path) -> bool:
        """Check if path should be included (not excluded)."""
        path_str = str(path)
        for exclude_pattern in self.config.exclude_patterns:
            if fnmatch.fnmatch(path_str, f"*{exclude_pattern}*"):
                return False
        return True
