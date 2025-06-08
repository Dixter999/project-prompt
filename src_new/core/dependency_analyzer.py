#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Analizador unificado de dependencias.

Parte de la Fase 3: Corrección de Problemas Críticos
Resuelve: Problema 2 - Múltiples analizadores conflictivos de dependencias
Consolida: dependency_graph.py, madge_analyzer.py, smart_dependency_analyzer.py, connection_analyzer.py
"""

import networkx as nx
from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path
import ast
import re
import logging

logger = logging.getLogger(__name__)


class UnifiedDependencyAnalyzer:
    """
    Analizador unificado que combina lo mejor de cada implementación:
    - Detección de imports (de dependency_graph.py)
    - Análisis de llamadas (de connection_analyzer.py) 
    - Detección de circular deps (de smart_dependency_analyzer.py)
    """
    
    def __init__(self):
        """Initialize the unified dependency analyzer."""
        self.graph = nx.DiGraph()
        self.file_imports = {}
        self.circular_deps = []
        self.logger = logger
    
    def analyze_dependencies(self, files: List[str]) -> Dict:
        """
        Análisis completo de dependencias.
        
        Args:
            files: Lista de rutas de archivos a analizar
            
        Returns:
            Diccionario con análisis completo:
            - graph: NetworkX DiGraph con dependencias
            - circular_dependencies: Lista de ciclos detectados
            - importance_scores: Scores de importancia por archivo
            - total_connections: Número total de conexiones
        """
        self.logger.info(f"Starting dependency analysis for {len(files)} files")
        
        # 1. Construir grafo de dependencias
        self.graph = self._build_dependency_graph(files)
        
        # 2. Detectar dependencias circulares
        self.circular_deps = self._detect_circular_dependencies()
        
        # 3. Calcular métricas de importancia
        importance_scores = self._calculate_importance_scores()
        
        result = {
            'graph': self.graph,
            'circular_dependencies': self.circular_deps,
            'importance_scores': importance_scores,
            'total_connections': self.graph.number_of_edges(),
            'total_nodes': self.graph.number_of_nodes()
        }
        
        self.logger.info(f"✅ Dependency analysis complete: {result['total_connections']} connections, {result['total_nodes']} nodes")
        
        return result
    
    def _build_dependency_graph(self, files: List[str]) -> nx.DiGraph:
        """
        Construye grafo de dependencias sin conflictos.
        
        Args:
            files: Lista de archivos a analizar
            
        Returns:
            NetworkX DiGraph con las dependencias
        """
        graph = nx.DiGraph()
        
        # Crear mapeo de archivos para resolución de imports
        file_mapping = self._create_file_mapping(files)
        
        for file_path in files:
            try:
                if self._is_python_file(file_path):
                    imports = self._extract_python_imports(file_path)
                    self._add_imports_to_graph(graph, file_path, imports, file_mapping)
                elif self._is_javascript_file(file_path):
                    imports = self._extract_js_imports(file_path)
                    self._add_imports_to_graph(graph, file_path, imports, file_mapping)
                elif self._is_typescript_file(file_path):
                    imports = self._extract_ts_imports(file_path)
                    self._add_imports_to_graph(graph, file_path, imports, file_mapping)
                    
                # Añadir nodo aunque no tenga dependencias
                if file_path not in graph:
                    graph.add_node(file_path)
                    
            except Exception as e:
                self.logger.error(f"Error processing file {file_path}: {e}")
                # Añadir nodo aunque haya error
                if file_path not in graph:
                    graph.add_node(file_path)
        
        return graph
    
    def _create_file_mapping(self, files: List[str]) -> Dict[str, str]:
        """
        Crea mapeo de nombres de módulos a rutas de archivo.
        
        Args:
            files: Lista de archivos
            
        Returns:
            Diccionario módulo -> ruta
        """
        mapping = {}
        
        for file_path in files:
            # Mapear por nombre de archivo
            file_name = Path(file_path).stem
            mapping[file_name] = file_path
            
            # Mapear por ruta relativa
            if '/' in file_path:
                module_name = file_path.replace('/', '.').replace('.py', '')
                mapping[module_name] = file_path
        
        return mapping
    
    def _extract_python_imports(self, file_path: str) -> Set[str]:
        """
        Extrae imports de archivo Python usando AST.
        
        Args:
            file_path: Ruta del archivo Python
            
        Returns:
            Set de nombres de módulos importados
        """
        imports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
                        # También añadir imports relativos
                        if node.level > 0:
                            imports.add('.' + node.module if node.module else '.')
                        
        except Exception as e:
            self.logger.warning(f"Error parsing Python file {file_path}: {e}")
        
        return imports
    
    def _extract_js_imports(self, file_path: str) -> Set[str]:
        """
        Extrae imports de archivo JavaScript.
        
        Args:
            file_path: Ruta del archivo JavaScript
            
        Returns:
            Set de módulos importados
        """
        imports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Regex para import statements
            import_patterns = [
                r"import.*from\s+['\"]([^'\"]+)['\"]",  # import ... from '...'
                r"require\(['\"]([^'\"]+)['\"]\)",      # require('...')
                r"import\(['\"]([^'\"]+)['\"]\)"        # import('...')
            ]
            
            for pattern in import_patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                imports.update(matches)
                
        except Exception as e:
            self.logger.warning(f"Error parsing JavaScript file {file_path}: {e}")
        
        return imports
    
    def _extract_ts_imports(self, file_path: str) -> Set[str]:
        """
        Extrae imports de archivo TypeScript.
        
        Args:
            file_path: Ruta del archivo TypeScript
            
        Returns:
            Set de módulos importados
        """
        # TypeScript usa misma sintaxis que JavaScript para imports
        return self._extract_js_imports(file_path)
    
    def _add_imports_to_graph(self, graph: nx.DiGraph, file_path: str, imports: Set[str], file_mapping: Dict[str, str]):
        """
        Añade imports al grafo de dependencias.
        
        Args:
            graph: Grafo de dependencias
            file_path: Archivo fuente
            imports: Set de imports detectados
            file_mapping: Mapeo de módulos a archivos
        """
        # Añadir nodo fuente
        graph.add_node(file_path)
        
        for import_name in imports:
            # Buscar archivo correspondiente al import
            target_file = self._resolve_import(import_name, file_path, file_mapping)
            
            if target_file and target_file != file_path:
                graph.add_edge(file_path, target_file)
                self.logger.debug(f"Added dependency: {file_path} -> {target_file}")
    
    def _resolve_import(self, import_name: str, source_file: str, file_mapping: Dict[str, str]) -> Optional[str]:
        """
        Resuelve un import a su archivo correspondiente.
        
        Args:
            import_name: Nombre del import
            source_file: Archivo fuente del import
            file_mapping: Mapeo de módulos a archivos
            
        Returns:
            Ruta del archivo objetivo o None
        """
        # Búsqueda directa
        if import_name in file_mapping:
            return file_mapping[import_name]
        
        # Buscar por nombre parcial
        for module_name, file_path in file_mapping.items():
            if import_name in module_name or module_name in import_name:
                return file_path
        
        # Buscar archivos relativos
        if import_name.startswith('.'):
            source_dir = Path(source_file).parent
            relative_path = source_dir / (import_name.lstrip('.') + '.py')
            if relative_path.exists():
                return str(relative_path)
        
        return None
    
    def _detect_circular_dependencies(self) -> List[List[str]]:
        """
        Detecta dependencias circulares.
        
        Returns:
            Lista de ciclos detectados
        """
        try:
            cycles = list(nx.simple_cycles(self.graph))
            # Filtrar ciclos triviales (self-loops)
            meaningful_cycles = [list(cycle) for cycle in cycles if len(cycle) > 1]
            
            if meaningful_cycles:
                self.logger.warning(f"⚠️  Detected {len(meaningful_cycles)} circular dependencies")
            
            return meaningful_cycles
        except Exception as e:
            self.logger.error(f"Error detecting circular dependencies: {e}")
            return []
    
    def _calculate_importance_scores(self) -> Dict[str, float]:
        """
        Calcula scores de importancia basado en conexiones.
        
        Returns:
            Diccionario archivo -> score de importancia
        """
        if self.graph.number_of_nodes() == 0:
            return {}
        
        try:
            # PageRank para importancia
            pagerank = nx.pagerank(self.graph)
            
            # Normalizar scores
            max_score = max(pagerank.values()) if pagerank else 1
            normalized_scores = {
                node: score / max_score for node, score in pagerank.items()
            }
            
            return normalized_scores
            
        except Exception as e:
            self.logger.error(f"Error calculating importance scores: {e}")
            # Fallback: degree centrality
            try:
                return nx.degree_centrality(self.graph)
            except:
                return {}
    
    def _is_python_file(self, file_path: str) -> bool:
        """Verifica si es archivo Python."""
        return file_path.endswith('.py')
    
    def _is_javascript_file(self, file_path: str) -> bool:
        """Verifica si es archivo JavaScript."""
        return file_path.endswith(('.js', '.jsx'))
    
    def _is_typescript_file(self, file_path: str) -> bool:
        """Verifica si es archivo TypeScript."""
        return file_path.endswith(('.ts', '.tsx'))
    
    def get_dependency_summary(self) -> Dict:
        """
        Genera resumen del análisis de dependencias.
        
        Returns:
            Resumen con estadísticas clave
        """
        return {
            'total_files': self.graph.number_of_nodes(),
            'total_dependencies': self.graph.number_of_edges(),
            'circular_dependencies_count': len(self.circular_deps),
            'isolated_files': len([n for n in self.graph.nodes() if self.graph.degree(n) == 0]),
            'highly_connected_files': len([n for n in self.graph.nodes() if self.graph.degree(n) > 5])
        }
