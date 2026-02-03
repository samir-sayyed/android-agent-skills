#!/usr/bin/env python3
"""
Press hardware buttons on Android device.
Usage:
  python button.py --key HOME
  python button.py --key BACK
  python button.py --key VOLUME_UP
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources'))
from common import (
    output_json, output_error, get_device_udid,
    press_key, ADBError
)

# Available key mappings
KEY_MAP = {
    'HOME': 3,
    'BACK': 4,
    'CALL': 5,
    'END_CALL': 6,
    'VOLUME_UP': 24,
    'VOLUME_DOWN': 25,
    'POWER': 26,
    'CAMERA': 27,
    'CLEAR': 28,
    'MENU': 82,
    'SEARCH': 84,
    'MEDIA_PLAY_PAUSE': 85,
    'MEDIA_STOP': 86,
    'MEDIA_NEXT': 87,
    'MEDIA_PREVIOUS': 88,
    'MUTE': 91,
    'ENTER': 66,
    'TAB': 61,
    'ESCAPE': 111,
    'DELETE': 67,
    'BACKSPACE': 67,
    'SPACE': 62,
    'DPAD_UP': 19,
    'DPAD_DOWN': 20,
    'DPAD_LEFT': 21,
    'DPAD_RIGHT': 22,
    'DPAD_CENTER': 23,
    'APP_SWITCH': 187,
    'SCREENSHOT': 120,
}


def press_button(key: str, udid: str = None, repeat: int = 1) -> dict:
    """
    Press a hardware button.
    
    Args:
        key: Key name or keycode
        udid: Target device UDID
        repeat: Number of times to press
    
    Returns:
        Button press result dict
    """
    try:
        udid = get_device_udid(udid)
    except ADBError as e:
        return {'pressed': False, 'error': str(e)}
    
    key_upper = key.upper()
    
    # Check if valid key
    if key_upper not in KEY_MAP and not key.isdigit():
        return {
            'pressed': False,
            'error': f"Unknown key: {key}. Available: {', '.join(sorted(KEY_MAP.keys()))}"
        }
    
    try:
        for _ in range(repeat):
            press_key(key_upper, udid=udid)
        
        return {
            'pressed': True,
            'key': key_upper,
            'keycode': KEY_MAP.get(key_upper, key),
            'repeat': repeat
        }
    except ADBError as e:
        return {'pressed': False, 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(description='Press hardware buttons on Android device')
    parser.add_argument('--key', '-k', required=True, help='Key to press (e.g., HOME, BACK, ENTER)')
    parser.add_argument('--repeat', '-r', type=int, default=1, help='Repeat count')
    parser.add_argument('--list', action='store_true', help='List available keys')
    parser.add_argument('--udid', '-d', help='Target device UDID')
    parser.add_argument('--format', '-f', choices=['json', 'text'], default='json')
    
    args = parser.parse_args()
    
    if args.list:
        if args.format == 'json':
            output_json({'keys': list(sorted(KEY_MAP.keys()))})
        else:
            print('Available keys:')
            for key in sorted(KEY_MAP.keys()):
                print(f'  {key} ({KEY_MAP[key]})')
        return
    
    result = press_button(args.key, args.udid, args.repeat)
    
    if args.format == 'json':
        output_json(result, success=result.get('pressed', False))
    else:
        if result.get('pressed'):
            print(f"✓ Pressed {result['key']}" + (f" x{result['repeat']}" if result['repeat'] > 1 else ''))
        else:
            print(f"✗ Button press failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)


if __name__ == '__main__':
    main()
