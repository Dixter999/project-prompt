#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Interactive progress tracker for group analysis operations.

This module provides Rich-based progress indicators, status displays,
and interactive elements for the analyze-group command.
"""

import time
from typing import Dict, List, Optional, Any, Callable
from contextlib import contextmanager

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm, Prompt
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from rich.text import Text

from src.utils.logger import get_logger
from src.utils.token_counter import TokenEstimate

logger = get_logger()


class InteractiveGroupAnalyzer:
    """Interactive progress tracker and UI for group analysis."""
    
    def __init__(self, console: Optional[Console] = None):
        """
        Initialize interactive analyzer.
        
        Args:
            console: Rich console instance (optional)
        """
        self.console = console or Console()
        self.current_progress = None
        self.current_task = None
        
    def show_cost_confirmation(self, estimate: TokenEstimate, group_name: str) -> bool:
        """
        Show cost estimate and ask for user confirmation.
        
        Args:
            estimate: Token and cost estimate
            group_name: Name of the group being analyzed
            
        Returns:
            True if user confirms, False otherwise
        """
        # Create cost breakdown table
        cost_table = Table(title="💰 Cost Breakdown", box=None)
        cost_table.add_column("Item", style="bold")
        cost_table.add_column("Tokens", justify="right")
        cost_table.add_column("Cost (USD)", justify="right")
        
        cost_table.add_row(
            "Input tokens",
            f"{estimate.input_tokens:,}",
            f"${estimate.input_cost:.4f}"
        )
        cost_table.add_row(
            "Output tokens (est.)",
            f"{estimate.estimated_output_tokens:,}",
            f"${estimate.output_cost:.4f}"
        )
        cost_table.add_row(
            "[bold]Total[/bold]",
            f"[bold]{estimate.total_tokens:,}[/bold]",
            f"[bold]${estimate.total_cost:.4f}[/bold]"
        )
        
        # Create info panel
        info_content = f"""
🎯 **Group**: {group_name}
🤖 **Model**: {estimate.model}
📊 **Analysis scope**: Files and code quality review

The analysis will send your code to Anthropic Claude for AI-powered insights.
        """.strip()
        
        info_panel = Panel(
            info_content,
            title="🔍 Analysis Details",
            border_style="blue"
        )
        
        # Display information
        self.console.print()
        self.console.print(info_panel)
        self.console.print()
        self.console.print(cost_table)
        self.console.print()
        
        # Show warning for high costs
        if estimate.total_cost > 0.05:  # $0.05 threshold
            warning_text = Text("⚠️  High cost detected!", style="bold yellow")
            if estimate.total_cost > 0.20:  # $0.20 threshold
                warning_text = Text("🚨 Very high cost detected!", style="bold red")
            
            warning_panel = Panel(
                warning_text,
                border_style="yellow"
            )
            self.console.print(warning_panel)
            self.console.print()
        
        # Ask for confirmation
        return Confirm.ask(
            "[bold blue]💡 Proceed with AI analysis?[/bold blue]",
            default=True
        )
    
    def show_group_selection(self, groups: List[Dict[str, Any]], project_path: str) -> Optional[Dict[str, Any]]:
        """
        Display available groups and let user select one.
        
        Args:
            groups: List of available groups
            project_path: Path to the project (for display purposes)
            
        Returns:
            Selected group object or None if cancelled
        """
        if not groups:
            self.console.print("[red]❌ No functional groups found[/red]")
            return None
        
        # Display project info
        import os
        self.console.print(f"\n📁 Project: [bold]{os.path.basename(project_path)}[/bold]")
        self.console.print(f"📊 Total groups: [bold]{len(groups)}[/bold]")
        
        # Create groups table
        groups_table = Table(title="📋 Available Functional Groups")
        groups_table.add_column("#", style="dim", width=3)
        groups_table.add_column("Group Name", style="bold")
        groups_table.add_column("Type", style="cyan")
        groups_table.add_column("Files", justify="right", style="yellow")
        groups_table.add_column("Importance", justify="right", style="green")
        
        # Add groups to table
        for i, group in enumerate(groups, 1):
            name = group.get('name', 'Unknown')
            group_type = group.get('type', 'unknown')
            size = group.get('size', 0)
            importance = group.get('total_importance', 0)
            
            # Truncate long names
            display_name = name[:50] + "..." if len(name) > 50 else name
            
            groups_table.add_row(
                str(i),
                display_name,
                group_type,
                str(size),
                f"{importance:.1f}"
            )
        
        self.console.print()
        self.console.print(groups_table)
        self.console.print()
        
        # Get user selection
        while True:
            try:
                choice = Prompt.ask(
                    "[bold blue]Select group number (1-{}) or enter group name, or 'q' to quit[/bold blue]".format(len(groups)),
                    default="q"
                )
                
                # Check for quit
                if choice.lower() in ['q', 'quit', 'exit']:
                    return None
                
                # Check if it's a number
                if choice.isdigit():
                    index = int(choice) - 1
                    if 0 <= index < len(groups):
                        return groups[index]
                    else:
                        self.console.print("[red]❌ Invalid group number[/red]")
                        continue
                
                # Check if it's a group name
                for group in groups:
                    if choice.lower() in group.get('name', '').lower():
                        return group
                
                self.console.print("[red]❌ Group not found. Try again or 'q' to quit[/red]")
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]⚠️  Analysis cancelled[/yellow]")
                return None
    
    @contextmanager
    def progress_context(self, description: str, total: Optional[int] = None):
        """
        Context manager for progress tracking.
        
        Args:
            description: Description of the operation
            total: Total number of steps (optional for indeterminate progress)
        """
        if total is not None:
            # Determinate progress with bar
            progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                console=self.console
            )
        else:
            # Indeterminate progress with spinner
            progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                TimeElapsedColumn(),
                console=self.console
            )
        
        self.current_progress = progress
        
        try:
            with progress:
                if total is not None:
                    task = progress.add_task(description, total=total)
                else:
                    task = progress.add_task(description, total=None)
                
                self.current_task = task
                yield ProgressTracker(progress, task)
        finally:
            self.current_progress = None
            self.current_task = None
    
    def show_analysis_results(self, results: Dict[str, Any], cost_estimate=None):
        """
        Display analysis results in a formatted way.
        
        Args:
            results: Analysis results
        """
        if not results.get('success'):
            error_panel = Panel(
                f"[red]❌ Analysis failed: {results.get('error', 'Unknown error')}[/red]",
                title="Error",
                border_style="red"
            )
            self.console.print(error_panel)
            return
        
        # Success header
        success_panel = Panel(
            "[green]✅ Analysis completed successfully![/green]",
            title="🎉 Results",
            border_style="green"
        )
        self.console.print()
        self.console.print(success_panel)
        
        # Results summary
        summary_table = Table(title="📊 Analysis Summary", box=None)
        summary_table.add_column("Metric", style="bold")
        summary_table.add_column("Value", style="cyan")
        
        summary_table.add_row("Group analyzed", results.get('group_name', 'Unknown'))
        summary_table.add_row("Files processed", str(results.get('files_analyzed', 0)))
        summary_table.add_row("Report generated", results.get('report_path', 'N/A'))
        
        # Add quality metrics if available
        if 'analysis_results' in results:
            analysis_results = results['analysis_results']
            if analysis_results:
                quality_scores = [
                    r['analysis'].get('quality_score', 0)
                    for r in analysis_results
                    if r.get('analysis', {}).get('quality_score')
                ]
                
                if quality_scores:
                    avg_quality = sum(quality_scores) / len(quality_scores)
                    summary_table.add_row("Average quality", f"{avg_quality:.1f}/10")
                    summary_table.add_row("Best file quality", f"{max(quality_scores)}/10")
                    summary_table.add_row("Lowest file quality", f"{min(quality_scores)}/10")
        
        self.console.print()
        self.console.print(summary_table)
        
        # Show next steps
        next_steps = """
💡 **Next Steps:**
• Review the detailed report for file-by-file analysis
• Check quality recommendations and suggestions
• Consider implementing suggested improvements
• Run analysis on other groups if needed
        """.strip()
        
        steps_panel = Panel(
            next_steps,
            title="🎯 Recommendations",
            border_style="blue"
        )
        self.console.print()
        self.console.print(steps_panel)


class ProgressTracker:
    """Helper class for updating progress within a context."""
    
    def __init__(self, progress: Progress, task_id):
        """
        Initialize progress tracker.
        
        Args:
            progress: Rich Progress instance
            task_id: Task ID from progress
        """
        self.progress = progress
        self.task_id = task_id
    
    def update(self, advance: int = 1, description: Optional[str] = None):
        """
        Update progress.
        
        Args:
            advance: Amount to advance progress
            description: New description (optional)
        """
        kwargs = {"advance": advance}
        if description:
            kwargs["description"] = description
        
        self.progress.update(self.task_id, **kwargs)
    
    def update_status(self, description: str):
        """
        Update status description.
        
        Args:
            description: New status description
        """
        self.progress.update(self.task_id, description=description)
    
    def set_total(self, total: int):
        """
        Set total for the progress task.
        
        Args:
            total: Total number of steps
        """
        self.progress.update(self.task_id, total=total)
    
    def complete(self, description: Optional[str] = None):
        """
        Mark progress as complete.
        
        Args:
            description: Final description (optional)
        """
        self.progress.update(self.task_id, completed=True)
        if description:
            self.progress.update(self.task_id, description=description)


def create_status_panel(title: str, content: str, style: str = "blue") -> Panel:
    """
    Create a status panel with consistent styling.
    
    Args:
        title: Panel title
        content: Panel content
        style: Border style
        
    Returns:
        Rich Panel instance
    """
    return Panel(content, title=title, border_style=style)


def format_file_progress(current: int, total: int, filename: str) -> str:
    """
    Format file progress for display.
    
    Args:
        current: Current file number
        total: Total files
        filename: Name of current file
        
    Returns:
        Formatted progress string
    """
    # Truncate long filenames
    display_name = filename
    if len(filename) > 50:
        display_name = "..." + filename[-47:]
    
    return f"[{current}/{total}] Analyzing {display_name}"
