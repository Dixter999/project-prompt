#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generador de prompts contextuales mejorados.

Este módulo contiene clases y funciones para generar prompts
contextuales más específicos basados en el análisis de proyectos,
incluyendo referencias a archivos concretos y sugerencias basadas
en patrones detectados.
"""

import os
import re
import json
import random
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set, TYPE_CHECKING

from src.utils.logger import get_logger
from src.generators.prompt_generator import PromptGenerator

# Evitar importación circular - importar en los métodos donde sea necesario
if TYPE_CHECKING:
    from src.analyzers.project_scanner import ProjectScanner
    from src.analyzers.functionality_detector import FunctionalityDetector
    from src.analyzers.connection_analyzer import ConnectionAnalyzer
    from src.analyzers.dependency_graph import DependencyGraph

# Configurar logger
logger = get_logger()


class ContextualPromptGenerator(PromptGenerator):
    """
    Generador de prompts contextuales mejorados.
    
    Esta clase extiende el generador básico de prompts y añade
    funcionalidades para generar prompts más específicos y contextuales
    basados en el análisis detallado del proyecto.
    """
    
    def __init__(self, is_premium: bool = False):
        """
        Inicializar el generador de prompts contextuales.
        
        Args:
            is_premium: Si el usuario tiene acceso premium
        """
        super().__init__(is_premium)
        self.max_prompts = 15 if is_premium else 5  # Aumentamos el límite
        
        # Importar aquí para evitar importaciones circulares
        from src.analyzers.connection_analyzer import get_connection_analyzer
        from src.analyzers.dependency_graph import get_dependency_graph
        
        self.connection_analyzer = get_connection_analyzer()
        self.dependency_graph = get_dependency_graph()
        
    def generate_prompts(self, project_path: str) -> Dict[str, Any]:
        """
        Generar prompts contextuales mejorados basados en el análisis del proyecto.
        
        Args:
            project_path: Ruta al directorio del proyecto
            
        Returns:
            Dict con los prompts generados y metadatos
        """
        # Obtener datos básicos usando la clase padre
        result = super().generate_prompts(project_path)
        prompts = result.get('prompts', {})
        
        # Análisis adicional para prompts contextuales mejorados
        project_data = self.scanner.scan_project(project_path)
        functionality_data = self.functionality_detector.detect_functionalities(project_path)
        
        try:
            # Analizar conexiones entre archivos para contexto adicional
            connections_data = self.connection_analyzer.analyze_connections(project_path)
            graph_data = self.dependency_graph.build_dependency_graph(project_path)
            
            # Añadir prompts específicos para funcionalidades detectadas
            functionality_prompts = {}
            
            for functionality in functionality_data.get('main_functionalities', []):
                functionality_prompts[functionality] = self._generate_functionality_prompt(
                    project_data, functionality_data, connections_data, graph_data, functionality
                )
            
            if functionality_prompts:
                prompts['functionality'] = functionality_prompts
            
            # Añadir prompt de arquitectura basado en el grafo de dependencias
            prompts['architecture'] = self._generate_architecture_prompt(
                project_data, connections_data, graph_data
            )
            
            # Añadir prompt de código para completar
            prompts['code_completion'] = self._generate_code_completion_prompt(
                project_data, connections_data
            )
            
            # Añadir prompt de preguntas guiadas
            prompts['guided_questions'] = self._generate_guided_questions_prompt(
                project_data, functionality_data, connections_data
            )
            
            # Limitar cantidad según versión
            prompts_to_keep = {}
            count = 0
            
            # Primero incluir los básicos (description, improvements, issues)
            for key in ['description', 'improvements', 'issues']:
                if key in prompts:
                    prompts_to_keep[key] = prompts[key]
                    count += 1
            
            # Luego añadir los mejorados hasta el límite
            for key, value in prompts.items():
                if key not in prompts_to_keep and count < self.max_prompts:
                    prompts_to_keep[key] = value
                    count += 1
            
            # Actualizar el resultado
            result['prompts'] = prompts_to_keep
            result['prompt_count'] = count
            
        except Exception as e:
            logger.error(f"Error al generar prompts contextuales: {e}", exc_info=True)
            # En caso de error, devolver al menos los prompts básicos
        
        return result

    def _generate_functionality_prompt(
        self, project_data: Dict[str, Any], 
        functionality_data: Dict[str, Any],
        connections_data: Dict[str, Any],
        graph_data: Dict[str, Any], 
        functionality: str
    ) -> str:
        """
        Generar prompt específico para una funcionalidad.
        
        Args:
            project_data: Datos del proyecto
            functionality_data: Datos de funcionalidades
            connections_data: Datos de conexiones
            graph_data: Datos del grafo de dependencias
            functionality: Nombre de la funcionalidad
            
        Returns:
            Prompt formateado
        """
        # Datos básicos del proyecto
        project_name = os.path.basename(project_data.get('project_path', ''))
        file_count = project_data.get('stats', {}).get('total_files', 0)
        timestamp = self.scanner.get_timestamp()
        main_languages = ", ".join(project_data.get('languages', {}).get('_main', ['No detectado']))
        
        # Obtener información específica de la funcionalidad
        functionality_info = functionality_data.get('detected', {}).get(functionality, {})
        confidence = functionality_info.get('confidence', 0)
        description = functionality_info.get('description', 'No hay descripción disponible')
        
        # Obtener archivos principales para esta funcionalidad
        main_files_list = []
        for file_path, file_info in functionality_info.get('files', {}).items():
            relevance = file_info.get('relevance', 0)
            if relevance > 0.5:  # Solo incluir archivos relevantes
                main_files_list.append(f"- `{file_path}` (Relevancia: {relevance:.2f})")
        
        main_files = "\n".join(main_files_list) if main_files_list else "No se identificaron archivos principales."
        
        # Extraer conexiones relacionadas con esta funcionalidad
        connections_list = []
        file_connections = connections_data.get('file_connections', {})
        
        for file_path in functionality_info.get('files', {}).keys():
            if file_path in file_connections:
                for connected_file in file_connections[file_path]:
                    connections_list.append(f"- `{file_path}` importa/usa `{connected_file}`")
        
        connections = "\n".join(connections_list) if connections_list else "No se detectaron conexiones específicas."
        
        # Detectar patrones específicos
        patterns_list = []
        
        # Patrones comunes según la funcionalidad
        if functionality == "authentication":
            patterns_list.append("- Sistema de autenticación de usuarios")
            if "database" in functionality_data.get('main_functionalities', []):
                patterns_list.append("- Almacenamiento de credenciales en base de datos")
            if "api" in functionality_data.get('main_functionalities', []):
                patterns_list.append("- API de autenticación con tokens")
                
        elif functionality == "database":
            patterns_list.append("- Acceso a base de datos")
            orm_patterns = ["ORM", "entity", "model", "schema", "repository"]
            for file_path in functionality_info.get('files', {}).keys():
                if any(pattern.lower() in file_path.lower() for pattern in orm_patterns):
                    patterns_list.append("- Uso de patrón ORM (Object-Relational Mapping)")
                    break
                    
        elif functionality == "api":
            patterns_list.append("- API para comunicación entre componentes")
            if any("controller" in file_path.lower() for file_path in functionality_info.get('files', {})):
                patterns_list.append("- Patrón Controlador para gestión de endpoints")
                
        patterns = "\n".join(patterns_list) if patterns_list else "No se detectaron patrones específicos."
        
        # Generar preguntas guiadas según la funcionalidad
        questions_list = []
        
        if functionality == "authentication":
            questions_list.append("1. ¿Qué método de autenticación se utiliza (JWT, sesiones, OAuth)?")
            questions_list.append("2. ¿Cómo se gestionan los permisos y roles de usuarios?")
            questions_list.append("3. ¿Existen mecanismos de seguridad adicionales como 2FA?")
            
        elif functionality == "database":
            questions_list.append("1. ¿Qué sistema de base de datos se utiliza?")
            questions_list.append("2. ¿Cómo se gestionan las migraciones y cambios en el esquema?")
            questions_list.append("3. ¿Se implementa alguna estrategia de caché?")
            
        elif functionality == "api":
            questions_list.append("1. ¿La API sigue principios REST o GraphQL?")
            questions_list.append("2. ¿Cómo se gestionan los errores y excepciones?")
            questions_list.append("3. ¿Existe documentación automática (Swagger, OpenAPI)?")
            
        else:
            questions_list.append(f"1. ¿Cuál es el propósito principal del módulo {functionality}?")
            questions_list.append("2. ¿Cómo se integra con el resto del sistema?")
            questions_list.append("3. ¿Qué mejoras podrían implementarse?")
        
        guided_questions = "\n".join(questions_list)
        
        # Contexto adicional
        context_parts = []
        
        # Añadir información sobre ciclos si existen
        cycles = graph_data.get('file_cycles', [])
        for cycle in cycles:
            if any(file_path in functionality_info.get('files', {}) for file_path in cycle):
                cycle_files = ", ".join(f"`{f}`" for f in cycle)
                context_parts.append(f"**Dependencia circular detectada**: {cycle_files}")
        
        # Añadir información sobre componentes conectados
        connected_components = connections_data.get('connected_components', [])
        for i, component in enumerate(connected_components[:2]):  # Solo los 2 principales
            if any(file_path in functionality_info.get('files', {}) for file_path in component):
                files_in_component = len(component)
                context_parts.append(f"**Componente conectado #{i+1}**: {files_in_component} archivos interrelacionados")
        
        additional_context = "\n\n".join(context_parts) if context_parts else "No hay contexto adicional disponible."
        
        # Leer la plantilla
        template_path = Path(__file__).parent.parent / "templates" / "prompts" / "functionality_analysis.md"
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
        except Exception as e:
            logger.error(f"Error al leer plantilla de funcionalidad: {e}")
            template = "# Análisis de {functionality_name}\n\n{functionality_description}"
        
        # Formatear y devolver
        return template.format(
            functionality_name=functionality.capitalize(),
            project_name=project_name,
            main_languages=main_languages,
            file_count=file_count,
            timestamp=timestamp,
            functionality_description=f"{description} (Confianza: {confidence}%)",
            main_files=main_files,
            connections=connections,
            patterns=patterns,
            guided_questions=guided_questions,
            additional_context=additional_context
        )
    
    def _generate_architecture_prompt(
        self, project_data: Dict[str, Any], 
        connections_data: Dict[str, Any],
        graph_data: Dict[str, Any]
    ) -> str:
        """
        Generar prompt de análisis de arquitectura.
        
        Args:
            project_data: Datos del proyecto
            connections_data: Datos de conexiones
            graph_data: Datos del grafo de dependencias
            
        Returns:
            Prompt formateado
        """
        project_name = os.path.basename(project_data.get('project_path', ''))
        
        # Extraer información de arquitectura del grafo
        nodes_count = len(graph_data.get('nodes', []))
        edges_count = len(graph_data.get('edges', []))
        density = graph_data.get('metrics', {}).get('density', 0)
        
        # Componentes conectados
        components = connections_data.get('connected_components', [])
        component_info = []
        
        for i, component in enumerate(components[:5]):  # Limitar a 5 componentes principales
            component_info.append(f"- Componente #{i+1}: {len(component)} archivos")
            
            # Archivos clave en el componente (hasta 3)
            key_files = []
            for file in component[:3]:
                key_files.append(f"  - `{file}`")
                
            component_info.extend(key_files)
        
        components_description = "\n".join(component_info) if component_info else "No se detectaron componentes conectados."
        
        # Ciclos de dependencias
        cycles = graph_data.get('file_cycles', [])
        cycles_info = []
        
        for i, cycle in enumerate(cycles[:3]):  # Limitar a 3 ciclos
            cycles_info.append(f"- Ciclo #{i+1}: {' -> '.join(f'`{f}`' for f in cycle)} -> {cycle[0]}")
            
        cycles_description = "\n".join(cycles_info) if cycles_info else "No se detectaron ciclos de dependencias."
        
        # Archivos centrales
        central_files = graph_data.get('central_files', [])
        central_files_info = []
        
        for file, score in central_files[:5]:  # Top 5 archivos centrales
            central_files_info.append(f"- `{file}` (Centralidad: {score:.2f})")
            
        central_files_description = "\n".join(central_files_info) if central_files_info else "No se detectaron archivos centrales."
        
        # Patrones arquitectónicos detectados
        architecture_patterns = []
        
        # Detectar MVC
        has_models = any("model" in f.lower() for f in graph_data.get('nodes', []))
        has_views = any("view" in f.lower() for f in graph_data.get('nodes', []))
        has_controllers = any("controller" in f.lower() for f in graph_data.get('nodes', []))
        
        if has_models and has_views and has_controllers:
            architecture_patterns.append("- Patrón MVC (Model-View-Controller)")
            
        # Detectar Repositorio
        has_repositories = any("repository" in f.lower() or "dao" in f.lower() for f in graph_data.get('nodes', []))
        has_services = any("service" in f.lower() for f in graph_data.get('nodes', []))
        
        if has_repositories and has_services:
            architecture_patterns.append("- Patrón Repositorio con Servicios")
            
        # Detectar API/Capas
        has_api = any("api" in f.lower() or "controller" in f.lower() for f in graph_data.get('nodes', []))
        has_core = any("core" in f.lower() or "domain" in f.lower() for f in graph_data.get('nodes', []))
        has_db = any("database" in f.lower() or "repository" in f.lower() for f in graph_data.get('nodes', []))
        
        if has_api and has_core and has_db:
            architecture_patterns.append("- Arquitectura por capas (API, Dominio, Persistencia)")
            
        architecture_patterns_description = "\n".join(architecture_patterns) if architecture_patterns else "No se detectaron patrones arquitectónicos claros."
        
        # Generar el prompt
        return f"""# Análisis de Arquitectura: {project_name}

## Resumen del Grafo de Dependencias
- **Archivos (nodos)**: {nodes_count}
- **Dependencias (enlaces)**: {edges_count}
- **Densidad del grafo**: {density:.2f} (0=sin conexiones, 1=todos conectados)

## Componentes Conectados
{components_description}

## Ciclos de Dependencias
{cycles_description}

## Archivos Centrales
{central_files_description}

## Patrones Arquitectónicos Detectados
{architecture_patterns_description}

## Preguntas Guiadas sobre Arquitectura
1. ¿Cuál es el propósito de los archivos centrales identificados?
2. ¿Los ciclos de dependencias son intencionados o deberían refactorizarse?
3. ¿Qué patrón arquitectónico se está siguiendo o se debería seguir?
4. ¿Cómo podría mejorarse la modularidad del proyecto?
5. ¿Las dependencias entre componentes siguen un flujo lógico?

Por favor, añade información adicional sobre la arquitectura del proyecto para un análisis más preciso.
"""

    def _generate_code_completion_prompt(
        self, project_data: Dict[str, Any],
        connections_data: Dict[str, Any]
    ) -> str:
        """
        Generar prompt para completar código basado en patrones del proyecto.
        
        Args:
            project_data: Datos del proyecto
            connections_data: Datos de conexiones
            
        Returns:
            Prompt formateado
        """
        project_name = os.path.basename(project_data.get('project_path', ''))
        main_languages = ", ".join(project_data.get('languages', {}).get('_main', ['No detectado']))
        
        # Intentar identificar patrones de código
        file_imports = connections_data.get('file_imports', {})
        
        # Seleccionar archivos representativos según su lenguaje
        language_examples = {}
        
        for file_path, file_data in file_imports.items():
            language = file_data.get('language', 'unknown')
            if language != 'unknown' and language not in language_examples:
                language_examples[language] = file_path
                
        # Construir ejemplos de código por lenguaje
        code_examples = []
        
        for language, file_path in language_examples.items():
            code_examples.append(f"### Ejemplo en {language}:")
            code_examples.append(f"Archivo: `{file_path}`")
            code_examples.append("```")
            code_examples.append(f"// Código representativo de {language} en este proyecto")
            code_examples.append("// Este es un marcador de posición para que añadas")
            code_examples.append("// un fragmento específico del archivo mencionado")
            code_examples.append("```")
            code_examples.append("")
            
        code_examples_text = "\n".join(code_examples) if code_examples else "No hay ejemplos de código disponibles."
        
        # Patrones de importación comunes
        import_patterns = {}
        
        for file_path, file_data in file_imports.items():
            language = file_data.get('language', 'unknown')
            imports = file_data.get('imports', [])
            
            if language != 'unknown' and imports:
                if language not in import_patterns:
                    import_patterns[language] = {}
                    
                for imp in imports:
                    if imp in import_patterns[language]:
                        import_patterns[language][imp] += 1
                    else:
                        import_patterns[language][imp] = 1
                        
        # Mostrar principales patrones de importación por lenguaje
        import_patterns_list = []
        
        for language, patterns in import_patterns.items():
            import_patterns_list.append(f"#### {language}:")
            
            # Ordenar por frecuencia
            sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
            
            for pattern, count in sorted_patterns[:5]:  # Top 5
                import_patterns_list.append(f"- `{pattern}` (usado {count} veces)")
                
            import_patterns_list.append("")
            
        import_patterns_text = "\n".join(import_patterns_list) if import_patterns_list else "No se detectaron patrones de importación significativos."
        
        # Generar el prompt
        return f"""# Completado de Código para {project_name}

## Análisis del Proyecto
- **Lenguajes principales**: {main_languages}
- **Archivos analizados**: {len(file_imports)}

## Patrones de Importación Comunes
{import_patterns_text}

## Ejemplos de Código Representativos
{code_examples_text}

## Instrucciones
1. Utiliza los patrones de importación mostrados arriba para mantener la consistencia
2. Sigue los ejemplos de código como referencia para el estilo y estructura
3. Implementa tu código basándote en las convenciones del proyecto

Puedes proporcionar un fragmento de código que quieras completar o mejorar, y se generarán sugerencias
que mantengan la coherencia con el resto del proyecto.
"""

    def _generate_guided_questions_prompt(
        self, project_data: Dict[str, Any],
        functionality_data: Dict[str, Any],
        connections_data: Dict[str, Any]
    ) -> str:
        """
        Generar prompt con preguntas guiadas para aclarar funcionalidades poco claras.
        
        Args:
            project_data: Datos del proyecto
            functionality_data: Datos de funcionalidades
            connections_data: Datos de conexiones
            
        Returns:
            Prompt formateado
        """
        project_name = os.path.basename(project_data.get('project_path', ''))
        
        # Identificar funcionalidades con baja confianza
        unclear_functionalities = []
        
        for functionality, data in functionality_data.get('detected', {}).items():
            confidence = data.get('confidence', 0)
            if confidence < 70:  # Confianza menor al 70%
                unclear_functionalities.append((functionality, confidence))
                
        # Generar preguntas generales sobre el proyecto
        general_questions = [
            "1. ¿Cuál es el propósito principal de este proyecto?",
            "2. ¿Cuáles son los componentes o módulos más importantes?",
            "3. ¿Qué patrones de diseño o arquitectónicos se están utilizando?",
            "4. ¿Cuáles son los flujos de datos principales?",
            "5. ¿Existen integraciones con sistemas externos?"
        ]
        
        # Generar preguntas específicas por funcionalidad poco clara
        specific_questions = []
        
        for functionality, confidence in unclear_functionalities:
            specific_questions.append(f"### Preguntas sobre {functionality.capitalize()} (Confianza: {confidence}%)")
            
            if functionality == "authentication":
                specific_questions.extend([
                    "1. ¿Qué tipo de autenticación se implementa?",
                    "2. ¿Cómo se gestionan los tokens o sesiones?",
                    "3. ¿Existe un sistema de roles y permisos?"
                ])
            elif functionality == "database":
                specific_questions.extend([
                    "1. ¿Qué sistema de base de datos se utiliza?",
                    "2. ¿Existe un ORM o se usa SQL directo?",
                    "3. ¿Cómo se gestionan las transacciones?"
                ])
            elif functionality == "api":
                specific_questions.extend([
                    "1. ¿Es una API REST, GraphQL u otro tipo?",
                    "2. ¿Cuáles son los principales endpoints?",
                    "3. ¿Cómo se gestiona la validación y los errores?"
                ])
            else:
                specific_questions.extend([
                    f"1. ¿En qué consiste la funcionalidad de {functionality}?",
                    f"2. ¿Qué archivos son clave para {functionality}?",
                    f"3. ¿Cómo se integra {functionality} con el resto del sistema?"
                ])
                
            specific_questions.append("")
            
        # Preguntas sobre archivos sin conexiones claras
        disconnected_files = connections_data.get('disconnected_files', [])
        disconnected_questions = []
        
        if disconnected_files:
            disconnected_questions.append("### Preguntas sobre archivos sin conexiones claras")
            
            for i, file in enumerate(disconnected_files[:5]):  # Limitar a 5
                disconnected_questions.append(f"{i+1}. ¿Cuál es el propósito del archivo `{file}`?")
                
        # Unir todas las secciones
        sections = [
            f"# Preguntas Guiadas para Clarificación: {project_name}",
            "",
            "## Preguntas Generales",
            "\n".join(general_questions),
            ""
        ]
        
        if specific_questions:
            sections.extend([
                "## Preguntas sobre Funcionalidades Poco Claras",
                "\n".join(specific_questions)
            ])
            
        if disconnected_questions:
            sections.extend([
                "## Preguntas sobre Componentes Desconectados",
                "\n".join(disconnected_questions)
            ])
            
        sections.extend([
            "",
            "Por favor, responde a estas preguntas para generar un prompt más preciso y contextual para tu proyecto."
        ])
        
        return "\n".join(sections)


def get_contextual_prompt_generator(is_premium: bool = False) -> ContextualPromptGenerator:
    """
    Obtener una instancia del generador de prompts contextuales mejorados.
    
    Args:
        is_premium: Si el usuario tiene acceso premium
        
    Returns:
        Instancia del generador
    """
    return ContextualPromptGenerator(is_premium)
