"""Tests for the contextual prompt generator."""
import unittest
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# We'll import the ContextualPromptGenerator in each test method
# to avoid circular import issues


@patch('src.generators.contextual_prompt_generator.PromptGenerator')
class TestContextualPromptGenerator(unittest.TestCase):
    """Test suite for the ContextualPromptGenerator class."""
    
    def setUp(self):
        """Set up the test case."""
        self.mock_project_path = "/test/path"
        self.mock_config = {
            "project_name": "Test Project",
            "output_dir": "/test/output",
            "model_type": "gpt-4"
        }
    
    @patch('src.generators.contextual_prompt_generator.DependencyGraph')
    def test_generate_architecture_prompt(self, mock_prompt_generator, mock_dependency_graph):
        """Test generating architecture prompt."""
        # Import here to avoid circular import issues
        from src.generators.contextual_prompt_generator import ContextualPromptGenerator
        
        # Setup mock
        mock_graph_instance = MagicMock()
        mock_graph_instance.generate_graph.return_value = {"nodes": [], "edges": []}
        mock_dependency_graph.return_value = mock_graph_instance
        
        # Create the generator instance
        generator = ContextualPromptGenerator(self.mock_project_path, self.mock_config)
        
        # Test method
        result = generator.generate_architecture_prompt()
        self.assertIn("architecture", result.lower())
        self.assertIn(self.mock_config["project_name"], result)
    
    @patch('src.generators.contextual_prompt_generator.FunctionalityDetector')
    def test_generate_functionality_prompt(self, mock_prompt_generator, mock_functionality_detector):
        """Test generating functionality prompt."""
        # Import here to avoid circular import issues
        from src.generators.contextual_prompt_generator import ContextualPromptGenerator
        
        # Setup mock
        mock_detector = MagicMock()
        mock_detector.detect_functionalities.return_value = [
            {"name": "Test Function", "files": ["test1.py"], "description": "Test description"}
        ]
        mock_functionality_detector.return_value = mock_detector
        
        # Create the generator instance
        generator = ContextualPromptGenerator(self.mock_project_path, self.mock_config)
        
        # Test method
        functionality_name = "Test Function"
        result = generator.generate_functionality_prompt(functionality_name)
        self.assertIn(functionality_name, result)
        self.assertIn("test1.py", result)
    
    def test_generate_completion_prompt(self, mock_prompt_generator):
        """Test generating code completion prompt."""
        # Import here to avoid circular import issues
        from src.generators.contextual_prompt_generator import ContextualPromptGenerator
        
        # Create the generator instance
        generator = ContextualPromptGenerator(self.mock_project_path, self.mock_config)
        
        # Setup test data
        file_path = "test_file.py"
        code_context = "def test_function():\n    # Implementation needed\n    pass"
        
        # Test method
        result = generator.generate_completion_prompt(file_path, code_context)
        self.assertIn(file_path, result)
        self.assertIn(code_context, result)
    
    def test_generate_clarification_questions(self, mock_prompt_generator):
        """Test generating clarification questions."""
        # Import here to avoid circular import issues
        from src.generators.contextual_prompt_generator import ContextualPromptGenerator
        
        # Create the generator instance
        generator = ContextualPromptGenerator(self.mock_project_path, self.mock_config)
        
        # Setup test data
        functionality_description = "A complex system that should do something"
        
        # Test method
        result = generator.generate_clarification_questions(functionality_description)
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        for question in result:
            self.assertIsInstance(question, str)
    
    def test_enhance_prompt_with_context(self, mock_prompt_generator):
        """Test enhancing prompt with context."""
        # Import here to avoid circular import issues
        from src.generators.contextual_prompt_generator import ContextualPromptGenerator
        
        # Create the generator instance
        generator = ContextualPromptGenerator(self.mock_project_path, self.mock_config)
        
        # Test method
        base_prompt = "Create a function"
        files_context = ["file1.py", "file2.py"]
        enhanced_prompt = generator.enhance_prompt_with_context(base_prompt, files_context)
        self.assertIn(base_prompt, enhanced_prompt)
        for file in files_context:
            self.assertIn(file, enhanced_prompt)


if __name__ == '__main__':
    unittest.main()
