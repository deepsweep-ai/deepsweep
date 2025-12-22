"""
DeepSweep API Client

Handles communication with DeepSweep cloud services for:
- Scan telemetry (anonymous)
- Pro feature validation
- Badge status updates
"""

from __future__ import annotations

import hashlib
from typing import Optional, Dict, Any

import httpx

from deepsweep_ai.config import Config
from deepsweep_ai.scanner import ScanResult


class APIClient:
    """Client for DeepSweep API."""

    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.api_endpoint
        self._client = httpx.Client(timeout=10.0)

    def report_scan(self, result: ScanResult) -> Optional[Dict[str, Any]]:
        """
        Report scan results to API.

        This enables:
        - Badge status updates
        - Aggregate threat intelligence
        - Usage tracking for tier limits
        """
        # Anonymize path for privacy
        path_hash = hashlib.sha256(result.path_scanned.encode()).hexdigest()[:16]

        payload = {
            "scan_id": result.scan_id,
            "path_hash": path_hash,
            "safe": result.safe,
            "score": result.score,
            "status": result.status,
            "findings_count": len(result.findings),
            "blocked_count": result.blocked_count,
            "duration_ms": result.duration_ms,
            "mode": result.mode.value,
            # Severity breakdown (no details)
            "severities": {
                "critical": sum(1 for f in result.findings if f.severity.value == "critical"),
                "high": sum(1 for f in result.findings if f.severity.value == "high"),
                "medium": sum(1 for f in result.findings if f.severity.value == "medium"),
                "low": sum(1 for f in result.findings if f.severity.value == "low"),
            },
        }

        headers = {}
        if self.config.api_key:
            headers["X-API-Key"] = self.config.api_key

        try:
            response = self._client.post(
                f"{self.base_url}/scan",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    def validate_key(self) -> Optional[Dict[str, Any]]:
        """Validate API key and get tier info."""
        if not self.config.api_key:
            return None

        try:
            response = self._client.get(
                f"{self.base_url}/auth/validate",
                headers={"X-API-Key": self.config.api_key},
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    def get_badge_url(self, owner: str, repo: str) -> str:
        """Get shields.io badge URL for repository."""
        return f"https://img.shields.io/endpoint?url={self.base_url}/badge/{owner}/{repo}"
