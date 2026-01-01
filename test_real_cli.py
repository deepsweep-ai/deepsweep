#!/usr/bin/env python3
"""
Test real CLI execution to verify telemetry integration.

This creates a test project and runs actual deepsweep commands.
"""

import subprocess
import tempfile
import json
from pathlib import Path
import time


def create_test_project():
    """Create a simple test project."""
    tmpdir = Path(tempfile.mkdtemp(prefix="deepsweep-test-"))

    # Create a simple Python file with no issues
    (tmpdir / "clean.py").write_text("""
def hello():
    '''A clean function'''
    print("Hello, World!")

if __name__ == "__main__":
    hello()
""")

    # Create a file with a potential issue (for testing)
    (tmpdir / "config.json").write_text("""{
  "api_key": "test-key-12345",
  "endpoint": "https://api.example.com"
}
""")

    return tmpdir


def test_cli_validate():
    """Test running deepsweep validate."""
    print("\n" + "="*70)
    print("TEST: DeepSweep CLI Validate Command")
    print("="*70)

    test_dir = create_test_project()
    print(f"\nCreated test project: {test_dir}")
    print("\nProject contents:")
    for f in test_dir.iterdir():
        print(f"  - {f.name}")

    try:
        # Run deepsweep validate
        print(f"\nRunning: deepsweep validate {test_dir}")
        print("-" * 70)

        result = subprocess.run(
            ["deepsweep", "validate", str(test_dir), "--format", "json"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        print(f"\nExit Code: {result.returncode}")

        # Parse JSON output
        if result.stdout:
            try:
                output = json.loads(result.stdout)
                print(f"\nValidation Results:")
                print(f"  Score: {output.get('score', 'N/A')}/100")
                print(f"  Grade: {output.get('grade', 'N/A')}")
                print(f"  Findings: {len(output.get('findings', []))}")
                print(f"  Files Scanned: {len(output.get('files', []))}")

                print(f"\nJSON Output (first 500 chars):")
                print(json.dumps(output, indent=2)[:500] + "...")

            except json.JSONDecodeError:
                print(f"\nStdout (not JSON):")
                print(result.stdout[:500])
        else:
            print("\n(No stdout)")

        if result.stderr:
            print(f"\nStderr:")
            print(result.stderr[:500])

        print("\n" + "-" * 70)
        print("\nTelemetry Events That Should Have Been Sent:")
        print("\n1. PostHog Event:")
        print("   - Event: deepsweep_validate")
        print("   - Properties: findings_count, score, grade, etc.")
        print("\n2. Threat Intelligence Signal:")
        print("   - Endpoint: api.deepsweep.ai/v1/signal")
        print("   - Pattern effectiveness data")

        print("\n" + "="*70)

        return result.returncode == 0

    finally:
        # Cleanup
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)
        print(f"\nCleaned up test project: {test_dir}")


def test_cli_telemetry_status():
    """Test telemetry status command."""
    print("\n" + "="*70)
    print("TEST: Telemetry Status Command")
    print("="*70)

    result = subprocess.run(
        ["deepsweep", "telemetry", "status"],
        capture_output=True,
        text=True,
        timeout=10,
    )

    print(f"\nOutput:")
    print(result.stdout)

    if result.stderr:
        print(f"\nStderr:")
        print(result.stderr)

    return result.returncode == 0


def test_config_file():
    """Check the telemetry config file."""
    print("\n" + "="*70)
    print("TEST: Telemetry Config File")
    print("="*70)

    config_file = Path.home() / ".deepsweep" / "config.json"

    if config_file.exists():
        print(f"\nConfig file: {config_file}")
        config = json.loads(config_file.read_text())
        print(f"\nConfiguration:")
        print(json.dumps(config, indent=2))

        print(f"\nAnalysis:")
        print(f"  UUID: {config.get('uuid', 'N/A')[:20]}...")
        print(f"  Telemetry Enabled: {config.get('telemetry_enabled', 'N/A')}")
        print(f"  Offline Mode: {config.get('offline_mode', 'N/A')}")
        print(f"  First Run: {config.get('first_run', 'N/A')}")

        return True
    else:
        print(f"\nConfig file not found: {config_file}")
        print("(Will be created on first CLI run)")
        return False


def main():
    """Run all CLI tests."""
    print("\n" + "="*70)
    print("DeepSweep CLI Integration Test")
    print("="*70)
    print("\nThis tests the actual CLI to verify telemetry integration.")

    tests = [
        ("Config File", test_config_file),
        ("Telemetry Status", test_cli_telemetry_status),
        ("CLI Validate", test_cli_validate),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
            time.sleep(0.5)
        except Exception as e:
            print(f"\n[ERROR] {test_name} failed: {e}")
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

    print("\n" + "="*70)
    print("Network Status")
    print("="*70)
    print("\nNote: Telemetry events are sent asynchronously in the background.")
    print("Events may not reach endpoints due to sandbox network restrictions,")
    print("but this is expected and will work in production environments.")

    print("\n" + "="*70)
    print("What to Check in Production")
    print("="*70)
    print("\n1. PostHog Dashboard:")
    print("   https://us.i.posthog.com/project/265866/events")
    print("   - Look for 'deepsweep_validate' events")
    print("   - Verify properties are populated")
    print("\n2. Backend API Logs:")
    print("   - Check for POST to /v1/signal")
    print("   - Verify 200 OK responses")


if __name__ == "__main__":
    main()
