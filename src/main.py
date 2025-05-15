#!/usr/bin/env python3
"""
Punto de entrada principal para ProjectPrompt.
"""

import typer
from rich.console import Console

from src import __version__

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


@app.callback()
def main():
    """
    ProjectPrompt: Asistente inteligente para analizar proyectos y generar documentación
    utilizando IA.
    """
    pass


if __name__ == "__main__":
    app()
