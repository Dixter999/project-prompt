#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simplified ProjectScanner for the new architecture.

Scans project structure, files and directories without UI dependencies.
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import Counter

try:
    from models.project import ProjectStructure, FileInfo, DirectoryInfo, ScanConfig
except ImportError:
    # Fallback for direct execution
    from models.project import ProjectStructure, FileInfo, DirectoryInfo, ScanConfig


class ProjectScanner:
    """Simplified scanner for file and directory structure."""
    
    def __init__(self, config: Optional[ScanConfig] = None):
        """
        Initialize the project scanner.
        
        Args:
            config: Scanner configuration
        """
        self.config = config or ScanConfig()
        self.max_file_size = self.config.max_file_size_mb * 1024 * 1024  # Convert to bytes
        
        # Internal results
        self.reset()
    
    def reset(self):
        """Reset internal state."""
        self.files = []
        self.directories = []
        self.languages = {}
        self.stats = {
            'total_files': 0,
            'total_dirs': 0,
            'analyzed_files': 0,
            'binary_files': 0,
            'skipped_files': 0,
            'total_size_kb': 0,
        }
    
    def scan_project(self, project_path: str) -> ProjectStructure:
        """
        Scan a project and analyze its structure.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            ProjectStructure with complete information
        """
        start_time = time.time()
        self.reset()
        
        if not os.path.isdir(project_path):
            raise ValueError(f"Path is not a valid directory: {project_path}")
        
        # Scan recursively
        self._scan_directory(project_path, project_path)
        
        # Analyze main language
        self._analyze_languages()
        
        # Build result
        return ProjectStructure(
            root_path=project_path,
            files=self.files,
            directories=self.directories,
            total_files=self.stats['total_files'],
            total_directories=self.stats['total_dirs'],
            total_size=self.stats['total_size_kb'] * 1024,  # Convert back to bytes
            languages=self.languages,
            main_language=self._get_main_language()
        )
    
    def _scan_directory(self, dir_path: str, base_path: str, depth: int = 0):
        """Scan directory recursively."""
        if depth > 20:  # Prevent excessive recursion
            return
            
        # Early exit if we've hit file limit
        if self.stats['total_files'] >= self.config.max_files:
            return
            
        self.stats['total_dirs'] += 1
        
        try:
            items = os.listdir(dir_path)
            
            # Count files and subdirectories
            files_in_dir = 0
            subdirs_in_dir = 0
            dir_size = 0
            
            for item_name in items:
                # Check file limit
                if self.stats['total_files'] >= self.config.max_files:
                    break
                
                item_path = os.path.join(dir_path, item_name)
                
                if os.path.isdir(item_path):
                    subdirs_in_dir += 1
                    if not self._should_ignore_dir(item_name):
                        self._scan_directory(item_path, base_path, depth + 1)
                
                elif os.path.isfile(item_path):
                    files_in_dir += 1
                    if not self._should_ignore_file(item_name):
                        file_info = self._scan_file(item_path, base_path)
                        if file_info:
                            dir_size += file_info.size
            
            # Create directory info
            rel_path = os.path.relpath(dir_path, base_path)
            if rel_path != '.':  # Don't add root directory
                dir_info = DirectoryInfo(
                    path=rel_path,
                    name=os.path.basename(dir_path),
                    file_count=files_in_dir,
                    subdirectory_count=subdirs_in_dir,
                    total_size=dir_size
                )
                self.directories.append(dir_info)
        
        except (PermissionError, OSError):
            # Ignore directories without permissions
            pass
    
    def _scan_file(self, file_path: str, base_path: str):
        """Scan individual file."""
        self.stats['total_files'] += 1
        
        try:
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                self.stats['skipped_files'] += 1
                return
            
            # Analyze file
            file_info = self._analyze_file(file_path, base_path)
            if file_info:
                self.files.append(file_info)
                self.stats['analyzed_files'] += 1
                self.stats['total_size_kb'] += file_info.size / 1024  # Convert bytes to KB
                
                # Count by language
                language = file_info.language
                if language:
                    if language not in self.languages:
                        self.languages[language] = {'files': 0, 'size_kb': 0}
                    self.languages[language]['files'] += 1
                    self.languages[language]['size_kb'] += file_info.size / 1024
            
        except (PermissionError, OSError):
            self.stats['skipped_files'] += 1
    
    def _analyze_file(self, file_path: str, base_path: str) -> Optional[FileInfo]:
        """Analyze file and extract basic information."""
        try:
            stat = os.stat(file_path)
            file_name = os.path.basename(file_path)
            rel_path = os.path.relpath(file_path, base_path)
            
            # Detect if binary
            is_binary = self._is_binary_file(file_path)
            if is_binary:
                self.stats['binary_files'] += 1
            
            # Detect language by extension
            language = self._detect_language(file_name)
            
            return FileInfo(
                path=rel_path,
                name=file_name,
                extension=self._get_extension(file_name),
                size=stat.st_size,
                language=language or "unknown"
            )
            
        except Exception:
            return None
    
    def _is_binary_file(self, file_path: str) -> bool:
        """Verificar si archivo es binario."""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk
        except:
            return True
    
    def _detect_language(self, file_name: str) -> Optional[str]:
        """Detectar lenguaje por extensión de archivo."""
        ext = self._get_extension(file_name).lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'react',
            '.tsx': 'react',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.ini': 'ini',
            '.md': 'markdown',
            '.rst': 'rst',
            '.txt': 'text',
            '.sql': 'sql',
            '.sh': 'bash',
            '.bash': 'bash',
            '.zsh': 'zsh',
            '.fish': 'fish',
            '.ps1': 'powershell',
            '.bat': 'batch',
            '.dockerfile': 'docker',
        }
        
        return language_map.get(ext)
    
    def _get_extension(self, file_name: str) -> str:
        """Obtener extensión de archivo."""
        if '.' not in file_name:
            return ''
        return '.' + file_name.split('.')[-1]
    
    def _should_ignore_dir(self, dir_name: str) -> bool:
        """Verificar si directorio debe ser ignorado."""
        return any(
            dir_name == ignore_dir
            or (dir_name.startswith('.') and dir_name not in ['.github'])
            or (ignore_dir.startswith('*') and dir_name.endswith(ignore_dir[1:]))
            or (ignore_dir.endswith('*') and dir_name.startswith(ignore_dir[:-1]))
            for ignore_dir in self.config.ignore_dirs
        )
    
    def _should_ignore_file(self, file_name: str) -> bool:
        """Verificar si archivo debe ser ignorado."""
        return any(
            file_name == pattern
            or (file_name.startswith('.') and file_name not in ['.gitignore', '.env'])
            or (pattern.startswith('*') and file_name.endswith(pattern[1:]))
            or (pattern.endswith('*') and file_name.startswith(pattern[:-1]))
            for pattern in self.config.ignore_files
        )
    
    def _analyze_languages(self):
        """Analizar distribución de lenguajes."""
        if not self.languages:
            return
        
        total_files = sum(lang['files'] for lang in self.languages.values())
        
        # Calcular porcentajes
        for lang_data in self.languages.values():
            percentage = (lang_data['files'] / total_files * 100) if total_files else 0
            lang_data['percentage'] = round(percentage, 1)
        
        # Identificar lenguajes principales
        main_languages = [
            name for name, data in self.languages.items() 
            if data['percentage'] >= 10
        ]
        
        self.languages['_main'] = main_languages
    
    def _get_main_language(self) -> str:
        """Get the main language as a string."""
        main_languages = self.languages.get('_main', [])
        if main_languages:
            return main_languages[0]  # Return the most prominent language
        elif self.languages:
            # Return the language with the most files
            lang_counts = {lang: data['files'] for lang, data in self.languages.items() if lang != '_main'}
            if lang_counts:
                return max(lang_counts, key=lang_counts.get)
        return "unknown"
