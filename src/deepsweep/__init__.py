"""
DeepSweep - Security Gateway for AI Coding Assistants.

Validate configurations for Cursor, Copilot, Claude Code, Windsurf,
and MCP servers before they execute.
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
