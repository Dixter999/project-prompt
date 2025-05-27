#!/usr/bin/env python3
"""
Punto de entrada principal para ProjectPrompt.

Este script proporciona las funcionalidades principales de la herramienta ProjectPrompt,
permitiendo analizar proyectos, generar sugerencias con IA, y gestionar configuraciones.

Los resultados se guardan en la carpeta 'project-output'.
"""

import os
import sys
import json
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pathlib import Path

import typer
from rich.console import Console

from src import __version__
from src.utils import logger, config_manager, LogLevel, set_level
from src.utils.api_validator import get_api_validator
from src.utils.updater import Updater, check_and_notify_updates
from src.utils.sync_manager import SyncManager, get_sync_manager
from src.utils.telemetry import initialize_telemetry, shutdown_telemetry, get_telemetry_manager, record_command, record_error
from src.ui import menu
from src.ui.cli import cli
from src.ui.consent_manager import ConsentManager
from src.ui.analysis_view import analysis_view
from src.ui.documentation_navigator import get_documentation_navigator
from src.ui.subscription_view import show_subscription, activate_license, deactivate_license, show_plans
from src.ui.dashboard import DashboardCLI
# Importamos los analizadores bajo demanda para evitar carga innecesaria

# Define project directories
PROJECT_ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = PROJECT_ROOT / "project-output"
ANALYSES_DIR = OUTPUT_DIR / "analyses"
SUGGESTIONS_DIR = OUTPUT_DIR / "suggestions"

# Create output directories if they don't exist
os.makedirs(ANALYSES_DIR, exist_ok=True)
os.makedirs(SUGGESTIONS_DIR, exist_ok=True)

console = Console()
app = typer.Typer(help="ProjectPrompt: Asistente inteligente para proyectos")

# Submenu para comandos de documentación
docs_app = typer.Typer(help="Comandos de navegación de documentación")
app.add_typer(docs_app, name="docs")

# Submenu para comandos de IA avanzada
ai_app = typer.Typer(help="Comandos premium de IA (Copilot/Anthropic)")
app.add_typer(ai_app, name="ai")

# Submenu para comandos de suscripción
subscription_app = typer.Typer(help="Comandos para gestionar la suscripción")
app.add_typer(subscription_app, name="subscription")

# Submenu para comandos de actualización y sincronización
update_app = typer.Typer(help="Comandos para gestionar actualizaciones y sincronización")
app.add_typer(update_app, name="update")

# Submenu para comandos premium 
premium_app = typer.Typer(help="Comandos premium para acceso a funcionalidades avanzadas")
app.add_typer(premium_app, name="premium")

# Submenu para comandos de telemetría
telemetry_app = typer.Typer(help="Comandos para gestionar la telemetría anónima")
app.add_typer(telemetry_app, name="telemetry")

# Decorador para telemetría de comandos
import time
import functools
import inspect

def telemetry_command(func):
    """
    Decorador para registrar el uso de comandos en telemetría.
    También registra errores que ocurran durante la ejecución.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        telemetry_enabled = get_telemetry_manager().is_enabled()
        command_name = func.__name__
        start_time = time.time()
        
        try:
            # Ejecutar el comando original
            result = func(*args, **kwargs)
            
            # Registrar telemetría solo si está habilitada
            if telemetry_enabled:
                duration_ms = int((time.time() - start_time) * 1000)
                record_command(command_name, duration_ms)
                
            return result
        except Exception as e:
            # Registrar el error si la telemetría está habilitada
            if telemetry_enabled:
                error_type = type(e).__name__
                error_msg = str(e)
                
                # Obtener información del archivo y línea donde ocurrió el error
                # Solo para errores en nuestro código, no en librerías externas
                file = None
                line = None
                tb = getattr(e, '__traceback__', None)
                while tb:
                    if 'src' in tb.tb_frame.f_code.co_filename:
                        file = tb.tb_frame.f_code.co_filename
                        line = tb.tb_lineno
                        break
                    tb = tb.tb_next
                
                record_error(error_type, error_msg, file, line)
                
            # Re-lanzar la excepción para mantener el comportamiento normal
            raise
    
    return wrapper


@app.command()
@telemetry_command
def version():
    """Show the current version of ProjectPrompt."""
    cli.print_header("Version Information")
    cli.print_info(f"ProjectPrompt v{__version__}")
    
    # Check APIs status
    validator = get_api_validator()
    status = validator.get_status_summary()
    
    # Show additional information
    table = cli.create_table("Details", ["Component", "Version/Status"])
    table.add_row("Python", sys.version.split()[0])
    
    # API Status with helpful guidance messages
    anthropic_configured = status.get("anthropic", False)
    github_configured = status.get("github", False)
    
    table.add_row("API Anthropic", "Configured ✅" if anthropic_configured else "Not configured ❌")
    table.add_row("API GitHub", "Configured ✅" if github_configured else "Not configured ❌")
    console.print(table)
    
    # Show helpful guidance if APIs are not configured
    if not anthropic_configured or not github_configured:
        console.print("\n[bold yellow]💡 Consejos para resolución de problemas:[/bold yellow]")
        
        if not anthropic_configured:
            console.print("  • Para configurar Anthropic API: [bold]project-prompt set-api anthropic[/bold]")
        
        if not github_configured:
            console.print("  • Para configurar GitHub API: [bold]project-prompt set-api github[/bold]")
            
        console.print("  • Para verificar el estado de las APIs: [bold]project-prompt verify-api[/bold]")
        console.print("  • Las advertencias de conexión con el servidor son normales si no hay conexión a Internet")
        console.print("    ProjectPrompt funciona completamente sin conexión con sus características básicas.")


@app.command()
def init(name: str = typer.Option(None, "--name", "-n", help="Project name"),
         path: str = typer.Option(".", "--path", "-p", help="Path to initialize")):
    """Initialize a new project with ProjectPrompt."""
    cli.print_header("Project Initialization")
    
    # Si no se proporciona un nombre, solicitarlo
    if not name:
        name = typer.prompt("Nombre del proyecto")
    
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
    table.add_row("interview", "Realizar entrevista guiada sobre una funcionalidad")
    table.add_row("analyze-feature", "Analizar funcionalidad específica")
    table.add_row("list-interviews", "Listar entrevistas existentes")
    table.add_row("implementation-proposal", "Generar propuesta de implementación")
    table.add_row("implementation-prompt", "Generar prompt detallado para implementación (premium)")
    table.add_row("generate_prompts", "Generar prompts contextuales del proyecto")
    table.add_row("set-log-level", "Cambiar el nivel de logging")
    table.add_row("menu", "Iniciar el menú interactivo")
    table.add_row("dashboard", "Generar dashboard básico del proyecto")
    table.add_row("subscription", "Gestionar suscripción premium")
    table.add_row("premium", "Acceder a comandos premium")
    table.add_row("help", "Mostrar esta ayuda")
    
    # Comandos premium
    premium_table = cli.create_table("Comandos Premium", ["Comando", "Descripción"])
    premium_table.add_row("premium dashboard", "Dashboard avanzado interactivo")
    premium_table.add_row("premium test-generator", "Generador de tests unitarios")
    premium_table.add_row("premium verify-completeness", "Verificador de completitud")
    premium_table.add_row("premium implementation", "Asistente de implementación")
    console.print(premium_table)
    console.print(table)
    
    cli.print_info("Para más información sobre un comando específico, use:")
    console.print("  project-prompt [COMANDO] --help")


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


# Decorador para telemetría de comandos
import time
import functools
import inspect

def telemetry_command(func):
    """
    Decorador para registrar el uso de comandos en telemetría.
    También registra errores que ocurran durante la ejecución.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        telemetry_enabled = get_telemetry_manager().is_enabled()
        command_name = func.__name__
        start_time = time.time()
        
        try:
            # Ejecutar el comando original
            result = func(*args, **kwargs)
            
            # Registrar telemetría solo si está habilitada
            if telemetry_enabled:
                duration_ms = int((time.time() - start_time) * 1000)
                record_command(command_name, duration_ms)
                
            return result
        except Exception as e:
            # Registrar el error si la telemetría está habilitada
            if telemetry_enabled:
                error_type = type(e).__name__
                error_msg = str(e)
                
                # Obtener información del archivo y línea donde ocurrió el error
                # Solo para errores en nuestro código, no en librerías externas
                file = None
                line = None
                tb = getattr(e, '__traceback__', None)
                while tb:
                    if 'src' in tb.tb_frame.f_code.co_filename:
                        file = tb.tb_frame.f_code.co_filename
                        line = tb.tb_lineno
                        break
                    tb = tb.tb_next
                
                record_error(error_type, error_msg, file, line)
                
            # Re-lanzar la excepción para mantener el comportamiento normal
            raise
    
    return wrapper


# Implementación de comandos de IA
@ai_app.command("generate")
@telemetry_command
def ai_generate_code(
    description: str = typer.Argument(..., help="Descripción del código a generar"),
    language: str = typer.Option("python", "--language", "-l", help="Lenguaje de programación"),
    provider: str = typer.Option("anthropic", "--provider", "-p", 
                                help="Proveedor de IA (anthropic, copilot)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Archivo donde guardar el código")
):
    """
    Generar código utilizando IA avanzada (característica premium).
    """
    from src.integrations.anthropic_advanced import get_advanced_anthropic_client
    from src.integrations.copilot_advanced import get_advanced_copilot_client
    from src.utils.subscription_manager import get_subscription_manager
    
    cli.print_header("Generación de Código con IA")
    
    # Verificar suscripción
    subscription = get_subscription_manager()
    if not subscription.is_premium_feature_available("ai_integrations"):
        cli.print_error("Esta es una característica premium. Actualiza tu suscripción para acceder.")
        return
    
    # Seleccionar cliente según proveedor
    if provider.lower() == "anthropic":
        client = get_advanced_anthropic_client()
        provider_name = "Anthropic Claude"
    elif provider.lower() == "copilot":
        client = get_advanced_copilot_client()
        provider_name = "GitHub Copilot"
    else:
        cli.print_error(f"Proveedor no soportado: {provider}")
        return
    
    cli.print_info(f"Utilizando {provider_name} para generar código {language}")
    
    with cli.status(f"Generando código {language} con {provider_name}..."):
        result = client.generate_code(description, language)
    
    if result.get("success"):
        code = result.get("code", "")
        
        # Mostrar código generado
        cli.print_success("Código generado exitosamente:")
        console.print("")
        console.print(f"```{language}")
        console.print(code)
        console.print("```")
        console.print("")
        
        # Guardar a archivo si se especificó
        if output:
            try:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(code)
                cli.print_success(f"Código guardado en: {output}")
            except Exception as e:
                cli.print_error(f"Error al guardar código: {e}")
    else:
        cli.print_error(f"Error al generar código: {result.get('error', 'Error desconocido')}")


@ai_app.command("analyze")
@telemetry_command
def ai_analyze_code(
    file_path: str = typer.Argument(..., help="Ruta al archivo de código a analizar"),
    language: Optional[str] = typer.Option(None, "--language", "-l", help="Lenguaje de programación"),
    provider: str = typer.Option("anthropic", "--provider", "-p", 
                               help="Proveedor de IA (anthropic, copilot)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", 
                                       help="Archivo donde guardar el análisis")
):
    """
    Analizar código para detectar errores y problemas (característica premium).
    """
    from src.integrations.anthropic_advanced import get_advanced_anthropic_client
    from src.integrations.copilot_advanced import get_advanced_copilot_client
    from src.utils.subscription_manager import get_subscription_manager
    import os
    
    cli.print_header("Análisis de Código con IA")
    
    # Verificar suscripción
    subscription = get_subscription_manager()
    if not subscription.is_premium_feature_available("ai_integrations"):
        cli.print_error("Esta es una característica premium. Actualiza tu suscripción para acceder.")
        return
    
    # Verificar archivo
    if not os.path.isfile(file_path):
        cli.print_error(f"El archivo no existe: {file_path}")
        return
    
    # Determinar lenguaje si no se especificó
    if not language:
        _, ext = os.path.splitext(file_path)
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cs': 'csharp',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
        }
        language = language_map.get(ext.lower(), 'unknown')
        if language == 'unknown':
            cli.print_warning(f"No se pudo determinar el lenguaje para la extensión {ext}")
            language = 'python'  # Valor predeterminado
    
    # Leer contenido del archivo
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except Exception as e:
        cli.print_error(f"Error al leer archivo: {e}")
        return
    
    # Seleccionar cliente según proveedor
    if provider.lower() == "anthropic":
        client = get_advanced_anthropic_client()
        provider_name = "Anthropic Claude"
    elif provider.lower() == "copilot":
        client = get_advanced_copilot_client()
        provider_name = "GitHub Copilot"
    else:
        cli.print_error(f"Proveedor no soportado: {provider}")
        return
    
    cli.print_info(f"Analizando código {language} con {provider_name}")
    
    with cli.status(f"Analizando código..."):
        result = client.detect_errors(code, language)
    
    if result.get("success"):
        issues = result.get("issues", [])
        
        if issues:
            # Crear tabla con problemas detectados
            issues_table = cli.create_table(
                "Problemas Detectados", 
                ["Tipo", "Descripción", "Ubicación", "Severidad", "Solución"]
            )
            
            for issue in issues:
                issues_table.add_row(
                    issue.get("type", ""),
                    issue.get("description", ""),
                    issue.get("location", ""),
                    issue.get("severity", ""),
                    issue.get("fix", "")
                )
            
            console.print(issues_table)
            cli.print_info(f"Se detectaron {len(issues)} problemas en el código.")
        else:
            cli.print_success("No se detectaron problemas en el código.")
        
        # Guardar análisis si se especificó
        if output:
            try:
                import json
                with open(output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2)
                cli.print_success(f"Análisis guardado en: {output}")
            except Exception as e:
                cli.print_error(f"Error al guardar análisis: {e}")
    else:
        cli.print_error(f"Error al analizar código: {result.get('error', 'Error desconocido')}")


@ai_app.command("refactor")
@telemetry_command
def ai_refactor_code(
    file_path: str = typer.Argument(..., help="Ruta al archivo de código a refactorizar"),
    language: Optional[str] = typer.Option(None, "--language", "-l", help="Lenguaje de programación"),
    provider: str = typer.Option("anthropic", "--provider", "-p", 
                               help="Proveedor de IA (anthropic, copilot)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", 
                                       help="Archivo donde guardar el código refactorizado")
):
    """
    Refactorizar código para mejorar su calidad (característica premium).
    """
    from src.integrations.anthropic_advanced import get_advanced_anthropic_client
    from src.integrations.copilot_advanced import get_advanced_copilot_client
    from src.utils.subscription_manager import get_subscription_manager
    import os
    
    cli.print_header("Refactorización de Código con IA")
    
    # Verificar suscripción
    subscription = get_subscription_manager()
    if not subscription.is_premium_feature_available("ai_integrations"):
        cli.print_error("Esta es una característica premium. Actualiza tu suscripción para acceder.")
        return
    
    # Verificar archivo
    if not os.path.isfile(file_path):
        cli.print_error(f"El archivo no existe: {file_path}")
        return
    
    # Determinar lenguaje si no se especificó
    if not language:
        _, ext = os.path.splitext(file_path)
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cs': 'csharp',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
        }
        language = language_map.get(ext.lower(), 'unknown')
        if language == 'unknown':
            cli.print_warning(f"No se pudo determinar el lenguaje para la extensión {ext}")
            language = 'python'  # Valor predeterminado
    
    # Leer contenido del archivo
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except Exception as e:
        cli.print_error(f"Error al leer archivo: {e}")
        return
    
    # Seleccionar cliente según proveedor
    if provider.lower() == "anthropic":
        client = get_advanced_anthropic_client()
        provider_name = "Anthropic Claude"
    elif provider.lower() == "copilot":
        client = get_advanced_copilot_client()
        provider_name = "GitHub Copilot"
    else:
        cli.print_error(f"Proveedor no soportado: {provider}")
        return
    
    cli.print_info(f"Refactorizando código {language} con {provider_name}")
    
    with cli.status(f"Refactorizando código..."):
        result = client.suggest_refactoring(code, language)
    
    if result.get("success"):
        refactored_code = result.get("refactored_code", "")
        suggestions = result.get("suggestions", [])
        
        # Mostrar código refactorizado
        cli.print_success("Código refactorizado:")
        console.print("")
        console.print(f"```{language}")
        console.print(refactored_code)
        console.print("```")
        console.print("")
        
        # Mostrar sugerencias
        if suggestions:
            cli.print_info("Mejoras realizadas:")
            for i, suggestion in enumerate(suggestions):
                console.print(f"  {i+1}. {suggestion}")
        
        # Guardar a archivo si se especificó
        if output:
            try:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(refactored_code)
                cli.print_success(f"Código refactorizado guardado en: {output}")
            except Exception as e:
                cli.print_error(f"Error al guardar código: {e}")
    else:
        cli.print_error(f"Error al refactorizar código: {result.get('error', 'Error desconocido')}")


@ai_app.command("explain")
@telemetry_command
def ai_explain_code(
    file_path: str = typer.Argument(..., help="Ruta al archivo de código a explicar"),
    language: Optional[str] = typer.Option(None, "--language", "-l", help="Lenguaje de programación"),
    detail_level: str = typer.Option("standard", "--detail", "-d", 
                                   help="Nivel de detalle (basic, standard, advanced)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", 
                                       help="Archivo donde guardar la explicación")
):
    """
    Generar una explicación detallada del código (característica premium para nivel avanzado).
    """
    from src.integrations.anthropic_advanced import get_advanced_anthropic_client
    from src.utils.subscription_manager import get_subscription_manager
    import os
    
    cli.print_header("Explicación de Código con IA")
    
    # Verificar suscripción para nivel avanzado
    if detail_level == "advanced":
        subscription = get_subscription_manager()
        if not subscription.is_premium_feature_available("ai_integrations"):
            cli.print_warning("El nivel avanzado requiere suscripción premium. Usando nivel estándar.")
            detail_level = "standard"
    
    # Verificar archivo
    if not os.path.isfile(file_path):
        cli.print_error(f"El archivo no existe: {file_path}")
        return
    
    # Determinar lenguaje si no se especificó
    if not language:
        _, ext = os.path.splitext(file_path)
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cs': 'csharp',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
        }
        language = language_map.get(ext.lower(), 'unknown')
        if language == 'unknown':
            cli.print_warning(f"No se pudo determinar el lenguaje para la extensión {ext}")
            language = 'python'  # Valor predeterminado
    
    # Leer contenido del archivo
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except Exception as e:
        cli.print_error(f"Error al leer archivo: {e}")
        return
    
    # Usar Anthropic para la explicación
    client = get_advanced_anthropic_client()
    
    cli.print_info(f"Generando explicación de código {language} (nivel {detail_level})")
    
    with cli.status(f"Analizando y explicando código..."):
        result = client.explain_code(code, language, detail_level)
    
    if result.get("success"):
        explanation = result.get("explanation", "")
        
        # Mostrar explicación
        cli.print_success(f"Explicación del código ({os.path.basename(file_path)}):")
        console.print("")
        console.print(explanation)
        console.print("")
        
        # Guardar a archivo si se especificó
        if output:
            try:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(explanation)
                cli.print_success(f"Explicación guardada en: {output}")
            except Exception as e:
                cli.print_error(f"Error al guardar explicación: {e}")
    else:
        cli.print_error(f"Error al explicar código: {result.get('error', 'Error desconocido')}")


@app.command()
def dashboard(
    project: str = typer.Argument(".", help="Ruta al proyecto para generar el dashboard"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Ruta donde guardar el dashboard HTML"),
    no_browser: bool = typer.Option(False, "--no-browser", help="No abrir automáticamente en el navegador")
):
    """Generar un dashboard visual con el estado y progreso del proyecto."""
    cli.print_header("Dashboard de Progreso del Proyecto")
    
    # Sugerir versión premium para acceso a todas las características
    cli.print_info("ProjectPrompt ofrece una versión premium del dashboard con características adicionales.")
    cli.print_info("Para acceder a todas las funcionalidades como seguimiento de branches, progreso por característica")
    cli.print_info("y recomendaciones proactivas, use: 'project-prompt premium dashboard'")
    console.print("")
    
    try:
        # Crear instancia del CLI del dashboard
        dashboard_cli = DashboardCLI()
        
        # Configurar argumentos
        args = []
        if project != ".":
            args.extend(["--project", project])
        if output:
            args.extend(["--output", output])
        if no_browser:
            args.append("--no-browser")
            
        # Ejecutar el dashboard
        result = dashboard_cli.run(args)
        
        if result != 0:
            cli.print_error("Error al generar el dashboard")
            return
            
    except Exception as e:
        cli.print_error(f"Error al generar el dashboard: {str(e)}")
        logger.error(f"Error en dashboard: {str(e)}", exc_info=True)


# Implementación de comandos de suscripción
@subscription_app.command("info")
def subscription_info():
    """Mostrar información de la suscripción actual."""
    show_subscription()


@subscription_app.command("activate")
def subscription_activate(
    license_key: str = typer.Argument(..., help="Clave de licencia a activar")
):
    """Activar una licencia premium."""
    activate_license(license_key)


@subscription_app.command("deactivate")
def subscription_deactivate():
    """Desactivar la licencia actual y volver a la versión gratuita."""
    deactivate_license()


@subscription_app.command("plans")
def subscription_plans():
    """Mostrar los planes de suscripción disponibles."""
    show_plans()


# Implementación de comandos premium

@premium_app.command("dashboard")
def premium_dashboard(
    project: str = typer.Argument(".", help="Ruta al proyecto para generar el dashboard"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Ruta donde guardar el dashboard HTML"),
    no_browser: bool = typer.Option(False, "--no-browser", help="No abrir automáticamente en el navegador")
):
    """Genera un dashboard visual interactivo con el estado y progreso del proyecto (característica premium)."""
    from src.utils.subscription_manager import get_subscription_manager
    
    cli.print_header("Dashboard Premium de Proyecto")
    
    # Verificar suscripción
    subscription = get_subscription_manager()
    if not subscription.can_use_feature("project_dashboard"):
        cli.check_premium_feature("project_dashboard")
        return
    
    # Crear instancia del CLI del dashboard
    dashboard_cli = DashboardCLI()
    
    # Configurar argumentos
    args = []
    if project != ".":
        args.extend(["--project", project])
    if output:
        args.extend(["--output", output])
    if no_browser:
        args.append("--no-browser")
    
    # Ejecutar dashboard
    dashboard_cli.run(args)


@premium_app.command("test-generator")
def premium_generate_tests(
    target: str = typer.Argument(..., help="Archivo o directorio para generar tests"),
    output_dir: str = typer.Option("tests", "--output-dir", "-o", help="Directorio donde guardar los tests generados"),
    framework: str = typer.Option("auto", "--framework", "-f", help="Framework de tests (pytest, unittest, jest, auto)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Mostrar información detallada")
):
    """Genera tests unitarios automáticamente para un componente o archivo (característica premium)."""
    from src.generators.test_generator import TestGenerator
    from src.utils.subscription_manager import get_subscription_manager
    import os
    
    cli.print_header("Generación de Tests Unitarios")
    
    # Verificar suscripción
    subscription = get_subscription_manager()
    if not subscription.can_use_feature("test_generation"):
        cli.check_premium_feature("test_generation")
        return
    
    # Verificar que el objetivo existe
    target_path = os.path.abspath(target)
    if not os.path.exists(target_path):
        cli.print_error(f"El archivo o directorio no existe: {target_path}")
        return
    
    # Configurar generador de tests
    config = {
        "output_dir": output_dir,
        "test_framework": framework,
        "verbose": verbose,
    }
    
    cli.print_info(f"Generando tests unitarios para: {target_path}")
    
    try:
        generator = TestGenerator(config)
        
        with cli.status("Analizando código y generando tests..."):
            if os.path.isdir(target_path):
                results = generator.generate_tests_for_directory(target_path)
            else:
                results = generator.generate_tests_for_file(target_path)
        
        # Mostrar resultados
        if results.get("success"):
            cli.print_success(f"Tests generados exitosamente en: {os.path.abspath(output_dir)}")
            
            # Mostrar detalles de archivos generados
            tests_table = cli.create_table("Tests Generados", ["Archivo Original", "Archivo de Test", "Cobertura Est."])
            for item in results.get("generated_tests", []):
                tests_table.add_row(
                    os.path.basename(item.get("source_file", "")),
                    os.path.basename(item.get("test_file", "")),
                    f"{item.get('estimated_coverage', 0)}%"
                )
            console.print(tests_table)
            
            # Mostrar recomendaciones
            if results.get("recommendations"):
                cli.print_panel(
                    "Recomendaciones", 
                    "\n".join([f"• {r}" for r in results.get("recommendations", [])])
                )
        else:
            cli.print_error(f"Error al generar tests: {results.get('error', 'Error desconocido')}")
            
    except Exception as e:
        cli.print_error(f"Error durante la generación de tests: {e}")
        logger.error(f"Error en premium_generate_tests: {e}", exc_info=True)


@premium_app.command("verify-completeness")
def premium_verify_completeness(
    target: str = typer.Argument(".", help="Archivo, directorio o funcionalidad para verificar"),
    checklist_type: str = typer.Option("auto", "--type", "-t", 
                                      help="Tipo de verificación (component, feature, project, auto)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", 
                                        help="Archivo donde guardar el reporte en formato JSON")
):
    """Verifica la completitud de una implementación según criterios predefinidos (característica premium)."""
    from src.analyzers.completeness_verifier import CompletenessVerifier
    from src.utils.subscription_manager import get_subscription_manager
    import os
    
    cli.print_header("Verificación de Completitud")
    
    # Verificar suscripción
    subscription = get_subscription_manager()
    if not subscription.can_use_feature("completeness_verification"):
        cli.check_premium_feature("completeness_verification")
        return
    
    # Si es una ruta, verificar que existe
    if os.path.exists(target):
        target_path = os.path.abspath(target)
        target_type = "directory" if os.path.isdir(target_path) else "file"
        cli.print_info(f"Verificando completitud de {target_type}: {target_path}")
    else:
        # Podría ser el nombre de una funcionalidad
        target_path = "."
        cli.print_info(f"Verificando completitud de funcionalidad: {target}")
    
    try:
        # Crear el verificador con acceso premium
        config = {"premium": True}
        verifier = CompletenessVerifier(config)
        
        with cli.status("Analizando completitud..."):
            if target_type == "file":
                results = verifier.verify_file(target_path, checklist_type)
            elif target_type == "directory":
                results = verifier.verify_directory(target_path, checklist_type)
            else:
                # Funcionalidad
                results = verifier.verify_functionality(target, checklist_type)
        
        # Mostrar resultados
        completeness = results.get("completeness_score", 0)
        quality_score = results.get("quality_score", 0)
        
        # Determinar color según completitud
        color = "green" if completeness >= 80 else "yellow" if completeness >= 50 else "red"
        
        # Mostrar puntuación general
        console.print(f"Puntuación de completitud: [{color}]{completeness}%[/{color}]")
        console.print(f"Puntuación de calidad: [blue]{quality_score}%[/blue]")
        
        # Mostrar desglose de criterios
        criteria_table = cli.create_table("Criterios Evaluados", ["Criterio", "Estado", "Peso"])
        for criteria in results.get("criteria", []):
            status_icon = "✅" if criteria.get("satisfied") else "❌"
            criteria_table.add_row(
                criteria.get("name", ""),
                f"{status_icon} {criteria.get('status', '')}",
                f"{criteria.get('weight', 1)}"
            )
        console.print(criteria_table)
        
        # Mostrar componentes faltantes
        if results.get("missing_components"):
            cli.print_panel(
                "Componentes Faltantes", 
                "\n".join([f"• {c}" for c in results.get("missing_components", [])])
            )
        
        # Guardar reporte si se solicitó
        if output:
            try:
                with open(output, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2)
                cli.print_success(f"Reporte guardado en: {output}")
            except Exception as e:
                cli.print_error(f"Error al guardar reporte: {e}")
                
    except Exception as e:
        cli.print_error(f"Error durante la verificación: {e}")
        logger.error(f"Error en premium_verify_completeness: {e}", exc_info=True)


@premium_app.command("implementation")
def premium_implementation_assistant(
    functionality: str = typer.Argument(..., help="Nombre de la funcionalidad a implementar"),
    language: Optional[str] = typer.Option(None, "--language", "-l", help="Lenguaje de programación principal"),
    path: str = typer.Option(".", "--path", "-p", help="Ruta al proyecto"),
    output: Optional[str] = typer.Option(None, "--output", "-o", 
                                       help="Archivo donde guardar la guía de implementación")
):
    """Genera una guía detallada de implementación para una funcionalidad (característica premium)."""
    from src.generators.implementation_prompt_generator import get_implementation_prompt_generator
    from src.utils.subscription_manager import get_subscription_manager
    
    cli.print_header("Asistente de Implementación Premium")
    
    # Verificar suscripción
    subscription = get_subscription_manager()
    if not subscription.can_use_feature("implementation_prompts"):
        cli.check_premium_feature("implementation_prompts")
        return
    
    cli.print_info(f"Generando guía de implementación para: {functionality}")
    
    try:
        # Crear generador con configuración premium
        generator = get_implementation_prompt_generator(premium=True)
        
        with cli.status(f"Analizando proyecto y generando guía para {functionality}..."):
            # Generar guía de implementación detallada
            result = generator.generate_implementation_guide(
                functionality=functionality,
                project_path=path,
                language=language
            )
        
        # Mostrar resultados
        if result.get("success"):
            guide_content = result.get("content", "")
            
            # Mostrar resumen
            cli.print_success("Guía de implementación generada correctamente")
            
            # Mostrar vista previa
            cli.print_panel(
                "Vista previa de la guía", 
                guide_content[:300] + "..." if len(guide_content) > 300 else guide_content
            )
            
            # Guardar a archivo si se especificó
            if output:
                try:
                    output_path = output
                    if not output.lower().endswith('.md'):
                        output_path = f"{output}.md"
                        
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(guide_content)
                    cli.print_success(f"Guía guardada en: {output_path}")
                except Exception as e:
                    cli.print_error(f"Error al guardar guía: {e}")
            else:
                # Mostrar guía completa en consola
                console.print("\n")
                console.print(guide_content)
                console.print("\n")
        else:
            cli.print_error(f"Error al generar guía: {result.get('error', 'Error desconocido')}")
    except Exception as e:
        cli.print_error(f"Error en el asistente de implementación: {e}")
        logger.error(f"Error en premium_implementation_assistant: {e}", exc_info=True)


#
# Comandos para telemetría anónima
#

@telemetry_app.command("status")
def telemetry_status():
    """
    Muestra el estado actual de la telemetría anónima.
    """
    try:
        # Registrar el comando para telemetría (sólo si está activada)
        record_command("telemetry_status")
        
        manager = get_telemetry_manager()
        consent_manager = ConsentManager(console=console)
        
        # Mostrar estado
        cli.print_header("Estado de Telemetría")
        status = "Activada" if manager.is_enabled() else "Desactivada"
        status_color = "green" if manager.is_enabled() else "red"
        console.print(f"Telemetría anónima: [{status_color}]{status}[/{status_color}]")
        
        # Mostrar información detallada
        consent_manager.show_collected_data()
        
    except Exception as e:
        logger.error(f"Error al mostrar estado de telemetría: {e}")
        cli.print_error("No se pudo mostrar el estado de telemetría")


@telemetry_app.command("enable")
def telemetry_enable():
    """
    Activa la recolección anónima de telemetría.
    """
    try:
        consent_manager = ConsentManager(console=console)
        
        if consent_manager.enable_telemetry():
            cli.print_success("Telemetría anónima activada")
            console.print("\nGracias por ayudarnos a mejorar ProjectPrompt. Todos los datos recolectados son")
            console.print("completamente anónimos y se utilizan únicamente para mejorar la herramienta.")
            console.print("\nPuedes revisar los datos recolectados con: project-prompt telemetry status")
            console.print("Puedes desactivar la telemetría en cualquier momento con: project-prompt telemetry disable")
            
            # Registrar ahora que está activada
            record_command("telemetry_enable")
        else:
            cli.print_error("No se pudo activar la telemetría")
    except Exception as e:
        logger.error(f"Error al activar telemetría: {e}")
        cli.print_error("No se pudo activar la telemetría")


@telemetry_app.command("disable")
def telemetry_disable():
    """
    Desactiva la recolección anónima de telemetría.
    """
    try:
        # Registrar comando antes de desactivar
        record_command("telemetry_disable")
        
        consent_manager = ConsentManager(console=console)
        
        if consent_manager.disable_telemetry():
            cli.print_success("Telemetría anónima desactivada")
            console.print("\nLos datos pendientes de envío han sido eliminados. No se recopilarán más datos.")
            console.print("Puedes volver a activar la telemetría en cualquier momento con: project-prompt telemetry enable")
        else:
            cli.print_error("No se pudo desactivar la telemetría")
    except Exception as e:
        logger.error(f"Error al desactivar telemetría: {e}")
        cli.print_error("No se pudo desactivar la telemetría")


@telemetry_app.command("prompt")
def telemetry_prompt():
    """
    Muestra el prompt de consentimiento para telemetría.
    """
    try:
        consent_manager = ConsentManager(console=console)
        status = consent_manager.request_consent(force=True)
        
        # No necesitamos hacer nada más, el consent_manager ya maneja todo
        if status == "granted":
            record_command("telemetry_prompt")
    except Exception as e:
        logger.error(f"Error en prompt de telemetría: {e}")
        cli.print_error("No se pudo mostrar el prompt de telemetría")


# Submenu para comandos de actualización y sincronización
update_app = typer.Typer(help="Comandos para gestionar actualizaciones y sincronización")
app.add_typer(update_app, name="update")


@update_app.command("check")
def check_updates(
    force: bool = typer.Option(False, "--force", "-f", help="Forzar verificación incluso si se realizó recientemente")
):
    """Verificar si hay actualizaciones disponibles para ProjectPrompt."""
    cli.print_header("Verificación de Actualizaciones")
    
    updater = Updater(force=force)
    update_info = updater.check_for_updates()
    
    if update_info.get('available'):
        version = update_info.get('latest')
        current = update_info.get('version')
        cli.print_info(f"¡Actualización disponible! Versión actual: v{current}, Nueva versión: v{version}")
        
        if update_info.get('changes'):
            cli.print_info("\nMejoras destacadas:")
            for change in update_info.get('changes'):
                console.print(f"• [green]{change}[/]")
        
        console.print("\nPara actualizar, ejecute: [bold]project-prompt update system[/]")
    else:
        if update_info.get('error'):
            cli.print_warning(f"Error al verificar actualizaciones: {update_info.get('error')}")
        else:
            cli.print_success(f"Ya tiene la última versión: v{update_info.get('version')}")


@update_app.command("system")
def update_system(
    force: bool = typer.Option(False, "--force", "-f", help="Forzar actualización sin confirmación")
):
    """Actualizar ProjectPrompt a la última versión disponible."""
    cli.print_header("Actualización del Sistema")
    
    # Verificar si hay actualizaciones
    updater = Updater()
    update_info = updater.check_for_updates()
    
    if not update_info.get('available'):
        if update_info.get('error'):
            cli.print_warning(f"Error al verificar actualizaciones: {update_info.get('error')}")
            return
        else:
            cli.print_success(f"Ya tiene la última versión: v{update_info.get('version')}")
            return
    
    # Confirmar la actualización con el usuario si no es forzada
    if not force:
        current = update_info.get('version')
        new_version = update_info.get('latest')
        cli.print_info(f"Se actualizará de v{current} a v{new_version}")
        
        if update_info.get('changes'):
            cli.print_info("\nMejoras destacadas:")
            for change in update_info.get('changes'):
                console.print(f"• [green]{change}[/]")
        
        confirm = typer.confirm("¿Desea continuar con la actualización?")
        if not confirm:
            cli.print_info("Actualización cancelada.")
            return
    
    # Realizar la actualización
    with cli.status_spinner("Actualizando ProjectPrompt..."):
        success, message = updater.update_system()
    
    if success:
        cli.print_success(message)
        cli.print_info("Por favor, reinicie la aplicación para aplicar los cambios.")
    else:
        cli.print_error(f"Error durante la actualización: {message}")


@update_app.command("templates")
def update_templates():
    """Actualizar plantillas a la última versión disponible."""
    cli.print_header("Actualización de Plantillas")
    
    updater = Updater()
    with cli.status_spinner("Actualizando plantillas..."):
        success, stats = updater.update_templates()
    
    if success:
        cli.print_success("Plantillas actualizadas correctamente")
        table = cli.create_table("Estadísticas", ["Operación", "Cantidad"])
        table.add_row("Actualizadas", str(stats.get('updated', 0)))
        table.add_row("Añadidas", str(stats.get('added', 0)))
        table.add_row("Ignoradas", str(stats.get('skipped', 0)))
        table.add_row("Fallidas", str(stats.get('failed', 0)))
        console.print(table)
    else:
        cli.print_error("Error al actualizar las plantillas")


@update_app.command("skip")
def skip_version(
    version: str = typer.Argument(..., help="Versión a ignorar (ej: 1.2.3)")
):
    """Ignorar una versión específica para futuras actualizaciones."""
    cli.print_header("Ignorar Versión")
    
    updater = Updater()
    updater.skip_version(version)
    
    cli.print_info(f"La versión {version} no se notificará en futuras verificaciones.")


@update_app.command("sync")
def sync_data(
    direction: str = typer.Option("both", "--direction", "-d", 
                                 help="Dirección de sincronización: 'upload', 'download', o 'both'")
):
    """Sincronizar datos con la ubicación configurada."""
    cli.print_header("Sincronización de Datos")
    
    sync_manager = SyncManager()
    
    if not sync_manager.sync_enabled:
        cli.print_warning("La sincronización no está habilitada. Configure sync_enabled=True en config.yaml")
        return
    
    with cli.status_spinner("Sincronizando datos..."):
        if direction in ["both", "upload"]:
            success, stats = sync_manager.upload_data()
            if success:
                cli.print_success("Datos subidos correctamente")
                cli.print_info(f"Archivos sincronizados: {stats.get('uploaded', 0)}")
            else:
                cli.print_error("Error al subir datos")
        
        if direction in ["both", "download"]:
            success, stats = sync_manager.download_data()
            if success:
                cli.print_success("Datos descargados correctamente")
                cli.print_info(f"Archivos actualizados: {stats.get('downloaded', 0)}")
            else:
                cli.print_error("Error al descargar datos")


@update_app.command("backup")
def create_backup(
    output: str = typer.Option(None, "--output", "-o", help="Ruta donde guardar el archivo de respaldo")
):
    """Crear un respaldo de la configuración y datos de ProjectPrompt."""
    cli.print_header("Creación de Respaldo")
    
    sync_manager = SyncManager()
    
    # Si no se especifica ruta, usar la predeterminada
    if not output:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = os.path.expanduser(f"~/projectprompt_backup_{timestamp}.zip")
    
    with cli.status_spinner(f"Creando respaldo en {output}..."):
        success, message = sync_manager.create_backup(output)
    
    if success:
        cli.print_success(f"Respaldo creado correctamente en: {output}")
    else:
        cli.print_error(f"Error al crear respaldo: {message}")


@update_app.command("restore")
def restore_backup(
    backup_file: str = typer.Argument(..., help="Ruta al archivo de respaldo"),
    force: bool = typer.Option(False, "--force", "-f", help="Sobrescribir datos existentes sin confirmación")
):
    """Restaurar un respaldo de ProjectPrompt."""
    cli.print_header("Restauración de Respaldo")
    
    # Confirmar restauración si no es forzada
    if not force:
        confirm = typer.confirm("Esta operación sobrescribirá los datos actuales. ¿Desea continuar?")
        if not confirm:
            cli.print_info("Restauración cancelada.")
            return
    
    sync_manager = SyncManager()
    
    with cli.status_spinner("Restaurando datos desde respaldo..."):
        success, message = sync_manager.restore_backup(backup_file)
    
    if success:
        cli.print_success("Datos restaurados correctamente")
    else:
        cli.print_error(f"Error al restaurar: {message}")


@update_app.command("configure")
def configure_sync(
    provider: str = typer.Option(None, "--provider", "-p", 
                               help="Proveedor de sincronización: 'local', 'gdrive', 'dropbox', etc."),
    directory: str = typer.Option(None, "--directory", "-d", 
                                help="Directorio para sincronización local"),
    enable: bool = typer.Option(None, "--enable/--disable", 
                              help="Activar o desactivar la sincronización")
):
    """Configurar opciones de sincronización."""
    cli.print_header("Configuración de Sincronización")
    
    config = config_manager.get_config()
    modified = False
    
    if enable is not None:
        config['sync_enabled'] = enable
        cli.print_info(f"Sincronización {'activada' if enable else 'desactivada'}")
        modified = True
    
    if provider:
        config['sync_provider'] = provider
        cli.print_info(f"Proveedor de sincronización establecido a: {provider}")
        modified = True
    
    if directory:
        config['sync_directory'] = os.path.abspath(directory)
        cli.print_info(f"Directorio de sincronización establecido a: {directory}")
        modified = True
    
    if modified:
        config_manager.save_config(config)
        cli.print_success("Configuración guardada correctamente")
    else:
        # Mostrar configuración actual
        table = cli.create_table("Configuración Actual", ["Opción", "Valor"])
        table.add_row("Sincronización", "Activada ✅" if config.get('sync_enabled', False) else "Desactivada ❌")
        table.add_row("Proveedor", config.get('sync_provider', 'local'))
        table.add_row("Directorio", config.get('sync_directory', 'No configurado'))
        console.print(table)


@update_app.command("status")
def sync_status():
    """Mostrar estado de sincronización."""
    cli.print_header("Estado de Sincronización")
    
    sync_manager = SyncManager()
    
    if not sync_manager.sync_enabled:
        cli.print_warning("La sincronización no está habilitada. Use 'project-prompt update configure --enable' para activarla.")
        return
    
    # Obtener información de estado
    status = sync_manager.get_status()
    
    # Mostrar información
    table = cli.create_table("Estado de Sincronización", ["Propiedad", "Valor"])
    table.add_row("Proveedor", status.get('provider', 'No configurado'))
    table.add_row("Última sincronización", status.get('last_sync', 'Nunca'))
    table.add_row("Instalaciones registradas", str(status.get('installations', 0)))
    console.print(table)
    
    # Si hay instalaciones, mostrarlas
    installations = status.get('installation_list', [])
    if installations:
        install_table = cli.create_table("Instalaciones Registradas", ["Nombre", "Plataforma", "Última Sincronización"])
        for inst in installations:
            install_table.add_row(
                inst.get('name', 'Desconocido'),
                inst.get('platform', 'Desconocido'),
                inst.get('last_sync', 'Nunca')
            )
        console.print(install_table)


# Configurar callbacks para inicialización y cierre de telemetría

@app.callback()
def app_callback():
    """
    Callback que se ejecuta al iniciar la aplicación.
    Configura el entorno y la telemetría.
    """
    try:
        # Inicializar telemetría
        initialize_telemetry()
        
        # Verificar si es la primera ejecución para solicitar consentimiento
        check_first_run_telemetry_consent()
        
    except Exception as e:
        # No queremos que un error en la telemetría impida el uso de la aplicación
        error_message = str(e)
        logger.error(f"Error al inicializar telemetría: {error_message}")
        
        # Proporcionar información adicional sobre los errores comunes
        if "get_config" in error_message:
            logger.info("💡 Este error es inofensivo y no afecta a la funcionalidad principal del programa.")
            logger.info("   La telemetría es opcional y el programa funcionará normalmente sin ella.")
        elif "connection" in error_message.lower() or "connect" in error_message.lower():
            logger.info("💡 Error de conexión en telemetría - funcionamiento sin conexión habilitado.")
    
    # El callback de Typer no debe retornar nada para continuar con la ejecución normal
    return
    
def check_first_run_telemetry_consent():
    """
    Verifica si es la primera ejecución para solicitar consentimiento de telemetría.
    """
    # Acceder directamente a la configuración
    prompted = config_manager.get("telemetry", {}).get("prompted", False)
    
    # Verificar si ya se ha mostrado el prompt de telemetría
    if prompted:
        return
        
    # Marcar que ya se ha solicitado consentimiento
    config_manager.set("telemetry.prompted", True)
    config_manager.save_config()
    
    # Mostrar prompt de consentimiento
    try:
        consent_manager = ConsentManager(console=console)
        consent_manager.request_consent()
    except Exception as e:
        logger.error(f"Error al solicitar consentimiento de telemetría: {e}")


# Registrar cierre de telemetría al finalizar el programa
import atexit
atexit.register(shutdown_telemetry)


@app.command()
def init_project_folder(
    project_name: Optional[str] = typer.Argument(None, help="Nombre del proyecto (opcional)")
):
    """Inicializa una carpeta project-prompt organizada en el directorio actual.
    
    Crea una estructura de carpetas organizadas para gestionar los archivos generados por ProjectPrompt.
    """
    try:
        # Crear la carpeta principal project-prompt
        project_prompt_dir = os.path.join(os.getcwd(), "project-prompt")
        
        if os.path.exists(project_prompt_dir):
            cli.print_warning("La carpeta 'project-prompt' ya existe en este directorio.")
            overwrite = typer.confirm("¿Deseas sobrescribir la estructura existente?")
            if not overwrite:
                cli.print_info("Operación cancelada.")
                return
        
        # Crear estructura de carpetas
        folders_to_create = [
            "analyses",
            "suggestions", 
            "documentation",
            "prompts",
            "exports",
            "backups"
        ]
        
        os.makedirs(project_prompt_dir, exist_ok=True)
        
        for folder in folders_to_create:
            folder_path = os.path.join(project_prompt_dir, folder)
            os.makedirs(folder_path, exist_ok=True)
            
            # Crear archivo README en cada carpeta
            readme_path = os.path.join(folder_path, "README.md")
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(get_directory_description(folder))
        
        # Crear archivo de configuración del proyecto
        config_file = os.path.join(project_prompt_dir, "project-config.json")
        project_config = {
            "project_name": project_name or os.path.basename(os.getcwd()),
            "created_at": datetime.now().isoformat(),
            "version": __version__,
            "structure": {
                "analyses": "Análisis automáticos del proyecto",
                "suggestions": "Sugerencias de mejora generadas por IA",
                "documentation": "Documentación generada automáticamente",
                "prompts": "Prompts personalizados para el proyecto",
                "exports": "Exportaciones en diferentes formatos",
                "backups": "Copias de seguridad de archivos importantes"
            }
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(project_config, f, indent=2, ensure_ascii=False)
        
        # Crear archivo principal README
        main_readme = os.path.join(project_prompt_dir, "README.md")
        with open(main_readme, 'w', encoding='utf-8') as f:
            f.write(f"""# {project_config['project_name']} - ProjectPrompt

Este directorio contiene todos los archivos generados por ProjectPrompt para el proyecto **{project_config['project_name']}**.

## Estructura del directorio

- **analyses/**: Análisis automáticos del código y estructura del proyecto
- **suggestions/**: Sugerencias de mejora generadas por inteligencia artificial
- **documentation/**: Documentación generada automáticamente
- **prompts/**: Prompts personalizados para este proyecto específico
- **exports/**: Exportaciones en diferentes formatos (PDF, HTML, etc.)
- **backups/**: Copias de seguridad de archivos importantes

## Configuración

La configuración del proyecto se encuentra en `project-config.json`.

## Comandos útiles

```bash
# Analizar el proyecto
project-prompt analyze

# Generar sugerencias
project-prompt suggest

# Ver documentación
project-prompt docs

# Limpiar archivos generados
project-prompt delete all
```

---
*Generado por ProjectPrompt v{__version__} el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
""")

        cli.print_success(f"Carpeta 'project-prompt' inicializada correctamente en {project_prompt_dir}")
        cli.print_info(f"Proyecto: {project_config['project_name']}")
        cli.print_info(f"Estructura creada con {len(folders_to_create)} directorios organizados")
        
    except Exception as e:
        cli.print_error(f"Error al inicializar la carpeta del proyecto: {e}")


def get_directory_description(directory_name: str) -> str:
    """Obtiene la descripción para un directorio específico."""
    descriptions = {
        "analyses": """# Análisis del Proyecto

Este directorio contiene análisis automáticos del proyecto generados por ProjectPrompt.

## Tipos de análisis incluidos:
- Análisis de estructura del código
- Análisis de dependencias
- Análisis de calidad del código
- Análisis de patrones de diseño
- Análisis de arquitectura

Los archivos se nombran con timestamp para mantener un historial de análisis.
""",
        "suggestions": """# Sugerencias de Mejora

Este directorio contiene sugerencias de mejora generadas por inteligencia artificial.

## Tipos de sugerencias incluidas:
- Mejoras de rendimiento
- Refactorización de código
- Optimizaciones de arquitectura
- Mejores prácticas
- Corrección de problemas potenciales

Las sugerencias se organizan por categoría y prioridad.
""",
        "documentation": """# Documentación Generada

Este directorio contiene documentación generada automáticamente por ProjectPrompt.

## Tipos de documentación incluida:
- API Documentation
- README automáticos
- Guías de instalación
- Documentación de arquitectura
- Diagramas de flujo

La documentación se mantiene actualizada con cada análisis.
""",
        "prompts": """# Prompts Personalizados

Este directorio contiene prompts personalizados para este proyecto específico.

## Uso de prompts:
- Prompts para análisis específicos
- Plantillas de sugerencias
- Configuraciones de IA personalizadas
- Contexto específico del proyecto

Los prompts permiten adaptar ProjectPrompt a las necesidades específicas del proyecto.
""",
        "exports": """# Exportaciones

Este directorio contiene exportaciones de análisis y documentación en diferentes formatos.

## Formatos disponibles:
- PDF para informes
- HTML para visualización web
- Markdown para documentación
- JSON para integración con otras herramientas
- CSV para análisis de datos

Las exportaciones facilitan el compartir resultados con el equipo.
""",
        "backups": """# Copias de Seguridad

Este directorio contiene copias de seguridad de archivos importantes del proyecto.

## Contenido de backups:
- Configuraciones importantes
- Análisis históricos
- Versiones anteriores de archivos críticos
- Snapshots del estado del proyecto

Las copias de seguridad se crean automáticamente antes de cambios importantes.
"""
    }
    
    return descriptions.get(directory_name, f"# {directory_name.title()}\n\nDirectorio para {directory_name} del proyecto.\n")


@app.command()
def delete(
    scope: str = typer.Argument(..., 
                              help="Tipo de datos a eliminar: 'all', 'analyses', 'suggestions', 'project-prompt-folder'"),
    force: bool = typer.Option(False, "--force", "-f", 
                              help="Forzar eliminación sin confirmación")
):
    """Elimina archivos generados por ProjectPrompt.
    
    Puede eliminar análisis, sugerencias, todos los archivos generados, o la carpeta project-prompt completa.
    """
    import shutil
    
    if scope not in ["all", "analyses", "suggestions", "project-prompt-folder"]:
        cli.print_error(f"Ámbito no válido: {scope}. Use 'all', 'analyses', 'suggestions' o 'project-prompt-folder'.")
        return
    
    # Determinar qué eliminar
    if scope == "project-prompt-folder":
        # Eliminar toda la carpeta project-prompt en el directorio actual
        project_prompt_dir = os.path.join(os.getcwd(), "project-prompt")
        if not os.path.exists(project_prompt_dir):
            cli.print_warning("No se encontró la carpeta 'project-prompt' en el directorio actual.")
            return
        
        if not force:
            console.print(f"[yellow]¿Estás seguro de que deseas eliminar completamente la carpeta 'project-prompt' y todo su contenido?[/yellow]")
            confirmation = typer.confirm("Esta acción no se puede deshacer")
            if not confirmation:
                cli.print_info("Operación cancelada.")
                return
        
        try:
            shutil.rmtree(project_prompt_dir)
            cli.print_success("Carpeta 'project-prompt' eliminada completamente.")
        except Exception as e:
            cli.print_error(f"Error al eliminar la carpeta: {e}")
        return
    
    # Determinar directorios a eliminar (comportamiento original)
    dirs_to_clean = []
    if scope == "all" or scope == "analyses":
        dirs_to_clean.append(ANALYSES_DIR)
    if scope == "all" or scope == "suggestions":
        dirs_to_clean.append(SUGGESTIONS_DIR)
    
    if not force:
        # Pedir confirmación
        dirs_str = ", ".join([os.path.basename(d) for d in dirs_to_clean])
        console.print(f"[yellow]¿Estás seguro de que deseas eliminar los archivos en {dirs_str}?[/yellow]")
        confirmation = typer.confirm("Confirmar eliminación")
        if not confirmation:
            cli.print_info("Operación cancelada.")
            return
    
    # Proceder con la eliminación
    for directory in dirs_to_clean:
        if os.path.exists(directory):
            try:
                # Eliminar todos los archivos del directorio pero mantener el directorio
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                cli.print_success(f"Archivos en {os.path.basename(directory)} eliminados correctamente.")
            except Exception as e:
                cli.print_error(f"Error al eliminar archivos en {directory}: {e}")
    
    cli.print_success("Limpieza completada exitosamente.")


# Punto de entrada principal para ejecución directa
if __name__ == "__main__":
    app()
