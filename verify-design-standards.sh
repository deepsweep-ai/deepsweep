#!/bin/bash

echo "============================================================"
echo "MANDATORY DESIGN STANDARDS VERIFICATION"
echo "DeepSweep v1.2.0"
echo "============================================================"
echo ""

# Run Python verification
python3 << 'EOF'
import re
import os

checks_passed = 0
checks_total = 8

# Check 1: NO EMOJIS
print("[1/8] NO EMOJIS anywhere (code, docs, CLI, UI, logs)")
emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF]')
files_to_check = []
for root, dirs, files in os.walk('src'):
    for file in files:
        if file.endswith('.py'):
            files_to_check.append(os.path.join(root, file))
files_to_check.extend(['README.md', 'CHANGELOG.md'])

found_emojis = False
for filepath in files_to_check:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            if emoji_pattern.search(f.read()):
                found_emojis = True
                print(f"      Found emoji in: {filepath}")

if not found_emojis:
    print("      [PASS] No emojis detected")
    checks_passed += 1
else:
    print("      [FAIL] Emojis found - VIOLATION")
print()

# Check 2: ASCII Symbols
print("[2/8] ASCII symbols only: [PASS] [FAIL] [WARN] [INFO]")
with open('src/deepsweep/constants.py', 'r') as f:
    constants = f.read()
required_symbols = ['[PASS]', '[FAIL]', '[WARN]', '[INFO]', '[SKIP]']
all_present = all(sym in constants for sym in required_symbols)
if all_present:
    print(f"      [PASS] All symbols defined: {', '.join(required_symbols)}")
    checks_passed += 1
else:
    print("      [FAIL] Missing symbols")
print()

# Check 3: NO_COLOR support
print("[3/8] NO_COLOR environment variable support")
with open('src/deepsweep/output.py', 'r') as f:
    output_py = f.read()
no_color_ok = 'NO_COLOR' in output_py and 'os.environ.get("NO_COLOR")' in output_py
if no_color_ok:
    print("      [PASS] NO_COLOR support implemented")
    checks_passed += 1
else:
    print("      [FAIL] NO_COLOR not supported")
print()

# Check 4: Optimistic messaging
print("[4/8] Optimistic messaging (Wiz approach)")
optimistic_patterns = [
    ('items to review', 'NOT "vulnerabilities detected"'),
    ('How to address', 'NOT "Fix immediately"'),
    ('Ship with confidence', 'optimistic framing'),
]
violations = []
if 'vulnerabilities detected' in output_py:
    violations.append('Found "vulnerabilities detected"')
if 'Fix immediately' in output_py:
    violations.append('Found "Fix immediately"')

if not violations and 'items to review' in output_py and 'How to address' in output_py:
    print("      [PASS] Optimistic messaging enforced")
    checks_passed += 1
else:
    print(f"      [FAIL] {', '.join(violations) if violations else 'Missing optimistic terms'}")
print()

# Check 5: Vibe coding hooks
print("[5/8] Vibe coding hooks in visible output")
with open('README.md', 'r') as f:
    readme = f.read()
with open('src/deepsweep/cli.py', 'r') as f:
    cli = f.read()

hooks_present = (
    'Ship with vibes. Ship secure.' in readme and
    ('vibe coding' in cli.lower() or 'vibe coding' in readme.lower())
)
if hooks_present:
    print("      [PASS] Vibe coding hooks present")
    print("      - 'Ship with vibes. Ship secure.' ✓")
    print("      - 'vibe coding' references ✓")
    checks_passed += 1
else:
    print("      [FAIL] Missing vibe coding hooks")
print()

# Check 6: Terminology
print("[6/8] Terminology: 'validate' not 'scan'")
violations = []
for root, dirs, files in os.walk('src'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r') as f:
                content = f.read()
                if re.search(r'\.scan\(', content):
                    violations.append(f"{filepath}: .scan() method")
                if 'class Scanner' in content:
                    violations.append(f"{filepath}: Scanner class")

if not violations:
    print("      [PASS] Correct terminology throughout")
    checks_passed += 1
else:
    print(f"      [FAIL] {len(violations)} violations:")
    for v in violations[:3]:
        print(f"      - {v}")
print()

# Check 7: Two-tier telemetry
print("[7/8] Two-tier telemetry system")
two_tier_checks = [
    ('two-tier telemetry' in readme.lower(), 'System documented'),
    ('TIER 1' in readme or 'Essential' in readme, 'Essential tier described'),
    ('TIER 2' in readme or 'Optional' in readme, 'Optional tier described'),
    ('DEEPSWEEP_OFFLINE' in readme, 'Offline mode documented'),
]
two_tier_ok = all(check[0] for check in two_tier_checks)
if two_tier_ok:
    print("      [PASS] Two-tier system fully documented")
    checks_passed += 1
else:
    print("      [FAIL] Incomplete two-tier documentation")
    for check, desc in two_tier_checks:
        print(f"      {'✓' if check else '✗'} {desc}")
print()

# Check 8: Version consistency
print("[8/8] Version 1.2.0 consistency")
version_files = [
    'pyproject.toml',
    'src/deepsweep/__init__.py',
    'src/deepsweep/constants.py',
    'README.md',
    'CHANGELOG.md',
]
version_ok = True
for vfile in version_files:
    if os.path.exists(vfile):
        with open(vfile, 'r') as f:
            if '1.2.0' not in f.read():
                print(f"      [FAIL] Version mismatch in {vfile}")
                version_ok = False

if version_ok:
    print("      [PASS] Version 1.2.0 consistent across all files")
    checks_passed += 1
else:
    print("      [FAIL] Version inconsistency detected")
print()

# Summary
print("=" * 60)
print(f"RESULTS: {checks_passed}/{checks_total} checks passed")
if checks_passed == checks_total:
    print("✓ ALL DESIGN STANDARDS MET - SHIP READY")
else:
    print(f"✗ {checks_total - checks_passed} VIOLATIONS - NEEDS FIXES")
print("=" * 60)

exit(0 if checks_passed == checks_total else 1)
EOF
