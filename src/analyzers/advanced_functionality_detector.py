#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para la detección avanzada de funcionalidades en proyectos.

Este módulo analiza el código fuente para identificar funcionalidades
específicas, arquitecturas y patrones de código de forma más detallada
que el detector básico.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple, Union
from collections import Counter

from src.utils.logger import get_logger
from src.analyzers.project_scanner import ProjectScanner, get_project_scanner
from src.analyzers.functionality_detector import FunctionalityDetector, get_functionality_detector
from src.templates.common_functionalities import (
    FUNCTIONALITY_PATTERNS, DETECTION_WEIGHTS, CONFIDENCE_THRESHOLD
)
from src.templates.functionality_patterns import (
    COMMON_ARCHITECTURES, ADVANCED_FUNCTIONALITY_PATTERNS
)
from src.templates.functionality_patterns.auth import (
    AUTH_PATTERNS_ADVANCED, AUTH_FRAMEWORK_FEATURES, AUTH_SECURITY_LEVELS
)
from src.templates.functionality_patterns.database import (
    DATABASE_PATTERNS_ADVANCED, DATABASE_FRAMEWORK_TYPES
)

# Configurar logger
logger = get_logger()


class AdvancedFunctionalityDetector:
    """Detector avanzado de funcionalidades en proyectos de software."""
    
    def __init__(self, scanner: Optional[ProjectScanner] = None,
                basic_detector: Optional[FunctionalityDetector] = None):
        """
        Inicializar el detector avanzado de funcionalidades.
        
        Args:
            scanner: Escáner de proyectos opcional
            basic_detector: Detector básico de funcionalidades opcional
        """
        self.scanner = scanner or get_project_scanner()
        self.basic_detector = basic_detector or get_functionality_detector(self.scanner)
        
        # Resultados del análisis
        self.functionalities = {}
        self.architectures = {}
        self.frameworks = {}
        self.advanced_features = {}
        self.patterns = {}
        self.code_quality = {}
    
    def detect_functionalities(self, project_path: str) -> Dict[str, Any]:
        """
        Detectar funcionalidades presentes en un proyecto con análisis avanzado.
        
        Args:
            project_path: Ruta al directorio del proyecto
            
        Returns:
            Dict con funcionalidades detectadas y análisis avanzado
        """
        # Escanear el proyecto para obtener información
        project_data = self.scanner.scan_project(project_path)
        
        # Obtener resultados del detector básico primero
        basic_results = self.basic_detector.detect_functionalities(project_path)
        
        # Resetear resultados previos
        self.functionalities = basic_results.copy()
        self.architectures = {}
        self.frameworks = {}
        self.advanced_features = {}
        self.patterns = {}
        self.code_quality = {}
        
        # Realizar análisis avanzados
        self._detect_architectures(project_data)
        self._detect_frameworks(project_data)
        self._analyze_advanced_patterns(project_data)
        self._enrich_functionality_data(basic_results)
        
        # Agregar resultados avanzados
        self.functionalities['architectures'] = self.architectures
        self.functionalities['frameworks'] = self.frameworks
        self.functionalities['advanced_features'] = self.advanced_features
        self.functionalities['patterns'] = self.patterns
        self.functionalities['code_quality'] = self.code_quality
        
        # Añadir metadatos adicionales
        self.functionalities['analysis_level'] = 'advanced'
        
        return self.functionalities
    
    def _detect_architectures(self, project_data: Dict[str, Any]) -> None:
        """
        Detectar arquitecturas comunes en el proyecto.
        
        Args:
            project_data: Datos del proyecto escaneado
        """
        files = project_data.get('files', [])
        file_paths = [f.get('path', '') for f in files]
        
        # Analizar cada arquitectura definida
        for arch_name, arch_info in COMMON_ARCHITECTURES.items():
            patterns = arch_info.get('patterns', [])
            files_required = arch_info.get('files_required', [])
            confidence_threshold = arch_info.get('confidence_threshold', 0.7)
            
            # Contar coincidencias de patrones
            pattern_matches = 0
            matched_files = []
            
            for file_path in file_paths:
                for pattern in patterns:
                    if re.search(pattern, file_path, re.IGNORECASE):
                        pattern_matches += 1
                        matched_files.append(file_path)
                        break  # Contar cada archivo solo una vez
            
            # Verificar presencia de archivos requeridos
            required_matches = 0
            for req in files_required:
                if any(re.search(req, path, re.IGNORECASE) for path in file_paths):
                    required_matches += 1
            
            # Calcular confianza
            if files_required:
                required_confidence = required_matches / len(files_required)
            else:
                required_confidence = 1.0
                
            # Calcular puntuación general basada en coincidencias y archivos requeridos
            if pattern_matches > 0:
                confidence_score = min(pattern_matches / 10, 1.0) * 0.7 + required_confidence * 0.3
                confidence_percent = int(confidence_score * 100)
                
                # Guardar resultado si supera el umbral
                if confidence_score >= confidence_threshold:
                    self.architectures[arch_name] = {
                        'confidence': confidence_percent,
                        'description': arch_info.get('description', arch_name),
                        'matched_files': matched_files[:10],  # Limitar a 10 ejemplos
                        'required_matches': f"{required_matches}/{len(files_required)}"
                    }
    
    def _detect_frameworks(self, project_data: Dict[str, Any]) -> None:
        """
        Detectar frameworks y bibliotecas utilizadas en el proyecto.
        
        Args:
            project_data: Datos del proyecto escaneado
        """
        # Frameworks comunes por lenguaje
        framework_patterns = {
            'python': {
                'django': r'django',
                'flask': r'flask',
                'fastapi': r'fastapi',
                'pyramid': r'pyramid',
                'sqlalchemy': r'sqlalchemy',
                'tensorflow': r'tensorflow',
                'pytorch': r'torch',
                'pandas': r'pandas',
                'numpy': r'numpy',
                'scikit-learn': r'sklearn',
                'pytest': r'pytest',
                'celery': r'celery',
            },
            'javascript': {
                'react': r'react',
                'vue': r'vue',
                'angular': r'angular',
                'express': r'express',
                'next.js': r'next',
                'nuxt.js': r'nuxt',
                'electron': r'electron',
                'jest': r'jest',
                'mocha': r'mocha',
                'tensorflow.js': r'tensorflow',
                'jquery': r'jquery',
                'redux': r'redux',
                'graphql': r'graphql',
            },
            'typescript': {
                'react': r'react',
                'vue': r'vue',
                'angular': r'angular',
                'express': r'express',
                'next.js': r'next',
                'nuxt.js': r'nuxt',
                'nest.js': r'nest',
                'typeorm': r'typeorm',
                'prisma': r'prisma',
                'jest': r'jest',
            },
            'java': {
                'spring': r'spring',
                'hibernate': r'hibernate',
                'junit': r'junit',
                'log4j': r'log4j',
                'vertx': r'vertx',
                'jackson': r'jackson',
                'gson': r'gson',
            },
            'go': {
                'gin': r'gin',
                'echo': r'echo',
                'gorm': r'gorm',
                'chi': r'chi',
            },
            'ruby': {
                'rails': r'rails',
                'sinatra': r'sinatra',
                'rspec': r'rspec',
            },
            'php': {
                'laravel': r'laravel',
                'symfony': r'symfony',
                'wordpress': r'wordpress',
                'codeigniter': r'codeigniter',
                'phpunit': r'phpunit',
            },
            'csharp': {
                'aspnet': r'asp\.net',
                'entityframework': r'entity\s*framework',
                'xunit': r'xunit',
                'nunit': r'nunit',
            }
        }
        
        # Buscar referencias a frameworks en el código
        languages = project_data.get('languages', {})
        files = project_data.get('files', [])
        
        # Contadores para los frameworks detectados
        framework_counts = Counter()
        
        # Analizar cada archivo de código
        for file_info in files:
            if file_info.get('is_binary', True):
                continue
                
            language = file_info.get('language', '').lower()
            file_path = os.path.join(project_data.get('project_path', ''), file_info.get('path', ''))
            
            # Verificar frameworks para este lenguaje
            if language in framework_patterns:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # Buscar cada framework
                        for framework, pattern in framework_patterns[language].items():
                            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                                framework_counts[framework] += 1
                except Exception as e:
                    logger.debug(f"Error al analizar frameworks en {file_path}: {e}")
            
            # Verificar package.json para aplicaciones JavaScript/TypeScript
            if language in ['javascript', 'typescript'] and os.path.basename(file_path) == 'package.json':
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        package_data = json.load(f)
                        
                        # Buscar en dependencias
                        dependencies = {
                            **package_data.get('dependencies', {}),
                            **package_data.get('devDependencies', {})
                        }
                        
                        # Incrementar contadores basados en dependencias
                        if 'react' in dependencies:
                            framework_counts['react'] += 5
                        if 'vue' in dependencies:
                            framework_counts['vue'] += 5
                        if 'angular' in dependencies or '@angular/core' in dependencies:
                            framework_counts['angular'] += 5
                        if 'express' in dependencies:
                            framework_counts['express'] += 5
                        if 'next' in dependencies:
                            framework_counts['next.js'] += 5
                        if 'nuxt' in dependencies:
                            framework_counts['nuxt.js'] += 5
                        if '@nestjs/core' in dependencies:
                            framework_counts['nest.js'] += 5
                        if 'typeorm' in dependencies:
                            framework_counts['typeorm'] += 5
                        if '@prisma/client' in dependencies:
                            framework_counts['prisma'] += 5
                except Exception as e:
                    logger.debug(f"Error al analizar package.json en {file_path}: {e}")
            
            # Verificar requirements.txt para aplicaciones Python
            if language == 'python' and os.path.basename(file_path) in ['requirements.txt', 'Pipfile', 'poetry.lock']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        
                        # Buscar frameworks
                        if 'django' in content:
                            framework_counts['django'] += 5
                        if 'flask' in content:
                            framework_counts['flask'] += 5
                        if 'fastapi' in content:
                            framework_counts['fastapi'] += 5
                        if 'sqlalchemy' in content:
                            framework_counts['sqlalchemy'] += 5
                        if 'tensorflow' in content:
                            framework_counts['tensorflow'] += 5
                        if 'torch' in content:
                            framework_counts['pytorch'] += 5
                        if 'pandas' in content:
                            framework_counts['pandas'] += 5
                        if 'numpy' in content:
                            framework_counts['numpy'] += 5
                        if 'sklearn' in content or 'scikit-learn' in content:
                            framework_counts['scikit-learn'] += 5
                except Exception as e:
                    logger.debug(f"Error al analizar requirements en {file_path}: {e}")
        
        # Guardar frameworks detectados, si hay suficientes menciones
        for framework, count in framework_counts.items():
            if count >= 3:  # Umbral arbitrario para evitar falsos positivos
                confidence = min(count / 5, 1.0) * 100  # Máxima confianza con 5+ menciones
                
                if framework not in self.frameworks:
                    self.frameworks[framework] = {
                        'confidence': int(confidence),
                        'count': count
                    }
    
    def _analyze_advanced_patterns(self, project_data: Dict[str, Any]) -> None:
        """
        Analizar patrones avanzados en el código.
        
        Args:
            project_data: Datos del proyecto escaneado
        """
        files = project_data.get('files', [])
        
        # Inicializar resultados para cada funcionalidad avanzada
        for func_name in ADVANCED_FUNCTIONALITY_PATTERNS:
            self.advanced_features[func_name] = {
                'features': {},
                'frameworks': {},
                'patterns': {},
                'security_level': None
            }
        
        # Analizar autenticación avanzada
        self._analyze_authentication_patterns(project_data, files)
        
        # Analizar patrones de base de datos
        self._analyze_database_patterns(project_data, files)
    
    def _analyze_authentication_patterns(self, project_data: Dict[str, Any], files: List[Dict[str, Any]]) -> None:
        """
        Analizar patrones de autenticación avanzados.
        
        Args:
            project_data: Datos del proyecto
            files: Archivos del proyecto
        """
        auth_features = {}
        auth_frameworks = {}
        auth_security = []
        
        # Analizar características de autenticación
        for feature_name, patterns in AUTH_PATTERNS_ADVANCED['auth_features'].items():
            auth_features[feature_name] = {
                'present': False,
                'confidence': 0,
                'evidence': []
            }
            
            # Buscar patrones en el código
            for file_info in files:
                if file_info.get('is_binary', True):
                    continue
                    
                file_path = os.path.join(project_data.get('project_path', ''), file_info.get('path', ''))
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        for pattern in patterns:
                            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                                # Actualizar confianza
                                auth_features[feature_name]['present'] = True
                                auth_features[feature_name]['confidence'] += 10
                                
                                # Limitar confianza a 100
                                auth_features[feature_name]['confidence'] = min(
                                    auth_features[feature_name]['confidence'], 100)
                                
                                # Guardar evidencia
                                evidence = os.path.basename(file_path)
                                if evidence not in auth_features[feature_name]['evidence']:
                                    auth_features[feature_name]['evidence'].append(evidence)
                                    
                                # Identificar nivel de seguridad
                                if feature_name == 'jwt' and re.search(r'expire|exp|lifetime', content, re.IGNORECASE):
                                    auth_security.append('jwt_with_expiration')
                                if feature_name == 'jwt' and re.search(r'refresh.*token', content, re.IGNORECASE):
                                    auth_security.append('jwt_with_refresh')
                                if re.search(r'hash.*password', content, re.IGNORECASE):
                                    auth_security.append('hashed_passwords')
                                if re.search(r'salt', content, re.IGNORECASE) and re.search(r'hash', content, re.IGNORECASE):
                                    auth_security.append('hashed_with_salt')
                                if re.search(r'password\s*=', content, re.IGNORECASE) and not re.search(r'hash|encrypt|bcrypt', content, re.IGNORECASE):
                                    auth_security.append('plain_passwords')
                except Exception as e:
                    logger.debug(f"Error al analizar patrones de autenticación en {file_path}: {e}")
        
        # Detectar frameworks de autenticación específicos
        for framework, patterns in AUTH_PATTERNS_ADVANCED['frameworks'].items():
            auth_frameworks[framework] = {
                'present': False,
                'confidence': 0,
                'evidence': []
            }
            
            # Buscar patrones en el código
            for file_info in files:
                if file_info.get('is_binary', True):
                    continue
                    
                file_path = os.path.join(project_data.get('project_path', ''), file_info.get('path', ''))
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        for pattern in patterns:
                            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                                # Actualizar confianza
                                auth_frameworks[framework]['present'] = True
                                auth_frameworks[framework]['confidence'] += 20
                                
                                # Limitar confianza a 100
                                auth_frameworks[framework]['confidence'] = min(
                                    auth_frameworks[framework]['confidence'], 100)
                                
                                # Guardar evidencia
                                evidence = os.path.basename(file_path)
                                if evidence not in auth_frameworks[framework]['evidence']:
                                    auth_frameworks[framework]['evidence'].append(evidence)
                                    
                                # Añadir características típicas de este framework
                                if framework in AUTH_FRAMEWORK_FEATURES:
                                    for feature in AUTH_FRAMEWORK_FEATURES[framework]:
                                        if feature in auth_features:
                                            auth_features[feature]['confidence'] += 5
                                            auth_features[feature]['confidence'] = min(
                                                auth_features[feature]['confidence'], 100)
                except Exception as e:
                    logger.debug(f"Error al analizar frameworks de autenticación en {file_path}: {e}")
        
        # Determinar nivel de seguridad global
        security_level = self._determine_auth_security_level(auth_security)
        
        # Actualizar resultados de autenticación
        self.advanced_features['authentication']['features'] = auth_features
        self.advanced_features['authentication']['frameworks'] = auth_frameworks
        self.advanced_features['authentication']['security_level'] = security_level
    
    def _determine_auth_security_level(self, security_indicators: List[str]) -> Dict[str, Any]:
        """
        Determinar el nivel de seguridad de autenticación.
        
        Args:
            security_indicators: Lista de indicadores de seguridad detectados
            
        Returns:
            Dict con nivel de seguridad y recomendaciones
        """
        # Niveles de seguridad (de menor a mayor)
        levels = [
            'plain_passwords', 'jwt_without_expiration', 'hashed_passwords',
            'jwt_with_expiration', 'hashed_with_salt', 'jwt_with_refresh',
            'oauth', 'mfa'
        ]
        
        # Mapear niveles a categorías
        level_categories = {
            'plain_passwords': 'critical',
            'jwt_without_expiration': 'low',
            'hashed_passwords': 'medium',
            'jwt_with_expiration': 'medium',
            'hashed_with_salt': 'good',
            'jwt_with_refresh': 'good',
            'oauth': 'high',
            'mfa': 'very high'
        }
        
        # Recomendaciones según nivel
        recommendations = {
            'critical': [
                "CRÍTICO: No almacenar contraseñas en texto plano",
                "Implementar hash de contraseñas con salt (bcrypt, Argon2, PBKDF2, etc.)"
            ],
            'low': [
                "Implementar expiración de tokens JWT",
                "Considerar implementar tokens de refresco",
                "Usar salt aleatorio único para cada hash de contraseña"
            ],
            'medium': [
                "Considerar mejorar la seguridad con tokens de refresco",
                "Implementar políticas de contraseñas seguras",
                "Considerar autenticación de dos factores"
            ],
            'good': [
                "Buenas prácticas implementadas",
                "Considerar añadir autenticación de dos factores (2FA/MFA)"
            ],
            'high': [
                "Muy buen nivel de seguridad",
                "Considerar auditoría de accesos y sesiones"
            ],
            'very high': [
                "Excelente nivel de seguridad"
            ]
        }
        
        # Encontrar el nivel más bajo detectado (el más inseguro)
        lowest_level = None
        for level in levels:
            if level in security_indicators:
                lowest_level = level
                break
        
        # Si se detectó MFA u OAuth, elevar el nivel
        if 'mfa' in security_indicators:
            lowest_level = 'mfa'
        elif 'oauth' in security_indicators and lowest_level not in ['plain_passwords']:
            lowest_level = 'oauth'
        
        # Si no se detectó ningún nivel específico
        if not lowest_level:
            if any(s.startswith('jwt') for s in security_indicators):
                lowest_level = 'jwt_without_expiration'
            else:
                lowest_level = 'plain_passwords'
        
        # Obtener categoría y recomendaciones
        category = level_categories.get(lowest_level, 'unknown')
        recs = recommendations.get(category, ["Verificar implementación de seguridad"])
        
        return {
            'level': lowest_level,
            'category': category,
            'recommendations': recs,
            'indicators': security_indicators
        }
    
    def _analyze_database_patterns(self, project_data: Dict[str, Any], files: List[Dict[str, Any]]) -> None:
        """
        Analizar patrones de base de datos avanzados.
        
        Args:
            project_data: Datos del proyecto
            files: Archivos del proyecto
        """
        db_types = {}
        db_frameworks = {}
        db_operations = {}
        
        # Analizar tipos de bases de datos
        for db_type, patterns in DATABASE_PATTERNS_ADVANCED['db_types'].items():
            db_types[db_type] = {
                'present': False,
                'confidence': 0,
                'evidence': []
            }
            
            # Buscar patrones en el código
            for file_info in files:
                if file_info.get('is_binary', True):
                    continue
                    
                file_path = os.path.join(project_data.get('project_path', ''), file_info.get('path', ''))
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        for pattern in patterns:
                            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                                # Actualizar confianza
                                db_types[db_type]['present'] = True
                                db_types[db_type]['confidence'] += 15
                                
                                # Limitar confianza a 100
                                db_types[db_type]['confidence'] = min(
                                    db_types[db_type]['confidence'], 100)
                                
                                # Guardar evidencia
                                evidence = os.path.basename(file_path)
                                if evidence not in db_types[db_type]['evidence']:
                                    db_types[db_type]['evidence'].append(evidence)
                except Exception as e:
                    logger.debug(f"Error al analizar tipos de base de datos en {file_path}: {e}")
        
        # Detectar frameworks de base de datos específicos
        for framework, patterns in DATABASE_PATTERNS_ADVANCED['frameworks'].items():
            db_frameworks[framework] = {
                'present': False,
                'confidence': 0,
                'evidence': []
            }
            
            # Buscar patrones en el código
            for file_info in files:
                if file_info.get('is_binary', True):
                    continue
                    
                file_path = os.path.join(project_data.get('project_path', ''), file_info.get('path', ''))
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        for pattern in patterns:
                            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                                # Actualizar confianza
                                db_frameworks[framework]['present'] = True
                                db_frameworks[framework]['confidence'] += 20
                                
                                # Limitar confianza a 100
                                db_frameworks[framework]['confidence'] = min(
                                    db_frameworks[framework]['confidence'], 100)
                                
                                # Guardar evidencia
                                evidence = os.path.basename(file_path)
                                if evidence not in db_frameworks[framework]['evidence']:
                                    db_frameworks[framework]['evidence'].append(evidence)
                                    
                                # Asociar tipo de BD basado en el framework
                                if framework in DATABASE_FRAMEWORK_TYPES:
                                    for db_type in DATABASE_FRAMEWORK_TYPES[framework]:
                                        if db_type in db_types:
                                            db_types[db_type]['confidence'] += 10
                                            db_types[db_type]['confidence'] = min(
                                                db_types[db_type]['confidence'], 100)
                except Exception as e:
                    logger.debug(f"Error al analizar frameworks de base de datos en {file_path}: {e}")
        
        # Analizar operaciones de base de datos
        for operation, patterns in DATABASE_PATTERNS_ADVANCED['operations'].items():
            db_operations[operation] = {
                'present': False,
                'confidence': 0,
                'evidence': []
            }
            
            # Buscar patrones en el código
            for file_info in files:
                if file_info.get('is_binary', True):
                    continue
                    
                file_path = os.path.join(project_data.get('project_path', ''), file_info.get('path', ''))
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        for pattern in patterns:
                            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                                # Actualizar confianza
                                db_operations[operation]['present'] = True
                                db_operations[operation]['confidence'] += 15
                                
                                # Limitar confianza a 100
                                db_operations[operation]['confidence'] = min(
                                    db_operations[operation]['confidence'], 100)
                                
                                # Guardar evidencia
                                evidence = os.path.basename(file_path)
                                if evidence not in db_operations[operation]['evidence']:
                                    db_operations[operation]['evidence'].append(evidence)
                except Exception as e:
                    logger.debug(f"Error al analizar operaciones de base de datos en {file_path}: {e}")
                    
        # Actualizar resultados de base de datos
        self.advanced_features['database']['features'] = db_types
        self.advanced_features['database']['frameworks'] = db_frameworks
        self.advanced_features['database']['operations'] = db_operations
        
    def _enrich_functionality_data(self, basic_results: Dict[str, Any]) -> None:
        """
        Enriquecer los datos de funcionalidades básicas con información avanzada.
        
        Args:
            basic_results: Resultados del detector básico
        """
        if 'detected' not in basic_results:
            return
            
        detected = basic_results.get('detected', {})
        
        # Añadir información avanzada a cada funcionalidad detectada
        for func_name, func_data in detected.items():
            if func_data.get('present', False) and func_name in self.advanced_features:
                # Añadir detalles avanzados
                func_data['advanced'] = self.advanced_features[func_name]
    
    def get_architecture_info(self, architecture_name: str) -> Dict[str, Any]:
        """
        Obtener información detallada sobre una arquitectura específica.
        
        Args:
            architecture_name: Nombre de la arquitectura
            
        Returns:
            Dict con información detallada sobre la arquitectura
        """
        if not self.architectures or architecture_name not in self.architectures:
            return {}
            
        return self.architectures[architecture_name]
    
    def get_framework_info(self, framework_name: str) -> Dict[str, Any]:
        """
        Obtener información detallada sobre un framework específico.
        
        Args:
            framework_name: Nombre del framework
            
        Returns:
            Dict con información detallada sobre el framework
        """
        if not self.frameworks or framework_name not in self.frameworks:
            return {}
            
        return self.frameworks[framework_name]
    
    def summarize_advanced_findings(self) -> str:
        """
        Generar un resumen textual de los hallazgos avanzados.
        
        Returns:
            Texto con el resumen de hallazgos avanzados
        """
        if not self.functionalities:
            return "No se ha realizado ningún análisis avanzado."
            
        summary = []
        
        # Arquitecturas detectadas
        if self.architectures:
            summary.append("## Arquitecturas Detectadas")
            for arch_name, arch_data in self.architectures.items():
                summary.append(f"- {arch_data['description']} ({arch_data['confidence']}% de confianza)")
            summary.append("")
            
        # Frameworks detectados
        if self.frameworks:
            summary.append("## Frameworks y Bibliotecas")
            for framework, data in self.frameworks.items():
                summary.append(f"- {framework} ({data['confidence']}% de confianza)")
            summary.append("")
            
        # Características avanzadas por funcionalidad
        main_functionalities = self.functionalities.get('main_functionalities', [])
        if main_functionalities and self.advanced_features:
            summary.append("## Características Avanzadas")
            
            for func_name in main_functionalities:
                if func_name in self.advanced_features:
                    adv = self.advanced_features[func_name]
                    summary.append(f"### {func_name.capitalize()}")
                    
                    # Frameworks específicos
                    frameworks = adv.get('frameworks', {})
                    if frameworks:
                        detected = [name for name, data in frameworks.items() if data.get('confidence', 0) > 50]
                        if detected:
                            summary.append(f"**Frameworks:** {', '.join(detected)}")
                    
                    # Seguridad (solo para autenticación)
                    if func_name == 'authentication' and adv.get('security_level'):
                        sec = adv['security_level']
                        summary.append(f"**Nivel de seguridad:** {sec['category'].upper()}")
                        summary.append(f"**Recomendaciones:**")
                        for rec in sec['recommendations']:
                            summary.append(f"  - {rec}")
                    
                    # Tipos (solo para base de datos)
                    if func_name == 'database' and adv.get('features'):
                        detected = [name for name, data in adv.get('features', {}).items() 
                                   if data.get('confidence', 0) > 50]
                        if detected:
                            summary.append(f"**Tipos de BD:** {', '.join(detected)}")
                            
                        # Operaciones
                        if adv.get('operations'):
                            detected = [name for name, data in adv.get('operations', {}).items() 
                                       if data.get('confidence', 0) > 50]
                            if detected:
                                summary.append(f"**Operaciones:** {', '.join(detected)}")
                    
                    summary.append("")
        
        return "\n".join(summary)


def get_advanced_functionality_detector(scanner: Optional[ProjectScanner] = None,
                                      basic_detector: Optional[FunctionalityDetector] = None) -> AdvancedFunctionalityDetector:
    """
    Obtener una instancia del detector avanzado de funcionalidades.
    
    Args:
        scanner: Escáner de proyectos opcional
        basic_detector: Detector básico de funcionalidades opcional
        
    Returns:
        Instancia de AdvancedFunctionalityDetector
    """
    return AdvancedFunctionalityDetector(scanner=scanner, basic_detector=basic_detector)
