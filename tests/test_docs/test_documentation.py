
import os
import tempfile
import unittest
from pathlib import Path

from src.utils.markdown_manager import get_markdown_manager
from src.utils.documentation_system import get_documentation_system


class TestDocumentationSystem(unittest.TestCase):
    """Test case for the documentation system."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        self.markdown_manager = get_markdown_manager()
        self.doc_system = get_documentation_system()
        
        # Create test template
        self.templates_dir = self.test_dir / "templates"
        self.templates_dir.mkdir()
        test_template = self.templates_dir / "test_template.md"
        with open(test_template, "w") as f:
            f.write("# {{ title }}

{{ content }}")

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_create_document(self):
        """Test creating a document from a template."""
        # Create a document
        template_path = str(self.templates_dir / "test_template.md")
        output_path = str(self.test_dir / "test_doc.md")
        context = {"title": "Test Document", "content": "This is a test."}
        
        # Call the function being tested
        path = self.markdown_manager._resolve_template_path = lambda x: template_path
        result = self.markdown_manager.create_document(
            template_path, output_path, context
        )
        
        # Verify the result
        self.assertEqual(result, output_path)
        self.assertTrue(os.path.exists(output_path))
        
        # Check content
        with open(output_path, "r") as f:
            content = f.read()
        self.assertIn("# Test Document", content)
        self.assertIn("This is a test.", content)


if __name__ == "__main__":
    unittest.main()

