#!/usr/bin/env python3
"""
Capture screenshot from Android device.
Usage: python screenshot.py --output screen.png [--quality 80]
"""

import argparse
import sys
import os
import tempfile
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources'))
from common import (
    output_json, output_error, get_device_udid,
    run_shell_command, run_adb_command, ADBError
)


def capture_screenshot(output_path: str, udid: str = None) -> dict:
    """
    Capture screenshot from device.
    
    Args:
        output_path: Local path to save screenshot
        udid: Target device UDID
    
    Returns:
        Screenshot result dict
    """
    try:
        udid = get_device_udid(udid)
    except ADBError as e:
        return {'captured': False, 'error': str(e)}
    
    try:
        # Use exec-out to capture directly (works on Android 11+ with scoped storage)
        import subprocess
        
        cmd = ['adb']
        if udid:
            cmd.extend(['-s', udid])
        cmd.extend(['exec-out', 'screencap', '-p'])
        
        result = subprocess.run(cmd, capture_output=True, timeout=10)
        
        if result.returncode != 0 or len(result.stdout) < 1000:
            # Fallback to shell method for older devices
            device_path = f'/data/local/tmp/screenshot_{int(time.time())}.png'
            run_shell_command(f'screencap -p {device_path}', udid=udid)
            run_adb_command(['pull', device_path, output_path], udid=udid)
            run_shell_command(f'rm {device_path}', udid=udid, check=False)
        else:
            # Write directly from exec-out
            with open(output_path, 'wb') as f:
                f.write(result.stdout)
        
        # Get file size
        file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
        
        return {
            'captured': True,
            'path': os.path.abspath(output_path),
            'size_bytes': file_size,
            'device': udid
        }
    except ADBError as e:
        return {'captured': False, 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(description='Capture screenshot from Android device')
    parser.add_argument('--output', '-o', default='screenshot.png', help='Output file path')
    parser.add_argument('--udid', '-d', help='Target device UDID')
    parser.add_argument('--format', choices=['json', 'text'], default='json')
    
    args = parser.parse_args()
    
    result = capture_screenshot(args.output, args.udid)
    
    if args.format == 'json':
        output_json(result, success=result['captured'])
    else:
        if result['captured']:
            print(f"✓ Screenshot saved: {result['path']}")
            print(f"  Size: {result['size_bytes']} bytes")
        else:
            print(f"✗ Capture failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)


if __name__ == '__main__':
    main()
