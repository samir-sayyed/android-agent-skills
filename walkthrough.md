# Android Automation Skill - Walkthrough

## What Was Built

A complete **Android Automation Skill** for AI-driven mobile testing and automation, inspired by the iOS simulator skill and mobile-mcp.

## Skill Structure

```
android-skills/
├── SKILL.md                # Main skill documentation
├── resources/
│   └── common.py           # Shared ADB utilities
├── scripts/
│   ├── device/             # 4 scripts
│   ├── app/                # 5 scripts
│   ├── interaction/        # 4 scripts
│   ├── input/              # 3 scripts
│   └── testing/            # 4 scripts
└── examples/               # 3 workflow examples
```

**Total: 20 Python/Shell scripts + 1 shared utility**

---

## Scripts by Category

### Device Management (4)
| Script | Purpose |
|--------|---------|
| [list_devices.sh](file:///Users/samirsayyed/Desktop/android-skills/scripts/device/list_devices.sh) | List connected devices/emulators |
| [emulator_boot.py](file:///Users/samirsayyed/Desktop/android-skills/scripts/device/emulator_boot.py) | Boot emulator (supports headless) |
| [emulator_shutdown.py](file:///Users/samirsayyed/Desktop/android-skills/scripts/device/emulator_shutdown.py) | Shutdown emulator |
| [device_info.py](file:///Users/samirsayyed/Desktop/android-skills/scripts/device/device_info.py) | Get device properties |

### App Management (5)
| Script | Purpose |
|--------|---------|
| [app_install.py](file:///Users/samirsayyed/Desktop/android-skills/scripts/app/app_install.py) | Install APK |
| [app_uninstall.py](file:///Users/samirsayyed/Desktop/android-skills/scripts/app/app_uninstall.py) | Uninstall app |
| [app_launch.py](file:///Users/samirsayyed/Desktop/android-skills/scripts/app/app_launch.py) | Launch app |
| [app_stop.py](file:///Users/samirsayyed/Desktop/android-skills/scripts/app/app_stop.py) | Force stop app |
| [app_list.py](file:///Users/samirsayyed/Desktop/android-skills/scripts/app/app_list.py) | List installed apps |

### Screen Interaction (4)
| Script | Purpose |
|--------|---------|
| [screenshot.py](file:///Users/samirsayyed/Desktop/android-skills/scripts/interaction/screenshot.py) | Capture screenshot |
| [screen_mapper.py](file:///Users/samirsayyed/Desktop/android-skills/scripts/interaction/screen_mapper.py) | Analyze UI hierarchy |
| [navigator.py](file:///Users/samirsayyed/Desktop/android-skills/scripts/interaction/navigator.py) | **Semantic element finder** - find by text/ID/type |
| [gesture.py](file:///Users/samirsayyed/Desktop/android-skills/scripts/interaction/gesture.py) | Swipe, scroll, tap gestures |

### Input & Navigation (3)
| Script | Purpose |
|--------|---------|
| [keyboard.py](file:///Users/samirsayyed/Desktop/android-skills/scripts/input/keyboard.py) | Type text |
| [button.py](file:///Users/samirsayyed/Desktop/android-skills/scripts/input/button.py) | Hardware buttons (HOME, BACK, etc.) |
| [open_url.py](file:///Users/samirsayyed/Desktop/android-skills/scripts/input/open_url.py) | Open URL in browser |

### Testing & Analysis (4)
| Script | Purpose |
|--------|---------|
| [accessibility_audit.py](file:///Users/samirsayyed/Desktop/android-skills/scripts/testing/accessibility_audit.py) | Accessibility compliance check |
| [logcat_monitor.py](file:///Users/samirsayyed/Desktop/android-skills/scripts/testing/logcat_monitor.py) | Log monitoring with filters |
| [app_state.py](file:///Users/samirsayyed/Desktop/android-skills/scripts/testing/app_state.py) | Debug state capture |
| [visual_diff.py](file:///Users/samirsayyed/Desktop/android-skills/scripts/testing/visual_diff.py) | Visual regression testing |

---

## Key Features

✅ **Semantic Navigation** - Find elements by text, ID, or class instead of coordinates  
✅ **JSON Output** - All scripts output structured JSON for AI parsing  
✅ **Token Efficient** - Skills don't load context like MCPs  
✅ **CI/CD Ready** - Exit codes and batch operations  
✅ **Cross-Device** - Works with emulators and real devices via ADB  

---

## Quick Start

```bash
# Prerequisites: ADB in PATH
brew install android-platform-tools

# Check device
./scripts/device/list_devices.sh

# Launch app
python scripts/app/app_launch.py --package com.android.settings

# Map screen
python scripts/interaction/screen_mapper.py --clickable

# Tap by text
python scripts/interaction/navigator.py --find-text "Wi-Fi" --tap
```

---

## Examples Included

1. [login_flow.md](file:///Users/samirsayyed/Desktop/android-skills/examples/login_flow.md) - Login form testing
2. [ui_testing.md](file:///Users/samirsayyed/Desktop/android-skills/examples/ui_testing.md) - Navigation and gestures
3. [ci_cd_workflow.md](file:///Users/samirsayyed/Desktop/android-skills/examples/ci_cd_workflow.md) - GitHub Actions integration

---

## How AI Agents Use This Skill

When you give a command like:

> "Open Settings and navigate to Wi-Fi"

The AI agent:
1. Reads [SKILL.md](file:///Users/samirsayyed/Desktop/android-skills/SKILL.md)
2. Uses `app_launch.py` with `com.android.settings`
3. Uses `screen_mapper.py` to find elements
4. Uses `navigator.py --find-text "Wi-Fi" --tap`
