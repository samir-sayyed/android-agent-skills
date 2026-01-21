#!/usr/bin/env python3
"""
Boot an Android emulator by AVD name.
Usage: python emulator_boot.py --avd Pixel_7_API_34 [--headless] [--wipe-data]
"""

import argparse
import subprocess
import time
import sys
import os

# Add resources to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources'))
from common import output_json, output_error, get_connected_devices


def list_avds() -> list:
    """List available AVDs."""
    try:
        result = subprocess.run(
            ['emulator', '-list-avds'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return [avd.strip() for avd in result.stdout.strip().split('\n') if avd.strip()]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def boot_emulator(
    avd_name: str,
    headless: bool = False,
    wipe_data: bool = False,
    wait: bool = True,
    timeout: int = 120
) -> dict:
    """
    Boot an Android emulator.
    
    Args:
        avd_name: Name of the AVD to boot
        headless: Run without GUI (for CI/CD)
        wipe_data: Wipe user data before booting
        wait: Wait for device to be ready
        timeout: Timeout in seconds
    
    Returns:
        Dict with boot result
    """
    # Check if AVD exists
    avds = list_avds()
    if avd_name not in avds:
        return {
            'booted': False,
            'error': f"AVD '{avd_name}' not found. Available: {avds}"
        }
    
    # Build command
    cmd = ['emulator', '-avd', avd_name]
    
    if headless:
        cmd.extend(['-no-window', '-no-audio'])
    
    if wipe_data:
        cmd.append('-wipe-data')
    
    # Start emulator in background
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    if not wait:
        return {
            'booted': True,
            'pid': process.pid,
            'avd': avd_name,
            'message': 'Emulator starting in background'
        }
    
    # Wait for device to be ready
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        time.sleep(2)
        
        # Check if emulator is in device list
        devices = get_connected_devices()
        for device in devices:
            if 'emulator' in device.get('udid', ''):
                # Check if boot completed
                try:
                    result = subprocess.run(
                        ['adb', '-s', device['udid'], 'shell', 
                         'getprop', 'sys.boot_completed'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.stdout.strip() == '1':
                        return {
                            'booted': True,
                            'udid': device['udid'],
                            'avd': avd_name,
                            'boot_time_seconds': round(time.time() - start_time, 1)
                        }
                except subprocess.TimeoutExpired:
                    continue
    
    return {
        'booted': False,
        'error': f'Emulator boot timed out after {timeout}s'
    }


def main():
    parser = argparse.ArgumentParser(description='Boot Android emulator')
    parser.add_argument('--avd', required=True, help='AVD name to boot')
    parser.add_argument('--headless', action='store_true', help='Run without window')
    parser.add_argument('--wipe-data', action='store_true', help='Wipe user data')
    parser.add_argument('--no-wait', action='store_true', help='Don\'t wait for boot')
    parser.add_argument('--timeout', type=int, default=120, help='Boot timeout (seconds)')
    parser.add_argument('--list', action='store_true', help='List available AVDs')
    parser.add_argument('--format', choices=['json', 'text'], default='json')
    
    args = parser.parse_args()
    
    if args.list:
        avds = list_avds()
        if args.format == 'json':
            output_json({'avds': avds})
        else:
            print('Available AVDs:')
            for avd in avds:
                print(f'  - {avd}')
        return
    
    result = boot_emulator(
        avd_name=args.avd,
        headless=args.headless,
        wipe_data=args.wipe_data,
        wait=not args.no_wait,
        timeout=args.timeout
    )
    
    if args.format == 'json':
        output_json(result, success=result.get('booted', False))
    else:
        if result.get('booted'):
            print(f"✓ Emulator '{args.avd}' booted successfully")
            if 'udid' in result:
                print(f"  UDID: {result['udid']}")
            if 'boot_time_seconds' in result:
                print(f"  Boot time: {result['boot_time_seconds']}s")
        else:
            print(f"✗ Failed to boot emulator: {result.get('error', 'Unknown error')}")
            sys.exit(1)


if __name__ == '__main__':
    main()
