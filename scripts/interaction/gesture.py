#!/usr/bin/env python3
"""
Perform gestures on Android device.
Usage:
  python gesture.py --swipe up
  python gesture.py --swipe left --duration 500
  python gesture.py --scroll down --count 3
  python gesture.py --tap 500 800
"""

import argparse
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources'))
from common import (
    output_json, output_error, get_device_udid,
    tap as do_tap, swipe as do_swipe, get_screen_size, ADBError
)


def perform_swipe(
    direction: str,
    udid: str = None,
    duration_ms: int = 300,
    distance_percent: float = 0.5
) -> dict:
    """
    Perform swipe gesture.
    
    Args:
        direction: 'up', 'down', 'left', 'right'
        udid: Target device UDID
        duration_ms: Swipe duration in milliseconds
        distance_percent: Distance as percent of screen dimension
    
    Returns:
        Gesture result dict
    """
    try:
        udid = get_device_udid(udid)
    except ADBError as e:
        return {'performed': False, 'error': str(e)}
    
    try:
        width, height = get_screen_size(udid)
        
        # Calculate swipe coordinates
        center_x = width // 2
        center_y = height // 2
        
        swipe_map = {
            'up': (center_x, int(height * 0.7), center_x, int(height * (0.7 - distance_percent))),
            'down': (center_x, int(height * 0.3), center_x, int(height * (0.3 + distance_percent))),
            'left': (int(width * 0.8), center_y, int(width * (0.8 - distance_percent)), center_y),
            'right': (int(width * 0.2), center_y, int(width * (0.2 + distance_percent)), center_y),
        }
        
        if direction.lower() not in swipe_map:
            return {'performed': False, 'error': f"Invalid direction: {direction}. Use up/down/left/right"}
        
        x1, y1, x2, y2 = swipe_map[direction.lower()]
        do_swipe(x1, y1, x2, y2, duration_ms, udid)
        
        return {
            'performed': True,
            'gesture': 'swipe',
            'direction': direction,
            'from': (x1, y1),
            'to': (x2, y2),
            'duration_ms': duration_ms
        }
    except ADBError as e:
        return {'performed': False, 'error': str(e)}


def perform_scroll(
    direction: str,
    udid: str = None,
    count: int = 1,
    duration_ms: int = 200
) -> dict:
    """
    Perform scroll gesture (multiple small swipes).
    
    Args:
        direction: 'up' or 'down'
        udid: Target device UDID
        count: Number of scroll gestures
        duration_ms: Duration per scroll
    
    Returns:
        Gesture result dict
    """
    results = []
    for i in range(count):
        result = perform_swipe(direction, udid, duration_ms, distance_percent=0.3)
        results.append(result)
        if not result['performed']:
            return result
        time.sleep(0.1)
    
    return {
        'performed': True,
        'gesture': 'scroll',
        'direction': direction,
        'count': count
    }


def perform_tap(x: int, y: int, udid: str = None) -> dict:
    """
    Tap at coordinates.
    
    Args:
        x: X coordinate
        y: Y coordinate
        udid: Target device UDID
    
    Returns:
        Gesture result dict
    """
    try:
        udid = get_device_udid(udid)
    except ADBError as e:
        return {'performed': False, 'error': str(e)}
    
    try:
        do_tap(x, y, udid)
        return {
            'performed': True,
            'gesture': 'tap',
            'coordinates': (x, y)
        }
    except ADBError as e:
        return {'performed': False, 'error': str(e)}


def perform_double_tap(x: int, y: int, udid: str = None) -> dict:
    """Double tap at coordinates."""
    try:
        udid = get_device_udid(udid)
        do_tap(x, y, udid)
        time.sleep(0.05)
        do_tap(x, y, udid)
        return {
            'performed': True,
            'gesture': 'double_tap',
            'coordinates': (x, y)
        }
    except ADBError as e:
        return {'performed': False, 'error': str(e)}


def perform_long_press(x: int, y: int, udid: str = None, duration_ms: int = 1000) -> dict:
    """Long press at coordinates."""
    try:
        udid = get_device_udid(udid)
        do_swipe(x, y, x, y, duration_ms, udid)
        return {
            'performed': True,
            'gesture': 'long_press',
            'coordinates': (x, y),
            'duration_ms': duration_ms
        }
    except ADBError as e:
        return {'performed': False, 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(description='Perform gestures on Android device')
    
    # Gesture types
    parser.add_argument('--swipe', choices=['up', 'down', 'left', 'right'], help='Swipe direction')
    parser.add_argument('--scroll', choices=['up', 'down'], help='Scroll direction')
    parser.add_argument('--tap', nargs=2, type=int, metavar=('X', 'Y'), help='Tap at coordinates')
    parser.add_argument('--double-tap', nargs=2, type=int, metavar=('X', 'Y'), help='Double tap')
    parser.add_argument('--long-press', nargs=2, type=int, metavar=('X', 'Y'), help='Long press')
    
    # Options
    parser.add_argument('--duration', type=int, default=300, help='Gesture duration in ms')
    parser.add_argument('--count', type=int, default=1, help='Repeat count for scroll')
    parser.add_argument('--udid', '-d', help='Target device UDID')
    parser.add_argument('--format', '-f', choices=['json', 'text'], default='json')
    
    args = parser.parse_args()
    
    result = None
    
    if args.swipe:
        result = perform_swipe(args.swipe, args.udid, args.duration)
    elif args.scroll:
        result = perform_scroll(args.scroll, args.udid, args.count, args.duration)
    elif args.tap:
        result = perform_tap(args.tap[0], args.tap[1], args.udid)
    elif args.double_tap:
        result = perform_double_tap(args.double_tap[0], args.double_tap[1], args.udid)
    elif args.long_press:
        result = perform_long_press(args.long_press[0], args.long_press[1], args.udid, args.duration)
    else:
        parser.error('Specify a gesture: --swipe, --scroll, --tap, --double-tap, or --long-press')
    
    if args.format == 'json':
        output_json(result, success=result.get('performed', False))
    else:
        if result.get('performed'):
            gesture = result.get('gesture', 'gesture')
            print(f"✓ Performed {gesture}")
            if 'direction' in result:
                print(f"  Direction: {result['direction']}")
            if 'coordinates' in result:
                print(f"  Coordinates: {result['coordinates']}")
        else:
            print(f"✗ Gesture failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)


if __name__ == '__main__':
    main()
