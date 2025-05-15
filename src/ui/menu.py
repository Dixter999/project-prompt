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
from src.ui.cli import cli, print_header, print_success, print_error, print_warning, print_info


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
            "key": key,
            "description": description,
            "action": action,
            "args": args,
            "kwargs": kwargs or {}
        })
    
    def add_submenu(self, key: str, description: str, submenu: 'Menu'):
        """
        Añade un submenú como opción.
        
        Args:
            key: Clave para seleccionar la opción
            description: Descripción de la opción
            submenu: Menú a mostrar cuando se seleccione esta opción
        """
        self.add_option(key, description, submenu.show)
    
    def add_separator(self):
        """Añade una separación en el menú."""
        self.options.append({"key": "", "description": "─" * 50, "action": None})
    
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
            
            # Crear tabla de opciones
            table = Table(show_header=False, box=None)
            table.add_column("Key", style="cyan", no_wrap=True)
            table.add_column("Descripción")
            
            # Mostrar opciones
            for option in self.options:
                if "key" not in option or option["key"] == "":
                    table.add_row("", option["description"])
                else:
                    table.add_row(f"[{option['key']}]", option["description"])
            
            self.console.print(table)
            
            # Solicitar selección
            valid_keys = [opt["key"] for opt in self.options if "key" in opt and opt["key"]]
            selection = Prompt.ask("\nSeleccione una opción", choices=valid_keys)
            
            # Ejecutar acción seleccionada
            for option in self.options:
                if option.get("key") == selection:
                    action = option.get("action")
                    if action:
                        args = option.get("args", ())
                        kwargs = option.get("kwargs", {})
                        result = action(*args, **kwargs)
                        
                        # Para opciones de volver/salir
                        if selection in ["0", "b", "q"]:
                            return result
                        
                        # Pausa para que se vean los resultados antes de volver al menú
                        input("\nPresione Enter para continuar...")
                        break


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
