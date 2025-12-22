"""Extension Risk Detection Patterns"""

from dataclasses import dataclass
from typing import List


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


EXTENSION_RISK_PATTERNS: List[Pattern] = [
    Pattern(
        id="DS-EXT-001",
        title="Auto-Update from External URL",
        description="Extension configured to auto-update from external source",
        severity="high",
        category="extension_risk",
        regex=r'"(autoUpdate|updateUrl|downloadUrl)"\s*:\s*"https?://',
        file_patterns=["package.json", "extension.json", "*.vsix"],
        cve_ids=["CVE-2025-8217"],
        remediation="Disable auto-update or use marketplace only",
    ),
    Pattern(
        id="DS-EXT-002",
        title="Excessive Extension Permissions",
        description="Extension requesting unnecessary permissions",
        severity="medium",
        category="extension_risk",
        regex=r'"(activationEvents|permissions)"\s*:\s*\[.*"\*"',
        file_patterns=["package.json"],
        cve_ids=["CVE-2025-8217"],
        remediation="Request only necessary permissions",
    ),
    Pattern(
        id="DS-EXT-003",
        title="Network Access Without Restriction",
        description="Extension with unrestricted network access capability",
        severity="medium",
        category="extension_risk",
        regex=r'"contributes".*"networkAccess".*"unrestricted"',
        file_patterns=["package.json"],
        cve_ids=["CVE-2025-8217"],
        remediation="Restrict network access to necessary domains",
    ),
    Pattern(
        id="DS-EXT-004",
        title="Telemetry/Tracking Code",
        description="Extension with potential tracking/telemetry code",
        severity="low",
        category="extension_risk",
        regex=r'(analytics|telemetry|tracking|mixpanel|amplitude|segment)',
        file_patterns=["*.js", "*.ts"],
        cve_ids=[],
        remediation="Review telemetry implementation for data collection",
    ),
    Pattern(
        id="DS-EXT-005",
        title="File System Full Access",
        description="Extension requesting full filesystem access",
        severity="high",
        category="extension_risk",
        regex=r'"permissions".*"fileSystem".*"write"',
        file_patterns=["package.json", "manifest.json"],
        cve_ids=[],
        remediation="Limit filesystem access to necessary directories",
    ),
    Pattern(
        id="DS-EXT-006",
        title="Code Execution Capability",
        description="Extension with eval() or Function() constructor usage",
        severity="high",
        category="extension_risk",
        regex=r'(eval\s*\(|new\s+Function\s*\(|setTimeout\s*\(\s*["\'])',
        file_patterns=["*.js", "*.ts"],
        cve_ids=[],
        remediation="Avoid dynamic code execution in extensions",
    ),
]
