---
name: Android Automation Skill
description: |
  Use this skill when the user wants to:
  - Control Android devices, emulators, or simulators
  - Perform mobile testing, QA automation, or UI testing on Android
  - Find, tap, scroll, or interact with elements on Android screens
  - Launch, install, uninstall, or manage Android apps
  - Take screenshots, capture logs, or debug Android issues
  - Write or run Appium-like automation without Appium
  - Get element locators, accessibility tree, or UI hierarchy
  - Press hardware buttons like back, home, or volume
  - Type text or enter credentials on Android
  
  This skill provides 20+ ADB-based Python automation scripts.
triggers:
  - android
  - mobile testing
  - adb
  - emulator
  - appium alternative
  - ui automation
  - tap element
  - scroll screen
  - find locator
  - app testing
  - android device
  - mobile app
  - screen mapper
  - accessibility audit
invocation:
  - /android
  - /mobile
  - /adb
---

# Android Automation Skill

Production-ready automation for Android app testing. 20+ scripts optimized for AI agents and human developers.

## Prerequisites

- **Android SDK Platform Tools** (ADB) in PATH
  ```bash
  # macOS
  brew install android-platform-tools
  
  # Verify
  adb version
  ```
- **Python 3.8+**
- Connected Android device or running emulator

## Quick Start

```bash
# Check device connection
./scripts/device/list_devices.sh

# Take screenshot
python scripts/interaction/screenshot.py --output screen.png

# Map current screen
python scripts/interaction/screen_mapper.py

# Tap element by text
python scripts/interaction/navigator.py --find-text "Settings" --tap
```

---

## Scripts Reference

### Device Management

| Script | Description | Usage |
|--------|-------------|-------|
| `list_devices.sh` | List connected devices/emulators | `./scripts/device/list_devices.sh` |
| `emulator_boot.py` | Boot emulator by AVD name | `python scripts/device/emulator_boot.py --avd Pixel_7_API_34` |
| `emulator_shutdown.py` | Shutdown emulator | `python scripts/device/emulator_shutdown.py [--udid <id>]` |
| `device_info.py` | Get device properties | `python scripts/device/device_info.py` |

### App Management

| Script | Description | Usage |
|--------|-------------|-------|
| `app_install.py` | Install APK | `python scripts/app/app_install.py --apk app.apk` |
| `app_uninstall.py` | Uninstall app | `python scripts/app/app_uninstall.py --package com.example.app` |
| `app_launch.py` | Launch app | `python scripts/app/app_launch.py --package com.example.app` |
| `app_stop.py` | Force stop app | `python scripts/app/app_stop.py --package com.example.app` |
| `app_list.py` | List installed apps | `python scripts/app/app_list.py [--filter user]` |

### Screen Interaction

| Script | Description | Usage |
|--------|-------------|-------|
| `screenshot.py` | Capture screenshot | `python scripts/interaction/screenshot.py --output shot.png` |
| `annotated_screenshot.py` | Screenshot with labeled elements | `python scripts/interaction/annotated_screenshot.py --output annotated.png` |
| `screen_mapper.py` | Analyze UI hierarchy | `python scripts/interaction/screen_mapper.py [--format tree]` |
| `navigator.py` | Find/interact with elements | `python scripts/interaction/navigator.py --find-text "Login" --tap` |
| `gesture.py` | Swipe, scroll, pinch | `python scripts/interaction/gesture.py --swipe up` |
| `gesture_record.py` | Record/replay gestures | `python scripts/interaction/gesture_record.py --record gestures.json` |

#### Advanced Navigator Features

The `navigator.py` script supports advanced element finding:

```bash
# Wait for element (useful after navigation/loading)
python scripts/interaction/navigator.py --find-text "Welcome" --wait-timeout 10 --tap

# XPath queries
python scripts/interaction/navigator.py --xpath "//android.widget.Button[@text='Submit']" --tap

# Self-healing with fallbacks (tries primary, then fallbacks)
python scripts/interaction/navigator.py --find-text "Login" --fallback-id "submit_btn" --tap

# Retry on failure
python scripts/interaction/navigator.py --find-id "dynamic_element" --retry-count 3 --tap
```

### Input & Navigation

| Script | Description | Usage |
|--------|-------------|-------|
| `keyboard.py` | Type text | `python scripts/input/keyboard.py --text "Hello World"` |
| `button.py` | Hardware buttons | `python scripts/input/button.py --key HOME` |
| `open_url.py` | Open URL in browser | `python scripts/input/open_url.py --url "https://example.com"` |

### Testing & Analysis

| Script | Description | Usage |
|--------|-------------|-------|
| `accessibility_audit.py` | Check accessibility | `python scripts/testing/accessibility_audit.py` |
| `logcat_monitor.py` | Monitor logs | `python scripts/testing/logcat_monitor.py --package com.example.app` |
| `app_state.py` | Debug snapshot | `python scripts/testing/app_state.py --output state/` |
| `visual_diff.py` | Compare screenshots | `python scripts/testing/visual_diff.py baseline.png current.png` |

---

## How It Works

The AI agent automatically detects when to use this skill based on your request:

```
You: "Launch the Settings app"
AI: [Uses app_launch.py with com.android.settings]

You: "Tap on Wi-Fi"
AI: [Uses navigator.py to find and tap Wi-Fi element]

You: "Scroll down and take a screenshot"
AI: [Uses gesture.py to scroll, then screenshot.py]
```

---

## Usage Examples

### Example 1: Login Flow Testing
```bash
# Launch app
python scripts/app/app_launch.py --package com.example.app

# Map screen to find login fields
python scripts/interaction/screen_mapper.py

# Enter credentials
python scripts/interaction/navigator.py --find-type EditText --index 0 --enter-text "user@test.com"
python scripts/interaction/navigator.py --find-type EditText --index 1 --enter-text "password"

# Tap login button
python scripts/interaction/navigator.py --find-text "Login" --tap

# Check accessibility
python scripts/testing/accessibility_audit.py
```

### Example 2: Visual Regression Testing
```bash
# Capture baseline
python scripts/interaction/screenshot.py --output baseline.png

# Make changes and capture current
python scripts/interaction/screenshot.py --output current.png

# Compare
python scripts/testing/visual_diff.py baseline.png current.png
```

### Example 3: CI/CD Pipeline
```bash
# Boot emulator
python scripts/device/emulator_boot.py --avd CI_Emulator --headless

# Install APK
python scripts/app/app_install.py --apk app-debug.apk

# Run automated tests
python scripts/app/app_launch.py --package com.example.app
python scripts/interaction/navigator.py --find-text "Start" --tap

# Capture logs
python scripts/testing/logcat_monitor.py --package com.example.app --duration 30

# Cleanup
python scripts/device/emulator_shutdown.py
```

---

## Troubleshooting

### Device Not Found
```bash
# Check USB debugging is enabled
adb devices

# Restart ADB server
adb kill-server && adb start-server
```

### Element Not Found
```bash
# Dump full UI hierarchy
python scripts/interaction/screen_mapper.py --verbose

# Use different search strategies
python scripts/interaction/navigator.py --find-id "login_button" --tap
python scripts/interaction/navigator.py --find-class "android.widget.Button" --index 0 --tap
```

### Emulator Won't Boot
```bash
# List available AVDs
emulator -list-avds

# Check for locks
rm -rf ~/.android/avd/*.avd/*.lock
```

---

## Output Format

All scripts output JSON by default for easy parsing:

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

Use `--format text` for human-readable output.
