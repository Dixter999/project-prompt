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
        
    @staticmethod
    def check_premium_feature(feature_name: str) -> bool:
        """
        Verifica si una característica premium está disponible y muestra un mensaje apropiado.
        
        Args:
            feature_name: Nombre de la característica a verificar
            
        Returns:
            True si la característica está disponible, False en caso contrario
        """
        # Importar aquí para evitar dependencias circulares
        from src.utils.subscription_manager import get_subscription_manager
        
        subscription_manager = get_subscription_manager()
        is_available = subscription_manager.can_use_feature(feature_name)
        
        if not is_available:
            console.print(Panel(
                f"La característica '[bold]{feature_name}[/bold]' requiere una suscripción premium.\n"
                f"Tu suscripción actual es: [bold]{subscription_manager.get_subscription_type().upper()}[/bold]\n\n"
                f"Ejecuta '[bold]project-prompt subscription plans[/bold]' para ver los planes disponibles\n"
                f"o '[bold]project-prompt subscription activate[/bold]' para activar una licencia.",
                title="[bold red]Característica Premium[/bold red]",
                border_style="red"
            ))
            
        return is_available
    
    @staticmethod
    def status(message: str):
        """
        Muestra un mensaje de estado con un spinner que indica actividad.
        
        Args:
            message: Mensaje a mostrar
            
        Returns:
            Context manager para usar con 'with'
        """
        from rich.live import Live
        from rich.spinner import Spinner
        
        spinner = Spinner("dots", text=message)
        return Live(spinner, refresh_per_second=10)
    
    @staticmethod
    def create_tree(title: str):
        """
        Crea un árbol para mostrar estructuras de directorios.
        
        Args:
            title: Título del árbol
            
        Returns:
            Un árbol de Rich configurado
        """
        from rich.tree import Tree
        
        tree = Tree(f"[bold yellow]{title}[/bold yellow]")
        return tree
    
    @staticmethod
    def analyze_feature(feature: str, path: str = ".", output: Optional[str] = None, format: str = "md"):
        """
        Analizar una funcionalidad específica del proyecto.
        
        Args:
            feature: Nombre de la funcionalidad a analizar
            path: Ruta al proyecto
            output: Ruta para guardar el análisis
            format: Formato del reporte (md o json)
        """
        from src.main import analyze_feature as analyze_feature_cmd
        analyze_feature_cmd(feature=feature, path=path, output=output, format=format)
    
    @staticmethod
    def interview_functionality(functionality: str, path: str = ".", output: Optional[str] = None, list_interviews: bool = False):
        """
        Realizar una entrevista guiada sobre una funcionalidad específica.
        
        Args:
            functionality: Nombre de la funcionalidad a entrevistar
            path: Ruta al proyecto
            output: Ruta personalizada para guardar la entrevista
            list_interviews: Si debe listar las entrevistas existentes
        """
        from src.main import interview as interview_cmd
        interview_cmd(functionality=functionality, path=path, output=output, list_interviews=list_interviews)
    
    @staticmethod
    def suggest_branch_strategy(functionality: str, proposal: Optional[str] = None, branch_type: str = "feature",
                              description: str = "", files: str = "", output: Optional[str] = None):
        """
        Sugerir una estrategia de branches de Git para implementar una funcionalidad.
        
        Args:
            functionality: Nombre de la funcionalidad
            proposal: Ruta al archivo markdown con la propuesta de implementación
            branch_type: Tipo de branch (feature, bugfix, hotfix, refactor)
            description: Descripción corta de la funcionalidad
            files: Archivos a crear/modificar, separados por coma
            output: Ruta para guardar la estrategia en Markdown
        """
        from src.main import suggest_branches as suggest_branches_cmd
        suggest_branches_cmd(functionality=functionality, proposal=proposal, branch_type=branch_type,
                          description=description, files=files, output=output)


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
create_tree = cli.create_tree
confirm = cli.confirm
prompt = cli.prompt
status = cli.status
analyze_feature = cli.analyze_feature
interview_functionality = cli.interview_functionality
suggest_branch_strategy = cli.suggest_branch_strategy
check_premium_feature = cli.check_premium_feature
