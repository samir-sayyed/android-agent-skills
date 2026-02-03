#!/usr/bin/env python3
"""
Map and analyze UI elements on screen.
Usage: python screen_mapper.py [--clickable] [--format tree|list|json]
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources'))
from common import (
    output_json, output_error, get_device_udid,
    get_ui_hierarchy, parse_ui_hierarchy, ADBError
)


def map_screen(udid: str = None, clickable_only: bool = False, 
               max_elements: int = 50) -> dict:
    """
    Map all UI elements on screen.
    
    Args:
        udid: Target device UDID
        clickable_only: Only return clickable elements
        max_elements: Maximum elements to return
    
    Returns:
        Screen map dict
    """
    try:
        udid = get_device_udid(udid)
    except ADBError as e:
        return {'error': str(e)}
    
    try:
        xml = get_ui_hierarchy(udid)
        elements = parse_ui_hierarchy(xml)
        
        if clickable_only:
            elements = [e for e in elements if e.clickable]
        
        # Convert to simple dicts
        element_list = []
        for e in elements[:max_elements]:
            elem = {
                'index': e.index,
                'text': e.text,
                'id': e.resource_id.split('/')[-1] if '/' in e.resource_id else e.resource_id,
                'class': e.class_name.split('.')[-1] if '.' in e.class_name else e.class_name,
                'content_desc': e.content_desc,
                'bounds': e.bounds,
                'center': e.center,
                'clickable': e.clickable
            }
            
            # Only include non-empty fields
            elem = {k: v for k, v in elem.items() if v or k in ['index', 'clickable', 'bounds', 'center']}
            element_list.append(elem)
        
        return {
            'device': udid,
            'total_elements': len(parse_ui_hierarchy(xml)),
            'returned_elements': len(element_list),
            'clickable_only': clickable_only,
            'elements': element_list
        }
    except ADBError as e:
        return {'error': str(e)}


def format_tree(elements: list, indent: int = 0) -> str:
    """Format elements as tree view."""
    lines = []
    for e in elements:
        prefix = '  ' * indent
        name = e.get('text') or e.get('content_desc') or e.get('id') or e.get('class', 'unknown')
        click = '🔘' if e.get('clickable') else '  '
        center = e.get('center', (0, 0))
        lines.append(f"{click} [{e['index']:3d}] {name} @ ({center[0]}, {center[1]})")
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Map UI elements on Android screen')
    parser.add_argument('--udid', '-d', help='Target device UDID')
    parser.add_argument('--clickable', '-c', action='store_true', help='Only clickable elements')
    parser.add_argument('--max', '-m', type=int, default=50, help='Max elements to return')
    parser.add_argument('--format', '-f', choices=['json', 'tree', 'text'], default='json')
    parser.add_argument('--verbose', '-v', action='store_true', help='Include all element details')
    
    args = parser.parse_args()
    
    result = map_screen(
        udid=args.udid,
        clickable_only=args.clickable,
        max_elements=args.max
    )
    
    if 'error' in result:
        output_error(result['error'])
        return
    
    if args.format == 'json':
        output_json(result)
    elif args.format in ['tree', 'text']:
        print(f"Screen Elements ({result['returned_elements']}/{result['total_elements']})")
        print("=" * 60)
        print(format_tree(result['elements']))


if __name__ == '__main__':
    main()
