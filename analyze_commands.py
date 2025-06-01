#!/usr/bin/env python3
"""
Script to analyze available commands in ProjectPrompt
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def extract_commands():
    """Extract all available commands from the CLI"""
    try:
        from src.main import app, docs_app, ai_app, subscription_app, update_app, premium_app, telemetry_app
        from src.commands.rules_commands import rules_app
        
        commands = {
            'main': [],
            'docs': [],
            'ai': [],
            'subscription': [],
            'update': [],
            'premium': [],
            'telemetry': [],
            'rules': []
        }
        
        # Main app commands
        for cmd_name, cmd in app.commands.items():
            commands['main'].append(cmd_name)
        
        # Subapp commands
        for cmd_name, cmd in docs_app.commands.items():
            commands['docs'].append(f"docs {cmd_name}")
            
        for cmd_name, cmd in ai_app.commands.items():
            commands['ai'].append(f"ai {cmd_name}")
            
        for cmd_name, cmd in subscription_app.commands.items():
            commands['subscription'].append(f"subscription {cmd_name}")
            
        for cmd_name, cmd in update_app.commands.items():
            commands['update'].append(f"update {cmd_name}")
            
        for cmd_name, cmd in premium_app.commands.items():
            commands['premium'].append(f"premium {cmd_name}")
            
        for cmd_name, cmd in telemetry_app.commands.items():
            commands['telemetry'].append(f"telemetry {cmd_name}")
            
        for cmd_name, cmd in rules_app.commands.items():
            commands['rules'].append(f"rules {cmd_name}")
        
        return commands
        
    except Exception as e:
        print(f"Error extracting commands: {e}")
        return None

if __name__ == "__main__":
    commands = extract_commands()
    if commands:
        print("=== ProjectPrompt Available Commands ===")
        for category, cmd_list in commands.items():
            if cmd_list:
                print(f"\n{category.upper()}:")
                for cmd in sorted(cmd_list):
                    print(f"  - {cmd}")
        
        # Count total commands
        total = sum(len(cmd_list) for cmd_list in commands.values())
        print(f"\nTotal commands: {total}")
    else:
        print("Could not extract commands due to import errors")
