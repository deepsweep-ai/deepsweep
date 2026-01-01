#!/usr/bin/env python3
"""
Test script to verify PostHog and Threat Intelligence API integration.

This script tests:
1. PostHog event capture and API connectivity
2. Threat intelligence signal endpoint (api.deepsweep.ai/v1/signal)
3. Both tier-1 (essential) and tier-2 (optional) telemetry systems
"""

import json
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

import posthog

from deepsweep.telemetry import (
    POSTHOG_API_KEY,
    POSTHOG_HOST,
    THREAT_INTEL_ENDPOINT,
    ThreatSignal,
    create_threat_signal,
    get_telemetry_client,
)


def test_posthog_api() -> bool:
    """Test PostHog API connectivity and event capture."""
    print("\n" + "=" * 70)
    print("TEST 1: PostHog API Integration (TIER 2 - Optional Analytics)")
    print("=" * 70)

    print(f"\nPostHog Configuration:")
    print(f"  API Key: {POSTHOG_API_KEY[:20]}...")
    print(f"  Host: {POSTHOG_HOST}")

    try:
        # Initialize PostHog
        posthog.project_api_key = POSTHOG_API_KEY
        posthog.host = POSTHOG_HOST

        # Create a test event
        test_event_id = f"test-{int(time.time())}"
        print(f"\nSending test event (ID: {test_event_id})...")

        posthog.capture(
            distinct_id=test_event_id,
            event="test_integration",
            properties={
                "test": True,
                "timestamp": time.time(),
                "source": "integration_test",
            },
        )

        # Flush to ensure event is sent
        print("Flushing PostHog events...")
        posthog.flush()

        print("\n[PASS] PostHog event sent successfully")
        print("  Status: Event queued and flushed")
        print("  Note: Check PostHog dashboard to verify event arrival")
        print("  Dashboard: https://us.i.posthog.com")

        return True

    except Exception as e:
        print(f"\n[FAIL] PostHog test failed: {e}")
        print(f"  Error type: {type(e).__name__}")
        return False


def test_threat_intel_api() -> bool:
    """Test Threat Intelligence API endpoint connectivity."""
    print("\n" + "=" * 70)
    print("TEST 2: Threat Intelligence API (TIER 1 - Essential)")
    print("=" * 70)

    print(f"\nThreat Intel Configuration:")
    print(f"  Endpoint: {THREAT_INTEL_ENDPOINT}")

    # Create a test threat signal
    signal = create_threat_signal(
        findings_count=5,
        score=85,
        grade="B",
        duration_ms=1250,
        pattern_ids=["test-pattern-1", "test-pattern-2"],
        cve_matches=["CVE-2024-1234"],
        severity_counts={"high": 2, "medium": 3},
    )

    # Prepare payload
    payload = {
        "event": "threat_signal",
        "version": "1",
        **signal.__dict__,
    }

    print(f"\nSending test threat signal...")
    print(f"  Findings: {payload['finding_count']}")
    print(f"  Score: {payload['score']}")
    print(f"  Grade: {payload['grade']}")
    print(f"  Patterns: {len(payload['pattern_ids'])}")

    try:
        # Send request
        request = Request(
            THREAT_INTEL_ENDPOINT,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "deepsweep-cli/test",
            },
            method="POST",
        )

        print(f"\nMaking request to {THREAT_INTEL_ENDPOINT}...")

        with urlopen(request, timeout=10) as response:
            status_code = response.status
            response_body = response.read().decode("utf-8")

            print(f"\n[{'PASS' if status_code == 200 else 'WARN'}] Response received")
            print(f"  Status Code: {status_code}")
            print(f"  Response: {response_body[:200] if response_body else '(empty)'}")

            if status_code == 200:
                print("\n[PASS] Threat intelligence endpoint is working correctly")
                return True
            else:
                print(f"\n[WARN] Unexpected status code: {status_code}")
                return False

    except HTTPError as e:
        print(f"\n[FAIL] HTTP Error: {e.code} {e.reason}")
        try:
            error_body = e.read().decode("utf-8")
            print(f"  Error response: {error_body[:200]}")
        except Exception:
            pass
        return False

    except URLError as e:
        print(f"\n[FAIL] URL Error: {e.reason}")
        return False

    except Exception as e:
        print(f"\n[FAIL] Unexpected error: {e}")
        print(f"  Error type: {type(e).__name__}")
        return False


def test_telemetry_client() -> bool:
    """Test the integrated telemetry client."""
    print("\n" + "=" * 70)
    print("TEST 3: Integrated Telemetry Client")
    print("=" * 70)

    try:
        client = get_telemetry_client()

        print("\nTelemetry Config:")
        print(f"  UUID: {client.config.uuid}")
        print(f"  Enabled: {client.config.enabled}")
        print(f"  Offline Mode: {client.config.offline_mode}")
        print(f"  First Run: {client.config.first_run}")

        print("\nTesting track_command method...")
        client.track_command(
            command="test_validate",
            exit_code=0,
            findings_count=3,
            pattern_count=10,
            output_format="json",
            score=90,
            grade="A",
        )

        print("\nFlushing events...")
        client.shutdown()

        print("\n[PASS] Telemetry client test completed")
        return True

    except Exception as e:
        print(f"\n[FAIL] Telemetry client test failed: {e}")
        print(f"  Error type: {type(e).__name__}")
        return False


def main() -> None:
    """Run all integration tests."""
    print("\n")
    print("=" * 70)
    print("DeepSweep Telemetry Integration Test Suite")
    print("=" * 70)
    print("\nThis test verifies:")
    print("  1. PostHog event capture (Tier 2 - Optional)")
    print("  2. Threat intelligence API (Tier 1 - Essential)")
    print("  3. Integrated telemetry client functionality")

    results = {
        "PostHog API": test_posthog_api(),
        "Threat Intel API": test_threat_intel_api(),
        "Telemetry Client": test_telemetry_client(),
    }

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {test_name}")

    total_passed = sum(results.values())
    total_tests = len(results)

    print(f"\nTotal: {total_passed}/{total_tests} tests passed")

    if all(results.values()):
        print("\n[PASS] All telemetry systems are working correctly")
        print("\nNext Steps:")
        print("  1. Check PostHog dashboard for test events")
        print("  2. Verify threat signals are being received by backend")
        print("  3. Monitor for any errors in production")
    else:
        print("\n[WARN] Some tests failed - review output above")
        print("\nTroubleshooting:")
        print("  1. Check network connectivity")
        print("  2. Verify API keys are valid")
        print("  3. Check endpoint URLs are correct")
        print("  4. Review firewall/proxy settings")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
