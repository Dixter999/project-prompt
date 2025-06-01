#!/usr/bin/env python3
"""
Simplified CLI test to isolate the hanging issue
"""

print("Testing CLI class creation...")

# Import everything that CLI uses
import os
import sys
import platform
import shutil
import time
from typing import List, Optional, Dict, Any, Callable, Union, Tuple

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.layout import Layout
from rich.live import Live

from src import __version__
from src.utils import logger, LogLevel, set_level
from src.utils.config import config_manager

print("All imports successful!")

# Create the get_console function
_console = None

def get_console() -> Console:
    """Get console with theme applied, lazy initialization to avoid circular imports."""
    global _console
    if _console is None:
        try:
            from src.ui.themes import apply_theme_to_console
            _console = apply_theme_to_console(Console())
        except ImportError:
            # Fallback to basic console if themes not available
            _console = Console()
    return _console

print("Console function created!")

# Create simplified CLI class
class CLI:
    @staticmethod
    def print_header(title: str = "ProjectPrompt"):
        """Muestra un header con el título especificado."""
        get_console().print(f"\n[bold blue]{title}[/bold blue] [cyan]v{__version__}[/cyan]")

print("CLI class created!")

# Create instance
cli = CLI()

print("CLI instance created!")

# Test a method
cli.print_header()

print("CLI test completed successfully!")
