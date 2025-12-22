"""
Constants used throughout DeepSweep.

Design Standards:
- NO EMOJIS
- ASCII symbols only
- Optimistic messaging
"""

from typing import Final

# Version
VERSION: Final[str] = "1.0.0"

# ASCII Symbols - NO EMOJIS
SYMBOL_PASS: Final[str] = "[PASS]"
SYMBOL_FAIL: Final[str] = "[FAIL]"
SYMBOL_WARN: Final[str] = "[WARN]"
SYMBOL_INFO: Final[str] = "[INFO]"
SYMBOL_SKIP: Final[str] = "[SKIP]"

# Branding
PRODUCT_NAME: Final[str] = "DeepSweep"
TAGLINE: Final[str] = "Security Gateway for AI Coding Assistants"
SLOGAN: Final[str] = "Ship with vibes. Ship secure."

# URLs
DOCS_URL: Final[str] = "https://docs.deepsweep.ai"
REMEDIATION_URL: Final[str] = "https://docs.deepsweep.ai/remediation"
REPO_URL: Final[str] = "https://github.com/deepsweep-ai/deepsweep"

# File patterns to scan
SCANNABLE_FILES: Final[tuple[str, ...]] = (
    ".cursorrules",
    ".cursor/rules",
    "cursor.rules",
    ".github/copilot-instructions.md",
    "copilot-instructions.md",
    ".copilot/instructions.md",
    "claude_desktop_config.json",
    ".claude/config.json",
    "mcp.json",
    ".mcp/config.json",
    ".windsurfrules",
    ".windsurf/rules",
)

# Severity thresholds for exit codes
SEVERITY_ORDER: Final[tuple[str, ...]] = ("low", "medium", "high", "critical")

# Grade scale with optimistic messaging
GRADE_SCALE: Final[dict[str, tuple[int, str]]] = {
    "A": (90, "Ship ready"),
    "B": (80, "Looking good"),
    "C": (70, "Review recommended"),
    "D": (60, "Attention needed"),
    "F": (0, "Let's fix this together"),
}

# Colors (ANSI)
class Colors:
    """ANSI color codes. Respects NO_COLOR."""

    RESET: Final[str] = "\033[0m"
    BOLD: Final[str] = "\033[1m"
    DIM: Final[str] = "\033[2m"

    # Severity colors
    CRITICAL: Final[str] = "\033[91m"  # Red
    HIGH: Final[str] = "\033[91m"       # Red
    MEDIUM: Final[str] = "\033[93m"     # Yellow
    LOW: Final[str] = "\033[94m"        # Blue
    INFO: Final[str] = "\033[94m"       # Blue
    PASS: Final[str] = "\033[92m"       # Green
