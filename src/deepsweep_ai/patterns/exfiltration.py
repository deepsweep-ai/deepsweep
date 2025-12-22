"""
Data Exfiltration Detection Patterns

Covers:
- DNS exfiltration
- HTTP callbacks
- Environment variable exposure
- Credential harvesting
"""

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


EXFILTRATION_PATTERNS: List[Pattern] = [
    Pattern(
        id="DS-EX-001",
        title="DNS Exfiltration Pattern",
        description="Detects DNS-based data exfiltration attempts",
        severity="critical",
        category="exfiltration",
        regex=r"(nslookup|dig|host)\s+.{0,50}\$|(\$\{?\w+\}?)\.(burp|oast|interact|dnslog|ceye|requestbin)",
        file_patterns=[".cursorrules", "CLAUDE.md", "AGENTS.md", "*.sh"],
        cve_ids=["CVE-2025-55284"],
        remediation="Remove DNS lookup commands with variable interpolation",
    ),
    Pattern(
        id="DS-EX-002",
        title="HTTP Callback Exfiltration",
        description="Detects HTTP-based data exfiltration to external services",
        severity="critical",
        category="exfiltration",
        regex=r"(curl|wget|fetch|http|request).{0,50}(burp|oast|interact|webhook|requestbin|pipedream|hookbin|ngrok)",
        file_patterns=[".cursorrules", "CLAUDE.md", "AGENTS.md"],
        cve_ids=["CVE-2025-55284"],
        remediation="Remove HTTP callbacks to external services",
    ),
    Pattern(
        id="DS-EX-003",
        title="Environment Variable Exposure",
        description="Detects commands that expose environment variables externally",
        severity="high",
        category="exfiltration",
        regex=r"(env|printenv|export|echo\s+\$).{0,30}(curl|wget|nc|netcat|\||>)",
        file_patterns=["*"],
        cve_ids=["CVE-2025-55284"],
        remediation="Remove commands that pipe environment variables externally",
    ),
    Pattern(
        id="DS-EX-004",
        title="Credential File Access",
        description="Detects access to credential files like .env, .aws, .ssh",
        severity="high",
        category="exfiltration",
        regex=r"(cat|type|read|load|open|include).{0,30}(\.env|\.aws|credentials|\.ssh|id_rsa|\.netrc|\.npmrc|\.pypirc)",
        file_patterns=[".cursorrules", "CLAUDE.md", "AGENTS.md"],
        cve_ids=[],
        remediation="Remove instructions to access credential files",
    ),
    Pattern(
        id="DS-EX-005",
        title="Clipboard Exfiltration",
        description="Detects attempts to access and exfiltrate clipboard contents",
        severity="medium",
        category="exfiltration",
        regex=r"(pbpaste|xclip|xsel|powershell.{0,30}clipboard|Get-Clipboard).{0,30}(curl|wget|nc|\||>)",
        file_patterns=["*"],
        cve_ids=[],
        remediation="Remove clipboard access combined with network operations",
    ),
    Pattern(
        id="DS-EX-006",
        title="Git Credential Extraction",
        description="Detects attempts to extract git credentials",
        severity="high",
        category="exfiltration",
        regex=r"git\s+(credential|config).{0,30}(fill|get|store|helper)|\.git-credentials",
        file_patterns=[".cursorrules", "CLAUDE.md"],
        cve_ids=[],
        remediation="Remove git credential access patterns",
    ),
]
