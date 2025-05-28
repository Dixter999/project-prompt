#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Analizador de conexiones entre archivos.

Este módulo se encarga de detectar las conexiones entre archivos
a través de importaciones, referencias y dependencias.
"""

import os
import re
from typing import Dict, List, Set, Tuple, Any, Optional
import ast
from collections import defaultdict
import json

from src.utils.logger import get_logger
from src.analyzers.file_analyzer import FileAnalyzer, get_file_analyzer

logger = get_logger()


class ConnectionAnalyzer:
    """
    Analizador de conexiones entre archivos en un proyecto.
    
    Esta clase detecta las importaciones y referencias entre
    archivos para construir un mapa de dependencias.
    """
    
    def __init__(self):
        """Inicializar el analizador de conexiones."""
        self.file_analyzer = get_file_analyzer()
        
        # Patrones de exclusión de archivos no relevantes
        self.excluded_extensions = {
            # Archivos de imagen
            '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', '.webp', '.bmp', '.tif', '.tiff',
            # Archivos de video
            '.mp4', '.webm', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.m4v',
            # Archivos de audio
            '.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a',
            # Archivos de documentos
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            # Archivos binarios y compilados
            '.exe', '.dll', '.so', '.dylib', '.class', '.pyc', '.pyd',
            # Archivos de recursos
            '.ttf', '.woff', '.woff2', '.eot', '.otf',
            # Archivos de datos
            '.csv', '.json', '.xml', '.yaml', '.yml', '.toml', 
            # Excepciones para JSON/XML/YAML de configuración que serán analizados selectivamente
        }
        
        # Patrones de nombres de archivos/directorios a excluir
        self.excluded_patterns = [
            # Directorios comunes de dependencias y generados
            r'^node_modules/', r'^venv/', r'^__pycache__/', r'^\.git/',
            r'^\.svn/', r'^\.idea/', r'^\.vscode/', r'^dist/', r'^build/',
            # Archivos específicos
            r'package-lock\.json$', r'yarn\.lock$', r'\.DS_Store$',
            # Archivos generados o temporales
            r'.*\.min\.js$', r'.*\.min\.css$', r'.*\.map$',
            # Archivos de respaldo o temporales
            r'.*~$', r'.*\.bak$', r'.*\.swp$', r'.*\.tmp$'
        ]
        
        # Reglas especiales para HTML puramente presentacional
        self.html_content_patterns = {
            'presentational': [
                # Patrones que indican HTML puramente presentacional
                r'<!DOCTYPE\s+html>', 
                r'<html[^>]*>\s*<head[^>]*>', 
                r'<meta[^>]*>', 
                r'<link[^>]*rel=["\']stylesheet["\']'
            ],
            'functional': [
                # Patrones que indican HTML con lógica o funcionalidad
                r'<script[^>]*src=', 
                r'<script[^>]*>\s*.+?\s*</script>', 
                r'(?:ng|v)[-:](?:if|for|model|bind|on)', 
                r'data-[\w\-]+='
            ]
        }
        
        self.import_patterns = {
            # Patrones para diferentes lenguajes
            'python': [
                r'^import\s+([\w\.]+)(?:\s+as\s+[\w\.]+)?',
                r'^from\s+([\w\.]+)\s+import\s+(?:[\w\.\*]+)',
                r'^from\s+([\.\w]+)\s+import',
            ],
            'javascript': [
                r'import\s+(?:[\{,\s\w\}]+\s+from\s+)?[\'"`]([\w\.\/\-]+)[\'"`]',
                r'require\(\s*[\'"`]([\w\.\/\-]+)[\'"`]\s*\)',
                r'import\([\'"`]([\w\.\/\-]+)[\'"`]\)',
            ],
            'typescript': [
                r'import\s+(?:[\{,\s\w\}]+\s+from\s+)?[\'"`]([\w\.\/\-]+)[\'"`]',
                r'import\s+\*\s+as\s+[\w\$]+\s+from\s+[\'"`]([\w\.\/\-]+)[\'"`]',
                r'import\([\'"`]([\w\.\/\-]+)[\'"`]\)',
            ],
            'java': [
                r'import\s+([\w\.]+)(?:\.\*)?;',
                r'package\s+([\w\.]+);',
                r'@ImportResource\([\'"](?:classpath:)?([\w\.\/\-]+)[\'"]',
            ],
            'php': [
                r'(?:require|include)(?:_once)?\s*\(?\s*[\'"`]([\w\.\/\-]+)[\'"`]\s*\)?',
                r'use\s+([\\\w]+)(?:\s+as\s+[\w]+)?;',
                r'namespace\s+([\\\w]+);',
            ],
            'ruby': [
                r'require\s+[\'"`]([\w\.\/\-]+)[\'"`]',
                r'require_relative\s+[\'"`]([\w\.\/\-]+)[\'"`]',
                r'load\s+[\'"`]([\w\.\/\-]+)[\'"`]',
            ],
            'cpp': [
                r'#include\s+["<]([\w\.\/\-]+)[">]',
                r'#import\s+["<]([\w\.\/\-]+)[">]',
            ],
            'csharp': [
                r'using\s+([\w\.]+);',
                r'using\s+static\s+([\w\.]+);',
                r'using\s+[\w]+\s*=\s*([\w\.]+);',
            ],
            'html': [
                r'<script\s+(?:[^>]*?)src=["\']([\w\.\/\-]+)["\']',
                r'<link\s+(?:[^>]*?)href=["\']([\w\.\/\-]+)["\']',
                r'<img\s+(?:[^>]*?)src=["\']([\w\.\/\-]+)["\']',
            ],
            'css': [
                r'@import\s+[\'"](?:url\()?([\w\.\/\-]+)[\'"\)]',
                r'url\([\'"]?([\w\.\/\-]+)[\'"]?\)',
            ],
            'go': [
                r'import\s+[\'"`]([\w\.\/\-]+)[\'"`]',
                r'import\s+\((?:\s*[\'"`][\w\.\/\-]+[\'"`]\s*)+\)',
            ],
            'rust': [
                r'use\s+([\w\:]+)(?:\:\:\*|(?:\s+as\s+[\w]+)?)',
                r'extern\s+crate\s+([\w]+);',
            ]
        }
    
    def analyze_connections(self, project_path: str, max_files: int = 5000) -> Dict[str, Any]:
        """
        Analizar las conexiones entre archivos en un proyecto.
        
        Args:
            project_path: Ruta al proyecto
            max_files: Número máximo de archivos a procesar
            
        Returns:
            Diccionario con información de conexiones
        """
        logger.info(f"Analizando conexiones en: {project_path}")
        
        # Recopilación de archivos en el proyecto
        file_connections = {}
        file_imports = {}
        lang_stats = defaultdict(int)
        
        # Obtener todos los archivos del proyecto
        all_files = []
        excluded_count = {'extensions': 0, 'patterns': 0, 'html_presentational': 0}
        included_count = 0
        
        for root, dirs, files in os.walk(project_path):
            # Filtrar directorios según los patrones excluidos
            dirs[:] = [d for d in dirs if not any(re.match(pattern, os.path.join(root, d).replace(project_path + os.path.sep, '')) 
                                              for pattern in self.excluded_patterns)]
            
            for file in files:
                if len(all_files) >= max_files:
                    break
                
                file_path = os.path.join(root, file)
                rel_file_path = os.path.relpath(file_path, project_path)
                
                # Comprobar si debe excluirse por extensión
                _, extension = os.path.splitext(file)
                if extension.lower() in self.excluded_extensions:
                    excluded_count['extensions'] += 1
                    continue
                
                # Comprobar si debe excluirse por patrón de nombre
                if any(re.match(pattern, rel_file_path) for pattern in self.excluded_patterns):
                    excluded_count['patterns'] += 1
                    continue
                
                # Si es un archivo HTML, comprobar si es puramente presentacional
                if extension.lower() in ['.html', '.htm', '.xhtml']:
                    is_functional = self._is_functional_html(file_path)
                    if not is_functional:
                        excluded_count['html_presentational'] += 1
                        continue
                
                all_files.append(file_path)
                included_count += 1
        
        logger.debug(f"Archivos incluidos: {included_count}, excluidos por extensión: {excluded_count['extensions']}, " +
                   f"excluidos por patrón: {excluded_count['patterns']}, " +
                   f"HTML presentacional: {excluded_count['html_presentational']}")
                
        # Analizar importaciones en cada archivo
        for file_path in all_files:
            rel_path = os.path.relpath(file_path, project_path)
            
            try:
                # Detectar lenguaje
                file_info = self.file_analyzer.analyze_file(file_path)
                language = file_info.get('language', 'unknown')
                lang_stats[language] += 1
                
                # Analizar importaciones según el lenguaje
                imports = self._extract_imports(file_path, language)
                
                # Agregar al mapa de importaciones
                file_imports[rel_path] = {
                    'language': language,
                    'imports': imports
                }
                
            except Exception as e:
                logger.debug(f"Error al analizar conexiones en {rel_path}: {e}")
                continue
        
        # Resolver las importaciones a archivos reales
        file_connections = self._resolve_connections(file_imports, project_path)
        
        # Recopilación de información
        result = {
            'project_path': project_path,
            'files_analyzed': len(file_imports),
            'files_excluded': {
                'by_extension': excluded_count['extensions'],
                'by_pattern': excluded_count['patterns'],
                'html_presentational': excluded_count['html_presentational'],
                'total_excluded': sum(excluded_count.values())
            },
            'language_stats': dict(lang_stats),
            'file_imports': file_imports,
            'file_connections': file_connections,
            'connected_components': self._find_connected_components(file_connections),
            'disconnected_files': self._find_disconnected_files(file_connections, file_imports)
        }
        
        logger.info(f"Análisis de conexiones completado: {len(file_connections)} archivos con conexiones")
        return result
    
    def export_connections_json(self, connections_data: Dict[str, Any], output_path: str) -> str:
        """
        Exportar datos de conexiones a formato JSON.
        
        Args:
            connections_data: Datos de conexiones
            output_path: Ruta de salida
            
        Returns:
            Ruta al archivo generado
        """
        try:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(connections_data, f, indent=2)
                
            logger.info(f"Datos de conexiones exportados a: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error al exportar conexiones a JSON: {e}", exc_info=True)
            raise
    
    def _extract_imports(self, file_path: str, language: str) -> List[str]:
        """
        Extraer importaciones de un archivo según su lenguaje.
        
        Args:
            file_path: Ruta al archivo
            language: Lenguaje detectado
            
        Returns:
            Lista de importaciones encontradas
        """
        imports = []
        
        try:
            # Obtener patrones específicos para el lenguaje
            patterns = []
            for lang, lang_patterns in self.import_patterns.items():
                if lang.lower() in language.lower() or language.lower() in lang.lower():
                    patterns.extend(lang_patterns)
            
            # Si no hay patrones específicos, usar patrones genéricos
            if not patterns and language != 'unknown':
                patterns = self.import_patterns.get('python', []) + self.import_patterns.get('javascript', [])
                
            # Si es archivo Python, usar AST para análisis más preciso
            if language.lower() == 'python':
                py_imports = self._extract_python_imports(file_path)
                if py_imports:
                    return py_imports
            
            # Leer el archivo y buscar patrones
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Aplicar cada patrón
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.MULTILINE)
                for match in matches:
                    if match.groups():
                        imports.append(match.group(1))
            
            return imports
                
        except Exception as e:
            logger.debug(f"Error al extraer importaciones de {file_path}: {e}")
            return imports
    
    def _extract_python_imports(self, file_path: str) -> List[str]:
        """
        Extraer importaciones de un archivo Python usando AST.
        
        Args:
            file_path: Ruta al archivo Python
            
        Returns:
            Lista de módulos importados
        """
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                tree = ast.parse(f.read(), filename=file_path)
                
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(name.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                        
            return imports
            
        except Exception as e:
            logger.debug(f"Error al analizar AST en {file_path}: {e}")
            return []
    
    def _resolve_connections(self, file_imports: Dict[str, Dict], 
                           project_path: str) -> Dict[str, List[str]]:
        """
        Resolver las importaciones a archivos reales en el proyecto.
        
        Args:
            file_imports: Mapa de importaciones por archivo
            project_path: Ruta base del proyecto
            
        Returns:
            Diccionario de conexiones entre archivos
        """
        # Mapa de archivos a sus conexiones
        connections = defaultdict(list)
        
        # Mapear módulos a archivos reales
        module_to_file = self._build_module_map(file_imports, project_path)
        
        # Para cada archivo y sus importaciones
        for file_path, file_data in file_imports.items():
            language = file_data['language']
            imports = file_data['imports']
            
            for imp in imports:
                # Intentar resolver la importación a un archivo real
                resolved = self._resolve_import(imp, file_path, language, module_to_file, project_path)
                
                if resolved:
                    # Agregar la conexión si se resolvió
                    connections[file_path].append(resolved)
        
        return dict(connections)
    
    def _build_module_map(self, file_imports: Dict[str, Dict], 
                         project_path: str) -> Dict[str, str]:
        """
        Construir un mapa de nombres de módulos a archivos reales.
        
        Args:
            file_imports: Mapa de importaciones por archivo
            project_path: Ruta base del proyecto
            
        Returns:
            Mapa de módulos a archivos
        """
        module_map = {}
        
        for file_path, file_data in file_imports.items():
            language = file_data.get('language')
            
            # Skip if language is None or not detected
            if not language:
                continue
            
            # Convertir ruta relativa a posible módulo según el lenguaje
            if language.lower() == 'python':
                # En Python, convertir rutas a formato de módulo
                module_path = file_path.replace('/', '.').replace('\\', '.')
                if module_path.endswith('.py'):
                    module_path = module_path[:-3]  # Quitar la extensión .py
                    module_map[module_path] = file_path
                    
                    # También mapear partes del módulo
                    parts = module_path.split('.')
                    for i in range(1, len(parts) + 1):
                        module_prefix = '.'.join(parts[:i])
                        if module_prefix not in module_map:
                            module_map[module_prefix] = os.path.join(project_path, *parts[:i])
            
            elif 'javascript' in language.lower() or 'typescript' in language.lower():
                # En JS/TS, manejar rutas relativas
                path_no_ext = os.path.splitext(file_path)[0]
                module_map[path_no_ext] = file_path
                
                # Mapear variantes de importación
                base_name = os.path.basename(path_no_ext)
                dir_name = os.path.dirname(file_path)
                if dir_name and base_name == 'index':
                    module_map[os.path.dirname(path_no_ext)] = file_path
        
        return module_map
    
    def _resolve_import(self, import_name: str, importer_path: str, 
                       language: str, module_map: Dict[str, str], 
                       project_path: str) -> Optional[str]:
        """
        Resolver una importación a un archivo real.
        
        Args:
            import_name: Nombre de la importación
            importer_path: Ruta del archivo que importa
            language: Lenguaje del archivo
            module_map: Mapa de módulos a archivos
            project_path: Ruta base del proyecto
            
        Returns:
            Ruta relativa al archivo resuelto o None si no se pudo resolver
        """
        # Verificar en el mapa de módulos
        if import_name in module_map:
            return module_map[import_name]
        
        # Manejar según el lenguaje
        if language.lower() == 'python':
            # Probar diferentes extensiones
            for ext in ['.py', '/__init__.py', '.pyc', '.pyd', '.so']:
                candidate = import_name.replace('.', '/') + ext
                full_path = os.path.join(project_path, candidate)
                
                if os.path.exists(full_path):
                    return os.path.relpath(full_path, project_path)
        
        elif 'javascript' in language.lower() or 'typescript' in language.lower():
            # Para importaciones relativas al importador
            base_dir = os.path.dirname(os.path.join(project_path, importer_path))
            
            # Probar diferentes extensiones y convenciones
            for prefix in ['', './', '../']:
                for ext in ['.js', '.jsx', '.ts', '.tsx', '/index.js', '/index.jsx', '/index.ts', '/index.tsx']:
                    candidate = prefix + import_name + ext
                    full_path = os.path.normpath(os.path.join(base_dir, candidate))
                    
                    if os.path.exists(full_path) and project_path in full_path:
                        return os.path.relpath(full_path, project_path)
        
        # No se pudo resolver
        return None
    
    def _find_connected_components(self, connections: Dict[str, List[str]]) -> List[List[str]]:
        """
        Encontrar componentes conectados en el grafo de dependencias.
        
        Args:
            connections: Mapa de conexiones entre archivos
            
        Returns:
            Lista de componentes conectados (cada uno es una lista de archivos)
        """
        # Construir grafo no dirigido de conexiones
        graph = defaultdict(set)
        for src, dests in connections.items():
            for dest in dests:
                graph[src].add(dest)
                graph[dest].add(src)
        
        # Buscar componentes conectados con DFS
        components = []
        visited = set()
        
        def dfs(node, component):
            visited.add(node)
            component.append(node)
            
            for neighbor in graph[node]:
                if neighbor not in visited:
                    dfs(neighbor, component)
        
        # Recorrer cada nodo no visitado como posible nuevo componente
        for node in graph:
            if node not in visited:
                component = []
                dfs(node, component)
                components.append(component)
        
        # Ordenar componentes por tamaño
        return sorted(components, key=len, reverse=True)
    
    def _find_disconnected_files(self, connections: Dict[str, List[str]], 
                                file_imports: Dict[str, Dict]) -> List[str]:
        """
        Identificar archivos que no tienen conexiones con otros.
        
        Args:
            connections: Mapa de conexiones entre archivos
            file_imports: Información de importaciones por archivo
            
        Returns:
            Lista de archivos desconectados
        """
        # Obtener todos los archivos analizados
        all_files = set(file_imports.keys())
        
        # Obtener archivos conectados (como origen o destino)
        connected_files = set()
        for src, dests in connections.items():
            connected_files.add(src)
            connected_files.update(dests)
        
        # Encontrar archivos que no están en el conjunto conectado
        return list(all_files - connected_files)
    
    def _is_functional_html(self, file_path: str) -> bool:
        """
        Determina si un archivo HTML contiene lógica o es puramente presentacional.
        
        Args:
            file_path: Ruta al archivo HTML
            
        Returns:
            True si el HTML contiene lógica o funcionalidad, False si es puramente presentacional
        """
        try:
            # Leer el contenido del archivo
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Verificar si contiene elementos funcionales
            for pattern in self.html_content_patterns['functional']:
                if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                    # Contiene scripts, frameworks o elementos interactivos
                    return True
            
            # Si no contiene elementos funcionales pero tiene estructura básica, es presentacional
            presentational_matches = 0
            for pattern in self.html_content_patterns['presentational']:
                if re.search(pattern, content, re.IGNORECASE):
                    presentational_matches += 1
            
            # Si tiene varios elementos presentacionales pero ninguno funcional, es presentacional
            if presentational_matches >= 2:
                return False
            
            # Por defecto, incluimos archivos HTML a menos que estemos seguros de que son presentacionales
            return True
            
        except Exception as e:
            logger.debug(f"Error al analizar HTML {file_path}: {e}")
            # En caso de error, asumimos que es funcional para no perder conexiones potenciales
            return True


def get_connection_analyzer() -> ConnectionAnalyzer:
    """
    Obtener una instancia del analizador de conexiones.
    
    Returns:
        Instancia del analizador
    """
    return ConnectionAnalyzer()
