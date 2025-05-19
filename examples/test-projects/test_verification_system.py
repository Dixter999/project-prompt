#!/usr/bin/env python3
"""
Unit Tests for Anthropic Verification System

This script performs comprehensive unit tests for the Anthropic markdown generation
verification system, including actual API calls to test real functionality.
"""

import unittest
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
import logging

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
from enhanced_verify_anthropic import analyze_markdown_quality, check_environment
from create_test_project import create_test_project, PROJECT_TYPES

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestEnvironmentSetup(unittest.TestCase):
    """Test class to verify the environment setup"""
    
    def test_api_key_exists(self):
        """Test if Anthropic API key exists and is correctly loaded"""
        # Check if API key is in environment
        api_key = os.environ.get("anthropic_API")
        
        # If not in environment, try to read from .env file
        if not api_key:
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('anthropic_API'):
                            api_key = line.split('=')[1].strip().strip('"\'')
                            break
        
        self.assertIsNotNone(api_key, "Anthropic API key not found in environment or .env file")
    
    def test_analyzer_script_exists(self):
        """Test if the analyzer script exists"""
        analyzer_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analyze_with_anthropic_direct.py")
        self.assertTrue(os.path.exists(analyzer_path), f"Analyzer script not found: {analyzer_path}")


class TestProjectTemplates(unittest.TestCase):
    """Test class to verify project templates"""
    
    def test_template_directories_exist(self):
        """Test if all template directories exist"""
        templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
        
        for project_type in PROJECT_TYPES:
            if project_type == "mixed":
                continue  # Skip mixed as it's a combination of others
            
            template_path = os.path.join(templates_dir, project_type)
            self.assertTrue(os.path.exists(template_path), f"Template directory not found: {template_path}")
    
    def test_create_project(self):
        """Test if a project can be created from template"""
        # Create a temporary test project
        project_type = "web-project"  # Use web project as it's simpler
        project_name = "test_project_creation"
        
        try:
            project_path = create_test_project(project_type, project_name)
            self.assertIsNotNone(project_path, "Project creation failed")
            self.assertTrue(os.path.exists(project_path), f"Project directory not found: {project_path}")
            
            # Check README.md exists and was customized
            readme_path = os.path.join(project_path, "README.md")
            self.assertTrue(os.path.exists(readme_path), f"README.md not found: {readme_path}")
            
            with open(readme_path, 'r') as f:
                content = f.read()
                self.assertIn(project_name, content, f"Project name '{project_name}' not found in README.md")
        
        finally:
            # Clean up - remove test project
            if 'project_path' in locals() and os.path.exists(project_path):
                shutil.rmtree(project_path)


class TestMarkdownAnalysis(unittest.TestCase):
    """Test class to verify markdown analysis functionality"""
    
    def setUp(self):
        """Set up test case with a markdown file"""
        self.temp_dir = tempfile.mkdtemp()
        self.markdown_file = os.path.join(self.temp_dir, "test_markdown.md")
    
    def tearDown(self):
        """Clean up after test"""
        shutil.rmtree(self.temp_dir)
    
    def test_quality_analysis_good_markdown(self):
        """Test if markdown quality analysis correctly evaluates good markdown"""
        # Create a good quality markdown file
        with open(self.markdown_file, 'w') as f:
            f.write("""# Análisis del Proyecto

## Resumen
Este es un proyecto de ejemplo con buena estructura.

## Fortalezas
- Buena organización de archivos
- Documentación clara
- Pruebas unitarias completas

## Áreas de Mejora
- Optimizar rendimiento
- Añadir más comentarios al código

### Ejemplo de Código
```python
def hello_world():
    print("Hello, World!")
    return True
```

## Recomendaciones
1. Implementar linting
2. Mejorar la cobertura de pruebas
3. Optimizar consultas a la base de datos

## Sugerencias de Mejora (Generado por Anthropic Claude)
Este proyecto tiene una estructura sólida pero podría beneficiarse de
una mejor documentación y optimizaciones de rendimiento.
""")
        
        # Test the analysis
        result = analyze_markdown_quality(self.markdown_file)
        
        # Assertions
        self.assertTrue(result["success"], "Quality analysis should pass for good markdown")
        self.assertGreaterEqual(result["score"], 6, "Quality score should be at least 6 for good markdown")
        self.assertEqual(result["metrics"]["headings"], 5, "Should detect 5 headings")
        self.assertEqual(result["metrics"]["code_blocks"], 1, "Should detect 1 code block")
        self.assertGreaterEqual(result["metrics"]["list_items"], 5, "Should detect at least 5 list items")
    
    def test_quality_analysis_poor_markdown(self):
        """Test if markdown quality analysis correctly evaluates poor markdown"""
        # Create a poor quality markdown file
        with open(self.markdown_file, 'w') as f:
            f.write("""# Análisis
Proyecto sin estructura adecuada.
Sin secciones importantes.
""")
        
        # Test the analysis
        result = analyze_markdown_quality(self.markdown_file)
        
        # Assertions
        self.assertFalse(result["success"], "Quality analysis should fail for poor markdown")
        self.assertLess(result["score"], 6, "Quality score should be less than 6 for poor markdown")
    
    def test_quality_analysis_missing_anthropic_marker(self):
        """Test if analysis detects missing Anthropic marker"""
        # Create markdown without Anthropic marker
        with open(self.markdown_file, 'w') as f:
            f.write("""# Análisis del Proyecto

## Resumen
Este es un proyecto de ejemplo.

## Fortalezas
- Buena organización

## Áreas de Mejora
- Optimizar rendimiento
""")
        
        # Test the analysis
        result = analyze_markdown_quality(self.markdown_file)
        
        # Assertions
        self.assertFalse(result["success"], "Quality analysis should fail for markdown without Anthropic marker")
        self.assertEqual(result["reason"], "No Anthropic-generated content found", 
                        "Should detect missing Anthropic content")


class TestIntegration(unittest.TestCase):
    """Integration tests for the entire verification system"""
    
    @unittest.skipIf(not os.environ.get("RUN_EXPENSIVE_TESTS"), "Skipping expensive API tests")
    def test_full_verification_cycle(self):
        """Test a full verification cycle with actual API calls"""
        # This test is expensive and slow, so only run it when needed
        import subprocess
        
        try:
            cmd = [sys.executable, "enhanced_verify_anthropic.py", "--project-types", "web-project"]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            self.assertIn("VERIFICATION SUMMARY", result.stdout, "Verification summary should be in output")
            
            # Check if any results.json file was created
            output_dir = os.path.dirname(os.path.abspath(__file__))
            result_files = list(Path(output_dir).glob("verification_results_*.json"))
            
            self.assertTrue(len(result_files) > 0, "Should create a results JSON file")
            
            # Load the latest results file and check structure
            latest_file = max(result_files, key=os.path.getctime)
            with open(latest_file, 'r') as f:
                results = json.load(f)
            
            self.assertIn("overall_success", results, "Results JSON should have overall_success field")
            self.assertIn("results", results, "Results JSON should have results field")
            self.assertIn("web-project", results["results"], "Results JSON should have web-project results")
            
        except subprocess.CalledProcessError as e:
            self.fail(f"Verification failed with error:\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}")


if __name__ == "__main__":
    unittest.main()
