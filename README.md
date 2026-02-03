# 🤖 Android Automation Skill

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Android-green.svg)](https://developer.android.com/)

A comprehensive Python-based automation toolkit for Android devices. Enables AI agents and automation scripts to interact with Android apps through ADB, supporting both emulators and real devices.

**Perfect for:** UI testing, automated workflows, accessibility auditing, CI/CD pipelines, and AI-driven mobile automation.

---

## 📍 Table of Contents
- [🚀 New Here? Start Here!](#-new-here-start-here)
- [🔌 Compatibility](#-compatibility)
- [✨ Features](#-features)
- [📦 Installation](#-installation)
- [🚀 Quick Start](#-quick-start)
- [📁 Project Structure](#-project-structure)
- [📖 Script Reference](#-script-reference)
- [🤖 AI Agent Integration](#-ai-agent-integration)
- [🔄 CI/CD Integration](#-cicd-integration)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🚀 New Here? Start Here!
**First time using this repository?** This skill is designed to be "dropped in" to your AI coding assistant (Claude Code, Gemini CLI, Cursor, etc.) to give it native Android automation capabilities.

- **[SKILL.md](SKILL.md)** - Understanding how the AI uses this skill
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to add new automation scripts
- **[walkthrough.md](walkthrough.md)** - Detailed automation walkthrough (MDLive Example)

---

## 🔌 Compatibility
This skill follows the universal **SKILL.md** format and works with any AI coding assistant that supports agentic skills:

| Tool                | Type      | Compatibility | Recommended Installation Path            |
| ------------------- | --------- | ------------- | ---------------------------------------- |
| **Claude Code**     | CLI       | ✅ Full       | `.claude/skills/` or `.agent/skills/`    |
| **Gemini CLI**      | CLI       | ✅ Full       | `.gemini/skills/` or `.agent/skills/`    |
| **Codex CLI**       | CLI       | ✅ Full       | `.codex/skills/` or `.agent/skills/`     |
| **Antigravity IDE** | IDE       | ✅ Full       | `.agent/skills/`                         |
| **Cursor**          | IDE       | ✅ Full       | `.cursor/skills/` or project root        |
| **GitHub Copilot**  | Extension | ⚠️ Partial    | Copy skill content to `.github/copilot/` |

> [!TIP]
> Most modern AI tools auto-discover skills in the `.agent/skills/` directory of your project.

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

To use this skill with your AI coding assistant, clone it into your project's skill directory:

### Quick Install (Choose your tool)

```bash
# Navigate to your project
cd your-project

# Universal (works with most tools)
git clone https://github.com/samir-sayyed/android-agent-skills.git .agent/skills/android

# Claude Code
git clone https://github.com/samir-sayyed/android-agent-skills.git .claude/skills/android

# Gemini CLI
git clone https://github.com/samir-sayyed/android-agent-skills.git .gemini/skills/android

# Cursor
git clone https://github.com/samir-sayyed/android-agent-skills.git .cursor/skills/android

# Or as a submodule (for version control)
git submodule add https://github.com/samir-sayyed/android-agent-skills.git .agent/skills/android
```

### Enable Skills in Gemini CLI (if needed)

Add to `~/.gemini/settings.json`:
```json
{
  "experimental": {
    "skills": true
  }
}
```

### 🛠️ Local Setup
If you are running the scripts manually or developing:

1. **ADB:** Install Android Platform Tools
   ```bash
   brew install android-platform-tools
   ```
2. **Python:** 3.8+ required
3. **Pillow:** (Optional) for visual regression
   ```bash
   pip install Pillow
   ```

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

---

## 💡 Inspiration & Credits

This project was inspired by the architectural patterns and concepts developed in:
- **[mobile-mcp](https://github.com/mobile-next/mobile-mcp)** - A Model Context Protocol (MCP) implementation for mobile automation.

Developing this as a standalone **Android Skill** allows for seamless integration with agentic tools like Claude Code and Gemini CLI using standard ADB protocols.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

