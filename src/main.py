#!/usr/bin/env python3
"""
Punto de entrada principal para ProjectPrompt.
"""

import os
import sys
from enum import Enum
from typing import Optional

import typer
from rich.console import Console

from src import __version__
from src.utils import logger, config_manager, LogLevel, set_level
from src.ui import menu
from src.ui.cli import cli

console = Console()
app = typer.Typer(help="ProjectPrompt: Asistente inteligente para proyectos")


@app.command()
def version():
    """Mostrar la versión actual de ProjectPrompt."""
    cli.print_header("Información de Versión")
    cli.print_info(f"ProjectPrompt v{__version__}")
    
    # Mostrar información adicional
    table = cli.create_table("Detalles", ["Componente", "Versión/Estado"])
    table.add_row("Python", sys.version.split()[0])
    table.add_row("API OpenAI", "Configurada" if config_manager.get("api.openai.enabled") else "No configurada")
    table.add_row("API Anthropic", "Configurada" if config_manager.get("api.anthropic.enabled") else "No configurada")
    console.print(table)


@app.command()
def init(name: str = typer.Option(None, "--name", "-n", help="Nombre del proyecto"),
         path: str = typer.Option(".", "--path", "-p", help="Ruta donde inicializar")):
    """Inicializar un nuevo proyecto con ProjectPrompt."""
    cli.print_header("Inicialización de Proyecto")
    
    # Si no se proporciona un nombre, solicitarlo
    if not name:
        name = cli.prompt("Nombre del proyecto")
    
    cli.print_info(f"Inicializando proyecto '{name}' en {path}...")
    
    # Aquí iría la implementación real de inicialización de proyecto
    # Por ahora, solo simulamos con un mensaje
    
    cli.print_success(f"Proyecto '{name}' inicializado correctamente")


@app.command()
def analyze(path: str = typer.Argument(".", help="Ruta al proyecto a analizar")):
    """Analizar la estructura de un proyecto existente."""
    cli.print_header("Análisis de Proyecto")
    cli.print_info(f"Analizando proyecto en: {path}")
    cli.print_warning("Esta funcionalidad será implementada próximamente.")
    
    
@app.command()
def menu():
    """Iniciar el menú interactivo de ProjectPrompt."""
    menu.show()


@app.command()
def config(key: Optional[str] = None, value: Optional[str] = None, list_all: bool = typer.Option(False, "--list", "-l", help="Listar toda la configuración")):
    """Gestionar la configuración de ProjectPrompt."""
    if list_all:
        console.print("[bold]Configuración actual:[/bold]")
        import json
        console.print_json(json.dumps(config_manager.config))
        return

    if key and value:
        config_manager.set(key, value)
        config_manager.save_config()
        logger.info(f"Configuración actualizada: {key}={value}")
    elif key:
        value = config_manager.get(key)
        if value is not None:
            console.print(f"[bold]{key}[/bold] = {value}")
        else:
            console.print(f"[yellow]No se encontró la clave: {key}[/yellow]")
    else:
        console.print("[yellow]Especifique una clave y opcionalmente un valor.[/yellow]")


@app.command()
def set_api(service: str = typer.Argument(..., help="Servicio (anthropic, openai)"),
           key: str = typer.Argument(..., help="Clave API")):
    """Configurar una clave API para servicios."""
    if service.lower() not in ["anthropic", "openai"]:
        logger.error(f"Servicio no soportado: {service}")
        console.print("[red]Servicios soportados: anthropic, openai[/red]")
        return

    if config_manager.set_api_key(service.lower(), key):
        logger.info(f"Clave API para {service} configurada correctamente")
        console.print(f"[green]Clave API para {service} configurada correctamente[/green]")
    else:
        logger.error(f"Error al configurar la clave API para {service}")
        console.print("[red]Error al configurar la clave API[/red]")


@app.command()
def set_log_level(level: str = typer.Argument(..., help="Nivel de log: debug, info, warning, error, critical")):
    """Cambiar el nivel de logging."""
    try:
        log_level = LogLevel(level.lower())
        set_level(log_level)
        config_manager.set("log_level", log_level.value)
        config_manager.save_config()
        logger.info(f"Nivel de log cambiado a {log_level.value.upper()}")
    except ValueError:
        valid_levels = ", ".join([l.value for l in LogLevel])
        logger.error(f"Nivel de log no válido: {level}")
        console.print(f"[red]Niveles válidos: {valid_levels}[/red]")


@app.command()
def help():
    """Mostrar ayuda detallada sobre ProjectPrompt."""
    cli.print_header("Ayuda de ProjectPrompt")
    
    cli.print_panel(
        "Acerca de ProjectPrompt", 
        "ProjectPrompt es un asistente inteligente para analizar proyectos de código "
        "y generar prompts contextuales utilizando IA.\n\n"
        "Permite analizar la estructura de proyectos, detectar funcionalidades, "
        "y generar documentación progresiva."
    )
    
    # Comandos disponibles
    table = cli.create_table("Comandos Disponibles", ["Comando", "Descripción"])
    table.add_row("init", "Inicializar un nuevo proyecto")
    table.add_row("analyze", "Analizar la estructura de un proyecto")
    table.add_row("version", "Mostrar la versión actual")
    table.add_row("config", "Gestionar la configuración")
    table.add_row("set-api", "Configurar claves de API")
    table.add_row("set-log-level", "Cambiar el nivel de logging")
    table.add_row("menu", "Iniciar el menú interactivo")
    table.add_row("help", "Mostrar esta ayuda")
    console.print(table)
    
    cli.print_info("Para más información sobre un comando específico, use:")
    console.print("  project-prompt [COMANDO] --help")


@app.callback()
def main(debug: bool = typer.Option(False, "--debug", "-d", help="Activar modo debug")):
    """
    ProjectPrompt: Asistente inteligente para analizar proyectos y generar documentación
    utilizando IA.
    """
    # Configurar nivel de log
    if debug:
        set_level(LogLevel.DEBUG)
        logger.debug("Modo debug activado")
    else:
        log_level = config_manager.get("log_level", "info")
        set_level(log_level)
    
    # Mensaje de bienvenida en modo debug
    logger.debug(f"ProjectPrompt v{__version__} iniciado")


if __name__ == "__main__":
    app()
