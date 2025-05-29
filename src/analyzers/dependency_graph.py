#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generador de grafo de dependencias entre archivos.

Este módulo se encarga de generar un grafo de dependencias
entre archivos y proporciona funcionalidades para visualizarlo
en diferentes formatos.
"""

import os
import re
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict
import json
import textwrap

from src.utils.logger import get_logger
from src.analyzers.analysis_cache import get_analysis_cache

logger = get_logger()


class DependencyGraph:
    """
    Generador de grafo de dependencias entre archivos.
    
    Esta clase genera un grafo de dependencias a partir
    de los datos del analizador de conexiones y permite
    visualizarlo de diferentes formas.
    """
    
    def __init__(self):
        """Inicializar el generador de grafo de dependencias."""
        # Import dinamically to avoid circular imports
        from src.analyzers.connection_analyzer import get_connection_analyzer
        from src.analyzers.madge_analyzer import MadgeAnalyzer
        
        self.connection_analyzer = get_connection_analyzer()
        self.madge_analyzer = MadgeAnalyzer()
        self.cache = get_analysis_cache()
    
    def build_dependency_graph(self, project_path: str, max_files: int = 5000, 
                              use_madge: bool = True) -> Dict[str, Any]:
        """
        Construir un grafo de dependencias para un proyecto.
        
        Args:
            project_path: Ruta al proyecto
            max_files: Número máximo de archivos a analizar
            use_madge: Si usar Madge para análisis eficiente
            
        Returns:
            Diccionario con datos del grafo
        """
        logger.info(f"🔍 Iniciando análisis de dependencias: {os.path.basename(project_path)}")
        
        # Verificar caché primero
        cache_config = {'max_files': max_files, 'use_madge': use_madge}
        cached_result = self.cache.get(project_path, 'dependencies', cache_config)
        if cached_result:
            logger.info(f"✅ Usando análisis en caché para {os.path.basename(project_path)}")
            return cached_result
        
        # Intentar usar Madge primero para eficiencia
        if use_madge:
            logger.info("🔄 Ejecutando análisis con Madge...")
            madge_result = self.madge_analyzer.get_dependency_graph(project_path)
            
            if madge_result['analysis_type'] == 'madge':
                logger.info("✅ Análisis Madge exitoso - procesando resultados optimizados")
                result = self._enhance_madge_results(madge_result, project_path, max_files)
                # Almacenar en caché
                self.cache.set(project_path, 'dependencies', result, cache_config)
                return result
            else:
                logger.info("⚠️  Madge no disponible - usando análisis tradicional")
        
        # Análisis tradicional usando ConnectionAnalyzer
        logger.info("🔄 Ejecutando análisis tradicional de conexiones...")
        connections = self.connection_analyzer.analyze_connections(project_path, max_files)
        
        # Obtener estadísticas de gitignore usando ProjectScanner
        from src.analyzers.project_scanner import get_project_scanner
        scanner = get_project_scanner(max_files=max_files)
        
        # Realizar un escaneo rápido solo para obtener estadísticas de gitignore
        try:
            logger.info("📊 Obteniendo estadísticas de archivos excluidos por .gitignore...")
            scan_result = scanner.scan_project(project_path)
            gitignore_stats = scan_result.get('stats', {}).get('gitignore_excluded', 0)
            if gitignore_stats > 0:
                logger.info(f"📋 {gitignore_stats} archivos excluidos por .gitignore")
        except Exception as e:
            logger.warning(f"No se pudieron obtener estadísticas de gitignore: {e}")
            gitignore_stats = 0
        
        # Agregar estadísticas de gitignore a files_excluded
        if 'files_excluded' not in connections:
            connections['files_excluded'] = {}
        connections['files_excluded']['by_gitignore'] = gitignore_stats
        
        # Recalcular total_excluded
        excluded = connections['files_excluded']
        total_excluded = (excluded.get('by_extension', 0) + 
                         excluded.get('by_pattern', 0) + 
                         excluded.get('html_presentational', 0) + 
                         excluded.get('by_gitignore', 0))
        connections['files_excluded']['total_excluded'] = total_excluded
        
        # Construir grafo dirigido
        graph = self._build_directed_graph(connections['file_connections'])
        
        # Calcular métricas del grafo
        metrics = self._calculate_graph_metrics(graph, connections['file_imports'])
        
        # Detectar grupos de funcionalidad 
        logger.info("🔍 Detectando grupos de funcionalidad...")
        functionality_groups = self._detect_functionality_groups(connections['file_imports'], graph)
        
        # Estructura final del grafo de dependencias
        dependency_graph = {
            'project_path': project_path,
            'nodes': self._build_nodes_data(connections['file_imports']),
            'edges': self._build_edges_data(connections['file_connections']),
            'metrics': metrics,
            'connected_components': connections['connected_components'],
            'disconnected_files': connections['disconnected_files'],
            'central_files': self._identify_central_files(graph),
            'important_files': self._identify_important_files(connections['file_imports'], graph),
            'functionality_groups': functionality_groups,
            'language_stats': connections['language_stats'],
            'file_cycles': self._detect_cycles(graph),
            'files_excluded': connections.get('files_excluded', {})
        }
        
        logger.info(f"✅ Grafo de dependencias construido: {len(dependency_graph['nodes'])} nodos, {len(dependency_graph['edges'])} enlaces, {len(functionality_groups)} grupos funcionales")
        
        # Almacenar en caché
        self.cache.set(project_path, 'dependencies', dependency_graph, cache_config)
        
        return dependency_graph
    
    def export_graph_json(self, graph_data: Dict[str, Any], output_path: str) -> str:
        """
        Exportar grafo a formato JSON.
        
        Args:
            graph_data: Datos del grafo
            output_path: Ruta de salida
            
        Returns:
            Ruta al archivo generado
        """
        try:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, indent=2)
                
            logger.info(f"Grafo de dependencias exportado a: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error al exportar grafo a JSON: {e}", exc_info=True)
            raise
    
    def generate_markdown_visualization(self, graph_data: Dict[str, Any]) -> str:
        """
        Generar representación del grafo en formato markdown.
        
        Args:
            graph_data: Datos del grafo
            
        Returns:
            Texto en formato markdown
        """
        try:
            markdown = []
            
            # Encabezado
            markdown.append("# Grafo de Dependencias del Proyecto")
            markdown.append(f"\nProyecto: {os.path.basename(graph_data['project_path'])}")
            markdown.append(f"Ruta: {graph_data['project_path']}")
            markdown.append(f"Total de archivos analizados: {len(graph_data['nodes'])}")
            
            # Información sobre archivos excluidos
            if 'files_excluded' in graph_data:
                excluded = graph_data['files_excluded']
                total_excluded = excluded.get('total_excluded', 0)
                gitignore_excluded = excluded.get('by_gitignore', 0)
                
                markdown.append(f"Total de archivos excluidos: {total_excluded}")
                markdown.append("\n## 📋 Archivos Excluidos por .gitignore")
                
                if gitignore_excluded > 0:
                    markdown.append(f"✅ **{gitignore_excluded} archivos excluidos** por las reglas de .gitignore")
                    markdown.append("Esto ayuda a mantener el análisis enfocado en el código fuente relevante.")
                else:
                    markdown.append("ℹ️  No se encontraron archivos excluidos por .gitignore o no existe archivo .gitignore")
                
                markdown.append("\n### Desglose de Exclusiones")
                markdown.append("| Tipo de exclusión | Cantidad |")
                markdown.append("|---|---|")
                markdown.append(f"| Por extensión (multimedia, binarios, etc.) | {excluded.get('by_extension', 0)} |")
                markdown.append(f"| Por patrón (directorios/archivos no relevantes) | {excluded.get('by_pattern', 0)} |")
                markdown.append(f"| HTML puramente presentacional | {excluded.get('html_presentational', 0)} |")
                if gitignore_excluded > 0:
                    markdown.append(f"| **Por .gitignore** | **{gitignore_excluded}** |")
            
            # Métricas
            markdown.append("\n## Métricas del Grafo")
            markdown.append("| Métrica | Valor |")
            markdown.append("|---|---|")
            for metric, value in graph_data['metrics'].items():
                if isinstance(value, float):
                    markdown.append(f"| {metric.replace('_', ' ').title()} | {value:.2f} |")
                else:
                    markdown.append(f"| {metric.replace('_', ' ').title()} | {value} |")
            
            # Estadísticas por lenguaje
            markdown.append("\n## Lenguajes Detectados")
            markdown.append("| Lenguaje | Archivos |")
            markdown.append("|---|---|")
            for lang, count in graph_data['language_stats'].items():
                markdown.append(f"| {lang} | {count} |")
            
            # Componentes conectados
            markdown.append("\n## Componentes Conectados")
            markdown.append(f"Se detectaron {len(graph_data['connected_components'])} componentes conectados.")
            
            if graph_data['connected_components']:
                markdown.append("\n### Componentes Principales")
                # Mostrar solo los 3 componentes más grandes
                for i, component in enumerate(graph_data['connected_components'][:3], 1):
                    markdown.append(f"\n#### Componente {i} ({len(component)} archivos)")
                    # Mostrar ejemplo de 5 archivos
                    for file in component[:5]:
                        markdown.append(f"- `{file}`")
                    if len(component) > 5:
                        markdown.append(f"- ... {len(component) - 5} archivos más")
            
            # Archivos centrales
            markdown.append("\n## Archivos Centrales")
            markdown.append("Archivos con mayor número de dependencias (entrada/salida):")
            
            for file_info in graph_data['central_files'][:10]:  # Top 10
                # Compatibilidad con diferentes estructuras de datos
                file_path = file_info.get('file', file_info.get('path', 'unknown'))
                in_degree = file_info.get('in_degree', file_info.get('dependencies_in', 0))
                out_degree = file_info.get('out_degree', file_info.get('dependencies_out', 0))
                total = file_info.get('total', file_info.get('importance_score', in_degree + out_degree))
                markdown.append(f"- `{file_path}`: {total} conexiones ({in_degree} entrantes, {out_degree} salientes)")
            
            # Archivos desconectados
            if graph_data['disconnected_files']:
                markdown.append("\n## Archivos Desconectados")
                markdown.append(f"Se detectaron {len(graph_data['disconnected_files'])} archivos sin conexiones:")
                
                # Mostrar ejemplo de hasta 10 archivos desconectados
                for file in graph_data['disconnected_files'][:10]:
                    markdown.append(f"- `{file}`")
                if len(graph_data['disconnected_files']) > 10:
                    markdown.append(f"- ... {len(graph_data['disconnected_files']) - 10} archivos más")
            
            # Ciclos detectados
            if graph_data['file_cycles']:
                markdown.append("\n## Ciclos de Dependencias")
                markdown.append(f"Se detectaron {len(graph_data['file_cycles'])} ciclos en las dependencias:")
                
                # Mostrar hasta 5 ciclos
                for i, cycle in enumerate(graph_data['file_cycles'][:5], 1):
                    cycle_str = " → ".join([f"`{f}`" for f in cycle])
                    markdown.append(f"{i}. {cycle_str} → ... (ciclo)")
                
                if len(graph_data['file_cycles']) > 5:
                    markdown.append(f"... y {len(graph_data['file_cycles']) - 5} ciclos más.")
            
            # Grupos funcionales detectados
            if 'functionality_groups' in graph_data and graph_data['functionality_groups']:
                markdown.append("\n## 📊 Grupos Funcionales Detectados")
                markdown.append("Los siguientes grupos funcionales fueron identificados en el proyecto:")
                
                for i, group in enumerate(graph_data['functionality_groups'], 1):
                    markdown.append(f"\n### {i}. {group['name']}")
                    markdown.append(f"**Tipo:** {group.get('type', 'Unknown')}")
                    markdown.append(f"**Archivos:** {group.get('size', len(group.get('files', [])))}") 
                    
                    # Fix f-string syntax issue by extracting fallback description
                    default_desc = f"Grupo funcional: {group['name']}"
                    description = group.get('description', default_desc)
                    markdown.append(f"**Descripción:** {description}")
                    
                    # Mostrar archivos en el grupo (máximo 8)
                    markdown.append("\n**Archivos en el grupo:**")
                    files_to_show = group['files'][:8]
                    for file_info in files_to_show:
                        file_path = file_info.get('path', file_info.get('file', 'unknown'))
                        importance = file_info.get('importance_score', 0)
                        markdown.append(f"- `{file_path}` (importancia: {importance:.2f})")
                    
                    if len(group['files']) > 8:
                        markdown.append(f"- ... y {len(group['files']) - 8} archivos más")
                    
                    # Grafo textual del grupo si hay conexiones
                    markdown.append(f"\n**Grafo del grupo {group['name']}:**")
                    markdown.append("```")
                    group_graph = self._generate_group_text_visualization(group)
                    markdown.append(group_graph)
                    markdown.append("```")

            # Representación textual del grafo
            markdown.append("\n## Representación Textual del Grafo")
            markdown.append("```")
            markdown.append(self._generate_text_visualization(graph_data, max_nodes=20))
            markdown.append("```")
            
            return "\n".join(markdown)
            
        except Exception as e:
            logger.error(f"Error al generar visualización markdown: {e}", exc_info=True)
            return f"Error al generar visualización: {str(e)}"
    
    def generate_dependency_matrix(self, graph_data: Dict[str, Any], max_files: int = 10) -> str:
        """
        Generar una tabla matriz de dependencias.
        
        Args:
            graph_data: Datos del grafo
            max_files: Número máximo de archivos a incluir en la matriz
            
        Returns:
            Representación en markdown de la matriz de dependencias
        """
        important_files = graph_data.get('important_files', [])[:max_files]
        
        if len(important_files) < 2:
            return "### 📊 Matriz de Dependencias\n\n*No hay suficientes archivos para mostrar matriz.*\n\n"
        
        # Obtener rutas de archivos
        file_paths = []
        file_names = []
        
        for file_info in important_files:
            if isinstance(file_info, dict):
                file_path = file_info.get('path', file_info.get('file', ''))
            else:
                file_path = str(file_info)
            
            file_paths.append(file_path)
            # Usar solo el nombre del archivo para la tabla
            file_names.append(os.path.basename(file_path))
        
        # Crear matriz de dependencias
        edges = graph_data.get('edges', [])
        dependency_matrix = {}
        
        for file_path in file_paths:
            dependency_matrix[file_path] = set()
        
        # Llenar matriz con conexiones
        for edge in edges:
            source = edge.get('source', '')
            target = edge.get('target', '')
            
            if source in file_paths and target in file_paths:
                dependency_matrix[source].add(target)
        
        # Generar tabla markdown
        lines = ["### 📊 Matriz de Dependencias\n"]
        
        # Header de la tabla
        header = "| Archivo |"
        separator = "|---------|"
        
        for name in file_names:
            short_name = name[:10] + "..." if len(name) > 10 else name
            header += f" {short_name} |"
            separator += "-------|"
        
        lines.append(header)
        lines.append(separator)
        
        # Filas de la tabla
        for i, source_path in enumerate(file_paths):
            source_name = file_names[i]
            display_name = source_name[:15] + "..." if len(source_name) > 15 else source_name
            row = f"| **{display_name}** |"
            
            for target_path in file_paths:
                if target_path in dependency_matrix[source_path]:
                    row += " ✅ |"
                else:
                    row += " ❌ |"
            
            lines.append(row)
        
        lines.append("\n*✅ = Tiene dependencia, ❌ = No tiene dependencia*\n")
        return "\n".join(lines)

    def _build_directed_graph(self, connections: Dict[str, List[str]]) -> Dict[str, Dict[str, List[str]]]:
        """
        Construir un grafo dirigido a partir de las conexiones.
        
        Args:
            connections: Mapa de conexiones entre archivos
            
        Returns:
            Diccionario con grafo dirigido (ingoing y outgoing)
        """
        graph = {
            'ingoing': defaultdict(list),
            'outgoing': defaultdict(list)
        }
        
        # Construir enlaces
        for source, targets in connections.items():
            for target in targets:
                graph['outgoing'][source].append(target)
                graph['ingoing'][target].append(source)
        
        return {
            'ingoing': dict(graph['ingoing']),
            'outgoing': dict(graph['outgoing'])
        }
    
    def _calculate_graph_metrics(self, graph: Dict[str, Dict[str, List[str]]], 
                               file_imports: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Calcular métricas del grafo de dependencias.
        
        Args:
            graph: Grafo dirigido
            file_imports: Información de importaciones
            
        Returns:
            Diccionario con métricas
        """
        # Extraer datos
        ingoing = graph['ingoing']
        outgoing = graph['outgoing']
        all_files = set(file_imports.keys())
        
        # Calcular grados
        in_degrees = {file: len(deps) for file, deps in ingoing.items()}
        out_degrees = {file: len(deps) for file, deps in outgoing.items()}
        
        # Calcular promedio de importaciones
        total_imports = sum(len(data['imports']) for data in file_imports.values())
        avg_imports = total_imports / len(file_imports) if file_imports else 0
        
        # Calcular densidad del grafo
        nodes = len(all_files)
        edges = sum(len(deps) for deps in outgoing.values())
        max_possible_edges = nodes * (nodes - 1) if nodes > 1 else 0
        density = edges / max_possible_edges if max_possible_edges > 0 else 0
        
        # Contar archivos aislados
        isolated_files = len(all_files - set(ingoing.keys()) - set(outgoing.keys()))
        
        # Calcular estadísticas de grado
        all_in_degrees = [in_degrees.get(file, 0) for file in all_files]
        all_out_degrees = [out_degrees.get(file, 0) for file in all_files]
        
        # Métricas finales
        return {
            'nodes': nodes,
            'edges': edges,
            'avg_imports': avg_imports,
            'density': density,
            'isolated_files': isolated_files,
            'max_in_degree': max(all_in_degrees) if all_in_degrees else 0,
            'max_out_degree': max(all_out_degrees) if all_out_degrees else 0,
            'avg_in_degree': sum(all_in_degrees) / nodes if nodes > 0 else 0,
            'avg_out_degree': sum(all_out_degrees) / nodes if nodes > 0 else 0
        }
    
    def _build_nodes_data(self, file_imports: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """
        Construir datos de nodos para el grafo.
        
        Args:
            file_imports: Información de importaciones
            
        Returns:
            Lista de datos de nodos
        """
        nodes = []
        
        for file_path, data in file_imports.items():
            node = {
                'id': file_path,
                'language': data['language'],
                'import_count': len(data['imports'])
            }
            nodes.append(node)
            
        return nodes
    
    def _build_edges_data(self, connections: Dict[str, List[str]]) -> List[Dict[str, str]]:
        """
        Construir datos de enlaces para el grafo.
        
        Args:
            connections: Mapa de conexiones
            
        Returns:
            Lista de datos de enlaces
        """
        edges = []
        
        for source, targets in connections.items():
            for target in targets:
                edge = {
                    'source': source,
                    'target': target
                }
                edges.append(edge)
                
        return edges
    
    def _identify_central_files(self, graph: Dict[str, Dict[str, List[str]]]) -> List[Dict[str, Any]]:
        """
        Identificar archivos centrales en el grafo de dependencias.
        
        Args:
            graph: Grafo dirigido
            
        Returns:
            Lista ordenada de archivos centrales con métricas
        """
        ingoing = graph['ingoing']
        outgoing = graph['outgoing']
        
        # Calcular grado para todos los archivos
        files_with_degrees = []
        
        # Unir todos los nodos que aparecen en el grafo
        all_files = set(ingoing.keys()).union(set(outgoing.keys()))
        
        for file in all_files:
            in_degree = len(ingoing.get(file, []))
            out_degree = len(outgoing.get(file, []))
            files_with_degrees.append({
                'file': file,
                'in_degree': in_degree,
                'out_degree': out_degree,
                'total': in_degree + out_degree
            })
        
        # Ordenar por grado total descendente
        return sorted(files_with_degrees, key=lambda x: x['total'], reverse=True)
    
    def _detect_cycles(self, graph: Dict[str, Dict[str, List[str]]]) -> List[List[str]]:
        """
        Detectar ciclos en el grafo de dependencias.
        
        Args:
            graph: Grafo dirigido
            
        Returns:
            Lista de ciclos detectados
        """
        outgoing = graph['outgoing']
        cycles = []
        
        # Implementación de DFS para detectar ciclos
        def find_cycles(node, path=None, visited=None):
            if path is None:
                path = []
            if visited is None:
                visited = set()
                
            path.append(node)
            visited.add(node)
            
            for neighbor in outgoing.get(node, []):
                if neighbor in path:  # Ciclo detectado
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
                elif neighbor not in visited:
                    find_cycles(neighbor, path.copy(), visited)
        
        # Buscar ciclos desde cada nodo
        for node in outgoing:
            find_cycles(node)
        
        # Eliminar duplicados y ordenar por longitud
        unique_cycles = []
        cycle_strs = set()
        
        for cycle in cycles:
            # Normalizar el ciclo para evitar duplicados
            normalized = tuple(sorted(cycle))
            if normalized not in cycle_strs:
                cycle_strs.add(normalized)
                unique_cycles.append(cycle)
                
        return sorted(unique_cycles, key=len)
    
    def _generate_text_visualization(self, graph_data: Dict[str, Any], max_nodes: int = 20) -> str:
        """
        Generar una representación textual simple del grafo.
        
        Args:
            graph_data: Datos del grafo
            max_nodes: Máximo número de nodos a mostrar
            
        Returns:
            Representación textual del grafo
        """
        lines = []
        
        # Obtener archivos importantes (no solo centrales)
        important_files = graph_data.get('important_files', [])
        if not important_files:
            # Fallback a archivos centrales si no hay archivos importantes
            important_files = graph_data.get('central_files', [])
        
        # Limitar archivos a mostrar
        files_to_show = important_files[:max_nodes]
        
        if not files_to_show:
            return "No se encontraron archivos importantes para mostrar."
        
        # Preparar estructura para la visualización
        node_map = {}
        file_paths = []
        
        for i, file_info in enumerate(files_to_show):
            # Compatibilidad con diferentes estructuras de datos
            if isinstance(file_info, dict):
                file_path = file_info.get('file', file_info.get('path', f'unknown_{i}'))
                importance = file_info.get('importance_score', 0)
            else:
                file_path = str(file_info)
                importance = 0
            
            short_name = os.path.basename(file_path)
            node_map[file_path] = f"{i+1}"
            file_paths.append(file_path)
            
            # Añadir nodo a la visualización con información de importancia
            if importance > 0:
                lines.append(f"{i+1}. {file_path} (importancia: {importance:.1f})")
            else:
                lines.append(f"{i+1}. {file_path}")
        
        lines.append("\nDependencias:")
        
        # Mostrar conexiones de los archivos mostrados
        edges = graph_data.get('edges', [])
        connections_found = False
        
        # Crear un mapa para mostrar dependencias de manera más clara
        dependencies_map = {}
        
        for edge in edges:
            source = edge.get('source', '')
            target = edge.get('target', '')
            
            if source in file_paths:
                if source not in dependencies_map:
                    dependencies_map[source] = []
                dependencies_map[source].append(target)
                connections_found = True
        
        # Mostrar dependencias agrupadas por archivo
        if dependencies_map:
            for source_file in file_paths:
                if source_file in dependencies_map:
                    targets = dependencies_map[source_file]
                    # Filtrar solo targets que están en nuestros archivos mostrados
                    internal_targets = [t for t in targets if t in file_paths]
                    external_targets = [t for t in targets if t not in file_paths]
                    
                    if internal_targets or external_targets:
                        source_display = os.path.basename(source_file)
                        line_parts = [f"  {node_map[source_file]}. {source_display} →"]
                        
                        if internal_targets:
                            internal_display = [f"{node_map[t]}.{os.path.basename(t)}" for t in internal_targets if t in node_map]
                            if internal_display:
                                line_parts.append(f" [{', '.join(internal_display)}]")
                        
                        if external_targets:
                            line_parts.append(f" +{len(external_targets)} externas")
                        
                        lines.append(''.join(line_parts))
        
        if not connections_found:
            lines.append("  (No se detectaron conexiones entre los archivos mostrados)")
        
        return "\n".join(lines)
    
    def _enhance_madge_results(self, madge_result: Dict[str, Any], 
                               project_path: str, max_files: int) -> Dict[str, Any]:
        """
        Mejorar resultados de Madge con análisis adicional.
        
        Args:
            madge_result: Resultados del análisis de Madge
            project_path: Ruta al proyecto
            max_files: Número máximo de archivos
            
        Returns:
            Diccionario mejorado con datos adicionales
        """
        logger.info("Mejorando resultados de Madge con análisis adicional...")
        
        # Obtener estadísticas de gitignore usando ProjectScanner
        from src.analyzers.project_scanner import get_project_scanner
        scanner = get_project_scanner(max_files=max_files)
        
        # Realizar un escaneo rápido solo para obtener estadísticas de gitignore
        gitignore_stats = 0
        try:
            scan_result = scanner.scan_project(project_path)
            gitignore_stats = scan_result.get('stats', {}).get('gitignore_excluded', 0)
        except Exception as e:
            logger.warning(f"No se pudieron obtener estadísticas de gitignore: {e}")
        
        # Convertir formato de Madge al formato esperado
        nodes = []
        edges = []
        
        # Construir nodos desde archivos importantes
        for file_info in madge_result['important_files']:
            nodes.append({
                'id': file_info['path'],
                'path': file_info['path'],
                'full_path': file_info['full_path'],
                'type': file_info['file_info']['type'],
                'size': file_info['file_info']['size'],
                'directory': file_info['file_info']['directory'],
                'dependencies_count': file_info['dependencies_out'],
                'dependents_count': file_info['dependencies_in'],
                'importance_score': file_info['importance_score']
            })
        
        # Construir edges desde el grafo de dependencias
        dependency_graph = madge_result['dependency_graph']
        edge_id = 0
        for source, targets in dependency_graph.items():
            for target in targets:
                edges.append({
                    'id': edge_id,
                    'source': source,
                    'target': target,
                    'weight': 1
                })
                edge_id += 1
        
        # Calcular métricas adicionales
        enhanced_metrics = {
            **madge_result['metrics'],
            'analysis_method': 'madge_enhanced',
            'performance_optimized': True,
            'files_analyzed': len(madge_result['important_files']),
            'groups_detected': len(madge_result['functionality_groups'])
        }
        
        # Estructura final mejorada
        enhanced_result = {
            'project_path': project_path,
            'nodes': nodes,
            'edges': edges,
            'metrics': enhanced_metrics,
            'important_files': madge_result['important_files'],
            'functionality_groups': madge_result['functionality_groups'],
            'connected_components': [],  # Se puede calcular si es necesario
            'disconnected_files': [],
            'central_files': self._identify_central_files_from_madge(madge_result['important_files']),
            'language_stats': self._calculate_language_stats_from_madge(madge_result['important_files']),
            'file_cycles': self._extract_cycles_from_groups(madge_result['functionality_groups']),
            'files_excluded': {
                'by_gitignore': gitignore_stats,
                'total_excluded': gitignore_stats  # Para Madge, solo consideramos gitignore exclusions
            },
            'madge_analysis': True,
            'performance_summary': self._generate_performance_summary(madge_result)
        }
        
        logger.info(f"Análisis mejorado completado: {len(nodes)} archivos importantes analizados")
        return enhanced_result
    
    def _identify_central_files_from_madge(self, important_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identificar archivos centrales desde resultados de Madge.
        
        Args:
            important_files: Lista de archivos importantes
            
        Returns:
            Lista de archivos centrales
        """
        # Ordenar por puntuación de importancia
        sorted_files = sorted(important_files, key=lambda x: x['importance_score'], reverse=True)
        
        # Tomar los top archivos como centrales
        central_count = min(10, len(sorted_files) // 3)  # Top 1/3 o máximo 10
        central_files = []
        
        for file_info in sorted_files[:central_count]:
            central_files.append({
                'path': file_info['path'],
                'importance_score': file_info['importance_score'],
                'dependencies_out': file_info['dependencies_out'],
                'dependencies_in': file_info['dependencies_in'],
                'centrality_type': 'importance_based'
            })
        
        return central_files
    
    def _calculate_language_stats_from_madge(self, important_files: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Calcular estadísticas de lenguajes desde archivos importantes.
        
        Args:
            important_files: Lista de archivos importantes
            
        Returns:
            Diccionario con estadísticas por tipo de archivo
        """
        stats = {}
        for file_info in important_files:
            file_type = file_info['file_info']['type']
            stats[file_type] = stats.get(file_type, 0) + 1
        
        return stats
    
    def _extract_cycles_from_groups(self, groups: List[Dict[str, Any]]) -> List[List[str]]:
        """
        Extraer ciclos desde grupos de funcionalidad.
        
        Args:
            groups: Lista de grupos de funcionalidad
            
        Returns:
            Lista de ciclos detectados
        """
        cycles = []
        for group in groups:
            if group['type'] == 'circular' and 'cycle_path' in group:
                cycles.append(group['cycle_path'])
        
        return cycles
    
    def _generate_performance_summary(self, madge_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generar resumen de rendimiento del análisis.
        
        Args:
            madge_result: Resultados del análisis de Madge
            
        Returns:
            Diccionario con resumen de rendimiento
        """
        return {
            'analysis_type': madge_result['analysis_type'],
            'files_filtered': True,
            'important_files_count': len(madge_result['important_files']),
            'groups_detected': len(madge_result['functionality_groups']),
            'complexity_level': madge_result['metrics']['complexity'],
            'optimization_applied': 'dependency_filtering'
        }
    
    def _detect_functionality_groups(self, file_imports: Dict[str, Any], 
                                   graph: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """
        Detectar grupos de funcionalidad en el proyecto.
        
        Args:
            file_imports: Información de importaciones de archivos
            graph: Grafo de dependencias
            
        Returns:
            Lista de grupos de funcionalidad detectados
        """
        groups = []
        
        # Obtener archivos importantes primero
        important_files = self._identify_important_files(file_imports, graph)
        
        # Crear grupos basados en patrones de directorio
        directory_groups = {}
        for file_info in important_files:
            file_path = file_info['path']
            directory = os.path.dirname(file_path)
            
            # Normalizar nombre del directorio
            dir_parts = directory.replace('\\', '/').split('/')
            if len(dir_parts) > 1:
                group_name = '/'.join(dir_parts[-2:])  # Últimos 2 niveles
            else:
                group_name = dir_parts[-1] if dir_parts and dir_parts[-1] else 'root'
            
            if group_name not in directory_groups:
                directory_groups[group_name] = []
            directory_groups[group_name].append(file_info)
        
        # Convertir a formato de grupos
        for group_name, files in directory_groups.items():
            if len(files) >= 2:  # Solo grupos con múltiples archivos
                total_importance = sum(f.get('importance_score', 0) for f in files)
                groups.append({
                    'name': f"📁 {group_name}",
                    'type': 'directory',
                    'files': files,
                    'size': len(files),
                    'total_importance': total_importance,
                    'description': f"Archivos en {group_name}"
                })
        
        # Detectar grupos por tipo de archivo
        type_groups = {}
        for file_info in important_files:
            file_type = file_info.get('file_info', {}).get('type', 'unknown')
            if file_type not in type_groups:
                type_groups[file_type] = []
            type_groups[file_type].append(file_info)
        
        # Añadir grupos por tipo si son significativos
        for file_type, files in type_groups.items():
            if len(files) >= 3 and file_type != 'unknown':  # Solo tipos significativos
                total_importance = sum(f.get('importance_score', 0) for f in files)
                groups.append({
                    'name': f"🔧 Archivos {file_type}",
                    'type': 'filetype',
                    'files': files,
                    'size': len(files),
                    'total_importance': total_importance,
                    'description': f"Archivos de tipo {file_type}"
                })
        
        # Detectar dependencias circulares
        cycles = self._detect_cycles(graph)
        if cycles:
            cycle_files = []
            for cycle in cycles[:3]:  # Solo primeros 3 ciclos
                for file_path in cycle:
                    # Buscar info del archivo en important_files
                    file_info = next((f for f in important_files if f['path'] == file_path), None)
                    if file_info and file_info not in cycle_files:
                        cycle_files.append(file_info)
            
            if cycle_files:
                groups.append({
                    'name': f"🔄 Dependencias circulares",
                    'type': 'circular',
                    'files': cycle_files,
                    'size': len(cycle_files),
                    'total_importance': sum(f.get('importance_score', 0) for f in cycle_files),
                    'description': f"Archivos con dependencias circulares"
                })
        
        # Ordenar grupos por importancia
        groups.sort(key=lambda x: x['total_importance'], reverse=True)
        
        return groups[:10]  # Límite de 10 grupos
    
    def _identify_important_files(self, file_imports: Dict[str, Any], 
                                graph: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """
        Identificar archivos importantes basado en dependencias.
        
        Args:
            file_imports: Información de importaciones
            graph: Grafo de dependencias
            
        Returns:
            Lista de archivos importantes ordenada por importancia
        """
        important_files = []
        
        for file_path, imports_info in file_imports.items():
            # Contar dependencias entrantes y salientes
            deps_out = len(imports_info.get('imports', []))
            deps_in = sum(1 for deps in graph.values() if file_path in deps)
            
            # Calcular score de importancia
            importance_score = deps_out + (deps_in * 2)  # Dependencias entrantes valen más
            
            if importance_score >= 3:  # Umbral mínimo
                important_files.append({
                    'path': file_path,
                    'dependencies_out': deps_out,
                    'dependencies_in': deps_in,
                    'importance_score': importance_score,
                    'file_info': imports_info.get('file_info', {})
                })
        
        # Ordenar por importancia
        important_files.sort(key=lambda x: x['importance_score'], reverse=True)
        
        return important_files[:50]  # Límite de 50 archivos importantes
    
    def _generate_group_text_visualization(self, group: Dict[str, Any]) -> str:
        """
        Generar representación textual de un grupo funcional.
        
        Args:
            group: Información del grupo funcional
            
        Returns:
            Representación textual del grupo
        """
        try:
            lines = []
            files = group.get('files', [])
            
            if not files:
                return "Grupo vacío"
            
            # Título del grupo
            lines.append(f"Grupo: {group['name']} ({group['size']} archivos)")
            lines.append("=" * 50)
            
            # Si es un grupo de directorio, mostrar estructura
            if group['type'] == 'directory':
                lines.append("Estructura de directorio:")
                for file_info in files[:6]:  # Máximo 6 archivos
                    file_path = file_info.get('path', file_info.get('file', 'unknown'))
                    basename = os.path.basename(file_path)
                    importance = file_info.get('importance_score', 0)
                    lines.append(f"  📄 {basename} (importancia: {importance:.1f})")
                    
            elif group['type'] == 'filetype':
                lines.append(f"Archivos de tipo {group['name']}:")
                for file_info in files[:6]:
                    file_path = file_info.get('path', file_info.get('file', 'unknown'))
                    basename = os.path.basename(file_path)
                    importance = file_info.get('importance_score', 0)
                    lines.append(f"  🔧 {basename} (importancia: {importance:.1f})")
                    
            elif group['type'] == 'circular':
                lines.append("Archivos con dependencias circulares:")
                for file_info in files[:6]:
                    file_path = file_info.get('path', file_info.get('file', 'unknown'))
                    basename = os.path.basename(file_path)
                    lines.append(f"  🔄 {basename}")
                    
            # Mostrar conexiones si hay pocas
            if len(files) <= 4:
                lines.append("\nConexiones internas:")
                for i, file_info in enumerate(files):
                    file_path = file_info.get('path', file_info.get('file', 'unknown'))
                    basename = os.path.basename(file_path)
                    # Simplificar conexiones
                    connected_to = [os.path.basename(f.get('path', f.get('file', ''))) 
                                  for j, f in enumerate(files) if i != j]
                    if connected_to:
                        lines.append(f"  {basename} → {', '.join(connected_to[:3])}")
                    else:
                        lines.append(f"  {basename} (sin conexiones internas)")
            
            if len(files) > 6:
                lines.append(f"  ... y {len(files) - 6} archivos más")
            
            return "\n".join(lines)
            
        except Exception as e:
            return f"Error al generar visualización del grupo: {str(e)}"
        

def get_dependency_graph() -> DependencyGraph:
    """
    Obtener una instancia del generador de grafo de dependencias.
    
    Returns:
        Instancia del generador
    """
    return DependencyGraph()
