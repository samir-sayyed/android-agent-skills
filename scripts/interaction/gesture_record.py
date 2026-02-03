#!/usr/bin/env python3
"""
Record and replay touch gestures on Android devices.
Uses sendevent for precise gesture recording and replay.

Usage:
  python gesture_record.py --record gesture.json --duration 5
  python gesture_record.py --replay gesture.json
"""

import argparse
import sys
import os
import json
import time
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources'))
from common import (
    output_json, output_error, get_device_udid,
    run_shell_command, run_adb_command, get_screen_size,
    ADBError
)


def find_touch_device(udid: str = None) -> str:
    """Find the touch input device path."""
    try:
        result = run_shell_command('getevent -pl', udid=udid, check=False)
        lines = result.stdout.split('\n')
        
        current_device = None
        for line in lines:
            if line.startswith('add device'):
                match = re.search(r'(/dev/input/event\d+)', line)
                if match:
                    current_device = match.group(1)
            elif 'ABS_MT_POSITION_X' in line or 'ABS_MT_TOUCH' in line:
                if current_device:
                    return current_device
        
        # Fallback to common paths
        for i in range(10):
            device = f'/dev/input/event{i}'
            result = run_shell_command(f'getevent -pl {device}', udid=udid, check=False)
            if 'ABS_MT' in result.stdout:
                return device
        
        return '/dev/input/event1'  # Default fallback
    except:
        return '/dev/input/event1'


def record_gesture(
    udid: str = None,
    output_file: str = "gesture.json",
    duration: float = 5.0
) -> dict:
    """
    Record touch gestures from device.
    
    Args:
        udid: Target device UDID
        output_file: Path to save gesture recording
        duration: Recording duration in seconds
    
    Returns:
        Result dict
    """
    try:
        udid = get_device_udid(udid)
    except ADBError as e:
        return {'success': False, 'error': str(e)}
    
    try:
        device = find_touch_device(udid)
        screen_width, screen_height = get_screen_size(udid)
        
        # Start recording with timeout
        print(f"Recording gestures for {duration} seconds...")
        print("Perform your gesture on the device now!")
        
        # Use timeout to limit recording
        result = run_adb_command(
            ['shell', f'timeout {duration} getevent -t {device}'],
            udid=udid,
            check=False,
            timeout=int(duration) + 5
        )
        
        # Parse events
        events = []
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            
            # Parse getevent output: [ timestamp] type code value
            match = re.match(r'\[\s*([\d.]+)\]\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)', line)
            if match:
                timestamp = float(match.group(1))
                etype = int(match.group(2), 16)
                ecode = int(match.group(3), 16)
                evalue = int(match.group(4), 16)
                
                events.append({
                    'time': timestamp,
                    'type': etype,
                    'code': ecode,
                    'value': evalue
                })
        
        if not events:
            return {
                'success': False,
                'error': 'No touch events recorded. Make sure to touch the screen during recording.'
            }
        
        # Normalize timestamps
        start_time = events[0]['time']
        for event in events:
            event['time'] = event['time'] - start_time
        
        # Save recording
        recording = {
            'device': device,
            'screen_size': [screen_width, screen_height],
            'duration': events[-1]['time'] if events else 0,
            'event_count': len(events),
            'events': events
        }
        
        with open(output_file, 'w') as f:
            json.dump(recording, f, indent=2)
        
        return {
            'success': True,
            'file': output_file,
            'event_count': len(events),
            'duration': recording['duration']
        }
        
    except ADBError as e:
        return {'success': False, 'error': str(e)}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def replay_gesture(
    udid: str = None,
    input_file: str = "gesture.json",
    speed: float = 1.0
) -> dict:
    """
    Replay recorded touch gestures.
    
    Args:
        udid: Target device UDID
        input_file: Path to gesture recording
        speed: Playback speed multiplier (1.0 = normal)
    
    Returns:
        Result dict
    """
    try:
        udid = get_device_udid(udid)
    except ADBError as e:
        return {'success': False, 'error': str(e)}
    
    try:
        # Load recording
        with open(input_file, 'r') as f:
            recording = json.load(f)
        
        device = recording['device']
        events = recording['events']
        
        if not events:
            return {'success': False, 'error': 'No events in recording'}
        
        # Build sendevent commands
        commands = []
        last_time = 0
        
        for event in events:
            delay = (event['time'] - last_time) / speed
            if delay > 0.001:  # Skip tiny delays
                commands.append(f'sleep {delay:.3f}')
            
            cmd = f"sendevent {device} {event['type']} {event['code']} {event['value']}"
            commands.append(cmd)
            last_time = event['time']
        
        # Execute as a single shell script for better timing
        script = ' && '.join(commands)
        
        print(f"Replaying {len(events)} events...")
        run_shell_command(script, udid=udid, check=False)
        
        return {
            'success': True,
            'events_replayed': len(events),
            'duration': recording['duration'] / speed
        }
        
    except FileNotFoundError:
        return {'success': False, 'error': f'Recording file not found: {input_file}'}
    except ADBError as e:
        return {'success': False, 'error': str(e)}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def simple_gesture(
    udid: str = None,
    gesture_type: str = "swipe",
    direction: str = None,
    x1: int = None, y1: int = None,
    x2: int = None, y2: int = None,
    duration_ms: int = 300
) -> dict:
    """
    Perform simple predefined gestures.
    
    Args:
        udid: Target device UDID
        gesture_type: Type of gesture (swipe, tap, double_tap, long_press)
        direction: Direction for swipe (up, down, left, right)
        x1, y1: Start coordinates
        x2, y2: End coordinates
        duration_ms: Duration of gesture
    
    Returns:
        Result dict
    """
    try:
        udid = get_device_udid(udid)
        width, height = get_screen_size(udid)
    except ADBError as e:
        return {'success': False, 'error': str(e)}
    
    try:
        center_x, center_y = width // 2, height // 2
        
        if gesture_type == 'swipe':
            if direction:
                # Calculate swipe coordinates based on direction
                swipe_distance = min(width, height) // 3
                if direction == 'up':
                    x1, y1 = center_x, center_y + swipe_distance
                    x2, y2 = center_x, center_y - swipe_distance
                elif direction == 'down':
                    x1, y1 = center_x, center_y - swipe_distance
                    x2, y2 = center_x, center_y + swipe_distance
                elif direction == 'left':
                    x1, y1 = center_x + swipe_distance, center_y
                    x2, y2 = center_x - swipe_distance, center_y
                elif direction == 'right':
                    x1, y1 = center_x - swipe_distance, center_y
                    x2, y2 = center_x + swipe_distance, center_y
            
            run_shell_command(f'input swipe {x1} {y1} {x2} {y2} {duration_ms}', udid=udid)
            
        elif gesture_type == 'tap':
            x = x1 or center_x
            y = y1 or center_y
            run_shell_command(f'input tap {x} {y}', udid=udid)
            
        elif gesture_type == 'double_tap':
            x = x1 or center_x
            y = y1 or center_y
            run_shell_command(f'input tap {x} {y} && sleep 0.1 && input tap {x} {y}', udid=udid)
            
        elif gesture_type == 'long_press':
            x = x1 or center_x
            y = y1 or center_y
            run_shell_command(f'input swipe {x} {y} {x} {y} {duration_ms}', udid=udid)
        
        return {
            'success': True,
            'gesture': gesture_type,
            'direction': direction,
            'coordinates': {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}
        }
        
    except ADBError as e:
        return {'success': False, 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(
        description='Record and replay touch gestures',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Record a gesture for 5 seconds
  python gesture_record.py --record swipe.json --duration 5
  
  # Replay a recorded gesture
  python gesture_record.py --replay swipe.json
  
  # Replay at 2x speed
  python gesture_record.py --replay swipe.json --speed 2.0
  
  # Simple swipe gesture
  python gesture_record.py --swipe up
  python gesture_record.py --swipe left
'''
    )
    
    # Recording/Replay
    parser.add_argument('--record', metavar='FILE',
                       help='Record gestures to file')
    parser.add_argument('--replay', metavar='FILE',
                       help='Replay gestures from file')
    parser.add_argument('--duration', type=float, default=5.0,
                       help='Recording duration in seconds (default: 5)')
    parser.add_argument('--speed', type=float, default=1.0,
                       help='Replay speed multiplier (default: 1.0)')
    
    # Simple gestures
    parser.add_argument('--swipe', choices=['up', 'down', 'left', 'right'],
                       help='Perform simple swipe gesture')
    parser.add_argument('--tap', nargs=2, type=int, metavar=('X', 'Y'),
                       help='Tap at coordinates')
    parser.add_argument('--double-tap', nargs=2, type=int, metavar=('X', 'Y'),
                       help='Double tap at coordinates')
    parser.add_argument('--long-press', nargs=2, type=int, metavar=('X', 'Y'),
                       help='Long press at coordinates')
    
    # Common
    parser.add_argument('--udid', '-d', help='Target device UDID')
    parser.add_argument('--format', '-f', choices=['json', 'text'], default='json')
    
    args = parser.parse_args()
    
    # Execute requested action
    if args.record:
        result = record_gesture(
            udid=args.udid,
            output_file=args.record,
            duration=args.duration
        )
    elif args.replay:
        result = replay_gesture(
            udid=args.udid,
            input_file=args.replay,
            speed=args.speed
        )
    elif args.swipe:
        result = simple_gesture(
            udid=args.udid,
            gesture_type='swipe',
            direction=args.swipe
        )
    elif args.tap:
        result = simple_gesture(
            udid=args.udid,
            gesture_type='tap',
            x1=args.tap[0],
            y1=args.tap[1]
        )
    elif args.double_tap:
        result = simple_gesture(
            udid=args.udid,
            gesture_type='double_tap',
            x1=args.double_tap[0],
            y1=args.double_tap[1]
        )
    elif args.long_press:
        result = simple_gesture(
            udid=args.udid,
            gesture_type='long_press',
            x1=args.long_press[0],
            y1=args.long_press[1]
        )
    else:
        parser.error('Specify an action: --record, --replay, --swipe, --tap, --double-tap, or --long-press')
        return
    
    if args.format == 'json':
        output_json(result, success=result.get('success', False))
    else:
        if result.get('success'):
            if args.record:
                print(f"✓ Recorded {result['event_count']} events to {result['file']}")
                print(f"  Duration: {result['duration']:.2f}s")
            elif args.replay:
                print(f"✓ Replayed {result['events_replayed']} events")
                print(f"  Duration: {result['duration']:.2f}s")
            else:
                print(f"✓ Gesture: {result.get('gesture')}")
        else:
            print(f"✗ {result.get('error', 'Gesture failed')}")
            sys.exit(1)


if __name__ == '__main__':
    main()
