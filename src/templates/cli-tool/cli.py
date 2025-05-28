#!/usr/bin/env python3
"""
CLI Tool - Main entry point
"""
import argparse
import sys
import os
import logging

from src.commands import (
    analyze_command,
    generate_command,
    validate_command,
    init_command
)

from src.utils.config import load_config
from src.utils.logger import setup_logger

def main():
    """Main entry point for the CLI tool"""
    # Set up logger
    setup_logger()
    logger = logging.getLogger(__name__)
    logger.debug("Starting CLI tool")

    # Create main parser
    parser = argparse.ArgumentParser(
        description='CLI Tool for testing Anthropic markdown generation',
        prog='cli-tool'
    )
    
    # Add common arguments
    parser.add_argument('--config', '-c', type=str, help='Path to config file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--version', action='version', version='%(prog)s 1.1.7')
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Initialize command
    init_parser = subparsers.add_parser('init', help='Initialize a new project')
    init_parser.add_argument('path', type=str, help='Path for new project')
    init_parser.add_argument('--template', '-t', type=str, default='basic', help='Project template to use')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a project or file')
    analyze_parser.add_argument('target', type=str, help='Project or file to analyze')
    analyze_parser.add_argument('--output', '-o', type=str, help='Output file path')
    analyze_parser.add_argument('--format', '-f', choices=['text', 'json', 'markdown'], default='text',
                              help='Output format (default: text)')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate output files')
    generate_parser.add_argument('template', type=str, help='Template to generate from')
    generate_parser.add_argument('--output', '-o', type=str, required=True, help='Output directory')
    generate_parser.add_argument('--vars', '-v', type=str, help='Variables file in JSON format')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate a file or configuration')
    validate_parser.add_argument('target', type=str, help='File to validate')
    validate_parser.add_argument('--schema', '-s', type=str, help='Schema file for validation')
    
    # Parse the arguments
    args = parser.parse_args()
    
    # If no command provided, show help and exit
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Load configuration if provided
    config = None
    if args.config:
        try:
            config = load_config(args.config)
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)
    
    # Set up verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")
    
    # Execute the selected command
    try:
        if args.command == 'init':
            init_command.execute(args, config)
        elif args.command == 'analyze':
            analyze_command.execute(args, config)
        elif args.command == 'generate':
            generate_command.execute(args, config)
        elif args.command == 'validate':
            validate_command.execute(args, config)
        else:
            logger.error(f"Unknown command: {args.command}")
            parser.print_help()
            sys.exit(1)
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
        
    logger.debug("CLI tool completed successfully")

if __name__ == "__main__":
    main()
