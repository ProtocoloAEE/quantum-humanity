#!/usr/bin/env python3
"""
AEE Protocol - Command Line Interface
Usage: python main.py --hash <file> --user <id> [--debug]
       python main.py --verify <file> --anchor <hash>
"""

import argparse
import json
import sys
from aee import AEEProtocol


def format_output(data: dict, debug: bool = False) -> str:
    """Format output for console display"""
    
    if debug:
        # Debug output with metadata
        lines = [
            "=== AEE DEBUG TRACE ===",
            f"Filename   : {data['metadata'].get('filename', 'N/A')}",
            f"Filesize   : {data['metadata'].get('filesize', 'N/A')} bytes",
            f"User       : {data['metadata'].get('user', 'N/A')}",
            f"SHA-256    : {data['anchor']}",
            f"Metadata   : {data['metadata']}",
            "=======================",
            data['anchor']
        ]
    else:
        # Clean output for production
        lines = [
            "════════════════════════════════════════════",
            "AEE - Integrity Audit Test",
            "════════════════════════════════════════════",
            f"File  : {data['metadata'].get('filename', 'N/A')}",
            f"User  : {data['metadata'].get('user', 'N/A')}",
            "",
            "✔ INTEGRITY ANCHOR GENERATED",
            "════════════════════════════════════════════",
            f"Anchor: {data['anchor']}",
            f"Status: {data['status']}",
            "════════════════════════════════════════════"
        ]
    
    return "\n".join(lines)


def format_verify_output(data: dict) -> str:
    """Format verification output"""
    
    status_symbol = "✔" if data['verified'] else "✖"
    status_text = "VERIFIED" if data['verified'] else "MISMATCH"
    
    lines = [
        "════════════════════════════════════════════",
        "AEE - Integrity Verification",
        "════════════════════════════════════════════",
        f"{status_symbol} Status: {status_text}",
        "",
        f"Expected Anchor: {data['expected_anchor']}",
        f"Current Anchor : {data['current_anchor']}",
        "",
        f"Timestamp: {data['timestamp']}",
        "════════════════════════════════════════════"
    ]
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="AEE Protocol - Deterministic Integrity Anchor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate integrity anchor
  python main.py --hash dataset.csv --user "audit-test"
  
  # Generate with debug output
  python main.py --hash dataset.csv --user "audit-test" --debug
  
  # Verify file integrity
  python main.py --verify dataset.csv --anchor 3f7b2a1c9e4d8f6a...
        """
    )
    
    # Mode selection
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        '--hash',
        type=str,
        metavar='FILE',
        help='Generate integrity anchor for file'
    )
    mode.add_argument(
        '--verify',
        type=str,
        metavar='FILE',
        help='Verify file against anchor'
    )
    
    # Arguments
    parser.add_argument(
        '--user',
        type=str,
        default='system',
        help='User identifier (default: system)'
    )
    parser.add_argument(
        '--anchor',
        type=str,
        help='Anchor hash for verification (required with --verify)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Show debug trace information'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON (for scripting)'
    )
    
    args = parser.parse_args()
    
    try:
        protocol = AEEProtocol()
        
        if args.hash:
            # Generate mode
            result = protocol.generate(args.hash, user=args.user)
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(format_output(result, debug=args.debug))
            
            return 0
        
        elif args.verify:
            # Verify mode
            if not args.anchor:
                print("Error: --anchor is required for --verify mode", file=sys.stderr)
                return 1
            
            result = protocol.verify(args.verify, args.anchor)
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(format_verify_output(result))
            
            return 0 if result['verified'] else 1
    
    except FileNotFoundError as e:
        print(f"AEE Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"AEE Error: {e}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())