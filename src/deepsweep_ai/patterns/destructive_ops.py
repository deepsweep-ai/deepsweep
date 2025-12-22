"""Destructive Operations Detection Patterns"""

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


DESTRUCTIVE_OPS_PATTERNS: List[Pattern] = [
    Pattern(
        id="DS-DO-001",
        title="Recursive Delete Command",
        description="Detects rm -rf, del /s /q, and similar destructive commands",
        severity="critical",
        category="destructive_ops",
        regex=r"rm\s+(-rf|-fr|--force\s+--recursive)|del\s+/[sS]\s+/[qQ]|Remove-Item\s+.*-Recurse\s+.*-Force",
        file_patterns=["*"],
        cve_ids=["CVE-2025-8217"],
        remediation="Remove mass deletion commands",
    ),
    Pattern(
        id="DS-DO-002",
        title="Disk Wipe Command",
        description="Detects commands that wipe disks or partitions",
        severity="critical",
        category="destructive_ops",
        regex=r"(dd\s+if=/dev/zero|format\s+[A-Z]:|diskpart|fdisk\s+.*-d|wipefs|shred\s+.*-[uvz])",
        file_patterns=["*"],
        cve_ids=[],
        remediation="Remove disk wiping commands",
    ),
    Pattern(
        id="DS-DO-003",
        title="Cloud Resource Destruction",
        description="Detects AWS/GCP/Azure resource deletion commands",
        severity="critical",
        category="destructive_ops",
        regex=r"(aws\s+.*(delete|terminate|destroy)|gcloud\s+.*delete|az\s+.*delete|kubectl\s+delete)",
        file_patterns=["*"],
        cve_ids=[],
        remediation="Review cloud resource deletion commands",
    ),
    Pattern(
        id="DS-DO-004",
        title="Git History Manipulation",
        description="Detects commands that modify git history destructively",
        severity="high",
        category="destructive_ops",
        regex=r"git\s+(push\s+.*--force|reset\s+--hard|clean\s+-fd|filter-branch)",
        file_patterns=["*"],
        cve_ids=[],
        remediation="Review git history modification commands",
    ),
    Pattern(
        id="DS-DO-005",
        title="Database Drop Command",
        description="Detects SQL commands that drop databases or tables",
        severity="critical",
        category="destructive_ops",
        regex=r"(DROP\s+(DATABASE|TABLE|SCHEMA)|TRUNCATE\s+TABLE|DELETE\s+FROM\s+\w+\s*;)",
        file_patterns=["*"],
        cve_ids=[],
        remediation="Review database destruction commands",
    ),
    Pattern(
        id="DS-DO-006",
        title="Terraform Destroy",
        description="Detects terraform destroy commands",
        severity="high",
        category="destructive_ops",
        regex=r"terraform\s+(destroy|apply\s+.*-destroy)",
        file_patterns=["*"],
        cve_ids=[],
        remediation="Review infrastructure destruction commands",
    ),
    Pattern(
        id="DS-DO-007",
        title="Container/Pod Deletion",
        description="Detects kubernetes/docker mass deletion commands",
        severity="high",
        category="destructive_ops",
        regex=r"(kubectl\s+delete\s+.*--all|docker\s+(rm|rmi)\s+.*-f|\$\(docker\s+ps)",
        file_patterns=["*"],
        cve_ids=[],
        remediation="Review container deletion commands",
    ),
]
