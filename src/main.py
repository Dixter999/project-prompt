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
from src.ui.analysis_view import analysis_view
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
    functionalities: bool = typer.Option(True, "--functionalities/--no-functionalities", "-f/-nf", 
                                       help="Detectar funcionalidades del proyecto"),
    structure: bool = typer.Option(False, "--structure/--no-structure", "-st/-nst", 
                                 help="Mostrar estructura del proyecto"),
):
    """Analizar la estructura y funcionalidades de un proyecto existente."""
    from src.analyzers.project_scanner import get_project_scanner
    from src.analyzers.functionality_detector import get_functionality_detector
    import json
    import os
    from datetime import datetime
    
    project_path = os.path.abspath(path)
    
    if not os.path.isdir(project_path):
        cli.print_error(f"La ruta especificada no es un directorio válido: {project_path}")
        return
        
    cli.print_header("Análisis Completo de Proyecto")
    cli.print_info(f"Analizando proyecto en: {project_path}")
    
    try:
        # Crear escáner de proyectos
        scanner = get_project_scanner(max_file_size_mb=max_size, max_files=max_files)
        
        # Realizar análisis de estructura
        with cli.status("Escaneando archivos y directorios..."):
            project_data = scanner.scan_project(project_path)
        
        # Mostrar resumen general
        cli.print_success(f"Análisis completado en {project_data.get('scan_time', 0)} segundos")
        
        # Estadísticas básicas
        stats = project_data.get('stats', {})
        stats_table = cli.create_table("Estadísticas", ["Métrica", "Valor"])
        stats_table.add_row("Total de archivos", str(stats.get('total_files', 0)))
        stats_table.add_row("Total de directorios", str(stats.get('total_dirs', 0)))
        stats_table.add_row("Archivos analizados", str(stats.get('analyzed_files', 0)))
        stats_table.add_row("Archivos binarios", str(stats.get('binary_files', 0)))
        stats_table.add_row("Tamaño total", f"{stats.get('total_size_kb', 0):,} KB")
        console.print(stats_table)
        
        # Mostrar lenguajes principales
        analysis_view.show_languages(project_data)
        
        # Mostrar estructura del proyecto si se solicitó
        if structure:
            analysis_view.show_project_structure(project_data)
        
        # Detectar funcionalidades si se solicitó
        functionality_data = {}
        if functionalities:
            # Crear detector de funcionalidades
            detector = get_functionality_detector(scanner=scanner)
            
            # Mostrar progreso
            with cli.status("Detectando funcionalidades en el proyecto..."):
                # Realizar análisis
                functionality_data = detector.detect_functionalities(project_path)
            
            # Mostrar funcionalidades
            analysis_view.show_functionalities(functionality_data)
        
        # Guardar resultados si se especificó un archivo de salida
        if output:
            output_path = output
            
            # Si no se especificó extensión, añadir .json
            if not output.endswith('.json'):
                output_path = f"{output}.json"
                
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                
            # Simplificar datos para JSON
            combined_result = {
                'project_path': project_data.get('project_path', ''),
                'scan_time': project_data.get('scan_time', 0),
                'stats': project_data.get('stats', {}),
                'languages': project_data.get('languages', {}),
                'important_files': project_data.get('important_files', {}),
                'dependencies': project_data.get('dependencies', {}),
            }
            
            # Añadir funcionalidades si se detectaron
            if functionality_data:
                combined_result['functionalities'] = functionality_data
                
            # Guardar en formato JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(combined_result, f, indent=2)
                
            cli.print_success(f"Análisis guardado en: {output_path}")
        
        # Sugerir siguientes pasos    
        cli.print_info("Sugerencias:")
        
        if not structure:
            console.print("  - Ejecutar con --structure para ver la estructura del proyecto")
            
        if not functionalities:
            console.print("  - Ejecutar con --functionalities para detectar funcionalidades")
        
        console.print("  - Usar 'report' para generar un informe detallado en Markdown")
        console.print("  - Usar 'list' para ver solo las funcionalidades del proyecto")
            
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


@app.command()
def detect_functionalities(
    path: str = typer.Argument(".", help="Ruta al proyecto para analizar y detectar funcionalidades"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Ruta para guardar el análisis en formato JSON"),
    max_files: int = typer.Option(10000, "--max-files", "-m", help="Número máximo de archivos a analizar"),
    max_size: float = typer.Option(5.0, "--max-size", "-s", help="Tamaño máximo de archivo a analizar en MB"),
):
    """Detectar funcionalidades básicas en el proyecto."""
    from src.analyzers.project_scanner import get_project_scanner
    from src.analyzers.functionality_detector import get_functionality_detector
    import json
    import os
    
    project_path = os.path.abspath(path)
    
    if not os.path.isdir(project_path):
        cli.print_error(f"La ruta especificada no es un directorio válido: {project_path}")
        return
        
    cli.print_header("Detección de Funcionalidades")
    cli.print_info(f"Analizando proyecto en: {project_path}")
    
    try:
        # Crear escáner de proyectos
        scanner = get_project_scanner(max_file_size_mb=max_size, max_files=max_files)
        
        # Crear detector de funcionalidades
        detector = get_functionality_detector(scanner=scanner)
        
        # Mostrar progreso
        with cli.status("Detectando funcionalidades en el proyecto..."):
            # Realizar análisis
            result = detector.detect_functionalities(project_path)
        
        # Mostrar resumen
        main_functionalities = result.get('main_functionalities', [])
        detected = result.get('detected', {})
        
        if main_functionalities:
            cli.print_success(f"Se detectaron {len(main_functionalities)} funcionalidades principales")
            
            # Crear tabla de funcionalidades
            func_table = cli.create_table("Funcionalidades Detectadas", ["Funcionalidad", "Confianza", "Evidencia"])
            
            for func_name in main_functionalities:
                func_data = detected.get(func_name, {})
                confidence = func_data.get('confidence', 0)
                
                # Obtener evidencia más significativa
                evidence = []
                if func_data.get('evidence', {}).get('imports'):
                    imports = func_data.get('evidence', {}).get('imports', [])[:2]
                    evidence.extend(imports)
                    
                if func_data.get('evidence', {}).get('files'):
                    files = [os.path.basename(file) for file in func_data.get('evidence', {}).get('files', [])[:2]]
                    evidence.extend(files)
                
                # Añadir a la tabla
                func_table.add_row(
                    func_name.capitalize(),
                    f"{confidence}%",
                    ", ".join(evidence[:3]) if evidence else "N/A"
                )
                
            # Mostrar tabla
            console.print(func_table)
            
            # Mostrar detalles adicionales para cada funcionalidad
            for func_name in main_functionalities:
                func_data = detected.get(func_name, {})
                evidence = func_data.get('evidence', {})
                
                cli.print_info(f"[bold]{func_name.capitalize()}[/bold] (Confianza: {func_data.get('confidence', 0)}%)")
                
                # Mostrar archivos relevantes
                files = evidence.get('files', [])
                if files:
                    console.print(f"  [dim]Archivos relevantes:[/dim]")
                    for i, file in enumerate(files[:5]):
                        console.print(f"    - {file}")
                    if len(files) > 5:
                        console.print(f"    ... y {len(files) - 5} más")
                
                # Mostrar importaciones detectadas
                imports = evidence.get('imports', [])
                if imports:
                    console.print(f"  [dim]Importaciones detectadas:[/dim]")
                    for i, imp in enumerate(imports[:5]):
                        console.print(f"    - {imp}")
                    if len(imports) > 5:
                        console.print(f"    ... y {len(imports) - 5} más")
                        
                console.print("")
        else:
            cli.print_warning("No se detectaron funcionalidades principales en el proyecto")
            
        # Mostrar funcionalidades con baja confianza
        low_confidence = [
            name for name, data in detected.items()
            if not data.get('present', False) and data.get('confidence', 0) > 30
        ]
        
        if low_confidence:
            cli.print_info("Funcionalidades con baja confianza de detección:")
            for func in low_confidence:
                confidence = detected[func].get('confidence', 0)
                console.print(f"  - {func.capitalize()}: {confidence}%")
        
        # Guardar resultados si se especificó un archivo de salida
        if output:
            output_path = output
            
            # Si no se especificó extensión, añadir .json
            if not output.endswith('.json'):
                output_path = f"{output}.json"
                
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                
            # Guardar en formato JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
                
            cli.print_success(f"Resultados guardados en: {output_path}")
            
    except Exception as e:
        cli.print_error(f"Error durante la detección de funcionalidades: {e}")
        logger.error(f"Error en detect_functionalities: {e}", exc_info=True)


@app.command()
def list(
    path: str = typer.Argument(".", help="Ruta al proyecto para listar funcionalidades"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Ruta para guardar el análisis en formato JSON"),
    max_files: int = typer.Option(5000, "--max-files", "-m", help="Número máximo de archivos a analizar"),
    max_size: float = typer.Option(3.0, "--max-size", "-s", help="Tamaño máximo de archivo a analizar en MB"),
    detailed: bool = typer.Option(False, "--detailed/--simple", "-d/-s", 
                               help="Mostrar información detallada de cada funcionalidad")
):
    """Listar las funcionalidades detectadas en un proyecto."""
    import json
    import os
    
    project_path = os.path.abspath(path)
    
    if not os.path.isdir(project_path):
        cli.print_error(f"La ruta especificada no es un directorio válido: {project_path}")
        return
    
    cli.print_header("Listado de Funcionalidades")
    cli.print_info(f"Analizando proyecto en: {project_path}")
    
    try:
        # Obtener funcionalidades
        functionality_data = analysis_view.list_functionalities(
            project_path, max_files=max_files, max_size=max_size
        )
        
        if not functionality_data:
            cli.print_error("No se pudieron detectar funcionalidades en el proyecto")
            return
        
        # Obtener funcionalidades principales
        main_functionalities = functionality_data.get('main_functionalities', [])
        detected = functionality_data.get('detected', {})
        
        if not main_functionalities:
            cli.print_warning("No se detectaron funcionalidades principales en el proyecto")
            low_confidence = [
                name for name, data in detected.items()
                if not data.get('present', False) and data.get('confidence', 0) > 30
            ]
            
            if low_confidence:
                cli.print_info("Posibles funcionalidades con baja confianza:")
                for func in low_confidence:
                    confidence = detected[func].get('confidence', 0)
                    console.print(f"  - {func.capitalize()}: {confidence}%")
            return
        
        # Mostrar funcionalidades detectadas
        if detailed:
            # Mostrar con todos los detalles
            analysis_view.show_functionalities(functionality_data)
        else:
            # Mostrar versión simplificada
            cli.print_success(f"Se detectaron {len(main_functionalities)} funcionalidades principales")
            
            # Crear tabla simple
            func_table = cli.create_table("Funcionalidades Detectadas", ["Funcionalidad", "Confianza"])
            
            for func_name in main_functionalities:
                func_data = detected.get(func_name, {})
                confidence = func_data.get('confidence', 0)
                func_table.add_row(func_name.capitalize(), f"{confidence}%")
            
            console.print(func_table)
            
            # Sugerir ver más detalles
            cli.print_info("Usa --detailed para ver información detallada de cada funcionalidad")
        
        # Guardar resultados si se especificó un archivo de salida
        if output:
            output_path = output
            
            # Si no se especificó extensión, añadir .json
            if not output.endswith('.json'):
                output_path = f"{output}.json"
                
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Guardar en formato JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(functionality_data, f, indent=2)
                
            cli.print_success(f"Listado de funcionalidades guardado en: {output_path}")
            
    except Exception as e:
        cli.print_error(f"Error al listar funcionalidades: {e}")
        logger.error(f"Error en list: {e}", exc_info=True)


@app.command()
def generate_prompts(
    path: str = typer.Argument(".", help="Ruta al proyecto para generar prompts"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Ruta para guardar los prompts en formato JSON"),
    premium: bool = typer.Option(False, "--premium", "-p", help="Usar características premium"),
    show: bool = typer.Option(True, "--show/--no-show", help="Mostrar prompts generados"),
    enhanced: bool = typer.Option(False, "--enhanced", "-e", help="Usar generador de prompts mejorado"),
    store: bool = typer.Option(True, "--store/--no-store", help="Guardar en la estructura del proyecto")
):
    """Generar prompts contextuales basados en el análisis del proyecto."""
    import json
    import os
    
    # Elegir el generador apropiado según los parámetros
    if enhanced:
        from src.generators.contextual_prompt_generator import get_contextual_prompt_generator as get_generator
    else:
        from src.generators.prompt_generator import get_prompt_generator as get_generator
    
    project_path = os.path.abspath(path)
    
    if not os.path.isdir(project_path):
        cli.print_error(f"La ruta especificada no es un directorio válido: {project_path}")
        return
        
    cli.print_header("Generación de Prompts Contextuales")
    
    # Mostrar información sobre generador mejorado
    if enhanced:
        cli.print_info("Utilizando generador de prompts contextuales mejorado")
    
    # Mostrar advertencia si se intenta usar premium en versión gratuita
    if premium:
        cli.print_warning("Las funciones premium no están disponibles en esta versión")
        premium = False
    
    cli.print_info(f"Analizando proyecto en: {project_path}")
    
    try:
        # Crear generador de prompts (básico o mejorado según la opción)
        generator = get_generator(is_premium=premium)
        
        # Verificar si queremos usar la estructura de archivos
        use_structure = store and not output
        
        # Obtener configuración del proyecto
        project_config = config_manager.config.copy() or {}
        project_config['project_name'] = os.path.basename(project_path)
        
        if use_structure:
            # Si queremos guardar en la estructura de archivos
            from src.utils.project_structure import get_project_structure
            structure = get_project_structure(project_path, project_config)
            
            # Verificar si existe la estructura
            structure_info = structure.get_structure_info()
            if not structure_info['exists']:
                # Crear la estructura si no existe
                cli.print_info("Creando estructura de archivos del proyecto...")
                structure.create_structure()
        
        # Mostrar progreso
        with cli.status("Analizando proyecto y generando prompts..."):
            # Generar prompts en memoria
            result = generator.generate_prompts(project_path)
            
            # Determinar dónde guardar los prompts
            if output:
                # Guardar en una ubicación específica
                prompt_path = generator.save_prompts(project_path, output)
            elif use_structure:
                # Guardar en la estructura de archivos
                prompts_data = result.get('prompts', {})
                
                # Guardar prompt general
                general_prompt = prompts_data.get('general', '')
                if general_prompt:
                    prompt_path = structure.save_prompt(general_prompt)
                    
                # Guardar prompts por funcionalidad
                functionality_prompts = prompts_data.get('functionalities', {})
                for func_name, func_prompt in functionality_prompts.items():
                    structure.save_functionality_prompt(func_name, func_prompt)
                
                prompt_path = os.path.join(structure.structure_root, 'prompts')
            else:
                # No guardar
                prompt_path = None
        
        # Mostrar resultado
        if prompt_path:
            cli.print_success(f"Prompts generados correctamente y guardados en: {prompt_path}")
        
        # Si se solicitó mostrar y hay resultado disponible
        if show and (result or output):
            prompts = result.get('prompts', {}) if result else {}
            
            # Si no hay resultado en memoria pero sí hay ruta de salida, cargar desde archivo
            if not prompts and output:
                try:
                    with open(prompt_path, 'r', encoding='utf-8') as f:
                        prompts = json.load(f).get('prompts', {})
                except Exception as e:
                    logger.error(f"Error al cargar prompts desde archivo: {e}", exc_info=True)
            
            # Mostrar cada prompt en un panel
            if prompts:
                cli.print_info("Prompts generados:")
                
                # Mostrar prompt de descripción
                if 'description' in prompts:
                    cli.print_panel(
                        "Prompt: Descripción del Proyecto",
                        prompts['description'],
                        "blue"
                    )
                
                # Mostrar prompt de mejoras
                if 'improvements' in prompts:
                    cli.print_panel(
                        "Prompt: Sugerencias de Mejora",
                        prompts['improvements'],
                        "cyan"
                    )
                
                # Mostrar prompt de problemas
                if 'issues' in prompts:
                    cli.print_panel(
                        "Prompt: Problemas Potenciales",
                        prompts['issues'],
                        "yellow"
                    )
                
                # Mostrar advertencia de límite freemium
                if not premium:
                    cli.print_info("Nota: Versión gratuita limitada a 3 prompts contextuales básicos")
        
        # Sugerir siguientes pasos
        cli.print_info("Para utilizar estos prompts:")
        console.print("  1. Copia el contenido del archivo de prompts")
        console.print("  2. Pégalo en tu asistente de IA favorito")
        console.print("  3. Añade tu pregunta específica al final del prompt")
            
    except Exception as e:
        cli.print_error(f"Error al generar prompts: {e}")
        logger.error(f"Error en generate_prompts: {e}", exc_info=True)


@app.command()
def docs(
    path: str = typer.Argument(".", help="Ruta al proyecto para generar documentación"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Ruta para guardar la documentación"),
    update: bool = typer.Option(False, "--update", "-u", help="Actualizar documentación existente"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Sobrescribir documentación existente"),
):
    """Generar documentación en markdown para el proyecto analizado."""
    import os
    from src.utils.documentation_system import get_documentation_system
    
    project_path = os.path.abspath(path)
    
    if not os.path.isdir(project_path):
        cli.print_error(f"La ruta especificada no es un directorio válido: {project_path}")
        return
    
    # Determinar directorio de documentación
    output_dir = output
    if not output_dir:
        output_dir = os.path.join(project_path, '.project-prompt')
    
    cli.print_header("Sistema de Documentación")
    cli.print_info(f"Generando documentación para proyecto en: {project_path}")
    
    # Verificar si ya existe documentación
    if os.path.exists(output_dir) and not update and not overwrite:
        cli.print_warning(f"Ya existe documentación en: {output_dir}")
        cli.print_info("Use --update para actualizar o --overwrite para sobrescribir")
        
        # Mostrar información básica
        try:
            doc_system = get_documentation_system()
            info = doc_system.get_documentation_info(output_dir)
            
            cli.print_panel(
                "Documentación Existente",
                f"Última actualización: {info.get('last_updated', 'Desconocida')}\n"
                f"Documentos: {info.get('document_count', 0)}\n"
                f"Funcionalidades: {len(info.get('functionalities', []))}"
            )
        except Exception as e:
            logger.error(f"Error al obtener info de documentación: {e}", exc_info=True)
            
        return
    
    try:
        with cli.status("Generando documentación..."):
            doc_system = get_documentation_system()
            
            if update and os.path.exists(output_dir):
                result = doc_system.update_documentation(project_path, output_dir)
                action = "actualizada"
            else:
                result = doc_system.generate_project_documentation(
                    project_path, output_dir, overwrite=overwrite
                )
                action = "generada"
        
        # Mostrar resultados
        cli.print_success(f"Documentación {action} exitosamente")
        cli.print_info(f"Directorio de documentación: {result['docs_dir']}")
        
        # Mostrar contenido generado
        cli.print_panel(
            "Documentos Generados",
            f"Análisis general: {os.path.basename(result['project_analysis'])}\n"
            f"Funcionalidades: {len(result['functionalities'])}\n"
            f"Configuración: {os.path.basename(result['config'])}"
        )
            
    except Exception as e:
        cli.print_error(f"Error al generar documentación: {e}")
        logger.error(f"Error en docs: {e}", exc_info=True)


@app.command()
def docs_list(
    path: str = typer.Argument(".", help="Ruta al proyecto con documentación"),
    pattern: str = typer.Option("**/*.md", "--pattern", "-p", help="Patrón para filtrar documentos")
):
    """Listar documentos de la documentación generada."""
    import os
    from tabulate import tabulate
    from src.utils.markdown_manager import get_markdown_manager
    
    project_path = os.path.abspath(path)
    
    if not os.path.isdir(project_path):
        cli.print_error(f"La ruta especificada no es un directorio válido: {project_path}")
        return
    
    # Determinar directorio de documentación
    docs_dir = os.path.join(project_path, '.project-prompt')
    if not os.path.exists(docs_dir):
        cli.print_error(f"No se encontró documentación en: {docs_dir}")
        cli.print_info(f"Genere documentación primero con: project-prompt docs {project_path}")
        return
    
    cli.print_header("Listado de Documentación")
    
    try:
        # Obtener listado de documentos
        markdown_manager = get_markdown_manager()
        docs = markdown_manager.list_documents(docs_dir, pattern)
        
        if not docs:
            cli.print_warning(f"No se encontraron documentos con el patrón: {pattern}")
            return
            
        # Preparar tabla para mostrar
        table_data = []
        for doc in docs:
            rel_path = doc.get('relative_path', '')
            updated = doc.get('updated', doc.get('modified', 'Desconocido'))
            version = doc.get('version', '-')
            word_count = doc.get('word_count', 0)
            
            table_data.append([
                rel_path,
                version,
                word_count,
                updated
            ])
                
        # Mostrar tabla
        table = tabulate(
            table_data,
            headers=["Documento", "Versión", "Palabras", "Actualizado"],
            tablefmt="fancy_grid"
        )
        console.print(table)
        cli.print_info(f"Total de documentos: {len(docs)}")
            
    except Exception as e:
        cli.print_error(f"Error al listar documentación: {e}")
        logger.error(f"Error en docs_list: {e}", exc_info=True)


@app.command()
def docs_view(
    doc_path: str = typer.Argument(..., help="Ruta relativa al documento dentro de .project-prompt"),
    project: str = typer.Option(".", "--project", "-p", help="Ruta al proyecto con documentación")
):
    """Ver un documento específico de la documentación."""
    import os
    import re
    from rich.markdown import Markdown
    from src.utils.markdown_manager import get_markdown_manager
    
    project_path = os.path.abspath(project)
    
    if not os.path.isdir(project_path):
        cli.print_error(f"La ruta del proyecto no es válida: {project_path}")
        return
    
    # Determinar ruta completa al documento
    docs_dir = os.path.join(project_path, '.project-prompt')
    if not os.path.exists(docs_dir):
        cli.print_error(f"No se encontró documentación en: {docs_dir}")
        return
    
    # Asegurar que la extensión sea .md
    if not doc_path.endswith('.md'):
        doc_path = f"{doc_path}.md"
        
    # Construir ruta completa
    full_path = os.path.join(docs_dir, doc_path)
    if not os.path.exists(full_path):
        cli.print_error(f"No se encontró el documento: {doc_path}")
        cli.print_info(f"Use 'project-prompt docs_list' para ver documentos disponibles")
        return
    
    try:
        # Leer contenido del documento
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraer frontmatter si existe
        frontmatter_match = re.match(r'---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if frontmatter_match:
            content = content[len(frontmatter_match.group(0)):]
        
        # Mostrar documento
        cli.print_header(f"Documento: {doc_path}")
        console.print(Markdown(content))
        
    except Exception as e:
        cli.print_error(f"Error al mostrar documento: {e}")
        logger.error(f"Error en docs_view: {e}", exc_info=True)


@app.command()
def connections(
    path: str = typer.Argument(".", help="Ruta al proyecto para analizar conexiones"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Ruta para guardar el análisis en formato JSON"),
    max_files: int = typer.Option(5000, "--max-files", "-m", help="Número máximo de archivos a analizar"),
    detailed: bool = typer.Option(False, "--detailed/--simple", "-d/-s", help="Mostrar información detallada")
):
    """Analiza las conexiones entre archivos de un proyecto."""
    import os
    from src.ui import analysis_view
    from src.ui.analysis_view import AnalysisView, analyze_connections
    
    project_path = os.path.abspath(path)
    
    if not os.path.isdir(project_path):
        cli.print_error(f"La ruta especificada no es un directorio válido: {project_path}")
        return
    
    cli.print_header("Análisis de Conexiones Entre Archivos")
    cli.print_info(f"Analizando proyecto en: {project_path}")
    
    try:
        # Analizar conexiones
        with cli.status("Analizando conexiones entre archivos..."):
            connections_data = analyze_connections(
                project_path, max_files=max_files, output=output
            )
        
        # Mostrar resultados
        analysis_view.show_connections_analysis(connections_data, detailed=detailed)
        
        if output:
            cli.print_success(f"Análisis de conexiones guardado en: {output}")
            
    except Exception as e:
        cli.print_error(f"Error durante el análisis de conexiones: {e}")
        logger.error(f"Error en connections: {e}", exc_info=True)


@app.command()
def dependency_graph(
    path: str = typer.Argument(".", help="Ruta al proyecto para generar grafo"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Ruta para guardar el grafo en formato JSON"),
    markdown: Optional[str] = typer.Option(None, "--markdown", "-md", help="Ruta para guardar visualización en markdown"),
    max_files: int = typer.Option(5000, "--max-files", "-m", help="Número máximo de archivos a analizar"),
    detailed: bool = typer.Option(False, "--detailed/--simple", "-d/-s", help="Mostrar información detallada")
):
    """Genera un grafo de dependencias entre archivos de un proyecto."""
    import os
    from src.ui import analysis_view
    
    project_path = os.path.abspath(path)
    
    if not os.path.isdir(project_path):
        cli.print_error(f"La ruta especificada no es un directorio válido: {project_path}")
        return
    
    cli.print_header("Generación de Grafo de Dependencias")
    cli.print_info(f"Analizando proyecto en: {project_path}")
    
    try:
        # Generar grafo
        with cli.status("Generando grafo de dependencias..."):
            graph_data = analysis_view.generate_dependency_graph(
                project_path, max_files=max_files, output=output, markdown_output=markdown
            )
        
        # Mostrar resultados
        analysis_view.show_dependency_graph(graph_data, detailed=detailed)
        
        if output:
            cli.print_success(f"Grafo de dependencias guardado en: {output}")
            
        if markdown:
            cli.print_success(f"Visualización markdown guardada en: {markdown}")
            
    except Exception as e:
        cli.print_error(f"Error durante la generación del grafo: {e}")
        logger.error(f"Error en dependency_graph: {e}", exc_info=True)


@app.command()
def project_structure(
    path: str = typer.Argument(".", help="Ruta al proyecto para crear/gestionar estructura"),
    init: bool = typer.Option(False, "--init", "-i", help="Inicializar la estructura del proyecto"),
    info: bool = typer.Option(False, "--info", help="Mostrar información de la estructura existente"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Sobrescribir estructura existente"),
    clean: bool = typer.Option(False, "--clean", help="Eliminar la estructura completa"),
):
    """Gestionar la estructura de archivos del proyecto."""
    from src.utils.project_structure import get_project_structure
    
    project_path = os.path.abspath(path)
    
    if not os.path.isdir(project_path):
        cli.print_error(f"La ruta especificada no es un directorio válido: {project_path}")
        return
    
    cli.print_header("Estructura de Archivos del Proyecto")
    cli.print_info(f"Proyecto: {project_path}")
    
    # Obtener configuración del proyecto
    project_config = config_manager.config.copy() or {}
    project_config['project_name'] = os.path.basename(project_path)
    
    # Inicializar gestor de estructura
    structure = get_project_structure(project_path, project_config)
    
    # Ejecutar acción solicitada
    try:
        if clean:
            with cli.status("Eliminando estructura..."):
                result = structure.clear_structure(confirm=True)
            
            if result:
                cli.print_success("Estructura eliminada correctamente.")
            else:
                cli.print_warning("No había estructura que eliminar.")
            return
        
        if init:
            with cli.status("Inicializando estructura de proyecto..."):
                result = structure.create_structure(overwrite=overwrite)
            
            # Mostrar resultado de la inicialización
            cli.print_success(f"Estructura creada en: {result['structure_root']}")
            cli.print_info(f"Directorios creados: {len(result['directories_created'])}")
            cli.print_info(f"Archivos creados: {len(result['files_created'])}")
            
            # Mostrar la estructura creada
            structure_tree = cli.create_tree("Estructura del proyecto")
            root_node = structure_tree.add(".project-prompt")
            root_node.add("project-analysis.md")
            root_node.add("config.yaml")
            func_node = root_node.add("functionalities/")
            prompts_node = root_node.add("prompts/")
            prompts_node.add("general.md")
            prompts_node.add("functionality/")
            
            console.print(structure_tree)
            return
        
        # Si no se especificó ninguna acción, mostrar información
        if info or not (init or clean):
            with cli.status("Analizando estructura existente..."):
                structure_info = structure.get_structure_info()
            
            if not structure_info['exists']:
                cli.print_warning("No existe estructura de proyecto ProjectPrompt.")
                cli.print_info("Use el comando 'project-structure --init' para crear la estructura.")
                return
            
            # Mostrar información de la estructura
            cli.print_success(f"Estructura encontrada en: {structure_info['structure_root']}")
            
            # Crear tabla con información
            table = cli.create_table("Detalles de la estructura", ["Elemento", "Valor"])
            table.add_row("Directorios", str(structure_info['directories_count']))
            table.add_row("Archivos", str(structure_info['files_count']))
            table.add_row("Análisis de proyecto", "Disponible ✅" if structure_info['has_analysis'] else "No disponible ❌")
            table.add_row("Configuración", "Disponible ✅" if structure_info['has_config'] else "No disponible ❌")
            
            # Funcionalidades
            func_str = ", ".join(structure_info['functionalities']) if structure_info['functionalities'] else "Ninguna"
            table.add_row("Funcionalidades", func_str)
            
            # Prompts
            prompts_str = ", ".join(structure_info['prompts']) if structure_info['prompts'] else "Ninguno"
            table.add_row("Prompts de funcionalidad", prompts_str)
            
            console.print(table)
            return
    
    except Exception as e:
        cli.print_error(f"Error al gestionar la estructura: {e}")
        logger.error(f"Error en project_structure: {e}", exc_info=True)


@app.command()
def functionality_files(
    name: str = typer.Argument(..., help="Nombre de la funcionalidad"),
    path: str = typer.Option(".", "--path", "-p", help="Ruta al proyecto"),
    description: str = typer.Option(None, "--description", "-d", help="Descripción corta de la funcionalidad")
):
    """Crear archivos de análisis y prompts para una funcionalidad específica."""
    from src.utils.project_structure import get_project_structure
    
    project_path = os.path.abspath(path)
    
    if not os.path.isdir(project_path):
        cli.print_error(f"La ruta especificada no es un directorio válido: {project_path}")
        return
    
    cli.print_header(f"Creando archivos para funcionalidad: {name}")
    
    # Obtener configuración del proyecto
    project_config = config_manager.config.copy() or {}
    project_config['project_name'] = os.path.basename(project_path)
    
    # Inicializar gestor de estructura
    structure = get_project_structure(project_path, project_config)
    
    # Verificar si existe la estructura
    structure_info = structure.get_structure_info()
    
    if not structure_info['exists']:
        cli.print_warning("No existe estructura de proyecto ProjectPrompt.")
        if typer.confirm("¿Desea crear la estructura primero?"):
            structure.create_structure()
            cli.print_success("Estructura creada correctamente.")
        else:
            return
    
    # Descripción por defecto si no se proporciona
    if not description:
        description = f"Funcionalidad {name} del proyecto {project_config['project_name']}"
    
    try:
        # Crear contenido para el análisis de la funcionalidad
        analysis_content = f"""# Análisis de funcionalidad: {name}

## Descripción
{description}

## Archivos relacionados
*Este campo se completará al ejecutar el análisis detallado de la funcionalidad.*

## Dependencias
*Este campo se completará al ejecutar el análisis detallado de la funcionalidad.*

## Notas adicionales
*Espacio para notas y observaciones sobre la funcionalidad.*
"""

        # Crear contenido para el prompt de la funcionalidad
        prompt_content = f"""# Prompt para funcionalidad: {name}

## Descripción de la funcionalidad
{description}

## Contexto y referencias
*Este campo se completará al generar los prompts contextuales.*

## Instrucciones específicas
*Este campo contendrá instrucciones específicas para trabajar con esta funcionalidad.*

## Ejemplos de código relevantes
*Este campo mostrará ejemplos de código relacionados con la funcionalidad.*
"""

        # Guardar los archivos
        with cli.status("Creando archivos..."):
            analysis_path = structure.save_functionality_analysis(name, analysis_content)
            prompt_path = structure.save_functionality_prompt(name, prompt_content)
        
        cli.print_success("Archivos creados correctamente:")
        cli.print_info(f"Análisis: {os.path.relpath(analysis_path, project_path)}")
        cli.print_info(f"Prompt: {os.path.relpath(prompt_path, project_path)}")
        
    except Exception as e:
        cli.print_error(f"Error al crear archivos para la funcionalidad: {e}")
        logger.error(f"Error en functionality_files: {e}", exc_info=True)


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
