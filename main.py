#!/usr/bin/env python3
"""
ProjectPrompt v2.0 - Entry point
"""

import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

def main():
    """Main entry point for CLI"""
    # Import and run CLI directly
    import cli
    cli.main()

if __name__ == '__main__':
    main()
