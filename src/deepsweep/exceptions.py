"""
Custom exceptions for DeepSweep.

All exceptions inherit from DeepSweepError for easy catching.
"""


class DeepSweepError(Exception):
    """Base exception for all DeepSweep errors."""

    def __init__(self, message: str, details: str | None = None) -> None:
        self.message = message
        self.details = details
        super().__init__(message)


class ValidationError(DeepSweepError):
    """Raised when validation fails unexpectedly."""
    pass


class PatternError(DeepSweepError):
    """Raised when a pattern is invalid or fails to compile."""
    pass


class ConfigurationError(DeepSweepError):
    """Raised when configuration is invalid."""
    pass


class FileAccessError(DeepSweepError):
    """Raised when a file cannot be read."""
    pass
