#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para el análisis básico de archivos.

Este módulo proporciona funcionalidades para identificar el tipo de archivo,
lenguaje de programación y contenido relevante dentro de los archivos de un proyecto.
"""

import os
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
import re
import json

from src.utils.logger import get_logger

# Configurar logger
logger = get_logger()

# Mapeo de extensiones a lenguajes de programación
LANGUAGE_EXTENSIONS = {
    # Lenguajes comunes
    '.py': 'Python',
    '.js': 'JavaScript',
    '.jsx': 'JavaScript (React)',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript (React)',
    '.html': 'HTML',
    '.css': 'CSS',
    '.scss': 'SCSS',
    '.sass': 'Sass',
    '.less': 'Less',
    '.json': 'JSON',
    '.xml': 'XML',
    '.md': 'Markdown',
    '.yml': 'YAML',
    '.yaml': 'YAML',
    
    # Lenguajes de backend
    '.java': 'Java',
    '.cs': 'C#',
    '.go': 'Go',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.pl': 'Perl',
    '.sh': 'Shell',
    '.bash': 'Bash',
    '.rs': 'Rust',
    '.c': 'C',
    '.cpp': 'C++',
    '.h': 'C/C++ Header',
    '.swift': 'Swift',
    '.kt': 'Kotlin',
    
    # Configuración y datos
    '.toml': 'TOML',
    '.ini': 'INI',
    '.cfg': 'Configuration',
    '.conf': 'Configuration',
    '.env': 'Environment',
    '.sql': 'SQL',
    '.csv': 'CSV',
    '.lock': 'Lock File',
    '.ipynb': 'Jupyter Notebook',
    '.graphql': 'GraphQL',
    '.proto': 'Protocol Buffers',
}

# Archivos importantes por función
IMPORTANT_FILES = {
    'main': [
        'main.py', 'app.py', 'index.py', 'server.py', 'start.py', 'run.py',
        'main.js', 'index.js', 'app.js', 'server.js',
        'program.cs', 'Main.java', 'main.go', 'index.ts', 'app.ts',
    ],
    'config': [
        'config.py', 'settings.py', '.env', '.env.example', '.env.sample',
        'config.js', 'config.json', 'config.yml', 'config.yaml',
        'appsettings.json', 'package.json', 'pyproject.toml', 'setup.py',
        '.gitignore', '.dockerignore', '.editorconfig', 'tsconfig.json',
        'vite.config.js', 'webpack.config.js', 'babel.config.js', 'jest.config.js',
        'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
        'requirements.txt', 'Pipfile', 'Pipfile.lock',
    ],
    'documentation': [
        'README.md', 'README.rst', 'CONTRIBUTING.md', 'CHANGELOG.md', 'LICENSE',
        'docs/', 'documentation/', 'wiki/', 'INSTALL.md', 'USAGE.md', 'API.md',
    ],
    'test': [
        'test_', 'tests/', 'spec_', 'specs/', '_test.py', '_spec.py',
        'test.js', 'spec.js', '*Tests.cs', '*Test.java',
    ],
}

# Patrones para identificar dependencias
DEPENDENCY_PATTERNS = {
    'Python': [
        r'^\s*import\s+([a-zA-Z0-9_.,\s]+)$',
        r'^\s*from\s+([a-zA-Z0-9_.]+)\s+import\s+',
        r'^\s*require\s*\(["\']([^"\']+)["\']\)',
    ],
    'JavaScript': [
        r'^\s*import\s+.*\s+from\s+["\']([^"\']+)["\']',
        r'^\s*require\s*\(["\']([^"\']+)["\']\)',
        r'^\s*import\s+["\']([^"\']+)["\']',
    ],
    'TypeScript': [
        r'^\s*import\s+.*\s+from\s+["\']([^"\']+)["\']',
        r'^\s*require\s*\(["\']([^"\']+)["\']\)',
        r'^\s*import\s+["\']([^"\']+)["\']',
    ],
    'Java': [
        r'^\s*import\s+([a-zA-Z0-9_.]+)(?:;|\s)',
    ],
    'C#': [
        r'^\s*using\s+([a-zA-Z0-9_.]+)(?:;|\s)',
    ],
}


class FileAnalyzer:
    """Analizador de archivos de código y configuración."""

    def __init__(self, max_file_size_mb: float = 5.0):
        """
        Inicializar el analizador de archivos.
        
        Args:
            max_file_size_mb: Tamaño máximo de archivo a analizar en MB
        """
        self.max_file_size = max_file_size_mb * 1024 * 1024  # Convertir a bytes
        mimetypes.init()
    
    def get_file_type(self, file_path: str) -> Dict[str, Any]:
        """
        Determinar el tipo de archivo y su lenguaje de programación.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Dict con información del archivo (tipo, lenguaje, etc.)
        """
        file_info = {
            'path': file_path,
            'name': os.path.basename(file_path),
            'extension': os.path.splitext(file_path)[1].lower(),
            'size': os.path.getsize(file_path),
            'is_binary': False,
            'language': None,
            'mime_type': None,
            'category': self._categorize_file(file_path),
        }
        
        # Determinar tipo MIME
        mime_type, _ = mimetypes.guess_type(file_path)
        file_info['mime_type'] = mime_type
        
        # Determinar si es binario o texto
        file_info['is_binary'] = self._is_binary_file(file_path)
        
        # Obtener lenguaje por extensión
        if file_info['extension'] in LANGUAGE_EXTENSIONS:
            file_info['language'] = LANGUAGE_EXTENSIONS[file_info['extension']]
        
        # Si no se identificó por extensión, intentar por contenido
        if not file_info['language'] and not file_info['is_binary']:
            file_info['language'] = self._detect_language_by_content(file_path)
        
        return file_info
    
    def _is_binary_file(self, file_path: str) -> bool:
        """
        Determinar si un archivo es binario.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si es binario, False si es texto
        """
        try:
            # Verificar por tamaño primero
            if os.path.getsize(file_path) > self.max_file_size:
                return True
                
            # Leer primeros bytes para detección
            with open(file_path, 'rb') as f:
                chunk = f.read(4096)
                return b'\0' in chunk  # Archivo binario si contiene byte nulo
        except Exception as e:
            logger.warning(f"Error al verificar si {file_path} es binario: {e}")
            return True  # En caso de error, asumir binario por seguridad
    
    def _detect_language_by_content(self, file_path: str) -> Optional[str]:
        """
        Detectar el lenguaje de programación por el contenido del archivo.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Nombre del lenguaje o None
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(4096)  # Leer solo los primeros 4KB
                
            # Buscar pistas en el contenido
            if content.startswith('#!/usr/bin/env python'):
                return 'Python'
            elif content.startswith('#!/usr/bin/env node'):
                return 'JavaScript'
            elif content.startswith('<?php'):
                return 'PHP'
            elif '<?xml' in content[:100]:
                return 'XML'
            elif content.strip().startswith('{') and content.strip().endswith('}'):
                try:
                    # Probar si es JSON válido
                    json.loads(content)
                    return 'JSON'
                except:
                    pass
            
        except Exception as e:
            logger.warning(f"Error al detectar lenguaje por contenido en {file_path}: {e}")
        
        return None
    
    def _categorize_file(self, file_path: str) -> Optional[str]:
        """
        Categorizar el archivo según su nombre y ruta.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Categoría del archivo o None
        """
        filename = os.path.basename(file_path)
        relpath = file_path  # En una implementación real, obtener path relativo
        
        # Verificar cada categoría
        for category, patterns in IMPORTANT_FILES.items():
            for pattern in patterns:
                if pattern.endswith('/'):  # Es un directorio
                    dir_name = pattern.rstrip('/')
                    if dir_name in relpath.split(os.path.sep):
                        return category
                elif pattern.startswith('*') and filename.endswith(pattern[1:]):
                    return category
                elif pattern.endswith('*') and filename.startswith(pattern[:-1]):
                    return category
                elif pattern in filename:
                    return category
        
        return None
    
    def extract_dependencies(self, file_path: str, file_language: Optional[str] = None) -> Set[str]:
        """
        Extraer dependencias del archivo basado en el lenguaje.
        
        Args:
            file_path: Ruta al archivo
            file_language: Lenguaje del archivo (opcional)
            
        Returns:
            Conjunto de dependencias encontradas
        """
        if not file_language:
            file_info = self.get_file_type(file_path)
            file_language = file_info['language']
        
        if not file_language or file_language not in DEPENDENCY_PATTERNS:
            return set()
            
        dependencies = set()
        
        try:
            # Solo analizar archivos de texto y no demasiado grandes
            if os.path.getsize(file_path) <= self.max_file_size and not self._is_binary_file(file_path):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        
                        # Aplicar patrones para este lenguaje
                        for pattern in DEPENDENCY_PATTERNS[file_language]:
                            matches = re.findall(pattern, line)
                            if matches:
                                # Limpiar resultados
                                for match in matches:
                                    # Eliminar alias y extraer solo el nombre del paquete/módulo
                                    dependency = match.split(' as ')[0].strip()
                                    dependency = dependency.split('.')[0]  # Solo primer componente
                                    dependencies.add(dependency)
        except Exception as e:
            logger.warning(f"Error al extraer dependencias de {file_path}: {e}")
            
        return dependencies
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analizar un archivo completamente.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Dict con análisis completo del archivo
        """
        # Obtener tipo de archivo y lenguaje
        file_info = self.get_file_type(file_path)
        
        # Si no es un archivo binario y tiene lenguaje identificado, extraer dependencias
        if not file_info['is_binary'] and file_info['language']:
            file_info['dependencies'] = list(self.extract_dependencies(file_path, file_info['language']))
        else:
            file_info['dependencies'] = []
            
        # Calcular información adicional
        file_info['size_kb'] = round(file_info['size'] / 1024, 2)
        file_info['is_important'] = bool(file_info['category'])
        
        return file_info


def get_file_analyzer(max_file_size_mb: float = 5.0) -> FileAnalyzer:
    """
    Obtener una instancia del analizador de archivos.
    
    Args:
        max_file_size_mb: Tamaño máximo de archivo a analizar en MB
        
    Returns:
        Instancia de FileAnalyzer
    """
    return FileAnalyzer(max_file_size_mb=max_file_size_mb)
