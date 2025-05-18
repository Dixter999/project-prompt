#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Punto de entrada principal para test-project.
"""

import typer
from rich.console import Console

app = typer.Typer(help="test-project: Descripción de la aplicación")
console = Console()

@app.command()
def hello(name: str = "World"):
    """Saludar al usuario."""
    console.print(f"[bold green]¡Hola {name}![/bold green]")

@app.command()
def version():
    """Mostrar la versión de la aplicación."""
    from src import __version__
    console.print(f"[bold]test-project[/bold] versión: {__version__}")

if __name__ == "__main__":
    app()
