# 🤖 Android Automation Skill

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Android-green.svg)](https://developer.android.com/)

A comprehensive Python-based automation toolkit for Android devices. Enables AI agents and automation scripts to interact with Android apps through ADB, supporting both emulators and real devices.

**Perfect for:** UI testing, automated workflows, accessibility auditing, CI/CD pipelines, and AI-driven mobile automation.

---

## ✨ Features

- 🎯 **Semantic Navigation** - Find UI elements by text, ID, or class instead of fragile coordinates
- 📱 **Universal Compatibility** - Works with emulators and real devices (Android 5.0+)
- 🔄 **JSON Output** - All scripts return structured JSON for easy parsing
- 🤖 **AI-Ready** - Designed for integration with AI agents and LLMs
- 🧪 **Testing Tools** - Accessibility audits, visual regression, and log monitoring
- ⚡ **CI/CD Ready** - Exit codes and headless emulator support

---

## 📦 Installation

### Prerequisites

1. **Python 3.8+**
   ```bash
   python3 --version
   ```

2. **Android SDK Platform Tools (ADB)**
   ```bash
   # macOS
   brew install android-platform-tools

   # Linux
   sudo apt install android-tools-adb

   # Windows
   # Download from: https://developer.android.com/tools/releases/platform-tools
   ```

3. **Verify ADB is in PATH**
   ```bash
   adb version
   ```

### Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/android-automation-skill.git
cd android-automation-skill
```

### Optional Dependencies

For visual regression testing:
```bash
pip install Pillow
```

---

## 🚀 Quick Start

### 1. Connect Your Device

```bash
# List connected devices
./scripts/device/list_devices.sh

# Expected output:
# {
#   "success": true,
#   "data": {
#     "devices": [{"udid": "emulator-5554", "state": "device", ...}]
#   }
# }
```

### 2. Launch an App

```bash
python3 scripts/app/app_launch.py --package com.android.settings
```

### 3. Interact with UI

```bash
# Map screen elements
python3 scripts/interaction/screen_mapper.py --clickable

# Tap an element by text
python3 scripts/interaction/navigator.py --find-text "Wi-Fi" --tap

# Take a screenshot
python3 scripts/interaction/screenshot.py --output screenshot.png
```

---

## 📁 Project Structure

```
android-automation-skill/
├── SKILL.md                    # AI agent instructions
├── README.md                   # This file
├── resources/
│   └── common.py               # Shared utilities
├── scripts/
│   ├── device/                 # Device management
│   │   ├── list_devices.sh
│   │   ├── emulator_boot.py
│   │   ├── emulator_shutdown.py
│   │   └── device_info.py
│   ├── app/                    # App management
│   │   ├── app_install.py
│   │   ├── app_uninstall.py
│   │   ├── app_launch.py
│   │   ├── app_stop.py
│   │   └── app_list.py
│   ├── interaction/            # Screen interaction
│   │   ├── screenshot.py
│   │   ├── screen_mapper.py
│   │   ├── navigator.py
│   │   └── gesture.py
│   ├── input/                  # Input simulation
│   │   ├── keyboard.py
│   │   ├── button.py
│   │   └── open_url.py
│   └── testing/                # Testing & analysis
│       ├── accessibility_audit.py
│       ├── logcat_monitor.py
│       ├── app_state.py
│       └── visual_diff.py
└── examples/                   # Usage examples
    ├── login_flow.md
    ├── ui_testing.md
    └── ci_cd_workflow.md
```

---

## 📖 Script Reference

### Device Management

| Script | Description | Example |
|--------|-------------|---------|
| `list_devices.sh` | List connected devices | `./scripts/device/list_devices.sh` |
| `emulator_boot.py` | Start emulator | `python3 scripts/device/emulator_boot.py --avd Pixel_6` |
| `emulator_shutdown.py` | Stop emulator | `python3 scripts/device/emulator_shutdown.py --all` |
| `device_info.py` | Get device details | `python3 scripts/device/device_info.py` |

### App Management

| Script | Description | Example |
|--------|-------------|---------|
| `app_install.py` | Install APK | `python3 scripts/app/app_install.py --apk app.apk` |
| `app_uninstall.py` | Uninstall app | `python3 scripts/app/app_uninstall.py --package com.example` |
| `app_launch.py` | Launch app | `python3 scripts/app/app_launch.py --package com.example` |
| `app_stop.py` | Force stop app | `python3 scripts/app/app_stop.py --package com.example` |
| `app_list.py` | List installed apps | `python3 scripts/app/app_list.py --filter user` |

### Screen Interaction

| Script | Description | Example |
|--------|-------------|---------|
| `screenshot.py` | Capture screenshot | `python3 scripts/interaction/screenshot.py -o screen.png` |
| `screen_mapper.py` | Analyze UI hierarchy | `python3 scripts/interaction/screen_mapper.py --clickable` |
| `navigator.py` | Find & interact with elements | `python3 scripts/interaction/navigator.py --find-text "Login" --tap` |
| `gesture.py` | Swipes, taps, scrolls | `python3 scripts/interaction/gesture.py --scroll down` |

### Input Simulation

| Script | Description | Example |
|--------|-------------|---------|
| `keyboard.py` | Type text | `python3 scripts/input/keyboard.py --text "Hello"` |
| `button.py` | Press hardware buttons | `python3 scripts/input/button.py --key BACK` |
| `open_url.py` | Open URL in browser | `python3 scripts/input/open_url.py --url "https://example.com"` |

### Testing & Analysis

| Script | Description | Example |
|--------|-------------|---------|
| `accessibility_audit.py` | Check accessibility issues | `python3 scripts/testing/accessibility_audit.py` |
| `logcat_monitor.py` | Monitor logs | `python3 scripts/testing/logcat_monitor.py --package com.example` |
| `app_state.py` | Capture debug state | `python3 scripts/testing/app_state.py -o debug/` |
| `visual_diff.py` | Compare screenshots | `python3 scripts/testing/visual_diff.py base.png current.png` |

---

## 🔧 Common Options

All scripts support these common options:

| Option | Description |
|--------|-------------|
| `--udid`, `-d` | Target specific device by UDID |
| `--format`, `-f` | Output format: `json` (default) or `text` |
| `--help`, `-h` | Show help message |

---

## 🧪 Example: Automated Login Test

```bash
#!/bin/bash

# Launch app
python3 scripts/app/app_launch.py --package com.example.myapp --clear

# Wait for app to load
sleep 2

# Enter username
python3 scripts/interaction/navigator.py \
  --find-id "username_field" \
  --enter-text "testuser@example.com"

# Enter password
python3 scripts/interaction/navigator.py \
  --find-id "password_field" \
  --enter-text "SecurePass123!"

# Tap login button
python3 scripts/interaction/navigator.py \
  --find-text "Login" \
  --tap

# Verify success
sleep 3
python3 scripts/interaction/screenshot.py --output login_result.png
```

---

## 🤖 AI Agent Integration

This skill is designed for AI agents. The `SKILL.md` file contains instructions for AI systems to understand and use the automation scripts.

### Example AI Workflow

When an AI agent receives a command like:
> "Open Settings and turn on Wi-Fi"

The agent can:
1. Read `SKILL.md` for available scripts
2. Execute `app_launch.py` with `com.android.settings`
3. Use `screen_mapper.py` to find UI elements
4. Use `navigator.py` to tap on "Wi-Fi"
5. Use `navigator.py` to toggle the switch

---

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Android UI Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 34
          script: |
            python3 scripts/app/app_install.py --apk app.apk
            python3 scripts/app/app_launch.py --package com.example
            python3 scripts/testing/accessibility_audit.py
```

---

## 🛠️ Troubleshooting

### Device Not Detected

```bash
# Check USB debugging is enabled
adb devices

# Restart ADB server
adb kill-server && adb start-server
```

### Permission Denied on Android 11+

The scripts automatically handle scoped storage restrictions by using `/data/local/tmp` instead of `/sdcard`.

### Element Not Found

1. Use `screen_mapper.py` to see available elements
2. Try different selectors: `--find-text`, `--find-id`, `--find-desc`
3. Add delays for dynamic content: `sleep 2`

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Inspired by [mobile-mcp](https://github.com/anthropics/mobile-mcp)
- Built with Android Debug Bridge (ADB)
- Designed for AI-driven automation

---

## 📬 Contact

Your Name - [@your_twitter](https://twitter.com/your_twitter)

Project Link: [https://github.com/YOUR_USERNAME/android-automation-skill](https://github.com/YOUR_USERNAME/android-automation-skill)
