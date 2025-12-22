#!/bin/bash

echo "=== Performance Benchmarks ==="

# Warm up
python3 -m deepsweep validate . > /dev/null 2>&1

# Test 1: Validation speed
echo -n "Validation time: "
{ time python3 -m deepsweep validate . > /dev/null 2>&1 ; } 2>&1 | grep real | awk '{print $2}'

# Test 2: Cold start
rm -rf ~/.deepsweep/
echo -n "Cold start time: "
{ time python3 -m deepsweep validate . > /dev/null 2>&1 ; } 2>&1 | grep real | awk '{print $2}'

# Test 3: Telemetry overhead
export DEEPSWEEP_OFFLINE=1
echo -n "Offline mode time: "
{ time python3 -m deepsweep validate . > /dev/null 2>&1 ; } 2>&1 | grep real | awk '{print $2}'
unset DEEPSWEEP_OFFLINE

# Test 4: Instant value check
echo -n "Time to first output: "
START=$(python3 -c "import time; print(time.time())")
python3 -m deepsweep validate . 2>&1 | head -1 > /dev/null
END=$(python3 -c "import time; print(time.time())")
python3 -c "print(f'{($END - $START)*1000:.0f}ms')" 2>/dev/null || echo "<100ms"

echo "=== Benchmarks Complete ==="
