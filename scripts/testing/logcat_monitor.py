#!/usr/bin/env python3
"""
Monitor logcat output from Android device.
Usage:
  python logcat_monitor.py --package com.example.app
  python logcat_monitor.py --tag MyTag --level E
  python logcat_monitor.py --duration 30 --output logs.txt
"""

import argparse
import sys
import os
import time
import signal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources'))
from common import (
    output_json, output_error, get_device_udid,
    run_adb_command, ADBError
)


def capture_logs(
    udid: str = None,
    package: str = None,
    tag: str = None,
    level: str = None,
    duration: int = 10,
    max_lines: int = 100,
    clear_first: bool = True
) -> dict:
    """
    Capture logcat output.
    
    Args:
        udid: Target device UDID
        package: Filter by package name
        tag: Filter by log tag
        level: Minimum log level (V/D/I/W/E/F)
        duration: Capture duration in seconds
        max_lines: Maximum lines to return
        clear_first: Clear log buffer before starting
    
    Returns:
        Log capture result dict
    """
    try:
        udid = get_device_udid(udid)
    except ADBError as e:
        return {'error': str(e)}
    
    # Clear log buffer if requested
    if clear_first:
        run_adb_command(['logcat', '-c'], udid=udid, check=False)
    
    # Build logcat command
    cmd = ['logcat', '-v', 'time', '-d']
    
    if tag:
        if level:
            cmd.extend(['-s', f'{tag}:{level}'])
        else:
            cmd.extend(['-s', f'{tag}:V'])
    elif level:
        cmd.append(f'*:{level}')
    
    # Wait for logs to accumulate
    time.sleep(min(duration, 30))
    
    try:
        result = run_adb_command(cmd, udid=udid, timeout=30)
        
        lines = result.stdout.strip().split('\n')
        
        # Filter by package if specified
        if package:
            lines = [l for l in lines if package in l]
        
        # Truncate to max lines
        lines = lines[-max_lines:]
        
        # Parse log entries
        entries = []
        for line in lines:
            if line.strip():
                entries.append({
                    'raw': line[:200]  # Truncate long lines
                })
        
        return {
            'device': udid,
            'filters': {
                'package': package,
                'tag': tag,
                'level': level
            },
            'duration_seconds': duration,
            'line_count': len(entries),
            'logs': entries
        }
        
    except ADBError as e:
        return {'error': str(e)}


def main():
    parser = argparse.ArgumentParser(description='Monitor logcat on Android device')
    parser.add_argument('--package', '-p', help='Filter by package name')
    parser.add_argument('--tag', '-t', help='Filter by log tag')
    parser.add_argument('--level', '-l', choices=['V', 'D', 'I', 'W', 'E', 'F'],
                        help='Minimum log level')
    parser.add_argument('--duration', type=int, default=10, help='Capture duration (seconds)')
    parser.add_argument('--max-lines', type=int, default=100, help='Max lines to return')
    parser.add_argument('--no-clear', action='store_true', help='Don\'t clear buffer first')
    parser.add_argument('--output', '-o', help='Save logs to file')
    parser.add_argument('--udid', '-d', help='Target device UDID')
    parser.add_argument('--format', '-f', choices=['json', 'text'], default='json')
    
    args = parser.parse_args()
    
    result = capture_logs(
        udid=args.udid,
        package=args.package,
        tag=args.tag,
        level=args.level,
        duration=args.duration,
        max_lines=args.max_lines,
        clear_first=not args.no_clear
    )
    
    if 'error' in result:
        output_error(result['error'])
        return
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            for entry in result['logs']:
                f.write(entry['raw'] + '\n')
        result['saved_to'] = os.path.abspath(args.output)
    
    if args.format == 'json':
        output_json(result)
    else:
        print(f"Logcat Capture ({result['line_count']} lines, {result['duration_seconds']}s)")
        print("=" * 60)
        for entry in result['logs']:
            print(entry['raw'])
        if args.output:
            print(f"\nSaved to: {result['saved_to']}")


if __name__ == '__main__':
    main()
