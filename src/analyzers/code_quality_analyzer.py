#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para analizar la calidad del código en proyectos.

Este módulo permite la detección de problemas comunes de calidad de código,
buenas prácticas y métricas de calidad generales.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple, Union
from collections import defaultdict

from src.utils.logger import get_logger
from src.analyzers.project_scanner import ProjectScanner, get_project_scanner

# Configurar logger
logger = get_logger()

# Patrones de código para detectar posibles problemas
CODE_SMELLS_PATTERNS = {
    'long_methods': {
        'description': 'Métodos o funciones demasiado largos',
        'patterns': [
            r'(def|function)\s+\w+\s*\([^)]*\)[^{]*\{[^}]{500,}\}',  # JavaScript/TypeScript/Java
            r'def\s+\w+\s*\([^)]*\):[^\n]{0,100}(\n[ \t]+[^\n]+){30,}',  # Python
            r'(public|private|protected|internal|\s+)?\s+\w+\s+\w+\s*\([^)]*\)[^{]*\{[^}]{500,}\}'  # C#/Java
        ],
        'severity': 'warning',
        'recommendations': [
            'Dividir en funciones más pequeñas',
            'Extraer lógica común a funciones auxiliares',
            'Utilizar el principio de responsabilidad única'
        ]
    },
    'magic_numbers': {
        'description': 'Uso de números mágicos en el código',
        'patterns': [
            r'[^_a-zA-Z0-9][-+]?[0-9]{3,}[^_a-zA-Z0-9]',  # Números de 3+ dígitos
            r'[^_a-zA-Z0-9][-+]?[0-9]+\.[0-9]+[^_a-zA-Z0-9]'  # Números decimales
        ],
        'exclude_patterns': [
            r'(0|1|-1)',  # Excluir números comunes
            r'[\'"].*[0-9].*[\'"]',  # Excluir números en strings
            r'\/\*.*?[0-9].*?\*\/',  # Excluir números en comentarios multilínea
            r'\/\/.*?[0-9].*?$',  # Excluir números en comentarios de línea
            r'#.*?[0-9].*?$',  # Excluir números en comentarios Python
            r'^\s*(import|from)\s',  # Excluir import statements
            r'version\s*[:=]\s*[\'"][0-9\.]+[\'"]',  # Excluir versiones
            r'(port|PORT)\s*[:=]\s*[0-9]+'  # Excluir puertos
        ],
        'severity': 'info',
        'recommendations': [
            'Extraer números a constantes con nombres significativos',
            'Utilizar enumeraciones para conjuntos de valores relacionados'
        ]
    },
    'deeply_nested': {
        'description': 'Código con múltiples niveles de anidamiento',
        'patterns': [
            r'if\s*\(.*?\)\s*\{[^{}]*\{[^{}]*\{[^{}]*\{',  # 4+ niveles en JS/TS/Java
            r'if\s+.*?:\s*\n[ \t]+if\s+.*?:\s*\n[ \t]+[ \t]+if\s+.*?:\s*\n[ \t]+[ \t]+[ \t]+if'  # 4+ niveles en Python
        ],
        'severity': 'warning',
        'recommendations': [
            'Extraer lógica a funciones separadas',
            'Utilizar cláusulas de guarda para salir temprano de funciones',
            'Combinar condiciones relacionadas',
            'Considerar refactorizar usando el patrón estrategia'
        ]
    },
    'commented_code': {
        'description': 'Código comentado',
        'patterns': [
            r'\/\/\s*(if|for|while|switch|function|class|def|import|return)',
            r'#\s*(if|for|while|def|class|import|return)',
            r'\/\*\s*(if|for|while|switch|function|class|def|import)[^*]*\*\/'
        ],
        'severity': 'info',
        'recommendations': [
            'Eliminar código muerto',
            'Si es necesario, documentar por qué se deshabilitó',
            'Utilizar control de versiones en lugar de conservar código comentado'
        ]
    },
    'todos': {
        'description': 'TODOs pendientes',
        'patterns': [
            r'\/\/\s*TODO',
            r'#\s*TODO',
            r'\/\*\s*TODO',
            r'<!--\s*TODO'
        ],
        'severity': 'info',
        'recommendations': [
            'Convertir en tareas en un sistema de seguimiento',
            'Priorizar y planificar la implementación',
            'Documentar el propósito y requisitos'
        ]
    },
    'hardcoded_credentials': {
        'description': 'Credenciales hardcodeadas',
        'patterns': [
            r'(password|passwd|pwd|secret|api_?key)\s*[:=]\s*[\'"]((?!\s*\$).{5,})[\'"]',
            r'(username|user|login)\s*[:=]\s*[\'"](?!admin|root|user|guest|test)[^\'"]{3,}[\'"]',
            r'Bearer\s+[A-Za-z0-9\-_]{10,}',
            r'[A-Za-z0-9\-_]{30,}'  # Posibles tokens largos
        ],
        'severity': 'critical',
        'recommendations': [
            'Utilizar variables de entorno',
            'Implementar un sistema de gestión de secretos',
            'Nunca incluir credenciales en control de versiones'
        ]
    },
    'empty_catch': {
        'description': 'Bloques catch vacíos',
        'patterns': [
            r'catch\s*\([^)]*\)\s*{\s*}',  # JavaScript/Java/C#
            r'except\s+\w+:(\s*pass|\s*#|$)'  # Python
        ],
        'severity': 'warning',
        'recommendations': [
            'Registrar errores en logs',
            'Manejar excepciones específicamente',
            'Si se ignora intencionalmente, documentar razón'
        ]
    },
    'large_classes': {
        'description': 'Clases demasiado grandes',
        'patterns': [
            r'(class|interface)\s+\w+[^{]*\{[^}]{3000,}\}'  # Clases grandes en JS/TS/Java
        ],
        'severity': 'warning',
        'recommendations': [
            'Dividir en clases más pequeñas',
            'Extraer funcionalidades a clases auxiliares',
            'Aplicar principios SOLID'
        ]
    }
}

# Patrones de buenas prácticas por lenguaje
BEST_PRACTICES_PATTERNS = {
    'python': {
        'docstrings': {
            'description': 'Uso de docstrings en funciones y clases',
            'patterns': [
                r'def\s+\w+\s*\([^)]*\):\s*[\'"]{3}',
                r'class\s+\w+[^:]*:\s*[\'"]{3}'
            ],
            'severity': 'info',
            'recommendations': [
                'Documentar funciones con docstrings',
                'Incluir parámetros y valores de retorno',
                'Añadir ejemplos cuando sea apropiado'
            ]
        },
        'type_hints': {
            'description': 'Uso de type hints',
            'patterns': [
                r'def\s+\w+\s*\([^:)]*:\s*[A-Za-z][A-Za-z0-9_]*[^)]*\)',
                r'def\s+\w+\s*\([^)]*\)\s*->\s*[A-Za-z][A-Za-z0-9_]*'
            ],
            'severity': 'info',
            'recommendations': [
                'Usar type hints para mejorar la documentación',
                'Facilitar la detección temprana de errores',
                'Mejorar el soporte de IDEs'
            ]
        },
        'context_managers': {
            'description': 'Uso de context managers para recursos',
            'patterns': [
                r'with\s+[^:]+:'
            ],
            'severity': 'info',
            'recommendations': [
                'Usar context managers (with) para archivos y recursos',
                'Implementar __enter__ y __exit__ en clases propias'
            ]
        }
    },
    'javascript': {
        'async_await': {
            'description': 'Uso de async/await en lugar de callbacks',
            'patterns': [
                r'async\s+function',
                r'const\s+\w+\s*=\s*async\s*\(',
                r'await\s+'
            ],
            'severity': 'info',
            'recommendations': [
                'Preferir async/await sobre callbacks anidados',
                'Manejar errores con try/catch',
                'Realizar operaciones asíncronas en paralelo cuando sea posible'
            ]
        },
        'const_let': {
            'description': 'Uso de const y let en lugar de var',
            'patterns': [
                r'const\s+\w+',
                r'let\s+\w+'
            ],
            'anti_patterns': [
                r'var\s+\w+'
            ],
            'severity': 'info',
            'recommendations': [
                'Usar const para valores inmutables',
                'Usar let para variables que cambian',
                'Evitar var debido a problemas de scope'
            ]
        },
        'destructuring': {
            'description': 'Uso de destructuring',
            'patterns': [
                r'const\s*{\s*[^}]+\s*}\s*=',
                r'const\s*\[\s*[^\]]+\s*\]\s*='
            ],
            'severity': 'info',
            'recommendations': [
                'Usar destructuring para extraer propiedades de objetos',
                'Simplificar código al trabajar con arrays',
                'Mejora la legibilidad del código'
            ]
        }
    },
    'typescript': {
        'interfaces': {
            'description': 'Uso de interfaces o tipos',
            'patterns': [
                r'interface\s+\w+',
                r'type\s+\w+\s*='
            ],
            'severity': 'info',
            'recommendations': [
                'Definir interfaces para estructuras de datos',
                'Usar tipos para uniones y tipos más complejos',
                'Mejorar la documentación y detección de errores'
            ]
        },
        'strict_null': {
            'description': 'Uso de null checks',
            'patterns': [
                r'\w+\s*\?\.',
                r'\w+\s*!\.'
            ],
            'severity': 'info',
            'recommendations': [
                'Usar operador ?. para accesos seguros',
                'Verificar valores nulos antes de acceder a propiedades',
                'Habilitar strictNullChecks en tsconfig.json'
            ]
        }
    }
}


class CodeQualityAnalyzer:
    """Analizador de calidad de código para proyectos de software."""
    
    def __init__(self, scanner: Optional[ProjectScanner] = None):
        """
        Inicializar analizador de calidad de código.
        
        Args:
            scanner: Escáner de proyectos opcional
        """
        self.scanner = scanner or get_project_scanner()
        
        # Resultados del análisis
        self.code_smells = {}
        self.best_practices = {}
        self.metrics = {}
        self.language_stats = {}
        self.summary = {}
    
    def analyze_code_quality(self, project_path: str) -> Dict[str, Any]:
        """
        Analizar la calidad del código en un proyecto.
        
        Args:
            project_path: Ruta al directorio del proyecto
            
        Returns:
            Dict con resultados de análisis de calidad
        """
        # Escanear el proyecto para obtener información
        project_data = self.scanner.scan_project(project_path)
        
        # Resetear resultados previos
        self.code_smells = {}
        self.best_practices = {}
        self.metrics = {}
        self.language_stats = {}
        
        # Analizar problemas de código
        self._analyze_code_smells(project_data)
        
        # Analizar buenas prácticas
        self._analyze_best_practices(project_data)
        
        # Calcular métricas de código
        self._calculate_metrics(project_data)
        
        # Generar resumen
        self._generate_summary()
        
        # Preparar resultado
        return {
            'code_smells': self.code_smells,
            'best_practices': self.best_practices,
            'metrics': self.metrics,
            'summary': self.summary,
            'project_path': project_path
        }
    
    def _analyze_code_smells(self, project_data: Dict[str, Any]) -> None:
        """
        Analizar el código en busca de problemas comunes.
        
        Args:
            project_data: Datos del proyecto escaneado
        """
        files = project_data.get('files', [])
        
        # Inicializar resultados para cada tipo de problema
        for smell_name in CODE_SMELLS_PATTERNS:
            self.code_smells[smell_name] = {
                'description': CODE_SMELLS_PATTERNS[smell_name]['description'],
                'severity': CODE_SMELLS_PATTERNS[smell_name]['severity'],
                'recommendations': CODE_SMELLS_PATTERNS[smell_name]['recommendations'],
                'occurrences': [],
                'count': 0
            }
        
        # Analizar cada archivo
        for file_info in files:
            # Omitir archivos binarios o demasiado grandes
            if file_info.get('is_binary', True) or not file_info.get('language'):
                continue
                
            file_path = file_info.get('path', '')
            language = file_info.get('language', '').lower()
            
            try:
                # Leer contenido del archivo
                with open(os.path.join(project_data.get('project_path', ''), file_path), 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Buscar cada tipo de problema
                    for smell_name, smell_info in CODE_SMELLS_PATTERNS.items():
                        patterns = smell_info.get('patterns', [])
                        exclude_patterns = smell_info.get('exclude_patterns', [])
                        severity = smell_info.get('severity', 'warning')
                        
                        # Verificar si debemos excluir este archivo para este smell
                        exclude_file = False
                        for exclude in exclude_patterns:
                            if re.search(exclude, content, re.IGNORECASE | re.MULTILINE):
                                exclude_file = True
                                break
                                
                        if exclude_file:
                            continue
                        
                        # Buscar patrones en el contenido
                        for pattern in patterns:
                            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                            
                            for match in matches:
                                # Extraer contexto limitado para evitar textos demasiado largos
                                match_text = match.group(0)[:100] + ('...' if len(match.group(0)) > 100 else '')
                                
                                # Calcular número de línea
                                line_number = content[:match.start()].count('\n') + 1
                                
                                # Añadir ocurrencia
                                self.code_smells[smell_name]['occurrences'].append({
                                    'file': file_path,
                                    'line': line_number,
                                    'context': match_text,
                                    'language': language
                                })
                                
                                self.code_smells[smell_name]['count'] += 1
                    
            except Exception as e:
                logger.debug(f"Error al analizar calidad en {file_path}: {e}")
    
    def _analyze_best_practices(self, project_data: Dict[str, Any]) -> None:
        """
        Analizar el código en busca de buenas prácticas.
        
        Args:
            project_data: Datos del proyecto escaneado
        """
        files = project_data.get('files', [])
        languages = project_data.get('languages', {})
        
        # Inicializar resultados por lenguaje
        for language, practices in BEST_PRACTICES_PATTERNS.items():
            self.best_practices[language] = {}
            for practice_name, practice_info in practices.items():
                self.best_practices[language][practice_name] = {
                    'description': practice_info['description'],
                    'severity': practice_info['severity'],
                    'recommendations': practice_info['recommendations'],
                    'detected': [],
                    'count': 0,
                    'applicable_files': 0,
                    'compliance_rate': 0
                }
        
        # Contar archivos por lenguaje para calcular porcentajes
        language_file_counts = defaultdict(int)
        
        # Analizar cada archivo
        for file_info in files:
            # Omitir archivos binarios o demasiado grandes
            if file_info.get('is_binary', True) or not file_info.get('language'):
                continue
                
            file_path = file_info.get('path', '')
            language = file_info.get('language', '').lower()
            
            # Normalizar lenguaje
            if language == 'js':
                language = 'javascript'
            elif language == 'ts':
                language = 'typescript'
            elif language == 'py':
                language = 'python'
            
            # Incrementar contador de archivos por lenguaje
            language_file_counts[language] += 1
            
            # Verificar si tenemos patrones para este lenguaje
            if language not in BEST_PRACTICES_PATTERNS:
                continue
                
            try:
                # Leer contenido del archivo
                with open(os.path.join(project_data.get('project_path', ''), file_path), 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Verificar cada buena práctica para este lenguaje
                    for practice_name, practice_info in BEST_PRACTICES_PATTERNS[language].items():
                        practices_detected = False
                        
                        # Buscar patrones de buena práctica
                        for pattern in practice_info.get('patterns', []):
                            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                                self.best_practices[language][practice_name]['count'] += 1
                                self.best_practices[language][practice_name]['detected'].append(file_path)
                                practices_detected = True
                                break
                        
                        # Si hay anti-patrones, verificarlos
                        for anti_pattern in practice_info.get('anti_patterns', []):
                            if re.search(anti_pattern, content, re.IGNORECASE | re.MULTILINE):
                                # Si encontramos un anti-patrón, incrementamos el contador de archivos aplicables
                                self.best_practices[language][practice_name]['applicable_files'] += 1
                                break
                        
                        # Incrementar contador de archivos aplicables
                        if practices_detected or 'anti_patterns' not in practice_info:
                            self.best_practices[language][practice_name]['applicable_files'] += 1
                    
            except Exception as e:
                logger.debug(f"Error al analizar buenas prácticas en {file_path}: {e}")
        
        # Calcular ratios de conformidad
        for language, practices in self.best_practices.items():
            for practice_name, practice_data in practices.items():
                applicable_files = practice_data['applicable_files']
                
                if applicable_files > 0:
                    practice_data['compliance_rate'] = int((practice_data['count'] / applicable_files) * 100)
                else:
                    practice_data['compliance_rate'] = 0
    
    def _calculate_metrics(self, project_data: Dict[str, Any]) -> None:
        """
        Calcular métricas de calidad del código.
        
        Args:
            project_data: Datos del proyecto escaneado
        """
        files = project_data.get('files', [])
        
        # Inicializar métricas
        self.metrics = {
            'total_files': 0,
            'lines_of_code': 0,
            'comment_lines': 0,
            'comment_ratio': 0,
            'avg_file_size': 0,
            'function_count': 0,
            'class_count': 0,
            'complexity': {},
            'size_distribution': {
                'small': 0,    # < 100 líneas
                'medium': 0,   # 100-300 líneas
                'large': 0,    # 300-500 líneas
                'x_large': 0   # > 500 líneas
            }
        }
        
        # Contadores
        total_size = 0
        code_files = 0
        
        # Patrones para detectar funciones y clases
        function_pattern = re.compile(r'(function|def)\s+\w+|(?<!\w)(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>|\(\s*(?:[^)]*)\s*\)\s*=>', re.IGNORECASE)
        class_pattern = re.compile(r'class\s+\w+|interface\s+\w+|type\s+\w+\s*=', re.IGNORECASE)
        comment_pattern = re.compile(r'\/\/.*$|\/\*[\s\S]*?\*\/|#.*$', re.MULTILINE)
        
        # Analizar cada archivo
        for file_info in files:
            # Omitir archivos binarios
            if file_info.get('is_binary', True) or not file_info.get('language'):
                continue
                
            file_path = file_info.get('path', '')
            language = file_info.get('language', '').lower()
            
            try:
                # Leer contenido del archivo
                with open(os.path.join(project_data.get('project_path', ''), file_path), 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Contar líneas de código
                    lines = content.split('\n')
                    num_lines = len(lines)
                    
                    # Contar líneas de comentarios
                    comment_matches = comment_pattern.findall(content)
                    comment_lines = 0
                    for match in comment_matches:
                        if isinstance(match, tuple):
                            for m in match:
                                if m:
                                    comment_lines += m.count('\n') + 1
                        else:
                            comment_lines += match.count('\n') + 1
                    
                    # Actualizar métricas
                    self.metrics['lines_of_code'] += num_lines
                    self.metrics['comment_lines'] += comment_lines
                    
                    # Contar funciones y clases
                    function_matches = function_pattern.findall(content)
                    class_matches = class_pattern.findall(content)
                    
                    self.metrics['function_count'] += len(function_matches)
                    self.metrics['class_count'] += len(class_matches)
                    
                    # Clasificar archivo por tamaño
                    if num_lines < 100:
                        self.metrics['size_distribution']['small'] += 1
                    elif num_lines < 300:
                        self.metrics['size_distribution']['medium'] += 1
                    elif num_lines < 500:
                        self.metrics['size_distribution']['large'] += 1
                    else:
                        self.metrics['size_distribution']['x_large'] += 1
                    
                    # Actualizar contadores
                    total_size += num_lines
                    code_files += 1
            
            except Exception as e:
                logger.debug(f"Error al calcular métricas en {file_path}: {e}")
        
        # Actualizar métricas finales
        self.metrics['total_files'] = code_files
        
        if code_files > 0:
            self.metrics['avg_file_size'] = int(total_size / code_files)
        
        if self.metrics['lines_of_code'] > 0:
            self.metrics['comment_ratio'] = round((self.metrics['comment_lines'] / self.metrics['lines_of_code']) * 100, 2)
        
        # Calcular complejidad estimada
        code_smells_count = sum(smell['count'] for smell in self.code_smells.values())
        large_files = self.metrics['size_distribution']['large'] + self.metrics['size_distribution']['x_large']
        
        if code_files > 0:
            smell_ratio = code_smells_count / code_files
            large_ratio = large_files / code_files
            
            # Estimar complejidad
            if smell_ratio < 0.5 and large_ratio < 0.1:
                complexity = "baja"
            elif smell_ratio < 1.5 and large_ratio < 0.3:
                complexity = "media"
            else:
                complexity = "alta"
                
            self.metrics['complexity'] = {
                'level': complexity,
                'smell_ratio': round(smell_ratio, 2),
                'large_file_ratio': round(large_ratio, 2)
            }
    
    def _generate_summary(self) -> None:
        """Generar un resumen del análisis de calidad."""
        # Obtener estadísticas de code smells
        critical_issues = sum(1 for smell in self.code_smells.values() 
                            for occurrence in smell['occurrences'] 
                            if smell['severity'] == 'critical')
                            
        warnings = sum(1 for smell in self.code_smells.values() 
                     for occurrence in smell['occurrences'] 
                     if smell['severity'] == 'warning')
                     
        infos = sum(1 for smell in self.code_smells.values() 
                  for occurrence in smell['occurrences'] 
                  if smell['severity'] == 'info')
        
        # Identificar principales problemas
        top_issues = sorted(
            [(name, data['count'], data['severity']) for name, data in self.code_smells.items()],
            key=lambda x: (0 if x[2] == 'critical' else (1 if x[2] == 'warning' else 2), -x[1])
        )[:3]
        
        # Identificar buenas prácticas con baja adopción
        low_adoption_practices = []
        for language, practices in self.best_practices.items():
            for name, data in practices.items():
                if data['applicable_files'] > 3 and data['compliance_rate'] < 50:
                    low_adoption_practices.append({
                        'language': language,
                        'practice': name,
                        'description': data['description'],
                        'compliance_rate': data['compliance_rate']
                    })
        
        # Crear recomendaciones de mejora
        recommendations = []
        
        # Recomendar resolver problemas críticos primero
        if critical_issues > 0:
            recommendations.append({
                'title': f"Resolver {critical_issues} problemas críticos",
                'description': "Priorizar la resolución de problemas de seguridad y problemas críticos.",
                'priority': 'alta'
            })
        
        # Recomendar mejoras basadas en top_issues
        for issue_name, count, severity in top_issues:
            if count > 0:
                issue_info = self.code_smells[issue_name]
                recommendations.append({
                    'title': f"Resolver {issue_info['description'].lower()}",
                    'description': issue_info['recommendations'][0],
                    'priority': 'alta' if severity == 'critical' else ('media' if severity == 'warning' else 'baja')
                })
        
        # Recomendar buenas prácticas con baja adopción
        for practice in low_adoption_practices[:2]:  # Tomar hasta 2
            practice_info = BEST_PRACTICES_PATTERNS[practice['language']][practice['practice']]
            recommendations.append({
                'title': f"Mejorar adopción de {practice['description'].lower()}",
                'description': practice_info['recommendations'][0],
                'priority': 'media'
            })
        
        # Si hay muchos archivos grandes, recomendar refactorización
        if self.metrics['size_distribution']['x_large'] > 5 or self.metrics['size_distribution']['large'] > 10:
            recommendations.append({
                'title': "Refactorizar archivos grandes",
                'description': "Dividir archivos grandes en módulos más pequeños y cohesivos.",
                'priority': 'media'
            })
        
        # Si la ratio de comentarios es baja, sugerir mejorar documentación
        if self.metrics['comment_ratio'] < 10 and self.metrics['lines_of_code'] > 1000:
            recommendations.append({
                'title': "Mejorar documentación del código",
                'description': "Añadir comentarios explicativos y documentación para mejorar mantenibilidad.",
                'priority': 'baja'
            })
        
        # Crear resumen final
        self.summary = {
            'issues': {
                'critical': critical_issues,
                'warnings': warnings,
                'info': infos,
                'total': critical_issues + warnings + infos
            },
            'top_issues': [{'name': name, 'count': count, 'severity': severity} for name, count, severity in top_issues],
            'recommendations': recommendations,
            'quality_score': self._calculate_quality_score(critical_issues, warnings, infos)
        }
    
    def _calculate_quality_score(self, critical: int, warnings: int, infos: int) -> int:
        """
        Calcular puntuación de calidad del código.
        
        Args:
            critical: Número de problemas críticos
            warnings: Número de advertencias
            infos: Número de informaciones
            
        Returns:
            Puntuación del 0-100
        """
        base_score = 100
        
        # Penalizar por problemas
        if self.metrics.get('lines_of_code', 0) > 0:
            # Normalizar por tamaño del código
            loc_factor = min(1.0, 5000 / self.metrics['lines_of_code'])
            
            # Calcular penalizaciones
            critical_penalty = critical * 10 * loc_factor
            warning_penalty = warnings * 3 * loc_factor
            info_penalty = infos * 0.5 * loc_factor
            
            # Aplicar penalizaciones
            score = base_score - critical_penalty - warning_penalty - info_penalty
            
            # Ajustar basado en métricas de complejidad
            if self.metrics.get('complexity', {}).get('level') == 'alta':
                score -= 10
            elif self.metrics.get('complexity', {}).get('level') == 'media':
                score -= 5
                
            # Ajustar basado en best practices
            best_practices_bonus = 0
            practice_count = 0
            
            for language, practices in self.best_practices.items():
                for practice, data in practices.items():
                    if data['applicable_files'] > 0:
                        best_practices_bonus += data['compliance_rate']
                        practice_count += 1
            
            if practice_count > 0:
                # Añadir hasta 10 puntos de bonus por buenas prácticas
                best_practices_bonus = min(10, (best_practices_bonus / practice_count) / 10)
                score += best_practices_bonus
            
            return max(0, min(100, int(score)))
        
        return base_score
    
    def generate_quality_report(self) -> str:
        """
        Generar un informe de texto sobre la calidad del código.
        
        Returns:
            Informe en formato texto
        """
        if not self.summary:
            return "No se ha realizado ningún análisis de calidad."
        
        report = []
        report.append("# Informe de Calidad de Código")
        report.append(f"Puntuación de Calidad: {self.summary['quality_score']}/100")
        report.append("")
        
        # Añadir resumen de problemas
        issues = self.summary['issues']
        report.append(f"## Resumen de Problemas Detectados")
        report.append(f"- **Críticos**: {issues['critical']}")
        report.append(f"- **Advertencias**: {issues['warnings']}")
        report.append(f"- **Información**: {issues['info']}")
        report.append(f"- **Total**: {issues['total']}")
        report.append("")
        
        # Añadir principales problemas
        if self.summary['top_issues']:
            report.append("## Principales Problemas")
            for issue in self.summary['top_issues']:
                severity_icon = "🔴" if issue['severity'] == 'critical' else ("🟠" if issue['severity'] == 'warning' else "🔵")
                report.append(f"- {severity_icon} **{issue['name']}**: {issue['count']} ocurrencias")
            report.append("")
        
        # Añadir recomendaciones
        if self.summary['recommendations']:
            report.append("## Recomendaciones")
            for rec in self.summary['recommendations']:
                priority_icon = "🔴" if rec['priority'] == 'alta' else ("🟠" if rec['priority'] == 'media' else "🔵")
                report.append(f"- {priority_icon} **{rec['title']}**: {rec['description']}")
            report.append("")
        
        # Añadir métricas
        report.append("## Métricas")
        report.append(f"- **Archivos de código**: {self.metrics['total_files']}")
        report.append(f"- **Líneas de código**: {self.metrics['lines_of_code']}")
        report.append(f"- **Ratio de comentarios**: {self.metrics['comment_ratio']}%")
        report.append(f"- **Funciones**: {self.metrics['function_count']}")
        report.append(f"- **Clases/Interfaces**: {self.metrics['class_count']}")
        report.append(f"- **Complejidad estimada**: {self.metrics.get('complexity', {}).get('level', 'n/a')}")
        report.append("")
        
        # Añadir distribución de tamaños
        report.append("## Distribución de Tamaño de Archivos")
        report.append(f"- **Pequeños** (<100 líneas): {self.metrics['size_distribution']['small']}")
        report.append(f"- **Medianos** (100-300 líneas): {self.metrics['size_distribution']['medium']}")
        report.append(f"- **Grandes** (300-500 líneas): {self.metrics['size_distribution']['large']}")
        report.append(f"- **Extra grandes** (>500 líneas): {self.metrics['size_distribution']['x_large']}")
        
        return "\n".join(report)


def get_code_quality_analyzer(scanner: Optional[ProjectScanner] = None) -> CodeQualityAnalyzer:
    """
    Obtener una instancia del analizador de calidad de código.
    
    Args:
        scanner: Escáner de proyectos opcional
        
    Returns:
        Instancia de CodeQualityAnalyzer
    """
    return CodeQualityAnalyzer(scanner=scanner)
