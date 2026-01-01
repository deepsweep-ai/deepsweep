#!/usr/bin/env python3
"""
Detailed API connectivity test for PostHog and Threat Intelligence endpoints.
"""

import json
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# Test configurations
POSTHOG_API_KEY = "phc_2KxJqV5jZ9nY8wH3pL7mT6sN4vR1cX0bQ9dE8fG7hI6jK5lM4n"
POSTHOG_HOST = "https://us.i.posthog.com"
THREAT_INTEL_ENDPOINT = "https://api.deepsweep.ai/v1/signal"


def test_posthog_capture_api():
    """Test PostHog Capture API directly using HTTP."""
    print("\n" + "=" * 70)
    print("TEST: PostHog Capture API (Direct HTTP)")
    print("=" * 70)

    # PostHog capture endpoint
    capture_url = f"{POSTHOG_HOST}/capture/"

    # Create test event payload
    payload = {
        "api_key": POSTHOG_API_KEY,
        "event": "test_integration",
        "properties": {
            "distinct_id": "test-user-123",
            "test": True,
            "source": "direct_http_test",
        },
        "timestamp": "2026-01-01T00:00:00.000Z",
    }

    print(f"\nEndpoint: {capture_url}")
    print(f"API Key: {POSTHOG_API_KEY[:20]}...")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        request = Request(
            capture_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "deepsweep-test/1.0",
            },
            method="POST",
        )

        print(f"\nSending request...")

        with urlopen(request, timeout=10) as response:
            status_code = response.status
            response_body = response.read().decode("utf-8")

            print(f"\n[{'PASS' if status_code == 200 else 'FAIL'}] Response")
            print(f"  Status Code: {status_code}")
            print(f"  Response Body: {response_body}")

            return status_code == 200

    except HTTPError as e:
        print(f"\n[FAIL] HTTP Error")
        print(f"  Code: {e.code}")
        print(f"  Reason: {e.reason}")
        try:
            error_body = e.read().decode("utf-8")
            print(f"  Response: {error_body}")
        except Exception:
            pass
        return False

    except URLError as e:
        print(f"\n[FAIL] URL Error: {e.reason}")
        return False

    except Exception as e:
        print(f"\n[FAIL] Unexpected Error: {e}")
        print(f"  Type: {type(e).__name__}")
        return False


def test_posthog_batch_api():
    """Test PostHog Batch API."""
    print("\n" + "=" * 70)
    print("TEST: PostHog Batch API")
    print("=" * 70)

    batch_url = f"{POSTHOG_HOST}/batch/"

    payload = {
        "api_key": POSTHOG_API_KEY,
        "batch": [
            {
                "event": "test_batch_event",
                "properties": {
                    "distinct_id": "test-user-batch",
                    "test": True,
                },
                "timestamp": "2026-01-01T00:00:00.000Z",
            }
        ],
    }

    print(f"\nEndpoint: {batch_url}")
    print(f"Sending batch request...")

    try:
        request = Request(
            batch_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "deepsweep-test/1.0",
            },
            method="POST",
        )

        with urlopen(request, timeout=10) as response:
            status_code = response.status
            response_body = response.read().decode("utf-8")

            print(f"\n[{'PASS' if status_code == 200 else 'FAIL'}] Response")
            print(f"  Status Code: {status_code}")
            print(f"  Response Body: {response_body}")

            return status_code == 200

    except HTTPError as e:
        print(f"\n[FAIL] HTTP Error: {e.code} {e.reason}")
        try:
            print(f"  Response: {e.read().decode('utf-8')}")
        except Exception:
            pass
        return False

    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        return False


def test_threat_intel_api():
    """Test Threat Intelligence API."""
    print("\n" + "=" * 70)
    print("TEST: Threat Intelligence API (api.deepsweep.ai)")
    print("=" * 70)

    payload = {
        "event": "threat_signal",
        "version": "1",
        "pattern_ids": ["test-1", "test-2"],
        "cve_matches": ["CVE-2024-1234"],
        "severity_counts": {"high": 2, "medium": 3},
        "score": 85,
        "grade": "B",
        "finding_count": 5,
        "duration_ms": 1250,
        "cli_version": "0.1.0",
        "os_type": "linux",
    }

    print(f"\nEndpoint: {THREAT_INTEL_ENDPOINT}")
    print(f"Payload: {json.dumps(payload, indent=2)[:300]}...")

    try:
        request = Request(
            THREAT_INTEL_ENDPOINT,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "deepsweep-cli/0.1.0",
            },
            method="POST",
        )

        print(f"\nSending request...")

        with urlopen(request, timeout=10) as response:
            status_code = response.status
            response_body = response.read().decode("utf-8")

            print(f"\n[{'PASS' if status_code == 200 else 'FAIL'}] Response")
            print(f"  Status Code: {status_code}")
            print(f"  Response Body: {response_body[:500]}")

            return status_code == 200

    except HTTPError as e:
        print(f"\n[FAIL] HTTP Error")
        print(f"  Code: {e.code}")
        print(f"  Reason: {e.reason}")
        try:
            error_body = e.read().decode("utf-8")
            print(f"  Response: {error_body[:500]}")
        except Exception:
            pass
        return False

    except URLError as e:
        print(f"\n[FAIL] URL Error")
        print(f"  Reason: {e.reason}")
        print(f"\nPossible causes:")
        print("  1. Network connectivity issues")
        print("  2. DNS resolution failure")
        print("  3. Firewall/proxy blocking the connection")
        print("  4. API endpoint not yet deployed")
        return False

    except Exception as e:
        print(f"\n[FAIL] Unexpected Error: {e}")
        print(f"  Type: {type(e).__name__}")
        return False


def main():
    """Run all API connectivity tests."""
    print("\n" + "=" * 70)
    print("DeepSweep API Connectivity Diagnostic")
    print("=" * 70)

    results = {
        "PostHog Capture API": test_posthog_capture_api(),
        "PostHog Batch API": test_posthog_batch_api(),
        "Threat Intel API": test_threat_intel_api(),
    }

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {test_name}")

    total_passed = sum(results.values())
    total_tests = len(results)

    print(f"\nTotal: {total_passed}/{total_tests} tests passed")

    if all(results.values()):
        print("\n[SUCCESS] All API endpoints are accessible")
        return 0
    else:
        print("\n[WARNING] Some API endpoints failed")
        print("\nRecommended Actions:")

        if not results["PostHog Capture API"] and not results["PostHog Batch API"]:
            print("  PostHog:")
            print("    - Verify API key is valid")
            print("    - Check network connectivity to us.i.posthog.com")
            print("    - Review PostHog account status")

        if not results["Threat Intel API"]:
            print("  Threat Intelligence:")
            print("    - Verify api.deepsweep.ai is accessible")
            print("    - Check if endpoint requires authentication")
            print("    - Confirm endpoint is deployed and active")
            print("    - Test with: curl -X POST https://api.deepsweep.ai/v1/signal")

        return 1


if __name__ == "__main__":
    sys.exit(main())
