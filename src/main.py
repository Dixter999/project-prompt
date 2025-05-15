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

console = Console()
app = typer.Typer(help="ProjectPrompt: Asistente inteligente para proyectos")


@app.command()
def version():
    """Mostrar la versión actual de ProjectPrompt."""
    console.print(f"[bold green]ProjectPrompt v{__version__}[/bold green]")


@app.command()
def init():
    """Inicializar un nuevo proyecto con ProjectPrompt."""
    console.print("[bold]Inicializando ProjectPrompt...[/bold]")
    # Implementación básica para comenzar
    console.print("[green]Proyecto inicializado correctamente.[/green]")


@app.command()
def analyze(path: str = typer.Argument(".", help="Ruta al proyecto a analizar")):
    """Analizar la estructura de un proyecto existente."""
    console.print(f"[bold]Analizando proyecto en: [blue]{path}[/blue][/bold]")
    console.print("[yellow]Esta funcionalidad será implementada próximamente.[/yellow]")


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
    pass


if __name__ == "__main__":
    app()
