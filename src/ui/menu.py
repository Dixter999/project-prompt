#!/usr/bin/env python3
"""
Menú interactivo para ProjectPrompt.
Este módulo provee una interfaz interactiva para navegar por las funcionalidades del programa.
"""

import os
import sys
from typing import List, Dict, Any, Callable, Optional, Union, Tuple

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table

from src import __version__
from src.utils import logger, config_manager
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# Create console instance
console = Console()

def print_header(title: str = "ProjectPrompt"):
    """Muestra un header con el título especificado."""
    console.print(f"\n[bold blue]{title}[/bold blue]")
    console.print("[dim]Asistente inteligente para proyectos usando IA[/dim]")
    console.print("─" * 60)

def print_success(message: str):
    """Muestra un mensaje de éxito."""
    console.print(f"[bold green]✓[/bold green] {message}")

def print_error(message: str):
    """Muestra un mensaje de error."""
    console.print(f"[bold red]✗[/bold red] {message}")

def print_warning(message: str):
    """Muestra un mensaje de advertencia."""
    console.print(f"[bold yellow]![/bold yellow] {message}")

def print_info(message: str):
    """Muestra un mensaje informativo."""
    console.print(f"[bold blue]i[/bold blue] {message}")


# Tipo para las opciones del menú
MenuOption = Dict[str, Union[str, Callable]]


class Menu:
    """
    Clase que implementa un menú interactivo para ProjectPrompt.
    Permite navegar por las diferentes funcionalidades del programa.
    """
    
    def __init__(self, title: str = "Menú Principal"):
        """
        Inicializa un nuevo menú.
        
        Args:
            title: Título del menú
        """
        self.title = title
        self.options: List[MenuOption] = []
        self.console = Console()
    
    def add_option(self, key: str, description: str, action: Callable, args: Tuple = (), kwargs: Dict = None):
        """
        Añade una opción al menú.
        
        Args:
            key: Clave para seleccionar la opción (e.g., "1", "q")
            description: Descripción de la opción
            action: Función a ejecutar cuando se seleccione la opción
            args: Argumentos a pasar a la función
            kwargs: Argumentos con nombre a pasar a la función
        """
        self.options.append({
            "type": "option",
            "key": key,
            "description": description,
            "action": action,
            "args": args,
            "kwargs": kwargs or {}
        })
    
    def add_section(self, title: str):
        """
        Añade una sección al menú para agrupar opciones.
        
        Args:
            title: Título de la sección
        """
        self.options.append({
            "type": "section",
            "title": title
        })

    def add_separator(self):
        """Añade una línea separadora al menú."""
        self.options.append({
            "type": "separator"
        })

    def add_info(self, text: str):
        """
        Añade un texto informativo al menú.
        
        Args:
            text: Texto a mostrar
        """
        self.options.append({
            "type": "info",
            "text": text
        })

    def add_submenu(self, key: str, description: str, submenu: 'Menu'):
        """
        Añade un submenú como opción.
        
        Args:
            key: Clave para seleccionar la opción
            description: Descripción del submenú
            submenu: Objeto Menu del submenú
        """
        self.options.append({
            "type": "submenu",
            "key": key,
            "description": description,
            "submenu": submenu
        })
        
    def add_back_option(self, key: str = "0", description: str = "Volver al menú anterior"):
        """
        Añade una opción para volver al menú anterior.
        
        Args:
            key: Clave para seleccionar la opción
            description: Descripción de la opción
        """
        self.add_option(key, description, lambda: None)
    
    def add_exit_option(self, key: str = "q", description: str = "Salir"):
        """
        Añade una opción para salir.
        
        Args:
            key: Clave para seleccionar la opción
            description: Descripción de la opción
        """
        self.add_option(key, description, sys.exit)
    
    def show(self) -> Any:
        """
        Muestra el menú y procesa la selección del usuario.
        
        Returns:
            El resultado de la acción seleccionada, o None para volver/salir
        """
        while True:
            # Limpiar pantalla
            # os.system('cls' if os.name == 'nt' else 'clear')
            
            # Mostrar cabecera
            print_header(self.title)
            
            # Mostrar opciones usando el método correcto
            self._print_options()
            
            # Solicitar selección
            valid_keys = [opt["key"] for opt in self.options if "key" in opt and opt["key"]]
            selection = Prompt.ask("\nSeleccione una opción", choices=valid_keys)
            
            # Para opciones de salir
            if selection in ["q", "exit"]:
                return None
            
            # Ejecutar acción seleccionada usando _handle_selection
            if self._handle_selection(selection):
                # Si fue una acción normal, continuar mostrando el menú
                if selection not in ["0", "b"]:  # Si no es volver/atrás
                    input("\nPresione Enter para continuar...")
            else:
                # Si retorna False, significa que hubo un error o se debe salir
                if selection in ["0", "b"]:  # Opciones de volver
                    return None
    
    def show_with_autocompletion(self):
        """
        Muestra el menú con autocompletado de opciones.
        
        Returns:
            Opción seleccionada
        """
        from prompt_toolkit import PromptSession
        from prompt_toolkit.completion import WordCompleter
        
        print_header(self.title)
        
        # Extraer opciones seleccionables
        selectable_options = {}
        for option in self.options:
            if option.get("type") == "option":
                selectable_options[option["key"]] = option["description"]
            elif option.get("type") == "submenu":
                selectable_options[option["key"]] = option["description"]
        
        # Crear completador de palabras
        option_completer = WordCompleter(list(selectable_options.keys()), ignore_case=True)
        session = PromptSession(completer=option_completer)
        
        # Mostrar opciones
        self._print_options()
        
        # Solicitar selección con autocompletado
        try:
            selected = session.prompt("\nSeleccione una opción (Tab para autocompletar): ")
            self._handle_selection(selected)
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Operación cancelada.[/yellow]")
            
        return selected
        
    def _print_options(self):
        """Muestra las opciones del menú."""
        table = Table(box=None, show_header=False)
        table.add_column("Key", style="cyan")
        table.add_column("Description")
        
        for option in self.options:
            option_type = option.get("type", "option")
            
            if option_type == "section":
                # Añadir una sección
                table.add_row("", f"[bold blue]{option['title']}[/bold blue]")
                
            elif option_type == "separator":
                # Añadir un separador
                table.add_row("", "─" * 40)
                
            elif option_type == "info":
                # Añadir texto informativo
                table.add_row("", f"[dim]{option['text']}[/dim]")
                
            elif option_type == "submenu":
                # Añadir opción de submenú
                table.add_row(option["key"], f"{option['description']} [dim]→[/dim]")
                
            else:  # opción normal
                table.add_row(option["key"], option["description"])
        
        self.console.print(table)
        
    def _handle_selection(self, key: str):
        """
        Maneja la selección de una opción.
        
        Args:
            key: Clave seleccionada
            
        Returns:
            True si se procesó correctamente, False en caso contrario
        """
        for option in self.options:
            if option.get("type") != "option" and option.get("type") != "submenu":
                continue
                
            if option["key"] == key:
                if option.get("type") == "option":
                    # Ejecutar función asociada
                    kwargs = option.get("kwargs", {}) or {}
                    option["action"](*option.get("args", ()), **kwargs)
                    return True
                elif option.get("type") == "submenu":
                    # Mostrar submenú
                    submenu = option["submenu"]
                    submenu.show()
                    return True
        
        self.console.print(f"[red]Opción no válida: {key}[/red]")
        return False


# Funciones específicas para los menús
def show_proyecto_info():
    """Muestra información del proyecto actual."""
    print_info("Mostrando información del proyecto...")
    
    table = Table(title="Información del Proyecto")
    table.add_column("Campo")
    table.add_column("Valor")
    
    table.add_row("Versión", __version__)
    table.add_row("Modo", "Premium" if config_manager.is_premium() else "Free")
    table.add_row("API OpenAI", "Configurada" if config_manager.get("api.openai.enabled") else "No configurada")
    table.add_row("API Anthropic", "Configurada" if config_manager.get("api.anthropic.enabled") else "No configurada")
    
    Console().print(table)


def config_api_keys():
    """Configura las claves de API."""
    print_info("Configuración de APIs")
    
    # OpenAI
    if Confirm.ask("¿Desea configurar la API de OpenAI?"):
        key = Prompt.ask("Introduzca su clave de API de OpenAI", password=True)
        if config_manager.set_api_key("openai", key):
            print_success("API de OpenAI configurada correctamente")
        else:
            print_error("Error al configurar la API de OpenAI")
    
    # Anthropic
    if Confirm.ask("¿Desea configurar la API de Anthropic?"):
        key = Prompt.ask("Introduzca su clave de API de Anthropic", password=True)
        if config_manager.set_api_key("anthropic", key):
            print_success("API de Anthropic configurada correctamente")
        else:
            print_error("Error al configurar la API de Anthropic")


def analyze_project():
    """Analiza un proyecto existente."""
    print_info("Análisis de proyecto")
    path = Prompt.ask("Introduzca la ruta al proyecto", default=".")
    
    print_info(f"Analizando proyecto en: {path}")
    # En una implementación real, aquí iría el código para analizar el proyecto
    print_warning("Esta función será implementada en futuras versiones")


def create_menu():
    """
    Crea el menú principal y todos los submenús.
    
    Returns:
        El menú principal completo
    """
    # Menú principal
    main_menu = Menu("Menú Principal de ProjectPrompt")
    main_menu.add_option("1", "Analizar proyecto", analyze_project)
    main_menu.add_option("2", "Información del proyecto", show_proyecto_info)
    main_menu.add_separator()
    
    # Submenú de configuración
    config_menu = Menu("Configuración")
    config_menu.add_option("1", "Configurar APIs", config_api_keys)
    config_menu.add_back_option()
    main_menu.add_submenu("3", "Configuración", config_menu)
    
    main_menu.add_separator()
    main_menu.add_exit_option()
    
    return main_menu


# Menú global para uso directo
menu = create_menu()
