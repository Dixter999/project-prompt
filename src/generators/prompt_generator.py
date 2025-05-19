#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generador de prompts contextuales para proyectos.

Este módulo contiene clases y funciones para generar prompts
basados en el análisis de proyectos, que pueden ser utilizados
con modelos de IA para obtener sugerencias y recomendaciones.
"""

import os
import re
import random
from typing import Dict, List, Any, Optional, Tuple, TYPE_CHECKING
import json
from pathlib import Path

from src.utils.logger import get_logger

# Evitar importación circular
if TYPE_CHECKING:
    from src.analyzers.project_scanner import ProjectScanner 
    from src.analyzers.functionality_detector import FunctionalityDetector
from src.templates.prompt_templates import (
    FREE_TEMPLATES,
    PROJECT_TYPE_HINTS,
    FUNCTIONALITY_DESCRIPTIONS,
    COMMON_FRAMEWORKS,
    PREGENERATED_PHRASES
)

# Configurar logger
logger = get_logger()


class PromptGenerator:
    """Generador de prompts contextuales para asistentes IA."""
    
    def __init__(self, is_premium: bool = False):
        """
        Inicializar el generador de prompts.
        
        Args:
            is_premium: Si el usuario tiene acceso premium
        """
        self.is_premium = is_premium
        self.max_prompts = 10 if is_premium else 3
        
        # Importar aquí para evitar importaciones circulares
        from src.analyzers.project_scanner import get_project_scanner
        from src.analyzers.functionality_detector import get_functionality_detector
        
        self.scanner = get_project_scanner()
        self.functionality_detector = get_functionality_detector(scanner=self.scanner)
        
    def generate_prompts(self, project_path: str) -> Dict[str, Any]:
        """
        Generar prompts contextuales basados en el análisis del proyecto.
        
        Args:
            project_path: Ruta al directorio del proyecto
            
        Returns:
            Dict con los prompts generados
        """
        # Analizar proyecto
        project_data = self.scanner.scan_project(project_path)
        
        # Detectar funcionalidades
        functionality_data = self.functionality_detector.detect_functionalities(project_path)
        
        # Generar prompts básicos (versión freemium)
        prompts = {}
        
        # Descripción general del proyecto
        prompts['description'] = self._generate_description_prompt(project_data, functionality_data)
        
        # Sugerencias de mejora
        prompts['improvements'] = self._generate_improvements_prompt(project_data, functionality_data)
        
        # Identificación de problemas potenciales
        prompts['issues'] = self._generate_issues_prompt(project_data, functionality_data)
        
        # Añadir metadata
        import datetime
        result = {
            'prompts': prompts,
            'project_path': project_path,
            'timestamp': datetime.datetime.now().isoformat(),
            'is_premium': self.is_premium,
            'prompt_count': len(prompts)
        }
        
        return result
    
    def save_prompts(self, project_path: str, output_path: Optional[str] = None) -> str:
        """
        Generar y guardar prompts en un archivo JSON.
        
        Args:
            project_path: Ruta al directorio del proyecto
            output_path: Ruta donde guardar el archivo (opcional)
            
        Returns:
            Ruta al archivo generado
        """
        # Generar prompts
        result = self.generate_prompts(project_path)
        
        # Determinar ruta de salida
        if not output_path:
            # Crear directorio .project-prompt si no existe
            output_dir = os.path.join(project_path, '.project-prompt')
            os.makedirs(output_dir, exist_ok=True)
            
            # Generar nombre de archivo basado en timestamp
            timestamp = result.get('timestamp', self.scanner.get_timestamp())
            output_path = os.path.join(output_dir, f"prompts_{timestamp}.json")
        else:
            # Asegurar la extensión .json
            if not output_path.endswith('.json'):
                output_path = f"{output_path}.json"
                
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Guardar en formato JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
            
        return output_path
    
    def _generate_description_prompt(self, project_data: Dict[str, Any], functionality_data: Dict[str, Any]) -> str:
        """
        Generar prompt de descripción del proyecto.
        
        Args:
            project_data: Datos del proyecto escaneado
            functionality_data: Datos de funcionalidades detectadas
            
        Returns:
            Prompt formateado
        """
        # Obtener datos básicos
        project_name = os.path.basename(project_data.get('project_path', ''))
        file_count = project_data.get('stats', {}).get('total_files', 0)
        dir_count = project_data.get('stats', {}).get('total_dirs', 0)
        
        # Obtener lenguajes principales
        main_languages = ", ".join(project_data.get('languages', {}).get('_main', ['No detectado']))
        
        # Obtener archivos importantes
        important_files_list = []
        for category, files in project_data.get('important_files', {}).items():
            if category.startswith('_'):  # Skip meta entries
                continue
            
            for file_path in files[:3]:  # Limitar a 3 por categoría
                important_files_list.append(f"- {file_path} ({category})")
                
        important_files = "\n".join(important_files_list) if important_files_list else "No se detectaron archivos importantes."
        
        # Obtener dependencias principales
        main_deps = project_data.get('dependencies', {}).get('_main', [])
        main_dependencies = ", ".join(main_deps[:10]) if main_deps else "No se detectaron dependencias principales."
        
        # Crear descripción del tipo de proyecto
        detected_features = functionality_data.get('main_functionalities', [])
        
        project_type_phrases = []
        for feature in detected_features:
            if feature in PROJECT_TYPE_HINTS:
                project_type_phrases.append(random.choice(PROJECT_TYPE_HINTS[feature]))
        
        if not project_type_phrases:
            project_type_description = "un proyecto de software"
        else:
            project_type_description = " y ".join(project_type_phrases[:2])
            
        # Crear descripción de frameworks
        languages_map = {}
        for lang in project_data.get('languages', {}).get('_main', []):
            lang_lower = lang.lower()
            for key in COMMON_FRAMEWORKS:
                if key in lang_lower:
                    languages_map[key] = True
        
        framework_phrases = []
        for lang in languages_map:
            if lang in COMMON_FRAMEWORKS:
                frameworks = COMMON_FRAMEWORKS[lang]
                framework_phrases.append(f"posiblemente {' o '.join(random.sample(frameworks, min(2, len(frameworks))))}")
        
        if not framework_phrases:
            framework_description = "tecnologías no identificadas"
        else:
            framework_description = ", ".join(framework_phrases)
        
        # Crear el prompt utilizando la plantilla
        return FREE_TEMPLATES['description'].format(
            project_name=project_name,
            file_count=file_count,
            dir_count=dir_count,
            main_languages=main_languages,
            important_files=important_files,
            main_dependencies=main_dependencies,
            project_type_description=project_type_description,
            framework_description=framework_description
        )
    
    def _generate_improvements_prompt(self, project_data: Dict[str, Any], functionality_data: Dict[str, Any]) -> str:
        """
        Generar prompt de sugerencias de mejora.
        
        Args:
            project_data: Datos del proyecto escaneado
            functionality_data: Datos de funcionalidades detectadas
            
        Returns:
            Prompt formateado
        """
        # Obtener datos básicos
        project_name = os.path.basename(project_data.get('project_path', ''))
        file_count = project_data.get('stats', {}).get('total_files', 0)
        dir_count = project_data.get('stats', {}).get('total_dirs', 0)
        
        # Obtener lenguajes principales
        main_languages = ", ".join(project_data.get('languages', {}).get('_main', ['No detectado']))
        main_language = project_data.get('languages', {}).get('_main', ['generic'])[0]
        
        # Obtener funcionalidades detectadas
        detected_features_list = []
        for feature in functionality_data.get('main_functionalities', []):
            confidence = functionality_data.get('detected', {}).get(feature, {}).get('confidence', 0)
            description = FUNCTIONALITY_DESCRIPTIONS.get(feature, "funcionalidad no especificada")
            detected_features_list.append(f"- {feature.capitalize()} ({confidence}%): {description}")
            
        detected_features = "\n".join(detected_features_list) if detected_features_list else "No se detectaron funcionalidades principales."
        
        # Determinar complejidad de estructura de archivos
        complexity = "simple"
        if file_count > 100:
            complexity = "compleja"
        elif file_count > 30:
            complexity = "moderada"
            
        file_structure_complexity = f"{complexity} ({file_count} archivos en {dir_count} directorios)"
        
        # Determinar patrones de código
        code_patterns = "Patrón no identificado"
        if 'api' in functionality_data.get('main_functionalities', []):
            code_patterns = "Patrón de API/Servicio"
        elif 'frontend' in functionality_data.get('main_functionalities', []):
            code_patterns = "Patrón de aplicación frontend"
            if 'api' in functionality_data.get('main_functionalities', []):
                code_patterns = "Arquitectura cliente-servidor (frontend-backend)"
        
        # Contar dependencias
        dependency_count = len(project_data.get('dependencies', {}).get('_all', []))
        
        # Crear el prompt utilizando la plantilla
        return FREE_TEMPLATES['improvements'].format(
            project_name=project_name,
            file_count=file_count,
            dir_count=dir_count,
            main_languages=main_languages,
            detected_features=detected_features,
            file_structure_complexity=file_structure_complexity,
            code_patterns=code_patterns,
            dependency_count=dependency_count,
            main_language=main_language
        )
    
    def _generate_issues_prompt(self, project_data: Dict[str, Any], functionality_data: Dict[str, Any]) -> str:
        """
        Generar prompt de identificación de problemas potenciales.
        
        Args:
            project_data: Datos del proyecto escaneado
            functionality_data: Datos de funcionalidades detectadas
            
        Returns:
            Prompt formateado
        """
        # Obtener datos básicos
        project_name = os.path.basename(project_data.get('project_path', ''))
        stats = project_data.get('stats', {})
        file_count = stats.get('total_files', 0)
        binary_count = stats.get('binary_files', 0)
        total_size = stats.get('total_size_kb', 0)
        
        # Obtener lenguajes principales
        main_languages = ", ".join(project_data.get('languages', {}).get('_main', ['No detectado']))
        
        # Calcular métricas
        files_per_dir = round(file_count / max(stats.get('total_dirs', 1), 1), 1)
        avg_file_size = round(total_size / max(file_count, 1), 2)
        
        # Contar archivos grandes
        large_files = 0
        for file_info in project_data.get('files', []):
            if file_info.get('size_kb', 0) > 100:
                large_files += 1
        
        # Identificar patrones problemáticos
        detected_patterns_list = []
        
        # Patrones de complejidad
        if files_per_dir > 10:
            detected_patterns_list.append("- Directorios con muchos archivos (promedio > 10)")
            
        if avg_file_size > 50:
            detected_patterns_list.append("- Archivos con tamaño promedio elevado (> 50KB)")
            
        if large_files > 5:
            detected_patterns_list.append(f"- Múltiples archivos grandes detectados ({large_files})")
        
        # Patrones de funcionalidades
        features = functionality_data.get('main_functionalities', [])
        if 'database' in features and 'tests' not in features:
            detected_patterns_list.append("- Código de base de datos sin tests automatizados")
            
        if 'authentication' in features and 'tests' not in features:
            detected_patterns_list.append("- Implementación de autenticación sin tests de seguridad")
            
        if len(features) >= 3 and file_count < 20:
            detected_patterns_list.append("- Múltiples funcionalidades en un proyecto pequeño (posible falta de separación)")
        
        # Generar lista final
        if not detected_patterns_list:
            detected_patterns_list.append("- No se detectaron patrones problemáticos obvios")
            
        detected_patterns = "\n".join(detected_patterns_list)
        
        # Crear el prompt utilizando la plantilla
        return FREE_TEMPLATES['issues'].format(
            project_name=project_name,
            total_size=total_size,
            file_count=file_count,
            binary_count=binary_count,
            main_languages=main_languages,
            files_per_dir=files_per_dir,
            avg_file_size=avg_file_size,
            large_files_count=large_files,
            detected_patterns=detected_patterns
        )


def get_prompt_generator(is_premium: bool = False) -> PromptGenerator:
    """
    Obtener una instancia del generador de prompts.
    
    Args:
        is_premium: Si el usuario tiene acceso premium
        
    Returns:
        Instancia de PromptGenerator
    """
    return PromptGenerator(is_premium=is_premium)
