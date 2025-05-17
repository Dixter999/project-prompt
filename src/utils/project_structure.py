#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gestor de estructura de archivos del proyecto.

Este módulo se encarga de crear y mantener la estructura
de archivos para almacenar análisis y prompts contextuales.
"""

import os
import yaml
import datetime
from typing import Dict, List, Optional, Any, Union
import shutil

from src.utils.logger import get_logger
from src.utils.markdown_manager import get_markdown_manager

logger = get_logger()

class ProjectStructure:
    """
    Gestor de estructura de archivos del proyecto ProjectPrompt.
    
    Esta clase se encarga de crear y mantener la estructura de directorios
    y archivos necesarios para almacenar los análisis y prompts generados.
    """
    
    DEFAULT_CONFIG = {
        'project_name': 'Unknown Project',
        'version': '0.1.0',
        'language': 'en',
        'structure': {
            'root': '.project-prompt',
            'analysis': 'project-analysis.md',
            'functionalities_dir': 'functionalities',
            'prompts_dir': 'prompts',
            'prompts_functionality_dir': 'prompts/functionality',
            'config': 'config.yaml'
        }
    }
    
    def __init__(self, project_path: str, config: Optional[Dict[str, Any]] = None):
        """
        Inicializar el gestor de estructura de archivos.
        
        Args:
            project_path: Ruta base del proyecto a analizar
            config: Configuración opcional
        """
        self.project_path = os.path.abspath(project_path)
        self.config = config or {}
        self.config = {**self.DEFAULT_CONFIG, **self.config}
        
        # Ruta de la estructura de ProjectPrompt dentro del proyecto
        self.structure_root = os.path.join(
            self.project_path, 
            self.config['structure']['root']
        )
        
        self.markdown_manager = get_markdown_manager(self.config)
        
    def get_current_date(self) -> str:
        """
        Obtener la fecha actual en formato ISO.
        
        Returns:
            Fecha actual en formato ISO
        """
        return datetime.datetime.now().isoformat()
    
    def create_structure(self, overwrite: bool = False) -> Dict[str, Any]:
        """
        Crear la estructura de archivos para ProjectPrompt.
        
        Args:
            overwrite: Si es True, sobrescribe archivos existentes
        
        Returns:
            Diccionario con información de la estructura creada
        """
        logger.info(f"Creando estructura de archivos en: {self.structure_root}")
        
        # Verificar si la estructura ya existe
        structure_exists = os.path.exists(self.structure_root)
        
        if structure_exists and not overwrite:
            logger.info("La estructura ya existe. Se actualizará de forma incremental.")
            return self._update_existing_structure()
        
        # Crear directorios
        created_dirs = self._create_directories()
        
        # Crear archivos base
        created_files = self._create_base_files()
        
        # Guardar configuración
        config_path = self._save_config()
        
        result = {
            'structure_root': self.structure_root,
            'directories_created': created_dirs,
            'files_created': created_files,
            'config_path': config_path,
            'status': 'created' if not structure_exists else 'overwritten'
        }
        
        logger.info(f"Estructura de archivos creada: {len(created_dirs)} directorios, {len(created_files)} archivos")
        return result
    
    def get_structure_info(self) -> Dict[str, Any]:
        """
        Obtener información de la estructura existente.
        
        Returns:
            Diccionario con información de la estructura
        """
        if not os.path.exists(self.structure_root):
            return {'exists': False, 'structure_root': self.structure_root}
        
        # Contar archivos y directorios
        dirs_count = 0
        files_count = 0
        functionalities = []
        prompts = []
        
        for root, dirs, files in os.walk(self.structure_root):
            dirs_count += len(dirs)
            files_count += len(files)
            
            # Detectar funcionalidades
            if os.path.basename(root) == self.config['structure']['functionalities_dir']:
                for file in files:
                    if file.endswith('.md'):
                        functionalities.append(file[:-3])  # Quitar extensión .md
            
            # Detectar prompts por funcionalidad
            if os.path.basename(root) == 'functionality' and os.path.dirname(root).endswith(self.config['structure']['prompts_dir']):
                for file in files:
                    if file.endswith('.md'):
                        prompts.append(file[:-3])  # Quitar extensión .md
        
        # Verificar archivos principales
        analysis_path = os.path.join(self.structure_root, self.config['structure']['analysis'])
        config_path = os.path.join(self.structure_root, self.config['structure']['config'])
        
        result = {
            'exists': True,
            'structure_root': self.structure_root,
            'directories_count': dirs_count,
            'files_count': files_count,
            'functionalities': functionalities,
            'prompts': prompts,
            'has_analysis': os.path.exists(analysis_path),
            'has_config': os.path.exists(config_path)
        }
        
        return result
    
    def get_file_path(self, file_type: str, functionality: Optional[str] = None) -> str:
        """
        Obtener la ruta absoluta a un archivo específico en la estructura.
        
        Args:
            file_type: Tipo de archivo ('analysis', 'functionality', 'prompt', 'prompt_functionality')
            functionality: Nombre de la funcionalidad (para tipos que lo requieran)
        
        Returns:
            Ruta absoluta al archivo solicitado
        """
        if file_type == 'analysis':
            return os.path.join(self.structure_root, self.config['structure']['analysis'])
        
        elif file_type == 'functionality' and functionality:
            return os.path.join(
                self.structure_root, 
                self.config['structure']['functionalities_dir'],
                f"{functionality}.md"
            )
        
        elif file_type == 'prompt':
            return os.path.join(
                self.structure_root, 
                self.config['structure']['prompts_dir'],
                "general.md"
            )
        
        elif file_type == 'prompt_functionality' and functionality:
            return os.path.join(
                self.structure_root, 
                self.config['structure']['prompts_functionality_dir'],
                f"{functionality}.md"
            )
        
        elif file_type == 'config':
            return os.path.join(self.structure_root, self.config['structure']['config'])
        
        else:
            raise ValueError(f"Tipo de archivo no válido o funcionalidad no especificada: {file_type}")
    
    def save_analysis(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Guardar el análisis general del proyecto.
        
        Args:
            content: Contenido del análisis
            metadata: Metadatos opcionales
        
        Returns:
            Ruta al archivo generado
        """
        file_path = self.get_file_path('analysis')
        
        # Metadata por defecto
        default_metadata = {
            'title': f"Análisis del proyecto: {self.config['project_name']}",
            'date': self.get_current_date(),
            'version': self.config.get('version', '0.1.0')
        }
        
        # Combinar con metadata proporcionada
        file_metadata = {**default_metadata, **(metadata or {})}
        
        # Asegurar que el directorio existe
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Guardar archivo
        with open(file_path, 'w', encoding='utf-8') as f:
            # Añadir frontmatter si hay metadata
            if file_metadata:
                f.write('---\n')
                yaml.dump(file_metadata, f, default_flow_style=False)
                f.write('---\n\n')
            
            # Escribir contenido
            f.write(content)
        
        return file_path
    
    def save_functionality_analysis(self, functionality: str, content: str, 
                                  metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Guardar el análisis de una funcionalidad específica.
        
        Args:
            functionality: Nombre de la funcionalidad
            content: Contenido del análisis
            metadata: Metadatos opcionales
        
        Returns:
            Ruta al archivo generado
        """
        file_path = self.get_file_path('functionality', functionality)
        
        # Metadata por defecto
        default_metadata = {
            'title': f"Análisis de funcionalidad: {functionality}",
            'functionality': functionality,
            'date': self.get_current_date(),
            'version': self.config.get('version', '0.1.0')
        }
        
        # Combinar con metadata proporcionada
        file_metadata = {**default_metadata, **(metadata or {})}
        
        # Asegurar que el directorio existe
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Guardar archivo
        with open(file_path, 'w', encoding='utf-8') as f:
            # Añadir frontmatter si hay metadata
            if file_metadata:
                f.write('---\n')
                yaml.dump(file_metadata, f, default_flow_style=False)
                f.write('---\n\n')
            
            # Escribir contenido
            f.write(content)
        
        return file_path
    
    def save_prompt(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Guardar un prompt general.
        
        Args:
            content: Contenido del prompt
            metadata: Metadatos opcionales
        
        Returns:
            Ruta al archivo generado
        """
        file_path = self.get_file_path('prompt')
        
        # Metadata por defecto
        default_metadata = {
            'title': f"Prompt general para {self.config['project_name']}",
            'date': self.get_current_date(),
            'version': self.config.get('version', '0.1.0'),
            'type': 'general'
        }
        
        # Combinar con metadata proporcionada
        file_metadata = {**default_metadata, **(metadata or {})}
        
        # Asegurar que el directorio existe
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Guardar archivo
        with open(file_path, 'w', encoding='utf-8') as f:
            # Añadir frontmatter si hay metadata
            if file_metadata:
                f.write('---\n')
                yaml.dump(file_metadata, f, default_flow_style=False)
                f.write('---\n\n')
            
            # Escribir contenido
            f.write(content)
        
        return file_path
    
    def save_functionality_prompt(self, functionality: str, content: str, 
                                metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Guardar un prompt para una funcionalidad específica.
        
        Args:
            functionality: Nombre de la funcionalidad
            content: Contenido del prompt
            metadata: Metadatos opcionales
        
        Returns:
            Ruta al archivo generado
        """
        file_path = self.get_file_path('prompt_functionality', functionality)
        
        # Metadata por defecto
        default_metadata = {
            'title': f"Prompt para funcionalidad: {functionality}",
            'functionality': functionality,
            'date': self.get_current_date(),
            'version': self.config.get('version', '0.1.0'),
            'type': 'functionality'
        }
        
        # Combinar con metadata proporcionada
        file_metadata = {**default_metadata, **(metadata or {})}
        
        # Asegurar que el directorio existe
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Guardar archivo
        with open(file_path, 'w', encoding='utf-8') as f:
            # Añadir frontmatter si hay metadata
            if file_metadata:
                f.write('---\n')
                yaml.dump(file_metadata, f, default_flow_style=False)
                f.write('---\n\n')
            
            # Escribir contenido
            f.write(content)
        
        return file_path
    
    def save_premium_functionality_prompt(self, functionality: str, prompt_type: str, content: str, 
                                        metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Guardar un prompt premium para una funcionalidad específica.
        
        Args:
            functionality: Nombre de la funcionalidad
            prompt_type: Tipo de prompt premium (implementation, testing, integration)
            content: Contenido del prompt
            metadata: Metadatos opcionales
        
        Returns:
            Ruta al archivo generado
        """
        # Crear el directorio premium si no existe
        premium_dir = os.path.join(self.structure_root, 'prompts', 'premium')
        os.makedirs(premium_dir, exist_ok=True)
        
        # Crear directorio para la funcionalidad dentro de premium
        functionality_dir = os.path.join(premium_dir, functionality.lower())
        os.makedirs(functionality_dir, exist_ok=True)
        
        # Definir el nombre del archivo
        file_name = f"{prompt_type}.md"
        file_path = os.path.join(functionality_dir, file_name)
        
        # Metadata por defecto
        default_metadata = {
            'title': f"Prompt premium de {prompt_type} para: {functionality}",
            'functionality': functionality,
            'date': self.get_current_date(),
            'version': self.config.get('version', '0.1.0'),
            'type': 'premium',
            'premium_feature': prompt_type
        }
        
        # Combinar con metadata proporcionada
        file_metadata = {**default_metadata, **(metadata or {})}
        
        # Guardar archivo
        with open(file_path, 'w', encoding='utf-8') as f:
            # Añadir frontmatter
            f.write('---\n')
            yaml.dump(file_metadata, f, default_flow_style=False)
            f.write('---\n\n')
            
            # Escribir contenido
            f.write(content)
        
        return file_path
    
    def clear_structure(self, confirm: bool = False) -> bool:
        """
        Eliminar toda la estructura de archivos.
        
        Args:
            confirm: Si es True, se eliminará sin más confirmación
        
        Returns:
            True si se eliminó, False en caso contrario
        """
        if not os.path.exists(self.structure_root):
            logger.info("La estructura no existe, nada que eliminar.")
            return False
        
        if not confirm:
            logger.warning("Se solicitó eliminar la estructura pero no se confirmó la operación.")
            return False
        
        # Eliminar todo el directorio
        shutil.rmtree(self.structure_root)
        logger.info(f"Estructura eliminada: {self.structure_root}")
        return True
    
    def _create_directories(self) -> List[str]:
        """
        Crear los directorios de la estructura.
        
        Returns:
            Lista de directorios creados
        """
        # Directorios a crear
        directories = [
            self.structure_root,
            os.path.join(self.structure_root, self.config['structure']['functionalities_dir']),
            os.path.join(self.structure_root, self.config['structure']['prompts_dir']),
            os.path.join(self.structure_root, self.config['structure']['prompts_functionality_dir']),
        ]
        
        created = []
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                created.append(directory)
                logger.debug(f"Directorio creado: {directory}")
        
        return created
    
    def _create_base_files(self) -> List[str]:
        """
        Crear los archivos base de la estructura.
        
        Returns:
            Lista de archivos creados
        """
        created_files = []
        
        # Crear archivo de análisis general
        analysis_content = (
            f"# Análisis del proyecto: {self.config['project_name']}\n\n"
            f"Este archivo contiene el análisis general del proyecto.\n\n"
            f"## Estructura general\n\n"
            f"*Este análisis será completado cuando se ejecute el analizador del proyecto.*\n\n"
        )
        
        analysis_path = self.save_analysis(analysis_content)
        created_files.append(analysis_path)
        
        # Crear prompt general
        prompt_content = (
            f"# Prompt general para {self.config['project_name']}\n\n"
            f"Este archivo contiene un prompt contextual general para el proyecto.\n\n"
            f"## Contexto del proyecto\n\n"
            f"*Este prompt será generado cuando se ejecute el generador de prompts.*\n\n"
        )
        
        prompt_path = self.save_prompt(prompt_content)
        created_files.append(prompt_path)
        
        return created_files
    
    def _save_config(self) -> str:
        """
        Guardar la configuración en un archivo YAML.
        
        Returns:
            Ruta al archivo de configuración
        """
        config_path = os.path.join(self.structure_root, self.config['structure']['config'])
        
        # Preparar configuración para guardar
        config_to_save = {
            'project_name': self.config['project_name'],
            'version': self.config['version'],
            'language': self.config['language'],
            'last_updated': self.get_current_date(),
            'structure_version': '0.1.0'
        }
        
        # Guardar configuración
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_to_save, f, default_flow_style=False)
        
        logger.debug(f"Configuración guardada en: {config_path}")
        return config_path
    
    def _update_existing_structure(self) -> Dict[str, Any]:
        """
        Actualizar estructura existente de forma incremental.
        
        Returns:
            Diccionario con información de la actualización
        """
        # Verificar directorios existentes y crear los que faltan
        created_dirs = self._create_directories()
        
        # Actualizar configuración
        config_path = self._save_config()
        
        # No sobrescribimos archivos existentes, solo los que faltan
        created_files = []
        
        # Verificar archivo de análisis general
        analysis_path = self.get_file_path('analysis')
        if not os.path.exists(analysis_path):
            analysis_content = (
                f"# Análisis del proyecto: {self.config['project_name']}\n\n"
                f"Este archivo contiene el análisis general del proyecto.\n\n"
                f"## Estructura general\n\n"
                f"*Este análisis será completado cuando se ejecute el analizador del proyecto.*\n\n"
            )
            self.save_analysis(analysis_content)
            created_files.append(analysis_path)
        
        # Verificar prompt general
        prompt_path = self.get_file_path('prompt')
        if not os.path.exists(prompt_path):
            prompt_content = (
                f"# Prompt general para {self.config['project_name']}\n\n"
                f"Este archivo contiene un prompt contextual general para el proyecto.\n\n"
                f"## Contexto del proyecto\n\n"
                f"*Este prompt será generado cuando se ejecute el generador de prompts.*\n\n"
            )
            self.save_prompt(prompt_content)
            created_files.append(prompt_path)
        
        result = {
            'structure_root': self.structure_root,
            'directories_created': created_dirs,
            'files_created': created_files,
            'config_path': config_path,
            'status': 'updated'
        }
        
        logger.info(f"Estructura actualizada: {len(created_dirs)} nuevos directorios, {len(created_files)} nuevos archivos")
        return result


def get_project_structure(project_path: str, config: Optional[Dict[str, Any]] = None) -> ProjectStructure:
    """
    Obtener una instancia del gestor de estructura de proyecto.
    
    Args:
        project_path: Ruta al proyecto
        config: Configuración opcional
    
    Returns:
        Instancia del gestor de estructura
    """
    return ProjectStructure(project_path, config)
