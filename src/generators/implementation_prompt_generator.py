#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generador de prompts para implementación detallada.

Este módulo contiene clases y funciones para generar prompts
específicos para guiar la implementación de funcionalidades,
incluyendo pasos detallados, ejemplos de código y consideraciones
arquitectónicas.
"""

import os
import re
import json
import random
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set, Union
import string

from src.utils.logger import get_logger
from src.analyzers.project_scanner import get_project_scanner
from src.analyzers.functionality_detector import get_functionality_detector
from src.analyzers.connection_analyzer import get_connection_analyzer
from src.analyzers.file_analyzer import get_file_analyzer
from src.generators.contextual_prompt_generator import ContextualPromptGenerator
from src.templates.implementation_templates import (
    IMPLEMENTATION_INSTRUCTION_TEMPLATE, 
    DESIGN_PATTERNS,
    CODE_PATTERNS,
    LIBRARY_REFERENCES,
    ARCHITECTURE_CONSIDERATIONS,
    CODE_DOCUMENTATION_TEMPLATES,
    SECURITY_CONSIDERATIONS,
    PERFORMANCE_CONSIDERATIONS,
    PREMIUM_TEMPLATES
)

# Configurar logger
logger = get_logger()

# Definir excepción personalizada para errores de integración
class IntegrationError(Exception):
    """Excepción para errores de integración con sistemas externos."""
    pass


class ImplementationPromptGenerator(ContextualPromptGenerator):
    """
    Generador de prompts premium para implementación de funcionalidades.
    
    Esta clase extiende el generador contextual de prompts y añade
    funcionalidades específicas para generar guías de implementación
    paso a paso con ejemplos de código, patrones arquitectónicos y
    consideraciones técnicas.
    """
    
    def __init__(self, is_premium: bool = False):
        """
        Inicializar el generador de prompts de implementación.
        
        Args:
            is_premium: Si el usuario tiene acceso premium
        """
        super().__init__(is_premium)
        self.file_analyzer = get_file_analyzer()
        
        # Premium features now available for all users
        self.is_premium = True
        
    def generate_implementation_prompt(self, project_path: str, feature_name: str) -> Dict[str, Any]:
        """
        Genera un prompt detallado para guiar la implementación de una funcionalidad.
        
        Args:
            project_path: Ruta al proyecto
            feature_name: Nombre de la funcionalidad a implementar
            
        Returns:
            Diccionario con la información generada
        """
        if not self.is_premium:
            logger.warning("La generación de prompts de implementación es una característica premium")
            return {
                "success": False,
                "error": "premium_required",
                "message": "La generación de prompts de implementación requiere una suscripción premium."
            }
        
        try:
            # Premium features now available for all users - no usage limits
                
            # Analizar el proyecto
            project_data = self.scanner.scan_project(project_path)
            project_name = os.path.basename(project_path)
            
            # Detectar funcionalidades
            functionality_data = self.functionality_detector.detect_functionalities(project_path)
            main_functionalities = functionality_data.get('main_functionalities', [])
            detected_features = functionality_data.get('detected', {})
            
            # Determinar tipo de proyecto y lenguajes principales
            main_languages = project_data.get('languages', {})
            main_language = next(iter(main_languages)) if main_languages else "python"
            
            # Obtener frameworks usados
            frameworks = self._detect_frameworks(project_data)
            
            # Analizar la funcionalidad solicitada
            feature_info = self._analyze_feature(feature_name, project_path, detected_features)
            
            # Determinar el tipo de aplicación para consideraciones arquitectónicas
            app_type = self._detect_app_type(project_data, frameworks)
            
            # Generar prompt de implementación
            implementation_prompt = self._generate_implementation_guide(
                project_name=project_name,
                feature_name=feature_name,
                feature_info=feature_info,
                main_language=main_language,
                frameworks=frameworks,
                app_type=app_type,
                project_data=project_data
            )
            
            # Recopilar información de archivos relacionados
            related_files = self._find_related_files(feature_name, project_path)
            
            # Generar prompts adicionales si corresponde
            integration_prompt = None
            testing_prompt = None
            
            if random.random() < 0.7:  # 70% de probabilidad de generar prompt de integración
                integration_prompt = self._generate_integration_guide(
                    feature_name=feature_name,
                    feature_info=feature_info,
                    main_language=main_language,
                    frameworks=frameworks,
                    related_files=related_files
                )
            
            if random.random() < 0.7:  # 70% de probabilidad de generar prompt de pruebas
                testing_prompt = self._generate_testing_guide(
                    feature_name=feature_name,
                    feature_info=feature_info,
                    main_language=main_language,
                    frameworks=frameworks
                )
            
            return {
                "success": True,
                "prompts": {
                    "implementation": implementation_prompt,
                    "integration": integration_prompt,
                    "testing": testing_prompt
                },
                "feature_info": feature_info,
                "related_files": related_files
            }
            
        except Exception as e:
            logger.error(f"Error al generar prompt de implementación: {e}")
            return {
                "success": False,
                "error": "generation_error",
                "message": f"Error al generar prompt de implementación: {str(e)}"
            }
    
    def _analyze_feature(self, feature_name: str, project_path: str, detected_features: Dict) -> Dict[str, Any]:
        """
        Analiza una funcionalidad específica para obtener información relevante.
        
        Args:
            feature_name: Nombre de la funcionalidad
            project_path: Ruta al proyecto
            detected_features: Diccionario de funcionalidades detectadas
            
        Returns:
            Diccionario con información sobre la funcionalidad
        """
        # Normalizar el nombre de la característica
        normalized_name = feature_name.lower().strip()
        
        # Buscar coincidencia en las funcionalidades detectadas
        feature_data = {}
        for name, data in detected_features.items():
            if name.lower() == normalized_name:
                feature_data = data
                break
        
        # Si no hay coincidencia, crear información básica
        if not feature_data:
            return {
                "name": feature_name,
                "description": f"Implementación de {feature_name}",
                "confidence": 0,
                "present": False,
                "evidence": {
                    "imports": [],
                    "files": [],
                    "patterns": []
                }
            }
            
        return feature_data
    
    def _detect_frameworks(self, project_data: Dict) -> Dict[str, List[str]]:
        """
        Detecta frameworks utilizados en el proyecto.
        
        Args:
            project_data: Datos del proyecto
            
        Returns:
            Diccionario con frameworks por lenguaje
        """
        frameworks = {}
        dependencies = project_data.get('dependencies', {})
        
        # Detectar frameworks para cada lenguaje
        for lang, deps in dependencies.items():
            if not deps:
                continue
                
            frameworks[lang] = []
            
            # Python
            if lang == "python":
                python_web_frameworks = ["django", "flask", "fastapi", "tornado", "pyramid", "bottle"]
                python_data_frameworks = ["pandas", "numpy", "scipy", "matplotlib", "tensorflow", "pytorch"]
                
                for dep in deps:
                    if dep.lower() in python_web_frameworks:
                        frameworks[lang].append(dep)
                    if dep.lower() in python_data_frameworks:
                        frameworks[lang].append(dep)
            
            # JavaScript
            elif lang == "javascript" or lang == "typescript":
                js_frontend_frameworks = ["react", "vue", "angular", "svelte"]
                js_backend_frameworks = ["express", "koa", "nest", "next"]
                
                for dep in deps:
                    if dep.lower() in js_frontend_frameworks:
                        frameworks[lang].append(dep)
                    if dep.lower() in js_backend_frameworks:
                        frameworks[lang].append(dep)
            
            # Otros lenguajes
            else:
                # Detectar frameworks conocidos genéricos
                common_frameworks = ["spring", "hibernate", "rails", "laravel", "dotnet", "aspnet"]
                for dep in deps:
                    if any(fw in dep.lower() for fw in common_frameworks):
                        frameworks[lang].append(dep)
                        
        return frameworks
    
    def _detect_app_type(self, project_data: Dict, frameworks: Dict[str, List[str]]) -> str:
        """
        Detecta el tipo de aplicación basado en los frameworks y estructura.
        
        Args:
            project_data: Datos del proyecto
            frameworks: Frameworks detectados
            
        Returns:
            Tipo de aplicación (web_api, frontend, microservice, etc.)
        """
        # Verificar estructura de directorios y archivos clave
        important_files = project_data.get('important_files', {})
        file_paths = []
        for category, files in important_files.items():
            file_paths.extend(files)
        
        # Detectar si es API web
        api_indicators = ["api", "controller", "endpoint", "route"]
        if any(any(indicator in os.path.basename(f).lower() for indicator in api_indicators) for f in file_paths):
            return "web_api"
            
        # Detectar si es frontend
        frontend_indicators = ["component", "view", "template", "page"]
        has_frontend_files = any(any(indicator in os.path.basename(f).lower() for indicator in frontend_indicators) for f in file_paths)
        
        has_frontend_framework = False
        for lang, fws in frameworks.items():
            if any(fw.lower() in ["react", "vue", "angular", "svelte"] for fw in fws):
                has_frontend_framework = True
                break
                
        if has_frontend_files or has_frontend_framework:
            return "frontend"
            
        # Detectar si son microservicios
        service_indicators = ["service", "microservice"]
        if any(any(indicator in os.path.basename(f).lower() for indicator in service_indicators) for f in file_paths):
            return "microservice"
            
        # Por defecto, asumir API web
        return "web_api"
    
    def _find_related_files(self, feature_name: str, project_path: str) -> List[Dict[str, Any]]:
        """
        Encuentra archivos relacionados con la funcionalidad.
        
        Args:
            feature_name: Nombre de la funcionalidad
            project_path: Ruta al proyecto
            
        Returns:
            Lista de diccionarios con información sobre archivos relacionados
        """
        related_files = []
        
        # Normalizar nombre para búsqueda
        search_terms = self._generate_search_terms(feature_name)
        
        # Buscar archivos relacionados
        for root, _, files in os.walk(project_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                
                # Ignorar directorios comunes que no contienen código fuente
                if any(part for part in file_path.split(os.path.sep) if part in [".git", "node_modules", "venv", "__pycache__"]):
                    continue
                
                # Verificar si el archivo está relacionado por nombre
                file_base = os.path.splitext(file_name)[0].lower()
                if any(term in file_base for term in search_terms):
                    try:
                        # Analizar el contenido del archivo
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        related_files.append({
                            "path": os.path.relpath(file_path, project_path),
                            "name": file_name,
                            "relevance": "high",
                            "content_preview": content[:500] + "..." if len(content) > 500 else content
                        })
                    except Exception as e:
                        logger.debug(f"No se pudo leer el archivo {file_path}: {e}")
                        
        return related_files
    
    def _generate_search_terms(self, feature_name: str) -> List[str]:
        """
        Genera diferentes variantes del nombre de la funcionalidad para búsqueda.
        
        Args:
            feature_name: Nombre de la funcionalidad
            
        Returns:
            Lista de términos de búsqueda
        """
        name = feature_name.lower()
        
        # Generar variantes
        result = [name]
        
        # Separar palabras
        words = re.split(r'[-_\s]', name)
        if len(words) > 1:
            result.append('_'.join(words))  # snake_case
            result.append('-'.join(words))  # kebab-case
            result.append(''.join(w.capitalize() for w in words))  # PascalCase
            result.append(words[0] + ''.join(w.capitalize() for w in words[1:]))  # camelCase
        
        # Singulares/plurales básicos
        if name.endswith('s'):
            result.append(name[:-1])
        else:
            result.append(name + 's')
            
        return result
    
    def _format_feature_name(self, feature_name: str, format_type: str) -> str:
        """
        Formatea el nombre de la característica según el formato requerido.
        
        Args:
            feature_name: Nombre original de la característica
            format_type: Tipo de formato (snake, camel, pascal)
            
        Returns:
            Nombre formateado
        """
        # Normalizar: separar por espacios, guiones o guiones bajos
        words = re.split(r'[-_\s]', feature_name.lower())
        
        if format_type == "snake":
            return '_'.join(words)
        elif format_type == "camel":
            return words[0] + ''.join(w.capitalize() for w in words[1:])
        elif format_type == "pascal":
            return ''.join(w.capitalize() for w in words)
        elif format_type == "kebab":
            return '-'.join(words)
        else:
            return feature_name
    
    def _generate_implementation_guide(self, project_name: str, feature_name: str, feature_info: Dict,
                                     main_language: str, frameworks: Dict[str, List[str]], 
                                     app_type: str, project_data: Dict) -> str:
        """
        Genera una guía detallada para implementación.
        
        Args:
            project_name: Nombre del proyecto
            feature_name: Nombre de la funcionalidad
            feature_info: Información sobre la funcionalidad
            main_language: Lenguaje principal del proyecto
            frameworks: Frameworks detectados
            app_type: Tipo de aplicación
            project_data: Datos del proyecto
        
        Returns:
            Prompt con guía de implementación
        """
        # Preparar variables para la plantilla
        feature_description = feature_info.get("description", f"Implementación de {feature_name}")
        
        # Formatear nombres para código
        feature_name_snake = self._format_feature_name(feature_name, "snake")
        feature_name_camel = self._format_feature_name(feature_name, "camel")
        feature_name_pascal = self._format_feature_name(feature_name, "pascal")
        feature_path = self._format_feature_name(feature_name, "kebab")
        feature_variable = self._format_feature_name(feature_name, "camel")
        
        # Detectar frameworks específicos del lenguaje
        frameworks_list = []
        for lang, fws in frameworks.items():
            frameworks_list.extend(fws)
        
        frameworks_str = ", ".join(frameworks_list) if frameworks_list else "No se detectaron frameworks"
        
        # Obtener consideraciones arquitectónicas según el tipo de app
        architecture_desc = ARCHITECTURE_CONSIDERATIONS.get(app_type, "")
        
        # Seleccionar patrones de diseño relevantes
        design_patterns = []
        suggested_patterns = []
        
        if app_type == "web_api":
            suggested_patterns = ["repository", "factory", "strategy"]
        elif app_type == "frontend":
            suggested_patterns = ["observer", "strategy", "factory"]
        else:
            suggested_patterns = ["factory", "strategy", "repository"]
            
        # Elegir patrones relevantes y formatear según el lenguaje
        for pattern in suggested_patterns:
            if pattern in DESIGN_PATTERNS:
                pattern_info = DESIGN_PATTERNS[pattern]
                example = pattern_info["example"].format(
                    language=main_language,
                    feature_name=feature_name,
                    feature_name_pascal=feature_name_pascal,
                    feature_name_camel=feature_name_camel
                )
                design_patterns.append(f"### {pattern_info['name']}\n\n{pattern_info['description']}\n\n{example}")
                
        design_patterns_text = "\n\n".join(design_patterns)
        
        # Generar ejemplos de código según el tipo de app y lenguaje
        code_examples = {}
        
        if app_type == "web_api":
            if main_language == "python":
                if "flask" in frameworks_list:
                    code_examples["api"] = CODE_PATTERNS["api_endpoint"]["python_flask"]
                elif "fastapi" in frameworks_list:
                    code_examples["api"] = CODE_PATTERNS["api_endpoint"]["python_fastapi"]
                else:
                    code_examples["api"] = CODE_PATTERNS["api_endpoint"]["python_flask"]
                    
                code_examples["model"] = CODE_PATTERNS["database_model"]["python_sqlalchemy"]
                code_examples["service"] = CODE_PATTERNS["service_layer"]["python"]
                code_examples["test"] = CODE_PATTERNS["test_suite"]["python_pytest"]
            
            elif main_language in ["javascript", "typescript"]:
                code_examples["api"] = CODE_PATTERNS["api_endpoint"]["javascript_express"]
                code_examples["model"] = CODE_PATTERNS["database_model"]["typescript_typeorm"]
                code_examples["service"] = CODE_PATTERNS["service_layer"]["typescript"]
                code_examples["test"] = CODE_PATTERNS["test_suite"]["typescript_jest"]
        
        # Formatear los ejemplos de código
        for key, code in code_examples.items():
            code_examples[key] = code.format(
                feature_name=feature_name,
                feature_name_snake=feature_name_snake,
                feature_name_camel=feature_name_camel,
                feature_name_pascal=feature_name_pascal,
                feature_path=feature_path,
                feature_variable=feature_variable,
                module_path=f"{project_name}.{feature_name_snake}"
            )
        
        # Seleccionar bibliotecas relevantes
        libraries = []
        if main_language in LIBRARY_REFERENCES:
            for category, libs in LIBRARY_REFERENCES[main_language].items():
                if len(libs) > 3:
                    selected = random.sample(libs, 3)
                else:
                    selected = libs
                libraries.append(f"**{category.capitalize()}**: {', '.join(selected)}")
        
        libraries_text = "\n".join(libraries) if libraries else "No se sugieren bibliotecas específicas."
        
        # Seleccionar consideraciones de seguridad y rendimiento
        security = random.sample(SECURITY_CONSIDERATIONS, min(4, len(SECURITY_CONSIDERATIONS)))
        performance = random.sample(PERFORMANCE_CONSIDERATIONS, min(4, len(PERFORMANCE_CONSIDERATIONS)))
        
        security_text = "- " + "\n- ".join(security)
        performance_text = "- " + "\n- ".join(performance)
        
        # Construir la guía completa
        guide = PREMIUM_TEMPLATES["implementation_guide"].format(
            feature_name=feature_name,
            project_name=project_name,
            project_type=app_type.replace("_", " ").title(),
            main_languages=main_language.capitalize(),
            detected_frameworks=frameworks_str,
            feature_description=feature_description,
            related_components="- " + "\n- ".join([f"`{f['name']}`" for f in feature_info.get("related_components", [])[:5]]) 
                if "related_components" in feature_info else "No se detectaron componentes relacionados.",
            required_dependencies="- " + "\n- ".join([f"`{d}`" for d in feature_info.get("dependencies", [])[:5]])
                if "dependencies" in feature_info else "No se detectaron dependencias específicas.",
            architecture_description=architecture_desc,
            preparation_code=code_examples.get("setup", "# Código de preparación no disponible para esta configuración"),
            data_structure_code=code_examples.get("model", "# Modelo de datos no disponible para esta configuración"),
            business_logic_code=code_examples.get("service", "# Lógica de negocio no disponible para esta configuración"),
            interface_code=code_examples.get("api", "# Código de interfaz no disponible para esta configuración"),
            test_code=code_examples.get("test", "# Código de prueba no disponible para esta configuración"),
            design_patterns=design_patterns_text,
            performance_considerations=performance_text,
            security_considerations=security_text,
            scalability_considerations="- Considerar patrones de caché para mejorar rendimiento\n"
                                     "- Diseñar para escalabilidad horizontal\n"
                                     "- Implementar monitoreo y telemetría",
            references=libraries_text,
            additional_notes="Esta guía es generada automáticamente basada en el análisis del proyecto. "
                           "Adaptarla según las necesidades específicas del caso."
        )
        
        return guide
    
    def _generate_integration_guide(self, feature_name: str, feature_info: Dict, main_language: str,
                                  frameworks: List[str], related_files: List[Dict]) -> Optional[str]:
        """
        Genera una guía de integración para la funcionalidad.
        
        Args:
            feature_name: Nombre de la funcionalidad
            feature_info: Información sobre la funcionalidad
            main_language: Lenguaje principal del proyecto
            frameworks: Frameworks detectados
            related_files: Archivos relacionados
            
        Returns:
            Prompt con guía de integración o None si no aplica
        """
        # Simular un sistema con el que integrar
        integrated_systems = {
            "python": ["Django REST API", "PostgreSQL Database", "Redis Cache", "Celery Task Queue"],
            "javascript": ["Express.js API", "MongoDB Database", "Redis Cache", "Socket.io"],
            "typescript": ["NestJS API", "TypeORM Database", "Redis Cache", "GraphQL API"],
            "java": ["Spring Boot API", "MySQL Database", "Kafka Message Queue", "Elasticsearch"]
        }
        
        # Seleccionar un sistema para integración
        default_systems = ["REST API", "Database", "Cache Service", "Message Queue"]
        systems = integrated_systems.get(main_language, default_systems)
        integrated_system = random.choice(systems)
        
        # Decidir tipo de integración
        integration_types = ["API REST", "Base de datos", "Mensajería asíncrona", "Caché distribuida", "Eventos"]
        integration_type = random.choice(integration_types)
        
        # Formatear nombres para código
        feature_name_snake = self._format_feature_name(feature_name, "snake")
        feature_name_camel = self._format_feature_name(feature_name, "camel")
        feature_name_pascal = self._format_feature_name(feature_name, "pascal")
        
        # Generar un diagrama de flujo sencillo en ASCII
        flow_diagram = f"""
+----------------+      +----------------+      +----------------+
|                |      |                |      |                |
|  {feature_name_pascal:<12} +----->+ Integration    +----->+  {integrated_system:<12} |
|  Component     |      |  Layer        |      |  Service       |
|                |      |                |      |                |
+----------------+      +----------------+      +----------------+
         |                                              ^
         |                                              |
         |                    +----------------+        |
         |                    |                |        |
         +-------------------->  Error        +--------+
                              |  Handling     |
                              |                |
                              +----------------+
"""
        
        # Generar código de ejemplo según el tipo de integración y el lenguaje
        credentials_code = ""
        adapter_code = ""
        event_handling_code = ""
        data_transformation_code = ""
        error_handling_code = ""
        integration_test_code = ""
        
        # Código de credenciales
        if main_language == "python":
            credentials_code = f"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

{integrated_system.upper().replace(' ', '_')}_API_KEY = os.getenv("{integrated_system.upper().replace(' ', '_')}_API_KEY")
{integrated_system.upper().replace(' ', '_')}_URL = os.getenv("{integrated_system.upper().replace(' ', '_')}_URL")

# Validar configuración
if not {integrated_system.upper().replace(' ', '_')}_API_KEY:
    raise ValueError("La clave API para {integrated_system} no está configurada")

if not {integrated_system.upper().replace(' ', '_')}_URL:
    raise ValueError("La URL para {integrated_system} no está configurada")
"""
        elif main_language in ["javascript", "typescript"]:
            credentials_code = f"""
import dotenv from 'dotenv';

// Cargar variables de entorno
dotenv.config();

const {integrated_system.upper().replace(' ', '_')}_API_KEY = process.env.{integrated_system.upper().replace(' ', '_')}_API_KEY;
const {integrated_system.upper().replace(' ', '_')}_URL = process.env.{integrated_system.upper().replace(' ', '_')}_URL;

// Validar configuración
if (!{integrated_system.upper().replace(' ', '_')}_API_KEY) {{
  throw new Error("La clave API para {integrated_system} no está configurada");
}}

if (!{integrated_system.upper().replace(' ', '_')}_URL) {{
  throw new Error("La URL para {integrated_system} no está configurada");
}}
"""
        
        # Código del adaptador
        if main_language == "python":
            adapter_code = f"""
import requests
from typing import Dict, Any, Optional

class {feature_name_pascal}{integrated_system.replace(' ', '')}Adapter:
    \"\"\"
    Adaptador para integración con {integrated_system}.
    \"\"\"
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {{
            "Authorization": f"Bearer {{api_key}}",
            "Content-Type": "application/json"
        }}
    
    def get_{feature_name_snake}_data(self, {feature_name_snake}_id: str) -> Dict[str, Any]:
        \"\"\"
        Obtiene datos de {feature_name} desde {integrated_system}.
        \"\"\"
        url = f"{self.base_url}/api/{feature_name_snake}s/{feature_name_snake}_id"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise IntegrationError(f"Error al obtener datos de {integrated_system}: {{str(e)}}")
    
    def create_{feature_name_snake}(self, data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        Crea un nuevo {feature_name} en {integrated_system}.
        \"\"\"
        url = f"{self.base_url}/api/{feature_name_snake}s"
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise IntegrationError(f"Error al crear {feature_name} en {integrated_system}: {{str(e)}}")
"""
        elif main_language in ["javascript", "typescript"]:
            adapter_code = f"""
import axios from 'axios';

class {feature_name_pascal}{integrated_system.replace(' ', '')}Adapter {{
  /**
   * Adaptador para integración con {integrated_system}.
   */
  private apiKey: string;
  private baseUrl: string;
  private headers: any;
  
  constructor(apiKey: string, baseUrl: string) {{
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
    this.headers = {{
      'Authorization': 'Bearer ' + apiKey,
      'Content-Type': 'application/json'
    }};
  }}
  
  async get{feature_name_pascal}Data({feature_name_camel}Id: string): Promise<any> {{
    /**
     * Obtiene datos de {feature_name} desde {integrated_system}.
     */
    const url = this.baseUrl + '/api/{feature_name_snake}s/' + {feature_name_camel}Id;
    
    try {{
      const response = await axios.get(url, {{ headers: this.headers }});
      return response.data;
    }} catch (error) {{
      throw new IntegrationError('Error al obtener datos de {integrated_system}: ' + error.message);
    }}
  }}
  
  async create{feature_name_pascal}(data: any): Promise<any> {{
    /**
     * Crea un nuevo {feature_name} en {integrated_system}.
     */
    const url = this.baseUrl + '/api/{feature_name_snake}s';
    
    try {{
      const response = await axios.post(url, data, {{ headers: this.headers }});
      return response.data;
    }} catch (error) {{
      throw new IntegrationError('Error al crear {feature_name} en {integrated_system}: ' + error.message);
    }}
  }}
}}
"""
        
        # Guía completa de integración
        guide = PREMIUM_TEMPLATES["integration_steps"].format(
            feature_name=feature_name,
            integrated_system=integrated_system,
            integration_objective=f"Integrar la funcionalidad {feature_name} con {integrated_system}",
            systems_involved=f"{feature_name_pascal} y {integrated_system}",
            integration_type=integration_type,
            flow_diagram=flow_diagram,
            prerequisites=f"- Acceso a {integrated_system}\n- Credenciales API configuradas\n- Dependencias necesarias instaladas",
            main_language=main_language,
            credentials_code=credentials_code,
            adapter_code=adapter_code,
            event_handling_code=event_handling_code or "# Código de manejo de eventos no disponible para esta configuración",
            data_transformation_code=data_transformation_code or "# Código de transformación de datos no disponible para esta configuración",
            error_handling_code=error_handling_code or "# Código de manejo de errores no disponible para esta configuración",
            integration_test_code=integration_test_code or "# Código de prueba de integración no disponible para esta configuración",
            operational_considerations="- Monitorizar rendimiento de integración\n- Implementar circuit breaker para resiliencia\n- Revisar tasas de error y latencia\n- Establecer alertas para fallos de integración",
            api_references=f"- [Documentación API de {integrated_system}](https://api.example.com/docs)\n- [SDK Cliente para {main_language}](https://github.com/example/{integrated_system.lower().replace(' ', '-')})"
        )
        
        return guide
    
    def _generate_testing_guide(self, feature_name: str, feature_info: Dict, main_language: str, 
                              frameworks: List[str]) -> Optional[str]:
        """
        Genera una guía para pruebas de la funcionalidad implementada.
        
        Args:
            feature_name: Nombre de la funcionalidad
            feature_info: Información sobre la funcionalidad
            main_language: Lenguaje principal 
            frameworks: Frameworks detectados
            
        Returns:
            Guía de pruebas o None si no aplica
        """
        # Esta función se implementará cuando se desarrolle la tarea 5.3
        return None


# Función para obtener una instancia del generador
def get_implementation_prompt_generator(is_premium: bool = False) -> ImplementationPromptGenerator:
    """
    Obtiene una instancia del generador de prompts de implementación.
    
    Args:
        is_premium: Si se debe crear una instancia con acceso premium
        
    Returns:
        Instancia del generador
    """
    return ImplementationPromptGenerator(is_premium=is_premium)
