"""Módulo para interfaz de usuario y CLI."""

from src.ui.cli import (
    cli, print_header, print_success, print_error, 
    print_warning, print_info, print_panel, create_table,
    confirm, prompt,
)
from src.ui.menu import Menu, menu
from src.ui.analysis_view import analysis_view, AnalysisView
from src.ui.interview_system import get_interview_system
from src.ui.dashboard import DashboardGenerator, DashboardCLI

__all__ = [
    'cli', 'print_header', 'print_success', 'print_error', 
    'print_warning', 'print_info', 'print_panel', 'create_table',
    'confirm', 'prompt', 'Menu', 'menu', 'analysis_view', 'AnalysisView',
    'get_interview_system', 'DashboardGenerator', 'DashboardCLI',
]
