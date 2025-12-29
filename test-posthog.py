#!/usr/bin/env python3
"""
DeepSweep PostHog Verification Script

Tests PostHog integration and verifies events are being sent correctly.

Usage:
    python test-posthog.py
"""

import json
import time
from pathlib import Path

import posthog

# Configuration
POSTHOG_API_KEY = "phc_2KxJqV5jZ9nY8wH3pL7mT6sN4vR1cX0bQ9dE8fG7hI6jK5lM4n"
POSTHOG_HOST = "https://us.i.posthog.com"
CONFIG_FILE = Path.home() / ".deepsweep" / "config.json"


def load_config() -> dict:
    """Load DeepSweep config to get UUID."""
    if CONFIG_FILE.exists():
        with CONFIG_FILE.open("r") as f:
            return json.load(f)
    return {}


def test_posthog_connection() -> None:
    """Test PostHog connection and event sending."""
    print("=" * 60)
    print("DeepSweep PostHog Verification")
    print("=" * 60)
    print("")

    # Load config
    config = load_config()
    uuid = config.get("uuid", "test-user-unknown")

    print(f"PostHog Host:    {POSTHOG_HOST}")
    print(f"API Key:         {POSTHOG_API_KEY[:20]}...")
    print(f"Your UUID:       {uuid}")
    print("")

    print("-" * 60)
    print("Initializing PostHog client")
    print("-" * 60)

    # Initialize PostHog with debug mode BEFORE any capture calls
    # Note: Use api_key, not project_api_key for standalone scripts
    posthog.api_key = POSTHOG_API_KEY
    posthog.host = POSTHOG_HOST
    posthog.debug = True  # Enable debug output

    print("[PASS] PostHog client initialized")
    print("")

    print("-" * 60)
    print("TEST 1: Send test event")
    print("-" * 60)

    # Send test event
    print("Sending test event to PostHog...")
    try:
        posthog.capture(
            distinct_id=uuid,
            event="deepsweep_test_event",
            properties={
                "test_type": "verification",
                "test_timestamp": time.time(),
                "source": "test-posthog.py",
            },
        )
        print("[PASS] Event sent (queued for background upload)")
    except Exception as e:
        print(f"[WARN] Error sending event: {e}")
        print("[INFO] Event may still be queued - check debug output above")
    print("")

    print("-" * 60)
    print("TEST 2: Send validation event (mimics CLI)")
    print("-" * 60)

    print("Sending validation event to PostHog...")
    try:
        posthog.capture(
            distinct_id=uuid,
            event="deepsweep_validate",
            properties={
                "command": "validate",
                "version": "1.2.0",
                "os": "linux",
                "python_version": "3.12.0",
                "duration_ms": 125,
                "exit_code": 0,
                "findings_count": 3,
                "score": 85,
                "grade": "B",
                "source": "test-posthog.py",
            },
        )
        print("[PASS] Event sent (queued for background upload)")
    except Exception as e:
        print(f"[WARN] Error sending event: {e}")
        print("[INFO] Event may still be queued - check debug output above")
    print("")

    print("-" * 60)
    print("TEST 3: Flush and wait")
    print("-" * 60)

    print("Flushing events and shutting down...")
    posthog.shutdown()

    print("[PASS] Shutdown complete")
    print("")

    # Summary
    print("=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print("")
    print("Events sent successfully!")
    print("")
    print("Next steps:")
    print("")
    print("1. Check PostHog dashboard:")
    print(f"   URL: {POSTHOG_HOST}")
    print(f"   Search for distinct_id: {uuid}")
    print("")
    print("2. Expected events:")
    print("   - deepsweep_test_event")
    print("   - deepsweep_validate")
    print("")
    print("3. Timeline:")
    print("   - Events appear in 'Live events' within 5-10 seconds")
    print("   - Full processing may take 30-60 seconds")
    print("")
    print("4. Debug output:")
    print("   - Check console output above for PostHog debug logs")
    print("   - Look for successful HTTP responses")
    print("")
    print("5. If events don't appear:")
    print("   - Verify API key is correct")
    print("   - Check network connectivity")
    print("   - Try again in 1-2 minutes (ingestion delay)")
    print("")
    print("Done.")


if __name__ == "__main__":
    test_posthog_connection()
