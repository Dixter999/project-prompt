"""
Project Structure Analyzer Module.

This module provides functionality to analyze the structure of a project,
including directory hierarchy, file organization, and structural patterns.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict

logger = logging.getLogger(__name__)


class ProjectStructureAnalyzer:
    """Analyzer for project structure and organization."""
    
    def __init__(self, max_depth: int = 10, exclude_dirs: Optional[Set[str]] = None):
        """
        Initialize the project structure analyzer.
        
        Args:
            max_depth: Maximum directory depth to analyze
            exclude_dirs: Set of directory names to exclude from analysis
        """
        self.max_depth = max_depth
        self.exclude_dirs = exclude_dirs or {
            '.git', '.svn', '__pycache__', '.pytest_cache', 
            'node_modules', '.venv', 'venv', '.env', 'dist', 'build'
        }
    
    def analyze_structure(self, project_path: str) -> Dict[str, Any]:
        """
        Analyze the structure of a project.
        
        Args:
            project_path: Path to the project root
            
        Returns:
            Dict containing structure analysis results
        """
        project_path = Path(project_path).resolve()
        
        if not project_path.exists():
            raise FileNotFoundError(f"Project path does not exist: {project_path}")
        
        if not project_path.is_dir():
            raise ValueError(f"Project path is not a directory: {project_path}")
        
        analysis = {
            'project_path': str(project_path),
            'project_name': project_path.name,
            'structure': self._analyze_directory_structure(project_path),
            'statistics': {},
            'patterns': {},
            'recommendations': []
        }
        
        # Calculate statistics
        analysis['statistics'] = self._calculate_statistics(analysis['structure'])
        
        # Detect patterns
        analysis['patterns'] = self._detect_patterns(analysis['structure'])
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _analyze_directory_structure(self, path: Path, current_depth: int = 0) -> Dict[str, Any]:
        """
        Recursively analyze directory structure.
        
        Args:
            path: Current path to analyze
            current_depth: Current recursion depth
            
        Returns:
            Dict representing the directory structure
        """
        if current_depth > self.max_depth:
            return {"error": "Max depth exceeded"}
        
        if path.name in self.exclude_dirs:
            return {"excluded": True}
        
        structure = {
            'name': path.name,
            'type': 'directory' if path.is_dir() else 'file',
            'path': str(path),
            'size': 0,
            'children': [],
            'file_count': 0,
            'dir_count': 0
        }
        
        if path.is_file():
            try:
                structure['size'] = path.stat().st_size
                structure['extension'] = path.suffix.lower()
            except (OSError, IOError):
                structure['size'] = 0
            return structure
        
        # Process directory contents
        try:
            for item in sorted(path.iterdir()):
                if item.name.startswith('.') and item.name not in {'.gitignore', '.env.example'}:
                    continue
                    
                child_structure = self._analyze_directory_structure(item, current_depth + 1)
                structure['children'].append(child_structure)
                
                if child_structure.get('type') == 'file':
                    structure['file_count'] += 1
                    structure['size'] += child_structure.get('size', 0)
                elif child_structure.get('type') == 'directory':
                    structure['dir_count'] += 1
                    structure['file_count'] += child_structure.get('file_count', 0)
                    structure['size'] += child_structure.get('size', 0)
                    
        except (OSError, PermissionError) as e:
            logger.warning(f"Cannot access directory {path}: {e}")
            structure['error'] = str(e)
        
        return structure
    
    def _calculate_statistics(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate project statistics."""
        stats = {
            'total_files': 0,
            'total_directories': 0,
            'total_size': 0,
            'file_types': defaultdict(int),
            'largest_files': [],
            'deepest_path': 0,
            'directory_sizes': []
        }
        
        def collect_stats(node: Dict[str, Any], depth: int = 0):
            if node.get('excluded') or node.get('error'):
                return
                
            stats['deepest_path'] = max(stats['deepest_path'], depth)
            
            if node.get('type') == 'file':
                stats['total_files'] += 1
                stats['total_size'] += node.get('size', 0)
                
                extension = node.get('extension', 'no_extension')
                stats['file_types'][extension] += 1
                
                # Track largest files
                file_info = {
                    'path': node.get('path', ''),
                    'size': node.get('size', 0)
                }
                stats['largest_files'].append(file_info)
                
            elif node.get('type') == 'directory':
                stats['total_directories'] += 1
                
                dir_info = {
                    'path': node.get('path', ''),
                    'size': node.get('size', 0),
                    'file_count': node.get('file_count', 0)
                }
                stats['directory_sizes'].append(dir_info)
                
                for child in node.get('children', []):
                    collect_stats(child, depth + 1)
        
        collect_stats(structure)
        
        # Sort and limit largest files
        stats['largest_files'] = sorted(
            stats['largest_files'], 
            key=lambda x: x['size'], 
            reverse=True
        )[:10]
        
        # Sort directory sizes
        stats['directory_sizes'] = sorted(
            stats['directory_sizes'],
            key=lambda x: x['size'],
            reverse=True
        )[:10]
        
        return dict(stats)
    
    def _detect_patterns(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Detect common project patterns."""
        patterns = {
            'project_type': 'unknown',
            'framework': None,
            'language': None,
            'build_system': None,
            'has_tests': False,
            'has_docs': False,
            'package_structure': False
        }
        
        def find_patterns(node: Dict[str, Any]):
            if node.get('excluded') or node.get('error'):
                return
                
            name = node.get('name', '').lower()
            
            # Detect project type by files
            if name in ['package.json']:
                patterns['project_type'] = 'javascript'
                patterns['build_system'] = 'npm'
            elif name in ['pyproject.toml', 'setup.py']:
                patterns['project_type'] = 'python'
                patterns['build_system'] = 'pip'
            elif name in ['pom.xml']:
                patterns['project_type'] = 'java'
                patterns['build_system'] = 'maven'
            elif name in ['cargo.toml']:
                patterns['project_type'] = 'rust'
                patterns['build_system'] = 'cargo'
            
            # Detect test directories
            if 'test' in name or name == 'tests':
                patterns['has_tests'] = True
            
            # Detect documentation
            if name in ['docs', 'doc', 'documentation']:
                patterns['has_docs'] = True
            
            # Detect package structure
            if name in ['src', 'lib', 'source']:
                patterns['package_structure'] = True
            
            # Process children
            for child in node.get('children', []):
                find_patterns(child)
        
        find_patterns(structure)
        
        return patterns
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate structure recommendations."""
        recommendations = []
        stats = analysis['statistics']
        patterns = analysis['patterns']
        
        # Test recommendations
        if not patterns['has_tests']:
            recommendations.append("Consider adding a tests directory and unit tests")
        
        # Documentation recommendations
        if not patterns['has_docs']:
            recommendations.append("Consider adding documentation in a docs/ directory")
        
        # Structure recommendations
        if not patterns['package_structure'] and patterns['project_type'] in ['python', 'javascript']:
            recommendations.append("Consider organizing code in a src/ directory")
        
        # Size recommendations
        if stats['total_files'] > 1000:
            recommendations.append("Large project - consider modularization")
        
        # Depth recommendations
        if stats['deepest_path'] > 8:
            recommendations.append("Deep directory structure - consider flattening")
        
        return recommendations


def get_project_structure_analyzer(max_depth: int = 10, exclude_dirs: Optional[Set[str]] = None) -> ProjectStructureAnalyzer:
    """
    Get a configured project structure analyzer instance.
    
    Args:
        max_depth: Maximum directory depth to analyze
        exclude_dirs: Set of directory names to exclude
        
    Returns:
        ProjectStructureAnalyzer instance
    """
    return ProjectStructureAnalyzer(max_depth=max_depth, exclude_dirs=exclude_dirs)
