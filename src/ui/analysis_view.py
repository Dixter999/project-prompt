#!/usr/bin/env python3
"""
Vista para mostrar resultados del análisis de proyectos.

Este módulo contiene las funciones para visualizar los resultados
del análisis de estructura de proyectos y funcionalidades detectadas.
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.syntax import Syntax

from src.analyzers.project_scanner import get_project_scanner
from src.analyzers.functionality_detector import get_functionality_detector
from src.utils.logger import get_logger

# Create console instance
console = Console()

# Configurar logger
logger = get_logger()

# Create local CLI helper functions to replace the removed dependency
class LocalCLI:
    def print_header(self, text: str):
        console.print(f"\n[bold cyan]{text}[/bold cyan]")
        console.print("─" * len(text))
    
    def print_info(self, text: str):
        console.print(f"[cyan]ℹ[/cyan] {text}")
    
    def print_warning(self, text: str):
        console.print(f"[yellow]⚠[/yellow] {text}")
    
    def print_error(self, text: str):
        console.print(f"[red]❌[/red] {text}")
    
    def create_table(self, title: str, headers: List[str]) -> Table:
        table = Table(title=title, show_header=True, header_style="bold magenta")
        for header in headers:
            table.add_column(header)
        return table
    
    def print_panel(self, content: str, title: str = None, **kwargs):
        console.print(Panel(content, title=title, **kwargs))
    
    def status(self, text: str):
        return console.status(text)

# Create local CLI instance
cli = LocalCLI()

class AnalysisView:
    """Clase para mostrar resultados del análisis de proyectos."""
    
    @staticmethod
    def show_project_structure(project_data: Dict[str, Any], max_files: int = 50) -> None:
        """
        Muestra la estructura del proyecto en forma de árbol.
        
        Args:
            project_data: Datos del proyecto analizado
            max_files: Número máximo de archivos a mostrar
        """
        cli.print_header("Estructura del Proyecto")
        
        # Obtener el directorio raíz
        root_path = project_data.get('project_path', '')
        if not root_path:
            cli.print_error("No se pudo determinar la ruta del proyecto")
            return
            
        root_dir = os.path.basename(root_path)
        
        # Crear árbol
        tree = Tree(f"[bold blue]{root_dir}[/bold blue]")
        
        # Construir estructura
        files = project_data.get('files', [])
        dirs = {}
        
        # Organizar archivos por directorio
        for file in files[:max_files]:
            path = file.get('path', '')
            if not path:
                continue
                
            parts = path.split('/')
            current = tree
            
            # Navegar o crear la estructura de directorios
            for i, part in enumerate(parts[:-1]):  # Todos menos el último (nombre de archivo)
                full_path = '/'.join(parts[:i+1])
                
                if full_path not in dirs:
                    dirs[full_path] = current.add(f"[bold yellow]{part}/[/bold yellow]")
                current = dirs[full_path]
            
            # Añadir archivo
            file_name = parts[-1]
            language = file.get('language', '')
            
            # Colorear según el lenguaje
            language = language or ''
            lang_lower = language.lower()
            
            if 'python' in lang_lower:
                color = 'green'
            elif 'javascript' in lang_lower or 'typescript' in lang_lower:
                color = 'yellow'
            elif 'html' in lang_lower or 'css' in lang_lower:
                color = 'cyan'
            elif 'markdown' in lang_lower or 'text' in lang_lower:
                color = 'white'
            elif 'json' in lang_lower or 'yaml' in lang_lower:
                color = 'magenta'
            else:
                color = 'blue'
                
            current.add(f"[{color}]{file_name}[/{color}]")
        
        # Mostrar árbol
        console.print(tree)
        
        # Mostrar aviso si se omitieron archivos
        if len(files) > max_files:
            cli.print_warning(f"Se muestran solo {max_files} de {len(files)} archivos.")
            cli.print_info("Usa --output para guardar el análisis completo en un archivo")

    @staticmethod
    def show_functionalities(functionality_data: Dict[str, Any]) -> None:
        """
        Muestra las funcionalidades detectadas en el proyecto.
        
        Args:
            functionality_data: Datos de funcionalidades detectadas
        """
        main_functionalities = functionality_data.get('main_functionalities', [])
        detected = functionality_data.get('detected', {})
        
        cli.print_header("Funcionalidades Detectadas")
        
        if not main_functionalities:
            cli.print_warning("No se detectaron funcionalidades principales en el proyecto")
            return
            
        # Crear tabla de funcionalidades
        func_table = cli.create_table("Resumen de Funcionalidades", ["Funcionalidad", "Confianza", "Descripción"])
        
        # Descripciones de funcionalidades
        descriptions = {
            'authentication': "Sistema de autenticación y manejo de seguridad",
            'database': "Acceso y manipulación de bases de datos",
            'api': "APIs e integraciones con servicios externos",
            'frontend': "Interfaz de usuario y componentes visuales",
            'tests': "Pruebas automatizadas (unitarias, integración, etc.)"
        }
        
        for func_name in main_functionalities:
            func_data = detected.get(func_name, {})
            confidence = func_data.get('confidence', 0)
            
            # Añadir a la tabla
            func_table.add_row(
                func_name.capitalize(),
                f"{confidence}%",
                descriptions.get(func_name, "Funcionalidad detectada")
            )
        
        # Mostrar tabla
        console.print(func_table)
        
        # Mostrar detalles de cada funcionalidad
        cli.print_info("Detalles de funcionalidades detectadas:")
        
        for func_name in main_functionalities:
            func_data = detected.get(func_name, {})
            evidence = func_data.get('evidence', {})
            
            panel_content = []
            
            # Archivos relevantes
            if evidence.get('files'):
                files = evidence.get('files', [])[:5]
                panel_content.append("[bold]Archivos relevantes:[/bold]")
                for file in files:
                    panel_content.append(f"• {os.path.basename(file)}")
                if len(evidence.get('files', [])) > 5:
                    panel_content.append(f"  ... y {len(evidence.get('files', [])) - 5} más")
            
            # Patrones de importación
            if evidence.get('imports'):
                panel_content.append("\n[bold]Importaciones/dependencias:[/bold]")
                imports = evidence.get('imports', [])[:5]
                for imp in imports:
                    panel_content.append(f"• {imp}")
                if len(evidence.get('imports', [])) > 5:
                    panel_content.append(f"  ... y {len(evidence.get('imports', [])) - 5} más")
            
            # Mostrar panel
            if panel_content:
                cli.print_panel(
                    "\n".join(panel_content),
                    f"{func_name.capitalize()} ({func_data.get('confidence', 0)}%)",
                    border_style="blue"
                )
                
    @staticmethod
    def show_languages(project_data: Dict[str, Any]) -> None:
        """
        Muestra los lenguajes de programación detectados.
        
        Args:
            project_data: Datos del proyecto analizado
        """
        languages = project_data.get('languages', {})
        if not languages:
            return
            
        cli.print_header("Lenguajes Detectados")
        
        # Crear tabla de lenguajes
        lang_table = cli.create_table("Estadísticas de Lenguajes", 
                                     ["Lenguaje", "Archivos", "% del proyecto", "Tamaño (KB)"])
        
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
        
        # Mostrar gráfico simple de barras
        cli.print_info("Distribución de lenguajes (por número de archivos):")
        
        # Ordenar lenguajes por número de archivos
        sorted_langs = sorted(
            [(lang, data) for lang, data in languages.items() if not lang.startswith('_')],
            key=lambda x: x[1].get('files', 0),
            reverse=True
        )
        
        # Mostrar hasta 5 lenguajes principales
        max_files = max([data.get('files', 0) for _, data in sorted_langs[:5]] or [1])
        bar_width = 40
        
        for lang, data in sorted_langs[:5]:
            files = data.get('files', 0)
            bar_length = int((files / max_files) * bar_width)
            bar = "█" * bar_length
            console.print(f"{lang.ljust(15)} {bar} ({files} archivos)")

    @staticmethod
    def list_functionalities(project_path: str, max_files: int = 1000, max_size: float = 5.0) -> Dict[str, Any]:
        """
        Lista las funcionalidades detectadas en el proyecto.
        
        Args:
            project_path: Ruta al proyecto
            max_files: Número máximo de archivos a analizar
            max_size: Tamaño máximo de archivo a analizar en MB
            
        Returns:
            Datos de las funcionalidades detectadas
        """
        # Asegurar que la ruta existe
        if not os.path.isdir(project_path):
            cli.print_error(f"La ruta especificada no es un directorio válido: {project_path}")
            return {}
        
        try:
            # Crear escáner y detector
            scanner = get_project_scanner(max_file_size_mb=max_size, max_files=max_files)
            detector = get_functionality_detector(scanner=scanner)
            
            # Mostrar progreso
            with cli.status("Detectando funcionalidades en el proyecto..."):
                # Realizar análisis
                result = detector.detect_functionalities(project_path)
            
            return result
        except Exception as e:
            logger.error(f"Error al listar funcionalidades: {e}", exc_info=True)
            cli.print_error(f"Error al analizar el proyecto: {e}")
            return {}

    @staticmethod
    def show_connections_analysis(connections_data: Dict[str, Any], detailed: bool = False) -> None:
        """
        Muestra el análisis de conexiones entre archivos.
        
        Args:
            connections_data: Datos de conexiones
            detailed: Si se debe mostrar información detallada
        """
        cli.print_header("Análisis de Conexiones Entre Archivos")
        
        # Información general
        cli.print_info(f"Proyecto: {os.path.basename(connections_data['project_path'])}")
        cli.print_info(f"Archivos analizados: {connections_data['files_analyzed']}")
        
        # Información sobre exclusiones
        if 'files_excluded' in connections_data:
            excluded = connections_data['files_excluded']
            cli.print_info(f"Archivos excluidos: {excluded.get('total_excluded', 0)}")
            
            if detailed:
                exclude_table = Table(title="Archivos Excluidos")
                exclude_table.add_column("Tipo de exclusión", style="cyan")
                exclude_table.add_column("Cantidad", style="green")
                
                exclude_table.add_row("Por extensión (multimedia, binarios)", str(excluded.get('by_extension', 0)))
                exclude_table.add_row("Por patrón (dir/archivos no relevantes)", str(excluded.get('by_pattern', 0)))
                exclude_table.add_row("HTML puramente presentacional", str(excluded.get('html_presentational', 0)))
                exclude_table.add_row("Total excluidos", str(excluded.get('total_excluded', 0)))
                
                console.print(exclude_table)
        
        # Estadísticas de lenguajes
        langs_table = Table(title="Lenguajes Detectados")
        langs_table.add_column("Lenguaje", style="cyan")
        langs_table.add_column("Archivos", style="green")
        
        for lang, count in connections_data['language_stats'].items():
            langs_table.add_row(lang, str(count))
        console.print(langs_table)
        
        # Componentes conectados
        connected_components = connections_data['connected_components']
        cli.print_info(f"Componentes conectados: {len(connected_components)}")
        
        if connected_components and detailed:
            comp_table = Table(title="Principales Componentes Conectados")
            comp_table.add_column("Componente", style="cyan")
            comp_table.add_column("Archivos", style="green")
            comp_table.add_column("Ejemplo", style="yellow")
            
            for i, component in enumerate(connected_components[:5]):
                example = component[0] if component else "N/A"
                comp_table.add_row(f"Comp. {i+1}", str(len(component)), example)
            console.print(comp_table)
        
        # Archivos desconectados
        disconnected = connections_data['disconnected_files']
        cli.print_info(f"Archivos desconectados: {len(disconnected)}")
        
        if disconnected and detailed and len(disconnected) > 0:
            disc_panel = Panel(
                "\n".join(disconnected[:10] + (["..."] if len(disconnected) > 10 else [])),
                title="Archivos Desconectados (10 primeros)",
                border_style="yellow"
            )
            console.print(disc_panel)
        
        # Mostrar algunos archivos y sus importaciones
        if detailed:
            imports_table = Table(title="Importaciones por Archivo (10 primeros)")
            imports_table.add_column("Archivo", style="cyan")
            imports_table.add_column("Lenguaje", style="green")
            imports_table.add_column("Importaciones", style="yellow")
            
            count = 0
            for file_path, file_data in connections_data['file_imports'].items():
                if count >= 10:
                    break
                    
                imports = ", ".join(file_data['imports'][:5])
                if len(file_data['imports']) > 5:
                    imports += f" ... (+{len(file_data['imports']) - 5})"
                
                imports_table.add_row(
                    file_path, 
                    file_data['language'],
                    imports or "N/A"
                )
                count += 1
                
            console.print(imports_table)
    
    @staticmethod
    def show_dependency_graph(graph_data: Dict[str, Any], detailed: bool = False) -> None:
        """
        Muestra el grafo de dependencias entre archivos.
        
        Args:
            graph_data: Datos del grafo
            detailed: Si se debe mostrar información detallada
        """
        cli.print_header("Grafo de Dependencias Entre Archivos")
        
        # Métricas del grafo
        metrics_table = Table(title="Métricas del Grafo")
        metrics_table.add_column("Métrica", style="cyan")
        metrics_table.add_column("Valor", style="green")
        
        metrics = graph_data['metrics']
        for metric, value in metrics.items():
            if isinstance(value, float):
                metrics_table.add_row(metric.replace('_', ' ').title(), f"{value:.2f}")
            else:
                metrics_table.add_row(metric.replace('_', ' ').title(), str(value))
                
        console.print(metrics_table)
        
        # Archivos centrales
        central_files = graph_data['central_files'][:10]  # Top 10
        
        if central_files:
            central_table = Table(title="Archivos Centrales (10 primeros)")
            central_table.add_column("Archivo", style="cyan")
            central_table.add_column("Conexiones", style="green")
            central_table.add_column("Entrantes", style="yellow")
            central_table.add_column("Salientes", style="magenta")
            
            for file_info in central_files:
                central_table.add_row(
                    file_info['file'],
                    str(file_info['total']),
                    str(file_info['in_degree']),
                    str(file_info['out_degree'])
                )
                
            console.print(central_table)
        
        # Ciclos de dependencias
        cycles = graph_data['file_cycles']
        if cycles:
            cli.print_info(f"Ciclos de dependencias: {len(cycles)}")
            
            if detailed and cycles:
                cycles_table = Table(title="Ciclos de Dependencias (5 primeros)")
                cycles_table.add_column("Ciclo", style="red")
                cycles_table.add_column("Longitud", style="green")
                
                for i, cycle in enumerate(cycles[:5]):
                    cycle_str = " → ".join([os.path.basename(f) for f in cycle])
                    cycles_table.add_row(f"{i+1}. {cycle_str} → ...", str(len(cycle)))
                    
                console.print(cycles_table)

def analyze_connections(
    project_path: str, 
    max_files: int = 5000, 
    output: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analiza las conexiones entre archivos de un proyecto.
    
    Args:
        project_path: Ruta al proyecto
        max_files: Número máximo de archivos a analizar
        output: Ruta para guardar el resultado (opcional)
        
    Returns:
        Diccionario con información de conexiones
    """
    from src.analyzers.connection_analyzer import get_connection_analyzer
    
    # Analizar conexiones
    analyzer = get_connection_analyzer()
    connections = analyzer.analyze_connections(project_path, max_files)
    
    # Guardar resultado si se especificó output
    if output:
        analyzer.export_connections_json(connections, output)
        logger.info(f"Datos de conexiones guardados en: {output}")
    
    return connections

def generate_dependency_graph(
    project_path: str, 
    max_files: int = 5000, 
    output: Optional[str] = None,
    markdown_output: Optional[str] = None
) -> Dict[str, Any]:
    """
    Genera un grafo de dependencias entre archivos.
    
    Args:
        project_path: Ruta al proyecto
        max_files: Número máximo de archivos a analizar
        output: Ruta para guardar el resultado JSON (opcional)
        markdown_output: Ruta para guardar la visualización en markdown (opcional)
        
    Returns:
        Diccionario con grafo de dependencias
    """
    from src.analyzers.dependency_graph import get_dependency_graph
    
    # Generar grafo de dependencias
    graph_generator = get_dependency_graph()
    graph = graph_generator.build_dependency_graph(project_path, max_files)
    
    # Guardar resultado como JSON si se especificó output
    if output:
        graph_generator.export_graph_json(graph, output)
        logger.info(f"Grafo de dependencias guardado en: {output}")
    
    # Generar y guardar visualización en markdown si se solicitó
    if markdown_output:
        markdown = graph_generator.generate_markdown_visualization(graph)
        
        # Asegurar que el directorio existe
        os.makedirs(os.path.dirname(os.path.abspath(markdown_output)), exist_ok=True)
        
        # Guardar markdown
        with open(markdown_output, 'w', encoding='utf-8') as f:
            f.write(markdown)
            
        logger.info(f"Visualización markdown guardada en: {markdown_output}")
    
    return graph

# Instancia global para uso directo
analysis_view = AnalysisView()
