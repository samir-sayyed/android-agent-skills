#!/usr/bin/env python3
"""
Force stop Android app.
Usage: python app_stop.py --package com.example.app
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources'))
from common import (
    output_json, output_error, get_device_udid,
    run_shell_command, ADBError
)


def stop_app(package: str, udid: str = None) -> dict:
    """
    Force stop an app.
    
    Args:
        package: Package name to stop
        udid: Target device UDID
    
    Returns:
        Stop result dict
    """
    try:
        udid = get_device_udid(udid)
    except ADBError as e:
        return {'stopped': False, 'error': str(e)}
    
    try:
        run_shell_command(f'am force-stop {package}', udid=udid)
        return {
            'stopped': True,
            'package': package,
            'device': udid
        }
    except ADBError as e:
        return {'stopped': False, 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(description='Force stop Android app')
    parser.add_argument('--package', '-p', required=True, help='Package name')
    parser.add_argument('--udid', '-d', help='Target device UDID')
    parser.add_argument('--format', choices=['json', 'text'], default='json')
    
    args = parser.parse_args()
    
    result = stop_app(args.package, args.udid)
    
    if args.format == 'json':
        output_json(result, success=result['stopped'])
    else:
        if result['stopped']:
            print(f"✓ Stopped {result['package']}")
        else:
            print(f"✗ Stop failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)


if __name__ == '__main__':
    main()
