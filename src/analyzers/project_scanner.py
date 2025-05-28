#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para escanear la estructura de proyectos.

Este módulo proporciona funcionalidades para identificar y analizar
la estructura de directorios y archivos en un proyecto de código.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Tuple
import json
import time
from collections import Counter

from src.analyzers.file_analyzer import FileAnalyzer, get_file_analyzer
from src.utils.logger import get_logger
from src.utils.gitignore_parser import GitignoreParser, get_gitignore_parser

# Configurar logger
logger = get_logger()

# Directorios comunes que suelen ignorarse
DEFAULT_IGNORE_DIRS = [
    '.git', '.svn', '.hg', '.idea', '.vscode', '__pycache__',
    'node_modules', 'venv', '.env', 'env', '.venv', 'ENV',
    'build', 'dist', 'target', 'bin', 'obj',
    '.pytest_cache', '.coverage', 'htmlcov',
    '.next', '.nuxt', '.output',
]

# Patrones para archivos a ignorar
DEFAULT_IGNORE_FILES = [
    '.DS_Store', 'Thumbs.db', '*.pyc', '*.pyo', '*.pyd',
    '*.so', '*.dylib', '*.dll', '*.exe', '*.bin',
    '*.cache', '*.log', '*.tmp', '*.temp',
]


class ProjectScanner:
    """Escáner para la estructura de archivos y directorios de un proyecto."""
    
    def __init__(self, 
                 ignore_dirs: Optional[List[str]] = None,
                 ignore_files: Optional[List[str]] = None,
                 max_file_size_mb: float = 5.0,
                 max_files: int = 10000,
                 progress_callback=None):
        """
        Inicializar el escáner de proyectos.
        
        Args:
            ignore_dirs: Lista de directorios a ignorar
            ignore_files: Lista de patrones de archivos a ignorar
            max_file_size_mb: Tamaño máximo de archivo a analizar en MB
            max_files: Número máximo de archivos a procesar
            progress_callback: Función de callback para reportar progreso
        """
        self.ignore_dirs = ignore_dirs or DEFAULT_IGNORE_DIRS
        self.ignore_files = ignore_files or DEFAULT_IGNORE_FILES
        self.max_file_size = max_file_size_mb
        self.max_files = max_files
        self.file_analyzer = get_file_analyzer(max_file_size_mb)
        self.progress_callback = progress_callback
        
        # Parser de gitignore - se inicializará en scan_project
        self.gitignore_parser: Optional[GitignoreParser] = None
        
        # Atributos para almacenar resultados
        self.structure = {}
        self.files = []
        self.languages = {}
        self.important_files = {}
        self.dependencies = {}
        self.stats = {
            'total_files': 0,
            'total_dirs': 0,
            'analyzed_files': 0,
            'binary_files': 0,
            'skipped_files': 0,
            'total_size_kb': 0,
            'gitignore_excluded': 0,  # Nuevo contador para archivos excluidos por gitignore
        }
    
    def _report_progress(self, current_file: str = None, message: str = None):
        """
        Reportar progreso del escaneo si hay un callback configurado.
        
        Args:
            current_file: Archivo actualmente siendo procesado
            message: Mensaje de estado personalizado
        """
        if self.progress_callback:
            progress_info = {
                'total_files': self.stats['total_files'],
                'analyzed_files': self.stats['analyzed_files'],
                'total_dirs': self.stats['total_dirs'],
                'current_file': current_file,
                'message': message
            }
            self.progress_callback(progress_info)
    
    def _should_ignore_dir(self, dir_path: str, project_path: str = None) -> bool:
        """
        Comprobar si se debe ignorar un directorio.
        
        Args:
            dir_path: Ruta completa al directorio o solo el nombre
            project_path: Ruta raíz del proyecto para verificar .gitignore
        """
        dir_name = os.path.basename(dir_path)
        
        # Verificar con gitignore primero si está disponible
        if self.gitignore_parser and project_path:
            if self.gitignore_parser.should_ignore(dir_path, project_path):
                return True
        
        # Verificar patrones tradicionales
        return any(
            # Ignorar directorios que empiezan con punto si no están explícitamente permitidos
            (dir_name.startswith('.') and dir_name not in ['.github'])
            # Ignorar directorios específicos 
            or dir_name == ignore_dir
            # Ignorar patrones de directorios
            or (ignore_dir.startswith('*') and dir_name.endswith(ignore_dir[1:]))
            or (ignore_dir.endswith('*') and dir_name.startswith(ignore_dir[:-1]))
            for ignore_dir in self.ignore_dirs
        )
    
    def _should_ignore_file(self, file_path: str, project_path: str = None) -> bool:
        """
        Comprobar si se debe ignorar un archivo.
        
        Args:
            file_path: Ruta completa al archivo o solo el nombre
            project_path: Ruta raíz del proyecto para verificar .gitignore
        """
        file_name = os.path.basename(file_path)
        
        # Verificar con gitignore primero si está disponible
        if self.gitignore_parser and project_path:
            if self.gitignore_parser.should_ignore(file_path, project_path):
                return True
        
        # Verificar patrones tradicionales
        return any(
            # Ignorar archivos que empiezan con punto si no están explícitamente permitidos
            (file_name.startswith('.') and file_name not in ['.gitignore', '.env', '.editorconfig'])
            # Patrones exactos
            or file_name == ignore_pattern
            # Patrones con comodín
            or (ignore_pattern.startswith('*') and file_name.endswith(ignore_pattern[1:]))
            or (ignore_pattern.endswith('*') and file_name.startswith(ignore_pattern[:-1]))
            for ignore_pattern in self.ignore_files
        )
    
    def scan_project(self, project_path: str) -> Dict[str, Any]:
        """
        Escanear un proyecto y analizar su estructura.
        
        Args:
            project_path: Ruta al directorio del proyecto
            
        Returns:
            Dict con la estructura y análisis completo
        """
        start_time = time.time()
        logger.info(f"Iniciando escaneo del proyecto en: {project_path}")
        
        try:
            # Reiniciar estado
            self.structure = {}
            self.files = []
            self.languages = {}
            self.important_files = {}
            self.dependencies = {}
            
            # Inicializar parser de gitignore
            self.gitignore_parser = get_gitignore_parser(project_path)
            if self.gitignore_parser and self.gitignore_parser.get_ignored_count() > 0:
                logger.info(f"Cargadas {self.gitignore_parser.get_ignored_count()} reglas de .gitignore")
            
            self.stats = {
                'total_files': 0, 
                'total_dirs': 0,
                'analyzed_files': 0,
                'binary_files': 0,
                'skipped_files': 0,
                'total_size_kb': 0,
                'gitignore_excluded': 0,
            }
            
            # Comenzar escaneo recursivo
            self.structure = self._scan_directory(project_path, project_path)
            
            # Analizar dependencias a nivel de proyecto
            self._report_progress(message="Analizando dependencias del proyecto")
            self._analyze_project_dependencies()
            
            # Identificar lenguajes principales del proyecto
            self._report_progress(message="Identificando lenguajes principales")
            self._identify_main_languages()
            
            # Identificar archivos importantes
            self._report_progress(message="Identificando archivos importantes")
            self._identify_important_files()
            
            # Calcular tiempo total
            scan_time = time.time() - start_time
            
            # Construir resultado
            result = {
                'project_path': project_path,
                'structure': self.structure,
                'files': self.files,
                'stats': self.stats,
                'languages': self.languages,
                'dependencies': self.dependencies,
                'important_files': self.important_files,
                'scan_time': round(scan_time, 2),
            }
            
            logger.info(f"Escaneo completado en {round(scan_time, 2)} segundos. "
                       f"Archivos analizados: {self.stats['analyzed_files']} de {self.stats['total_files']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error al escanear proyecto: {e}")
            raise
    
    def _scan_directory(self, dir_path: str, base_path: str, depth: int = 0) -> Dict[str, Any]:
        """
        Escanear recursivamente un directorio y sus contenidos.
        
        Args:
            dir_path: Ruta completa al directorio
            base_path: Ruta base del proyecto para calcular rutas relativas
            depth: Nivel de profundidad actual (para limitar recursión)
            
        Returns:
            Dict con la estructura del directorio
        """
        if depth > 20:  # Evitar recursión excesiva
            logger.warning(f"Alcanzada profundidad máxima en: {dir_path}")
            return {}
        
        try:
            # Preparar estructura
            dir_name = os.path.basename(dir_path)
            dir_info = {
                'name': dir_name,
                'path': os.path.relpath(dir_path, base_path),
                'type': 'directory',
                'contents': {},
            }
            
            # Actualizar estadísticas
            self.stats['total_dirs'] += 1
            
            # Reportar progreso del directorio
            relative_dir = os.path.relpath(dir_path, base_path)
            self._report_progress(message=f"Escaneando directorio: {relative_dir}")
            
            # Listar contenidos
            for item_name in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item_name)
                
                # Detener si hemos alcanzado el límite de archivos
                if self.stats['total_files'] >= self.max_files:
                    logger.warning(f"Alcanzado límite de archivos ({self.max_files}). Deteniendo escaneo.")
                    break
                
                # Procesar subdirectorios
                if os.path.isdir(item_path):
                    if not self._should_ignore_dir(item_path, base_path):
                        subdir_info = self._scan_directory(item_path, base_path, depth + 1)
                        if subdir_info:  # Solo incluir si no está vacío
                            dir_info['contents'][item_name] = subdir_info
                    else:
                        # Contar archivos ignorados por gitignore si aplicó
                        if (self.gitignore_parser and 
                            self.gitignore_parser.should_ignore(item_path, base_path)):
                            self.stats['gitignore_excluded'] += 1
                
                # Procesar archivos
                elif os.path.isfile(item_path):
                    if not self._should_ignore_file(item_path, base_path):
                        file_info = self._scan_file(item_path, base_path)
                        dir_info['contents'][item_name] = file_info
                    else:
                        # Contar archivos ignorados por gitignore si aplicó
                        if (self.gitignore_parser and 
                            self.gitignore_parser.should_ignore(item_path, base_path)):
                            self.stats['gitignore_excluded'] += 1
            
            return dir_info
            
        except Exception as e:
            logger.error(f"Error al escanear directorio {dir_path}: {e}")
            return {}
    
    def _scan_file(self, file_path: str, base_path: str) -> Dict[str, Any]:
        """
        Escanear un archivo individual.
        
        Args:
            file_path: Ruta al archivo
            base_path: Ruta base del proyecto para calcular rutas relativas
            
        Returns:
            Dict con información del archivo
        """
        self.stats['total_files'] += 1
        
        # Reportar progreso
        relative_path = os.path.relpath(file_path, base_path)
        self._report_progress(current_file=relative_path, message="Analizando archivo")
        
        try:
            # Comprobar tamaño
            file_size = os.path.getsize(file_path)
            
            if file_size > (self.max_file_size * 1024 * 1024):
                # Archivo demasiado grande
                self.stats['skipped_files'] += 1
                
                return {
                    'name': os.path.basename(file_path),
                    'path': os.path.relpath(file_path, base_path),
                    'type': 'file',
                    'size_kb': round(file_size / 1024, 2),
                    'skipped': True,
                    'reason': 'file_too_large',
                }
            
            # Analizar archivo
            file_info = self.file_analyzer.analyze_file(file_path)
            
            # Asegurar ruta relativa
            file_info['path'] = os.path.relpath(file_path, base_path)
            file_info['type'] = 'file'
            
            # Actualizar estadísticas
            self.stats['analyzed_files'] += 1
            self.stats['total_size_kb'] += file_info['size_kb']
            
            if file_info.get('is_binary', False):
                self.stats['binary_files'] += 1
            
            # Añadir a lista de archivos
            self.files.append(file_info)
            
            # Actualizar contador de lenguajes
            if file_info.get('language'):
                language = file_info['language']
                if language not in self.languages:
                    self.languages[language] = {
                        'files': 0,
                        'size_kb': 0,
                    }
                self.languages[language]['files'] += 1
                self.languages[language]['size_kb'] += file_info.get('size_kb', 0)
            
            # Registrar archivo importante
            if file_info.get('category'):
                category = file_info['category']
                if category not in self.important_files:
                    self.important_files[category] = []
                self.important_files[category].append(file_info['path'])
            
            # Registrar dependencias
            for dependency in file_info.get('dependencies', []):
                if dependency not in self.dependencies:
                    self.dependencies[dependency] = {
                        'count': 0,
                        'files': []
                    }
                self.dependencies[dependency]['count'] += 1
                self.dependencies[dependency]['files'].append(file_info['path'])
            
            return file_info
            
        except Exception as e:
            logger.error(f"Error al escanear archivo {file_path}: {e}")
            self.stats['skipped_files'] += 1
            
            return {
                'name': os.path.basename(file_path),
                'path': os.path.relpath(file_path, base_path),
                'type': 'file',
                'skipped': True,
                'reason': f'error: {str(e)}',
            }
    
    def _identify_main_languages(self) -> None:
        """Identificar y clasificar los lenguajes principales del proyecto."""
        if not self.languages:
            return
            
        # Ordenar lenguajes por número de archivos
        languages_list = sorted(
            self.languages.items(),
            key=lambda x: (x[1]['files'], x[1]['size_kb']),
            reverse=True
        )
        
        # Calcular porcentajes
        total_files = sum(lang[1]['files'] for lang in languages_list)
        for lang_name, lang_data in self.languages.items():
            percentage = (lang_data['files'] / total_files * 100) if total_files else 0
            self.languages[lang_name]['percentage'] = round(percentage, 1)
        
        # Marcar lenguajes principales (>10%)
        main_languages = []
        secondary_languages = []
        
        for lang_name, lang_data in self.languages.items():
            if lang_data['percentage'] >= 10:
                main_languages.append(lang_name)
            elif lang_data['percentage'] >= 2:
                secondary_languages.append(lang_name)
        
        self.languages['_main'] = main_languages
        self.languages['_secondary'] = secondary_languages
    
    def _identify_important_files(self) -> None:
        """Identificar archivos importantes adicionales basándose en el análisis."""
        # Identificar archivo principal
        if 'main' not in self.important_files or not self.important_files['main']:
            main_candidates = []
            
            # Buscar por convención en la raíz
            for file_info in self.files:
                if os.path.dirname(file_info['path']) == '':  # Si está en la raíz
                    name = file_info['name'].lower()
                    if 'main' in name or 'app' in name or 'server' in name or 'index' in name:
                        main_candidates.append(file_info['path'])
            
            if main_candidates:
                if 'main' not in self.important_files:
                    self.important_files['main'] = []
                self.important_files['main'].extend(main_candidates)
    
    def _analyze_project_dependencies(self) -> None:
        """Analizar dependencias a nivel de proyecto."""
        # Contabilizar dependencias
        if not self.dependencies:
            return
            
        # Ordenar por frecuencia
        sorted_dependencies = sorted(
            self.dependencies.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        
        # Identificar dependencias principales (más de 3 referencias)
        main_dependencies = []
        
        for dep_name, dep_data in sorted_dependencies:
            if dep_data['count'] >= 3:
                main_dependencies.append(dep_name)
        
        # Guardar lista de dependencias principales
        self.dependencies['_main'] = main_dependencies

    def get_dependency_graph(self, max_items: int = 20) -> Dict[str, List[str]]:
        """
        Generar un gráfico de dependencias para los archivos principales.
        
        Args:
            max_items: Número máximo de archivos a incluir
            
        Returns:
            Dict con grafo de dependencias
        """
        graph = {}
        file_count = 0
        
        # Seleccionar archivos importantes primero
        important_paths = []
        for category, paths in self.important_files.items():
            if category not in ['_main', '_secondary']:  # Skip meta-categories
                important_paths.extend(paths)
        
        # Priorizar archivos importantes
        prioritized_files = []
        for file_info in self.files:
            if file_info['path'] in important_paths:
                prioritized_files.append(file_info)
                
        # Añadir otros archivos con dependencias
        for file_info in self.files:
            if file_info['path'] not in important_paths and file_info.get('dependencies', []):
                prioritized_files.append(file_info)
        
        # Construir grafo simplificado
        for file_info in prioritized_files[:max_items]:
            file_path = file_info['path']
            file_deps = file_info.get('dependencies', [])
            
            if file_deps:
                graph[file_path] = file_deps
                file_count += 1
            
            if file_count >= max_items:
                break
        
        return graph


def get_project_scanner(
    ignore_dirs: Optional[List[str]] = None,
    ignore_files: Optional[List[str]] = None,
    max_file_size_mb: float = 5.0,
    max_files: int = 10000,
    progress_callback=None
) -> ProjectScanner:
    """
    Obtener una instancia configurada del escáner de proyectos.
    
    Args:
        ignore_dirs: Lista de directorios a ignorar
        ignore_files: Lista de patrones de archivos a ignorar
        max_file_size_mb: Tamaño máximo de archivo a analizar en MB
        max_files: Número máximo de archivos a procesar
        progress_callback: Función de callback para reportar progreso
        
    Returns:
        Instancia de ProjectScanner
    """
    return ProjectScanner(
        ignore_dirs=ignore_dirs,
        ignore_files=ignore_files,
        max_file_size_mb=max_file_size_mb,
        max_files=max_files,
        progress_callback=progress_callback
    )
