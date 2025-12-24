"""
Data models for DeepSweep.

Uses Pydantic for validation and immutability.
"""

from enum import Enum

from pydantic import BaseModel, Field, computed_field


class Severity(str, Enum):
    """Finding severity levels."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class Finding(BaseModel):
    """
    A single security finding.

    Represents something that needs review in the user's configuration.
    Note: We say "finding" not "vulnerability" (optimistic framing).
    """

    model_config = {"frozen": True}

    severity: Severity
    file_path: str
    line: int = Field(ge=1)
    message: str
    pattern_id: str
    cve: str | None = None
    owasp: str | None = None
    remediation: str | None = None

    @computed_field
    def location(self) -> str:
        """Human-readable location string."""
        return f"{self.file_path}:{self.line}"


class FileResult(BaseModel):
    """Results for a single file."""

    model_config = {"frozen": True}

    path: str
    findings: tuple[Finding, ...] = Field(default_factory=tuple)
    skipped: bool = False
    skip_reason: str | None = None

    @computed_field
    def has_findings(self) -> bool:
        """Whether this file has any findings."""
        return len(self.findings) > 0

    @computed_field
    def finding_count(self) -> int:
        """Number of findings in this file."""
        return len(self.findings)


class ValidationResult(BaseModel):
    """
    Complete validation result for a path.

    Contains all findings, score, and grade.
    """

    model_config = {"frozen": True}

    files: tuple[FileResult, ...] = Field(default_factory=tuple)
    pattern_count: int = Field(ge=0)

    @computed_field
    def all_findings(self) -> tuple[Finding, ...]:
        """All findings across all files."""
        findings: list[Finding] = []
        for file_result in self.files:
            findings.extend(file_result.findings)
        return tuple(findings)

    @computed_field
    def finding_count(self) -> int:
        """Total number of findings."""
        return len(self.all_findings)

    @computed_field
    def has_findings(self) -> bool:
        """Whether any findings exist."""
        return self.finding_count > 0

    @computed_field
    def critical_count(self) -> int:
        """Number of critical findings."""
        return sum(1 for f in self.all_findings if f.severity == Severity.CRITICAL)

    @computed_field
    def high_count(self) -> int:
        """Number of high severity findings."""
        return sum(1 for f in self.all_findings if f.severity == Severity.HIGH)

    @computed_field
    def medium_count(self) -> int:
        """Number of medium severity findings."""
        return sum(1 for f in self.all_findings if f.severity == Severity.MEDIUM)

    @computed_field
    def low_count(self) -> int:
        """Number of low severity findings."""
        return sum(1 for f in self.all_findings if f.severity == Severity.LOW)

    @computed_field
    def score(self) -> int:
        """
        Security score from 0-100.

        Scoring:
        - Start at 100
        - Critical: -25 each
        - High: -15 each
        - Medium: -5 each
        - Low: -1 each
        - Minimum score: 0
        """
        score = 100
        score -= self.critical_count * 25
        score -= self.high_count * 15
        score -= self.medium_count * 5
        score -= self.low_count * 1
        return max(0, score)

    @computed_field
    def grade(self) -> str:
        """
        Letter grade with encouraging context.

        Even F grade is optimistic: "Let's fix this together"
        """
        if self.score >= 90:
            return "A - Ship ready"
        elif self.score >= 80:
            return "B - Looking good"
        elif self.score >= 70:
            return "C - Review recommended"
        elif self.score >= 60:
            return "D - Attention needed"
        else:
            return "F - Let's fix this together"

    @computed_field
    def grade_letter(self) -> str:
        """Just the letter grade."""
        return self.grade.split(" - ")[0]
