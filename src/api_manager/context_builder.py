"""
Context Builder - FASE 1: Pre-procesamiento y Enriquecimiento
Analyzes project context and builds comprehensive implementation context for the API.
"""

import os
import ast
import json
from typing import Dict, List, Any, Set, Optional
from pathlib import Path
import re


class ContextBuilder:
    """
    Intelligent project context analyzer that builds comprehensive context
    for API-driven implementation suggestions.
    """
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.context_cache = {}
        
    def build_complete_context(self, target_files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Build complete project context for API processing.
        
        Args:
            target_files: Specific files to focus on (optional)
            
        Returns:
            Comprehensive context dictionary
        """
        context = {
            'project_metadata': self._extract_project_metadata(),
            'file_structure': self._analyze_file_structure(),
            'dependencies': self._analyze_dependencies(),
            'code_patterns': self._analyze_code_patterns(),
            'implementation_context': self._build_implementation_context(target_files),
            'integration_points': self._identify_integration_points(),
            'complexity_metrics': self._calculate_complexity_metrics()
        }
        
        return context
    
    def _extract_project_metadata(self) -> Dict[str, Any]:
        """Extract project metadata from various configuration files."""
        metadata = {
            'name': self.project_root.name,
            'type': 'unknown',
            'framework': None,
            'language': None,
            'version': None
        }
        
        # Check for Python project
        if (self.project_root / 'setup.py').exists() or (self.project_root / 'pyproject.toml').exists():
            metadata['language'] = 'python'
            metadata['type'] = 'python_package'
            
        # Check for Node.js project
        if (self.project_root / 'package.json').exists():
            metadata['language'] = 'javascript'
            metadata['type'] = 'node_project'
            try:
                with open(self.project_root / 'package.json', 'r') as f:
                    package_data = json.load(f)
                    metadata['name'] = package_data.get('name', metadata['name'])
                    metadata['version'] = package_data.get('version')
                    
                    # Detect framework
                    deps = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}
                    if 'react' in deps:
                        metadata['framework'] = 'react'
                    elif 'vue' in deps:
                        metadata['framework'] = 'vue'
                    elif 'angular' in deps:
                        metadata['framework'] = 'angular'
                    elif 'express' in deps:
                        metadata['framework'] = 'express'
            except (json.JSONDecodeError, FileNotFoundError):
                pass
                
        # Check for requirements.txt to confirm Python
        if (self.project_root / 'requirements.txt').exists():
            metadata['language'] = 'python'
            
        return metadata
    
    def _analyze_file_structure(self) -> Dict[str, Any]:
        """Analyze project file structure and organization patterns."""
        structure = {
            'total_files': 0,
            'directories': {},
            'file_types': {},
            'key_files': [],
            'organization_pattern': 'unknown'
        }
        
        key_files_patterns = [
            'main.py', '__init__.py', 'app.py', 'index.js', 'index.html',
            'README.md', 'setup.py', 'package.json', 'requirements.txt'
        ]
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'dist', 'build']]
            
            rel_root = os.path.relpath(root, self.project_root)
            if rel_root == '.':
                rel_root = 'root'
                
            structure['directories'][rel_root] = len(files)
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                structure['total_files'] += 1
                
                # Track file types
                ext = os.path.splitext(file)[1]
                structure['file_types'][ext] = structure['file_types'].get(ext, 0) + 1
                
                # Identify key files
                if file in key_files_patterns:
                    structure['key_files'].append(os.path.join(rel_root, file))
        
        # Determine organization pattern
        if 'src' in structure['directories']:
            structure['organization_pattern'] = 'src_based'
        elif any('app' in d for d in structure['directories']):
            structure['organization_pattern'] = 'app_based'
        elif structure['file_types'].get('.py', 0) > 5:
            structure['organization_pattern'] = 'python_module'
        
        return structure
    
    def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies and their relationships."""
        dependencies = {
            'external': {},
            'internal': {},
            'missing': [],
            'circular': []
        }
        
        # Python dependencies
        if (self.project_root / 'requirements.txt').exists():
            try:
                with open(self.project_root / 'requirements.txt', 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Parse dependency with version
                            match = re.match(r'^([a-zA-Z0-9_-]+)([>=<~!]+.*)?', line)
                            if match:
                                dep_name = match.group(1)
                                version_spec = match.group(2) or ''
                                dependencies['external'][dep_name] = version_spec
            except FileNotFoundError:
                pass
        
        # Analyze internal imports in Python files
        for py_file in self.project_root.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        self._extract_import_info(node, py_file, dependencies)
                        
            except (SyntaxError, UnicodeDecodeError, FileNotFoundError):
                continue
        
        return dependencies
    
    def _extract_import_info(self, node: ast.AST, file_path: Path, dependencies: Dict):
        """Extract import information from AST node."""
        rel_path = str(file_path.relative_to(self.project_root))
        
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name.split('.')[0]
                if not self._is_stdlib_module(module_name):
                    if module_name not in dependencies['internal']:
                        dependencies['internal'][module_name] = []
                    dependencies['internal'][module_name].append(rel_path)
                    
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module_name = node.module.split('.')[0]
                if node.level == 0 and not self._is_stdlib_module(module_name):
                    if module_name not in dependencies['internal']:
                        dependencies['internal'][module_name] = []
                    dependencies['internal'][module_name].append(rel_path)
    
    def _is_stdlib_module(self, module_name: str) -> bool:
        """Check if module is part of Python standard library."""
        stdlib_modules = {
            'os', 'sys', 'json', 'datetime', 'time', 'random', 'math', 
            'collections', 'itertools', 'functools', 're', 'pathlib',
            'typing', 'dataclasses', 'enum', 'abc', 'ast', 'inspect'
        }
        return module_name in stdlib_modules
    
    def _analyze_code_patterns(self) -> Dict[str, Any]:
        """Analyze code patterns and architectural decisions."""
        patterns = {
            'design_patterns': [],
            'architectural_style': 'unknown',
            'code_quality': {},
            'common_patterns': {}
        }
        
        # Analyze Python files for patterns
        class_count = 0
        function_count = 0
        total_lines = 0
        
        for py_file in self.project_root.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    total_lines += len(content.splitlines())
                    
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_count += 1
                        # Check for common patterns
                        if any(base.id in ['ABC', 'Protocol'] for base in node.bases if isinstance(base, ast.Name)):
                            if 'Abstract Base Class' not in patterns['design_patterns']:
                                patterns['design_patterns'].append('Abstract Base Class')
                                
                    elif isinstance(node, ast.FunctionDef):
                        function_count += 1
                        
            except (SyntaxError, UnicodeDecodeError, FileNotFoundError):
                continue
        
        patterns['code_quality'] = {
            'total_lines': total_lines,
            'class_count': class_count,
            'function_count': function_count,
            'avg_lines_per_file': total_lines / max(len(list(self.project_root.rglob('*.py'))), 1)
        }
        
        return patterns
    
    def _build_implementation_context(self, target_files: Optional[List[str]] = None) -> Dict[str, Any]:
        """Build specific implementation context for targeted changes."""
        context = {
            'target_files': target_files or [],
            'related_files': [],
            'modification_scope': 'unknown',
            'impact_analysis': {}
        }
        
        if target_files:
            for file_path in target_files:
                if os.path.exists(os.path.join(self.project_root, file_path)):
                    # Analyze file content and find related files
                    related = self._find_related_files(file_path)
                    context['related_files'].extend(related)
        
        return context
    
    def _find_related_files(self, file_path: str) -> List[str]:
        """Find files related to the target file through imports or references."""
        related = []
        full_path = self.project_root / file_path
        
        if not full_path.exists() or not full_path.suffix == '.py':
            return related
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if node.level > 0:  # Relative import
                        # Convert relative import to file path
                        base_dir = full_path.parent
                        for _ in range(node.level - 1):
                            base_dir = base_dir.parent
                        
                        module_parts = node.module.split('.') if node.module else []
                        potential_file = base_dir / '/'.join(module_parts)
                        
                        for suffix in ['.py', '/__init__.py']:
                            candidate = str(potential_file) + suffix
                            if os.path.exists(candidate):
                                rel_path = os.path.relpath(candidate, self.project_root)
                                if rel_path not in related:
                                    related.append(rel_path)
                                
        except (SyntaxError, UnicodeDecodeError, FileNotFoundError):
            pass
            
        return related
    
    def _identify_integration_points(self) -> Dict[str, Any]:
        """Identify key integration points in the project."""
        integration_points = {
            'entry_points': [],
            'api_endpoints': [],
            'cli_commands': [],
            'configuration_files': [],
            'extension_points': []
        }
        
        # Find entry points
        for pattern in ['main.py', 'app.py', '__main__.py']:
            matches = list(self.project_root.rglob(pattern))
            integration_points['entry_points'].extend([str(p.relative_to(self.project_root)) for p in matches])
        
        # Find CLI commands (Click framework)
        for py_file in self.project_root.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if '@click.command' in content or '@cli.command' in content:
                    rel_path = str(py_file.relative_to(self.project_root))
                    integration_points['cli_commands'].append(rel_path)
                    
            except (UnicodeDecodeError, FileNotFoundError):
                continue
        
        # Find configuration files
        config_patterns = ['*.json', '*.yaml', '*.yml', '*.toml', '*.ini', '*.cfg']
        for pattern in config_patterns:
            matches = list(self.project_root.rglob(pattern))
            config_files = [str(p.relative_to(self.project_root)) for p in matches 
                          if not any(ignore in str(p) for ignore in ['node_modules', '.git', '__pycache__'])]
            integration_points['configuration_files'].extend(config_files)
        
        return integration_points
    
    def _calculate_complexity_metrics(self) -> Dict[str, Any]:
        """Calculate project complexity metrics."""
        metrics = {
            'cyclomatic_complexity': 0,
            'maintainability_index': 0,
            'code_duplication': 0,
            'technical_debt': 'low'
        }
        
        total_complexity = 0
        file_count = 0
        
        for py_file in self.project_root.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                tree = ast.parse(content)
                file_complexity = self._calculate_file_complexity(tree)
                total_complexity += file_complexity
                file_count += 1
                
            except (SyntaxError, UnicodeDecodeError, FileNotFoundError):
                continue
        
        if file_count > 0:
            metrics['cyclomatic_complexity'] = total_complexity / file_count
            
            # Simple maintainability heuristic
            if metrics['cyclomatic_complexity'] < 5:
                metrics['maintainability_index'] = 85
                metrics['technical_debt'] = 'low'
            elif metrics['cyclomatic_complexity'] < 10:
                metrics['maintainability_index'] = 65
                metrics['technical_debt'] = 'medium'
            else:
                metrics['maintainability_index'] = 45
                metrics['technical_debt'] = 'high'
        
        return metrics
    
    def _calculate_file_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity for a single file."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, (ast.Lambda, ast.ListComp, ast.DictComp, ast.SetComp)):
                complexity += 1
                
        return complexity
    
    def get_context_summary(self, context: Dict[str, Any]) -> str:
        """Generate a human-readable summary of the project context."""
        metadata = context['project_metadata']
        structure = context['file_structure']
        deps = context['dependencies']
        
        summary = f"""
Project Context Summary:
========================
Name: {metadata['name']}
Type: {metadata['type']} ({metadata['language']})
Framework: {metadata.get('framework', 'None')}

File Structure:
- Total files: {structure['total_files']}
- Organization: {structure['organization_pattern']}
- Main directories: {', '.join(list(structure['directories'].keys())[:5])}

Dependencies:
- External: {len(deps['external'])} packages
- Internal modules: {len(deps['internal'])}

Complexity:
- Maintainability Index: {context['complexity_metrics']['maintainability_index']}/100
- Technical Debt: {context['complexity_metrics']['technical_debt']}
"""
        return summary.strip()
