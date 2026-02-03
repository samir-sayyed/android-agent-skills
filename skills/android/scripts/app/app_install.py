#!/usr/bin/env python3
"""
Install APK to Android device.
Usage: python app_install.py --apk path/to/app.apk [--replace]
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources'))
from common import (
    output_json, output_error, get_device_udid,
    run_adb_command, ADBError
)


def install_apk(apk_path: str, udid: str = None, replace: bool = False, 
                grant_permissions: bool = True) -> dict:
    """
    Install APK to device.
    
    Args:
        apk_path: Path to APK file
        udid: Target device UDID
        replace: Replace existing app if installed
        grant_permissions: Grant all runtime permissions
    
    Returns:
        Installation result dict
    """
    if not os.path.exists(apk_path):
        return {'installed': False, 'error': f"APK not found: {apk_path}"}
    
    try:
        udid = get_device_udid(udid)
    except ADBError as e:
        return {'installed': False, 'error': str(e)}
    
    args = ['install']
    
    if replace:
        args.append('-r')
    
    if grant_permissions:
        args.append('-g')
    
    args.append(apk_path)
    
    try:
        result = run_adb_command(args, udid=udid, timeout=120)
        
        if 'Success' in result.stdout:
            return {
                'installed': True,
                'apk': os.path.basename(apk_path),
                'device': udid
            }
        else:
            return {
                'installed': False,
                'error': result.stdout.strip() or result.stderr.strip()
            }
    except ADBError as e:
        return {'installed': False, 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(description='Install APK to Android device')
    parser.add_argument('--apk', required=True, help='Path to APK file')
    parser.add_argument('--udid', '-d', help='Target device UDID')
    parser.add_argument('--replace', '-r', action='store_true', help='Replace existing app')
    parser.add_argument('--no-permissions', action='store_true', help='Don\'t grant permissions')
    parser.add_argument('--format', choices=['json', 'text'], default='json')
    
    args = parser.parse_args()
    
    result = install_apk(
        apk_path=args.apk,
        udid=args.udid,
        replace=args.replace,
        grant_permissions=not args.no_permissions
    )
    
    if args.format == 'json':
        output_json(result, success=result['installed'])
    else:
        if result['installed']:
            print(f"✓ Installed {result['apk']} on {result['device']}")
        else:
            print(f"✗ Installation failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)


if __name__ == '__main__':
    main()
