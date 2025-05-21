"""Tests for the project_analyzer module."""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

# Import the class we're testing
from src.analyzers.project_analyzer import ProjectAnalyzer


class TestProjectAnalyzer:
    """Test cases for ProjectAnalyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.project_root = Path(self.test_dir) / "test_project"
        self.project_root.mkdir()
        
        # Create a sample project structure
        (self.project_root / "src").mkdir()
        (self.project_root / "tests").mkdir()
        
        # Create sample Python files
        (self.project_root / "src" / "__init__.py").touch()
        (self.project_root / "src" / "main.py").write_text(
            'import os\n\n'  # stdlib import
            'import requests  # external import\n\n'  # external import
            'def hello(name: str) -> str:\n'  # function definition
            '    """Say hello to someone."""\n'
            '    return f"Hello, {name}!"\n\n'  # function body
            'class Greeter:\n'  # class definition
            '    """A simple greeter class."""\n\n'
            '    def __init__(self, name: str):\n'  # method definition
            '        self.name = name\n\n'
            '    def greet(self) -> str:\n'  # method definition
            '        """Return a greeting."""\n'
            '        return f"Hello, {self.name}!"\n'  # method body
        )
        
        # Create a test file that imports from main
        (self.project_root / "tests" / "test_main.py").write_text(
            'from src.main import hello, Greeter\n\n'  # local import
            'def test_hello():\n'
            '    assert hello("world") == "Hello, world!"\n\n'
            'def test_greeter():\n'
            '    greeter = Greeter("world")\n'
            '    assert greeter.greet() == "Hello, world!"\n'
        )
        
        # Initialize the analyzer
        self.analyzer = ProjectAnalyzer(self.project_root)
    
    def teardown_method(self):
        """Clean up after each test."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test that the analyzer initializes correctly."""
        assert self.analyzer.project_root == self.project_root
        assert hasattr(self.analyzer, 'structure_analyzer')
    
    def test_analyze_structure(self):
        """Test project structure analysis."""
        structure = self.analyzer.analyze_structure()
        
        # The structure should be a dictionary with directory names as keys
        assert isinstance(structure, dict)
        
        # Check that our test directories are in the structure
        assert 'src' in structure
        assert 'tests' in structure
        
        # The structure values should be dictionaries for directories or lists for files
        assert isinstance(structure['src'], dict)
        assert isinstance(structure['tests'], dict)
        
        # Check for the presence of our test files
        # The structure is nested with '_files' keys containing lists of files
        src_files = structure['src'].get('_files', [])
        test_files = structure['tests'].get('_files', [])
        
        # Convert to sets for easier checking
        src_file_names = {f[0] if isinstance(f, tuple) else f for f in src_files}
        test_file_names = {f[0] if isinstance(f, tuple) else f for f in test_files}
        
        # Check that our test files are in the structure
        assert 'main.py' in src_file_names
        assert 'test_main.py' in test_file_names
    
    def test_analyze_python_modules(self):
        """Test Python module analysis."""
        modules = self.analyzer.analyze_python_modules()
        
        # Check that both modules were found
        assert 'src.main' in modules
        assert 'tests.test_main' in modules
        
        # Check main module contents
        main_module = modules['src.main']
        assert 'functions' in main_module
        assert 'classes' in main_module
        assert 'imports' in main_module
        
        # Check function detection
        functions = {f['name']: f for f in main_module['functions']}
        assert 'hello' in functions
        assert functions['hello']['docstring'] == 'Say hello to someone.'
        assert functions['hello']['args'] == ['name']
        assert functions['hello']['returns'] == 'str'
        
        # Check class detection
        classes = {c['name']: c for c in main_module['classes']}
        assert 'Greeter' in classes
        assert classes['Greeter']['docstring'] == 'A simple greeter class.'
        assert len(classes['Greeter']['methods']) == 2  # __init__ and greet
    
    def test_analyze_dependencies(self):
        """Test dependency analysis."""
        # First, analyze the project to get the module structure
        analysis = self.analyzer.analyze()
        
        # Get the dependencies from the analysis
        dependencies = analysis.get('dependencies', {})
        
        # Check that dependencies were found
        assert isinstance(dependencies, dict), "Dependencies should be a dictionary"
        
        # Check that we have some modules with dependencies
        assert len(dependencies) > 0, "No module dependencies found"
        
        # Find our test modules
        main_module = next((k for k in dependencies.keys() if 'src.main' in k), None)
        test_module = next((k for k in dependencies.keys() if 'tests.test_main' in k), None)
        
        # Check that we found our test modules
        assert main_module is not None, "src.main module not found in dependencies"
        assert test_module is not None, "tests.test_main module not found in dependencies"
        
        # Check dependencies for src.main
        main_deps = dependencies[main_module]
        assert isinstance(main_deps, list), f"Dependencies for {main_module} should be a list"
        
        # Check for standard library imports (should be in the first part of the import)
        assert any('os' in dep for dep in main_deps), f"os import not found in {main_module}"
        
        # Check for external package imports
        assert any('requests' in dep for dep in main_deps), f"requests import not found in {main_module}"
        
        # Check dependencies for tests.test_main
        test_deps = dependencies[test_module]
        assert isinstance(test_deps, list), f"Dependencies for {test_module} should be a list"
        
        # Check for local imports (should be in the first part of the import)
        assert any('src' in dep for dep in test_deps), f"src import not found in {test_module}"
    
    def test_analyze_complete(self):
        """Test complete project analysis."""
        analysis = self.analyzer.analyze()
        
        # Check that all analysis components are present
        assert 'structure' in analysis
        assert 'modules' in analysis
        assert 'dependencies' in analysis
        
        # Check that modules were analyzed
        assert 'src.main' in analysis['modules']
        assert 'tests.test_main' in analysis['modules']
        
        # Check that dependencies were analyzed
        assert 'src.main' in analysis['dependencies']
        assert 'tests.test_main' in analysis['dependencies']
    
    def test_analyze_invalid_python_file(self):
        """Test analysis of an invalid Python file."""
        # Create an invalid Python file
        invalid_file = self.project_root / "invalid.py"
        invalid_file.write_text('def invalid_syntax(')  # Missing closing parenthesis
        
        # This should not raise an exception
        modules = self.analyzer.analyze_python_modules()
        
        # The invalid file should not be in the modules
        assert 'invalid' not in modules
    
    def test_get_module_name(self):
        """Test module name extraction."""
        # Test with a file in a package
        main_py = self.project_root / "src" / "main.py"
        assert self.analyzer._get_module_name(main_py) == "src.main"
        
        # Test with a file in a subpackage
        sub_pkg = self.project_root / "src" / "subpkg"
        sub_pkg.mkdir()
        (sub_pkg / "__init__.py").touch()
        sub_file = sub_pkg / "module.py"
        sub_file.touch()
        assert self.analyzer._get_module_name(sub_file) == "src.subpkg.module"
        
        # Test with a file not in a package
        other_file = self.project_root / "script.py"
        other_file.touch()
        assert self.analyzer._get_module_name(other_file) == "script"
        
        # Test with a file not in the project root
        outside_file = Path("/tmp/outside.py")
        assert self.analyzer._get_module_name(outside_file) is None
