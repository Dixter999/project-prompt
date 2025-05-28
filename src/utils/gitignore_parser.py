#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilidad para parsear archivos .gitignore.

Este módulo proporciona funcionalidades para leer y aplicar reglas de .gitignore
al análisis de proyectos, evitando que se procesen archivos que deben ser ignorados.
"""

import os
import re
from typing import List, Set, Pattern
from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger()


class GitignoreParser:
    """
    Parser para archivos .gitignore que convierte patrones en reglas aplicables.
    
    Soporta la sintaxis estándar de .gitignore incluyendo:
    - Patrones con wildcards (* y **)
    - Negaciones (!)
    - Directorios específicos (/)
    - Comentarios (#)
    """
    
    def __init__(self, gitignore_path: str = None):
        """
        Inicializar el parser de gitignore.
        
        Args:
            gitignore_path: Ruta al archivo .gitignore. Si es None, buscará en el directorio actual.
        """
        self.patterns: List[Pattern[str]] = []
        self.negation_patterns: List[Pattern[str]] = []
        self.gitignore_path = gitignore_path
        
        if gitignore_path and os.path.exists(gitignore_path):
            self._load_gitignore(gitignore_path)
    
    def _load_gitignore(self, gitignore_path: str) -> None:
        """
        Cargar y parsear el archivo .gitignore.
        
        Args:
            gitignore_path: Ruta al archivo .gitignore
        """
        try:
            with open(gitignore_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            logger.debug(f"Cargando reglas de .gitignore desde: {gitignore_path}")
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Ignorar líneas vacías y comentarios
                if not line or line.startswith('#'):
                    continue
                
                # Procesar patrón
                try:
                    is_negation = line.startswith('!')
                    if is_negation:
                        line = line[1:]  # Remover el !
                    
                    pattern = self._convert_gitignore_pattern_to_regex(line)
                    compiled_pattern = re.compile(pattern)
                    
                    if is_negation:
                        self.negation_patterns.append(compiled_pattern)
                    else:
                        self.patterns.append(compiled_pattern)
                        
                    logger.debug(f"Patrón añadido (línea {line_num}): {line} -> {pattern}")
                    
                except re.error as e:
                    logger.warning(f"Error al compilar patrón de gitignore en línea {line_num}: {line} - {e}")
                    
        except Exception as e:
            logger.error(f"Error al cargar archivo .gitignore {gitignore_path}: {e}")
    
    def _convert_gitignore_pattern_to_regex(self, pattern: str) -> str:
        """
        Convertir un patrón de .gitignore a expresión regular.
        
        Args:
            pattern: Patrón de .gitignore
            
        Returns:
            Expresión regular equivalente
        """
        # Escapar caracteres especiales de regex
        escaped = re.escape(pattern)
        
        # Reemplazar wildcards escapados por sus equivalentes regex
        # ** significa cualquier directorio (incluyendo subdirectorios)
        escaped = escaped.replace(r'\*\*', '.*')
        # * significa cualquier secuencia de caracteres excepto /
        escaped = escaped.replace(r'\*', '[^/]*')
        # ? significa cualquier carácter excepto /
        escaped = escaped.replace(r'\?', '[^/]')
        
        # Si el patrón termina con /, solo coincide con directorios
        if pattern.endswith('/'):
            escaped += '(?:/.*)?'
        
        # Si el patrón no comienza con /, puede estar en cualquier nivel
        if not pattern.startswith('/'):
            escaped = f'(?:^|.*/)(?:{escaped})'
        else:
            # Remover el / inicial para que coincida desde la raíz
            escaped = escaped[1:] if escaped.startswith('/') else escaped
        
        # Asegurar que coincida con el final de la ruta o con un directorio
        if not pattern.endswith('/'):
            escaped = f'{escaped}(?:/.*)?$'
        
        return escaped
    
    def should_ignore(self, file_path: str, project_root: str = None) -> bool:
        """
        Verificar si un archivo/directorio debe ser ignorado según las reglas de .gitignore.
        
        Args:
            file_path: Ruta del archivo o directorio a verificar
            project_root: Ruta raíz del proyecto (para calcular rutas relativas)
            
        Returns:
            True si debe ser ignorado, False en caso contrario
        """
        if not self.patterns and not self.negation_patterns:
            return False
        
        # Convertir a ruta relativa si se proporciona project_root
        if project_root:
            try:
                relative_path = os.path.relpath(file_path, project_root)
                # Normalizar separadores a /
                relative_path = relative_path.replace(os.sep, '/')
            except ValueError:
                # Si hay error (ej: diferentes drives), usar ruta absoluta
                relative_path = file_path.replace(os.sep, '/')
        else:
            relative_path = file_path.replace(os.sep, '/')
        
        # Verificar patrones de ignorar
        ignored = False
        for pattern in self.patterns:
            if pattern.match(relative_path):
                ignored = True
                logger.debug(f"Archivo ignorado por patrón: {relative_path}")
                break
        
        # Verificar patrones de negación (!)
        if ignored:
            for negation_pattern in self.negation_patterns:
                if negation_pattern.match(relative_path):
                    ignored = False
                    logger.debug(f"Archivo incluido por patrón de negación: {relative_path}")
                    break
        
        return ignored
    
    def get_ignored_count(self) -> int:
        """Obtener el número de patrones de ignorar cargados."""
        return len(self.patterns)
    
    def get_negation_count(self) -> int:
        """Obtener el número de patrones de negación cargados."""
        return len(self.negation_patterns)


def find_gitignore(project_path: str) -> str:
    """
    Buscar el archivo .gitignore en el proyecto.
    
    Args:
        project_path: Ruta del proyecto
        
    Returns:
        Ruta al archivo .gitignore o None si no se encuentra
    """
    gitignore_path = os.path.join(project_path, '.gitignore')
    if os.path.exists(gitignore_path):
        return gitignore_path
    return None


def get_gitignore_parser(project_path: str) -> GitignoreParser:
    """
    Obtener un parser de .gitignore para el proyecto dado.
    
    Args:
        project_path: Ruta del proyecto
        
    Returns:
        Instancia de GitignoreParser
    """
    gitignore_path = find_gitignore(project_path)
    return GitignoreParser(gitignore_path)
