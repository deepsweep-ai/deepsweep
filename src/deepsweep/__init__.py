"""
DeepSweep - Security Gateway for AI Coding Assistants.

Validate configurations for Cursor, Copilot, Claude Code, Windsurf,
and MCP servers before they execute. Ship with vibes. Ship secure.
"""

from deepsweep.exceptions import DeepSweepError, PatternError, ValidationError
from deepsweep.models import Finding, Severity, ValidationResult
from deepsweep.validator import validate_content, validate_path

__version__ = "1.0.0"
__all__ = [
    "__version__",
    "validate_path",
    "validate_content",
    "ValidationResult",
    "Finding",
    "Severity",
    "DeepSweepError",
    "ValidationError",
    "PatternError",
]
