#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de entrevistas guiadas para obtener información detallada sobre funcionalidades.

Este módulo proporciona un sistema interactivo para realizar preguntas contextuales
sobre funcionalidades poco claras o incompletas en un proyecto.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from src.utils.logger import get_logger
from src.utils.documentation_system import get_documentation_system
from src.templates.interviews import generic
from src.analyzers.project_scanner import get_project_scanner
from src.analyzers.functionality_detector import get_functionality_detector

# Importar plantillas específicas de entrevista
try:
    from src.templates.interviews import api_integration
except ImportError:
    api_integration = None

# Configurar logger
logger = get_logger()
console = Console()


class InterviewSystem:
    """
    Sistema de entrevistas guiadas para clarificar aspectos de funcionalidades.
    
    Este sistema permite realizar preguntas contextuales adaptativas basadas
    en la funcionalidad específica y en las respuestas previas del usuario.
    """
    
    def __init__(self):
        """Inicializar el sistema de entrevistas."""
        self.doc_system = get_documentation_system()
        self.scanner = get_project_scanner()
        self.functionality_detector = get_functionality_detector(scanner=self.scanner)
        
        # Cargar plantillas de preguntas
        self.templates = {
            'generic': generic.INTERVIEW_TEMPLATES,
        }
        
        # Cargar plantillas específicas si existen
        if api_integration:
            self.templates['api'] = api_integration.INTERVIEW_TEMPLATES
            
        # Inicializar datos de entrevista
        self.reset_interview()
        
    def reset_interview(self):
        """Reiniciar los datos de la entrevista actual."""
        self.current_interview = {
            'functionality': '',
            'questions': [],
            'answers': {},
            'context': {},
            'started_at': None,
            'completed_at': None,
            'summary': '',
            'recommendations': []
        }
        
    def start_interview(self, project_path: str, functionality_name: str) -> Dict[str, Any]:
        """
        Iniciar una entrevista guiada sobre una funcionalidad específica.
        
        Args:
            project_path: Ruta al proyecto
            functionality_name: Nombre de la funcionalidad a entrevistar
            
        Returns:
            Diccionario con resultados de la entrevista
        """
        self.reset_interview()
        
        # Registrar inicio de la entrevista
        self.current_interview['functionality'] = functionality_name
        self.current_interview['started_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Obtener contexto del proyecto y la funcionalidad
        project_context = self._gather_project_context(project_path, functionality_name)
        self.current_interview['context'] = project_context
        
        console.print(Panel(
            f"[bold blue]Entrevista sobre la funcionalidad: {functionality_name.capitalize()}[/bold blue]\n\n"
            "[yellow]Esta entrevista ayudará a comprender mejor la funcionalidad y generar "
            "documentación más precisa. Por favor responda las preguntas con el máximo detalle posible.[/yellow]",
            border_style="blue"
        ))
        
        # Seleccionar la plantilla adecuada para la funcionalidad
        template_name = self._select_template_for_functionality(functionality_name)
        
        # Realizar preguntas iniciales
        initial_questions = self._get_initial_questions(template_name, functionality_name)
        
        for q in initial_questions:
            self._ask_question(q)
            
        # Análisis adaptativo (preguntas de seguimiento basadas en respuestas anteriores)
        self._ask_adaptive_questions(template_name, functionality_name)
        
        # Finalizar entrevista
        self._complete_interview(project_path)
        
        return self.current_interview
        
    def _gather_project_context(self, project_path: str, functionality_name: str) -> Dict[str, Any]:
        """
        Recopilar contexto del proyecto y la funcionalidad específica.
        
        Args:
            project_path: Ruta al proyecto
            functionality_name: Nombre de la funcionalidad
            
        Returns:
            Diccionario con contexto relevante
        """
        context = {
            'project_path': project_path,
            'project_name': os.path.basename(project_path),
            'functionality': functionality_name,
            'detected_evidence': {},
            'files': []
        }
        
        try:
            # Escanear el proyecto para obtener información
            project_data = self.scanner.scan_project(project_path)
            context['languages'] = project_data.get('languages', {})
            
            # Detectar funcionalidades para obtener evidencia
            functionality_data = self.functionality_detector.detect_functionalities(project_path)
            func_info = functionality_data.get('detected', {}).get(functionality_name, {})
            
            if func_info:
                context['detected_evidence'] = func_info.get('evidence', {})
                context['confidence'] = func_info.get('confidence', 0)
                context['present'] = func_info.get('present', False)
                
                # Guardar rutas de archivos relevantes
                files = func_info.get('evidence', {}).get('files', [])
                context['files'] = files
        except Exception as e:
            logger.error(f"Error al recopilar contexto del proyecto: {e}", exc_info=True)
            
        return context
    
    def _select_template_for_functionality(self, functionality_name: str) -> str:
        """
        Seleccionar la plantilla más adecuada para la funcionalidad.
        
        Args:
            functionality_name: Nombre de la funcionalidad
            
        Returns:
            Nombre de la plantilla a utilizar
        """
        # Mapeo de funcionalidades a plantillas especializadas
        functionality_templates = {
            'api': 'api',
            'api_integration': 'api',
            'rest_api': 'api',
            'graphql_api': 'api',
            'external_api': 'api',
        }
        
        # Buscar si hay una plantilla específica para esta funcionalidad
        for key, template in functionality_templates.items():
            if key in functionality_name.lower() and template in self.templates:
                return template
                
        # Por defecto usar la plantilla genérica
        return 'generic'
    
    def _get_initial_questions(self, template_name: str, functionality_name: str) -> List[Dict[str, Any]]:
        """
        Obtener las preguntas iniciales para la funcionalidad.
        
        Args:
            template_name: Nombre de la plantilla a utilizar
            functionality_name: Nombre de la funcionalidad
            
        Returns:
            Lista de preguntas iniciales
        """
        # Obtener plantilla
        template = self.templates.get(template_name, self.templates['generic'])
        
        # Obtener categoría de preguntas según la funcionalidad
        if functionality_name in template:
            category = functionality_name
        else:
            category = 'general'
            
        # Obtener preguntas iniciales
        questions = template.get(category, {}).get('initial_questions', [])
        if not questions:
            questions = template.get('general', {}).get('initial_questions', [])
            
        # Si aún no hay preguntas, usar preguntas genéricas
        if not questions:
            questions = self.templates['generic']['general']['initial_questions']
            
        # Personalizar preguntas con el nombre de la funcionalidad
        for q in questions:
            if 'question' in q:
                q['question'] = q['question'].replace('{functionality}', functionality_name.capitalize())
                
        return questions
    
    def _ask_question(self, question: Dict[str, Any]) -> str:
        """
        Realizar una pregunta al usuario y almacenar la respuesta.
        
        Args:
            question: Diccionario con la información de la pregunta
            
        Returns:
            Respuesta del usuario
        """
        question_text = question.get('question', '')
        question_id = question.get('id', f"q{len(self.current_interview['questions']) + 1}")
        question_type = question.get('type', 'text')
        options = question.get('options', [])
        
        # Guardar la pregunta en el historial
        question_data = {
            'id': question_id,
            'text': question_text,
            'type': question_type
        }
        
        if options:
            question_data['options'] = options
            
        self.current_interview['questions'].append(question_data)
        
        # Realizar la pregunta según su tipo
        if question_type == 'boolean':
            console.print(f"\n[bold cyan]{question_text}[/bold cyan]")
            answer = Confirm.ask("", default=False)
        elif question_type == 'choice' and options:
            console.print(f"\n[bold cyan]{question_text}[/bold cyan]")
            
            # Mostrar opciones
            for i, option in enumerate(options, 1):
                console.print(f"{i}. {option}")
                
            # Solicitar selección
            selection = Prompt.ask(
                "\nSeleccione una opción (número)", 
                choices=[str(i) for i in range(1, len(options) + 1)]
            )
            answer = options[int(selection) - 1]
        else:
            # Pregunta de texto libre
            console.print(f"\n[bold cyan]{question_text}[/bold cyan]")
            answer = Prompt.ask("", default="")
            
        # Almacenar la respuesta
        self.current_interview['answers'][question_id] = answer
        
        return answer
    
    def _ask_adaptive_questions(self, template_name: str, functionality_name: str):
        """
        Realizar preguntas de seguimiento basadas en respuestas anteriores.
        
        Args:
            template_name: Nombre de la plantilla a utilizar
            functionality_name: Nombre de la funcionalidad
        """
        # Obtener plantilla
        template = self.templates.get(template_name, self.templates['generic'])
        
        # Obtener categoría de preguntas de seguimiento
        follow_up_questions = template.get(functionality_name, {}).get('follow_up_questions', [])
        if not follow_up_questions:
            follow_up_questions = template.get('general', {}).get('follow_up_questions', [])
            
        # Si no hay preguntas de seguimiento, usar las genéricas
        if not follow_up_questions:
            follow_up_questions = self.templates['generic']['general'].get('follow_up_questions', [])
            
        # Evaluar cada pregunta de seguimiento para ver si aplica
        for q in follow_up_questions:
            condition = q.get('condition', None)
            
            # Si no hay condición o la condición se cumple, hacer la pregunta
            if not condition or self._evaluate_condition(condition):
                self._ask_question(q)
                
        # Preguntas finales
        final_questions = template.get(functionality_name, {}).get('final_questions', [])
        if not final_questions:
            final_questions = template.get('general', {}).get('final_questions', [])
            
        # Si no hay preguntas finales, usar las genéricas
        if not final_questions:
            final_questions = self.templates['generic']['general'].get('final_questions', [])
            
        # Realizar preguntas finales
        for q in final_questions:
            self._ask_question(q)
    
    def _evaluate_condition(self, condition: Dict[str, Any]) -> bool:
        """
        Evaluar una condición para preguntas adaptativas.
        
        Args:
            condition: Diccionario con la condición a evaluar
            
        Returns:
            True si la condición se cumple, False en caso contrario
        """
        condition_type = condition.get('type', '')
        
        if condition_type == 'answer_equals':
            question_id = condition.get('question_id', '')
            expected_value = condition.get('value', '')
            answer = self.current_interview['answers'].get(question_id, '')
            return answer == expected_value
            
        elif condition_type == 'answer_contains':
            question_id = condition.get('question_id', '')
            substring = condition.get('substring', '').lower()
            answer = str(self.current_interview['answers'].get(question_id, '')).lower()
            return substring in answer
            
        elif condition_type == 'answer_boolean':
            question_id = condition.get('question_id', '')
            expected = condition.get('is_true', True)
            answer = self.current_interview['answers'].get(question_id, False)
            return answer == expected
            
        elif condition_type == 'context_has':
            key = condition.get('key', '')
            value = condition.get('value', '')
            
            if key.startswith('context.'):
                path = key.split('.')
                current = self.current_interview['context']
                
                for p in path[1:]:
                    if p in current:
                        current = current[p]
                    else:
                        return False
                        
                return current == value
                
        # Por defecto, si la condición no se reconoce, no se cumple
        return False
    
    def _complete_interview(self, project_path: str):
        """
        Finalizar la entrevista y generar documentación.
        
        Args:
            project_path: Ruta al proyecto
        """
        # Registrar finalización de la entrevista
        self.current_interview['completed_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Generar resumen de la entrevista
        self._generate_summary()
        
        # Generar recomendaciones
        self._generate_recommendations()
        
        # Guardar resultados en la documentación del proyecto
        self._save_to_documentation(project_path)
        
        # Mostrar mensaje de finalización
        console.print(Panel(
            "[bold green]¡Entrevista completada![/bold green]\n\n"
            f"[yellow]{self.current_interview['summary']}[/yellow]",
            title="Resumen",
            border_style="green"
        ))
        
        if self.current_interview['recommendations']:
            console.print("\n[bold cyan]Recomendaciones:[/bold cyan]")
            for i, rec in enumerate(self.current_interview['recommendations'], 1):
                console.print(f"  {i}. {rec}")
    
    def _generate_summary(self):
        """Generar un resumen de la entrevista basado en las respuestas."""
        functionality = self.current_interview['functionality']
        answers = self.current_interview['answers']
        
        # Construir un resumen básico
        summary = f"Entrevista sobre la funcionalidad '{functionality}'. "
        
        # Añadir información sobre el propósito
        purpose_qids = [q['id'] for q in self.current_interview['questions'] 
                       if 'propósito' in q['text'].lower() or 'objetivo' in q['text'].lower()]
        
        if purpose_qids and purpose_qids[0] in answers:
            summary += f"Propósito: {answers[purpose_qids[0]]}. "
            
        # Añadir información sobre el estado actual
        status_qids = [q['id'] for q in self.current_interview['questions'] 
                      if 'estado' in q['text'].lower() or 'implementado' in q['text'].lower()]
        
        if status_qids and status_qids[0] in answers:
            summary += f"Estado actual: {answers[status_qids[0]]}. "
            
        # Contar preguntas y respuestas
        total_questions = len(self.current_interview['questions'])
        answered_questions = sum(1 for q in self.current_interview['questions'] 
                               if q['id'] in answers and answers[q['id']])
                               
        summary += f"Se respondieron {answered_questions} de {total_questions} preguntas."
        
        self.current_interview['summary'] = summary
    
    def _generate_recommendations(self):
        """Generar recomendaciones basadas en las respuestas de la entrevista."""
        recommendations = []
        functionality = self.current_interview['functionality']
        answers = self.current_interview['answers']
        
        # Verificar si la funcionalidad está implementada
        implemented_qids = [q['id'] for q in self.current_interview['questions'] 
                          if 'implementado' in q['text'].lower()]
                          
        if implemented_qids and implemented_qids[0] in answers:
            if not answers[implemented_qids[0]] or 'no' in str(answers[implemented_qids[0]]).lower():
                recommendations.append(f"Implementar la funcionalidad '{functionality}' según los requisitos recopilados")
                
        # Verificar si hay problemas identificados
        problem_qids = [q['id'] for q in self.current_interview['questions'] 
                       if 'problema' in q['text'].lower() or 'desafío' in q['text'].lower()]
                       
        if problem_qids and problem_qids[0] in answers and answers[problem_qids[0]]:
            recommendations.append(f"Resolver los problemas identificados en '{functionality}': {answers[problem_qids[0]]}")
            
        # Verificar si hay mejoras sugeridas
        improvement_qids = [q['id'] for q in self.current_interview['questions'] 
                          if 'mejora' in q['text'].lower() or 'optimizar' in q['text'].lower()]
                          
        if improvement_qids and improvement_qids[0] in answers and answers[improvement_qids[0]]:
            recommendations.append(f"Implementar mejoras sugeridas para '{functionality}': {answers[improvement_qids[0]]}")
            
        # Guardar recomendaciones
        self.current_interview['recommendations'] = recommendations
    
    def _save_to_documentation(self, project_path: str):
        """
        Guardar los resultados de la entrevista en la documentación del proyecto.
        
        Args:
            project_path: Ruta al proyecto
        """
        try:
            # Crear estructura de documentación si no existe
            docs_dir = self.doc_system.ensure_documentation_dir(project_path)
            
            # Crear directorio de entrevistas si no existe
            interviews_dir = os.path.join(docs_dir, 'interviews')
            os.makedirs(interviews_dir, exist_ok=True)
            
            # Nombre del archivo de la entrevista
            functionality = self.current_interview['functionality']
            timestamp = self.current_interview['started_at'].replace(' ', '_').replace(':', '-')
            filename = f"{functionality}_interview_{timestamp}.json"
            file_path = os.path.join(interviews_dir, filename)
            
            # Guardar entrevista en formato JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_interview, f, indent=2)
                
            # Crear archivo markdown con la entrevista
            self._create_markdown_summary(interviews_dir, functionality, timestamp)
                
            logger.info(f"Entrevista guardada en: {file_path}")
            
        except Exception as e:
            logger.error(f"Error al guardar la entrevista en documentación: {e}", exc_info=True)
    
    def _create_markdown_summary(self, interviews_dir: str, functionality: str, timestamp: str):
        """
        Crear un resumen de la entrevista en formato markdown.
        
        Args:
            interviews_dir: Directorio de entrevistas
            functionality: Nombre de la funcionalidad
            timestamp: Marca de tiempo de la entrevista
        """
        try:
            markdown_filename = f"{functionality}_interview_{timestamp}.md"
            md_path = os.path.join(interviews_dir, markdown_filename)
            
            with open(md_path, 'w', encoding='utf-8') as f:
                # Cabecera y metadatos
                f.write(f"# Entrevista: {functionality.capitalize()}\n\n")
                f.write(f"**Fecha**: {self.current_interview['started_at']}\n\n")
                
                # Resumen
                f.write("## Resumen\n\n")
                f.write(f"{self.current_interview['summary']}\n\n")
                
                # Preguntas y respuestas
                f.write("## Preguntas y Respuestas\n\n")
                
                for i, question in enumerate(self.current_interview['questions'], 1):
                    qid = question['id']
                    q_text = question['text']
                    
                    answer = self.current_interview['answers'].get(qid, "Sin respuesta")
                    
                    f.write(f"### {i}. {q_text}\n\n")
                    f.write(f"{answer}\n\n")
                
                # Recomendaciones
                if self.current_interview['recommendations']:
                    f.write("## Recomendaciones\n\n")
                    
                    for rec in self.current_interview['recommendations']:
                        f.write(f"- {rec}\n")
                    
                    f.write("\n")
                    
        except Exception as e:
            logger.error(f"Error al crear resumen markdown de la entrevista: {e}", exc_info=True)

    def load_interview(self, file_path: str) -> Dict[str, Any]:
        """
        Cargar una entrevista guardada desde un archivo JSON.
        
        Args:
            file_path: Ruta al archivo de la entrevista
            
        Returns:
            Diccionario con los datos de la entrevista
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                interview_data = json.load(f)
                
            return interview_data
        except Exception as e:
            logger.error(f"Error al cargar entrevista desde {file_path}: {e}", exc_info=True)
            return {}
            
    def list_interviews(self, project_path: str) -> List[Dict[str, Any]]:
        """
        Listar todas las entrevistas guardadas para un proyecto.
        
        Args:
            project_path: Ruta al proyecto
            
        Returns:
            Lista de metadatos de entrevistas
        """
        interviews = []
        
        try:
            # Obtener directorio de documentación
            docs_dir = self.doc_system.get_documentation_dir(project_path)
            if not docs_dir:
                return []
                
            # Verificar directorio de entrevistas
            interviews_dir = os.path.join(docs_dir, 'interviews')
            if not os.path.exists(interviews_dir):
                return []
                
            # Buscar archivos JSON de entrevistas
            for file_name in os.listdir(interviews_dir):
                if file_name.endswith('.json') and 'interview' in file_name:
                    file_path = os.path.join(interviews_dir, file_name)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                        # Extraer metadatos básicos
                        interviews.append({
                            'functionality': data.get('functionality', 'desconocida'),
                            'started_at': data.get('started_at', ''),
                            'completed_at': data.get('completed_at', ''),
                            'questions_count': len(data.get('questions', [])),
                            'answers_count': len(data.get('answers', {})),
                            'file_path': file_path,
                            'file_name': file_name
                        })
                    except Exception as e:
                        logger.error(f"Error al procesar entrevista {file_name}: {e}")
                        
            # Ordenar por fecha de inicio (más reciente primero)
            interviews.sort(key=lambda x: x.get('started_at', ''), reverse=True)
                
        except Exception as e:
            logger.error(f"Error al listar entrevistas: {e}", exc_info=True)
            
        return interviews


def get_interview_system() -> InterviewSystem:
    """
    Obtener una instancia del sistema de entrevistas.
    
    Returns:
        Instancia de InterviewSystem
    """
    return InterviewSystem()
