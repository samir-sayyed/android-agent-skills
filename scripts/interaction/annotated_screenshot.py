#!/usr/bin/env python3
"""
Capture screenshot with annotated clickable elements.
Creates a visual map for AI agents to understand screen layout.

Usage:
  python annotated_screenshot.py --output annotated.png
  python annotated_screenshot.py --output annotated.png --show-all
"""

import argparse
import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources'))
from common import (
    output_json, output_error, get_device_udid,
    get_ui_hierarchy, parse_ui_hierarchy, run_adb_command,
    ADBError
)

# Try to import Pillow
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


def capture_annotated_screenshot(
    udid: str = None,
    output_path: str = "annotated.png",
    show_all: bool = False,
    show_bounds: bool = True,
    show_numbers: bool = True,
    json_output: str = None
) -> dict:
    """
    Capture screenshot with annotated UI elements.
    
    Args:
        udid: Target device UDID
        output_path: Path to save annotated screenshot
        show_all: Show all elements, not just clickable ones
        show_bounds: Draw bounding boxes
        show_numbers: Draw element numbers
        json_output: Path to save element mapping JSON
    
    Returns:
        Result dict with element mapping
    """
    if not PILLOW_AVAILABLE:
        return {
            'success': False,
            'error': 'Pillow not installed. Run: pip install Pillow'
        }
    
    try:
        udid = get_device_udid(udid)
    except ADBError as e:
        return {'success': False, 'error': str(e)}
    
    try:
        # Capture screenshot
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp_path = tmp.name
        
        # Take screenshot on device
        device_path = '/data/local/tmp/screenshot.png'
        run_adb_command(['shell', 'screencap', '-p', device_path], udid=udid)
        
        # Pull to local
        run_adb_command(['pull', device_path, tmp_path], udid=udid)
        
        # Clean up device file
        run_adb_command(['shell', 'rm', device_path], udid=udid, check=False)
        
        # Get UI hierarchy
        xml = get_ui_hierarchy(udid)
        elements = parse_ui_hierarchy(xml)
        
        # Filter elements
        if show_all:
            target_elements = [e for e in elements if e.enabled]
        else:
            target_elements = [e for e in elements if e.clickable and e.enabled]
        
        # Open image and create drawing context
        img = Image.open(tmp_path)
        draw = ImageDraw.Draw(img)
        
        # Try to get a font, fall back to default
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
            small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        except:
            font = ImageFont.load_default()
            small_font = font
        
        # Color scheme
        colors = {
            'box': (255, 0, 0, 180),      # Red boxes
            'text_bg': (255, 255, 0),      # Yellow background
            'text': (0, 0, 0),             # Black text
            'number_bg': (255, 0, 0),      # Red number background
            'number': (255, 255, 255),     # White number text
        }
        
        # Annotate elements
        element_map = []
        for idx, elem in enumerate(target_elements):
            bounds = elem.bounds
            left, top, right, bottom = bounds
            
            # Skip elements with invalid bounds
            if right <= left or bottom <= top:
                continue
            
            # Draw bounding box
            if show_bounds:
                draw.rectangle([left, top, right, bottom], outline=colors['box'], width=2)
            
            # Draw number label
            if show_numbers:
                number = str(idx + 1)
                # Draw number circle
                circle_x = left - 12
                circle_y = top - 12
                circle_radius = 14
                draw.ellipse(
                    [circle_x, circle_y, circle_x + circle_radius * 2, circle_y + circle_radius * 2],
                    fill=colors['number_bg']
                )
                # Draw number text
                draw.text(
                    (circle_x + circle_radius - 5, circle_y + 2),
                    number,
                    fill=colors['number'],
                    font=small_font
                )
            
            # Build element info
            label = elem.text or elem.content_desc or elem.resource_id.split('/')[-1] if elem.resource_id else elem.class_name.split('.')[-1]
            element_map.append({
                'number': idx + 1,
                'text': elem.text,
                'content_desc': elem.content_desc,
                'resource_id': elem.resource_id,
                'class': elem.class_name.split('.')[-1],
                'bounds': list(bounds),
                'center': list(elem.center),
                'label': label
            })
        
        # Save annotated image
        img.save(output_path)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        # Save JSON mapping if requested
        if json_output:
            with open(json_output, 'w') as f:
                json.dump({'elements': element_map}, f, indent=2)
        
        return {
            'success': True,
            'screenshot': output_path,
            'element_count': len(element_map),
            'elements': element_map,
            'json_file': json_output
        }
        
    except ADBError as e:
        return {'success': False, 'error': str(e)}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(
        description='Capture screenshot with annotated clickable elements',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Basic annotated screenshot
  python annotated_screenshot.py --output screen.png
  
  # Include all elements (not just clickable)
  python annotated_screenshot.py --output screen.png --show-all
  
  # Save element mapping as JSON
  python annotated_screenshot.py --output screen.png --json elements.json
'''
    )
    
    parser.add_argument('--output', '-o', default='annotated.png',
                       help='Output path for annotated screenshot')
    parser.add_argument('--json', '-j', dest='json_output',
                       help='Output path for element mapping JSON')
    parser.add_argument('--show-all', action='store_true',
                       help='Show all elements, not just clickable ones')
    parser.add_argument('--no-bounds', action='store_true',
                       help='Hide bounding boxes')
    parser.add_argument('--no-numbers', action='store_true',
                       help='Hide element numbers')
    parser.add_argument('--udid', '-d', help='Target device UDID')
    parser.add_argument('--format', '-f', choices=['json', 'text'], default='json')
    
    args = parser.parse_args()
    
    result = capture_annotated_screenshot(
        udid=args.udid,
        output_path=args.output,
        show_all=args.show_all,
        show_bounds=not args.no_bounds,
        show_numbers=not args.no_numbers,
        json_output=args.json_output
    )
    
    if args.format == 'json':
        output_json(result, success=result.get('success', False))
    else:
        if result.get('success'):
            print(f"✓ Screenshot saved: {result['screenshot']}")
            print(f"  Elements annotated: {result['element_count']}")
            if result.get('json_file'):
                print(f"  JSON mapping: {result['json_file']}")
            print("\nElement Summary:")
            for elem in result.get('elements', [])[:10]:
                print(f"  [{elem['number']}] {elem['label']} @ {elem['center']}")
            if len(result.get('elements', [])) > 10:
                print(f"  ... and {len(result['elements']) - 10} more")
        else:
            print(f"✗ {result.get('error', 'Failed to capture screenshot')}")
            sys.exit(1)


if __name__ == '__main__':
    main()
