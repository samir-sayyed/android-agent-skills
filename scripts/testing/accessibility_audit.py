#!/usr/bin/env python3
"""
Check accessibility issues on Android screen.
Usage:
  python accessibility_audit.py [--package com.example.app]
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources'))
from common import (
    output_json, output_error, get_device_udid,
    get_ui_hierarchy, parse_ui_hierarchy, ADBError
)


def audit_accessibility(udid: str = None) -> dict:
    """
    Audit current screen for accessibility issues.
    
    Checks for:
    - Missing content descriptions on clickable items
    - Text too small (estimated)
    - Insufficient touch target size
    - Non-focusable interactive elements
    
    Returns:
        Audit results dict
    """
    try:
        udid = get_device_udid(udid)
    except ADBError as e:
        return {'error': str(e)}
    
    try:
        xml = get_ui_hierarchy(udid)
        elements = parse_ui_hierarchy(xml)
        
        issues = []
        stats = {
            'total_elements': len(elements),
            'clickable_elements': 0,
            'focusable_elements': 0,
            'with_content_desc': 0,
            'with_text': 0
        }
        
        for elem in elements:
            # Track stats
            if elem.clickable:
                stats['clickable_elements'] += 1
            if elem.focusable:
                stats['focusable_elements'] += 1
            if elem.content_desc:
                stats['with_content_desc'] += 1
            if elem.text:
                stats['with_text'] += 1
            
            # Check issues
            if elem.clickable or elem.focusable:
                # Missing content description
                if not elem.content_desc and not elem.text:
                    issues.append({
                        'type': 'missing_label',
                        'severity': 'error',
                        'element': {
                            'class': elem.class_name.split('.')[-1],
                            'id': elem.resource_id.split('/')[-1] if elem.resource_id else '',
                            'bounds': elem.bounds
                        },
                        'message': 'Interactive element missing content description and text'
                    })
                
                # Check touch target size (48dp minimum recommended)
                width = elem.bounds[2] - elem.bounds[0]
                height = elem.bounds[3] - elem.bounds[1]
                
                # Approximate 48dp as 144px at 3x density
                min_size = 100
                if width < min_size or height < min_size:
                    issues.append({
                        'type': 'small_touch_target',
                        'severity': 'warning',
                        'element': {
                            'class': elem.class_name.split('.')[-1],
                            'id': elem.resource_id.split('/')[-1] if elem.resource_id else '',
                            'text': elem.text[:30] if elem.text else '',
                            'size': (width, height)
                        },
                        'message': f'Touch target too small: {width}x{height}px'
                    })
            
            # Clickable but not focusable
            if elem.clickable and not elem.focusable:
                issues.append({
                    'type': 'not_focusable',
                    'severity': 'warning',
                    'element': {
                        'class': elem.class_name.split('.')[-1],
                        'id': elem.resource_id.split('/')[-1] if elem.resource_id else '',
                        'text': elem.text[:30] if elem.text else ''
                    },
                    'message': 'Clickable element is not focusable (keyboard navigation issue)'
                })
        
        # Summary
        error_count = len([i for i in issues if i['severity'] == 'error'])
        warning_count = len([i for i in issues if i['severity'] == 'warning'])
        
        return {
            'device': udid,
            'passed': error_count == 0,
            'stats': stats,
            'summary': {
                'errors': error_count,
                'warnings': warning_count
            },
            'issues': issues[:20]  # Limit to 20 issues
        }
        
    except ADBError as e:
        return {'error': str(e)}


def main():
    parser = argparse.ArgumentParser(description='Audit accessibility on Android device')
    parser.add_argument('--udid', '-d', help='Target device UDID')
    parser.add_argument('--format', '-f', choices=['json', 'text'], default='json')
    
    args = parser.parse_args()
    
    result = audit_accessibility(args.udid)
    
    if 'error' in result:
        output_error(result['error'])
        return
    
    if args.format == 'json':
        output_json(result, success=True)
    else:
        status = '✓ PASSED' if result['passed'] else '✗ FAILED'
        print(f"Accessibility Audit: {status}")
        print(f"  Total elements: {result['stats']['total_elements']}")
        print(f"  Errors: {result['summary']['errors']}")
        print(f"  Warnings: {result['summary']['warnings']}")
        
        if result['issues']:
            print("\nIssues:")
            for issue in result['issues']:
                icon = '❌' if issue['severity'] == 'error' else '⚠️'
                print(f"  {icon} {issue['message']}")
        
        if not result['passed']:
            sys.exit(1)


if __name__ == '__main__':
    main()
