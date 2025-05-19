#!/usr/bin/env python3
"""
Unit test to validate the new directory structure organization.

This test ensures that all required directories exist and key files are found
in the expected locations after project reorganization.
"""

import os
import unittest
from pathlib import Path


class TestDirectoryStructure(unittest.TestCase):
    """Test suite for validating the project directory structure."""

    def setUp(self):
        """Set up test variables."""
        self.project_root = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
    def test_top_level_directories(self):
        """Test that all required top-level directories exist."""
        required_dirs = [
            'src',
            'tests',
            'docs',
            'scripts',
            'project-output',
            'examples'
        ]
        
        for directory in required_dirs:
            dir_path = self.project_root / directory
            self.assertTrue(dir_path.exists(), f"Directory {directory} does not exist")
            self.assertTrue(dir_path.is_dir(), f"{directory} is not a directory")
    
    def test_src_subdirectories(self):
        """Test that all required src subdirectories exist."""
        required_dirs = [
            'src/core',
            'src/utils',
            'src/api',
            'src/templates',
            'src/analyzers',
            'src/ui'
        ]
        
        for directory in required_dirs:
            dir_path = self.project_root / directory
            self.assertTrue(dir_path.exists(), f"Directory {directory} does not exist")
            self.assertTrue(dir_path.is_dir(), f"{directory} is not a directory")
    
    def test_tests_subdirectories(self):
        """Test that all required tests subdirectories exist."""
        required_dirs = [
            'tests/unit',
            'tests/integration',
            'tests/verification'
        ]
        
        for directory in required_dirs:
            dir_path = self.project_root / directory
            self.assertTrue(dir_path.exists(), f"Directory {directory} does not exist")
            self.assertTrue(dir_path.is_dir(), f"{directory} is not a directory")
    
    def test_project_output_directories(self):
        """Test that project-output directories exist."""
        required_dirs = [
            'project-output/analyses',
            'project-output/suggestions'
        ]
        
        for directory in required_dirs:
            dir_path = self.project_root / directory
            self.assertTrue(dir_path.exists(), f"Directory {directory} does not exist")
            self.assertTrue(dir_path.is_dir(), f"{directory} is not a directory")
    
    def test_key_files_exist(self):
        """Test that key files exist in their expected locations."""
        key_files = [
            'src/main.py',
            'src/core/project_prompt.py',
            'src/core/analyze_with_anthropic_direct.py',
            'scripts/project-prompt.sh',
            'tests/run_anthropic_verification.sh',
            'project-output/README.md'
        ]
        
        for file_path in key_files:
            path = self.project_root / file_path
            self.assertTrue(path.exists(), f"File {file_path} does not exist")
            self.assertTrue(path.is_file(), f"{file_path} is not a file")
    
    def test_templates_moved(self):
        """Test that templates were moved from test-projects to src/templates."""
        # Check that templates exist in new location
        templates_dir = self.project_root / 'src' / 'templates'
        self.assertTrue(templates_dir.exists(), "Templates directory doesn't exist")
        
        # Make sure it has content
        templates = list(templates_dir.glob('*'))
        self.assertGreater(len(templates), 0, "Templates directory is empty")
        
        # Check that the old location doesn't exist
        old_templates_dir = self.project_root / 'test-projects' / 'templates'
        self.assertFalse(old_templates_dir.exists(), 
                         "Old templates directory still exists and wasn't properly moved")


if __name__ == '__main__':
    unittest.main(verbosity=2)
