#!/usr/bin/env python3
"""
Navigate and interact with UI elements by semantic search.
Usage: 
  python navigator.py --find-text "Login" --tap
  python navigator.py --find-id "submit_button" --tap
  python navigator.py --find-type EditText --index 0 --enter-text "hello"
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources'))
from common import (
    output_json, output_error, get_device_udid,
    get_ui_hierarchy, parse_ui_hierarchy, find_element, find_elements,
    tap, input_text, ADBError
)


def navigate(
    udid: str = None,
    find_text: str = None,
    find_id: str = None,
    find_class: str = None,
    find_desc: str = None,
    index: int = 0,
    do_tap: bool = False,
    do_long_press: bool = False,
    enter_text: str = None,
    list_matches: bool = False
) -> dict:
    """
    Find and interact with UI element.
    
    Args:
        udid: Target device UDID
        find_text: Find by text content
        find_id: Find by resource ID
        find_class: Find by class name
        find_desc: Find by content description
        index: Which match to use (0-indexed)
        do_tap: Tap the element
        do_long_press: Long press the element
        enter_text: Text to enter after finding
        list_matches: Just list all matches
    
    Returns:
        Navigation result dict
    """
    try:
        udid = get_device_udid(udid)
    except ADBError as e:
        return {'found': False, 'error': str(e)}
    
    try:
        xml = get_ui_hierarchy(udid)
        all_elements = parse_ui_hierarchy(xml)
        
        # Find matching elements
        matches = find_elements(
            all_elements,
            text=find_text,
            resource_id=find_id,
            class_name=find_class,
            content_desc=find_desc
        )
        
        if not matches:
            criteria = []
            if find_text: criteria.append(f"text='{find_text}'")
            if find_id: criteria.append(f"id='{find_id}'")
            if find_class: criteria.append(f"class='{find_class}'")
            if find_desc: criteria.append(f"desc='{find_desc}'")
            return {
                'found': False,
                'error': f"No element found matching: {', '.join(criteria)}",
                'total_elements': len(all_elements)
            }
        
        # If listing matches
        if list_matches:
            return {
                'found': True,
                'match_count': len(matches),
                'matches': [m.to_dict() for m in matches[:10]]
            }
        
        # Get specific match by index
        if index >= len(matches):
            return {
                'found': False,
                'error': f"Index {index} out of range. Found {len(matches)} matches.",
                'match_count': len(matches)
            }
        
        element = matches[index]
        result = {
            'found': True,
            'element': element.to_dict(),
            'match_count': len(matches),
            'used_index': index,
            'actions': []
        }
        
        # Perform tap
        if do_tap:
            center = element.center
            tap(center[0], center[1], udid=udid)
            result['actions'].append('tap')
        
        # Perform long press
        if do_long_press:
            from common import swipe
            center = element.center
            swipe(center[0], center[1], center[0], center[1], duration_ms=1000, udid=udid)
            result['actions'].append('long_press')
        
        # Enter text
        if enter_text is not None:
            # Tap to focus first
            if not do_tap:
                center = element.center
                tap(center[0], center[1], udid=udid)
            # Clear existing text and enter new
            input_text(enter_text, udid=udid)
            result['actions'].append(f'enter_text: "{enter_text}"')
        
        return result
        
    except ADBError as e:
        return {'found': False, 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(description='Navigate and interact with UI elements')
    
    # Search criteria
    parser.add_argument('--find-text', '-t', help='Find by text content')
    parser.add_argument('--find-id', '-i', help='Find by resource ID')
    parser.add_argument('--find-class', '-c', help='Find by class name (e.g., EditText, Button)')
    parser.add_argument('--find-desc', help='Find by content description')
    parser.add_argument('--index', type=int, default=0, help='Which match to use (0-indexed)')
    
    # Actions
    parser.add_argument('--tap', action='store_true', help='Tap the element')
    parser.add_argument('--long-press', action='store_true', help='Long press the element')
    parser.add_argument('--enter-text', help='Text to enter (taps and types)')
    parser.add_argument('--list', action='store_true', help='List all matches')
    
    # Common
    parser.add_argument('--udid', '-d', help='Target device UDID')
    parser.add_argument('--format', '-f', choices=['json', 'text'], default='json')
    
    args = parser.parse_args()
    
    # Validate at least one search criteria
    if not any([args.find_text, args.find_id, args.find_class, args.find_desc]):
        parser.error('At least one search criteria required: --find-text, --find-id, --find-class, or --find-desc')
    
    result = navigate(
        udid=args.udid,
        find_text=args.find_text,
        find_id=args.find_id,
        find_class=args.find_class,
        find_desc=args.find_desc,
        index=args.index,
        do_tap=args.tap,
        do_long_press=args.long_press,
        enter_text=args.enter_text,
        list_matches=args.list
    )
    
    if args.format == 'json':
        output_json(result, success=result.get('found', False))
    else:
        if result.get('found'):
            elem = result.get('element', {})
            print(f"✓ Found element: {elem.get('text') or elem.get('resource_id') or elem.get('class_name')}")
            print(f"  Center: {elem.get('center')}")
            if result.get('actions'):
                print(f"  Actions: {', '.join(result['actions'])}")
        else:
            print(f"✗ {result.get('error', 'Element not found')}")
            sys.exit(1)


if __name__ == '__main__':
    main()
