#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Analizador de dependencias usando Madge para procesamiento eficiente.

Este módulo usa Madge para generar grafos de dependencias rápidamente
y filtra archivos importantes para mejorar el rendimiento en proyectos grandes.
"""

import os
import json
import subprocess
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict, Counter
from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger()


class MadgeAnalyzer:
    """
    Analizador de dependencias usando Madge para eficiencia.
    
    Usa Madge para análisis rápido y filtra archivos importantes
    basándose en el número de dependencias para mejorar rendimiento.
    """
    
    def __init__(self):
        """Inicializar el analizador Madge."""
        self.min_dependencies = 3  # Mínimo de dependencias para considerar archivo importante
        self.max_files_to_analyze = 1000  # Máximo de archivos importantes a analizar
        
    def is_madge_available(self) -> bool:
        """Verificar si Madge está disponible."""
        try:
            result = subprocess.run(['npx', 'madge', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_dependency_graph(self, project_path: str, 
                           file_extensions: List[str] = None) -> Dict[str, Any]:
        """
        Obtener grafo de dependencias usando Madge.
        
        Args:
            project_path: Ruta al proyecto
            file_extensions: Extensiones de archivos a analizar
            
        Returns:
            Diccionario con el grafo de dependencias
        """
        if not self.is_madge_available():
            logger.warning("Madge no está disponible, usando análisis manual")
            return self._fallback_analysis(project_path)
        
        try:
            # Configurar parámetros de Madge
            cmd = ['npx', 'madge', '--json']
            
            # Detectar tipo de proyecto y configurar extensiones apropiadas
            python_files = False
            js_files = False
            
            # Verificar tipos de archivos en el directorio
            for root, dirs, files in os.walk(project_path):
                if python_files and js_files:
                    break
                for f in files[:20]:  # Check first 20 files only
                    if f.endswith('.py'):
                        python_files = True
                    elif f.endswith(('.js', '.ts', '.jsx', '.tsx')):
                        js_files = True
                        
                # Solo verificar el primer nivel para eficiencia
                break
            
            logger.info(f"Archivos detectados - Python: {python_files}, JS/TS: {js_files}")
            
            # Configurar extensiones basándose en el tipo de proyecto
            if python_files and not js_files:
                # Proyecto Python - usar análisis optimizado
                logger.info("Proyecto Python puro detectado - usando análisis optimizado")
                return self._python_optimized_analysis(project_path)
            
            if file_extensions:
                for ext in file_extensions:
                    cmd.extend(['--extensions', ext])
            elif js_files:
                # Proyecto JavaScript/TypeScript
                cmd.extend(['--extensions', 'js,ts,jsx,tsx'])
            
            # Excluir directorios comunes que no son relevantes
            exclude_patterns = [
                'node_modules',
                '.git',
                '__pycache__',
                '.pytest_cache',
                'dist',
                'build',
                '.venv',
                'venv'
            ]
            
            for pattern in exclude_patterns:
                cmd.extend(['--exclude', pattern])
            
            cmd.append(project_path)
            
            # Ejecutar Madge
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  timeout=60, cwd=project_path)  # Aumentar timeout a 60 segundos
            
            if result.returncode != 0:
                logger.warning(f"Madge falló: {result.stderr}")
                return self._fallback_analysis(project_path)
            
            # Parsear resultado JSON
            dependency_data = json.loads(result.stdout)
            
            return self._process_madge_output(dependency_data, project_path)
            
        except Exception as e:
            logger.warning(f"Error usando Madge: {e}")
            return self._fallback_analysis(project_path)
    
    def _process_madge_output(self, madge_data: Dict, project_path: str) -> Dict[str, Any]:
        """
        Procesar la salida de Madge para extraer información útil.
        
        Args:
            madge_data: Datos de Madge en formato JSON
            project_path: Ruta al proyecto
            
        Returns:
            Diccionario procesado con información de dependencias
        """
        # Contar dependencias para cada archivo
        dependency_counts = defaultdict(int)
        reverse_dependencies = defaultdict(set)
        
        for file_path, dependencies in madge_data.items():
            dependency_counts[file_path] = len(dependencies)
            
            # Construir dependencias inversas
            for dep in dependencies:
                reverse_dependencies[dep].add(file_path)
        
        # Encontrar archivos importantes (con muchas dependencias)
        important_files = self._find_important_files(
            dependency_counts, reverse_dependencies, project_path
        )
        
        # Generar grupos de funcionalidad
        functionality_groups = self._detect_functionality_groups(
            important_files, madge_data, project_path
        )
        
        # Calcular métricas
        metrics = self._calculate_metrics(madge_data, important_files)
        
        return {
            'dependency_graph': madge_data,
            'important_files': important_files,
            'functionality_groups': functionality_groups,
            'metrics': metrics,
            'analysis_type': 'madge'
        }
    
    def _find_important_files(self, dependency_counts: Dict[str, int], 
                            reverse_dependencies: Dict[str, Set], 
                            project_path: str) -> List[Dict[str, Any]]:
        """
        Encontrar archivos importantes basándose en dependencias.
        
        Args:
            dependency_counts: Contador de dependencias por archivo
            reverse_dependencies: Dependencias inversas
            project_path: Ruta al proyecto
            
        Returns:
            Lista de archivos importantes con sus métricas
        """
        important_files = []
        
        for file_path, dep_count in dependency_counts.items():
            reverse_count = len(reverse_dependencies[file_path])
            
            # Calcular puntuación de importancia
            importance_score = dep_count + (reverse_count * 2)  # Peso mayor para dependencias inversas
            
            if (dep_count >= self.min_dependencies or 
                reverse_count >= self.min_dependencies or
                importance_score >= 5):
                
                # Obtener información adicional del archivo
                full_path = os.path.join(project_path, file_path)
                file_info = self._get_file_info(full_path, file_path)
                
                important_files.append({
                    'path': file_path,
                    'full_path': full_path,
                    'dependencies_out': dep_count,
                    'dependencies_in': reverse_count,
                    'importance_score': importance_score,
                    'file_info': file_info
                })
        
        # Ordenar por importancia y limitar resultados
        important_files.sort(key=lambda x: x['importance_score'], reverse=True)
        return important_files[:self.max_files_to_analyze]
    
    def _get_file_info(self, full_path: str, relative_path: str) -> Dict[str, Any]:
        """
        Obtener información adicional de un archivo.
        
        Args:
            full_path: Ruta completa al archivo
            relative_path: Ruta relativa del archivo
            
        Returns:
            Diccionario con información del archivo
        """
        try:
            stat = os.stat(full_path)
            file_extension = Path(full_path).suffix
            
            # Determinar tipo de archivo
            file_type = self._determine_file_type(file_extension, relative_path)
            
            return {
                'size': stat.st_size,
                'extension': file_extension,
                'type': file_type,
                'directory': os.path.dirname(relative_path)
            }
        except OSError:
            return {
                'size': 0,
                'extension': '',
                'type': 'unknown',
                'directory': ''
            }
    
    def _determine_file_type(self, extension: str, path: str) -> str:
        """
        Determinar el tipo de archivo basándose en extensión y ruta.
        
        Args:
            extension: Extensión del archivo
            path: Ruta del archivo
            
        Returns:
            Tipo de archivo categorizado
        """
        # Mapeo de extensiones a tipos
        type_mapping = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'react',
            '.tsx': 'react-typescript',
            '.vue': 'vue',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'header',
            '.css': 'stylesheet',
            '.scss': 'stylesheet',
            '.html': 'markup',
            '.json': 'config',
            '.yaml': 'config',
            '.yml': 'config'
        }
        
        # Determinar por extensión
        file_type = type_mapping.get(extension.lower(), 'other')
        
        # Refinamiento basado en ruta
        path_lower = path.lower()
        if 'test' in path_lower or 'spec' in path_lower:
            file_type += '-test'
        elif 'config' in path_lower or 'settings' in path_lower:
            file_type = 'config'
        elif 'api' in path_lower or 'service' in path_lower:
            file_type += '-service'
        elif 'component' in path_lower or 'ui' in path_lower:
            file_type += '-ui'
        
        return file_type
    
    def _detect_functionality_groups(self, important_files: List[Dict[str, Any]], 
                                   dependency_graph: Dict[str, List], 
                                   project_path: str) -> List[Dict[str, Any]]:
        """
        Detectar grupos de funcionalidad basándose en dependencias y estructura.
        
        Args:
            important_files: Lista de archivos importantes
            dependency_graph: Grafo de dependencias
            project_path: Ruta al proyecto
            
        Returns:
            Lista de grupos de funcionalidad detectados
        """
        groups = []
        
        # Agrupar por directorio
        directory_groups = defaultdict(list)
        for file_info in important_files:
            directory = file_info['file_info']['directory']
            if directory:
                directory_groups[directory].append(file_info)
        
        # Agrupar por tipo de archivo
        type_groups = defaultdict(list)
        for file_info in important_files:
            file_type = file_info['file_info']['type']
            type_groups[file_type].append(file_info)
        
        # Crear grupos de directorio
        for directory, files in directory_groups.items():
            if len(files) >= 2:  # Al menos 2 archivos importantes
                groups.append({
                    'name': f"Directory: {directory}",
                    'type': 'directory',
                    'files': files,
                    'size': len(files),
                    'total_importance': sum(f['importance_score'] for f in files)
                })
        
        # Crear grupos por tipo
        for file_type, files in type_groups.items():
            if len(files) >= 3:  # Al menos 3 archivos del mismo tipo
                groups.append({
                    'name': f"Type: {file_type}",
                    'type': 'file_type',
                    'files': files,
                    'size': len(files),
                    'total_importance': sum(f['importance_score'] for f in files)
                })
        
        # Detectar grupos de dependencias circulares
        circular_groups = self._detect_circular_dependencies(important_files, dependency_graph)
        groups.extend(circular_groups)
        
        # Ordenar grupos por importancia
        groups.sort(key=lambda x: x['total_importance'], reverse=True)
        
        return groups
    
    def _detect_circular_dependencies(self, important_files: List[Dict[str, Any]], 
                                    dependency_graph: Dict[str, List]) -> List[Dict[str, Any]]:
        """
        Detectar dependencias circulares entre archivos importantes.
        
        Args:
            important_files: Lista de archivos importantes
            dependency_graph: Grafo de dependencias
            
        Returns:
            Lista de grupos con dependencias circulares
        """
        circular_groups = []
        visited = set()
        
        for file_info in important_files:
            file_path = file_info['path']
            if file_path in visited:
                continue
                
            # Buscar ciclos desde este archivo
            cycle = self._find_cycle(file_path, dependency_graph, set(), [])
            
            if cycle and len(cycle) > 1:
                # Verificar que los archivos en el ciclo son importantes
                important_cycle_files = [
                    f for f in important_files 
                    if f['path'] in cycle
                ]
                
                if len(important_cycle_files) >= 2:
                    circular_groups.append({
                        'name': f"Circular Dependencies: {' → '.join(cycle[:3])}{'...' if len(cycle) > 3 else ''}",
                        'type': 'circular',
                        'files': important_cycle_files,
                        'cycle_path': cycle,
                        'size': len(important_cycle_files),
                        'total_importance': sum(f['importance_score'] for f in important_cycle_files)
                    })
                    
                    # Marcar archivos como visitados
                    visited.update(cycle)
        
        return circular_groups
    
    def _find_cycle(self, start: str, graph: Dict[str, List], 
                   visited: Set[str], path: List[str]) -> Optional[List[str]]:
        """
        Encontrar un ciclo en el grafo de dependencias.
        
        Args:
            start: Nodo de inicio
            graph: Grafo de dependencias
            visited: Nodos visitados
            path: Ruta actual
            
        Returns:
            Lista representando el ciclo, o None si no hay ciclo
        """
        if start in visited:
            # Encontramos un ciclo
            cycle_start = path.index(start) if start in path else 0
            return path[cycle_start:] + [start]
        
        if start not in graph:
            return None
        
        visited.add(start)
        path.append(start)
        
        for neighbor in graph[start]:
            cycle = self._find_cycle(neighbor, graph, visited.copy(), path.copy())
            if cycle:
                return cycle
        
        return None
    
    def _calculate_metrics(self, dependency_graph: Dict[str, List], 
                         important_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcular métricas del proyecto.
        
        Args:
            dependency_graph: Grafo de dependencias
            important_files: Lista de archivos importantes
            
        Returns:
            Diccionario con métricas calculadas
        """
        total_files = len(dependency_graph)
        total_dependencies = sum(len(deps) for deps in dependency_graph.values())
        
        if total_files == 0:
            return {'total_files': 0, 'complexity': 'low'}
        
        avg_dependencies = total_dependencies / total_files
        important_files_ratio = len(important_files) / total_files
        
        # Determinar complejidad
        complexity = 'low'
        if avg_dependencies > 5 or important_files_ratio > 0.3:
            complexity = 'high'
        elif avg_dependencies > 2 or important_files_ratio > 0.15:
            complexity = 'medium'
        
        return {
            'total_files': total_files,
            'total_dependencies': total_dependencies,
            'average_dependencies': round(avg_dependencies, 2),
            'important_files_count': len(important_files),
            'important_files_ratio': round(important_files_ratio, 3),
            'complexity': complexity
        }
    
    def _fallback_analysis(self, project_path: str) -> Dict[str, Any]:
        """
        Análisis de respaldo cuando Madge no está disponible.
        
        Args:
            project_path: Ruta al proyecto
            
        Returns:
            Diccionario con análisis básico
        """
        logger.info("Usando análisis de respaldo sin Madge")
        
        # Análisis básico de archivos
        important_files = []
        file_types = defaultdict(int)
        
        for root, dirs, files in os.walk(project_path):
            # Excluir directorios irrelevantes
            dirs[:] = [d for d in dirs if d not in [
                'node_modules', '.git', '__pycache__', '.pytest_cache',
                'dist', 'build', '.venv', 'venv'
            ]]
            
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, project_path)
                
                file_extension = Path(file_path).suffix
                file_type = self._determine_file_type(file_extension, relative_path)
                file_types[file_type] += 1
                
                # Considerar archivos importantes basándose en tamaño y tipo
                try:
                    file_size = os.path.getsize(file_path)
                    if (file_size > 1000 and file_extension in ['.py', '.js', '.ts', '.java']) or \
                       any(keyword in relative_path.lower() for keyword in ['main', 'app', 'index', 'core']):
                        
                        important_files.append({
                            'path': relative_path,
                            'full_path': file_path,
                            'dependencies_out': 0,  # No podemos calcular sin Madge
                            'dependencies_in': 0,
                            'importance_score': file_size // 1000,  # Usar tamaño como proxy
                            'file_info': {
                                'size': file_size,
                                'extension': file_extension,
                                'type': file_type,
                                'directory': os.path.dirname(relative_path)
                            }
                        })
                except OSError:
                    continue
        
        # Limitar archivos importantes
        important_files.sort(key=lambda x: x['importance_score'], reverse=True)
        important_files = important_files[:self.max_files_to_analyze]
        
        return {
            'dependency_graph': {},
            'important_files': important_files,
            'functionality_groups': [],
            'metrics': {
                'total_files': sum(file_types.values()),
                'complexity': 'unknown',
                'file_types': dict(file_types)
            },
            'analysis_type': 'fallback'
        }
    
    def _python_optimized_analysis(self, project_path: str) -> Dict[str, Any]:
        """
        Análisis optimizado específico para proyectos Python.
        
        Args:
            project_path: Ruta al proyecto Python
            
        Returns:
            Diccionario con análisis optimizado para Python
        """
        logger.info("Ejecutando análisis optimizado para Python")
        
        # Encontrar archivos Python importantes
        python_files = []
        import_graph = defaultdict(list)
        
        for root, dirs, files in os.walk(project_path):
            # Excluir directorios irrelevantes
            dirs[:] = [d for d in dirs if d not in [
                'node_modules', '.git', '__pycache__', '.pytest_cache',
                'dist', 'build', '.venv', 'venv', '.env'
            ]]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, project_path)
                    
                    try:
                        # Analizar importaciones Python
                        imports = self._analyze_python_imports(file_path)
                        if imports:
                            import_graph[relative_path] = imports
                            
                        # Obtener información del archivo
                        file_size = os.path.getsize(file_path)
                        python_files.append({
                            'path': relative_path,
                            'full_path': file_path,
                            'size': file_size,
                            'imports': len(imports),
                            'importance_score': len(imports) + (file_size // 1000)
                        })
                    except Exception as e:
                        logger.debug(f"Error analizando {file_path}: {e}")
                        continue
        
        # Procesar resultados como si fueran de Madge
        madge_style_data = {}
        for file_info in python_files:
            madge_style_data[file_info['path']] = import_graph.get(file_info['path'], [])
        
        return self._process_madge_output(madge_style_data, project_path)
    
    def _analyze_python_imports(self, file_path: str) -> List[str]:
        """
        Analizar importaciones de un archivo Python.
        
        Args:
            file_path: Ruta al archivo Python
            
        Returns:
            Lista de módulos importados
        """
        imports = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar importaciones usando regex simple
            import re
            
            # from module import ...
            from_imports = re.findall(r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import', content)
            imports.extend(from_imports)
            
            # import module
            direct_imports = re.findall(r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)', content)
            imports.extend(direct_imports)
            
            # Filtrar solo importaciones locales (relativas al proyecto)
            local_imports = []
            for imp in imports:
                # Si empieza con punto o no contiene punto, probablemente es local
                if imp.startswith('.') or ('.' not in imp and not imp in ['os', 'sys', 'json', 'time', 'datetime', 're']):
                    local_imports.append(imp)
            
            return list(set(local_imports))  # Eliminar duplicados
            
        except Exception as e:
            logger.debug(f"Error leyendo {file_path}: {e}")
            return []
