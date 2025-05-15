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

from src.ui.cli import cli
from src.analyzers.project_scanner import get_project_scanner
from src.analyzers.functionality_detector import get_functionality_detector
from src.utils.logger import get_logger

# Configurar logger
logger = get_logger()
console = Console()

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
                    f"{func_name.capitalize()} ({func_data.get('confidence', 0)}%)",
                    "\n".join(panel_content),
                    "blue"
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

# Instancia global para uso directo
analysis_view = AnalysisView()
