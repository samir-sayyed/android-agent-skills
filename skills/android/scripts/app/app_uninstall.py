#!/usr/bin/env python3
"""
Uninstall app from Android device.
Usage: python app_uninstall.py --package com.example.app [--keep-data]
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources'))
from common import (
    output_json, output_error, get_device_udid,
    run_adb_command, ADBError
)


def uninstall_app(package: str, udid: str = None, keep_data: bool = False) -> dict:
    """
    Uninstall app from device.
    
    Args:
        package: Package name to uninstall
        udid: Target device UDID
        keep_data: Keep app data after uninstall
    
    Returns:
        Uninstall result dict
    """
    try:
        udid = get_device_udid(udid)
    except ADBError as e:
        return {'uninstalled': False, 'error': str(e)}
    
    args = ['uninstall']
    
    if keep_data:
        args.append('-k')
    
    args.append(package)
    
    try:
        result = run_adb_command(args, udid=udid, timeout=30)
        
        if 'Success' in result.stdout:
            return {
                'uninstalled': True,
                'package': package,
                'device': udid,
                'data_kept': keep_data
            }
        else:
            return {
                'uninstalled': False,
                'error': result.stdout.strip() or result.stderr.strip()
            }
    except ADBError as e:
        return {'uninstalled': False, 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(description='Uninstall app from Android device')
    parser.add_argument('--package', '-p', required=True, help='Package name')
    parser.add_argument('--udid', '-d', help='Target device UDID')
    parser.add_argument('--keep-data', '-k', action='store_true', help='Keep app data')
    parser.add_argument('--format', choices=['json', 'text'], default='json')
    
    args = parser.parse_args()
    
    result = uninstall_app(
        package=args.package,
        udid=args.udid,
        keep_data=args.keep_data
    )
    
    if args.format == 'json':
        output_json(result, success=result['uninstalled'])
    else:
        if result['uninstalled']:
            print(f"✓ Uninstalled {result['package']}")
        else:
            print(f"✗ Uninstall failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)


if __name__ == '__main__':
    main()
