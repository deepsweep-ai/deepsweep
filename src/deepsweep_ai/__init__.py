"""
DeepSweep - The #1 Security Gateway for Agentic AI Code Assistants

Intercept and validate AI assistant configurations before execution.
Aligned with OWASP Top 10 for Agentic AI Applications (December 2025).

Coverage:
- Prompt injection (ASI01)
- MCP poisoning (ASI02, ASI04, ASI06)
- Supply chain attacks (ASI04)
- Credential exposure (ASI03)
- Auto-execution patterns (ASI05, ASI09)
"""

__version__ = "1.0.0rc1"
__description__ = "The #1 Security Gateway for Agentic AI Code Assistants"
__owasp_alignment__ = "OWASP Top 10 for Agentic AI Applications 2025"
__author__ = "DeepSweep.ai"

from deepsweep_ai.scanner import Scanner, ScanResult, Finding, Severity
from deepsweep_ai.config import Config, Mode

__all__ = [
    "__version__",
    "Scanner",
    "ScanResult",
    "Finding",
    "Severity",
    "Config",
    "Mode",
]
