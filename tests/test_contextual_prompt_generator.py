import unittest
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.generators.contextual_prompt_generator import ContextualPromptGenerator
from src.analyzers.dependency_graph import DependencyGraph
from src.analyzers.functionality_detector import FunctionalityDetector


class TestContextualPromptGenerator(unittest.TestCase):
    
    def setUp(self):
        self.mock_project_path = "/test/path"
        self.mock_config = {
            "project_name": "Test Project",
            "output_dir": "/test/output",
            "model_type": "gpt-4"
        }
        self.generator = ContextualPromptGenerator(self.mock_project_path, self.mock_config)
    
    @patch('src.generators.contextual_prompt_generator.DependencyGraph')
    def test_generate_architecture_prompt(self, mock_dependency_graph):
        # Setup mock
        mock_graph_instance = MagicMock()
        mock_graph_instance.generate_graph.return_value = {"nodes": [], "edges": []}
        mock_dependency_graph.return_value = mock_graph_instance
        
        # Test method
        result = self.generator.generate_architecture_prompt()
        self.assertIn("architecture", result.lower())
        self.assertIn(self.mock_config["project_name"], result)
    
    @patch('src.generators.contextual_prompt_generator.FunctionalityDetector')
    def test_generate_functionality_prompt(self, mock_functionality_detector):
        # Setup mock
        mock_detector = MagicMock()
        mock_detector.detect_functionalities.return_value = [
            {"name": "Test Function", "files": ["test1.py"], "description": "Test description"}
        ]
        mock_functionality_detector.return_value = mock_detector
        
        # Test method
        functionality_name = "Test Function"
        result = self.generator.generate_functionality_prompt(functionality_name)
        self.assertIn(functionality_name, result)
        self.assertIn("test1.py", result)
    
    def test_generate_completion_prompt(self):
        # Setup test data
        file_path = "test_file.py"
        code_context = "def test_function():\n    # Implementation needed\n    pass"
        
        # Test method
        result = self.generator.generate_completion_prompt(file_path, code_context)
        self.assertIn(file_path, result)
        self.assertIn(code_context, result)
    
    def test_generate_clarification_questions(self):
        # Setup test data
        functionality_description = "A complex system that should do something"
        
        # Test method
        result = self.generator.generate_clarification_questions(functionality_description)
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        for question in result:
            self.assertIsInstance(question, str)
    
    def test_enhance_prompt_with_context(self):
        # Test method
        base_prompt = "Create a function"
        files_context = ["file1.py", "file2.py"]
        enhanced_prompt = self.generator.enhance_prompt_with_context(base_prompt, files_context)
        self.assertIn(base_prompt, enhanced_prompt)
        for file in files_context:
            self.assertIn(file, enhanced_prompt)


if __name__ == '__main__':
    unittest.main()
