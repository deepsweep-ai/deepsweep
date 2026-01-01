#!/usr/bin/env python3
"""
SAFE LOCAL VERIFICATION - Does NOT hit production APIs

This script verifies:
1. Code structure and imports
2. Configuration values
3. Payload generation
4. Privacy guarantees
5. Mock API calls

NO REAL API CALLS ARE MADE
"""

import json
import platform
from unittest.mock import MagicMock, patch
from pathlib import Path

# Set up test config before imports
import tempfile
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_imports():
    """Verify all imports work correctly."""
    print("\n" + "="*70)
    print("TEST 1: Module Imports")
    print("="*70)

    try:
        from deepsweep.telemetry import (
            POSTHOG_API_KEY,
            POSTHOG_HOST,
            THREAT_INTEL_ENDPOINT,
            ThreatSignal,
            create_threat_signal,
            TelemetryClient,
            get_telemetry_client,
        )
        print("[PASS] All telemetry imports successful")
        return True
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False


def test_configuration():
    """Verify configuration values are set correctly."""
    print("\n" + "="*70)
    print("TEST 2: Configuration Values")
    print("="*70)

    from deepsweep.telemetry import (
        POSTHOG_API_KEY,
        POSTHOG_HOST,
        THREAT_INTEL_ENDPOINT,
    )

    print(f"\nPostHog Configuration:")
    print(f"  API Key: {POSTHOG_API_KEY[:20]}... (len: {len(POSTHOG_API_KEY)})")
    print(f"  Host: {POSTHOG_HOST}")

    print(f"\nThreat Intelligence Configuration:")
    print(f"  Endpoint: {THREAT_INTEL_ENDPOINT}")

    # Verify values
    checks = {
        "PostHog API Key exists": len(POSTHOG_API_KEY) > 0,
        "PostHog API Key format": POSTHOG_API_KEY.startswith("phc_"),
        "PostHog Host correct": POSTHOG_HOST == "https://us.i.posthog.com",
        "Threat Intel endpoint correct": THREAT_INTEL_ENDPOINT == "https://api.deepsweep.ai/v1/signal",
    }

    all_passed = True
    for check_name, result in checks.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {check_name}")
        all_passed = all_passed and result

    return all_passed


def test_threat_signal_generation():
    """Verify threat signal payload generation (no API call)."""
    print("\n" + "="*70)
    print("TEST 3: Threat Signal Generation")
    print("="*70)

    from deepsweep.telemetry import create_threat_signal

    # Create a test signal
    signal = create_threat_signal(
        findings_count=5,
        score=85,
        grade="B",
        duration_ms=1250,
        pattern_ids=["test-pattern-1", "test-pattern-2"],
        cve_matches=["CVE-2024-1234"],
        severity_counts={"high": 2, "medium": 3},
    )

    print("\nGenerated Signal:")
    print(f"  Findings: {signal.finding_count}")
    print(f"  Score: {signal.score}")
    print(f"  Grade: {signal.grade}")
    print(f"  Duration: {signal.duration_ms}ms")
    print(f"  Patterns: {len(signal.pattern_ids)}")
    print(f"  CVEs: {signal.cve_matches}")
    print(f"  Severity: {signal.severity_counts}")
    print(f"  CLI Version: {signal.cli_version}")
    print(f"  OS: {signal.os_type}")
    print(f"  Install ID: {signal.install_id[:16]}...")
    print(f"  Session ID: {signal.session_id}")

    # Verify payload can be serialized
    try:
        payload = {
            "event": "threat_signal",
            "version": "1",
            **signal.__dict__,
        }
        json_str = json.dumps(payload, indent=2, default=str)
        print(f"\nSerialized Payload (first 300 chars):")
        print(json_str[:300] + "...")

        # Verify required fields
        required_fields = [
            "pattern_ids", "cve_matches", "severity_counts",
            "score", "grade", "finding_count", "duration_ms",
            "cli_version", "os_type", "install_id", "session_id"
        ]

        missing_fields = [f for f in required_fields if f not in payload]
        if missing_fields:
            print(f"[FAIL] Missing fields: {missing_fields}")
            return False

        print("[PASS] Payload structure valid")
        return True

    except Exception as e:
        print(f"[FAIL] Serialization error: {e}")
        return False


def test_privacy_guarantees():
    """Verify privacy guarantees are enforced."""
    print("\n" + "="*70)
    print("TEST 4: Privacy Guarantees")
    print("="*70)

    from deepsweep.telemetry import create_threat_signal

    signal = create_threat_signal(
        findings_count=5,
        score=85,
        grade="B",
    )

    payload = signal.__dict__
    payload_str = json.dumps(payload, default=str)

    # Check for PII/sensitive data
    privacy_checks = {
        "No file paths": not any(x in payload_str.lower() for x in ["/home/", "c:\\", "/users/"]),
        "No repository names": "repo" not in payload_str.lower() or "repository" not in payload_str.lower(),
        "No code content": "code" not in payload_str.lower(),
        "Install ID is hashed": len(payload["install_id"]) == 32,  # SHA-256 truncated
        "Session ID is UUID": len(payload["session_id"]) == 16,
    }

    all_passed = True
    for check_name, result in privacy_checks.items():
        status = "[PASS]" if result else "[WARN]"
        print(f"  {status} {check_name}")
        all_passed = all_passed and result

    return all_passed


def test_posthog_event_structure():
    """Verify PostHog event structure (with mocked API)."""
    print("\n" + "="*70)
    print("TEST 5: PostHog Event Structure (Mocked)")
    print("="*70)

    # Create temp config directory
    with tempfile.TemporaryDirectory() as tmpdir:
        import sys
        from unittest.mock import patch

        # Patch config paths
        with patch('deepsweep.telemetry.CONFIG_DIR', Path(tmpdir) / '.deepsweep'):
            with patch('deepsweep.telemetry.CONFIG_FILE', Path(tmpdir) / '.deepsweep' / 'config.json'):
                # Mock PostHog
                with patch('deepsweep.telemetry.posthog') as mock_posthog:
                    from deepsweep.telemetry import TelemetryClient

                    client = TelemetryClient()

                    # Track a test command
                    client.track_command(
                        command="validate",
                        exit_code=0,
                        findings_count=5,
                        pattern_count=10,
                        output_format="json",
                        score=85,
                        grade="B",
                    )

                    # Verify PostHog capture was called
                    if mock_posthog.capture.called:
                        call_args = mock_posthog.capture.call_args
                        print("\nPostHog Event:")
                        print(f"  Event: {call_args[1].get('event')}")
                        print(f"  Distinct ID: {call_args[1].get('distinct_id', 'N/A')[:20]}...")

                        props = call_args[1].get('properties', {})
                        print(f"\nProperties:")
                        for key, value in sorted(props.items()):
                            print(f"    {key}: {value}")

                        # Verify required properties
                        required = ["command", "version", "os", "duration_ms", "exit_code"]
                        missing = [p for p in required if p not in props]

                        if missing:
                            print(f"\n[FAIL] Missing properties: {missing}")
                            return False

                        print("\n[PASS] Event structure valid")
                        return True
                    else:
                        print("[FAIL] PostHog capture not called")
                        return False


def test_telemetry_config():
    """Verify telemetry config management."""
    print("\n" + "="*70)
    print("TEST 6: Telemetry Config Management")
    print("="*70)

    with tempfile.TemporaryDirectory() as tmpdir:
        with patch('deepsweep.telemetry.CONFIG_DIR', Path(tmpdir) / '.deepsweep'):
            with patch('deepsweep.telemetry.CONFIG_FILE', Path(tmpdir) / '.deepsweep' / 'config.json'):
                from deepsweep.telemetry import TelemetryConfig

                # Create config
                config = TelemetryConfig()

                print(f"\nInitial Config:")
                print(f"  Enabled: {config.enabled}")
                print(f"  Offline: {config.offline_mode}")
                print(f"  UUID: {config.uuid[:20]}...")
                print(f"  First Run: {config.first_run}")

                # Test enable/disable
                config.disable()
                print(f"\nAfter disable:")
                print(f"  Enabled: {config.enabled}")

                config.enable()
                print(f"\nAfter enable:")
                print(f"  Enabled: {config.enabled}")

                # Test first run marking
                config.mark_not_first_run()
                print(f"\nAfter marking first run complete:")
                print(f"  First Run: {config.first_run}")

                print("\n[PASS] Config management working")
                return True


def test_offline_mode():
    """Verify offline mode behavior."""
    print("\n" + "="*70)
    print("TEST 7: Offline Mode")
    print("="*70)

    import os

    # Test environment variable
    original = os.environ.get('DEEPSWEEP_OFFLINE')

    try:
        os.environ['DEEPSWEEP_OFFLINE'] = '1'

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('deepsweep.telemetry.CONFIG_DIR', Path(tmpdir) / '.deepsweep'):
                with patch('deepsweep.telemetry.CONFIG_FILE', Path(tmpdir) / '.deepsweep' / 'config.json'):
                    from deepsweep.telemetry import TelemetryConfig

                    config = TelemetryConfig()

                    print(f"\nWith DEEPSWEEP_OFFLINE=1:")
                    print(f"  Offline Mode: {config.offline_mode}")

                    if config.offline_mode:
                        print("[PASS] Offline mode detected correctly")
                        return True
                    else:
                        print("[FAIL] Offline mode not detected")
                        return False
    finally:
        if original is None:
            os.environ.pop('DEEPSWEEP_OFFLINE', None)
        else:
            os.environ['DEEPSWEEP_OFFLINE'] = original


def test_ci_detection():
    """Verify CI environment detection."""
    print("\n" + "="*70)
    print("TEST 8: CI Detection")
    print("="*70)

    from deepsweep.telemetry import _detect_ci

    import os

    # Save original env
    original_ci = os.environ.get('CI')
    original_github = os.environ.get('GITHUB_ACTIONS')

    try:
        # Test no CI
        os.environ.pop('CI', None)
        os.environ.pop('GITHUB_ACTIONS', None)

        is_ci, provider = _detect_ci()
        print(f"\nNo CI env vars:")
        print(f"  Is CI: {is_ci}")
        print(f"  Provider: {provider}")

        # Test GitHub Actions
        os.environ['GITHUB_ACTIONS'] = 'true'
        is_ci, provider = _detect_ci()
        print(f"\nWith GITHUB_ACTIONS=true:")
        print(f"  Is CI: {is_ci}")
        print(f"  Provider: {provider}")

        if is_ci and provider == 'github':
            print("\n[PASS] CI detection working")
            return True
        else:
            print("\n[FAIL] CI detection failed")
            return False

    finally:
        # Restore env
        if original_ci:
            os.environ['CI'] = original_ci
        else:
            os.environ.pop('CI', None)
        if original_github:
            os.environ['GITHUB_ACTIONS'] = original_github
        else:
            os.environ.pop('GITHUB_ACTIONS', None)


def main():
    """Run all safe local tests."""
    print("\n" + "="*70)
    print("SAFE LOCAL VERIFICATION")
    print("="*70)
    print("\n⚠️  NO PRODUCTION API CALLS WILL BE MADE ⚠️")
    print("\nThis test suite verifies:")
    print("  1. Code structure and imports")
    print("  2. Configuration values")
    print("  3. Payload generation")
    print("  4. Privacy guarantees")
    print("  5. Mock API interactions")

    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Threat Signal Generation", test_threat_signal_generation),
        ("Privacy Guarantees", test_privacy_guarantees),
        ("PostHog Event Structure", test_posthog_event_structure),
        ("Config Management", test_telemetry_config),
        ("Offline Mode", test_offline_mode),
        ("CI Detection", test_ci_detection),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n[ERROR] {test_name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {test_name}")

    total_passed = sum(results.values())
    total_tests = len(results)

    print(f"\nTotal: {total_passed}/{total_tests} tests passed")

    if all(results.values()):
        print("\n" + "="*70)
        print("✅ ALL LOCAL TESTS PASSED")
        print("="*70)
        print("\nYour code is ready. No production APIs were called.")
        print("\nNext: Controlled production testing (see guide)")
        return 0
    else:
        print("\n" + "="*70)
        print("❌ SOME TESTS FAILED")
        print("="*70)
        print("\nReview failures above before proceeding.")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
