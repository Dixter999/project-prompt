#!/usr/bin/env python3
"""
Interfaz de línea de comandos (CLI) para ProjectPrompt.
Este módulo provee todas las interfaces basadas en texto para interactuar con el programa.
"""

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
# Lazy import to avoid circular dependencies
# console will be initialized when first accessed

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


class CLI:
    """
    Clase que maneja la interfaz de línea de comandos de ProjectPrompt.
    Provee métodos de utilidad para mostrar mensajes, tablas y panels al usuario.
    """
    
    @staticmethod
    def print_header(title: str = "ProjectPrompt"):
        """Muestra un header con el título especificado."""
        get_console().print(f"\n[bold blue]{title}[/bold blue] [cyan]v{__version__}[/cyan]")
        get_console().print("[dim]Asistente inteligente para proyectos usando IA[/dim]")
        get_console().print("─" * 60)
    
    @staticmethod
    def print_success(message: str):
        """Muestra un mensaje de éxito."""
        get_console().print(f"[bold green]✓[/bold green] {message}")
    
    @staticmethod
    def print_error(message: str):
        """Muestra un mensaje de error."""
        get_console().print(f"[bold red]✗[/bold red] {message}")
    
    @staticmethod
    def print_warning(message: str):
        """Muestra un mensaje de advertencia."""
        get_console().print(f"[bold yellow]![/bold yellow] {message}")
    
    @staticmethod
    def print_info(message: str):
        """Muestra un mensaje informativo."""
        get_console().print(f"[bold blue]i[/bold blue] {message}")
    
    @staticmethod
    def print_panel(title: str, content: str, style: str = "blue"):
        """Muestra un panel con título y contenido."""
        get_console().print(Panel(content, title=title, border_style=style))
    
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
        # Premium features now available for all users
        is_available = True
        
        if not is_available:
            # This code will never run since is_available is always True
            get_console().print(Panel(
                f"La característica '[bold]{feature_name}[/bold]' requiere una suscripción premium.\n"
                f"Premium features are now available for all users!\n\n"
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
    
    @staticmethod
    def status_spinner(message: str):
        """
        Muestra un spinner con un mensaje que indica actividad.
        
        Args:
            message: Mensaje a mostrar
            
        Returns:
            Context manager para usar con 'with'
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=get_console()
        )
    
    @staticmethod
    def progress_bar(message: str, total: int = 100):
        """
        Crea una barra de progreso.
        
        Args:
            message: Mensaje a mostrar
            total: Total de pasos
            
        Returns:
            Object Progress para usar con 'with'
        """
        return Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=get_console()
        )
        
    @staticmethod
    def display_code(code: str, language: str = "python", line_numbers: bool = True):
        """
        Muestra código con resaltado de sintaxis.
        
        Args:
            code: Código a mostrar
            language: Lenguaje del código (para resaltado)
            line_numbers: Si debe mostrar números de línea
        """
        syntax = Syntax(code, language, line_numbers=line_numbers)
        get_console().print(syntax)
    
    @staticmethod
    def display_markdown(text: str):
        """
        Muestra texto en formato Markdown.
        
        Args:
            text: Texto en Markdown
        """
        md = Markdown(text)
        get_console().print(md)
    
    @staticmethod
    def clear_screen():
        """Limpia la pantalla de la consola."""
        os.system('cls' if platform.system() == 'Windows' else 'clear')
    
    @staticmethod
    def get_console_size() -> Tuple[int, int]:
        """
        Obtiene el tamaño de la consola.
        
        Returns:
            Tupla con el ancho y alto de la consola (columnas, filas)
        """
        terminal_width, terminal_height = shutil.get_terminal_size((80, 20))
        return terminal_width, terminal_height
    
    @staticmethod
    def create_layout() -> Layout:
        """
        Crea un layout para organizar la interfaz.
        
        Returns:
            Layout de Rich configurado
        """
        layout = Layout()
        return layout
    
    @staticmethod
    def create_multi_column_table(title: str, column_groups: List[List[str]]) -> Table:
        """
        Crea una tabla con grupos de columnas.
        
        Args:
            title: Título de la tabla
            column_groups: Lista de grupos de columnas, donde cada grupo es una lista de nombres de columnas
            
        Returns:
            Una tabla de Rich configurada
        """
        table = Table(title=title, show_header=True, header_style="bold blue")
        
        for group in column_groups:
            for column in group:
                table.add_column(column)
                
        return table
    
    @staticmethod
    def ask_choice(prompt_text: str, choices: List[str], default: int = 0) -> str:
        """
        Solicita al usuario que elija una opción de una lista.
        
        Args:
            prompt_text: Texto del prompt
            choices: Lista de opciones
            default: Índice de la opción por defecto
            
        Returns:
            Opción seleccionada
        """
        if not choices:
            raise ValueError("La lista de opciones no puede estar vacía")
            
        # Mostrar opciones numeradas
        get_console().print(f"\n{prompt_text}")
        for i, choice in enumerate(choices):
            get_console().print(f"  [cyan]{i+1}.[/cyan] {choice}")
        
        # Solicitar selección
        while True:
            try:
                selected = IntPrompt.ask(
                    "\nSeleccione una opción",
                    default=default + 1,
                    console=get_console()
                )
                
                if 1 <= selected <= len(choices):
                    return choices[selected - 1]
                else:
                    get_console().print("[red]Opción inválida. Intente de nuevo.[/red]")
            except ValueError:
                get_console().print("[red]Por favor ingrese un número.[/red]")
    
    @staticmethod
    def ask_input(prompt_text: str, default: str = "", password: bool = False) -> str:
        """
        Solicita una entrada de texto al usuario.
        
        Args:
            prompt_text: Texto del prompt
            default: Valor por defecto
            password: Si debe ocultar la entrada
            
        Returns:
            Texto ingresado por el usuario
        """
        return Prompt.ask(
            prompt_text, 
            default=default, 
            password=password,
            console=get_console()
        )
    
    @staticmethod
    def ask_confirm(prompt_text: str, default: bool = True) -> bool:
        """
        Solicita una confirmación al usuario.
        
        Args:
            prompt_text: Texto del prompt
            default: Valor por defecto
            
        Returns:
            True si el usuario confirma, False en caso contrario
        """
        return Confirm.ask(prompt_text, default=default, console=get_console())
    
    @staticmethod
    def apply_theme():
        """Aplica el tema actual a la consola."""
        # Reset console to force reinitialization with new theme
        global _console
        _console = None


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
