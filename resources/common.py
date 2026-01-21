#!/usr/bin/env python3
"""
Common utilities for Android automation scripts.
Provides shared functionality for ADB operations, UI parsing, and output formatting.
"""

import subprocess
import json
import sys
import os
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, asdict
import re


@dataclass
class UIElement:
    """Represents a UI element from the accessibility tree."""
    resource_id: str
    class_name: str
    text: str
    content_desc: str
    bounds: Tuple[int, int, int, int]  # left, top, right, bottom
    clickable: bool
    focusable: bool
    enabled: bool
    index: int = 0

    @property
    def center(self) -> Tuple[int, int]:
        """Get center coordinates of the element."""
        return (
            (self.bounds[0] + self.bounds[2]) // 2,
            (self.bounds[1] + self.bounds[3]) // 2
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = asdict(self)
        d['center'] = self.center
        return d


class ADBError(Exception):
    """Custom exception for ADB errors."""
    pass


def get_connected_devices() -> List[Dict[str, str]]:
    """Get list of connected Android devices/emulators."""
    result = run_adb_command(['devices', '-l'], check=False)
    devices = []
    
    for line in result.stdout.strip().split('\n')[1:]:
        if line.strip() and 'device' in line:
            parts = line.split()
            udid = parts[0]
            state = parts[1] if len(parts) > 1 else 'unknown'
            
            # Parse device info
            info = {'udid': udid, 'state': state}
            for part in parts[2:]:
                if ':' in part:
                    key, value = part.split(':', 1)
                    info[key] = value
            
            devices.append(info)
    
    return devices


def get_device_udid(specified_udid: Optional[str] = None) -> str:
    """
    Get device UDID. Uses specified UDID if provided,
    otherwise auto-detects if only one device is connected.
    """
    if specified_udid:
        return specified_udid
    
    devices = get_connected_devices()
    
    if not devices:
        raise ADBError("No Android devices connected. Run 'adb devices' to check.")
    
    if len(devices) > 1:
        device_list = '\n'.join([f"  - {d['udid']}" for d in devices])
        raise ADBError(f"Multiple devices connected. Specify --udid:\n{device_list}")
    
    return devices[0]['udid']


def run_adb_command(
    args: List[str],
    udid: Optional[str] = None,
    check: bool = True,
    timeout: int = 30
) -> subprocess.CompletedProcess:
    """
    Execute an ADB command with optional device targeting.
    
    Args:
        args: ADB command arguments
        udid: Target device UDID (optional)
        check: Whether to raise on non-zero exit
        timeout: Command timeout in seconds
    
    Returns:
        CompletedProcess result
    
    Raises:
        ADBError: If command fails and check=True
    """
    cmd = ['adb']
    
    if udid:
        cmd.extend(['-s', udid])
    
    cmd.extend(args)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if check and result.returncode != 0:
            raise ADBError(f"ADB command failed: {result.stderr.strip()}")
        
        return result
        
    except subprocess.TimeoutExpired:
        raise ADBError(f"ADB command timed out after {timeout}s: {' '.join(cmd)}")
    except FileNotFoundError:
        raise ADBError("ADB not found. Install Android SDK Platform Tools.")


def run_shell_command(
    command: str,
    udid: Optional[str] = None,
    check: bool = True
) -> subprocess.CompletedProcess:
    """Execute a shell command on the device."""
    return run_adb_command(['shell', command], udid=udid, check=check)


def get_ui_hierarchy(udid: Optional[str] = None) -> str:
    """
    Dump and retrieve the UI hierarchy XML from the device.
    
    Returns:
        XML string of the UI hierarchy
    """
    device_path = '/data/local/tmp/window_dump.xml'
    
    # Dump UI hierarchy
    run_shell_command(f'uiautomator dump {device_path}', udid=udid)
    
    # Pull the file
    result = run_adb_command(['shell', 'cat', device_path], udid=udid)
    
    # Clean up
    run_shell_command(f'rm {device_path}', udid=udid, check=False)
    
    return result.stdout


def parse_bounds(bounds_str: str) -> Tuple[int, int, int, int]:
    """Parse bounds string '[left,top][right,bottom]' to tuple."""
    match = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds_str)
    if match:
        return tuple(int(x) for x in match.groups())
    return (0, 0, 0, 0)


def parse_ui_hierarchy(xml_string: str) -> List[UIElement]:
    """
    Parse UI hierarchy XML into list of UIElement objects.
    
    Args:
        xml_string: XML dump from uiautomator
    
    Returns:
        List of UIElement objects
    """
    elements = []
    
    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError:
        return elements
    
    index = 0
    for node in root.iter('node'):
        bounds = parse_bounds(node.get('bounds', '[0,0][0,0]'))
        
        element = UIElement(
            resource_id=node.get('resource-id', ''),
            class_name=node.get('class', ''),
            text=node.get('text', ''),
            content_desc=node.get('content-desc', ''),
            bounds=bounds,
            clickable=node.get('clickable', 'false') == 'true',
            focusable=node.get('focusable', 'false') == 'true',
            enabled=node.get('enabled', 'true') == 'true',
            index=index
        )
        elements.append(element)
        index += 1
    
    return elements


def find_element(
    elements: List[UIElement],
    text: Optional[str] = None,
    resource_id: Optional[str] = None,
    class_name: Optional[str] = None,
    content_desc: Optional[str] = None,
    index: int = 0
) -> Optional[UIElement]:
    """
    Find a UI element by various criteria.
    
    Args:
        elements: List of UIElement objects
        text: Match by text content
        resource_id: Match by resource ID (partial match)
        class_name: Match by class name (partial match)
        content_desc: Match by content description
        index: Which match to return if multiple found
    
    Returns:
        Matching UIElement or None
    """
    matches = []
    
    for element in elements:
        if text and text.lower() not in element.text.lower():
            continue
        if resource_id and resource_id.lower() not in element.resource_id.lower():
            continue
        if class_name and class_name.lower() not in element.class_name.lower():
            continue
        if content_desc and content_desc.lower() not in element.content_desc.lower():
            continue
        
        matches.append(element)
    
    if matches and index < len(matches):
        return matches[index]
    
    return None


def find_elements(
    elements: List[UIElement],
    text: Optional[str] = None,
    resource_id: Optional[str] = None,
    class_name: Optional[str] = None,
    content_desc: Optional[str] = None,
    clickable_only: bool = False
) -> List[UIElement]:
    """
    Find all UI elements matching criteria.
    
    Returns:
        List of matching UIElement objects
    """
    matches = []
    
    for element in elements:
        if clickable_only and not element.clickable:
            continue
        if text and text.lower() not in element.text.lower():
            continue
        if resource_id and resource_id.lower() not in element.resource_id.lower():
            continue
        if class_name and class_name.lower() not in element.class_name.lower():
            continue
        if content_desc and content_desc.lower() not in element.content_desc.lower():
            continue
        
        matches.append(element)
    
    return matches


def tap(x: int, y: int, udid: Optional[str] = None) -> None:
    """Tap at coordinates."""
    run_shell_command(f'input tap {x} {y}', udid=udid)


def swipe(
    x1: int, y1: int, x2: int, y2: int,
    duration_ms: int = 300,
    udid: Optional[str] = None
) -> None:
    """Swipe from (x1,y1) to (x2,y2)."""
    run_shell_command(f'input swipe {x1} {y1} {x2} {y2} {duration_ms}', udid=udid)


def input_text(text: str, udid: Optional[str] = None) -> None:
    """Type text (escapes special characters)."""
    # Escape special shell characters
    escaped = text.replace(' ', '%s').replace("'", "\\'").replace('"', '\\"')
    run_shell_command(f"input text '{escaped}'", udid=udid)


def press_key(keycode: str, udid: Optional[str] = None) -> None:
    """Press a key by keycode name or number."""
    # Common key mappings
    key_map = {
        'HOME': 3,
        'BACK': 4,
        'MENU': 82,
        'ENTER': 66,
        'TAB': 61,
        'ESCAPE': 111,
        'VOLUME_UP': 24,
        'VOLUME_DOWN': 25,
        'POWER': 26,
        'CAMERA': 27,
        'DELETE': 67,
        'SEARCH': 84,
    }
    
    if keycode.upper() in key_map:
        code = key_map[keycode.upper()]
    elif keycode.isdigit():
        code = int(keycode)
    else:
        code = keycode
    
    run_shell_command(f'input keyevent {code}', udid=udid)


def get_screen_size(udid: Optional[str] = None) -> Tuple[int, int]:
    """Get device screen size (width, height)."""
    result = run_shell_command('wm size', udid=udid)
    match = re.search(r'(\d+)x(\d+)', result.stdout)
    if match:
        return int(match.group(1)), int(match.group(2))
    return (1080, 1920)  # Default


def output_json(data: Any, success: bool = True, error: Optional[str] = None) -> None:
    """Output result as JSON to stdout."""
    result = {
        'success': success,
        'data': data,
        'error': error
    }
    print(json.dumps(result, indent=2, default=str))


def output_error(message: str, exit_code: int = 1) -> None:
    """Output error as JSON and exit."""
    output_json(None, success=False, error=message)
    sys.exit(exit_code)


def setup_argparse_common(parser) -> None:
    """Add common arguments to argument parser."""
    parser.add_argument(
        '--udid', '-d',
        help='Target device UDID (auto-detected if one device connected)'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['json', 'text'],
        default='json',
        help='Output format (default: json)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
