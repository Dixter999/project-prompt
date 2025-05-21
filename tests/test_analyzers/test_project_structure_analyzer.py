"""Tests for the project_structure_analyzer module."""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

# Import the class we're testing
from src.analyzers.project_structure_analyzer import ProjectStructureAnalyzer


class TestProjectStructureAnalyzer:
    """Test cases for ProjectStructureAnalyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.project_root = Path(self.test_dir) / "test_project"
        self.project_root.mkdir()
        
        # Create a sample project structure
        (self.project_root / "src").mkdir()
        (self.project_root / "tests").mkdir()
        (self.project_root / "docs").mkdir()
        
        # Create some files
        (self.project_root / "README.md").write_text("# Test Project\n")
        (self.project_root / "src" / "__init__.py").touch()
        (self.project_root / "src" / "main.py").write_text("def main():\n    pass\n")
        (self.project_root / "tests" / "__init__.py").touch()
        (self.project_root / "tests" / "test_main.py").write_text("def test_main():\n    pass\n")
        
        # Create some ignored files/directories
        (self.project_root / "__pycache__").mkdir()
        (self.project_root / "venv").mkdir()
        (self.project_root / ".git").mkdir()
        (self.project_root / "temp.pyc").touch()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test that the analyzer initializes correctly."""
        analyzer = ProjectStructureAnalyzer(self.project_root)
        assert analyzer.root_path == self.project_root.resolve()
        
        # Test with string path
        analyzer = ProjectStructureAnalyzer(str(self.project_root))
        assert analyzer.root_path == self.project_root.resolve()
        
        # Test with non-existent directory
        with pytest.raises(NotADirectoryError):
            ProjectStructureAnalyzer(self.project_root / "nonexistent")
    
    def test_get_project_structure(self):
        """Test getting the project structure."""
        analyzer = ProjectStructureAnalyzer(self.project_root)
        structure = analyzer.get_project_structure()
        
        # Check top-level directories
        assert 'src' in structure
        assert 'tests' in structure
        assert 'docs' in structure
        
        # Check files in src
        assert '_files' in structure['src']
        assert '__init__.py' in structure['src']['_files']
        assert 'main.py' in structure['src']['_files']
        
        # Check that ignored files/directories are not included
        assert '__pycache__' not in structure
        assert 'venv' not in structure
        assert '.git' not in structure
    
    def test_find_files_by_extension(self):
        """Test finding files by extension."""
        analyzer = ProjectStructureAnalyzer(self.project_root)
        
        # Find Python files
        py_files = [str(f).replace('\\', '/') for f in analyzer.find_files_by_extension('.py')]
        # Should find: src/__init__.py, src/main.py, tests/__init__.py, tests/test_main.py
        assert len(py_files) == 4
        assert any('src/__init__.py' in f for f in py_files)
        assert any('src/main.py' in f for f in py_files)
        assert any('tests/__init__.py' in f for f in py_files)
        assert any('tests/test_main.py' in f for f in py_files)
        
        # Find markdown files
        md_files = analyzer.find_files_by_extension('md')
        assert len(md_files) == 1
        assert 'README.md' in str(md_files[0])
        
        # Non-existent extension
        assert not analyzer.find_files_by_extension('.xyz')
    
    def test_get_file_contents(self):
        """Test getting file contents."""
        analyzer = ProjectStructureAnalyzer(self.project_root)
        
        # Test reading a text file
        content = analyzer.get_file_contents('README.md')
        assert content.startswith('# Test Project')
        
        # Test reading a Python file
        content = analyzer.get_file_contents('src/main.py')
        assert 'def main():' in content
        
        # Test non-existent file
        with pytest.raises(FileNotFoundError):
            analyzer.get_file_contents('nonexistent.txt')
    
    def test_get_file_metadata(self):
        """Test getting file metadata."""
        analyzer = ProjectStructureAnalyzer(self.project_root)
        
        # Test with a file
        metadata = analyzer.get_file_metadata('README.md')
        assert metadata['name'] == 'README.md'
        assert metadata['extension'] == '.md'
        assert metadata['is_file'] is True
        assert metadata['is_dir'] is False
        assert metadata['size'] > 0
        
        # Test with a directory
        metadata = analyzer.get_file_metadata('src')
        assert metadata['name'] == 'src'
        assert metadata['is_dir'] is True
        assert metadata['is_file'] is False
        
        # Test non-existent file
        with pytest.raises(FileNotFoundError):
            analyzer.get_file_metadata('nonexistent.txt')
