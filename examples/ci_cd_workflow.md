# CI/CD Workflow Example

This example demonstrates how to use the Android automation skill in CI/CD pipelines.

## GitHub Actions Example

```yaml
name: Android UI Tests

on: [push, pull_request]

jobs:
  ui-tests:
    runs-on: macos-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Android Emulator
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 34
          target: default
          arch: x86_64
          script: |
            # Wait for emulator
            adb wait-for-device
            
            # Install app
            python scripts/app/app_install.py --apk app/build/outputs/apk/debug/app-debug.apk
            
            # Run tests
            python scripts/app/app_launch.py --package com.example.myapp
            
            # Screenshot
            python scripts/interaction/screenshot.py --output test-results/home.png
            
            # Navigate and test
            python scripts/interaction/navigator.py --find-text "Login" --tap
            python scripts/interaction/screenshot.py --output test-results/login.png
            
            # Accessibility audit
            python scripts/testing/accessibility_audit.py > test-results/a11y.json
      
      - name: Upload Test Results
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: test-results/
```

## Shell Script for CI

```bash
#!/bin/bash
set -e

PACKAGE="com.example.myapp"
APK_PATH="app/build/outputs/apk/debug/app-debug.apk"
RESULTS_DIR="test-results"

mkdir -p $RESULTS_DIR

echo "=== Starting CI Tests ==="

# 1. Check device
echo "Checking device..."
./scripts/device/list_devices.sh || exit 1

# 2. Install app
echo "Installing app..."
python scripts/app/app_install.py --apk $APK_PATH --replace

# 3. Launch app
echo "Launching app..."
python scripts/app/app_launch.py --package $PACKAGE --clear

# 4. Wait for load
sleep 5

# 5. Capture initial state
echo "Capturing initial state..."
python scripts/testing/app_state.py \
  --package $PACKAGE \
  --output $RESULTS_DIR/initial_state/

# 6. Run accessibility audit
echo "Running accessibility audit..."
python scripts/testing/accessibility_audit.py > $RESULTS_DIR/accessibility.json

# 7. Capture logs
echo "Capturing logs..."
python scripts/testing/logcat_monitor.py \
  --package $PACKAGE \
  --duration 5 \
  --output $RESULTS_DIR/app.log

# 8. Clean up
echo "Cleaning up..."
python scripts/app/app_stop.py --package $PACKAGE

echo "=== CI Tests Complete ==="
echo "Results saved to: $RESULTS_DIR"
```

## Headless Emulator Testing

```bash
# Boot emulator in headless mode (no GUI)
python scripts/device/emulator_boot.py \
  --avd CI_Emulator \
  --headless \
  --wipe-data

# Run tests...

# Shutdown when done
python scripts/device/emulator_shutdown.py
```

## Exit Codes

All scripts follow standard exit code conventions:
- `0` - Success
- `1` - Failure

Use these for CI/CD pipeline control:

```bash
# Fail pipeline if accessibility audit finds errors
python scripts/testing/accessibility_audit.py --format json
if [ $? -ne 0 ]; then
  echo "Accessibility errors found!"
  exit 1
fi
```
