#!/usr/bin/env python3
"""
Launch Android app.
Usage: python app_launch.py --package com.example.app [--activity .MainActivity] [--clear]
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources'))
from common import (
    output_json, output_error, get_device_udid,
    run_shell_command, run_adb_command, ADBError
)


def get_launcher_activity(package: str, udid: str = None) -> str:
    """Get the launcher activity for a package."""
    try:
        result = run_shell_command(
            f"cmd package resolve-activity --brief {package} | tail -n 1",
            udid=udid
        )
        activity = result.stdout.strip()
        if '/' in activity:
            return activity.split('/')[1]
        return activity
    except ADBError:
        return ''


def launch_app(package: str, udid: str = None, activity: str = None, 
               clear: bool = False, wait: bool = True) -> dict:
    """
    Launch an Android app.
    
    Args:
        package: Package name
        udid: Target device UDID
        activity: Optional activity to launch
        clear: Clear app data before launching
        wait: Wait for launch to complete
    
    Returns:
        Launch result dict
    """
    try:
        udid = get_device_udid(udid)
    except ADBError as e:
        return {'launched': False, 'error': str(e)}
    
    # Clear data if requested
    if clear:
        run_shell_command(f'pm clear {package}', udid=udid, check=False)
    
    # Build launch command
    if activity:
        if not activity.startswith('.') and '/' not in activity:
            activity = f'.{activity}'
        component = f'{package}/{activity}'
        cmd = f'am start -n {component}'
    else:
        # Use monkey to launch without knowing activity
        cmd = f'monkey -p {package} -c android.intent.category.LAUNCHER 1'
    
    if wait:
        cmd = cmd.replace('am start', 'am start -W')
    
    try:
        result = run_shell_command(cmd, udid=udid)
        
        # Check for success indicators
        if 'Error' in result.stdout or 'Exception' in result.stdout:
            return {
                'launched': False,
                'package': package,
                'error': result.stdout.strip()
            }
        
        return {
            'launched': True,
            'package': package,
            'device': udid,
            'cleared': clear
        }
    except ADBError as e:
        return {'launched': False, 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(description='Launch Android app')
    parser.add_argument('--package', '-p', required=True, help='Package name')
    parser.add_argument('--activity', '-a', help='Activity to launch')
    parser.add_argument('--udid', '-d', help='Target device UDID')
    parser.add_argument('--clear', '-c', action='store_true', help='Clear app data first')
    parser.add_argument('--no-wait', action='store_true', help='Don\'t wait for launch')
    parser.add_argument('--format', choices=['json', 'text'], default='json')
    
    args = parser.parse_args()
    
    result = launch_app(
        package=args.package,
        udid=args.udid,
        activity=args.activity,
        clear=args.clear,
        wait=not args.no_wait
    )
    
    if args.format == 'json':
        output_json(result, success=result['launched'])
    else:
        if result['launched']:
            print(f"✓ Launched {result['package']}")
        else:
            print(f"✗ Launch failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)


if __name__ == '__main__':
    main()
