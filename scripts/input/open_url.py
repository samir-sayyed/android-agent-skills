#!/usr/bin/env python3
"""
Open URL on Android device.
Usage:
  python open_url.py --url "https://example.com"
  python open_url.py --url "https://play.google.com/store/apps/details?id=com.example"
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources'))
from common import (
    output_json, output_error, get_device_udid,
    run_shell_command, ADBError
)


def open_url(url: str, udid: str = None, browser: str = None) -> dict:
    """
    Open URL in browser.
    
    Args:
        url: URL to open
        udid: Target device UDID
        browser: Optional specific browser package
    
    Returns:
        Result dict
    """
    try:
        udid = get_device_udid(udid)
    except ADBError as e:
        return {'opened': False, 'error': str(e)}
    
    # Build intent command
    cmd = f'am start -a android.intent.action.VIEW -d "{url}"'
    
    if browser:
        cmd += f' -n {browser}'
    
    try:
        result = run_shell_command(cmd, udid=udid)
        
        if 'Error' in result.stdout:
            return {
                'opened': False,
                'error': result.stdout.strip()
            }
        
        return {
            'opened': True,
            'url': url,
            'browser': browser or 'default'
        }
    except ADBError as e:
        return {'opened': False, 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(description='Open URL on Android device')
    parser.add_argument('--url', '-u', required=True, help='URL to open')
    parser.add_argument('--browser', '-b', help='Specific browser package (optional)')
    parser.add_argument('--udid', '-d', help='Target device UDID')
    parser.add_argument('--format', '-f', choices=['json', 'text'], default='json')
    
    args = parser.parse_args()
    
    result = open_url(args.url, args.udid, args.browser)
    
    if args.format == 'json':
        output_json(result, success=result.get('opened', False))
    else:
        if result.get('opened'):
            print(f"✓ Opened: {result['url']}")
        else:
            print(f"✗ Failed to open URL: {result.get('error', 'Unknown error')}")
            sys.exit(1)


if __name__ == '__main__':
    main()
