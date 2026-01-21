#!/usr/bin/env python3
"""
Shutdown Android emulator.
Usage: python emulator_shutdown.py [--udid emulator-5554] [--all]
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources'))
from common import (
    output_json, output_error, get_connected_devices,
    run_adb_command, ADBError
)


def shutdown_emulator(udid: str) -> dict:
    """Shutdown a specific emulator."""
    try:
        run_adb_command(['emu', 'kill'], udid=udid)
        return {'udid': udid, 'shutdown': True}
    except ADBError as e:
        return {'udid': udid, 'shutdown': False, 'error': str(e)}


def shutdown_all_emulators() -> list:
    """Shutdown all running emulators."""
    devices = get_connected_devices()
    results = []
    
    for device in devices:
        if 'emulator' in device.get('udid', ''):
            result = shutdown_emulator(device['udid'])
            results.append(result)
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Shutdown Android emulator')
    parser.add_argument('--udid', '-d', help='Target emulator UDID')
    parser.add_argument('--all', action='store_true', help='Shutdown all emulators')
    parser.add_argument('--format', choices=['json', 'text'], default='json')
    
    args = parser.parse_args()
    
    if args.all:
        results = shutdown_all_emulators()
        if args.format == 'json':
            output_json({'results': results})
        else:
            if not results:
                print('No emulators running')
            else:
                for r in results:
                    status = '✓' if r['shutdown'] else '✗'
                    print(f"{status} {r['udid']}")
        return
    
    # Get target device
    devices = get_connected_devices()
    emulators = [d for d in devices if 'emulator' in d.get('udid', '')]
    
    if not emulators:
        output_error('No emulators running')
        return
    
    if args.udid:
        target = args.udid
    elif len(emulators) == 1:
        target = emulators[0]['udid']
    else:
        udids = [e['udid'] for e in emulators]
        output_error(f"Multiple emulators running. Specify --udid: {udids}")
        return
    
    result = shutdown_emulator(target)
    
    if args.format == 'json':
        output_json(result, success=result['shutdown'])
    else:
        if result['shutdown']:
            print(f"✓ Emulator {target} shutdown")
        else:
            print(f"✗ Failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)


if __name__ == '__main__':
    main()
