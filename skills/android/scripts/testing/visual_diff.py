#!/usr/bin/env python3
"""
Compare screenshots for visual regression testing.
Usage:
  python visual_diff.py baseline.png current.png
  python visual_diff.py baseline.png current.png --threshold 0.05 --output diff.png
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources'))
from common import output_json, output_error


def compare_images(
    baseline_path: str,
    current_path: str,
    threshold: float = 0.01,
    output_path: str = None
) -> dict:
    """
    Compare two images for visual differences.
    
    Args:
        baseline_path: Path to baseline image
        current_path: Path to current image
        threshold: Acceptable difference ratio (0.0-1.0)
        output_path: Optional path to save diff image
    
    Returns:
        Comparison result dict
    """
    # Check files exist
    if not os.path.exists(baseline_path):
        return {'match': False, 'error': f"Baseline not found: {baseline_path}"}
    if not os.path.exists(current_path):
        return {'match': False, 'error': f"Current not found: {current_path}"}
    
    try:
        from PIL import Image, ImageChops, ImageDraw
        
        # Load images
        baseline = Image.open(baseline_path).convert('RGB')
        current = Image.open(current_path).convert('RGB')
        
        # Check dimensions
        if baseline.size != current.size:
            return {
                'match': False,
                'error': 'Image dimensions differ',
                'baseline_size': baseline.size,
                'current_size': current.size
            }
        
        # Calculate difference
        diff = ImageChops.difference(baseline, current)
        
        # Count different pixels
        diff_data = list(diff.getdata())
        total_pixels = len(diff_data)
        diff_pixels = sum(1 for pixel in diff_data if any(channel > 10 for channel in pixel))
        diff_ratio = diff_pixels / total_pixels
        
        # Determine if match
        is_match = diff_ratio <= threshold
        
        result = {
            'match': is_match,
            'baseline': os.path.basename(baseline_path),
            'current': os.path.basename(current_path),
            'dimensions': baseline.size,
            'diff_pixels': diff_pixels,
            'total_pixels': total_pixels,
            'diff_ratio': round(diff_ratio, 6),
            'threshold': threshold
        }
        
        # Save diff image if requested
        if output_path and not is_match:
            # Enhance diff for visibility
            diff_enhanced = diff.point(lambda x: min(255, x * 3))
            
            # Create side-by-side comparison
            width = baseline.width + current.width + diff_enhanced.width
            height = max(baseline.height, current.height, diff_enhanced.height)
            comparison = Image.new('RGB', (width, height))
            comparison.paste(baseline, (0, 0))
            comparison.paste(current, (baseline.width, 0))
            comparison.paste(diff_enhanced, (baseline.width + current.width, 0))
            
            # Add labels
            draw = ImageDraw.Draw(comparison)
            draw.text((10, 10), "Baseline", fill='white')
            draw.text((baseline.width + 10, 10), "Current", fill='white')
            draw.text((baseline.width + current.width + 10, 10), "Diff", fill='white')
            
            comparison.save(output_path)
            result['diff_image'] = os.path.abspath(output_path)
        
        return result
        
    except ImportError:
        # Fallback to simple file comparison
        with open(baseline_path, 'rb') as f1, open(current_path, 'rb') as f2:
            is_match = f1.read() == f2.read()
        
        return {
            'match': is_match,
            'method': 'binary_compare',
            'note': 'Install Pillow for pixel-level comparison: pip install Pillow'
        }


def main():
    parser = argparse.ArgumentParser(description='Compare screenshots for visual regression')
    parser.add_argument('baseline', help='Baseline image path')
    parser.add_argument('current', help='Current image path')
    parser.add_argument('--threshold', '-t', type=float, default=0.01,
                        help='Acceptable difference ratio (default: 0.01 = 1%%)')
    parser.add_argument('--output', '-o', help='Save diff image to path')
    parser.add_argument('--format', '-f', choices=['json', 'text'], default='json')
    
    args = parser.parse_args()
    
    result = compare_images(
        baseline_path=args.baseline,
        current_path=args.current,
        threshold=args.threshold,
        output_path=args.output
    )
    
    if 'error' in result and not result.get('match', True):
        if args.format == 'json':
            output_json(result, success=False)
        else:
            print(f"✗ Error: {result['error']}")
        sys.exit(1)
    
    if args.format == 'json':
        output_json(result, success=True)
    else:
        if result['match']:
            print(f"✓ MATCH - Images are identical (diff: {result.get('diff_ratio', 0)*100:.2f}%)")
        else:
            print(f"✗ MISMATCH - Images differ by {result.get('diff_ratio', 0)*100:.2f}%")
            print(f"  Threshold: {result.get('threshold', 0)*100:.2f}%")
            print(f"  Different pixels: {result.get('diff_pixels', 'N/A')}")
            if 'diff_image' in result:
                print(f"  Diff saved to: {result['diff_image']}")
            sys.exit(1)


if __name__ == '__main__':
    main()
