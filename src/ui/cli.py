#!/usr/bin/env python3
"""
Interfaz de línea de comandos (CLI) para ProjectPrompt.
Este módulo provee todas las interfaces basadas en texto para interactuar con el programa.
"""

import os
import sys
from typing import List, Optional, Dict, Any, Callable

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src import __version__
from src.utils import logger, config_manager, LogLevel, set_level

# Console para output estándar
console = Console()


class CLI:
    """
    Clase que maneja la interfaz de línea de comandos de ProjectPrompt.
    Provee métodos de utilidad para mostrar mensajes, tablas y panels al usuario.
    """
    
    @staticmethod
    def print_header(title: str = "ProjectPrompt"):
        """Muestra un header con el título especificado."""
        console.print(f"\n[bold blue]{title}[/bold blue] [cyan]v{__version__}[/cyan]")
        console.print("[dim]Asistente inteligente para proyectos usando IA[/dim]")
        console.print("─" * 60)
    
    @staticmethod
    def print_success(message: str):
        """Muestra un mensaje de éxito."""
        console.print(f"[bold green]✓[/bold green] {message}")
    
    @staticmethod
    def print_error(message: str):
        """Muestra un mensaje de error."""
        console.print(f"[bold red]✗[/bold red] {message}")
    
    @staticmethod
    def print_warning(message: str):
        """Muestra un mensaje de advertencia."""
        console.print(f"[bold yellow]![/bold yellow] {message}")
    
    @staticmethod
    def print_info(message: str):
        """Muestra un mensaje informativo."""
        console.print(f"[bold blue]i[/bold blue] {message}")
    
    @staticmethod
    def print_panel(title: str, content: str, style: str = "blue"):
        """Muestra un panel con título y contenido."""
        console.print(Panel(content, title=title, border_style=style))
    
    @staticmethod
    def create_table(title: str, columns: List[str]) -> Table:
        """
        Crea una tabla con el título y columnas especificadas.
        
        Args:
            title: Título de la tabla
            columns: Lista de nombres de columnas
            
        Returns:
            Una tabla de Rich configurada
        """
        table = Table(title=title, show_header=True, header_style="bold blue")
        for column in columns:
            table.add_column(column)
        return table
    
    @staticmethod
    def confirm(question: str, default: bool = False) -> bool:
        """
        Solicita confirmación al usuario.
        
        Args:
            question: Pregunta a realizar
            default: Valor por defecto
            
        Returns:
            True si el usuario confirma, False en caso contrario
        """
        return typer.confirm(question, default=default)
    
    @staticmethod
    def prompt(prompt_text: str, default: str = "", hide_input: bool = False) -> str:
        """
        Solicita un valor al usuario.
        
        Args:
            prompt_text: Texto del prompt
            default: Valor por defecto
            hide_input: Si debe ocultar la entrada (para contraseñas)
            
        Returns:
            El valor ingresado por el usuario
        """
        return typer.prompt(prompt_text, default=default, hide_input=hide_input)


# Exportar una instancia global para uso directo
cli = CLI()

# Para uso directo sin la clase
print_header = cli.print_header
print_success = cli.print_success
print_error = cli.print_error
print_warning = cli.print_warning
print_info = cli.print_info
print_panel = cli.print_panel
create_table = cli.create_table
confirm = cli.confirm
prompt = cli.prompt
