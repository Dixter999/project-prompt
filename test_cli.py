#!/usr/bin/env python3
"""
Test script to isolate CLI hanging issue
"""
import os
import sys

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("Testing imports...")

try:
    import typer
    print("✓ typer imported")
except Exception as e:
    print(f"✗ typer failed: {e}")

try:
    from rich.console import Console
    print("✓ rich imported")
except Exception as e:
    print(f"✗ rich failed: {e}")

try:
    from src.utils.enhanced_rules_manager import EnhancedRulesManager
    print("✓ enhanced rules manager imported")
except Exception as e:
    print(f"✗ enhanced rules manager failed: {e}")

try:
    from src.ui.cli import cli
    print("✓ cli imported")
except Exception as e:
    print(f"✗ cli failed: {e}")

print("Creating simple typer app...")

app = typer.Typer()

@app.command()
def test_command():
    """Simple test command"""
    print("Test command executed successfully!")

if __name__ == "__main__":
    print("Starting app...")
    app()
