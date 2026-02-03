# Android Automation Instructions

When working with Android automation in this project, use the scripts from the android-skills folder.

## Quick Reference

### Find and interact with elements
```bash
python scripts/interaction/navigator.py --find-text "Login" --tap
python scripts/interaction/navigator.py --find-id "submit_button" --tap
```

### Take screenshots
```bash
python scripts/interaction/screenshot.py --output screenshot.png
```

### Map screen elements
```bash
python scripts/interaction/screen_mapper.py --clickable
```

### Launch apps
```bash
python scripts/app/app_launch.py --package com.android.settings
```

### Get device info
```bash
./scripts/device/list_devices.sh
```

## Full Documentation

See [SKILL.md](../../SKILL.md) for all available scripts and detailed usage.
