#!/usr/bin/env python3
"""
Quick test script to verify PostHog is working.

Usage:
    # Using the default/placeholder key (won't send real events):
    python test_posthog.py

    # Using your actual PostHog key:
    export POSTHOG_API_KEY="phc_YOUR_REAL_KEY_HERE"
    python test_posthog.py
"""

import os
import sys
import time

# Add src to path so we can import deepsweep
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from deepsweep.telemetry import get_telemetry_client

def main():
    print("=" * 60)
    print("PostHog Connection Test")
    print("=" * 60)

    # Check if using real API key or placeholder
    api_key = os.environ.get("POSTHOG_API_KEY", "phc_2KxJqV5jZ9nY8wH3pL7mT6sN4vR1cX0bQ9dE8fG7hI6jK5lM4n")
    if api_key == "phc_2KxJqV5jZ9nY8wH3pL7mT6sN4vR1cX0bQ9dE8fG7hI6jK5lM4n":
        print("\n⚠️  WARNING: Using placeholder API key!")
        print("   Events will NOT appear in your PostHog dashboard.")
        print("\n   To use your real key:")
        print("   export POSTHOG_API_KEY='phc_YOUR_REAL_KEY_HERE'")
        print("   python test_posthog.py\n")
    else:
        print(f"\n✅ Using custom API key: {api_key[:15]}...")
        print("   Events should appear in your PostHog dashboard\n")

    # Get telemetry client
    print("Initializing telemetry client...")
    client = get_telemetry_client()

    # Identify user
    print(f"User UUID: {client.config.uuid}")
    print("\nSending identify event...")
    client.identify()

    # Send a test event
    print("Sending test validation event...")
    client.track_command(
        command="validate",
        exit_code=0,
        findings_count=3,
        pattern_count=16,
        output_format="json",
        score=85,
        grade="B",
    )

    # Send a test error
    print("Sending test error event...")
    client.track_error(
        command="validate",
        error_type="TestError",
        error_message="This is a test error from test_posthog.py",
    )

    # Flush events
    print("\nFlushing events to PostHog...")
    client.shutdown()

    # Give PostHog time to send
    print("Waiting 2 seconds for events to send...")
    time.sleep(2)

    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("=" * 60)

    if api_key == "phc_2KxJqV5jZ9nY8wH3pL7mT6sN4vR1cX0bQ9dE8fG7hI6jK5lM4n":
        print("\n⚠️  Remember: You need to set your REAL PostHog API key")
        print("   to see events in your dashboard!")
    else:
        print("\nCheck your PostHog dashboard for these events:")
        print("  1. Identify event")
        print("  2. deepsweep_validate event")
        print("  3. deepsweep_error event")
        print(f"\nUser distinct_id: {client.config.uuid}")

    print("\nPostHog dashboard: https://app.posthog.com")
    print()

if __name__ == "__main__":
    main()
