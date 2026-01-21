# UI Testing Example

This example demonstrates how to perform comprehensive UI testing using the Android automation skill.

## Scenario

Test various UI interactions including navigation, scrolling, and gestures.

## Navigation Testing

```bash
# Open Settings app
python scripts/app/app_launch.py --package com.android.settings

# Find and tap "Network & internet"
python scripts/interaction/navigator.py --find-text "Network" --tap

# Go back
python scripts/input/button.py --key BACK

# Find "Connected devices"
python scripts/interaction/navigator.py --find-text "Connected" --tap

# Go home
python scripts/input/button.py --key HOME
```

## Scroll Testing

```bash
# Launch an app with scrollable content
python scripts/app/app_launch.py --package com.android.settings

# Scroll down to find more options
python scripts/interaction/gesture.py --scroll down --count 3

# Check what's on screen now
python scripts/interaction/screen_mapper.py --clickable

# Scroll back up
python scripts/interaction/gesture.py --scroll up --count 3
```

## Gesture Testing

```bash
# Swipe gestures
python scripts/interaction/gesture.py --swipe left
python scripts/interaction/gesture.py --swipe right

# Tap at specific coordinates
python scripts/interaction/gesture.py --tap 500 800

# Long press
python scripts/interaction/gesture.py --long-press 500 800 --duration 1000

# Double tap
python scripts/interaction/gesture.py --double-tap 500 800
```

## Visual Regression Test

```bash
# Capture baseline
python scripts/interaction/screenshot.py --output baseline.png

# Make changes or navigate...
python scripts/interaction/gesture.py --swipe left

# Capture current state
python scripts/interaction/screenshot.py --output current.png

# Compare
python scripts/testing/visual_diff.py baseline.png current.png --output diff.png
```

## Full Screen Analysis

```bash
# Get all elements with details
python scripts/interaction/screen_mapper.py --format tree

# Get only clickable elements
python scripts/interaction/screen_mapper.py --clickable --format tree
```
