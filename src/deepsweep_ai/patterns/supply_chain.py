"""Supply Chain Attack Detection Patterns"""

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


SUPPLY_CHAIN_PATTERNS: List[Pattern] = [
    Pattern(
        id="DS-SC-001",
        title="Curl Pipe Bash",
        description="Detects curl | bash pattern which can execute arbitrary code",
        severity="critical",
        category="supply_chain",
        regex=r"curl\s+.*\|\s*(bash|sh|zsh)|wget\s+.*-O-\s*\|\s*(bash|sh)",
        file_patterns=["*"],
        cve_ids=[],
        remediation="Download scripts first, review, then execute",
    ),
    Pattern(
        id="DS-SC-002",
        title="Direct URL Package Install",
        description="Detects pip/npm install from direct URLs",
        severity="high",
        category="supply_chain",
        regex=r"(pip|pip3)\s+install\s+https?://|npm\s+install\s+https?://",
        file_patterns=["*"],
        cve_ids=[],
        remediation="Use package registries instead of direct URL installs",
    ),
    Pattern(
        id="DS-SC-003",
        title="Custom Package Registry",
        description="Detects configuration of untrusted package registries",
        severity="medium",
        category="supply_chain",
        regex=r"(registry\s*=|--index-url|--extra-index-url)\s*https?://(?!pypi\.org|registry\.npmjs\.org)",
        file_patterns=["*.toml", "*.cfg", ".npmrc", ".pip.conf", "pip.conf"],
        cve_ids=[],
        remediation="Only use trusted package registries",
    ),
    Pattern(
        id="DS-SC-004",
        title="Unpinned Dependency",
        description="Detects installation of packages without version pinning",
        severity="low",
        category="supply_chain",
        regex=r'(pip|pip3)\s+install\s+(?!.*[=<>!])[a-zA-Z][a-zA-Z0-9_-]+\s*$',
        file_patterns=["*"],
        cve_ids=[],
        remediation="Pin package versions for reproducible builds",
    ),
    Pattern(
        id="DS-SC-005",
        title="Suspicious Postinstall Script",
        description="Detects npm packages with suspicious postinstall scripts",
        severity="high",
        category="supply_chain",
        regex=r'"(postinstall|preinstall)"\s*:\s*".*(curl|wget|nc|bash|sh|eval|exec)',
        file_patterns=["package.json"],
        cve_ids=["CVE-2025-64439"],
        remediation="Review and remove suspicious lifecycle scripts",
    ),
]
