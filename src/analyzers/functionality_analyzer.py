#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para analizar en detalle las funcionalidades detectadas en un proyecto.

Este módulo permite analizar en profundidad cada funcionalidad detectada,
evaluando su completitud, calidad, y generando sugerencias específicas.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple, Union
from collections import defaultdict

from src.utils.logger import get_logger
from src.analyzers.project_scanner import ProjectScanner, get_project_scanner
from src.analyzers.functionality_detector import FunctionalityDetector, get_functionality_detector
from src.analyzers.advanced_functionality_detector import AdvancedFunctionalityDetector, get_advanced_functionality_detector
from src.analyzers.code_quality_analyzer import CodeQualityAnalyzer, get_code_quality_analyzer

# Configurar logger
logger = get_logger()

# Patrones de implementación para cada funcionalidad
IMPLEMENTATION_PATTERNS = {
    'authentication': {
        'essential_components': [
            {
                'name': 'autenticación básica',
                'patterns': [
                    r'login|signin|authenticate|verify.*password|check.*password',
                    r'authentication|authenticat(e|ion)'
                ],
                'weight': 1.0
            },
            {
                'name': 'gestión de sesiones',
                'patterns': [
                    r'session\.|sessionstorage|cookie|token|jwt',
                    r'isAuthenticated|currentUser|getUser'
                ],
                'weight': 0.8
            },
            {
                'name': 'gestión de usuarios',
                'patterns': [
                    r'user\.|usermodel|createuser|updateuser|finduser',
                    r'register|signup|create.*account'
                ],
                'weight': 0.8
            },
            {
                'name': 'seguridad',
                'patterns': [
                    r'hash|encrypt|bcrypt|salt|secure|protection',
                    r'verify|validate|sanitize'
                ],
                'weight': 0.7
            },
            {
                'name': 'autorización',
                'patterns': [
                    r'role|permission|authorization|access.*control',
                    r'isAdmin|hasPermission|canAccess|middleware.*auth'
                ],
                'weight': 0.6
            }
        ],
        'advanced_components': [
            {
                'name': 'autenticación de dos factores',
                'patterns': [
                    r'2fa|two.*factor|multi.*factor|otp|totp',
                    r'verification.*code|authenticator'
                ],
                'weight': 0.4
            },
            {
                'name': 'oauth/redes sociales',
                'patterns': [
                    r'oauth|openid|social.*login|facebook|google|github',
                    r'provider.*auth|strategy.*auth'
                ],
                'weight': 0.5
            },
            {
                'name': 'recuperación de contraseñas',
                'patterns': [
                    r'resetpassword|forgotpassword|recovery|reset.*link',
                    r'passwordreset|changepassword'
                ],
                'weight': 0.5
            }
        ],
        'security_checks': [
            {
                'name': 'almacenamiento seguro de contraseñas',
                'patterns': [
                    r'bcrypt|argon2|pbkdf2|scrypt|hash.*password',
                    r'salt.*password|secure.*storage'
                ],
                'importance': 'critical'
            },
            {
                'name': 'protección contra CSRF',
                'patterns': [
                    r'csrf|cross.*site|forgery|token.*validation',
                    r'samesite|csrf.*middleware'
                ],
                'importance': 'high'
            },
            {
                'name': 'protección contra XSS',
                'patterns': [
                    r'xss|cross.*script|sanitize|escape|encode',
                    r'content.*security.*policy|csp'
                ],
                'importance': 'high'
            },
            {
                'name': 'rate limiting',
                'patterns': [
                    r'rate.*limit|throttle|brute.*force|max.*attempts',
                    r'lockout|backoff|delay'
                ],
                'importance': 'medium'
            }
        ]
    },
    
    'database': {
        'essential_components': [
            {
                'name': 'conexión y configuración',
                'patterns': [
                    r'connect|connection|createconnection|db_config',
                    r'database.*url|connection.*string'
                ],
                'weight': 1.0
            },
            {
                'name': 'operaciones CRUD',
                'patterns': [
                    r'create|save|insert|add|update|delete|remove',
                    r'find.*by|get.*by|select|query'
                ],
                'weight': 0.9
            },
            {
                'name': 'modelos/esquemas',
                'patterns': [
                    r'model|schema|entity|table|collection|document',
                    r'field|column|property|relation'
                ],
                'weight': 0.7
            },
            {
                'name': 'manejo de errores',
                'patterns': [
                    r'try|catch|exception|error.*handling|database.*error',
                    r'rollback|transaction'
                ],
                'weight': 0.6
            }
        ],
        'advanced_components': [
            {
                'name': 'migraciones',
                'patterns': [
                    r'migration|migrate|seed|schema.*change|version',
                    r'upgrade|downgrade|alembic|knex|sequelize.*migration'
                ],
                'weight': 0.5
            },
            {
                'name': 'relaciones',
                'patterns': [
                    r'relation|association|join|foreign.*key|references',
                    r'one.*to.*many|many.*to.*many|belongs.*to|has.*many'
                ],
                'weight': 0.5
            },
            {
                'name': 'consultas avanzadas',
                'patterns': [
                    r'aggregate|group.*by|having|subquery|nested.*query',
                    r'sort|order.*by|limit|offset|paginate'
                ],
                'weight': 0.4
            },
            {
                'name': 'optimización',
                'patterns': [
                    r'index|optimization|cache|performance|lazy.*loading',
                    r'eager.*loading|explain|analyze'
                ],
                'weight': 0.4
            }
        ],
        'security_checks': [
            {
                'name': 'protección contra SQL injection',
                'patterns': [
                    r'prepare|statement|parameterized|sanitize|escape',
                    r'\?.*binding|\$\d+.*binding|named.*parameter'
                ],
                'importance': 'critical'
            },
            {
                'name': 'credenciales seguras',
                'patterns': [
                    r'env|environment|secret|config|variable',
                    r'vault|secret.*manager|key.*storage'
                ],
                'importance': 'critical'
            },
            {
                'name': 'validación de datos',
                'patterns': [
                    r'validate|validation|sanitize|check.*input',
                    r'filter.*input|clean.*data'
                ],
                'importance': 'high'
            }
        ]
    },
    
    'api': {
        'essential_components': [
            {
                'name': 'endpoints',
                'patterns': [
                    r'(get|post|put|delete|patch).*route|endpoint|controller',
                    r'@(get|post|put|delete|patch)|request.*mapping'
                ],
                'weight': 1.0
            },
            {
                'name': 'respuestas HTTP',
                'patterns': [
                    r'response|status|code|json|send|return.*json',
                    r'http.*response|http.*status'
                ],
                'weight': 0.9
            },
            {
                'name': 'manejo de errores',
                'patterns': [
                    r'try|catch|exception|error.*handling|api.*error',
                    r'status.*4\d\d|status.*5\d\d'
                ],
                'weight': 0.8
            },
            {
                'name': 'middleware',
                'patterns': [
                    r'middleware|interceptor|filter|handler|pipeline',
                    r'before.*action|after.*action'
                ],
                'weight': 0.7
            }
        ],
        'advanced_components': [
            {
                'name': 'validación',
                'patterns': [
                    r'validate|validation|schema|dto|input.*validation',
                    r'request.*body|request.*param|validate.*input'
                ],
                'weight': 0.5
            },
            {
                'name': 'documentación',
                'patterns': [
                    r'swagger|openapi|apispec|apidoc|jsdoc',
                    r'description|summary|parameter|response.*schema'
                ],
                'weight': 0.4
            },
            {
                'name': 'versionado',
                'patterns': [
                    r'version|v\d+|api.*version|version.*header',
                    r'content.*type.*version|accept.*version'
                ],
                'weight': 0.4
            },
            {
                'name': 'rate limiting',
                'patterns': [
                    r'rate.*limit|throttle|max.*request|limit.*request',
                    r'quota|api.*key.*limit'
                ],
                'weight': 0.4
            },
            {
                'name': 'caching',
                'patterns': [
                    r'cache|cache.*control|etag|last.*modified',
                    r'if.*modified.*since|if.*none.*match'
                ],
                'weight': 0.3
            }
        ],
        'security_checks': [
            {
                'name': 'autenticación API',
                'patterns': [
                    r'api.*key|bearer|token|jwt|oauth',
                    r'auth.*header|authorization.*header'
                ],
                'importance': 'critical'
            },
            {
                'name': 'CORS',
                'patterns': [
                    r'cors|origin|cross.*origin|allow.*origin',
                    r'preflight|options.*request'
                ],
                'importance': 'high'
            },
            {
                'name': 'validación de entrada',
                'patterns': [
                    r'validate.*input|sanitize|clean.*input|escape',
                    r'schema.*validation|request.*validation'
                ],
                'importance': 'high'
            }
        ]
    },
    
    'frontend': {
        'essential_components': [
            {
                'name': 'componentes UI',
                'patterns': [
                    r'component|view|page|template|element',
                    r'render|display|ui|interface'
                ],
                'weight': 1.0
            },
            {
                'name': 'gestión de estado',
                'patterns': [
                    r'state|store|redux|vuex|context|provider|observable',
                    r'reducer|action|dispatch|commit|mutation|useState'
                ],
                'weight': 0.8
            },
            {
                'name': 'navegación/enrutamiento',
                'patterns': [
                    r'router|route|navigation|link|redirect|history',
                    r'path|param|query|useRouter|useNavigate'
                ],
                'weight': 0.7
            },
            {
                'name': 'formularios',
                'patterns': [
                    r'form|input|field|validation|submit|onChange',
                    r'formik|reacthookform|template.*form'
                ],
                'weight': 0.6
            }
        ],
        'advanced_components': [
            {
                'name': 'gestión de peticiones',
                'patterns': [
                    r'fetch|axios|http|api|request|response',
                    r'loading|success|error|useQuery|useMutation'
                ],
                'weight': 0.5
            },
            {
                'name': 'internacionalización',
                'patterns': [
                    r'i18n|internationalization|localization|translate',
                    r'language|locale|message|dictionary'
                ],
                'weight': 0.4
            },
            {
                'name': 'animaciones',
                'patterns': [
                    r'animation|transition|transform|animate|motion',
                    r'keyframe|gsap|framer.*motion|animated'
                ],
                'weight': 0.3
            },
            {
                'name': 'testing',
                'patterns': [
                    r'test|spec|jest|cypress|enzyme|testing.*library',
                    r'mock|stub|spy|render|screen|fireEvent|userEvent'
                ],
                'weight': 0.4
            },
            {
                'name': 'accesibilidad',
                'patterns': [
                    r'accessibility|a11y|aria|role|alt|label',
                    r'keyboard|focus|screen.*reader'
                ],
                'weight': 0.4
            }
        ],
        'security_checks': [
            {
                'name': 'sanitización de datos',
                'patterns': [
                    r'sanitize|escape|xss|dangerouslySetInnerHTML',
                    r'htmlFor|innerHTML'
                ],
                'importance': 'high'
            },
            {
                'name': 'almacenamiento seguro',
                'patterns': [
                    r'localStorage|sessionStorage|cookie|secure.*storage',
                    r'httpOnly|samesite|sensitive.*data'
                ],
                'importance': 'medium'
            }
        ]
    },
    
    'tests': {
        'essential_components': [
            {
                'name': 'framework de testing',
                'patterns': [
                    r'test|spec|assert|expect|describe|it|should',
                    r'jest|mocha|jasmine|pytest|unittest|testng|junit'
                ],
                'weight': 1.0
            },
            {
                'name': 'aserciones',
                'patterns': [
                    r'assert|expect|should|equal|match|true|false',
                    r'toBe|toEqual|contains|verifyEquals'
                ],
                'weight': 0.9
            },
            {
                'name': 'estructura de tests',
                'patterns': [
                    r'describe|context|it|test|suite|scenario|feature',
                    r'beforeEach|afterEach|beforeAll|afterAll|setup|teardown'
                ],
                'weight': 0.8
            },
            {
                'name': 'mocks/stubs',
                'patterns': [
                    r'mock|stub|spy|fake|double|jest\.fn|sinon',
                    r'createMock|mockImplementation|mockResolvedValue'
                ],
                'weight': 0.7
            }
        ],
        'advanced_components': [
            {
                'name': 'testing de integración',
                'patterns': [
                    r'integration|end.*to.*end|e2e|system.*test|api.*test',
                    r'supertest|request|cypress|selenium|playwright'
                ],
                'weight': 0.5
            },
            {
                'name': 'testing UI',
                'patterns': [
                    r'render|screen|fireEvent|userEvent|click|change',
                    r'waitFor|findBy|queryBy|getBy|component.*test'
                ],
                'weight': 0.5
            },
            {
                'name': 'cobertura de código',
                'patterns': [
                    r'coverage|istanbul|nyc|cover|branch|line|statement',
                    r'lcov|codecov|sonar|coveralls'
                ],
                'weight': 0.4
            },
            {
                'name': 'test de rendimiento',
                'patterns': [
                    r'performance|benchmark|load|stress|jmeter|lighthouse',
                    r'timing|measure|profile|speed|metrics'
                ],
                'weight': 0.3
            }
        ]
    }
}

# Requerimientos mínimos para cada nivel de calidad de implementación
IMPLEMENTATION_TIERS = {
    'básico': 0.4,  # 40% de componentes esenciales
    'adecuado': 0.7,  # 70% de componentes esenciales
    'completo': 0.9,  # 90% de componentes esenciales + algunos avanzados
    'avanzado': 1.2   # 100% de componentes esenciales + muchos avanzados
}

class FunctionalityAnalyzer:
    """Analizador profundo de funcionalidades en proyectos de software."""
    
    def __init__(
        self, 
        scanner: Optional[ProjectScanner] = None,
        functionality_detector: Optional[AdvancedFunctionalityDetector] = None,
        code_quality_analyzer: Optional[CodeQualityAnalyzer] = None
    ):
        """
        Inicializar analizador de funcionalidades.
        
        Args:
            scanner: Escáner de proyectos opcional
            functionality_detector: Detector avanzado de funcionalidades opcional
            code_quality_analyzer: Analizador de calidad de código opcional
        """
        self.scanner = scanner or get_project_scanner()
        self.functionality_detector = functionality_detector or get_advanced_functionality_detector(scanner=self.scanner)
        self.code_quality_analyzer = code_quality_analyzer or get_code_quality_analyzer(scanner=self.scanner)
        
        # Resultados del análisis
        self.functionality_analysis = {}
        self.quality_analysis = {}
        self.completeness_scores = {}
        self.security_analysis = {}
        self.missing_components = {}
        self.recommendations = {}
    
    def analyze_functionality(self, project_path: str, functionality_name: str) -> Dict[str, Any]:
        """
        Analizar en profundidad una funcionalidad específica.
        
        Args:
            project_path: Ruta al directorio del proyecto
            functionality_name: Nombre de la funcionalidad a analizar
            
        Returns:
            Dict con el análisis detallado de la funcionalidad
        """
        # Verificar que la funcionalidad es compatible con el análisis
        if functionality_name not in IMPLEMENTATION_PATTERNS:
            return {
                'error': f"La funcionalidad '{functionality_name}' no está soportada para análisis profundo",
                'supported_functionalities': list(IMPLEMENTATION_PATTERNS.keys())
            }
            
        # Obtener información básica de la funcionalidad
        functionality_data = self.functionality_detector.detect_functionalities(project_path)
        detected = functionality_data.get('detected', {}).get(functionality_name, {})
        
        if not detected.get('present', False):
            return {
                'error': f"No se detectó la funcionalidad '{functionality_name}' en el proyecto",
                'suggestion': "Ejecute primero el comando de detección de funcionalidades"
            }
        
        # Escanear el proyecto para obtener información
        project_data = self.scanner.scan_project(project_path)
        
        # Analizar implementación de componentes
        implementation_analysis = self._analyze_implementation(
            project_data, 
            functionality_name, 
            detected.get('evidence', {})
        )
        
        # Analizar calidad de código específico para esta funcionalidad
        quality_analysis = self._analyze_code_quality(
            project_data, 
            functionality_name, 
            implementation_analysis.get('files', [])
        )
        
        # Analizar seguridad si aplica
        security_analysis = self._analyze_security(
            project_data,
            functionality_name,
            implementation_analysis.get('files', [])
        )
        
        # Identificar componentes faltantes
        missing_components = self._identify_missing_components(implementation_analysis)
        
        # Generar recomendaciones específicas
        recommendations = self._generate_recommendations(
            functionality_name, 
            implementation_analysis,
            quality_analysis,
            security_analysis,
            missing_components
        )
        
        # Determinar nivel de completitud
        completeness_level = self._determine_completeness(
            functionality_name, 
            implementation_analysis,
            security_analysis
        )
        
        # Guardar resultados
        self.functionality_analysis = implementation_analysis
        self.quality_analysis = quality_analysis
        self.security_analysis = security_analysis
        self.missing_components = missing_components
        self.recommendations = recommendations
        self.completeness_scores = completeness_level
        
        # Construir resultado
        return {
            'functionality': functionality_name,
            'implementation': implementation_analysis,
            'quality': quality_analysis,
            'security': security_analysis,
            'missing_components': missing_components,
            'recommendations': recommendations,
            'completeness': completeness_level,
            'project_path': project_path
        }
    
    def _analyze_implementation(
        self, 
        project_data: Dict[str, Any], 
        functionality_name: str,
        evidence: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Analizar implementación de componentes para una funcionalidad.
        
        Args:
            project_data: Datos del proyecto escaneado
            functionality_name: Nombre de la funcionalidad
            evidence: Evidencia recopilada por el detector
            
        Returns:
            Dict con análisis de implementación
        """
        # Obtener patrones para esta funcionalidad
        patterns = IMPLEMENTATION_PATTERNS.get(functionality_name, {})
        essential_components = patterns.get('essential_components', [])
        advanced_components = patterns.get('advanced_components', [])
        
        # Obtener archivos relevantes
        files = self._get_relevant_files(project_data, functionality_name, evidence)
        
        # Resultados para cada componente
        component_results = {
            'essential': {},
            'advanced': {}
        }
        
        # Analizar componentes esenciales
        for component in essential_components:
            component_name = component.get('name', '')
            component_patterns = component.get('patterns', [])
            component_weight = component.get('weight', 1.0)
            
            matches_found = self._find_component_matches(files, component_patterns)
            
            component_results['essential'][component_name] = {
                'present': len(matches_found) > 0,
                'confidence': min(100, len(matches_found) * 20),  # Max 100%
                'importance': component_weight,
                'matches': matches_found[:5]  # Limitar a 5 ejemplos
            }
            
        # Analizar componentes avanzados
        for component in advanced_components:
            component_name = component.get('name', '')
            component_patterns = component.get('patterns', [])
            component_weight = component.get('weight', 0.5)
            
            matches_found = self._find_component_matches(files, component_patterns)
            
            component_results['advanced'][component_name] = {
                'present': len(matches_found) > 0,
                'confidence': min(100, len(matches_found) * 20),  # Max 100%
                'importance': component_weight,
                'matches': matches_found[:5]  # Limitar a 5 ejemplos
            }
            
        # Calcular puntuación de implementación
        implementation_score = self._calculate_implementation_score(component_results)
            
        return {
            'components': component_results,
            'score': implementation_score,
            'files': files
        }
    
    def _get_relevant_files(
        self, 
        project_data: Dict[str, Any], 
        functionality_name: str,
        evidence: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Obtener archivos relevantes para una funcionalidad.
        
        Args:
            project_data: Datos del proyecto escaneado
            functionality_name: Nombre de la funcionalidad
            evidence: Evidencia recopilada por el detector
            
        Returns:
            Lista de archivos relevantes
        """
        files = project_data.get('files', [])
        evidence_files = evidence.get('files', [])
        
        # Si no hay archivos de evidencia, devolver todos los archivos con código
        if not evidence_files:
            return [f for f in files if not f.get('is_binary', True)]
        
        # Obtener nombres base de archivos de evidencia
        evidence_basenames = set()
        evidence_dirs = set()
        for file_path in evidence_files:
            basename = os.path.basename(file_path)
            evidence_basenames.add(basename)
            
            # También guardar directorios que pueden contener código relacionado
            dirname = os.path.dirname(file_path)
            if dirname:
                evidence_dirs.add(dirname)
        
        # Filtrar archivos relevantes
        relevant_files = []
        for file_info in files:
            if file_info.get('is_binary', True) or not file_info.get('language'):
                continue
                
            file_path = file_info.get('path', '')
            basename = os.path.basename(file_path)
            dirname = os.path.dirname(file_path)
            
            # Incluir archivos que:
            # 1. Son parte de la evidencia directa
            # 2. Están en directorios de evidencia
            # 3. Tienen nombres similares a archivos de evidencia
            if file_path in evidence_files or dirname in evidence_dirs or basename in evidence_basenames:
                # Añadir la ruta absoluta para análisis posterior
                file_info['absolute_path'] = os.path.join(project_data.get('project_path', ''), file_path)
                relevant_files.append(file_info)
        
        return relevant_files
    
    def _find_component_matches(self, files: List[Dict[str, Any]], patterns: List[str]) -> List[Dict[str, Any]]:
        """
        Encontrar coincidencias de componentes en archivos.
        
        Args:
            files: Lista de archivos relevantes
            patterns: Patrones a buscar
            
        Returns:
            Lista de coincidencias encontradas
        """
        matches = []
        
        for file_info in files:
            absolute_path = file_info.get('absolute_path')
            if not absolute_path or not os.path.isfile(absolute_path):
                continue
                
            try:
                with open(absolute_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Buscar cada patrón
                    for pattern in patterns:
                        for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
                            # Extraer contexto limitado
                            match_text = match.group(0)[:50] + ('...' if len(match.group(0)) > 50 else '')
                            
                            # Calcular número de línea
                            line_number = content[:match.start()].count('\n') + 1
                            
                            # Añadir coincidencia
                            matches.append({
                                'file': file_info.get('path', ''),
                                'line': line_number,
                                'context': match_text
                            })
                    
            except Exception as e:
                logger.debug(f"Error al buscar componentes en {absolute_path}: {e}")
        
        return matches
    
    def _calculate_implementation_score(self, component_results: Dict[str, Dict[str, Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Calcular puntuación de implementación basada en componentes.
        
        Args:
            component_results: Resultados de análisis de componentes
            
        Returns:
            Dict con puntuación y nivel de implementación
        """
        # Contar componentes esenciales presentes e importantes
        essential_components = component_results.get('essential', {})
        essential_count = len(essential_components)
        essential_present = sum(1 for c in essential_components.values() if c.get('present', False))
        
        # Ponderación por importancia para componentes esenciales
        essential_weighted_score = sum(
            c.get('importance', 1.0) for name, c in essential_components.items() 
            if c.get('present', False)
        )
        
        # Total de pesos de componentes esenciales
        essential_total_weight = sum(c.get('importance', 1.0) for c in essential_components.values())
        
        # Contar componentes avanzados presentes
        advanced_components = component_results.get('advanced', {})
        advanced_count = len(advanced_components)
        advanced_present = sum(1 for c in advanced_components.values() if c.get('present', False))
        
        # Ponderación por importancia para componentes avanzados
        advanced_weighted_score = sum(
            c.get('importance', 0.5) for name, c in advanced_components.items() 
            if c.get('present', False)
        )
        
        # Total de pesos de componentes avanzados
        advanced_total_weight = sum(c.get('importance', 0.5) for c in advanced_components.values())
        
        # Calcular puntuación normalizada (0-100)
        if essential_total_weight > 0:
            essential_score = (essential_weighted_score / essential_total_weight) * 100
        else:
            essential_score = 0
            
        if advanced_total_weight > 0:
            advanced_score = (advanced_weighted_score / advanced_total_weight) * 100
        else:
            advanced_score = 0
            
        # La puntuación total da más peso a los componentes esenciales
        total_score = (essential_score * 0.7) + (advanced_score * 0.3)
        
        # Determinar nivel de implementación
        implementation_ratio = essential_weighted_score / essential_total_weight if essential_total_weight > 0 else 0
        advanced_ratio = advanced_weighted_score / advanced_total_weight if advanced_total_weight > 0 else 0
        
        combined_score = implementation_ratio + (advanced_ratio * 0.5)
        
        # Determinar nivel según umbrales
        if combined_score >= IMPLEMENTATION_TIERS['avanzado']:
            level = 'avanzado'
        elif combined_score >= IMPLEMENTATION_TIERS['completo']:
            level = 'completo'
        elif combined_score >= IMPLEMENTATION_TIERS['adecuado']:
            level = 'adecuado'
        elif combined_score >= IMPLEMENTATION_TIERS['básico']:
            level = 'básico'
        else:
            level = 'incompleto'
            
        return {
            'essential': {
                'total': essential_count,
                'present': essential_present,
                'percentage': round(essential_score, 1)
            },
            'advanced': {
                'total': advanced_count,
                'present': advanced_present,
                'percentage': round(advanced_score, 1)
            },
            'total_score': round(total_score, 1),
            'level': level
        }
    
    def _analyze_code_quality(
        self, 
        project_data: Dict[str, Any], 
        functionality_name: str,
        relevant_files: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analizar calidad de código específico para una funcionalidad.
        
        Args:
            project_data: Datos del proyecto escaneado
            functionality_name: Nombre de la funcionalidad
            relevant_files: Archivos relevantes para la funcionalidad
            
        Returns:
            Dict con análisis de calidad específico
        """
        # Si no hay archivos relevantes, devolver vacío
        if not relevant_files:
            return {
                'score': 0,
                'issues': {'critical': 0, 'warnings': 0, 'info': 0, 'total': 0},
                'specific_issues': []
            }
            
        # Crear un subconjunto de project_data con solo los archivos relevantes
        subset_project_data = project_data.copy()
        subset_project_data['files'] = relevant_files
        
        # Ejecutar análisis de calidad
        quality_results = self.code_quality_analyzer.analyze_code_quality(project_data['project_path'])
        
        # Filtrar code smells solo para archivos relevantes
        relevant_paths = set(file.get('path', '') for file in relevant_files)
        
        filtered_code_smells = []
        for smell_name, smell_data in quality_results.get('code_smells', {}).items():
            relevant_occurrences = [
                occurrence for occurrence in smell_data.get('occurrences', [])
                if occurrence.get('file', '') in relevant_paths
            ]
            
            if relevant_occurrences:
                filtered_code_smells.append({
                    'type': smell_name,
                    'description': smell_data.get('description', ''),
                    'severity': smell_data.get('severity', 'info'),
                    'count': len(relevant_occurrences),
                    'examples': relevant_occurrences[:3]  # Limitar a 3 ejemplos
                })
                
        # Contar problemas por severidad
        issue_counts = {
            'critical': sum(1 for issue in filtered_code_smells if issue['severity'] == 'critical'),
            'warnings': sum(1 for issue in filtered_code_smells if issue['severity'] == 'warning'),
            'info': sum(1 for issue in filtered_code_smells if issue['severity'] == 'info')
        }
        issue_counts['total'] = issue_counts['critical'] + issue_counts['warnings'] + issue_counts['info']
        
        # Calcular puntuación de calidad basada en densidad de problemas
        if len(relevant_files) > 0:
            issue_density = issue_counts['total'] / len(relevant_files)
            
            # Mayor densidad = menor puntuación
            if issue_density == 0:
                quality_score = 100
            elif issue_density < 0.5:
                quality_score = 90
            elif issue_density < 1:
                quality_score = 80
            elif issue_density < 2:
                quality_score = 70
            elif issue_density < 3:
                quality_score = 60
            else:
                quality_score = max(30, 100 - (issue_density * 10))
                
            # Ajustar por problemas críticos
            critical_penalty = min(40, issue_counts['critical'] * 10)
            quality_score = max(0, quality_score - critical_penalty)
        else:
            quality_score = 0
            
        return {
            'score': round(quality_score, 1),
            'issues': issue_counts,
            'specific_issues': filtered_code_smells
        }
    
    def _analyze_security(
        self, 
        project_data: Dict[str, Any], 
        functionality_name: str,
        relevant_files: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analizar aspectos de seguridad para una funcionalidad.
        
        Args:
            project_data: Datos del proyecto escaneado
            functionality_name: Nombre de la funcionalidad
            relevant_files: Archivos relevantes para la funcionalidad
            
        Returns:
            Dict con análisis de seguridad
        """
        # Verificar si la funcionalidad tiene checks de seguridad definidos
        security_checks = IMPLEMENTATION_PATTERNS.get(functionality_name, {}).get('security_checks', [])
        
        if not security_checks or not relevant_files:
            return {
                'score': None,
                'checks': [],
                'warnings': [],
                'applicable': False
            }
            
        # Resolver rutas absolutas
        for file in relevant_files:
            if 'absolute_path' not in file:
                file['absolute_path'] = os.path.join(project_data.get('project_path', ''), file.get('path', ''))
                
        # Resultados para cada check de seguridad
        security_results = []
        
        for check in security_checks:
            check_name = check.get('name', '')
            check_patterns = check.get('patterns', [])
            check_importance = check.get('importance', 'medium')
            
            # Buscar patrones de seguridad
            matches_found = self._find_component_matches(relevant_files, check_patterns)
            
            security_results.append({
                'name': check_name,
                'implemented': len(matches_found) > 0,
                'importance': check_importance,
                'matches': matches_found[:3]  # Limitar a 3 ejemplos
            })
            
        # Preparar advertencias para checks críticos/importantes no implementados
        security_warnings = []
        for result in security_results:
            if not result.get('implemented', False) and result.get('importance') in ['critical', 'high']:
                security_warnings.append({
                    'check': result.get('name', ''),
                    'importance': result.get('importance', ''),
                    'message': f"No se detectó implementación de '{result.get('name', '')}', lo cual es {result.get('importance', '')} para esta funcionalidad."
                })
                
        # Calcular puntuación de seguridad
        implemented = sum(1 for r in security_results if r.get('implemented', False))
        total = len(security_results)
        
        # Ponderar por importancia
        importance_weights = {'critical': 3, 'high': 2, 'medium': 1, 'low': 0.5}
        weighted_score = sum(
            importance_weights.get(r.get('importance'), 1) for r in security_results if r.get('implemented', False)
        )
        weighted_total = sum(
            importance_weights.get(r.get('importance'), 1) for r in security_results
        )
        
        if weighted_total > 0:
            security_score = (weighted_score / weighted_total) * 100
        else:
            security_score = 0
            
        return {
            'score': round(security_score, 1),
            'checks': security_results,
            'warnings': security_warnings,
            'applicable': True
        }
    
    def _identify_missing_components(self, implementation_analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Identificar componentes faltantes en la implementación.
        
        Args:
            implementation_analysis: Análisis de implementación
            
        Returns:
            Dict con componentes faltantes
        """
        missing = {
            'essential': [],
            'advanced': []
        }
        
        # Identificar componentes esenciales faltantes
        essential_components = implementation_analysis.get('components', {}).get('essential', {})
        for name, component in essential_components.items():
            if not component.get('present', False) and component.get('importance', 0) >= 0.7:
                missing['essential'].append(name)
                
        # Identificar componentes avanzados importantes faltantes
        advanced_components = implementation_analysis.get('components', {}).get('advanced', {})
        for name, component in advanced_components.items():
            if not component.get('present', False) and component.get('importance', 0) >= 0.5:
                missing['advanced'].append(name)
                
        return missing
    
    def _generate_recommendations(
        self, 
        functionality_name: str,
        implementation_analysis: Dict[str, Any],
        quality_analysis: Dict[str, Any],
        security_analysis: Dict[str, Any],
        missing_components: Dict[str, List[str]]
    ) -> List[Dict[str, str]]:
        """
        Generar recomendaciones específicas basadas en el análisis.
        
        Args:
            functionality_name: Nombre de la funcionalidad
            implementation_analysis: Análisis de implementación
            quality_analysis: Análisis de calidad
            security_analysis: Análisis de seguridad
            missing_components: Componentes faltantes
            
        Returns:
            Lista de recomendaciones
        """
        recommendations = []
        
        # Recomendaciones basadas en componentes faltantes esenciales
        for component in missing_components.get('essential', []):
            recommendations.append({
                'type': 'completeness',
                'priority': 'alta',
                'title': f"Implementar {component}",
                'description': f"Este es un componente esencial para la funcionalidad de {functionality_name}"
            })
            
        # Recomendaciones basadas en componentes avanzados importantes
        for component in missing_components.get('advanced', [])[:2]:  # Limitar a 2
            recommendations.append({
                'type': 'enhancement',
                'priority': 'media',
                'title': f"Considerar implementar {component}",
                'description': f"Mejoraría la funcionalidad de {functionality_name} añadiendo características avanzadas"
            })
            
        # Recomendaciones de seguridad
        for warning in security_analysis.get('warnings', []):
            priority = 'alta' if warning.get('importance') == 'critical' else 'media'
            recommendations.append({
                'type': 'security',
                'priority': priority,
                'title': f"Implementar {warning.get('check', '')}",
                'description': warning.get('message', '')
            })
            
        # Recomendaciones de calidad
        critical_issues = [issue for issue in quality_analysis.get('specific_issues', []) 
                         if issue.get('severity') == 'critical']
                         
        for issue in critical_issues[:2]:  # Limitar a 2 críticos
            recommendations.append({
                'type': 'quality',
                'priority': 'alta',
                'title': f"Resolver problemas de {issue.get('description', '').lower()}",
                'description': f"Se encontraron {issue.get('count', 0)} instancias en el código de {functionality_name}"
            })
            
        # Si hay muchas advertencias, añadir recomendación general
        warning_count = quality_analysis.get('issues', {}).get('warnings', 0)
        if warning_count >= 5:
            recommendations.append({
                'type': 'quality',
                'priority': 'media',
                'title': f"Resolver {warning_count} advertencias de calidad de código",
                'description': f"Mejorar la calidad general del código para la funcionalidad de {functionality_name}"
            })
            
        # Si el nivel es incompleto pero tiene algo implementado, sugerir completar
        if implementation_analysis.get('score', {}).get('level') == 'incompleto' and \
           implementation_analysis.get('score', {}).get('essential', {}).get('present', 0) > 0:
            recommendations.append({
                'type': 'completeness',
                'priority': 'alta',
                'title': f"Completar implementación básica de {functionality_name}",
                'description': f"La implementación actual es parcial y no cumple con los requisitos mínimos"
            })
            
        return recommendations
    
    def _determine_completeness(
        self, 
        functionality_name: str,
        implementation_analysis: Dict[str, Any],
        security_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determinar el nivel de completitud de la funcionalidad.
        
        Args:
            functionality_name: Nombre de la funcionalidad
            implementation_analysis: Análisis de implementación
            security_analysis: Análisis de seguridad
            
        Returns:
            Dict con nivel de completitud y justificación
        """
        # Obtener nivel de implementación
        implementation_level = implementation_analysis.get('score', {}).get('level', 'incompleto')
        implementation_score = implementation_analysis.get('score', {}).get('total_score', 0)
        
        # Verificar seguridad si aplica
        has_security_issues = False
        if security_analysis.get('applicable', False):
            security_score = security_analysis.get('score', 0)
            
            # Verificar warnings críticos
            critical_warnings = [w for w in security_analysis.get('warnings', []) 
                              if w.get('importance') == 'critical']
                              
            has_security_issues = len(critical_warnings) > 0 or security_score < 50
        
        # Determinar nivel final
        if implementation_level == 'incompleto':
            completeness_level = 'incompleto'
            justification = "Faltan componentes esenciales para esta funcionalidad"
            
        elif implementation_level == 'básico':
            if has_security_issues:
                completeness_level = 'inseguro'
                justification = "Implementación básica con problemas de seguridad críticos"
            else:
                completeness_level = 'mínimo'
                justification = "Implementación mínima funcional"
                
        elif implementation_level == 'adecuado':
            if has_security_issues:
                completeness_level = 'parcial'
                justification = "Buena implementación pero con problemas de seguridad"
            else:
                completeness_level = 'adecuado'
                justification = "Implementación adecuada para casos de uso comunes"
                
        elif implementation_level == 'completo':
            if has_security_issues:
                completeness_level = 'sustancial'
                justification = "Implementación completa pero con consideraciones de seguridad"
            else:
                completeness_level = 'completo'
                justification = "Implementación completa y segura"
                
        elif implementation_level == 'avanzado':
            if has_security_issues:
                completeness_level = 'avanzado-inseguro'
                justification = "Implementación avanzada pero con vulnerabilidades"
            else:
                completeness_level = 'avanzado'
                justification = "Implementación avanzada y segura"
                
        else:
            completeness_level = 'desconocido'
            justification = "No se pudo determinar el nivel de completitud"
            
        return {
            'level': completeness_level,
            'implementation_score': implementation_score,
            'justification': justification,
            'has_security_issues': has_security_issues
        }
    
    def generate_analysis_report(self, functionality_name: str) -> str:
        """
        Generar un informe de texto sobre el análisis de la funcionalidad.
        
        Args:
            functionality_name: Nombre de la funcionalidad
            
        Returns:
            Informe en formato texto
        """
        if not self.functionality_analysis:
            return "No se ha realizado ningún análisis de funcionalidad."
        
        # Convertir a formato markdown
        report = []
        report.append(f"# Análisis de Funcionalidad: {functionality_name.capitalize()}")
        
        # Sección de completitud
        completeness = self.completeness_scores
        report.append("## Nivel de Completitud")
        report.append(f"**Nivel**: {completeness.get('level', 'desconocido').capitalize()}")
        report.append(f"**Puntuación**: {completeness.get('implementation_score', 0)}/100")
        report.append(f"**Justificación**: {completeness.get('justification', '')}")
        report.append("")
        
        # Sección de implementación
        implementation = self.functionality_analysis
        report.append("## Implementación")
        
        # Componentes esenciales
        essential = implementation.get('components', {}).get('essential', {})
        if essential:
            report.append("### Componentes Esenciales")
            for name, component in essential.items():
                status = "✅" if component.get('present', False) else "❌"
                report.append(f"- {status} **{name}**")
            report.append("")
        
        # Componentes avanzados
        advanced = implementation.get('components', {}).get('advanced', {})
        if advanced:
            report.append("### Componentes Avanzados")
            for name, component in advanced.items():
                status = "✅" if component.get('present', False) else "❌"
                report.append(f"- {status} **{name}**")
            report.append("")
        
        # Sección de seguridad si aplica
        security = self.security_analysis
        if security.get('applicable', False):
            report.append("## Seguridad")
            if security.get('warnings', []):
                report.append("### Advertencias de Seguridad")
                for warning in security.get('warnings', []):
                    importance = warning.get('importance', '')
                    icon = "🔴" if importance == 'critical' else "🟠"
                    report.append(f"- {icon} **{warning.get('check', '')}**: {warning.get('message', '')}")
                report.append("")
        
        # Recomendaciones
        recommendations = self.recommendations
        if recommendations:
            report.append("## Recomendaciones")
            
            high_priority = [r for r in recommendations if r.get('priority') == 'alta']
            if high_priority:
                report.append("### Prioridad Alta")
                for rec in high_priority:
                    report.append(f"- **{rec.get('title', '')}**: {rec.get('description', '')}")
                report.append("")
                
            medium_priority = [r for r in recommendations if r.get('priority') == 'media']
            if medium_priority:
                report.append("### Prioridad Media")
                for rec in medium_priority:
                    report.append(f"- **{rec.get('title', '')}**: {rec.get('description', '')}")
                report.append("")
        
        return "\n".join(report)


def get_functionality_analyzer(
    scanner: Optional[ProjectScanner] = None,
    functionality_detector: Optional[AdvancedFunctionalityDetector] = None,
    code_quality_analyzer: Optional[CodeQualityAnalyzer] = None
) -> FunctionalityAnalyzer:
    """
    Obtener una instancia del analizador de funcionalidades.
    
    Args:
        scanner: Escáner de proyectos opcional
        functionality_detector: Detector avanzado de funcionalidades opcional
        code_quality_analyzer: Analizador de calidad de código opcional
        
    Returns:
        Instancia de FunctionalityAnalyzer
    """
    return FunctionalityAnalyzer(
        scanner=scanner,
        functionality_detector=functionality_detector,
        code_quality_analyzer=code_quality_analyzer
    )
