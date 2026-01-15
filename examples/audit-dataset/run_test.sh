#!/bin/bash
# AEE Protocol - Integrity Audit Test (Bash)
# This script tests AEE on Linux and macOS systems

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DATASET_PATH="$SCRIPT_DIR/dataset.csv"
EXPECTED_OUTPUT_FILE="$SCRIPT_DIR/expected_output.txt"

echo ""
echo "AEE - Integrity Audit Test"
echo "--------------------------------"
echo "Project root: $PROJECT_ROOT"
echo "Dataset: $(basename $DATASET_PATH)"
echo ""

# Check if dataset exists
if [ ! -f "$DATASET_PATH" ]; then
    echo "ERROR: dataset.csv not found at $DATASET_PATH"
    exit 1
fi

# Run test 1: Generate anchor
echo "STEP 1: Generate Integrity Anchor"
echo "=================================="

GENERATE_OUTPUT=$(cd "$PROJECT_ROOT" && python main.py --hash "$DATASET_PATH" --user "audit-test" 2>&1)
GENERATE_EXIT=$?

if [ $GENERATE_EXIT -ne 0 ]; then
    echo "ERROR: Failed to generate anchor"
    echo "$GENERATE_OUTPUT"
    exit 1
fi

echo "$GENERATE_OUTPUT"
echo ""

# Extract anchor (last non-empty line)
ANCHOR=$(echo "$GENERATE_OUTPUT" | grep -v "^$" | tail -1)

echo "Extracted anchor: $ANCHOR"
echo ""

# Run test 2: Verify anchor
echo "STEP 2: Verify Integrity"
echo "=================================="

VERIFY_OUTPUT=$(cd "$PROJECT_ROOT" && python main.py --verify "$DATASET_PATH" --anchor "$ANCHOR" 2>&1)
VERIFY_EXIT=$?

echo "$VERIFY_OUTPUT"

if [ $VERIFY_EXIT -eq 0 ]; then
    echo "✔ Test finished successfully."
    echo ""
    echo "=================================="
    echo "Test Results: PASSED"
    echo "=================================="
    exit 0
else
    echo "✖ Verification failed!"
    exit 1
fi