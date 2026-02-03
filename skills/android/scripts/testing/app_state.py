#!/usr/bin/env python3
"""
Capture app state for debugging.
Usage:
  python app_state.py --output state/
  python app_state.py --package com.example.app --output debug/
"""

import argparse
import sys
import os
import time
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources'))
from common import (
    output_json, output_error, get_device_udid,
    run_shell_command, run_adb_command, get_ui_hierarchy,
    ADBError
)


def capture_app_state(
    output_dir: str,
    udid: str = None,
    package: str = None
) -> dict:
    """
    Capture comprehensive app state for debugging.
    
    Captures:
    - Screenshot
    - UI hierarchy
    - Logcat snapshot
    - Memory info (if package specified)
    
    Args:
        output_dir: Directory to save state files
        udid: Target device UDID
        package: Optional package to focus on
    
    Returns:
        Capture result dict
    """
    try:
        udid = get_device_udid(udid)
    except ADBError as e:
        return {'error': str(e)}
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    timestamp = int(time.time())
    
    captured = []
    errors = []
    
    # 1. Screenshot
    try:
        device_path = f'/data/local/tmp/state_{timestamp}.png'
        local_path = os.path.join(output_dir, 'screenshot.png')
        run_shell_command(f'screencap -p {device_path}', udid=udid)
        run_adb_command(['pull', device_path, local_path], udid=udid)
        run_shell_command(f'rm {device_path}', udid=udid, check=False)
        captured.append({'type': 'screenshot', 'path': local_path})
    except ADBError as e:
        errors.append({'type': 'screenshot', 'error': str(e)})
    
    # 2. UI Hierarchy
    try:
        xml = get_ui_hierarchy(udid)
        xml_path = os.path.join(output_dir, 'ui_hierarchy.xml')
        with open(xml_path, 'w') as f:
            f.write(xml)
        captured.append({'type': 'ui_hierarchy', 'path': xml_path})
    except ADBError as e:
        errors.append({'type': 'ui_hierarchy', 'error': str(e)})
    
    # 3. Logcat snapshot
    try:
        log_cmd = ['logcat', '-d', '-v', 'time', '-t', '100']
        result = run_adb_command(log_cmd, udid=udid)
        logs = result.stdout
        
        if package:
            logs = '\n'.join([l for l in logs.split('\n') if package in l])
        
        log_path = os.path.join(output_dir, 'logcat.txt')
        with open(log_path, 'w') as f:
            f.write(logs)
        captured.append({'type': 'logcat', 'path': log_path})
    except ADBError as e:
        errors.append({'type': 'logcat', 'error': str(e)})
    
    # 4. Memory info (if package specified)
    if package:
        try:
            result = run_shell_command(f'dumpsys meminfo {package}', udid=udid)
            mem_path = os.path.join(output_dir, 'meminfo.txt')
            with open(mem_path, 'w') as f:
                f.write(result.stdout)
            captured.append({'type': 'meminfo', 'path': mem_path})
        except ADBError as e:
            errors.append({'type': 'meminfo', 'error': str(e)})
    
    # 5. Device info summary
    info = {
        'timestamp': timestamp,
        'device': udid,
        'package': package,
        'captured': [c['type'] for c in captured],
        'errors': [e['type'] for e in errors]
    }
    
    info_path = os.path.join(output_dir, 'state_info.json')
    with open(info_path, 'w') as f:
        json.dump(info, f, indent=2)
    
    return {
        'success': True,
        'output_dir': os.path.abspath(output_dir),
        'captured': captured,
        'errors': errors
    }


def main():
    parser = argparse.ArgumentParser(description='Capture app state for debugging')
    parser.add_argument('--output', '-o', required=True, help='Output directory')
    parser.add_argument('--package', '-p', help='Focus on specific package')
    parser.add_argument('--udid', '-d', help='Target device UDID')
    parser.add_argument('--format', '-f', choices=['json', 'text'], default='json')
    
    args = parser.parse_args()
    
    result = capture_app_state(
        output_dir=args.output,
        udid=args.udid,
        package=args.package
    )
    
    if 'error' in result:
        output_error(result['error'])
        return
    
    if args.format == 'json':
        output_json(result)
    else:
        print(f"✓ State captured to: {result['output_dir']}")
        print("\nCaptured:")
        for item in result['captured']:
            print(f"  - {item['type']}: {os.path.basename(item['path'])}")
        if result['errors']:
            print("\nErrors:")
            for err in result['errors']:
                print(f"  - {err['type']}: {err.get('error', 'Unknown')}")


if __name__ == '__main__':
    main()
