"""
Configuration management for DeepSweep.

Handles:
- Mode selection (observe vs enforce)
- Pricing tier limits
- API key management
- Custom rule configuration
"""

from __future__ import annotations

import os
import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any

import yaml


class Mode(Enum):
    """Scan mode - OBSERVE is default to minimize developer friction."""
    OBSERVE = "observe"   # Monitor + alert, no blocking (DEFAULT)
    ENFORCE = "enforce"   # Block dangerous actions


class Tier(Enum):
    """Pricing tiers."""
    FREE = "free"           # 100 scans/month, 3 projects
    PRO = "pro"             # Unlimited scans, unlimited projects, $20/month
    TEAM = "team"           # Pro + team dashboard, $15/user/month
    ENTERPRISE = "enterprise"  # Custom


@dataclass
class TierLimits:
    """Limits per pricing tier."""
    scans_per_month: int
    max_projects: int
    max_file_size_mb: int
    sarif_export: bool
    api_access: bool
    priority_support: bool

    @classmethod
    def for_tier(cls, tier: Tier) -> "TierLimits":
        limits = {
            Tier.FREE: cls(
                scans_per_month=100,
                max_projects=3,
                max_file_size_mb=10,
                sarif_export=False,
                api_access=False,
                priority_support=False,
            ),
            Tier.PRO: cls(
                scans_per_month=-1,  # Unlimited
                max_projects=-1,
                max_file_size_mb=100,
                sarif_export=True,
                api_access=True,
                priority_support=False,
            ),
            Tier.TEAM: cls(
                scans_per_month=-1,
                max_projects=-1,
                max_file_size_mb=500,
                sarif_export=True,
                api_access=True,
                priority_support=True,
            ),
            Tier.ENTERPRISE: cls(
                scans_per_month=-1,
                max_projects=-1,
                max_file_size_mb=-1,
                sarif_export=True,
                api_access=True,
                priority_support=True,
            ),
        }
        return limits[tier]


@dataclass
class Config:
    """DeepSweep configuration."""

    mode: Mode = Mode.OBSERVE  # DEFAULT: Observe mode (no blocking)
    tier: Tier = Tier.FREE
    api_key: Optional[str] = None
    api_endpoint: str = "https://api.deepsweep.ai/v1"

    # Scan settings
    include_patterns: List[str] = field(default_factory=lambda: [
        ".cursorrules",
        ".cursor/rules",
        ".github/copilot-instructions.md",
        "AGENTS.md",
        ".amazonq/",
        ".continue/",
        ".aider*",
        ".claude*",
        "mcp.json",
        "mcp-config.json",
        "claude_desktop_config.json",
        ".mcp/",
        "*.mcp.yaml",
        "*.mcp.json",
    ])

    exclude_patterns: List[str] = field(default_factory=lambda: [
        "node_modules/",
        ".git/",
        "__pycache__/",
        "*.pyc",
        ".venv/",
        "venv/",
    ])

    # Detection settings
    enable_prompt_injection: bool = True
    enable_exfiltration: bool = True
    enable_destructive_ops: bool = True
    enable_supply_chain: bool = True
    enable_mcp_poisoning: bool = True
    enable_extension_risk: bool = True

    # Output settings
    output_format: str = "text"  # text, json, sarif
    verbose: bool = False
    quiet: bool = False

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Config":
        """Load config from file or environment."""
        config = cls()

        # Load from file if exists
        config_paths = [
            path,
            Path(".deepsweep.yaml"),
            Path(".deepsweep.yml"),
            Path(".deepsweep.json"),
            Path.home() / ".config" / "deepsweep" / "config.yaml",
        ]

        for config_path in config_paths:
            if config_path and config_path.exists():
                config._load_from_file(config_path)
                break

        # Override with environment variables
        config._load_from_env()

        return config

    def _load_from_file(self, path: Path) -> None:
        """Load configuration from file."""
        content = path.read_text()

        if path.suffix in (".yaml", ".yml"):
            data = yaml.safe_load(content)
        else:
            data = json.loads(content)

        if not data:
            return

        if "mode" in data:
            self.mode = Mode(data["mode"])
        if "api_key" in data:
            self.api_key = data["api_key"]
        if "include_patterns" in data:
            self.include_patterns = data["include_patterns"]
        if "exclude_patterns" in data:
            self.exclude_patterns = data["exclude_patterns"]

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        if api_key := os.environ.get("DEEPSWEEP_API_KEY"):
            self.api_key = api_key

        if mode := os.environ.get("DEEPSWEEP_MODE"):
            self.mode = Mode(mode.lower())

        if endpoint := os.environ.get("DEEPSWEEP_API_ENDPOINT"):
            self.api_endpoint = endpoint

    def save(self, path: Path) -> None:
        """Save configuration to file."""
        data = {
            "mode": self.mode.value,
            "api_key": self.api_key,
            "include_patterns": self.include_patterns,
            "exclude_patterns": self.exclude_patterns,
        }

        path.parent.mkdir(parents=True, exist_ok=True)

        if path.suffix in (".yaml", ".yml"):
            path.write_text(yaml.dump(data, default_flow_style=False))
        else:
            path.write_text(json.dumps(data, indent=2))


# Legacy compatibility functions
def get_api_key() -> Optional[str]:
    """Get API key from config."""
    return Config.load().api_key


def set_api_key(key: str) -> None:
    """Set API key in config."""
    config = Config.load()
    config.api_key = key
    config.save(Path.home() / ".config" / "deepsweep" / "config.yaml")
