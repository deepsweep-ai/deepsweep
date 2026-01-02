"""
DeepSweep - The #1 Security Gateway for Agentic AI Code Assistants.

Privacy-preserving validation for AI assistant configurations, preventing
prompt injection, MCP poisoning, and supply chain attacks before execution.

Validates MCP (Model Context Protocol), AG-UI (Agent-User Interface), and
A2A (Agent-to-Agent) protocols across Cursor, Copilot, Claude Code, Windsurf,
and MCP servers.
"""

from deepsweep.exceptions import DeepSweepError, PatternError, ValidationError
from deepsweep.models import Finding, Severity, ValidationResult
from deepsweep.validator import validate_content, validate_path

__version__ = "0.1.0"
__all__ = [
    "DeepSweepError",
    "Finding",
    "PatternError",
    "Severity",
    "ValidationError",
    "ValidationResult",
    "__version__",
    "validate_content",
    "validate_path",
]
