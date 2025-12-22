"""
DeepSweep Detection Patterns

Seed database covering 24+ CVEs and 30+ detection patterns.
"""

from .prompt_injection import PROMPT_INJECTION_PATTERNS
from .exfiltration import EXFILTRATION_PATTERNS
from .destructive_ops import DESTRUCTIVE_OPS_PATTERNS
from .supply_chain import SUPPLY_CHAIN_PATTERNS
from .mcp_poisoning import MCP_POISONING_PATTERNS
from .extension_risk import EXTENSION_RISK_PATTERNS
from .cves import CVE_DATABASE

__all__ = [
    "PROMPT_INJECTION_PATTERNS",
    "EXFILTRATION_PATTERNS",
    "DESTRUCTIVE_OPS_PATTERNS",
    "SUPPLY_CHAIN_PATTERNS",
    "MCP_POISONING_PATTERNS",
    "EXTENSION_RISK_PATTERNS",
    "CVE_DATABASE",
    "ALL_PATTERNS",
]

ALL_PATTERNS = (
    PROMPT_INJECTION_PATTERNS +
    EXFILTRATION_PATTERNS +
    DESTRUCTIVE_OPS_PATTERNS +
    SUPPLY_CHAIN_PATTERNS +
    MCP_POISONING_PATTERNS +
    EXTENSION_RISK_PATTERNS
)

# Stats for marketing/social proof
PATTERN_COUNT = len(ALL_PATTERNS)
CVE_COUNT = len(CVE_DATABASE)
