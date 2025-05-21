"""Project structure analysis functionality.

This module provides tools for analyzing and navigating project directory structures.
"""

import os
import fnmatch
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Union

logger = logging.getLogger(__name__)


class ProjectStructureAnalyzer:
    """Analyzes project structure and provides information about files and directories."""
    
    # Common directories to ignore
    IGNORE_DIRS = {
        # Version control
        '.git', '.hg', '.svn',
        # Python
        '__pycache__', '.pytest_cache', '.mypy_cache',
        # Virtual environments
        'venv', 'env', '.venv',
        # Build and distribution
        'build', 'dist', '*.egg-info',
        # Node.js
        'node_modules',
        # IDEs and editors
        '.idea', '.vscode',
        # OS generated
        '.DS_Store', 'Thumbs.db',
    }
    
    # Common files to ignore
    IGNORE_FILES = {
        # Compiled files
        '*.pyc', '*.pyo', '*.pyd', '*.so',
        # Archives
        '*.zip', '*.tar.gz',
        # Logs and databases
        '*.log', '*.sqlite', '*.db',
        # Environment and credentials
        '.env', '*.pem', '*.key',
    }
    
    def __init__(self, root_path: Union[str, Path]):
        """Initialize with the project root path.
        
        Args:
            root_path: Path to the project root directory
        """
        self.root_path = Path(root_path).resolve()
        if not self.root_path.is_dir():
            raise NotADirectoryError(f"Directory not found: {self.root_path}")
        
        self._file_cache: Dict[str, List[Path]] = {}
        self._build_file_cache()
    
    def _should_ignore(self, name: str, is_dir: bool = False) -> bool:
        """Check if a file/directory should be ignored."""
        patterns = self.IGNORE_DIRS if is_dir else self.IGNORE_FILES
        return any(fnmatch.fnmatch(name, pattern) for pattern in patterns)
    
    def _build_file_cache(self) -> None:
        """Build a cache of files in the project, organized by extension."""
        self._file_cache = {}
        
        for root, dirs, files in os.walk(self.root_path, topdown=True):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore(d, is_dir=True)]
            
            # Get relative path from project root
            rel_root = Path(root).relative_to(self.root_path)
            
            for file in files:
                # Skip ignored files
                if self._should_ignore(file, is_dir=False):
                    continue
                
                # Get file extension (including the dot)
                ext = os.path.splitext(file)[1].lower()
                if not ext:
                    ext = '.no_extension'
                
                # Add to cache
                if ext not in self._file_cache:
                    self._file_cache[ext] = []
                
                file_path = rel_root / file
                self._file_cache[ext].append(file_path)
    
    def get_project_structure(self) -> Dict[str, Any]:
        """Get the project structure as a nested dictionary."""
        def build_structure(path: Path) -> Union[Dict, List]:
            if not path.is_dir():
                return []
                
            structure: Dict[str, Any] = {}
            
            # Process directories
            for item in sorted(path.iterdir()):
                if item.is_dir() and not self._should_ignore(item.name, is_dir=True):
                    structure[item.name] = build_structure(item)
                elif item.is_file() and not self._should_ignore(item.name, is_dir=False):
                    if '_files' not in structure:
                        structure['_files'] = []
                    structure['_files'].append(item.name)
                
            return structure
        
        return build_structure(self.root_path)
    
    def find_files_by_extension(self, extension: str) -> List[Path]:
        """Find all files with the given extension in the project."""
        if not extension.startswith('.'):
            extension = f'.{extension}'
        return self._file_cache.get(extension.lower(), [])
    
    def get_file_contents(self, relative_path: Union[str, Path]) -> str:
        """Get the contents of a file in the project."""
        file_path = self.root_path / relative_path
        
        # Security check
        try:
            file_path = file_path.resolve()
            if self.root_path.resolve() not in file_path.parents and file_path != self.root_path.resolve():
                raise ValueError(f"Path {file_path} is outside project root {self.root_path}")
        except (ValueError, RuntimeError) as e:
            raise FileNotFoundError(f"Invalid path: {e}")
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")
            
        if not file_path.is_file():
            raise IOError(f"Path is not a file: {relative_path}")
            
        try:
            return file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                return file_path.read_bytes().decode('utf-8', errors='replace')
            except Exception as e:
                raise IOError(f"Could not read file {relative_path}: {e}")
    
    def get_file_metadata(self, relative_path: Union[str, Path]) -> Dict[str, Any]:
        """Get metadata about a file in the project."""
        file_path = self.root_path / relative_path
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")
            
        stat = file_path.stat()
        
        return {
            'path': str(relative_path),
            'size': stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'is_dir': file_path.is_dir(),
            'is_file': file_path.is_file(),
            'extension': ''.join(file_path.suffixes),
            'name': file_path.name,
            'parent': str(file_path.parent.relative_to(self.root_path))
        }
