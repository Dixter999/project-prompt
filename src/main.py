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
import time
import functools
import inspect
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pathlib import Path

# Ensure local imports take precedence over system-installed packages
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import typer
from typer.core import TyperGroup
import click
from rich.console import Console

from src import __version__
from src.utils import logger, LogLevel, set_level
from src.utils.config import config_manager
from src.utils.api_validator import get_api_validator
from src.utils.updater import Updater, check_and_notify_updates
from src.utils.sync_manager import SyncManager, get_sync_manager
from src.utils.telemetry import initialize_telemetry, shutdown_telemetry, get_telemetry_manager, record_command, record_error
from src.ui import menu
from src.ui.cli import cli
from src.ui.consent_manager import ConsentManager
from src.ui.analysis_view import analysis_view
from src.ui.documentation_navigator import get_documentation_navigator
from src.ui.dashboard import DashboardCLI
# Importamos los analizadores bajo demanda para evitar carga innecesaria

# Custom help handler for better UX
class CustomTyperGroup(TyperGroup):
    """Custom Typer group that shows help when command is incomplete"""
    
    def invoke(self, ctx):
        # If no subcommand was provided, show custom help
        if ctx.invoked_subcommand is None:
            # Check if this is a specific app that needs custom help
            if hasattr(ctx, 'info') and hasattr(ctx.info, 'name'):
                command_name = ctx.info.name
                
                if command_name == 'ai':
                    # Show AI-specific help
                    show_ai_command_help()
                    ctx.exit()
                elif command_name == 'rules':
                    # Show rules-specific help
                    show_rules_command_help()
                    ctx.exit()
                elif command_name == 'premium':
                    # Show premium-specific help
                    show_premium_command_help()
                    ctx.exit()
            
            # Default behavior: show standard help
            click.echo(ctx.get_help())
            ctx.exit()
        return super().invoke(ctx)
    
    def parse_args(self, ctx, args):
        # Override to handle no-args case specifically
        if not args:
            # Check if this is a specific app that needs custom help
            if hasattr(ctx, 'info') and hasattr(ctx.info, 'name'):
                command_name = ctx.info.name
                
                if command_name == 'ai':
                    show_ai_command_help()
                    ctx.exit()
                elif command_name == 'rules':
                    show_rules_command_help()
                    ctx.exit()
                elif command_name == 'premium':
                    show_premium_command_help()
                    ctx.exit()
        
        return super().parse_args(ctx, args)

# Define project directories
PROJECT_ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = PROJECT_ROOT / "project-output"
ANALYSES_DIR = OUTPUT_DIR / "analyses"
SUGGESTIONS_DIR = OUTPUT_DIR / "suggestions"

# Create output directories if they don't exist
os.makedirs(ANALYSES_DIR, exist_ok=True)
os.makedirs(SUGGESTIONS_DIR, exist_ok=True)

console = Console()
app = typer.Typer(
    help="ProjectPrompt: Asistente inteligente para proyectos",
    cls=CustomTyperGroup,
    no_args_is_help=True
)

# Submenu para comandos de documentación
docs_app = typer.Typer(
    help="Comandos de navegación de documentación",
    cls=CustomTyperGroup,
    no_args_is_help=True
)
app.add_typer(docs_app, name="docs")

# Submenu para comandos de IA avanzada
ai_app = typer.Typer(
    help="Comandos de IA (Copilot/Anthropic) - Ahora disponibles para todos",
    cls=CustomTyperGroup,
    no_args_is_help=True
)

app.add_typer(ai_app, name="ai")

# Submenu para comandos de actualización y sincronización
update_app = typer.Typer(
    help="Comandos para gestionar actualizaciones y sincronización",
    cls=CustomTyperGroup,
    no_args_is_help=True
)
app.add_typer(update_app, name="update")

# Submenu para comandos premium 
premium_app = typer.Typer(
    help="Comandos avanzados (ahora disponibles para todos los usuarios)",
    cls=CustomTyperGroup,
    no_args_is_help=True
)

app.add_typer(premium_app, name="premium")

# Submenu para comandos de telemetría
telemetry_app = typer.Typer(
    help="Comandos para gestionar la telemetría anónima",
    cls=CustomTyperGroup,
    no_args_is_help=True
)
app.add_typer(telemetry_app, name="telemetry")

# Submenu para comandos de reglas
from src.commands.rules_commands import rules_app
app.add_typer(rules_app, name="rules")

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
    rules_file: Optional[str] = typer.Option(None, "--rules", "-r", help="Archivo de reglas para aplicar durante el análisis"),
    check_compliance: bool = typer.Option(False, "--compliance/--no-compliance", "-c/-nc", 
                                        help="Verificar cumplimiento de reglas durante el análisis"),
):
    """Analizar la estructura y funcionalidades de un proyecto existente."""
    from src.analyzers.project_scanner import get_project_scanner
    from src.analyzers.functionality_detector import get_functionality_detector
    from src.utils.enhanced_rules_manager import EnhancedRulesManager
    import json
    import os
    from datetime import datetime
    project_path = os.path.abspath(path)
    
    if not os.path.isdir(project_path):
        cli.print_error(f"La ruta especificada no es un directorio válido: {project_path}")
        return
    
    # Initialize rules manager if rules file provided or compliance checking enabled
    rules_manager = None
    if rules_file or check_compliance:
        try:
            rules_manager = EnhancedRulesManager(project_root=project_path)
            
            # Look for rules file in project if not explicitly provided
            if not rules_file:
                default_rules_path = os.path.join(project_path, "project-prompt-rules.md")
                if os.path.exists(default_rules_path):
                    rules_file = default_rules_path
                    cli.print_info(f"Usando archivo de reglas encontrado: {rules_file}")
                elif check_compliance:
                    cli.print_warning("Verificación de cumplimiento solicitada pero no se encontró archivo de reglas")
                    cli.print_info("Usa 'project-prompt rules-init' para crear un archivo de reglas desde una plantilla")
            
            # Load rules if we have a file
            if rules_file or check_compliance:
                success = rules_manager.load_rules()
                if success:
                    all_rules = rules_manager.get_all_rules()
                    cli.print_success(f"✅ Reglas cargadas: {len(all_rules)} reglas encontradas")
                else:
                    cli.print_warning("No se pudo cargar el archivo de reglas")
                    if check_compliance:
                        cli.print_info("Continuando análisis sin verificación de cumplimiento")
                        check_compliance = False
                        rules_manager = None
        except Exception as e:
            cli.print_error(f"Error al inicializar el sistema de reglas: {e}")
            if check_compliance:
                cli.print_warning("Continuando análisis sin verificación de cumplimiento")
                check_compliance = False
            rules_manager = None
        
    cli.print_header("Análisis Completo de Proyecto")
    cli.print_info(f"Analizando proyecto en: {project_path}")
    if rules_manager:
        cli.print_info(f"🔍 Aplicando reglas: {len(rules_manager.get_all_rules())} reglas cargadas")
    
    try:
        # Crear función de callback para el progreso
        progress_info = {}
        
        def update_progress(info):
            progress_info.update(info)
        
        # Crear escáner de proyectos con callback de progreso
        scanner = get_project_scanner(
            max_file_size_mb=max_size, 
            max_files=max_files,
            progress_callback=update_progress
        )
        
        # Realizar análisis de estructura con indicadores de progreso
        with cli.progress_bar("Escaneando proyecto", total=100) as progress:
            # Configurar task de progreso
            task = progress.add_task("Escaneando archivos y directorios...", total=100)
            
            # Iniciar el análisis en un hilo separado para poder actualizar el progreso
            import threading
            import time
            
            project_data = None
            analysis_complete = False
            error = None
            
            def run_analysis():
                nonlocal project_data, analysis_complete, error
                try:
                    project_data = scanner.scan_project(project_path)
                    analysis_complete = True
                except Exception as e:
                    error = e
                    analysis_complete = True
            
            # Iniciar análisis en hilo separado
            analysis_thread = threading.Thread(target=run_analysis)
            analysis_thread.start()
            
            # Actualizar progreso mientras el análisis está en curso
            while not analysis_complete:
                time.sleep(0.1)
                
                if progress_info:
                    total_files = progress_info.get('total_files', 1)
                    analyzed_files = progress_info.get('analyzed_files', 0)
                    current_file = progress_info.get('current_file', '')
                    message = progress_info.get('message', 'Escaneando...')
                    
                    # Calcular progreso como porcentaje
                    if total_files > 0:
                        progress_percent = min(95, (analyzed_files / total_files) * 95)  # Máximo 95% hasta completar
                    else:
                        progress_percent = 10
                    
                    # Actualizar tarea con información actual
                    if current_file:
                        status_msg = f"{message}: {current_file}"
                    else:
                        status_msg = message
                    
                    progress.update(task, completed=progress_percent, description=status_msg)
            
            # Completar el progreso
            progress.update(task, completed=100, description="Análisis completado")
            analysis_thread.join()
            
            if error:
                raise error
        
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
        
        # Perform rules compliance checking if enabled
        compliance_data = {}
        if check_compliance and rules_manager:
            cli.print_header("Verificación de Cumplimiento de Reglas")
            
            # Check compliance for key files
            important_files = project_data.get('important_files', {})
            
            compliance_summary = {
                'total_files_checked': 0,
                'total_violations': 0,
                'total_applicable_rules': 0,
                'files_with_violations': [],
                'compliance_by_category': {},
                'compliance_by_priority': {}
            }
            
            # Files to check - prioritize important files
            files_to_check = []
            
            # Add important files first
            for category, file_list in important_files.items():
                if isinstance(file_list, list):
                    files_to_check.extend(file_list)
                elif isinstance(file_list, dict):
                    for subcategory, subfiles in file_list.items():
                        if isinstance(subfiles, list):
                            files_to_check.extend(subfiles)
            
            # Add some additional source files from the scan
            source_files = project_data.get('source_files', [])[:20]  # Limit to 20 files for demo
            files_to_check.extend(source_files)
            
            # Remove duplicates and ensure files exist
            files_to_check = list(set([f for f in files_to_check if f and os.path.exists(os.path.join(project_path, f))]))
            
            if files_to_check:
                with cli.progress_bar("Verificando cumplimiento", total=len(files_to_check)) as progress:
                    task = progress.add_task("Checking compliance...", total=len(files_to_check))
                    
                    for i, file_path in enumerate(files_to_check):
                        full_path = os.path.join(project_path, file_path)
                        progress.update(task, completed=i+1, description=f"Checking {file_path}")
                        
                        try:
                            file_compliance = rules_manager.check_rule_compliance(full_path)
                            compliance_summary['total_files_checked'] += 1
                            compliance_summary['total_applicable_rules'] += file_compliance.get('applicable_rules_count', 0)
                            
                            # Check for violations
                            violations = file_compliance.get('violations', [])
                            if violations:
                                compliance_summary['total_violations'] += len(violations)
                                compliance_summary['files_with_violations'].append({
                                    'file': file_path,
                                    'violations': violations
                                })
                        except Exception as e:
                            logger.warning(f"Error checking compliance for {file_path}: {e}")
            
            # Display compliance results
            if compliance_summary['total_files_checked'] > 0:
                compliance_score = 1.0 - (compliance_summary['total_violations'] / max(compliance_summary['total_applicable_rules'], 1))
                
                cli.print_success(f"📊 Resumen de Cumplimiento:")
                cli.print_info(f"  • Archivos verificados: {compliance_summary['total_files_checked']}")
                cli.print_info(f"  • Reglas aplicables: {compliance_summary['total_applicable_rules']}")
                cli.print_info(f"  • Violaciones encontradas: {compliance_summary['total_violations']}")
                cli.print_info(f"  • Puntuación de cumplimiento: {compliance_score:.1%}")
                
                if compliance_summary['files_with_violations']:
                    cli.print_warning(f"⚠️  Archivos con violaciones ({len(compliance_summary['files_with_violations'])}):")
                    for file_violation in compliance_summary['files_with_violations'][:5]:  # Show first 5
                        cli.print_info(f"    • {file_violation['file']}: {len(file_violation['violations'])} violaciones")
                    
                    if len(compliance_summary['files_with_violations']) > 5:
                        cli.print_info(f"    ... y {len(compliance_summary['files_with_violations']) - 5} archivos más")
                    
                    cli.print_info("    Use 'project-prompt rules-report' para ver un informe detallado")
                else:
                    cli.print_success("✅ No se encontraron violaciones de reglas!")
                
                compliance_data = compliance_summary
            else:
                cli.print_warning("No se pudieron verificar archivos para cumplimiento de reglas")
        
        # Guardar resultados si se especificó un archivo de salida
        if output:
            # Check if output path is absolute or starts with project-output
            if os.path.isabs(output) or output.startswith('project-output'):
                output_path = output
            else:
                # Relative path - place it in project-output/analyses/
                project_name = os.path.basename(project_path)
                output_path = str(ANALYSES_DIR / project_name / output)
            
            # Si no se especificó extensión, añadir .json
            if not output_path.endswith('.json'):
                output_path = f"{output_path}.json"
                
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
                
            # Añadir datos de cumplimiento si se generaron
            if compliance_data:
                combined_result['compliance'] = compliance_data
                
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


@app.command(name="analyze-group")
@telemetry_command
def analyze_group_command(
    group_name: Optional[str] = typer.Argument(None, help="Nombre del grupo funcional a analizar"),
    project_path: str = typer.Option(".", "--path", "-p", help="Ruta al proyecto a analizar")
):
    """Analizar un grupo funcional específico con IA (Anthropic Claude)."""
    from src.commands.analyze_group import AnalyzeGroupCommand
    
    try:
        command = AnalyzeGroupCommand()
        success = command.execute(
            group_name=group_name,
            project_path=project_path
        )
        if not success:
            # If the command failed and no group_name was provided, show additional help
            if not group_name:
                console.print("\n")
                show_analyze_group_help()
            else:
                cli.print_error("El análisis no se completó exitosamente")
    except Exception as e:
        cli.print_error(f"Error durante el análisis del grupo: {e}")
        logger.error(f"Error en analyze_group_command: {e}", exc_info=True)


@app.command(name="generate-suggestions")
@telemetry_command
def generate_suggestions_command(
    group_name: Optional[str] = typer.Argument(None, help="Nombre del grupo funcional para generar sugerencias"),
    project_path: str = typer.Option(".", "--path", "-p", help="Ruta al proyecto")
):
    """Generar sugerencias de mejora estructuradas para un grupo funcional."""
    from src.commands.generate_suggestions import GenerateSuggestionsCommand
    
    # Check if group_name is provided, if not show help
    if not group_name:
        show_generate_suggestions_help()
        return
    
    try:
        command = GenerateSuggestionsCommand()
        success = command.execute(
            group_name=group_name,
            project_path=project_path
        )
        if not success:
            cli.print_error("La generación de sugerencias no se completó exitosamente")
    except Exception as e:
        cli.print_error(f"Error durante la generación de sugerencias: {e}")
        logger.error(f"Error en generate_suggestions_command: {e}", exc_info=True)


@app.command(name="track-progress")
@telemetry_command
def track_progress_command(
    group_name: Optional[str] = typer.Argument(None, help="Nombre del grupo funcional (opcional, muestra resumen si no se especifica)"),
    phase: Optional[int] = typer.Option(None, "--phase", "-p", help="Número de fase específica a rastrear (opcional)")
):
    """Rastrear y gestionar el progreso de implementación de mejoras."""
    from src.commands.track_progress import TrackProgressCommand
    
    try:
        command = TrackProgressCommand()
        command.execute(group_name=group_name, phase=phase)
    except Exception as e:
        cli.print_error(f"Error durante el seguimiento de progreso: {e}")
        logger.error(f"Error en track_progress_command: {e}", exc_info=True)


@app.command()
def menu():
    """Iniciar el menú interactivo de ProjectPrompt."""
    from src.ui.menu import menu as interactive_menu
    interactive_menu.show()


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
):
    """Configurar una clave API para servicios usando archivos .env (recomendado por seguridad)."""
    cli.print_header("Configuración de API - Método Seguro con .env")
    
    # Deprecar el método directo y guiar hacia .env
    cli.print_info("🔒 Para mayor seguridad, ProjectPrompt usa archivos .env para las claves API")
    cli.print_info("📝 Este método es más seguro que almacenar claves en el sistema keyring")
    
    # Determinar las rutas del archivo .env
    current_dir = os.getcwd()
    project_env = os.path.join(current_dir, ".env")
    home_env = os.path.expanduser("~/.env")
    
    # Verificar si ya existe un .env
    env_exists = os.path.exists(project_env)
    
    cli.print_info("\n📂 Ubicaciones recomendadas para el archivo .env:")
    cli.print_info(f"  1. Proyecto actual: {project_env} {'✅' if env_exists else '❌'}")
    cli.print_info(f"  2. Directorio home: {home_env}")
    
    # Mensaje específico por API
    if api_name == "anthropic":
        env_var = "anthropic_API"
        cli.print_info(f"\n🤖 Para configurar Anthropic Claude:")
    elif api_name == "github":
        env_var = "GITHUB_API_KEY"
        cli.print_info(f"\n🐙 Para configurar GitHub API:")
    else:
        env_var = f"{api_name.upper()}_API_KEY"
        cli.print_info(f"\n🔧 Para configurar {api_name}:")
    
    cli.print_info(f"   Variable requerida: {env_var}")
    
    # Instrucciones paso a paso
    console.print("\n[bold green]📋 Instrucciones paso a paso:[/bold green]")
    console.print("\n[bold]1. Crear archivo .env[/bold]")
    console.print(f"   Ejecuta: [cyan]touch {project_env}[/cyan]")
    
    console.print("\n[bold]2. Agregar tu clave API[/bold]")
    console.print(f"   Edita el archivo y agrega: [cyan]{env_var}=tu_clave_api_aquí[/cyan]")
    
    console.print("\n[bold]3. Verificar configuración[/bold]")
    console.print(f"   Ejecuta: [cyan]project-prompt verify-api {api_name}[/cyan]")
    
    console.print("\n[bold yellow]⚠️  Importante:[/bold yellow]")
    console.print("   • Nunca compartas tu archivo .env")
    console.print("   • Agrega .env a tu .gitignore")
    console.print("   • Las claves API son sensibles y deben mantenerse privadas")
    
    # Ofrecer crear el archivo automáticamente
    if typer.confirm(f"\n¿Quieres que cree el archivo .env en {project_env}?"):
        try:
            # Crear o actualizar .env
            env_content = ""
            if env_exists:
                with open(project_env, 'r') as f:
                    env_content = f.read()
            
            # Verificar si la variable ya existe
            if env_var not in env_content:
                if env_content and not env_content.endswith('\n'):
                    env_content += '\n'
                env_content += f"# {api_name.title()} API Configuration\n"
                env_content += f"{env_var}=your_api_key_here\n"
                
                with open(project_env, 'w') as f:
                    f.write(env_content)
                
                cli.print_success(f"✅ Archivo .env creado en {project_env}")
                cli.print_info(f"📝 Edita el archivo y reemplaza 'your_api_key_here' con tu clave real")
            else:
                cli.print_info(f"ℹ️  La variable {env_var} ya existe en {project_env}")
                
        except Exception as e:
            cli.print_error(f"❌ Error al crear .env: {e}")
    
    # Verificar si ya está configurado
    console.print(f"\n[bold]🔍 Verificando configuración actual...[/bold]")
    validator = get_api_validator()
    result = validator.validate_api(api_name)
    
    if result.get("valid", False):
        cli.print_success(f"✅ {api_name} ya está configurado y funcionando")
        if "usage" in result:
            cli.print_info("📊 Información de uso:")
            for key, value in result["usage"].items():
                console.print(f"  - {key}: {value}")
    else:
        cli.print_warning(f"⚠️  {api_name} no está configurado o la clave no es válida")
        cli.print_info(f"💡 Después de editar el .env, ejecuta: project-prompt verify-api {api_name}")
    
    # Consejos de seguridad adicionales
    console.print(f"\n[bold blue]🛡️  Consejos de seguridad:[/bold blue]")
    console.print("   • Usa variables de entorno en producción")
    console.print("   • Rota tus claves API regularmente")
    console.print("   • Revisa los permisos de tu archivo .env (debe ser 600)")
    console.print("   • Considera usar herramientas como direnv para gestión automática")


@app.command()
def check_env(
    api_name: Optional[str] = typer.Argument(None, help="API específica a verificar (anthropic, github). Si no se especifica, verifica todas.")
):
    """Verificar configuración de archivos .env y variables de entorno."""
    cli.print_header("Verificación de Configuración .env")
    
    # Definir APIs y sus variables de entorno
    api_vars = {
        "anthropic": "anthropic_API",
        "github": "GITHUB_API_KEY",
        "openai": "OPENAI_API_KEY"
    }
    
    # Si se especifica una API, solo verificar esa
    if api_name:
        if api_name not in api_vars:
            cli.print_error(f"❌ API no soportada: {api_name}")
            cli.print_info(f"APIs soportadas: {', '.join(api_vars.keys())}")
            return
        apis_to_check = {api_name: api_vars[api_name]}
    else:
        apis_to_check = api_vars
    
    # Determinar ubicaciones de archivos .env
    current_dir = os.getcwd()
    env_locations = [
        os.path.join(current_dir, ".env"),
        os.path.expanduser("~/.env"),
        os.path.join(current_dir, "test-projects", ".env")
    ]
    
    console.print(f"\n[bold]📂 Buscando archivos .env en:[/bold]")
    found_envs = []
    for env_path in env_locations:
        exists = os.path.exists(env_path)
        status = "✅ (existe)" if exists else "❌ (no existe)"
        console.print(f"   {env_path} {status}")
        if exists:
            found_envs.append(env_path)
    
    if not found_envs:
        cli.print_warning("⚠️  No se encontraron archivos .env")
        cli.print_info("💡 Usa 'project-prompt set-api' para crear uno")
        return
    
    # Verificar cada API
    console.print(f"\n[bold]🔍 Verificando configuración de APIs:[/bold]")
    
    for api, env_var in apis_to_check.items():
        console.print(f"\n[bold blue]{api.title()}:[/bold blue]")
        
        # Verificar variable de entorno
        env_value = os.getenv(env_var)
        if env_value:
            masked_value = f"{env_value[:4]}...{env_value[-4:]}" if len(env_value) > 8 else "***"
            console.print(f"   🌍 Variable de entorno: ✅ {env_var}={masked_value}")
        else:
            console.print(f"   🌍 Variable de entorno: ❌ {env_var} no establecida")
        
        # Verificar archivos .env
        found_in_env = False
        for env_path in found_envs:
            try:
                with open(env_path, 'r') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if line.strip().startswith(env_var):
                            parts = line.split('=', 1)
                            if len(parts) == 2:
                                value = parts[1].strip().strip('"\'')
                                if value and value != "your_api_key_here":
                                    masked_value = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
                                    console.print(f"   📄 {env_path}: ✅ {env_var}={masked_value}")
                                    found_in_env = True
                                else:
                                    console.print(f"   📄 {env_path}: ⚠️  Variable encontrada pero sin valor válido")
                                break
            except Exception as e:
                console.print(f"   📄 {env_path}: ❌ Error al leer archivo: {e}")
        
        if not found_in_env and not env_value:
            console.print(f"   ❌ {api.title()} no está configurado")
        elif found_in_env or env_value:
            # Verificar con el validador
            try:
                validator = get_api_validator()
                result = validator.validate_api(api)
                if result.get("valid", False):
                    console.print(f"   ✅ Validación exitosa - API funcional")
                else:
                    console.print(f"   ⚠️  Configurado pero no válido: {result.get('message', 'Error desconocido')}")
            except Exception as e:
                console.print(f"   ⚠️  Error al validar: {e}")
    
    # Consejos finales
    console.print(f"\n[bold green]💡 Consejos:[/bold green]")
    console.print("   • Las variables de entorno tienen prioridad sobre archivos .env")
    console.print("   • Usa 'project-prompt verify-api' para validación completa")
    console.print("   • Verifica permisos del archivo .env: chmod 600 .env")
    console.print("   • Agrega .env a tu .gitignore para evitar commits accidentales")


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


@app.command(name="deps")
def analyze_dependencies(
    path: str = typer.Argument(".", help="Ruta del proyecto a analizar"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Archivo de salida personalizado (auto-guardado si no se especifica)"),
    format: str = typer.Option("markdown", "--format", "-f", help="Formato de salida: markdown, json, html"),
    max_files: int = typer.Option(1000, "--max-files", help="Máximo número de archivos importantes a analizar"),
    min_deps: int = typer.Option(3, "--min-deps", help="Mínimo número de dependencias para considerar archivo importante"),
    use_madge: bool = typer.Option(True, "--madge/--no-madge", help="Usar Madge para análisis eficiente"),
    show_groups: bool = typer.Option(True, "--groups/--no-groups", help="Mostrar grupos de funcionalidad"),
    show_cycles: bool = typer.Option(True, "--cycles/--no-cycles", help="Detectar dependencias circulares")
):
    """Análisis eficiente de dependencias usando Madge (comando directo optimizado).
    
    Los resultados se guardan automáticamente en project-output/analyses/dependencies/ 
    a menos que se especifique un archivo de salida personalizado con --output.
    """
    
    project_path = os.path.abspath(path)
    
    if not os.path.isdir(project_path):
        cli.print_error(f"La ruta especificada no es un directorio válido: {project_path}")
        return
        
    cli.print_header("📊 Análisis Eficiente de Dependencias")
    cli.print_info(f"🔍 Analizando proyecto en: {project_path}")
    cli.print_info(f"⚙️  Configuración: max_files={max_files}, min_deps={min_deps}, madge={use_madge}")
    
    try:
        # Importar analizador de dependencias
        from src.analyzers.dependency_graph import DependencyGraph
        
        # Crear analizador con configuración personalizada
        analyzer = DependencyGraph()
        if hasattr(analyzer, 'madge_analyzer'):
            analyzer.madge_analyzer.min_dependencies = min_deps
            analyzer.madge_analyzer.max_files_to_analyze = max_files
        
        # Realizar análisis con indicador de progreso
        with cli.status("🔄 Ejecutando análisis de dependencias..."):
            start_time = time.time()
            dependency_data = analyzer.build_dependency_graph(
                project_path, 
                max_files=max_files * 10,  # Permitir más archivos para el análisis inicial
                use_madge=use_madge
            )
            analysis_time = time.time() - start_time
        
        # Mostrar resultados del análisis
        cli.print_success(f"✅ Análisis completado en {analysis_time:.2f} segundos")
        
        # Mostrar métricas generales
        metrics = dependency_data.get('metrics', {})
        if metrics:
            cli.print_info("\n📈 Métricas del proyecto:")
            
            metrics_table = cli.create_table("Métricas", ["Métrica", "Valor"])
            metrics_table.add_row("Método de análisis", metrics.get('analysis_method', 'tradicional'))
            metrics_table.add_row("Archivos totales", str(metrics.get('total_files', 0)))
            metrics_table.add_row("Archivos importantes", str(metrics.get('files_analyzed', len(dependency_data.get('important_files', [])))))
            metrics_table.add_row("Grupos funcionales", str(len(dependency_data.get('functionality_groups', []))))
            metrics_table.add_row("Dependencias totales", str(metrics.get('total_dependencies', 0)))
            metrics_table.add_row("Promedio dependencias", str(metrics.get('average_dependencies', 0)))
            metrics_table.add_row("Complejidad", metrics.get('complexity', 'desconocida'))
            
            if metrics.get('performance_optimized'):
                metrics_table.add_row("Optimización", "✅ Filtrado inteligente aplicado")
            
            console.print(metrics_table)
        
        # Mostrar archivos importantes
        important_files = dependency_data.get('important_files', [])
        if important_files:
            cli.print_info(f"\n🎯 Top {min(10, len(important_files))} archivos más importantes:")
            
            files_table = cli.create_table("Archivos Importantes", 
                                         ["Archivo", "Deps Out", "Deps In", "Score", "Tipo"])
            
            for file_info in important_files[:10]:
                path_display = file_info['path']
                if len(path_display) > 50:
                    path_display = "..." + path_display[-47:]
                    
                files_table.add_row(
                    path_display,
                    str(file_info.get('dependencies_out', 0)),
                    str(file_info.get('dependencies_in', 0)),
                    str(file_info.get('importance_score', 0)),
                    file_info.get('file_info', {}).get('type', 'unknown')
                )
            
            console.print(files_table)
        
        # Mostrar grupos de funcionalidad
        if show_groups:
            groups = dependency_data.get('functionality_groups', [])
            if groups:
                cli.print_info(f"\n🏗️  Grupos funcionales detectados ({len(groups)}):")
                
                for i, group in enumerate(groups[:5]):  # Mostrar solo los top 5
                    group_name = group['name']
                    group_size = group['size']
                    group_importance = group['total_importance']
                    group_type = group.get('type', 'unknown')
                    
                    console.print(f"  {i+1}. {group_name}")
                    console.print(f"     📁 {group_size} archivos, Score: {group_importance}")
                    
                    if group_type == 'circular':
                        console.print(f"     🔄 [yellow]Dependencia circular detectada[/yellow]")
                    elif group_type == 'directory':
                        console.print(f"     📂 [blue]Agrupación por directorio[/blue]")
                    elif group_type == 'filetype':
                        console.print(f"     🔧 [green]Agrupación por tipo de archivo[/green]")
            else:
                cli.print_info(f"\n🏗️  No se detectaron grupos funcionales significativos")
        
        # Mostrar ciclos si se detectaron
        if show_cycles:
            cycles = dependency_data.get('file_cycles', [])
            if cycles:
                cli.print_warning(f"\n🔄 Dependencias circulares detectadas ({len(cycles)}):")
                for i, cycle in enumerate(cycles[:3]):  # Mostrar solo los primeros 3
                    cycle_display = " → ".join(cycle[:4])
                    if len(cycle) > 4:
                        cycle_display += " → ..."
                    console.print(f"  {i+1}. {cycle_display}")
        
        # Generar archivo de salida (automático o solicitado)
        if output:
            output_path = output
            
            # Determinar formato basándose en extensión o parámetro
            if not output.endswith(('.json', '.md', '.html')):
                if format == 'json':
                    output_path = f"{output}.json"
                elif format == 'html':
                    output_path = f"{output}.html"
                else:
                    output_path = f"{output}.md"
            
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        else:
            # Auto-generar nombre de archivo y guardarlo en directorio estructurado
            project_name = os.path.basename(project_path)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            
            # Crear subdirectorio para dependencias dentro de ANALYSES_DIR
            dependencies_dir = ANALYSES_DIR / "dependencies"
            os.makedirs(dependencies_dir, exist_ok=True)
            
            # Generar nombre de archivo basado en formato
            if format == 'json':
                filename = f"deps_{project_name}_{timestamp}.json"
            elif format == 'html':
                filename = f"deps_{project_name}_{timestamp}.html"
            else:
                filename = f"deps_{project_name}_{timestamp}.md"
            
            output_path = str(dependencies_dir / filename)
            
            with cli.status(f"💾 Generando archivo {format}..."):
                if output_path.endswith('.json'):
                    # Guardar en formato JSON
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(dependency_data, f, indent=2, default=str)
                        
                elif output_path.endswith('.md'):
                    # Generar Markdown
                    markdown_content = analyzer.generate_markdown_visualization(dependency_data)
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(markdown_content)
                        
                elif output_path.endswith('.html'):
                    # Generar HTML (si está disponible)
                    try:
                        from src.ui.dashboard import DashboardCLI
                        dashboard = DashboardCLI()
                        html_content = dashboard.generate_dependencies_html(dependency_data)
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                    except Exception as e:
                        cli.print_warning(f"No se pudo generar HTML: {e}")
                        # Fallback a JSON
                        output_path = output_path.replace('.html', '.json')
                        with open(output_path, 'w', encoding='utf-8') as f:
                            json.dump(dependency_data, f, indent=2, default=str)
            
            if output:
                cli.print_success(f"📄 Análisis guardado en: {output_path}")
            else:
                cli.print_success(f"📄 Análisis guardado automáticamente en: {output_path}")
                cli.print_info(f"💡 Para especificar ubicación personalizada, usa: --output <archivo>")
        
        # Sugerir siguientes pasos
        cli.print_info("\n💡 Sugerencias para análisis más profundo:")
        
        if not use_madge:
            console.print("  • Prueba con --madge para análisis más rápido")
            
        if important_files and len(important_files) == max_files:
            console.print(f"  • Aumenta --max-files para analizar más archivos importantes")
            
        if output:
            console.print("  • Usa --format html para visualización interactiva")
        else:
            console.print("  • Usa --output <archivo> para especificar ubicación personalizada")
            console.print("  • Usa --format html para visualización interactiva")
            
        console.print("  • Usa 'project-prompt premium dashboard' para análisis completo con IA")
        
        # Registro de telemetría si está habilitado
        record_command("analyze_dependencies", {
            "files_analyzed": len(important_files),
            "analysis_time": analysis_time,
            "use_madge": use_madge,
            "complexity": metrics.get('complexity', 'unknown')
        })
            
    except Exception as e:
        cli.print_error(f"❌ Error durante el análisis: {e}")
        logger.error(f"Error en analyze_dependencies: {e}", exc_info=True)
        record_error("analyze_dependencies", str(e))


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
    table.add_row("premium", "Acceder a comandos premium (ahora disponibles para todos)")
    table.add_row("diagnose", "Diagnosticar instalación y problemas")
    table.add_row("rules-init", "Inicializar archivo de reglas del proyecto")
    table.add_row("rules-validate", "Validar sintaxis del archivo de reglas")
    table.add_row("rules-apply", "Aplicar reglas y verificar cumplimiento")
    table.add_row("rules-report", "Generar reporte de cumplimiento de reglas")
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
        output_dir = os.path.join(project_path, 'project-output/documentation')
    
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


# Helper function to create user-friendly command guidance
def show_command_guidance(command_name: str, available_commands: List[str]):
    """Show helpful guidance when a command is incomplete"""
    cli.print_warning(f"Comando incompleto: '{command_name}'")
    cli.print_info("Comandos disponibles:")
    for cmd in available_commands:
        cli.print_info(f"  • {command_name} {cmd}")
    cli.print_info(f"\nUse '{command_name} --help' para ver más detalles")

# Enhanced help for generate-suggestions command
def show_generate_suggestions_help():
    """Show specific help for generate-suggestions command"""
    cli.print_header("Comando: generate-suggestions")
    cli.print_info("Este comando genera sugerencias de mejora para un grupo funcional específico.")
    cli.print_info("")
    cli.print_info("IMPORTANTE: Antes de usar este comando:")
    cli.print_info("1. Ejecute 'pp analyze-group' para ver grupos disponibles")
    cli.print_info("2. Seleccione un grupo y analícelo con IA")
    cli.print_info("3. Luego use este comando con el nombre del grupo")
    cli.print_info("")
    cli.print_info("Uso:")
    cli.print_info("  pp generate-suggestions \"Nombre del Grupo\"")
    cli.print_info("")
    cli.print_info("Ejemplo:")
    cli.print_info("  pp analyze-group                    # Ver grupos disponibles")
    cli.print_info("  pp generate-suggestions \"src/ui\"   # Generar sugerencias")

# Enhanced help for ai commands
def show_ai_command_help():
    """Show specific help for ai commands"""
    from src.ui.cli import CLI
    cli = CLI()
    cli.print_header("Comandos de IA")
    cli.print_info("Los comandos de IA utilizan modelos avanzados para análisis de código.")
    cli.print_info("")
    cli.print_info("Comandos disponibles:")
    cli.print_info("  • ai analyze [archivo] --provider [anthropic|copilot]")
    cli.print_info("  • ai refactor [archivo] --provider [anthropic|copilot]")
    cli.print_info("  • ai explain [archivo] --provider [anthropic|copilot]")
    cli.print_info("  • ai generate [descripción] --output [directorio]")
    cli.print_info("")
    cli.print_info("Ejemplos:")
    cli.print_info("  pp ai analyze src/main.py --provider anthropic")
    cli.print_info("  pp ai generate \"crear función de validación\" --output src/utils/")

# Enhanced help for analyze-group command
def show_analyze_group_help():
    """Show specific help for analyze-group command"""
    cli.print_header("Comando: analyze-group")
    cli.print_info("Este comando analiza grupos funcionales específicos con IA avanzada.")
    cli.print_info("")
    cli.print_info("Flujo de trabajo:")
    cli.print_info("1. Sin argumentos: Muestra los grupos funcionales disponibles")
    cli.print_info("2. Con nombre de grupo: Analiza ese grupo específico con IA")
    cli.print_info("3. Genera análisis detallado guardado en project-output/analyses/groups/")
    cli.print_info("")
    cli.print_info("Uso:")
    cli.print_info("  pp analyze-group                    # Listar grupos disponibles")
    cli.print_info("  pp analyze-group \"Nombre del Grupo\" # Analizar grupo específico")
    cli.print_info("")
    cli.print_info("Ejemplos:")
    cli.print_info("  pp analyze-group                    # Ver todos los grupos")
    cli.print_info("  pp analyze-group \"src/ui\"          # Analizar grupo de interfaz")
    cli.print_info("  pp analyze-group \"Authentication\"  # Analizar autenticación")
    cli.print_info("")
    cli.print_info("Nota: Requiere API key de Anthropic configurada")

# Enhanced help for rules commands
def show_rules_command_help():
    """Show specific help for rules commands"""
    cli.print_header("Comandos de Reglas")
    cli.print_info("Sistema avanzado de gestión de reglas para desarrollo con IA.")
    cli.print_info("")
    cli.print_info("Comandos principales:")
    cli.print_info("  • rules suggest --ai --threshold 0.8     # Generar sugerencias de reglas")
    cli.print_info("  • rules analyze-patterns --detailed      # Analizar patrones del proyecto")
    cli.print_info("  • rules auto-generate --output rules.yaml # Auto-generar reglas completas")
    cli.print_info("  • rules generate-structured-rules --ai   # Reglas estructuradas avanzadas")
    cli.print_info("  • rules validate rules.yaml              # Validar archivo de reglas")
    cli.print_info("  • rules apply                            # Aplicar y verificar reglas")
    cli.print_info("  • rules report                           # Generar reporte de cumplimiento")
    cli.print_info("")
    cli.print_info("Flujo recomendado:")
    cli.print_info("1. rules suggest --ai                     # Generar sugerencias")
    cli.print_info("2. rules auto-generate --review           # Crear archivo de reglas")
    cli.print_info("3. rules validate project-rules.yaml     # Validar sintaxis")
    cli.print_info("4. rules apply                            # Aplicar reglas")
    cli.print_info("5. rules report                           # Verificar cumplimiento")
    cli.print_info("")
    cli.print_info("Características avanzadas:")
    cli.print_info("  • Análisis con IA para sugerencias inteligentes")
    cli.print_info("  • Detección automática de tecnologías y patrones")
    cli.print_info("  • Reglas estructuradas con contexto y prioridades")
    cli.print_info("  • Exportación en múltiples formatos (YAML, JSON, Markdown)")
    cli.print_info("  • Revisión interactiva de sugerencias")

# Enhanced help for premium commands
def show_premium_command_help():
    """Show specific help for premium commands"""
    from src.ui.cli import CLI
    cli = CLI()
    cli.print_header("Comandos Premium")
    cli.print_info("Funciones avanzadas ahora disponibles para todos los usuarios.")
    cli.print_info("")
    cli.print_info("Comandos disponibles:")
    cli.print_info("  • premium dashboard                      # Dashboard interactivo avanzado")
    cli.print_info("  • premium test-generator [archivo]      # Generador de tests unitarios")
    cli.print_info("  • premium verify-completeness           # Verificar completitud del proyecto")
    cli.print_info("  • premium implementation [descripción]  # Asistente de implementación")
    cli.print_info("")
    cli.print_info("Ejemplos:")
    cli.print_info("  pp premium dashboard")
    cli.print_info("  pp premium test-generator src/main.py")
    cli.print_info("  pp premium implementation \"sistema de autenticación\"")
    cli.print_info("")
    cli.print_info("Nota: Todas las funciones premium ahora están disponibles gratuitamente")

# Implementación de comandos de IA
@ai_app.command("generate")
@telemetry_command
def ai_generate_code(
    description: Optional[str] = typer.Argument(None, help="Descripción del código a generar"),
    language: str = typer.Option("python", "--language", "-l", help="Lenguaje de programación"),
    provider: str = typer.Option("anthropic", "--provider", "-p", 
                                help="Proveedor de IA (anthropic, copilot)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Archivo donde guardar el código")
):
    """
    Generar código utilizando IA avanzada (característica premium).
    """
    # Check if description parameter is provided
    if not description:
        show_ai_command_help()
        return
    from src.integrations.anthropic_advanced import get_advanced_anthropic_client
    from src.integrations.copilot_advanced import get_advanced_copilot_client
    
    cli.print_header("Generación de Código con IA")
    
    # Premium features now available for all users
    
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
    file_path: Optional[str] = typer.Argument(None, help="Ruta al archivo de código a analizar"),
    language: Optional[str] = typer.Option(None, "--language", "-l", help="Lenguaje de programación"),
    provider: str = typer.Option("anthropic", "--provider", "-p", 
                               help="Proveedor de IA (anthropic, copilot)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", 
                                       help="Archivo donde guardar el análisis")
):
    """
    Analizar código para detectar errores y problemas (característica premium).
    """
    # Check if file_path parameter is provided
    if not file_path:
        show_ai_command_help()
        return
    from src.integrations.anthropic_advanced import get_advanced_anthropic_client
    from src.integrations.copilot_advanced import get_advanced_copilot_client
    import os
    
    cli.print_header("Análisis de Código con IA")
    
    # Premium features now available for all users
    
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
    file_path: Optional[str] = typer.Argument(None, help="Ruta al archivo de código a refactorizar"),
    language: Optional[str] = typer.Option(None, "--language", "-l", help="Lenguaje de programación"),
    provider: str = typer.Option("anthropic", "--provider", "-p", 
                               help="Proveedor de IA (anthropic, copilot)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", 
                                       help="Archivo donde guardar el código refactorizado")
):
    """
    Refactorizar código para mejorar su calidad (característica premium).
    """
    # Check if file_path parameter is provided
    if not file_path:
        show_ai_command_help()
        return
    from src.integrations.anthropic_advanced import get_advanced_anthropic_client
    from src.integrations.copilot_advanced import get_advanced_copilot_client
    import os
    
    cli.print_header("Refactorización de Código con IA")
    
    # Premium features now available for all users
    
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
    file_path: Optional[str] = typer.Argument(None, help="Ruta al archivo de código a explicar"),
    language: Optional[str] = typer.Option(None, "--language", "-l", help="Lenguaje de programación"),
    detail_level: str = typer.Option("standard", "--detail", "-d", 
                                   help="Nivel de detalle (basic, standard, advanced)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", 
                                       help="Archivo donde guardar la explicación")
):
    """
    Generar una explicación detallada del código (característica premium para nivel avanzado).
    """
    # Check if file_path parameter is provided
    if not file_path:
        show_ai_command_help()
        return
    from src.integrations.anthropic_advanced import get_advanced_anthropic_client
    import os
    
    cli.print_header("Explicación de Código con IA")
    
    # Premium features now available for all users - advanced level enabled
    
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
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Ruta donde guardar el dashboard"),
    format: str = typer.Option("markdown", "--format", "-f", help="Formato de salida (html/markdown)"),
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
        if format:
            args.extend(["--format", format])
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


# Implementación de comandos premium (ahora disponibles para todos los usuarios)

@premium_app.command("dashboard")
def premium_dashboard(
    project: str = typer.Argument(".", help="Ruta al proyecto para generar el dashboard"),
    format: str = typer.Option("markdown", "--format", "-f", help="Formato de salida (html/markdown/md)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Ruta donde guardar el dashboard"),
    no_browser: bool = typer.Option(False, "--no-browser", help="No abrir automáticamente en el navegador"),
    detailed: bool = typer.Option(False, "--detailed", help="Incluir análisis detallado de dependencias y arquitectura")
):
    """Genera un dashboard premium con análisis avanzado de arquitectura y métricas detalladas."""
    
    cli.print_header("Dashboard Premium de Proyecto")
    
    # Premium features now available for all users
    
    # Crear instancia del CLI del dashboard
    dashboard_cli = DashboardCLI()
    
    # Configurar argumentos para premium
    args = ["--premium"]
    if project != ".":
        args.extend(["--project", project])
    if format != "html":
        args.extend(["--format", format])
    if output:
        args.extend(["--output", output])
    if no_browser:
        args.append("--no-browser")
    if detailed:
        args.append("--detailed")
    
    # Ejecutar dashboard premium
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
    import os
    
    cli.print_header("Generación de Tests Unitarios")
    
    # Premium features now available for all users
    
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
    import os
    
    cli.print_header("Verificación de Completitud")
    
    # Premium features now available for all users
    
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
            status_icon = "✅" if criteria.get("satisfied") else "❌" if criteria.get("satisfied") is False else "⚠️"
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
    
    cli.print_header("Asistente de Implementación Premium")
    
    # Premium features now available for all users
    
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
   Muestra el estado actual de la telemetría anónima."""
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


@app.command()
def status():
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
    Configura el entorno de forma simple sin telemetría bloqueante.
    """
    try:
        # Simplificar inicialización - solo configurar lo esencial
        pass
    except Exception:
        # Ignorar errores para no bloquear la CLI
        pass
    
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
    """Inicializa una carpeta project-output organizada en el directorio actual.
    
    Crea una estructura de carpetas organizadas para gestionar los archivos generados por ProjectPrompt.
    """
    try:
        # Crear la carpeta principal project-output
        project_prompt_dir = os.path.join(os.getcwd(), "project-output")
        
        if os.path.exists(project_prompt_dir):
            cli.print_warning("La carpeta 'project-output' ya existe en este directorio.")
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

        cli.print_success(f"Carpeta 'project-output' inicializada correctamente en {project_prompt_dir}")
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
