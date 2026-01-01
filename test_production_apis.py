#!/usr/bin/env python3
"""
Production API Testing - LIVE ENDPOINTS

This tests actual connectivity to:
1. PostHog API (us.i.posthog.com)
2. Threat Intelligence API (api.deepsweep.ai/v1/signal)
"""

import json
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_real_posthog():
    """Test PostHog with a real event."""
    print("\n" + "="*70)
    print("TEST 1: PostHog Production API")
    print("="*70)

    try:
        import posthog
        from deepsweep.telemetry import POSTHOG_API_KEY, POSTHOG_HOST

        print(f"\nConfiguration:")
        print(f"  API Key: {POSTHOG_API_KEY[:20]}...")
        print(f"  Host: {POSTHOG_HOST}")

        # Initialize
        posthog.project_api_key = POSTHOG_API_KEY
        posthog.host = POSTHOG_HOST

        # Send test event
        test_id = f"test-{int(time.time())}"
        print(f"\nSending test event (ID: {test_id})...")

        posthog.capture(
            distinct_id=test_id,
            event="deepsweep_test",
            properties={
                "test": True,
                "timestamp": time.time(),
                "source": "production_api_test",
                "version": "0.1.0",
            },
        )

        # Flush to ensure delivery
        print("Flushing events...")
        posthog.flush()

        print("\n[RESULT] Event sent successfully")
        print("  Check dashboard: https://us.i.posthog.com/project/265866/events")
        print(f"  Look for event 'deepsweep_test' with distinct_id '{test_id}'")

        return True

    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_real_threat_intel():
    """Test threat intelligence API with real request."""
    print("\n" + "="*70)
    print("TEST 2: Threat Intelligence Production API")
    print("="*70)

    try:
        from deepsweep.telemetry import (
            THREAT_INTEL_ENDPOINT,
            create_threat_signal,
        )
        from urllib.request import Request, urlopen
        from urllib.error import HTTPError, URLError

        print(f"\nEndpoint: {THREAT_INTEL_ENDPOINT}")

        # Create test signal
        signal = create_threat_signal(
            findings_count=3,
            score=92,
            grade="A",
            duration_ms=850,
            pattern_ids=["test-pattern-validation"],
            cve_matches=[],
            severity_counts={"medium": 2, "low": 1},
        )

        payload = {
            "event": "threat_signal",
            "version": "1",
            **signal.__dict__,
        }

        print(f"\nSending test threat signal...")
        print(f"  Score: {signal.score}")
        print(f"  Grade: {signal.grade}")
        print(f"  Findings: {signal.finding_count}")

        # Send request
        request = Request(
            THREAT_INTEL_ENDPOINT,
            data=json.dumps(payload, default=str).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "deepsweep-cli/0.1.0-test",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=10) as response:
                status = response.status
                body = response.read().decode("utf-8")

                print(f"\n[RESULT] Response received")
                print(f"  Status Code: {status}")
                print(f"  Response: {body[:200] if body else '(empty)'}")

                if status == 200:
                    print("\n[SUCCESS] Threat intel API working correctly!")
                    return True
                else:
                    print(f"\n[WARNING] Unexpected status: {status}")
                    return False

        except HTTPError as e:
            print(f"\n[ERROR] HTTP {e.code}: {e.reason}")
            try:
                error_body = e.read().decode("utf-8")
                print(f"  Response: {error_body[:200]}")
            except:
                pass
            return False

        except URLError as e:
            print(f"\n[ERROR] Connection failed: {e.reason}")
            print("  This might be a network/proxy issue")
            return False

    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integrated_telemetry():
    """Test the integrated telemetry client."""
    print("\n" + "="*70)
    print("TEST 3: Integrated Telemetry Client")
    print("="*70)

    try:
        from deepsweep.telemetry import get_telemetry_client
        import tempfile
        from unittest.mock import patch

        # Use temp config to avoid polluting real config
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".deepsweep"
            config_file = config_dir / "config.json"

            with patch('deepsweep.telemetry.CONFIG_DIR', config_dir):
                with patch('deepsweep.telemetry.CONFIG_FILE', config_file):
                    client = get_telemetry_client()

                    print(f"\nConfig:")
                    print(f"  UUID: {client.config.uuid[:20]}...")
                    print(f"  Enabled: {client.config.enabled}")
                    print(f"  Offline: {client.config.offline_mode}")

                    print(f"\nSending test command event...")

                    # Track a test command
                    client.track_command(
                        command="validate",
                        exit_code=0,
                        findings_count=2,
                        pattern_count=15,
                        output_format="json",
                        score=95,
                        grade="A",
                    )

                    print("Shutting down and flushing...")
                    client.shutdown()

                    print("\n[RESULT] Events sent via integrated client")
                    print("  Check PostHog for 'deepsweep_validate' event")

        return True

    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all production API tests."""
    print("\n" + "="*70)
    print("PRODUCTION API TESTING")
    print("="*70)
    print("\n⚠️  TESTING LIVE ENDPOINTS ⚠️")
    print("\nThis will send real events to:")
    print("  1. PostHog (us.i.posthog.com)")
    print("  2. Threat Intel API (api.deepsweep.ai/v1/signal)")

    input("\nPress ENTER to continue or Ctrl+C to cancel...")

    tests = [
        ("PostHog API", test_real_posthog),
        ("Threat Intel API", test_real_threat_intel),
        ("Integrated Client", test_integrated_telemetry),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
            time.sleep(1)  # Brief pause between tests
        except KeyboardInterrupt:
            print("\n\nTest cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n[ERROR] {test_name} crashed: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "="*70)
    print("PRODUCTION TEST SUMMARY")
    print("="*70)

    for test_name, passed in results.items():
        if passed is None:
            status = "[SKIP]"
        elif passed:
            status = "[PASS]"
        else:
            status = "[FAIL]"
        print(f"  {status} {test_name}")

    total_passed = sum(1 for r in results.values() if r is True)
    total_tests = len([r for r in results.values() if r is not None])

    print(f"\nTotal: {total_passed}/{total_tests} tests passed")

    if all(results.values()):
        print("\n" + "="*70)
        print("✅ ALL PRODUCTION TESTS PASSED")
        print("="*70)
        print("\nNext steps:")
        print("  1. Check PostHog dashboard for events")
        print("  2. Verify threat intel API received signals")
        print("  3. Monitor for any errors in production")
        return 0
    else:
        print("\n" + "="*70)
        print("⚠️  SOME TESTS FAILED")
        print("="*70)
        print("\nReview errors above and:")
        print("  1. Check network connectivity")
        print("  2. Verify API endpoints are accessible")
        print("  3. Confirm API keys are valid")
        return 1


if __name__ == "__main__":
    sys.exit(main())
