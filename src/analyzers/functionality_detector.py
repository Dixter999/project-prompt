#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para la detección de funcionalidades en proyectos.

Este módulo analiza el código fuente para identificar funcionalidades
comunes como autenticación, bases de datos, APIs, frontend, etc.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
import json

from src.utils.logger import get_logger
from src.analyzers.project_scanner import ProjectScanner, get_project_scanner
from src.templates.common_functionalities import (
    FUNCTIONALITY_PATTERNS, DETECTION_WEIGHTS, CONFIDENCE_THRESHOLD
)

# Configurar logger
logger = get_logger()


class FunctionalityDetector:
    """Detector de funcionalidades comunes en proyectos de software."""
    
    def __init__(self, scanner: Optional[ProjectScanner] = None):
        """
        Inicializar el detector de funcionalidades.
        
        Args:
            scanner: Escáner de proyectos opcional
        """
        self.scanner = scanner or get_project_scanner()
        
        # Resultados del análisis
        self.functionalities = {}
        self.evidence = {}
        self.confidence_scores = {}
    
    def detect_functionalities(self, project_path: str) -> Dict[str, Any]:
        """
        Detectar funcionalidades presentes en un proyecto.
        
        Args:
            project_path: Ruta al directorio del proyecto
            
        Returns:
            Dict con funcionalidades detectadas y scores de confianza
        """
        # Escanear el proyecto para obtener información
        project_data = self.scanner.scan_project(project_path)
        
        # Resetear resultados previos
        self.functionalities = {}
        self.evidence = {}
        self.confidence_scores = {}
        
        # Inicializar scores para cada funcionalidad
        for functionality in FUNCTIONALITY_PATTERNS:
            self.confidence_scores[functionality] = 0
            self.evidence[functionality] = {
                'files': [],
                'imports': [],
                'code_patterns': [],
                'config_keys': []
            }
        
        # Analizar archivos y directorios
        self._analyze_file_names(project_data)
        
        # Analizar importaciones y código
        self._analyze_file_contents(project_data)
        
        # Analizar archivos de configuración
        self._analyze_config_files(project_data)
        
        # Determinar funcionalidades presentes basado en scores
        detected = {}
        for functionality, score in self.confidence_scores.items():
            detected[functionality] = {
                'present': score >= CONFIDENCE_THRESHOLD,
                'confidence': min(100, round(score * 100 / (CONFIDENCE_THRESHOLD * 2))),
                'score': score,
                'evidence': self.evidence[functionality]
            }
            
        # Guardar resultados
        self.functionalities = {
            'detected': detected,
            'main_functionalities': self._get_main_functionalities(detected),
            'project_path': project_path,
            'detection_threshold': CONFIDENCE_THRESHOLD
        }
        
        return self.functionalities
    
    def _get_main_functionalities(self, detected: Dict[str, Any]) -> List[str]:
        """
        Obtener lista de funcionalidades principales detectadas.
        
        Args:
            detected: Diccionario con las funcionalidades detectadas
            
        Returns:
            Lista de nombres de funcionalidades principales
        """
        return [
            name for name, data in detected.items()
            if data.get('present', False)
        ]
    
    def _analyze_file_names(self, project_data: Dict[str, Any]) -> None:
        """
        Analizar nombres de archivos y directorios para detectar funcionalidades.
        
        Args:
            project_data: Datos del proyecto escaneado
        """
        files = project_data.get('files', [])
        
        for file_info in files:
            file_path = file_info.get('path', '')
            file_name = file_info.get('name', '')
            
            # Comprobar cada funcionalidad
            for func_name, patterns in FUNCTIONALITY_PATTERNS.items():
                for pattern in patterns['files']:
                    if re.search(pattern, file_path, re.IGNORECASE) or re.search(pattern, file_name, re.IGNORECASE):
                        # Incrementar score
                        self.confidence_scores[func_name] += DETECTION_WEIGHTS['files']
                        
                        # Guardar evidencia
                        if file_path not in self.evidence[func_name]['files']:
                            self.evidence[func_name]['files'].append(file_path)
                        
                        # Solo contar una vez por archivo
                        break
    
    def _analyze_file_contents(self, project_data: Dict[str, Any]) -> None:
        """
        Analizar contenido de archivos para detectar patrones de código e importaciones.
        
        Args:
            project_data: Datos del proyecto escaneado
        """
        files = project_data.get('files', [])
        
        for file_info in files:
            # Solo procesar archivos de código no binarios
            if file_info.get('is_binary', True) or not file_info.get('language'):
                continue
                
            file_path = file_info.get('path', '')
            
            try:
                # Leer contenido del archivo
                with open(os.path.join(project_data.get('project_path', ''), file_path), 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Analizar cada funcionalidad
                    for func_name, patterns in FUNCTIONALITY_PATTERNS.items():
                        # Buscar patrones de importaciones
                        for pattern in patterns['imports']:
                            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                                self.confidence_scores[func_name] += DETECTION_WEIGHTS['imports']
                                if pattern not in self.evidence[func_name]['imports']:
                                    self.evidence[func_name]['imports'].append(pattern)
                        
                        # Buscar patrones de código
                        for pattern in patterns['code_patterns']:
                            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                                self.confidence_scores[func_name] += DETECTION_WEIGHTS['code_patterns']
                                if pattern not in self.evidence[func_name]['code_patterns']:
                                    self.evidence[func_name]['code_patterns'].append(pattern)
                                
            except Exception as e:
                logger.debug(f"Error al analizar contenido de {file_path}: {e}")
    
    def _analyze_config_files(self, project_data: Dict[str, Any]) -> None:
        """
        Analizar archivos de configuración para detectar claves relacionadas con funcionalidades.
        
        Args:
            project_data: Datos del proyecto escaneado
        """
        files = project_data.get('files', [])
        
        # Identificar archivos de configuración común
        config_files = [
            f for f in files if any([
                f.get('name', '').endswith(('.json', '.yaml', '.yml', '.toml', '.ini', '.env')),
                f.get('name', '') in ['package.json', 'config.js', 'settings.py', 'app.config.js'],
                'config' in f.get('name', '').lower(),
                'setting' in f.get('name', '').lower()
            ])
        ]
        
        for file_info in config_files:
            file_path = file_info.get('path', '')
            
            try:
                # Leer contenido del archivo
                with open(os.path.join(project_data.get('project_path', ''), file_path), 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Analizar cada funcionalidad
                    for func_name, patterns in FUNCTIONALITY_PATTERNS.items():
                        for pattern in patterns['config_keys']:
                            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                                self.confidence_scores[func_name] += DETECTION_WEIGHTS['config_keys']
                                if pattern not in self.evidence[func_name]['config_keys']:
                                    self.evidence[func_name]['config_keys'].append(pattern)
                                
            except Exception as e:
                logger.debug(f"Error al analizar configuración en {file_path}: {e}")
    
    def get_functionality_info(self, functionality_name: str) -> Dict[str, Any]:
        """
        Obtener información detallada sobre una funcionalidad específica.
        
        Args:
            functionality_name: Nombre de la funcionalidad
            
        Returns:
            Dict con información detallada sobre la funcionalidad
        """
        if not self.functionalities:
            return {}
            
        if functionality_name not in self.functionalities.get('detected', {}):
            return {}
            
        return {
            'name': functionality_name,
            'present': self.functionalities['detected'][functionality_name]['present'],
            'confidence': self.functionalities['detected'][functionality_name]['confidence'],
            'evidence': self.functionalities['detected'][functionality_name]['evidence']
        }
    
    def summarize_functionalities(self) -> str:
        """
        Generar un resumen textual de las funcionalidades detectadas.
        
        Returns:
            Texto con el resumen de funcionalidades
        """
        if not self.functionalities or not self.functionalities.get('detected'):
            return "No se ha realizado ningún análisis de funcionalidades."
            
        main_functionalities = self.functionalities.get('main_functionalities', [])
        
        if not main_functionalities:
            return "No se han detectado funcionalidades principales en el proyecto."
            
        summary = []
        summary.append(f"Funcionalidades detectadas ({len(main_functionalities)}):")
        
        # Añadir cada funcionalidad con su nivel de confianza
        for func_name in main_functionalities:
            confidence = self.functionalities['detected'][func_name]['confidence']
            summary.append(f"- {func_name.capitalize()}: {confidence}% de confianza")
            
            # Añadir evidencia importante (top 3 de cada tipo)
            evidence = self.functionalities['detected'][func_name]['evidence']
            
            if evidence['files']:
                file_examples = evidence['files'][:3]
                summary.append(f"  Archivos: {', '.join(file_examples)}")
                
            if evidence['imports']:
                import_examples = evidence['imports'][:3]
                summary.append(f"  Importaciones: {', '.join(import_examples)}")
                
        return "\n".join(summary)


def get_functionality_detector(scanner: Optional[ProjectScanner] = None) -> FunctionalityDetector:
    """
    Obtener una instancia del detector de funcionalidades.
    
    Args:
        scanner: Escáner de proyectos opcional
        
    Returns:
        Instancia de FunctionalityDetector
    """
    return FunctionalityDetector(scanner=scanner)