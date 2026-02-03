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
    tap, input_text, ADBError, wait_for_element, find_by_xpath
)


def navigate(
    udid: str = None,
    find_text: str = None,
    find_id: str = None,
    find_class: str = None,
    find_desc: str = None,
    xpath: str = None,
    fallback_text: str = None,
    fallback_id: str = None,
    fallback_desc: str = None,
    index: int = 0,
    do_tap: bool = False,
    do_long_press: bool = False,
    enter_text: str = None,
    list_matches: bool = False,
    wait_timeout: float = 0,
    poll_interval: float = 0.5,
    retry_count: int = 1
) -> dict:
    """
    Find and interact with UI element with advanced features.
    
    Args:
        udid: Target device UDID
        find_text: Find by text content
        find_id: Find by resource ID
        find_class: Find by class name
        find_desc: Find by content description
        xpath: Find by XPath expression
        fallback_text: Fallback text if primary search fails
        fallback_id: Fallback resource ID if primary search fails
        fallback_desc: Fallback content description if primary search fails
        index: Which match to use (0-indexed)
        do_tap: Tap the element
        do_long_press: Long press the element
        enter_text: Text to enter after finding
        list_matches: Just list all matches
        wait_timeout: Wait up to N seconds for element (0 = no wait)
        poll_interval: Polling interval when waiting
        retry_count: Number of retries for finding element
    
    Returns:
        Navigation result dict
    """
    import time
    
    try:
        udid = get_device_udid(udid)
    except ADBError as e:
        return {'found': False, 'error': str(e)}
    
    # Build search strategies (primary + fallbacks)
    strategies = []
    
    # Primary strategy
    if xpath:
        strategies.append({'type': 'xpath', 'xpath': xpath})
    elif any([find_text, find_id, find_class, find_desc]):
        strategies.append({
            'type': 'standard',
            'text': find_text,
            'resource_id': find_id,
            'class_name': find_class,
            'content_desc': find_desc
        })
    
    # Fallback strategies (self-healing)
    if fallback_text:
        strategies.append({'type': 'standard', 'text': fallback_text})
    if fallback_id:
        strategies.append({'type': 'standard', 'resource_id': fallback_id})
    if fallback_desc:
        strategies.append({'type': 'standard', 'content_desc': fallback_desc})
    
    if not strategies:
        return {
            'found': False,
            'error': 'No search criteria provided. Use --find-text, --find-id, --find-class, --find-desc, or --xpath'
        }
    
    # Wait logic
    if wait_timeout > 0:
        # Use wait_for_element for primary strategy only
        primary = strategies[0]
        if primary['type'] == 'standard':
            element = wait_for_element(
                udid=udid,
                text=primary.get('text'),
                resource_id=primary.get('resource_id'),
                class_name=primary.get('class_name'),
                content_desc=primary.get('content_desc'),
                timeout=wait_timeout,
                poll_interval=poll_interval
            )
            if element:
                return _perform_actions(element, udid, do_tap, do_long_press, enter_text, 1, index, 'wait')
    
    # Retry logic with fallback strategies
    last_error = None
    for attempt in range(retry_count):
        for strategy_idx, strategy in enumerate(strategies):
            try:
                xml = get_ui_hierarchy(udid)
                all_elements = parse_ui_hierarchy(xml)
                
                if strategy['type'] == 'xpath':
                    matches = find_by_xpath(xml, strategy['xpath'])
                else:
                    matches = find_elements(
                        all_elements,
                        text=strategy.get('text'),
                        resource_id=strategy.get('resource_id'),
                        class_name=strategy.get('class_name'),
                        content_desc=strategy.get('content_desc')
                    )
                
                if matches:
                    # If listing matches
                    if list_matches:
                        return {
                            'found': True,
                            'match_count': len(matches),
                            'matches': [m.to_dict() for m in matches[:10]],
                            'strategy_used': strategy_idx,
                            'attempt': attempt + 1
                        }
                    
                    # Get specific match by index
                    if index >= len(matches):
                        last_error = f"Index {index} out of range. Found {len(matches)} matches."
                        continue
                    
                    element = matches[index]
                    strategy_name = 'primary' if strategy_idx == 0 else f'fallback_{strategy_idx}'
                    return _perform_actions(element, udid, do_tap, do_long_press, enter_text, 
                                          len(matches), index, strategy_name, attempt + 1)
                
            except ADBError as e:
                last_error = str(e)
        
        # Small delay before retry
        if attempt < retry_count - 1:
            time.sleep(0.5)
    
    # Build error message
    criteria = []
    if find_text: criteria.append(f"text='{find_text}'")
    if find_id: criteria.append(f"id='{find_id}'")
    if find_class: criteria.append(f"class='{find_class}'")
    if find_desc: criteria.append(f"desc='{find_desc}'")
    if xpath: criteria.append(f"xpath='{xpath}'")
    
    return {
        'found': False,
        'error': last_error or f"No element found matching: {', '.join(criteria)}",
        'strategies_tried': len(strategies),
        'retry_attempts': retry_count
    }


def _perform_actions(element, udid, do_tap, do_long_press, enter_text, 
                     match_count, used_index, strategy_used, attempt=1):
    """Helper to perform actions on found element."""
    result = {
        'found': True,
        'element': element.to_dict(),
        'match_count': match_count,
        'used_index': used_index,
        'strategy_used': strategy_used,
        'attempt': attempt,
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


def main():
    parser = argparse.ArgumentParser(
        description='Navigate and interact with UI elements',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Basic find and tap
  python navigator.py --find-text "Login" --tap
  
  # Wait for element to appear (up to 10 seconds)
  python navigator.py --find-text "Loading Complete" --wait-timeout 10 --tap
  
  # XPath query
  python navigator.py --xpath "//android.widget.Button[@text='Submit']" --tap
  
  # Self-healing with fallback locators
  python navigator.py --find-text "Login" --fallback-id "submit_btn" --tap
  
  # Retry on failure
  python navigator.py --find-id "dynamic_element" --retry-count 3 --tap
'''
    )
    
    # Search criteria
    parser.add_argument('--find-text', '-t', help='Find by text content')
    parser.add_argument('--find-id', '-i', help='Find by resource ID')
    parser.add_argument('--find-class', '-c', help='Find by class name (e.g., EditText, Button)')
    parser.add_argument('--find-desc', help='Find by content description')
    parser.add_argument('--xpath', '-x', help='Find by XPath expression')
    parser.add_argument('--index', type=int, default=0, help='Which match to use (0-indexed)')
    
    # Self-healing fallbacks
    parser.add_argument('--fallback-text', help='Fallback: find by text if primary fails')
    parser.add_argument('--fallback-id', help='Fallback: find by ID if primary fails')
    parser.add_argument('--fallback-desc', help='Fallback: find by description if primary fails')
    
    # Wait and retry
    parser.add_argument('--wait-timeout', type=float, default=0,
                       help='Wait up to N seconds for element to appear (default: 0 = no wait)')
    parser.add_argument('--poll-interval', type=float, default=0.5,
                       help='Polling interval in seconds when waiting (default: 0.5)')
    parser.add_argument('--retry-count', type=int, default=1,
                       help='Number of retry attempts (default: 1 = no retry)')
    
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
    if not any([args.find_text, args.find_id, args.find_class, args.find_desc, args.xpath]):
        parser.error('At least one search criteria required: --find-text, --find-id, --find-class, --find-desc, or --xpath')
    
    result = navigate(
        udid=args.udid,
        find_text=args.find_text,
        find_id=args.find_id,
        find_class=args.find_class,
        find_desc=args.find_desc,
        xpath=args.xpath,
        fallback_text=args.fallback_text,
        fallback_id=args.fallback_id,
        fallback_desc=args.fallback_desc,
        index=args.index,
        do_tap=args.tap,
        do_long_press=args.long_press,
        enter_text=args.enter_text,
        list_matches=args.list,
        wait_timeout=args.wait_timeout,
        poll_interval=args.poll_interval,
        retry_count=args.retry_count
    )
    
    if args.format == 'json':
        output_json(result, success=result.get('found', False))
    else:
        if result.get('found'):
            elem = result.get('element', {})
            strategy = result.get('strategy_used', 'primary')
            print(f"✓ Found element: {elem.get('text') or elem.get('resource_id') or elem.get('class_name')}")
            print(f"  Center: {elem.get('center')}")
            print(f"  Strategy: {strategy}")
            if result.get('actions'):
                print(f"  Actions: {', '.join(result['actions'])}")
        else:
            print(f"✗ {result.get('error', 'Element not found')}")
            sys.exit(1)


if __name__ == '__main__':
    main()
