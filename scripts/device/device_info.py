#!/usr/bin/env python3
"""
Get Android device information.
Usage: python device_info.py [--udid device_id]
"""

import argparse
import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources'))
from common import (
    output_json, output_error, get_device_udid,
    run_shell_command, run_adb_command, ADBError
)


def get_device_property(prop: str, udid: str = None) -> str:
    """Get a device property."""
    try:
        result = run_shell_command(f'getprop {prop}', udid=udid)
        return result.stdout.strip()
    except ADBError:
        return ''


def get_screen_size(udid: str = None) -> dict:
    """Get screen size and density."""
    try:
        # Physical size
        size_result = run_shell_command('wm size', udid=udid)
        size_match = re.search(r'Physical size: (\d+)x(\d+)', size_result.stdout)
        
        # Density
        density_result = run_shell_command('wm density', udid=udid)
        density_match = re.search(r'Physical density: (\d+)', density_result.stdout)
        
        return {
            'width': int(size_match.group(1)) if size_match else 0,
            'height': int(size_match.group(2)) if size_match else 0,
            'density': int(density_match.group(1)) if density_match else 0
        }
    except ADBError:
        return {'width': 0, 'height': 0, 'density': 0}


def get_battery_info(udid: str = None) -> dict:
    """Get battery information."""
    try:
        result = run_shell_command('dumpsys battery', udid=udid)
        info = {}
        
        for line in result.stdout.split('\n'):
            line = line.strip()
            if line.startswith('level:'):
                info['level'] = int(line.split(':')[1].strip())
            elif line.startswith('status:'):
                status_code = int(line.split(':')[1].strip())
                status_map = {1: 'unknown', 2: 'charging', 3: 'discharging', 
                             4: 'not_charging', 5: 'full'}
                info['status'] = status_map.get(status_code, 'unknown')
            elif line.startswith('plugged:'):
                plugged_code = int(line.split(':')[1].strip())
                plugged_map = {0: 'unplugged', 1: 'ac', 2: 'usb', 4: 'wireless'}
                info['plugged'] = plugged_map.get(plugged_code, 'unknown')
        
        return info
    except (ADBError, ValueError):
        return {}


def get_device_info(udid: str = None) -> dict:
    """Get comprehensive device information."""
    try:
        udid = get_device_udid(udid)
    except ADBError as e:
        return {'error': str(e)}
    
    return {
        'udid': udid,
        'manufacturer': get_device_property('ro.product.manufacturer', udid),
        'model': get_device_property('ro.product.model', udid),
        'device': get_device_property('ro.product.device', udid),
        'android_version': get_device_property('ro.build.version.release', udid),
        'sdk_version': get_device_property('ro.build.version.sdk', udid),
        'build_id': get_device_property('ro.build.display.id', udid),
        'screen': get_screen_size(udid),
        'battery': get_battery_info(udid),
        'is_emulator': 'emulator' in udid or get_device_property('ro.kernel.qemu', udid) == '1',
        'locale': get_device_property('persist.sys.locale', udid) or 
                  get_device_property('ro.product.locale', udid),
        'timezone': get_device_property('persist.sys.timezone', udid)
    }


def main():
    parser = argparse.ArgumentParser(description='Get Android device information')
    parser.add_argument('--udid', '-d', help='Target device UDID')
    parser.add_argument('--format', choices=['json', 'text'], default='json')
    
    args = parser.parse_args()
    
    info = get_device_info(args.udid)
    
    if 'error' in info:
        output_error(info['error'])
        return
    
    if args.format == 'json':
        output_json(info)
    else:
        print(f"Device: {info['manufacturer']} {info['model']}")
        print(f"UDID: {info['udid']}")
        print(f"Android: {info['android_version']} (SDK {info['sdk_version']})")
        print(f"Screen: {info['screen']['width']}x{info['screen']['height']} @ {info['screen']['density']}dpi")
        if info['battery']:
            print(f"Battery: {info['battery'].get('level', 'N/A')}% ({info['battery'].get('status', 'unknown')})")
        print(f"Emulator: {'Yes' if info['is_emulator'] else 'No'}")


if __name__ == '__main__':
    main()
