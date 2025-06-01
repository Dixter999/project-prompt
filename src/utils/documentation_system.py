#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de documentación para ProjectPrompt.

Este módulo proporciona funcionalidades para generar y mantener
documentación estructurada basada en el análisis de proyectos.
"""

import os
import json
import datetime
import shutil
from typing import Dict, List, Optional, Union, Any, Tuple

from src.utils.logger import get_logger
from src.utils.markdown_manager import get_markdown_manager
# Evitamos importación circular
# from src.analyzers.project_scanner import get_project_scanner
# from src.analyzers.functionality_detector import get_functionality_detector
# Delayed import to avoid circular dependency
# from src.generators.markdown_generator import get_markdown_generator

logger = get_logger()


class DocumentationSystem:
    """
    Sistema de documentación para ProjectPrompt.
    
    Esta clase coordina la generación y gestión de documentación
    basada en el análisis de proyectos, creando una estructura
    de archivos markdown organizados por funcionalidad.
    """
    
    def __init__(self):
        """Inicializar el sistema de documentación."""
        self.markdown_manager = get_markdown_manager()
        self._project_scanner = None
        self._functionality_detector = None
        self._markdown_generator = None
        
    @property
    def project_scanner(self):
        """Lazy loading of project scanner to avoid circular imports."""
        if self._project_scanner is None:
            from src.analyzers.project_scanner import get_project_scanner
            self._project_scanner = get_project_scanner()
        return self._project_scanner
        
    @property
    def functionality_detector(self):
        """Lazy loading of functionality detector to avoid circular imports."""
        if self._functionality_detector is None:
            from src.analyzers.functionality_detector import get_functionality_detector
            self._functionality_detector = get_functionality_detector()
        return self._functionality_detector
        
    @property
    def markdown_generator(self):
        """Lazy loading of markdown generator to avoid circular imports."""
        if self._markdown_generator is None:
            from src.generators.markdown_generator import get_markdown_generator
            self._markdown_generator = get_markdown_generator()
        return self._markdown_generator
        
    def setup_documentation_structure(self, 
                                     project_path: str, 
                                     output_dir: Optional[str] = None,
                                     overwrite: bool = False) -> str:
        """
        Configurar la estructura de documentación para un proyecto.
        
        Args:
            project_path: Ruta al proyecto
            output_dir: Directorio de salida (opcional)
            overwrite: Si se debe sobrescribir la estructura existente
            
        Returns:
            Ruta al directorio de documentación
        """
        # Determinar directorio de salida
        if not output_dir:
            output_dir = os.path.join(project_path, '.project-prompt')
            
        # Verificar si ya existe la estructura
        if os.path.exists(output_dir) and not overwrite:
            logger.info(f"La estructura de documentación ya existe en: {output_dir}")
            return output_dir
        
        # Crear o limpiar directorio
        if overwrite and os.path.exists(output_dir):
            shutil.rmtree(output_dir)
            
        os.makedirs(output_dir, exist_ok=True)
        
        # Crear subdirectorios
        os.makedirs(os.path.join(output_dir, 'functionalities'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'prompts'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'prompts', 'functionality'), exist_ok=True)
        
        logger.info(f"Estructura de documentación creada en: {output_dir}")
        return output_dir
        
    def generate_project_documentation(self, 
                                      project_path: str,
                                      output_dir: Optional[str] = None,
                                      update: bool = True) -> Dict[str, str]:
        """
        Generar documentación completa para un proyecto.
        
        Args:
            project_path: Ruta al proyecto
            output_dir: Directorio de salida (opcional)
            update: Si se debe actualizar documentación existente
            
        Returns:
            Diccionario con rutas a los archivos generados
        """
        try:
            # Configurar estructura
            docs_dir = self.setup_documentation_structure(project_path, output_dir)
            
            # Analizar proyecto
            logger.info(f"Analizando proyecto: {project_path}")
            project_data = self.project_scanner.scan_project(project_path)
            
            # Detectar funcionalidades
            logger.info("Detectando funcionalidades...")
            functionality_data = self.functionality_detector.detect_functionalities(
                project_path, project_data=project_data
            )
            
            # Generar documentación general del proyecto
            logger.info("Generando documentación general...")
            general_doc = self._generate_project_analysis(
                project_data, 
                functionality_data,
                os.path.join(docs_dir, 'project-analysis.md'),
                update
            )
            
            # Generar documentación para cada funcionalidad
            logger.info("Generando documentación por funcionalidad...")
            functionality_docs = self._generate_functionality_docs(
                project_data,
                functionality_data,
                os.path.join(docs_dir, 'functionalities'),
                update
            )
            
            # Generar archivo de configuración
            config_path = os.path.join(docs_dir, 'config.yaml')
            if not os.path.exists(config_path) or update:
                self._generate_config_file(config_path, project_path)
            
            # Recopilar rutas generadas
            generated_files = {
                'project_analysis': general_doc,
                'functionalities': functionality_docs,
                'config': config_path,
                'docs_dir': docs_dir
            }
            
            logger.info(f"Documentación generada exitosamente en: {docs_dir}")
            return generated_files
            
        except Exception as e:
            logger.error(f"Error al generar documentación: {e}", exc_info=True)
            raise
    
    def update_documentation(self, 
                            project_path: str,
                            docs_dir: Optional[str] = None) -> Dict[str, str]:
        """
        Actualizar documentación existente.
        
        Args:
            project_path: Ruta al proyecto
            docs_dir: Directorio de documentación (opcional)
            
        Returns:
            Diccionario con rutas a los archivos actualizados
        """
        # Determinar directorio de documentación
        if not docs_dir:
            docs_dir = os.path.join(project_path, '.project-prompt')
            
        if not os.path.exists(docs_dir):
            logger.warning(f"No existe documentación en: {docs_dir}")
            return self.generate_project_documentation(project_path, docs_dir)
            
        # Regenerar con actualización
        return self.generate_project_documentation(
            project_path, docs_dir, update=True
        )
    
    def get_documentation_info(self, docs_dir: str) -> Dict[str, Any]:
        """
        Obtener información sobre la documentación generada.
        
        Args:
            docs_dir: Directorio de documentación
            
        Returns:
            Información sobre la documentación
        """
        if not os.path.exists(docs_dir):
            raise FileNotFoundError(f"No existe documentación en: {docs_dir}")
            
        try:
            # Listar documentos existentes
            documents = self.markdown_manager.list_documents(docs_dir)
            
            # Obtener información de funcionalidades
            functionalities = []
            func_dir = os.path.join(docs_dir, 'functionalities')
            if os.path.exists(func_dir):
                for doc in self.markdown_manager.list_documents(func_dir):
                    functionalities.append(doc)
            
            # Obtener información básica del proyecto
            project_analysis_path = os.path.join(docs_dir, 'project-analysis.md')
            project_info = {}
            if os.path.exists(project_analysis_path):
                project_info = self.markdown_manager.get_document_info(project_analysis_path)
                
            # Obtener información de configuración
            config_path = os.path.join(docs_dir, 'config.yaml')
            config = {}
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    import yaml
                    config = yaml.safe_load(f)
            
            # Recopilar información
            info = {
                'docs_dir': docs_dir,
                'document_count': len(documents),
                'functionalities': functionalities,
                'project_info': project_info,
                'config': config,
                'last_updated': project_info.get('updated', 'Desconocido')
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error al obtener información de documentación: {e}", exc_info=True)
            raise
    
    def _generate_project_analysis(self, 
                                  project_data: Dict[str, Any],
                                  functionality_data: Dict[str, Any],
                                  output_path: str,
                                  update: bool = True) -> str:
        """
        Generar documento de análisis general del proyecto.
        
        Args:
            project_data: Datos del proyecto
            functionality_data: Datos de funcionalidades
            output_path: Ruta de salida
            update: Si se debe actualizar documento existente
            
        Returns:
            Ruta al documento generado
        """
        # Preparar contexto para la plantilla
        context = {
            'project_name': os.path.basename(project_data.get('project_path', '')),
            'project_path': project_data.get('project_path', ''),
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '0.1.0',  # TODO: Obtener versión real
            'stats': project_data.get('stats', {}),
            'languages': project_data.get('languages', {}),
            'important_files': project_data.get('important_files', {}),
            'dependencies': project_data.get('dependencies', {})
        }
        
        # Añadir datos de funcionalidades
        functionalities = {}
        for func_name, func_data in functionality_data.get('detected', {}).items():
            if func_data.get('confidence', 0) >= functionality_data.get('threshold', 0):
                functionalities[func_name] = func_data
                
        context['functionalities'] = functionalities
        
        # Frontmatter para el documento
        frontmatter_data = {
            'title': f"Análisis del Proyecto: {context['project_name']}",
            'generated_by': 'ProjectPrompt',
            'project_path': context['project_path'],
            'timestamp': context['timestamp']
        }
        
        # Generar documento
        if os.path.exists(output_path) and update:
            return self.markdown_manager.update_document(
                output_path, 
                context, 
                frontmatter_data,
                'project_analysis'
            )
        else:
            return self.markdown_manager.create_document(
                'project_analysis', 
                output_path, 
                context, 
                frontmatter_data
            )
    
    def _generate_functionality_docs(self,
                                   project_data: Dict[str, Any],
                                   functionality_data: Dict[str, Any],
                                   output_dir: str,
                                   update: bool = True) -> Dict[str, str]:
        """
        Generar documentación para cada funcionalidad.
        
        Args:
            project_data: Datos del proyecto
            functionality_data: Datos de funcionalidades
            output_dir: Directorio de salida
            update: Si se debe actualizar documentos existentes
            
        Returns:
            Diccionario con rutas a documentos generados
        """
        generated_docs = {}
        
        # Crear directorio si no existe
        os.makedirs(output_dir, exist_ok=True)
        
        # Obtener datos básicos del proyecto
        project_name = os.path.basename(project_data.get('project_path', ''))
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Procesar cada funcionalidad detectada
        for func_name, func_data in functionality_data.get('detected', {}).items():
            confidence = func_data.get('confidence', 0)
            threshold = functionality_data.get('threshold', 0)
            
            # Solo documentar funcionalidades con confianza suficiente
            if confidence >= threshold:
                # Preparar contexto
                context = {
                    'functionality_name': func_name,
                    'project_name': project_name,
                    'confidence': confidence,
                    'timestamp': timestamp,
                    'main_files': func_data.get('files', []),
                    'patterns': func_data.get('patterns', {})
                }
                
                # Preparar frontmatter
                frontmatter_data = {
                    'title': f"Funcionalidad: {func_name.title()}",
                    'functionality': func_name,
                    'confidence': confidence,
                    'generated_by': 'ProjectPrompt',
                    'timestamp': timestamp
                }
                
                # Ruta de salida
                output_path = os.path.join(output_dir, f"{func_name}.md")
                
                # Generar documento
                try:
                    if os.path.exists(output_path) and update:
                        doc_path = self.markdown_manager.update_document(
                            output_path, 
                            context, 
                            frontmatter_data,
                            'functionality'
                        )
                    else:
                        doc_path = self.markdown_manager.create_document(
                            'functionality', 
                            output_path, 
                            context, 
                            frontmatter_data
                        )
                    
                    generated_docs[func_name] = doc_path
                    
                except Exception as e:
                    logger.error(f"Error al generar documento para {func_name}: {e}")
        
        return generated_docs
    
    def _generate_config_file(self, config_path: str, project_path: str) -> str:
        """
        Generar archivo de configuración para la documentación.
        
        Args:
            config_path: Ruta de salida para el archivo
            project_path: Ruta al proyecto
            
        Returns:
            Ruta al archivo generado
        """
        try:
            import yaml
            
            # Configuración básica
            config = {
                'project': {
                    'path': project_path,
                    'name': os.path.basename(project_path)
                },
                'documentation': {
                    'created': datetime.datetime.now().isoformat(),
                    'updated': datetime.datetime.now().isoformat(),
                    'version': '0.1.0',
                    'tool': 'ProjectPrompt'
                },
                'settings': {
                    'auto_update': True,
                    'include_code_samples': True,
                    'max_sample_lines': 15
                }
            }
            
            # Guardar archivo
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
                
            return config_path
            
        except Exception as e:
            logger.error(f"Error al generar archivo de configuración: {e}", exc_info=True)
            raise

    def _analyze_project(self, project_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza un proyecto para generar documentación.
        
        Args:
            project_path: Ruta al proyecto
            options: Opciones de análisis
            
        Returns:
            Datos del análisis
        """
        try:
            # Importamos aquí para evitar importación circular
            from src.analyzers.project_scanner import get_project_scanner
            from src.analyzers.functionality_detector import get_functionality_detector
            
            logger.info(f"Analizando proyecto en: {project_path}")
            
            # Escanear estructura del proyecto
            scanner = get_project_scanner()
            project_data = scanner.scan_project(project_path)
            
            # Detectar funcionalidades
            if options.get('detect_functionalities', True):
                detector = get_functionality_detector()
                functionalities = detector.detect_functionalities(project_path, project_data)
                project_data['functionalities'] = functionalities
            
            return project_data
            
        except Exception as e:
            logger.error(f"Error al analizar proyecto: {e}", exc_info=True)
            raise


def get_documentation_system() -> DocumentationSystem:
    """
    Obtener una instancia del sistema de documentación.
    
    Returns:
        Instancia de DocumentationSystem
    """
    return DocumentationSystem()
