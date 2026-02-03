#!/usr/bin/env python3
"""
Type text and send key events on Android device.
Usage:
  python keyboard.py --text "Hello World"
  python keyboard.py --text "user@example.com" --submit
  python keyboard.py --clear
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources'))
from common import (
    output_json, output_error, get_device_udid,
    input_text, press_key, run_shell_command, ADBError
)


def type_text(text: str, udid: str = None, submit: bool = False, 
              clear_first: bool = False) -> dict:
    """
    Type text into focused field.
    
    Args:
        text: Text to type
        udid: Target device UDID
        submit: Press Enter after typing
        clear_first: Clear field before typing
    
    Returns:
        Typing result dict
    """
    try:
        udid = get_device_udid(udid)
    except ADBError as e:
        return {'typed': False, 'error': str(e)}
    
    try:
        actions = []
        
        # Clear existing text if requested
        if clear_first:
            # Select all and delete
            run_shell_command('input keyevent KEYCODE_CTRL_A', udid=udid, check=False)
            run_shell_command('input keyevent KEYCODE_DEL', udid=udid, check=False)
            actions.append('clear')
        
        # Type the text
        input_text(text, udid=udid)
        actions.append(f'typed: "{text}"')
        
        # Submit if requested
        if submit:
            press_key('ENTER', udid=udid)
            actions.append('submit')
        
        return {
            'typed': True,
            'text': text,
            'actions': actions
        }
    except ADBError as e:
        return {'typed': False, 'error': str(e)}


def clear_text(udid: str = None) -> dict:
    """Clear text in focused field."""
    try:
        udid = get_device_udid(udid)
        run_shell_command('input keyevent KEYCODE_CTRL_A', udid=udid, check=False)
        run_shell_command('input keyevent KEYCODE_DEL', udid=udid, check=False)
        return {'cleared': True}
    except ADBError as e:
        return {'cleared': False, 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(description='Type text on Android device')
    parser.add_argument('--text', '-t', help='Text to type')
    parser.add_argument('--submit', '-s', action='store_true', help='Press Enter after typing')
    parser.add_argument('--clear', action='store_true', help='Clear focused field first')
    parser.add_argument('--clear-only', action='store_true', help='Only clear the field')
    parser.add_argument('--udid', '-d', help='Target device UDID')
    parser.add_argument('--format', '-f', choices=['json', 'text'], default='json')
    
    args = parser.parse_args()
    
    if args.clear_only:
        result = clear_text(args.udid)
        if args.format == 'json':
            output_json(result, success=result.get('cleared', False))
        else:
            print('✓ Field cleared' if result.get('cleared') else f"✗ {result.get('error')}")
        return
    
    if not args.text:
        parser.error('--text is required unless --clear-only is specified')
    
    result = type_text(
        text=args.text,
        udid=args.udid,
        submit=args.submit,
        clear_first=args.clear
    )
    
    if args.format == 'json':
        output_json(result, success=result.get('typed', False))
    else:
        if result.get('typed'):
            print(f"✓ Typed: {result['text']}")
            if args.submit:
                print('  + Submitted')
        else:
            print(f"✗ Typing failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)


if __name__ == '__main__':
    main()
