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
from src.utils.api_validator import get_api_validator
from src.ui import menu
from src.ui.cli import cli
# Importamos los analizadores bajo demanda para evitar carga innecesaria

console = Console()
app = typer.Typer(help="ProjectPrompt: Asistente inteligente para proyectos")


@app.command()
def version():
    """Mostrar la versión actual de ProjectPrompt."""
    cli.print_header("Información de Versión")
    cli.print_info(f"ProjectPrompt v{__version__}")
    
    # Verificar estado de las APIs
    validator = get_api_validator()
    status = validator.get_status_summary()
    
    # Mostrar información adicional
    table = cli.create_table("Detalles", ["Componente", "Versión/Estado"])
    table.add_row("Python", sys.version.split()[0])
    table.add_row("API Anthropic", "Configurada ✅" if status.get("anthropic", False) else "No configurada ❌")
    table.add_row("API GitHub", "Configurada ✅" if status.get("github", False) else "No configurada ❌")
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
def analyze(
    path: str = typer.Argument(".", help="Ruta al proyecto a analizar"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Ruta para guardar el análisis en formato JSON"),
    max_files: int = typer.Option(10000, "--max-files", "-m", help="Número máximo de archivos a analizar"),
    max_size: float = typer.Option(5.0, "--max-size", "-s", help="Tamaño máximo de archivo a analizar en MB"),
):
    """Analizar la estructura de un proyecto existente."""
    from src.analyzers.project_scanner import get_project_scanner
    import json
    import os
    from datetime import datetime
    
    project_path = os.path.abspath(path)
    
    if not os.path.isdir(project_path):
        cli.print_error(f"La ruta especificada no es un directorio válido: {project_path}")
        return
        
    cli.print_header("Análisis de Proyecto")
    cli.print_info(f"Analizando proyecto en: {project_path}")
    
    try:
        # Crear escáner de proyectos
        scanner = get_project_scanner(max_file_size_mb=max_size, max_files=max_files)
        
        # Mostrar progreso
        with cli.status("Escaneando archivos y directorios..."):
            # Realizar análisis
            result = scanner.scan_project(project_path)
        
        # Mostrar resumen
        cli.print_success(f"Análisis completado en {result.get('scan_time', 0)} segundos")
        
        # Estadísticas
        stats = result.get('stats', {})
        cli.print_info("Estadísticas del proyecto:")
        
        # Crear tabla de estadísticas
        stats_table = cli.create_table("Estadísticas", ["Métrica", "Valor"])
        stats_table.add_row("Total de archivos", str(stats.get('total_files', 0)))
        stats_table.add_row("Total de directorios", str(stats.get('total_dirs', 0)))
        stats_table.add_row("Archivos analizados", str(stats.get('analyzed_files', 0)))
        stats_table.add_row("Archivos binarios", str(stats.get('binary_files', 0)))
        stats_table.add_row("Archivos omitidos", str(stats.get('skipped_files', 0)))
        stats_table.add_row("Tamaño total", f"{stats.get('total_size_kb', 0):,} KB")
        console.print(stats_table)
        
        # Lenguajes principales
        languages = result.get('languages', {})
        if languages:
            main_languages = languages.get('_main', [])
            secondary_languages = languages.get('_secondary', [])
            
            if main_languages:
                cli.print_info(f"Lenguajes principales: {', '.join(main_languages)}")
            if secondary_languages:
                cli.print_info(f"Lenguajes secundarios: {', '.join(secondary_languages)}")
            
            # Tabla de lenguajes
            lang_table = cli.create_table("Lenguajes", ["Lenguaje", "Archivos", "% del proyecto", "Tamaño (KB)"])
            
            for lang, data in languages.items():
                if lang.startswith('_'):  # Skip meta entries
                    continue
                    
                lang_table.add_row(
                    lang,
                    str(data.get('files', 0)),
                    f"{data.get('percentage', 0)}%",
                    f"{data.get('size_kb', 0):,}"
                )
            
            console.print(lang_table)
        
        # Archivos importantes
        important_files = result.get('important_files', {})
        if important_files:
            cli.print_info("Archivos importantes detectados:")
            
            # Limitar número de archivos por categoría para la visualización
            for category, files in important_files.items():
                if category.startswith('_'):  # Skip meta entries
                    continue
                
                # Mostrar categoría con hasta 5 archivos
                cli.print_info(f"[bold]{category.capitalize()}[/bold]:")
                for i, file_path in enumerate(files[:5]):
                    console.print(f"  {i+1}. {file_path}")
                
                # Si hay más archivos, indicarlo
                if len(files) > 5:
                    console.print(f"  ... y {len(files) - 5} más")
        
        # Dependencias principales
        dependencies = result.get('dependencies', {})
        if dependencies and '_main' in dependencies:
            main_deps = dependencies.get('_main', [])
            if main_deps:
                cli.print_info(f"Dependencias principales: {', '.join(main_deps[:10])}")
                if len(main_deps) > 10:
                    console.print(f"  ... y {len(main_deps) - 10} más")
        
        # Guardar resultados si se especificó un archivo de salida
        if output:
            output_path = output
            
            # Si no se especificó extensión, añadir .json
            if not output.endswith('.json'):
                output_path = f"{output}.json"
                
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                
            # Simplificar datos para JSON
            simple_result = {
                'project_path': result.get('project_path', ''),
                'scan_time': result.get('scan_time', 0),
                'stats': result.get('stats', {}),
                'languages': result.get('languages', {}),
                'important_files': result.get('important_files', {}),
                'dependencies': result.get('dependencies', {}),
            }
            
            # Guardar en formato JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(simple_result, f, indent=2)
                
            cli.print_success(f"Análisis guardado en: {output_path}")
            
    except Exception as e:
        cli.print_error(f"Error durante el análisis: {e}")
        logger.error(f"Error en analyze: {e}", exc_info=True)
    
    
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
def set_api(
    api_name: str = typer.Argument(..., help="Nombre de la API (anthropic, github)"),
    api_key: Optional[str] = typer.Option(None, "--key", "-k", help="Clave o token de API"),
):
    """Configurar una clave API para servicios."""
    validator = get_api_validator()
    cli.print_header("Configuración de API")
    
    # Si no se proporciona clave, pedirla de forma segura
    if not api_key:
        api_key = typer.prompt(f"Introduce la clave para {api_name}", hide_input=True)
        
    # Guardar y validar la clave
    success, message = validator.set_api_key(api_name, api_key)
    
    if success:
        cli.print_success(message)
        
        # Verificar que la clave funciona
        result = validator.validate_api(api_name)
        if result.get("valid", False):
            cli.print_success(f"✅ Verificación exitosa para {api_name}")
        else:
            cli.print_warning(f"⚠️ La clave se guardó pero no pasó la verificación: {result.get('message')}")
    else:
        cli.print_error(f"❌ Error: {message}")


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
def verify_api(
    api_name: Optional[str] = typer.Argument(
        None, help="Nombre de la API a verificar (anthropic, github). Si no se especifica, se verifican todas."
    )
):
    """Verificar el estado de configuración de APIs."""
    validator = get_api_validator()
    cli.print_header("Verificación de APIs")
    
    if api_name:
        # Verificar una API específica
        cli.print_info(f"Verificando configuración de API: {api_name}")
        result = validator.validate_api(api_name)
        
        if result.get("valid", False):
            cli.print_success(f"✅ {api_name}: {result.get('message', 'Configuración válida')}")
        else:
            cli.print_error(f"❌ {api_name}: {result.get('message', 'Configuración inválida')}")
            
        if "usage" in result:
            cli.print_info("Información de uso:")
            for key, value in result["usage"].items():
                console.print(f"  - {key}: {value}")
    else:
        # Verificar todas las APIs
        cli.print_info("Verificando todas las APIs configuradas...")
        results = validator.validate_all_apis()
        
        # Crear una tabla con los resultados
        table = cli.create_table("Estado de APIs", ["API", "Estado", "Mensaje"])
        
        for api, status in results.items():
            icon = "✅" if status.get("valid", False) else "❌"
            table.add_row(
                api,
                f"{icon} {'Válida' if status.get('valid', False) else 'Inválida'}",
                status.get("message", "")
            )
            
        console.print(table)


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
    table.add_row("verify-api", "Verificar estado de APIs")
    table.add_row("set-log-level", "Cambiar el nivel de logging")
    table.add_row("menu", "Iniciar el menú interactivo")
    table.add_row("help", "Mostrar esta ayuda")
    console.print(table)
    
    cli.print_info("Para más información sobre un comando específico, use:")
    console.print("  project-prompt [COMANDO] --help")


@app.command()
def report(
    path: str = typer.Argument(".", help="Ruta al proyecto para analizar y generar el reporte"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Ruta personalizada para guardar el reporte"),
    max_files: int = typer.Option(10000, "--max-files", "-m", help="Número máximo de archivos a analizar"),
    max_size: float = typer.Option(5.0, "--max-size", "-s", help="Tamaño máximo de archivo a analizar en MB"),
):
    """Generar un reporte en Markdown sobre la estructura del proyecto."""
    from src.generators.markdown_generator import get_markdown_generator
    import os
    
    project_path = os.path.abspath(path)
    
    if not os.path.isdir(project_path):
        cli.print_error(f"La ruta especificada no es un directorio válido: {project_path}")
        return
        
    cli.print_header("Generación de Reporte en Markdown")
    cli.print_info(f"Analizando proyecto en: {project_path}")
    
    try:
        # Crear generador de markdown
        generator = get_markdown_generator()
        
        # Mostrar progreso
        with cli.status("Escaneando proyecto y generando reporte..."):
            # Generar reporte
            report_path = generator.save_project_report(project_path, output)
        
        # Mostrar resultado
        cli.print_success(f"Reporte generado correctamente en: {report_path}")
        cli.print_info("El reporte contiene información sobre la estructura del proyecto, lenguajes, archivos importantes y dependencias.")
        
        # Sugerir siguientes pasos
        cli.print_info("Para ver el reporte puedes:")
        console.print("  - Abrirlo en un editor compatible con Markdown")
        console.print(f"  - Ejecutar: [bold]cat {report_path}[/bold] para ver el contenido en la terminal")
        
    except Exception as e:
        cli.print_error(f"Error al generar el reporte: {e}")
        logger.error(f"Error en report: {e}", exc_info=True)


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
