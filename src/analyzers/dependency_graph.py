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
from src.analyzers.connection_analyzer import ConnectionAnalyzer, get_connection_analyzer

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
        self.connection_analyzer = get_connection_analyzer()
    
    def build_dependency_graph(self, project_path: str, max_files: int = 5000) -> Dict[str, Any]:
        """
        Construir un grafo de dependencias para un proyecto.
        
        Args:
            project_path: Ruta al proyecto
            max_files: Número máximo de archivos a analizar
            
        Returns:
            Diccionario con datos del grafo
        """
        # Analizar conexiones entre archivos
        connections = self.connection_analyzer.analyze_connections(project_path, max_files)
        
        # Construir grafo dirigido
        graph = self._build_directed_graph(connections['file_connections'])
        
        # Calcular métricas del grafo
        metrics = self._calculate_graph_metrics(graph, connections['file_imports'])
        
        # Estructura final del grafo de dependencias
        dependency_graph = {
            'project_path': project_path,
            'nodes': self._build_nodes_data(connections['file_imports']),
            'edges': self._build_edges_data(connections['file_connections']),
            'metrics': metrics,
            'connected_components': connections['connected_components'],
            'disconnected_files': connections['disconnected_files'],
            'central_files': self._identify_central_files(graph),
            'language_stats': connections['language_stats'],
            'file_cycles': self._detect_cycles(graph),
            'files_excluded': connections.get('files_excluded', {})
        }
        
        logger.info(f"Grafo de dependencias construido: {len(dependency_graph['nodes'])} nodos, {len(dependency_graph['edges'])} enlaces")
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
                markdown.append(f"Total de archivos excluidos: {excluded.get('total_excluded', 0)}")
                markdown.append("\n## Archivos Excluidos")
                markdown.append("| Tipo de exclusión | Cantidad |")
                markdown.append("|---|---|")
                markdown.append(f"| Por extensión (multimedia, binarios, etc.) | {excluded.get('by_extension', 0)} |")
                markdown.append(f"| Por patrón (directorios/archivos no relevantes) | {excluded.get('by_pattern', 0)} |")
                markdown.append(f"| HTML puramente presentacional | {excluded.get('html_presentational', 0)} |")
            
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
                file_path = file_info['file']
                in_degree = file_info['in_degree']
                out_degree = file_info['out_degree']
                total = file_info['total']
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
            
            # Representación textual del grafo
            markdown.append("\n## Representación Textual del Grafo")
            markdown.append("```")
            markdown.append(self._generate_text_visualization(graph_data, max_nodes=20))
            markdown.append("```")
            
            return "\n".join(markdown)
            
        except Exception as e:
            logger.error(f"Error al generar visualización markdown: {e}", exc_info=True)
            return f"Error al generar visualización: {str(e)}"
    
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
        
        # Obtener archivos centrales
        central_files = graph_data['central_files'][:max_nodes]
        
        # Preparar estructura para la visualización
        node_map = {}
        for i, file_info in enumerate(central_files):
            file_path = file_info['file']
            short_name = os.path.basename(file_path)
            node_map[file_path] = f"[{i+1}] {short_name}"
            
            # Añadir nodo a la visualización
            lines.append(f"{i+1}. {file_path}")
        
        lines.append("\nDependencias:")
        
        # Añadir conexiones
        edges = graph_data['edges']
        shown_edges = set()
        
        for edge in edges:
            source = edge['source']
            target = edge['target']
            
            # Solo mostrar conexiones entre nodos centrales
            if source in node_map and target in node_map:
                edge_str = f"{source} -> {target}"
                if edge_str not in shown_edges:
                    lines.append(f"  {node_map[source]} -> {node_map[target]}")
                    shown_edges.add(edge_str)
        
        return "\n".join(lines)


def get_dependency_graph() -> DependencyGraph:
    """
    Obtener una instancia del generador de grafo de dependencias.
    
    Returns:
        Instancia del generador
    """
    return DependencyGraph()
