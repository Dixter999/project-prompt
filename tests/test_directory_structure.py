#!/usr/bin/env python3
"""
Directory Structure Validation Test

This script validates that the project directory structure is correctly organized
according to the project's organization standards.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


class TestDirectoryStructure(unittest.TestCase):
    """Test case for validating the project directory structure."""

    def setUp(self):
        """Set up the test case."""
        self.root_dir = project_root
        
    def test_main_directories_exist(self):
        """Test that all required main directories exist."""
        required_dirs = [
            "src", "tests", "docs", "examples", "scripts"
        ]
        
        for dir_name in required_dirs:
            dir_path = self.root_dir / dir_name
            self.assertTrue(dir_path.exists(), f"Directory '{dir_name}' does not exist")
            self.assertTrue(dir_path.is_dir(), f"'{dir_name}' exists but is not a directory")
    
    def test_src_structure(self):
        """Test that the src directory has the correct structure."""
        src_dir = self.root_dir / "src"
        required_src_dirs = [
            "core", "analyzers", "generators", "integrations", 
            "templates", "utils", "ui", "api"
        ]
        
        for dir_name in required_src_dirs:
            dir_path = src_dir / dir_name
            self.assertTrue(dir_path.exists(), f"src/{dir_name} directory does not exist")
            self.assertTrue(dir_path.is_dir(), f"src/{dir_name} exists but is not a directory")
    
    def test_docs_structure(self):
        """Test that the docs directory has the correct structure."""
        docs_dir = self.root_dir / "docs"
        required_docs_dirs = [
            "guides", "reference", "development", "archive"
        ]
        
        for dir_name in required_docs_dirs:
            dir_path = docs_dir / dir_name
            self.assertTrue(dir_path.exists(), f"docs/{dir_name} directory does not exist")
            self.assertTrue(dir_path.is_dir(), f"docs/{dir_name} exists but is not a directory")
    
    def test_tests_structure(self):
        """Test that the tests directory has the correct structure."""
        tests_dir = self.root_dir / "tests"
        required_tests_dirs = [
            "unit", "integration", "e2e", "anthropic", "verification"
        ]
        
        for dir_name in required_tests_dirs:
            dir_path = tests_dir / dir_name
            self.assertTrue(dir_path.exists(), f"tests/{dir_name} directory does not exist")
            self.assertTrue(dir_path.is_dir(), f"tests/{dir_name} exists but is not a directory")
    
    def test_no_test_projects_in_root(self):
        """Test that there's no test-projects directory in the root."""
        test_projects_path = self.root_dir / "test-projects"
        self.assertFalse(test_projects_path.exists(), 
                         "test-projects directory should not exist in the root")
    
    def test_examples_structure(self):
        """Test that the examples directory has the correct structure."""
        examples_dir = self.root_dir / "examples"
        self.assertTrue((examples_dir / "test-projects").exists(), 
                        "examples/test-projects directory does not exist")
    
    def test_env_files(self):
        """Test that there's only one .env.example file in the root."""
        env_template = self.root_dir / ".env.template"
        self.assertFalse(env_template.exists(), 
                         ".env.template should not exist, use .env.example instead")
        
        env_example = self.root_dir / ".env.example"
        self.assertTrue(env_example.exists(), ".env.example should exist")


if __name__ == "__main__":
    unittest.main()
