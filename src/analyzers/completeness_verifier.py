#!/usr/bin/env python3
"""
Verificador de completitud para ProjectPrompt.
Analiza el nivel de completitud de implementaciones según especificaciones.
"""
import os
import re
import json
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
import datetime

from src.utils import logger, config_manager
from src.analyzers.project_scanner import get_project_scanner
from src.analyzers.functionality_detector import get_functionality_detector
from src.analyzers.code_quality_analyzer import get_code_quality_analyzer


class CompletenessVerifier:
    """
    Verificador de completitud para implementaciones de funcionalidades.
    Analiza el grado de avance y completitud de una implementación según criterios
    predefinidos y checklists adaptados al tipo de proyecto y funcionalidad.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializar verificador de completitud.
        
        Args:
            config: Configuración adicional para el verificador
        """
        self.config = config or {}
        self.is_premium = self.config.get("premium", False)
        
        # Obtener analizadores necesarios
        self.scanner = get_project_scanner()
        self.functionality_detector = get_functionality_detector()
        self.code_quality_analyzer = get_code_quality_analyzer()
        
        # Rutas a plantillas y checklists
        self.templates_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "templates", "verification"
        )
        
        # Criterios generales de completitud por tipo de componente
        self._load_verification_templates()
    
    def _load_verification_templates(self):
        """Cargar plantillas de verificación desde archivos."""
        self.verification_templates = {}
        self.component_checklists = {}
        
        # Intentar cargar archivo de plantillas
        templates_path = os.path.join(self.templates_dir, "templates.json")
        if os.path.exists(templates_path):
            try:
                with open(templates_path, "r", encoding="utf-8") as f:
                    self.verification_templates = json.load(f)
            except Exception as e:
                logger.error(f"Error al cargar plantillas de verificación: {e}")
                # Usar plantillas por defecto
                self._setup_default_templates()
        else:
            # Usar plantillas por defecto
            self._setup_default_templates()
        
        # Cargar checklists para componentes
        checklists_path = os.path.join(self.templates_dir, "checklists.json")
        if os.path.exists(checklists_path):
            try:
                with open(checklists_path, "r", encoding="utf-8") as f:
                    self.component_checklists = json.load(f)
            except Exception as e:
                logger.error(f"Error al cargar checklists: {e}")
                # Usar checklists por defecto
                self._setup_default_checklists()
        else:
            # Usar checklists por defecto
            self._setup_default_checklists()
    
    def _setup_default_templates(self):
        """Configurar plantillas de verificación por defecto."""
        self.verification_templates = {
            "api": {
                "required_files": [
                    "{name}_client.py",
                    "{name}_api.py"
                ],
                "required_functions": [
                    "connect", 
                    "authenticate", 
                    "request"
                ],
                "required_components": [
                    "error_handling",
                    "authentication",
                    "rate_limiting"
                ],
                "quality_metrics": {
                    "test_coverage": 60,
                    "documentation": 70
                }
            },
            "database": {
                "required_files": [
                    "{name}_model.py",
                    "{name}_repository.py"
                ],
                "required_functions": [
                    "connect",
                    "query",
                    "insert",
                    "update",
                    "delete"
                ],
                "required_components": [
                    "connection_pooling",
                    "transaction_management",
                    "error_handling"
                ],
                "quality_metrics": {
                    "test_coverage": 70,
                    "documentation": 60
                }
            },
            "ui": {
                "required_files": [
                    "{name}_view.py",
                    "{name}_controller.py"
                ],
                "required_functions": [
                    "render",
                    "handle_input",
                    "update"
                ],
                "required_components": [
                    "error_handling",
                    "responsive_design",
                    "accessibility"
                ],
                "quality_metrics": {
                    "test_coverage": 50,
                    "documentation": 50
                }
            },
            "utility": {
                "required_files": [
                    "{name}.py"
                ],
                "required_functions": [
                    "main_function"
                ],
                "required_components": [
                    "error_handling",
                    "logging"
                ],
                "quality_metrics": {
                    "test_coverage": 60,
                    "documentation": 60
                }
            },
            "default": {
                "required_files": [
                    "{name}.py"
                ],
                "required_functions": [],
                "required_components": [
                    "error_handling"
                ],
                "quality_metrics": {
                    "test_coverage": 50,
                    "documentation": 50
                }
            }
        }
    
    def _setup_default_checklists(self):
        """Configurar checklists por defecto para componentes."""
        self.component_checklists = {
            "error_handling": [
                "¿Se capturan y gestionan excepciones específicas?",
                "¿Se registran los errores con nivel de log adecuado?",
                "¿Se devuelven mensajes de error útiles al usuario?",
                "¿Se manejan condiciones de borde y casos extremos?"
            ],
            "authentication": [
                "¿Se utilizan métodos seguros de autenticación?",
                "¿Se validan correctamente las credenciales?",
                "¿Se protegen adecuadamente los tokens y secretos?",
                "¿Existe manejo de sesiones y expiración de credenciales?"
            ],
            "rate_limiting": [
                "¿Se implementa limitación de tasa para prevenir abusos?",
                "¿Se respetan los límites de la API externa?",
                "¿Se informa al usuario sobre límites alcanzados?",
                "¿Existe una estrategia de reintentos con backoff?"
            ],
            "transaction_management": [
                "¿Se utilizan transacciones para operaciones múltiples?",
                "¿Se implementa rollback ante fallos?",
                "¿Se minimizan los bloqueos y se optimiza concurrencia?"
            ],
            "connection_pooling": [
                "¿Se reutilizan conexiones mediante pooling?",
                "¿Se gestionan adecuadamente el ciclo de vida de las conexiones?",
                "¿Se configuran tiempos de espera y reintentos adecuados?"
            ],
            "logging": [
                "¿Se utilizan niveles de log apropiados?",
                "¿Se evita registrar datos sensibles?",
                "¿Los mensajes de log son descriptivos y útiles?",
                "¿Se utiliza un formato estándar para todos los mensajes?"
            ],
            "responsive_design": [
                "¿La interfaz se adapta a diferentes tamaños de pantalla?",
                "¿Se utilizan unidades relativas para dimensiones?",
                "¿Se prueban diferentes resoluciones y dispositivos?"
            ],
            "accessibility": [
                "¿Se utilizan etiquetas y descripciones para elementos?",
                "¿La navegación es posible mediante teclado?",
                "¿Se cumplen estándares de contraste y legibilidad?",
                "¿Hay equivalentes textuales para contenido no textual?"
            ]
        }
    
    def verify_functionality(self, 
                            functionality_name: str, 
                            project_path: str,
                            template_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Verificar completitud de implementación de una funcionalidad.
        
        Args:
            functionality_name: Nombre de la funcionalidad
            project_path: Ruta al proyecto
            template_type: Tipo de plantilla a utilizar (api, database, ui, utility)
            
        Returns:
            Informe detallado sobre completitud
        """
        # Normalizar ruta al proyecto
        project_path = os.path.abspath(project_path)
        
        # Verificar existencia de la funcionalidad
        functionality_data = self.functionality_detector.detect_functionality(
            project_path, functionality_name
        )
        
        if not functionality_data:
            return {
                "success": False,
                "error": f"No se encontró la funcionalidad '{functionality_name}' en el proyecto"
            }
        
        # Determinar tipo de plantilla si no se especificó
        if not template_type:
            template_type = self._detect_template_type(functionality_data)
        
        # Obtener plantilla de verificación
        template = self.verification_templates.get(
            template_type, self.verification_templates.get("default", {})
        )
        
        # Obtener archivos de la funcionalidad
        files = functionality_data.get("files", [])
        
        # Resultados de la verificación
        result = {
            "functionality": functionality_name,
            "template_type": template_type,
            "timestamp": datetime.datetime.now().isoformat(),
            "completeness_score": 0,
            "quality_score": 0,
            "required_files_completeness": 0,
            "required_functions_completeness": 0,
            "required_components_completeness": 0,
            "quality_metrics": {},
            "missing_files": [],
            "missing_functions": [],
            "incomplete_components": [],
            "checklist_results": {},
            "improvement_suggestions": []
        }
        
        # Verificar archivos requeridos
        result.update(self._verify_required_files(
            template, functionality_name, files
        ))
        
        # Verificar funciones requeridas
        result.update(self._verify_required_functions(
            template, files, functionality_name
        ))
        
        # Verificar componentes requeridos
        result.update(self._verify_required_components(
            template, files, functionality_name
        ))
        
        # Medir métricas de calidad
        result.update(self._measure_quality_metrics(
            template, files
        ))
        
        # Calcular puntuaciones generales
        file_weight = 0.3
        function_weight = 0.3
        component_weight = 0.25
        quality_weight = 0.15
        
        result["completeness_score"] = int(
            (result["required_files_completeness"] * file_weight +
             result["required_functions_completeness"] * function_weight +
             result["required_components_completeness"] * component_weight +
             result["quality_score"] * quality_weight)
        )
        
        # Generar sugerencias de mejora
        result["improvement_suggestions"] = self._generate_improvement_suggestions(result)
        
        return result
    
    def verify_project(self, project_path: str) -> Dict[str, Any]:
        """
        Verificar completitud de múltiples funcionalidades en un proyecto.
        
        Args:
            project_path: Ruta al proyecto
            
        Returns:
            Informe detallado sobre completitud del proyecto
        """
        # Normalizar ruta al proyecto
        project_path = os.path.abspath(project_path)
        
        # Escanear proyecto
        project_data = self.scanner.scan_project(project_path)
        
        # Detectar funcionalidades principales
        functionality_data = self.functionality_detector.detect_functionalities(project_path)
        main_functionalities = functionality_data.get("main_functionalities", [])
        
        # Resultados por funcionalidad
        functionality_results = {}
        average_score = 0
        
        # Verificar cada funcionalidad
        for functionality in main_functionalities:
            result = self.verify_functionality(functionality, project_path)
            functionality_results[functionality] = result
            
            if "completeness_score" in result:
                average_score += result["completeness_score"]
        
        # Calcular promedio si hay funcionalidades
        if main_functionalities:
            average_score = int(average_score / len(main_functionalities))
        
        # Crear informe de proyecto
        project_result = {
            "project_name": os.path.basename(project_path),
            "timestamp": datetime.datetime.now().isoformat(),
            "average_completeness_score": average_score,
            "functionalities_analyzed": len(main_functionalities),
            "functionality_results": functionality_results,
            "project_checklist": self._verify_project_checklist(project_path, project_data),
            "overall_recommendations": self._generate_project_recommendations(
                average_score, functionality_results
            )
        }
        
        return project_result
    
    def _detect_template_type(self, functionality_data: Dict[str, Any]) -> str:
        """
        Detectar tipo de plantilla adecuado para una funcionalidad.
        
        Args:
            functionality_data: Datos de la funcionalidad
            
        Returns:
            Tipo de plantilla (api, database, ui, utility, default)
        """
        evidence = functionality_data.get("evidence", {})
        
        # Palabras clave que indican tipo de funcionalidad
        api_keywords = ["api", "client", "http", "request", "response", "endpoint", "rest"]
        db_keywords = ["database", "repository", "model", "entity", "sql", "mongo", "dao"]
        ui_keywords = ["ui", "gui", "view", "widget", "display", "interface", "button"]
        
        # Contar apariciones de palabras clave en importaciones y archivos
        api_count = 0
        db_count = 0
        ui_count = 0
        
        # Revisar importaciones
        imports = evidence.get("imports", [])
        for imp in imports:
            imp_lower = imp.lower()
            api_count += sum(1 for kw in api_keywords if kw in imp_lower)
            db_count += sum(1 for kw in db_keywords if kw in imp_lower)
            ui_count += sum(1 for kw in ui_keywords if kw in imp_lower)
        
        # Revisar nombres de archivos
        files = evidence.get("files", [])
        for file_path in files:
            file_name = os.path.basename(file_path).lower()
            api_count += sum(1 for kw in api_keywords if kw in file_name)
            db_count += sum(1 for kw in db_keywords if kw in file_name)
            ui_count += sum(1 for kw in ui_keywords if kw in file_name)
        
        # Determinar tipo por mayor conteo
        max_count = max(api_count, db_count, ui_count)
        
        if max_count == 0:
            return "utility"  # Tipo predeterminado si no hay coincidencias claras
        elif max_count == api_count:
            return "api"
        elif max_count == db_count:
            return "database"
        elif max_count == ui_count:
            return "ui"
        else:
            return "utility"
    
    def _verify_required_files(self, 
                             template: Dict[str, Any],
                             functionality_name: str,
                             files: List[str]) -> Dict[str, Any]:
        """
        Verificar presencia de archivos requeridos.
        
        Args:
            template: Plantilla de verificación
            functionality_name: Nombre de la funcionalidad
            files: Lista de archivos de la funcionalidad
            
        Returns:
            Resultado de la verificación de archivos
        """
        required_files = template.get("required_files", [])
        found_files = 0
        missing_files = []
        
        # Formato del nombre de la funcionalidad para patrones
        name_formats = [
            functionality_name.lower(),
            functionality_name.replace("-", "_").lower(),
            "".join(word.capitalize() for word in functionality_name.split("-"))
        ]
        
        # Para cada archivo requerido
        for req_file in required_files:
            found = False
            
            # Probar diferentes formatos del nombre
            for name_format in name_formats:
                pattern = req_file.format(name=name_format)
                
                # Verificar si algún archivo coincide con el patrón
                for file_path in files:
                    file_name = os.path.basename(file_path)
                    if file_name.lower() == pattern.lower():
                        found = True
                        break
            
            if found:
                found_files += 1
            else:
                # Si no se encontró, sugerir posibles nombres
                suggestions = [req_file.format(name=name_format) 
                             for name_format in name_formats]
                missing_files.append({
                    "pattern": req_file,
                    "suggestions": suggestions
                })
        
        # Calcular completitud
        files_completeness = 100
        if required_files:
            files_completeness = int((found_files / len(required_files)) * 100)
        
        return {
            "required_files_found": found_files,
            "required_files_total": len(required_files),
            "required_files_completeness": files_completeness,
            "missing_files": missing_files
        }
    
    def _verify_required_functions(self, 
                                 template: Dict[str, Any],
                                 files: List[str],
                                 functionality_name: str) -> Dict[str, Any]:
        """
        Verificar presencia de funciones requeridas.
        
        Args:
            template: Plantilla de verificación
            files: Lista de archivos de la funcionalidad
            functionality_name: Nombre de la funcionalidad
            
        Returns:
            Resultado de la verificación de funciones
        """
        required_functions = template.get("required_functions", [])
        found_functions = 0
        missing_functions = []
        
        # Extraer todas las funciones definidas en los archivos
        defined_functions = self._extract_functions_from_files(files)
        
        # Formato del nombre de la funcionalidad para patrones
        name_formats = [
            functionality_name.lower(),
            functionality_name.replace("-", "_").lower(),
            "".join(word.capitalize() for word in functionality_name.split("-"))
        ]
        
        # Para cada función requerida
        for req_function in required_functions:
            found = False
            
            # Buscar coincidencias directas
            if req_function in defined_functions:
                found = True
            else:
                # Buscar con prefijos basados en el nombre de la funcionalidad
                for name_format in name_formats:
                    prefixed_function = f"{name_format}_{req_function}"
                    if prefixed_function in defined_functions:
                        found = True
                        break
            
            if found:
                found_functions += 1
            else:
                # Sugerir nombres posibles para la función
                suggestions = [req_function] + [
                    f"{name_format}_{req_function}" for name_format in name_formats
                ]
                missing_functions.append({
                    "function": req_function,
                    "suggestions": suggestions
                })
        
        # Calcular completitud
        functions_completeness = 100
        if required_functions:
            functions_completeness = int((found_functions / len(required_functions)) * 100)
        
        return {
            "required_functions_found": found_functions,
            "required_functions_total": len(required_functions),
            "required_functions_completeness": functions_completeness,
            "missing_functions": missing_functions
        }
    
    def _extract_functions_from_files(self, files: List[str]) -> Set[str]:
        """
        Extraer nombres de funciones definidas en archivos Python.
        
        Args:
            files: Lista de rutas a archivos
            
        Returns:
            Conjunto con nombres de funciones
        """
        functions = set()
        
        # Patrón para detectar definiciones de funciones Python
        function_pattern = re.compile(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')
        
        for file_path in files:
            # Solo analizar archivos Python
            if not file_path.endswith('.py'):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Encontrar todas las coincidencias
                matches = function_pattern.findall(content)
                
                # Añadir al conjunto de funciones
                functions.update(matches)
                    
            except Exception as e:
                logger.warning(f"Error al leer archivo {file_path}: {e}")
        
        return functions
    
    def _verify_required_components(self, 
                                  template: Dict[str, Any],
                                  files: List[str],
                                  functionality_name: str) -> Dict[str, Any]:
        """
        Verificar presencia de componentes requeridos.
        
        Args:
            template: Plantilla de verificación
            files: Lista de archivos de la funcionalidad
            functionality_name: Nombre de la funcionalidad
            
        Returns:
            Resultado de la verificación de componentes
        """
        required_components = template.get("required_components", [])
        checklist_results = {}
        incomplete_components = []
        
        # Para cada componente
        for component in required_components:
            # Obtener checklist para este componente
            checklist = self.component_checklists.get(component, [])
            
            if not checklist:
                continue
                
            # Analizar contenido de archivos para este componente
            items_fulfilled = self._check_component_implementation(component, files)
            
            # Calcular porcentaje de cumplimiento
            fulfillment = 0
            if checklist:
                fulfillment = int((items_fulfilled / len(checklist)) * 100)
                
            # Guardar resultado
            checklist_results[component] = {
                "name": component,
                "checklist_items_total": len(checklist),
                "checklist_items_fulfilled": items_fulfilled,
                "fulfillment_percentage": fulfillment,
                "checklist": checklist
            }
            
            # Si no está completamente implementado, añadir a incompletos
            if fulfillment < 100:
                incomplete_components.append({
                    "component": component,
                    "fulfillment_percentage": fulfillment,
                    "missing_items": len(checklist) - items_fulfilled
                })
        
        # Calcular completitud global de componentes
        components_completeness = 100
        if required_components:
            total_fulfillment = sum(
                result["fulfillment_percentage"] 
                for result in checklist_results.values()
            )
            components_completeness = int(total_fulfillment / len(required_components))
        
        return {
            "required_components_total": len(required_components),
            "required_components_completeness": components_completeness,
            "incomplete_components": incomplete_components,
            "checklist_results": checklist_results
        }
    
    def _check_component_implementation(self, 
                                       component: str, 
                                       files: List[str]) -> int:
        """
        Verificar implementación de un componente mediante análisis de código.
        
        Args:
            component: Nombre del componente
            files: Lista de archivos a analizar
            
        Returns:
            Número de ítems de checklist cumplidos
        """
        checklist = self.component_checklists.get(component, [])
        items_fulfilled = 0
        
        # Patrones específicos para verificar cada tipo de componente
        component_patterns = {
            "error_handling": [
                r'try\s*:.*?except',
                r'raise\s+[A-Z][a-zA-Z0-9]*Error',
                r'logger\.(error|warning|exception)',
                r'if.*?:\s*return.*?error'
            ],
            "authentication": [
                r'auth[a-zA-Z]*',
                r'token',
                r'encrypt',
                r'password',
                r'secret',
                r'session'
            ],
            "rate_limiting": [
                r'rate.*?limit',
                r'throttle',
                r'sleep',
                r'delay',
                r'backoff'
            ],
            "transaction_management": [
                r'transaction',
                r'commit',
                r'rollback',
                r'atomic',
                r'begin'
            ],
            "connection_pooling": [
                r'pool',
                r'connection',
                r'timeout',
                r'retry'
            ],
            "logging": [
                r'log\.[a-z]+\(',
                r'logger\.[a-z]+\(',
                r'logging\.[a-z]+\('
            ],
            "responsive_design": [
                r'responsive',
                r'media.*?query',
                r'screen.*?size',
                r'mobile',
                r'resolution'
            ],
            "accessibility": [
                r'alt',
                r'aria',
                r'accessibility',
                r'keyboard.*?navigation'
            ]
        }
        
        # Obtener patrones para este componente
        patterns = component_patterns.get(component, [])
        
        if not patterns:
            return 0
            
        # Para cada archivo, buscar evidencia de implementación
        for file_path in files:
            if not file_path.endswith('.py'):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Comprobar los patrones
                matches_count = 0
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                        matches_count += 1
                
                # Calcular qué porcentaje de patrones se encontraron
                if patterns and matches_count / len(patterns) > 0.5:
                    # Si se encontraron más de la mitad de patrones, considerar cumplido
                    items_fulfilled += 1
                    break
                    
            except Exception as e:
                logger.warning(f"Error al leer archivo {file_path}: {e}")
        
        # Asegurar que no excedemos el número de ítems
        return min(items_fulfilled, len(checklist))
    
    def _measure_quality_metrics(self, 
                               template: Dict[str, Any],
                               files: List[str]) -> Dict[str, Any]:
        """
        Medir métricas de calidad en los archivos de la funcionalidad.
        
        Args:
            template: Plantilla de verificación
            files: Lista de archivos de la funcionalidad
            
        Returns:
            Métricas de calidad
        """
        expected_metrics = template.get("quality_metrics", {})
        quality_metrics = {}
        
        # Medir documentación
        doc_coverage = self._measure_documentation_coverage(files)
        quality_metrics["documentation"] = doc_coverage
        
        # Medir test coverage si está disponible
        test_coverage = self._estimate_test_coverage(files)
        quality_metrics["test_coverage"] = test_coverage
        
        # Calcular puntuación general de calidad
        total_weight = 0
        weighted_score = 0
        
        for metric, expected_value in expected_metrics.items():
            actual_value = quality_metrics.get(metric, 0)
            ratio = min(actual_value / expected_value, 1.0) if expected_value > 0 else 0
            weighted_score += ratio * 100
            total_weight += 1
        
        quality_score = 0
        if total_weight > 0:
            quality_score = int(weighted_score / total_weight)
        
        return {
            "quality_metrics": quality_metrics,
            "quality_score": quality_score
        }
    
    def _measure_documentation_coverage(self, files: List[str]) -> int:
        """
        Medir cobertura de documentación en archivos.
        
        Args:
            files: Lista de archivos a analizar
            
        Returns:
            Porcentaje estimado de cobertura de documentación
        """
        total_functions = 0
        documented_functions = 0
        
        # Patrones para detectar funciones y sus docstrings
        function_pattern = re.compile(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')
        docstring_pattern = re.compile(r'def\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(.*?\).*?:\s*\n\s*[\'"]')
        
        for file_path in files:
            if not file_path.endswith('.py'):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Contar funciones
                functions = function_pattern.findall(content)
                total_functions += len(functions)
                
                # Contar docstrings
                docstrings = docstring_pattern.findall(content)
                documented_functions += len(docstrings)
                
            except Exception as e:
                logger.warning(f"Error al leer archivo {file_path}: {e}")
        
        # Calcular porcentaje
        doc_coverage = 0
        if total_functions > 0:
            doc_coverage = int((documented_functions / total_functions) * 100)
        
        return doc_coverage
    
    def _estimate_test_coverage(self, files: List[str]) -> int:
        """
        Estimar cobertura de tests para los archivos dados.
        
        Args:
            files: Lista de archivos a analizar
            
        Returns:
            Porcentaje estimado de cobertura de tests
        """
        # Esta es una estimación muy básica
        # Una implementación real usaría herramientas como coverage.py
        
        module_names = set()
        
        # Extraer nombres de módulos/clases
        for file_path in files:
            if not file_path.endswith('.py'):
                continue
                
            try:
                # Obtener nombre del módulo del archivo
                file_name = os.path.basename(file_path)
                module_name, _ = os.path.splitext(file_name)
                module_names.add(module_name)
                
            except Exception as e:
                logger.warning(f"Error al procesar archivo {file_path}: {e}")
        
        # Buscar archivos de test correspondientes
        test_files_found = 0
        
        for module in module_names:
            # Verificar diferentes patrones de nombres de test
            test_patterns = [
                f"test_{module}.py",
                f"{module}_test.py",
                f"tests_{module}.py"
            ]
            
            # Buscar en posibles directorios de test
            test_directories = [
                os.path.dirname(f) for f in files
            ]
            test_directories += [
                os.path.join(d, "tests") for d in test_directories
            ]
            test_directories += [
                os.path.join(os.path.dirname(d), "tests") for d in test_directories
            ]
            
            # Eliminar duplicados
            test_directories = list(set(test_directories))
            
            # Buscar archivos de test
            for test_dir in test_directories:
                if not os.path.exists(test_dir):
                    continue
                    
                for test_pattern in test_patterns:
                    test_path = os.path.join(test_dir, test_pattern)
                    if os.path.exists(test_path):
                        test_files_found += 1
                        break
        
        # Calcular cobertura estimada
        test_coverage = 0
        if module_names:
            # Básicamente, cuántos módulos tienen archivos de test
            test_coverage = int((test_files_found / len(module_names)) * 100)
        
        return test_coverage
    
    def _verify_project_checklist(self, 
                               project_path: str, 
                               project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verificar checklist a nivel de proyecto.
        
        Args:
            project_path: Ruta al proyecto
            project_data: Datos del proyecto
            
        Returns:
            Resultado de verificación de checklist del proyecto
        """
        # Checklist básico para cualquier proyecto
        project_checklist = {
            "readme_exists": False,
            "license_exists": False,
            "gitignore_exists": False,
            "requirements_exists": False,
            "tests_directory_exists": False,
            "ci_configuration_exists": False,
            "documentation_exists": False,
            "error_handling": False
        }
        
        # Verificar README
        readme_paths = ['README.md', 'README.rst', 'README', 'README.txt']
        for readme in readme_paths:
            if os.path.exists(os.path.join(project_path, readme)):
                project_checklist["readme_exists"] = True
                break
                
        # Verificar LICENSE
        license_paths = ['LICENSE', 'LICENSE.md', 'LICENSE.txt']
        for license_file in license_paths:
            if os.path.exists(os.path.join(project_path, license_file)):
                project_checklist["license_exists"] = True
                break
                
        # Verificar .gitignore
        if os.path.exists(os.path.join(project_path, '.gitignore')):
            project_checklist["gitignore_exists"] = True
            
        # Verificar requirements
        req_paths = ['requirements.txt', 'setup.py', 'pyproject.toml']
        for req in req_paths:
            if os.path.exists(os.path.join(project_path, req)):
                project_checklist["requirements_exists"] = True
                break
                
        # Verificar directorio de tests
        test_paths = ['tests', 'test']
        for test_dir in test_paths:
            if os.path.exists(os.path.join(project_path, test_dir)):
                project_checklist["tests_directory_exists"] = True
                break
                
        # Verificar configuración CI
        ci_paths = ['.github/workflows', '.gitlab-ci.yml', '.travis.yml', 'azure-pipelines.yml']
        for ci_path in ci_paths:
            if os.path.exists(os.path.join(project_path, ci_path)):
                project_checklist["ci_configuration_exists"] = True
                break
                
        # Verificar documentación
        doc_paths = ['docs', 'doc', 'documentation']
        for doc_dir in doc_paths:
            if os.path.exists(os.path.join(project_path, doc_dir)):
                project_checklist["documentation_exists"] = True
                break
                
        # Verificar manejo de errores en el código
        # Análisis básico en archivos Python
        try:
            python_files = [f for f in project_data.get("files", []) if f.endswith('.py')]
            for file_path in python_files[:20]:  # Limitar a los primeros 20 archivos
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if re.search(r'try\s*:.*?except', content, re.DOTALL):
                        project_checklist["error_handling"] = True
                        break
        except Exception as e:
            logger.warning(f"Error al analizar manejo de errores: {e}")
        
        # Calcular puntuación de checklist
        total_items = len(project_checklist)
        fulfilled_items = sum(1 for value in project_checklist.values() if value)
        
        checklist_score = 0
        if total_items > 0:
            checklist_score = int((fulfilled_items / total_items) * 100)
        
        return {
            "checklist_items": project_checklist,
            "checklist_score": checklist_score,
            "fulfilled_items": fulfilled_items,
            "total_items": total_items
        }
    
    def _generate_improvement_suggestions(self, result: Dict[str, Any]) -> List[str]:
        """
        Generar sugerencias de mejora basadas en los resultados.
        
        Args:
            result: Resultado de la verificación
            
        Returns:
            Lista de sugerencias de mejora
        """
        suggestions = []
        
        # Sugerir crear archivos faltantes
        for file_info in result.get("missing_files", []):
            suggestions.append(
                f"Crear archivo(s) para el patrón '{file_info['pattern']}'. "
                f"Sugerencias: {', '.join(file_info['suggestions'])}"
            )
        
        # Sugerir implementar funciones faltantes
        for func_info in result.get("missing_functions", []):
            suggestions.append(
                f"Implementar función '{func_info['function']}'. "
                f"Nombres posibles: {', '.join(func_info['suggestions'])}"
            )
        
        # Sugerir completar componentes incompletos
        for comp_info in result.get("incomplete_components", []):
            component = comp_info["component"]
            component_results = result.get("checklist_results", {}).get(component, {})
            checklist = component_results.get("checklist", [])
            
            if checklist:
                checklist_str = "\n   - ".join([""] + checklist)
                suggestions.append(
                    f"Completar implementación del componente '{component}' "
                    f"(actualmente {comp_info['fulfillment_percentage']}% completo). "
                    f"Verificar los siguientes puntos:{checklist_str}"
                )
        
        # Sugerir mejorar calidad del código
        quality_metrics = result.get("quality_metrics", {})
        
        if quality_metrics.get("documentation", 0) < 50:
            suggestions.append(
                "Mejorar la documentación del código. Añadir docstrings a funciones "
                "y clases, explicando parámetros, retornos y excepciones."
            )
            
        if quality_metrics.get("test_coverage", 0) < 50:
            suggestions.append(
                "Aumentar la cobertura de tests. Crear tests unitarios para los "
                "módulos principales y funcionalidades críticas."
            )
            
        # Añadir sugerencias premium para usuarios premium
        if self.is_premium and result.get("completeness_score", 0) < 80:
            suggestions.append(
                "💡 Optimización Premium: Considere refactorizar el código para mejorar "
                "la cohesión y reducir el acoplamiento entre componentes."
            )
            
        return suggestions
    
    def _generate_project_recommendations(self, 
                                       average_score: int, 
                                       functionality_results: Dict[str, Any]) -> List[str]:
        """
        Generar recomendaciones a nivel de proyecto.
        
        Args:
            average_score: Puntuación promedio de completitud
            functionality_results: Resultados por funcionalidad
            
        Returns:
            Lista de recomendaciones para el proyecto
        """
        recommendations = []
        
        # Evaluar puntuación general
        if average_score < 40:
            recommendations.append(
                "⚠️ Implementación en fase inicial con carencias significativas. "
                "Enfóquese en completar los componentes básicos primero."
            )
        elif average_score < 70:
            recommendations.append(
                "🔄 Implementación en progreso con aspectos pendientes. "
                "Revise las sugerencias específicas para cada funcionalidad."
            )
        else:
            recommendations.append(
                "✅ Implementación en buen estado general. "
                "Considere optimizaciones y refinamientos adicionales."
            )
        
        # Identificar funcionalidades más incompletas (prioridades)
        incomplete_funcs = []
        for name, result in functionality_results.items():
            score = result.get("completeness_score", 0)
            if score < 50:
                incomplete_funcs.append((name, score))
        
        # Ordenar por puntuación ascendente
        incomplete_funcs.sort(key=lambda x: x[1])
        
        # Sugerir prioridades
        if incomplete_funcs:
            func_list = ", ".join(f"{name} ({score}%)" for name, score in incomplete_funcs[:3])
            recommendations.append(
                f"🚩 Prioridad: Complete la implementación de las siguientes "
                f"funcionalidades: {func_list}"
            )
        
        # Recomendación sobre tests
        test_coverages = []
        for result in functionality_results.values():
            test_coverage = result.get("quality_metrics", {}).get("test_coverage", 0)
            test_coverages.append(test_coverage)
        
        avg_test_coverage = 0
        if test_coverages:
            avg_test_coverage = sum(test_coverages) / len(test_coverages)
            
        if avg_test_coverage < 30:
            recommendations.append(
                "🧪 Cobertura de tests muy baja. Implemente tests unitarios "
                "para las funcionalidades principales."
            )
        elif avg_test_coverage < 60:
            recommendations.append(
                "🧪 Cobertura de tests moderada. Considere ampliar los tests "
                "para cubrir más casos de uso y condiciones de borde."
            )
        
        # Recomendaciones premium
        if self.is_premium:
            recommendations.append(
                "💎 Análisis Premium: Considere integrar herramientas de análisis "
                "estático de código como SonarQube o Pylint para mejorar la calidad."
            )
        
        return recommendations


def get_completeness_verifier(config: Optional[Dict[str, Any]] = None) -> CompletenessVerifier:
    """
    Obtener instancia del verificador de completitud.
    
    Args:
        config: Configuración adicional para el verificador
        
    Returns:
        Instancia de CompletenessVerifier
    """
    return CompletenessVerifier(config)