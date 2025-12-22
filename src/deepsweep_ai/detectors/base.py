"""Base detector class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from deepsweep_ai.scanner import Finding


class BaseDetector(ABC):
    """Base class for all detectors."""

    @abstractmethod
    def scan_file(self, path: Path) -> List["Finding"]:
        """
        Scan a single file for security issues.

        Args:
            path: Path to file to scan

        Returns:
            List of findings (empty if none found)
        """
        pass

    def _read_file(self, path: Path) -> str:
        """Safely read file contents."""
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""
