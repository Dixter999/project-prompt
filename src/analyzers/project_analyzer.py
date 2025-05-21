"""Project analysis functionality.

This module provides tools for analyzing Python projects, including:
- Project structure analysis
- Code analysis
- Dependency analysis
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Union

from src.analyzers.project_structure_analyzer import ProjectStructureAnalyzer


class ProjectAnalyzer:
    """Analyzes Python projects to extract structure and metadata."""
    
    def __init__(self, project_root: Union[str, Path]):
        """Initialize the project analyzer.
        
        Args:
            project_root: Path to the root directory of the project.
        """
        self.project_root = Path(project_root).resolve()
        self.structure_analyzer = ProjectStructureAnalyzer(self.project_root)
    
    def analyze(self) -> Dict[str, Any]:
        """Perform a complete analysis of the project.
        
        Returns:
            A dictionary containing the analysis results.
        """
        return {
            "structure": self.analyze_structure(),
            "modules": self.analyze_python_modules(),
            "dependencies": self.analyze_dependencies()
        }
    
    def analyze_structure(self) -> Dict[str, Any]:
        """Analyze the project structure.
        
        Returns:
            A dictionary containing the project structure.
        """
        return self.structure_analyzer.get_project_structure()
    
    def analyze_python_modules(self) -> Dict[str, Any]:
        """Analyze all Python modules in the project.
        
        Returns:
            A dictionary mapping module names to their analysis results.
        """
        modules = {}
        for py_file in self._find_python_files():
            try:
                module_name = self._get_module_name(py_file)
                if module_name:
                    modules[module_name] = self.analyze_python_file(py_file)
            except Exception as e:
                print(f"Error analyzing {py_file}: {e}")
        return modules
    
    def analyze_python_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Analyze a single Python file.
        
        Args:
            file_path: Path to the Python file to analyze.
            
        Returns:
            A dictionary containing the analysis results.
        """
        file_path = Path(file_path)
        try:
            source = file_path.read_text(encoding='utf-8')
            tree = ast.parse(source, filename=str(file_path))
            
            analyzer = _ASTAnalyzer()
            analyzer.visit(tree)
            
            return {
                "file_path": str(file_path.relative_to(self.project_root)),
                "module_name": self._get_module_name(file_path) or "",
                "functions": analyzer.functions,
                "classes": analyzer.classes,
                "imports": list(analyzer.imports),
            }
        except Exception as e:
            return {
                "file_path": str(file_path.relative_to(self.project_root)),
                "error": str(e)
            }
    
    def analyze_dependencies(self) -> Dict[str, List[str]]:
        """Analyze dependencies between Python modules.
        
        Returns:
            A dictionary mapping module names to their dependencies.
        """
        dependencies = {}
        for py_file in self._find_python_files():
            try:
                module_name = self._get_module_name(py_file)
                if not module_name:
                    continue
                    
                source = py_file.read_text(encoding='utf-8')
                tree = ast.parse(source, filename=str(py_file))
                
                analyzer = _ASTAnalyzer()
                analyzer.visit(tree)
                
                dependencies[module_name] = list(analyzer.imports)
            except Exception as e:
                print(f"Error analyzing dependencies in {py_file}: {e}")
        
        return dependencies
    
    def _find_python_files(self) -> List[Path]:
        """Find all Python files in the project.
        
        Returns:
            A list of Path objects for Python files.
        """
        return [
            self.project_root / path
            for path in self.structure_analyzer.find_files_by_extension('.py')
        ]
    
    def _get_module_name(self, file_path: Union[str, Path]) -> Optional[str]:
        """Get the full module name for a Python file.
        
        Args:
            file_path: Path to the Python file.
            
        Returns:
            The full module name, or None if the file is not in a Python package.
        """
        file_path = Path(file_path).resolve()
        if not file_path.is_relative_to(self.project_root):
            return None
            
        rel_path = file_path.relative_to(self.project_root)
        
        # Check if the file is in a Python package
        parts = list(rel_path.parts)
        if not parts:
            return None
            
        # Remove .py extension
        if parts[-1].endswith('.py'):
            parts[-1] = parts[-1][:-3]
        
        return '.'.join(parts)


class _ASTAnalyzer(ast.NodeVisitor):
    """AST visitor for analyzing Python source code."""
    
    def __init__(self):
        self.functions = []
        self.classes = []
        self.imports = set()
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit a function definition."""
        self.functions.append({
            'name': node.name,
            'lineno': node.lineno,
            'docstring': ast.get_docstring(node) or '',
            'args': [arg.arg for arg in node.args.args],
            'returns': ast.unparse(node.returns) if hasattr(node, 'returns') and node.returns else None,
        })
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit a class definition."""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append({
                    'name': item.name,
                    'lineno': item.lineno,
                    'docstring': ast.get_docstring(item) or '',
                })
        
        self.classes.append({
            'name': node.name,
            'lineno': node.lineno,
            'docstring': ast.get_docstring(node) or '',
            'bases': [ast.unparse(base) for base in node.bases],
            'methods': methods,
        })
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import) -> None:
        """Visit an import statement."""
        for name in node.names:
            self.imports.add(name.name.split('.')[0])
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit a from-import statement."""
        if node.module:
            self.imports.add(node.module.split('.')[0])
        self.generic_visit(node)
