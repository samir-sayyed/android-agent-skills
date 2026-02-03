#!/usr/bin/env python3
"""
List installed apps on Android device.
Usage: python app_list.py [--filter user|system|all] [--search keyword]
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources'))
from common import (
    output_json, output_error, get_device_udid,
    run_shell_command, ADBError
)


def list_apps(udid: str = None, filter_type: str = 'all', 
              search: str = None) -> dict:
    """
    List installed apps.
    
    Args:
        udid: Target device UDID
        filter_type: 'user', 'system', or 'all'
        search: Optional search keyword
    
    Returns:
        Dict with app list
    """
    try:
        udid = get_device_udid(udid)
    except ADBError as e:
        return {'error': str(e)}
    
    # Build pm list command
    if filter_type == 'user':
        cmd = 'pm list packages -3'
    elif filter_type == 'system':
        cmd = 'pm list packages -s'
    else:
        cmd = 'pm list packages'
    
    try:
        result = run_shell_command(cmd, udid=udid)
        
        packages = []
        for line in result.stdout.strip().split('\n'):
            if line.startswith('package:'):
                package = line.replace('package:', '').strip()
                
                # Apply search filter
                if search and search.lower() not in package.lower():
                    continue
                
                packages.append(package)
        
        packages.sort()
        
        return {
            'device': udid,
            'filter': filter_type,
            'count': len(packages),
            'packages': packages
        }
    except ADBError as e:
        return {'error': str(e)}


def main():
    parser = argparse.ArgumentParser(description='List installed Android apps')
    parser.add_argument('--udid', '-d', help='Target device UDID')
    parser.add_argument('--filter', '-f', choices=['user', 'system', 'all'], 
                        default='all', help='Filter by app type')
    parser.add_argument('--search', '-s', help='Search keyword')
    parser.add_argument('--format', choices=['json', 'text'], default='json')
    
    args = parser.parse_args()
    
    result = list_apps(
        udid=args.udid,
        filter_type=args.filter,
        search=args.search
    )
    
    if 'error' in result:
        output_error(result['error'])
        return
    
    if args.format == 'json':
        output_json(result)
    else:
        print(f"Installed apps ({result['filter']}): {result['count']}")
        for pkg in result['packages']:
            print(f"  {pkg}")


if __name__ == '__main__':
    main()
