#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gestor de archivos markdown para ProjectPrompt.

Este módulo proporciona herramientas para crear, actualizar y gestionar
la documentación en formato markdown, incluyendo el seguimiento de cambios
y la aplicación de plantillas.
"""

import os
import re
import shutil
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple

from jinja2 import Template, Environment, FileSystemLoader
import frontmatter

from src.utils.logger import get_logger

logger = get_logger()


class MarkdownManager:
    """
    Gestor de documentación en formato markdown.
    
    Esta clase proporciona funcionalidades para crear, actualizar y gestionar
    documentos markdown, aplicando plantillas y manteniendo un historial de cambios.
    """
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Inicializar el gestor de markdown.
        
        Args:
            templates_dir: Directorio donde se encuentran las plantillas
        """
        # Directorio base para plantillas
        self.templates_dir = templates_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'templates', 'documentation'
        )
        
        # Configurar entorno de Jinja2
        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        
    def create_document(self, 
                        template_name: str, 
                        output_path: str, 
                        context: Dict[str, Any],
                        frontmatter_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Crear un nuevo documento markdown a partir de una plantilla.
        
        Args:
            template_name: Nombre de la plantilla a utilizar
            output_path: Ruta donde se guardará el documento
            context: Contexto para renderizar la plantilla
            frontmatter_data: Datos para incluir en el frontmatter del documento
            
        Returns:
            Ruta al documento creado
        """
        # Asegurar que el directorio existe
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Si ya existe un documento, actualizar en lugar de crear
        if os.path.exists(output_path):
            return self.update_document(output_path, context, frontmatter_data)
        
        try:
            # Cargar plantilla
            template_path = self._resolve_template_path(template_name)
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
                
            # Renderizar documento
            template = Template(template_content)
            content = template.render(**context)
            
            # Añadir frontmatter si existe
            if frontmatter_data:
                # Agregar timestamp de creación
                frontmatter_data['created'] = datetime.datetime.now().isoformat()
                frontmatter_data['updated'] = frontmatter_data['created']
                frontmatter_data['version'] = 1
                
                # Crear objeto frontmatter
                doc = frontmatter.Post(content, **frontmatter_data)
                content = frontmatter.dumps(doc)
            
            # Guardar documento
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.info(f"Documento creado: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error al crear documento markdown: {e}", exc_info=True)
            raise
    
    def update_document(self, 
                        doc_path: str, 
                        context: Dict[str, Any],
                        frontmatter_data: Optional[Dict[str, Any]] = None,
                        template_name: Optional[str] = None) -> str:
        """
        Actualizar un documento markdown existente.
        
        Args:
            doc_path: Ruta al documento a actualizar
            context: Nuevo contexto para actualizar contenido
            frontmatter_data: Nuevos datos para el frontmatter
            template_name: Si se proporciona, se usará esta plantilla
            
        Returns:
            Ruta al documento actualizado
        """
        if not os.path.exists(doc_path):
            if template_name:
                return self.create_document(template_name, doc_path, context, frontmatter_data)
            else:
                raise FileNotFoundError(f"El documento {doc_path} no existe")
        
        try:
            # Leer documento existente
            with open(doc_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            # Si hay una plantilla específica, usarla para reemplazar contenido
            if template_name:
                template_path = self._resolve_template_path(template_name)
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                
                template = Template(template_content)
                new_content = template.render(**context)
                post.content = new_content
            else:
                # Actualizar secciones del contenido existente sin reemplazar todo
                self._update_content_sections(post, context)
            
            # Actualizar frontmatter si se proporcionó
            if frontmatter_data:
                for key, value in frontmatter_data.items():
                    post[key] = value
            
            # Actualizar metadatos de control de versiones
            post['updated'] = datetime.datetime.now().isoformat()
            if 'version' in post:
                post['version'] = post['version'] + 1
            else:
                post['version'] = 1
                
            # Mantener historial de cambios
            if 'history' not in post:
                post['history'] = []
                
            # Añadir entrada al historial
            history_entry = {
                'timestamp': post['updated'],
                'version': post['version']
            }
            post['history'].append(history_entry)
            
            # Guardar documento actualizado
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter.dumps(post))
            
            logger.info(f"Documento actualizado: {doc_path} (versión {post['version']})")
            return doc_path
            
        except Exception as e:
            logger.error(f"Error al actualizar documento markdown: {e}", exc_info=True)
            raise
    
    def create_documentation_structure(self, base_dir: str, structure_config: Dict[str, Any]) -> Dict[str, str]:
        """
        Crear una estructura de documentación completa.
        
        Args:
            base_dir: Directorio base para la documentación
            structure_config: Configuración de la estructura
            
        Returns:
            Diccionario con rutas a documentos creados
        """
        created_paths = {}
        
        # Asegurar que el directorio base existe
        os.makedirs(base_dir, exist_ok=True)
        
        try:
            # Procesar cada elemento de la estructura
            for item_name, item_config in structure_config.items():
                if isinstance(item_config, dict):
                    # Es un subdirectorio con archivos
                    subdir = os.path.join(base_dir, item_name)
                    os.makedirs(subdir, exist_ok=True)
                    
                    # Crear archivos en este subdirectorio
                    for file_name, file_config in item_config.items():
                        if isinstance(file_config, dict):
                            file_path = os.path.join(subdir, f"{file_name}.md")
                            template = file_config.get('template')
                            context = file_config.get('context', {})
                            frontmatter_data = file_config.get('frontmatter', {})
                            
                            created_paths[f"{item_name}/{file_name}"] = self.create_document(
                                template, file_path, context, frontmatter_data
                            )
                else:
                    # Es un archivo en el directorio base
                    file_path = os.path.join(base_dir, f"{item_name}.md")
                    template = item_config.get('template')
                    context = item_config.get('context', {})
                    frontmatter_data = item_config.get('frontmatter', {})
                    
                    created_paths[item_name] = self.create_document(
                        template, file_path, context, frontmatter_data
                    )
            
            return created_paths
            
        except Exception as e:
            logger.error(f"Error al crear estructura de documentación: {e}", exc_info=True)
            raise
    
    def get_document_info(self, doc_path: str) -> Dict[str, Any]:
        """
        Obtener información sobre un documento markdown.
        
        Args:
            doc_path: Ruta al documento
            
        Returns:
            Diccionario con información sobre el documento
        """
        if not os.path.exists(doc_path):
            raise FileNotFoundError(f"El documento {doc_path} no existe")
        
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            # Extraer información básica
            info = {
                'path': doc_path,
                'filename': os.path.basename(doc_path),
                'size': os.path.getsize(doc_path),
                'modified': datetime.datetime.fromtimestamp(os.path.getmtime(doc_path)).isoformat()
            }
            
            # Añadir metadatos del frontmatter
            for key, value in post.metadata.items():
                info[key] = value
                
            # Calcular estadísticas del contenido
            word_count = len(post.content.split())
            lines = post.content.count('\n') + 1
            
            info.update({
                'word_count': word_count,
                'lines': lines
            })
            
            return info
            
        except Exception as e:
            logger.error(f"Error al obtener información del documento: {e}", exc_info=True)
            raise
    
    def list_documents(self, base_dir: str, pattern: str = "**/*.md") -> List[Dict[str, Any]]:
        """
        Listar documentos markdown en un directorio.
        
        Args:
            base_dir: Directorio base para buscar
            pattern: Patrón glob para filtrar archivos
            
        Returns:
            Lista de información sobre documentos encontrados
        """
        try:
            documents = []
            base_path = Path(base_dir)
            
            # Buscar archivos que coincidan con el patrón
            for file_path in base_path.glob(pattern):
                if file_path.is_file():
                    # Obtener información básica
                    rel_path = file_path.relative_to(base_path)
                    try:
                        info = self.get_document_info(str(file_path))
                        info['relative_path'] = str(rel_path)
                        documents.append(info)
                    except Exception as e:
                        # Si hay error al procesar un documento, continuar con los demás
                        logger.warning(f"Error al procesar {file_path}: {e}")
                        documents.append({
                            'path': str(file_path),
                            'relative_path': str(rel_path),
                            'error': str(e)
                        })
            
            return documents
        
        except Exception as e:
            logger.error(f"Error al listar documentos: {e}", exc_info=True)
            raise
    
    def merge_documents(self, doc_paths: List[str], output_path: str, title: str) -> str:
        """
        Combinar varios documentos markdown en uno solo.
        
        Args:
            doc_paths: Lista de rutas a documentos a combinar
            output_path: Ruta donde se guardará el documento combinado
            title: Título para el documento combinado
            
        Returns:
            Ruta al documento combinado
        """
        try:
            combined_content = f"# {title}\n\n"
            source_docs = []
            
            for doc_path in doc_paths:
                if not os.path.exists(doc_path):
                    logger.warning(f"Documento no encontrado: {doc_path}")
                    continue
                    
                with open(doc_path, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                
                # Obtener nombre del documento para referencia
                doc_name = os.path.basename(doc_path).replace('.md', '')
                
                # Añadir contenido con encabezado separador
                combined_content += f"\n\n## De: {doc_name}\n\n"
                combined_content += post.content
                
                # Guardar metadatos del documento fuente
                source_docs.append({
                    'path': doc_path,
                    'name': doc_name,
                    'version': post.get('version', 1)
                })
            
            # Crear frontmatter para el documento combinado
            frontmatter_data = {
                'title': title,
                'created': datetime.datetime.now().isoformat(),
                'updated': datetime.datetime.now().isoformat(),
                'source_documents': source_docs,
                'combined': True,
                'version': 1
            }
            
            # Crear documento combinado
            doc = frontmatter.Post(combined_content, **frontmatter_data)
            
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Guardar documento
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter.dumps(doc))
            
            logger.info(f"Documentos combinados en: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error al combinar documentos: {e}", exc_info=True)
            raise
    
    def extract_section(self, doc_path: str, section_heading: str) -> str:
        """
        Extraer una sección específica de un documento markdown.
        
        Args:
            doc_path: Ruta al documento
            section_heading: Encabezado de la sección a extraer
            
        Returns:
            Contenido de la sección
        """
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Patrón para encontrar la sección
            pattern = fr'^(#+)\s*{re.escape(section_heading)}.*?$(.*?)(?:^(?:\1)(?!#)|\Z)'
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            
            if not match:
                logger.warning(f"Sección '{section_heading}' no encontrada en {doc_path}")
                return ""
            
            # Extraer contenido de la sección encontrada
            return match.group(2).strip()
            
        except Exception as e:
            logger.error(f"Error al extraer sección: {e}", exc_info=True)
            raise
    
    def _update_content_sections(self, post: frontmatter.Post, context: Dict[str, Any]) -> None:
        """
        Actualizar secciones específicas del contenido.
        
        Args:
            post: Objeto frontmatter.Post con el contenido actual
            context: Contexto con las secciones a actualizar
        """
        content = post.content
        
        # Si hay una clave 'sections' en el contexto, actualizar secciones
        sections = context.get('sections', {})
        for section_name, section_content in sections.items():
            # Buscar la sección en el contenido
            pattern = fr'^(#+)\s*{re.escape(section_name)}.*?$(.*?)(?:^(?:\1)(?!#)|\Z)'
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            
            if match:
                # Si la sección existe, reemplazarla
                header = match.group(0).split('\n')[0]  # Preservar encabezado original
                replacement = f"{header}\n{section_content.strip()}"
                content = content.replace(match.group(0), replacement)
            else:
                # Si la sección no existe, añadirla al final
                level = context.get('section_level', 2)
                header = '#' * level + f" {section_name}"
                content += f"\n\n{header}\n{section_content.strip()}"
        
        # Actualizar el contenido en el documento
        post.content = content
    
    def _resolve_template_path(self, template_name: str) -> str:
        """
        Resolver la ruta a una plantilla.
        
        Args:
            template_name: Nombre de la plantilla
            
        Returns:
            Ruta absoluta a la plantilla
        """
        # Si el nombre ya incluye la extensión, usarlo directamente
        if template_name.endswith('.md'):
            template_file = template_name
        else:
            template_file = f"{template_name}.md"
        
        # Si es una ruta absoluta, usarla directamente
        if os.path.isabs(template_name) and os.path.exists(template_name):
            return template_name
        
        # Buscar en el directorio de plantillas
        template_path = os.path.join(self.templates_dir, template_file)
        if os.path.exists(template_path):
            return template_path
        
        # Si no existe, probar sin extensión
        if not template_name.endswith('.md'):
            template_path = os.path.join(self.templates_dir, template_name)
            if os.path.exists(template_path):
                return template_path
        
        raise FileNotFoundError(f"Plantilla no encontrada: {template_name}")


def get_markdown_manager(templates_dir: Optional[str] = None) -> MarkdownManager:
    """
    Obtener una instancia del gestor de markdown.
    
    Args:
        templates_dir: Directorio de plantillas
        
    Returns:
        Instancia de MarkdownManager
    """
    return MarkdownManager(templates_dir)
