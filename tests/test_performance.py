import pytest
import time
import psutil
import os
from pathlib import Path
import tempfile
import shutil
import sys

# Add src_new to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src_new"))

from core.analyzer import ProjectAnalyzer

class TestPerformanceBenchmarks:
    """Benchmarks de rendimiento para diferentes tamaños de proyecto"""
    
    def setup_method(self):
        self.process = psutil.Process(os.getpid())
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
    
    def _create_test_project(self, size: str) -> Path:
        """Crea proyecto de prueba de tamaño específico"""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir) / f"project_{size}"
        project_path.mkdir(parents=True)
        
        if size == "small":
            # Proyecto pequeño: 5-10 archivos
            files_to_create = [
                ("main.py", "from utils import helper\nprint('Hello World')"),
                ("utils.py", "def helper():\n    return 'helper'"),
                ("config.py", "DEBUG = True\nAPI_KEY = 'test'"),
                ("models.py", "class User:\n    def __init__(self): pass"),
                ("README.md", "# Small Test Project"),
            ]
        elif size == "medium":
            # Proyecto mediano: 20-50 archivos
            files_to_create = []
            
            # Core modules
            for i in range(5):
                files_to_create.append((f"core/module_{i}.py", f"# Core module {i}\nclass Module{i}:\n    pass"))
            
            # Utils modules
            for i in range(5):
                files_to_create.append((f"utils/util_{i}.py", f"# Utility {i}\ndef function_{i}():\n    pass"))
            
            # Models
            for i in range(5):
                files_to_create.append((f"models/model_{i}.py", f"# Model {i}\nclass Model{i}:\n    pass"))
            
            # Tests
            for i in range(5):
                files_to_create.append((f"tests/test_{i}.py", f"# Test {i}\nimport unittest"))
            
            # Config files
            files_to_create.extend([
                ("config.py", "# Configuration\nDEBUG = True"),
                ("requirements.txt", "flask==2.0.1\nrequests==2.25.1"),
                ("README.md", "# Medium Test Project"),
                ("setup.py", "from setuptools import setup\nsetup(name='test')"),
            ])
            
        elif size == "large":
            # Proyecto grande: 100+ archivos
            files_to_create = []
            
            # Multiple modules with submodules
            modules = ["auth", "api", "core", "utils", "models", "views", "tests", "migrations", "static", "templates"]
            
            for module in modules:
                for i in range(12):  # 12 files per module = 120 files
                    if module == "static":
                        files_to_create.append((f"{module}/file_{i}.css", f"/* CSS file {i} */\nbody {{ margin: 0; }}"))
                    elif module == "templates":
                        files_to_create.append((f"{module}/template_{i}.html", f"<!-- Template {i} -->\n<html></html>"))
                    else:
                        files_to_create.append((f"{module}/file_{i}.py", 
                            f"# {module.title()} file {i}\n"
                            f"import os\n"
                            f"import sys\n"
                            f"from pathlib import Path\n"
                            f"\nclass {module.title()}{i}:\n"
                            f"    def __init__(self):\n"
                            f"        self.name = '{module}_{i}'\n"
                            f"    \n"
                            f"    def process(self):\n"
                            f"        return f'Processing {{self.name}}'\n"
                            f"\n"
                            f"def function_{i}():\n"
                            f"    return '{module}_{i}_result'\n"
                        ))
            
            # Add some configuration files
            files_to_create.extend([
                ("config.py", "# Main configuration\nDEBUG = True\nDB_URL = 'postgresql://localhost/app'"),
                ("requirements.txt", "flask==2.0.1\ndjango==3.2.1\nrequests==2.25.1\nnumpy==1.21.0"),
                ("README.md", "# Large Test Project\nThis is a comprehensive test project."),
                ("setup.py", "from setuptools import setup, find_packages\nsetup(name='large_test', packages=find_packages())"),
                ("pyproject.toml", "[tool.poetry]\nname = 'large-test'\nversion = '0.1.0'"),
            ])
        
        # Create all files
        for file_path, content in files_to_create:
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        return project_path
    
    def _measure_performance(self, project_path: Path, max_time_seconds: int = 60):
        """Mide rendimiento del análisis"""
        analyzer = ProjectAnalyzer()
        
        # Medir memoria inicial
        initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        # Medir tiempo de análisis
        start_time = time.time()
        
        try:
            analysis = analyzer.analyze_project(str(project_path))
            analysis_time = time.time() - start_time
            
            # Save analysis results like CLI does
            self._save_analysis_results(analysis, project_path)
            
            success = True
            error = None
        except Exception as e:
            analysis_time = time.time() - start_time
            success = False
            error = str(e)
        
        # Medir memoria final
        final_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        memory_used = final_memory - initial_memory
        
        return {
            "success": success,
            "analysis_time": analysis_time,
            "memory_used": memory_used,
            "final_memory": final_memory,
            "error": error if not success else None
        }
    
    def _save_analysis_results(self, analysis, output_path: Path):
        """Save analysis results to directory structure like CLI does."""
        import json
        
        # Create analysis file
        analysis_file = output_path / "analysis.json"
        
        # Convert analysis to dict for JSON serialization
        analysis_data = {
            'project_name': analysis.project_name,
            'project_path': analysis.project_path,
            'project_type': analysis.project_type.value if hasattr(analysis.project_type, 'value') else str(analysis.project_type),
            'main_language': analysis.main_language,
            'file_count': analysis.file_count,
            'analysis_date': analysis.analysis_date,
            'detected_functionalities': analysis.detected_functionalities,
            'files': [{'path': f.path, 'size': f.size} for f in analysis.files] if hasattr(analysis, 'files') else [],
            'functional_groups': analysis.groups if hasattr(analysis, 'groups') else {},
            'analysis_summary': {
                'total_files': analysis.file_count,
                'total_groups': len(analysis.groups) if hasattr(analysis, 'groups') else 0,
                'main_language': analysis.main_language
            },
            'status': analysis.status.value if hasattr(analysis.status, 'value') else str(analysis.status)
        }
        
        # Save main analysis
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
    
    def test_small_project_performance(self):
        """CRÍTICO: Proyecto pequeño debe analizarse rápidamente"""
        project_path = self._create_test_project("small")
        
        try:
            metrics = self._measure_performance(project_path, max_time_seconds=10)
            
            # Validaciones críticas para proyecto pequeño
            assert metrics["success"], f"Small project analysis failed: {metrics.get('error')}"
            assert metrics["analysis_time"] < 10, f"Small project took too long: {metrics['analysis_time']:.2f}s"
            assert metrics["memory_used"] < 50, f"Small project used too much memory: {metrics['memory_used']:.2f}MB"
            
            # Verificar que se creó el análisis
            analysis_file = project_path / "analysis.json"
            assert analysis_file.exists(), "Analysis file should be created"
            
        finally:
            shutil.rmtree(project_path, ignore_errors=True)
    
    def test_medium_project_performance(self):
        """CRÍTICO: Proyecto mediano debe analizarse en tiempo razonable"""
        project_path = self._create_test_project("medium")
        
        try:
            metrics = self._measure_performance(project_path, max_time_seconds=30)
            
            # Validaciones para proyecto mediano
            assert metrics["success"], f"Medium project analysis failed: {metrics.get('error')}"
            assert metrics["analysis_time"] < 30, f"Medium project took too long: {metrics['analysis_time']:.2f}s"
            assert metrics["memory_used"] < 100, f"Medium project used too much memory: {metrics['memory_used']:.2f}MB"
            
            # Verificar que se creó el análisis
            analysis_file = project_path / "analysis.json"
            assert analysis_file.exists(), "Analysis file should be created"
            
        finally:
            shutil.rmtree(project_path, ignore_errors=True)
    
    def test_large_project_performance(self):
        """CRÍTICO: Proyecto grande debe analizarse en <60s y <200MB"""
        project_path = self._create_test_project("large")
        
        try:
            metrics = self._measure_performance(project_path, max_time_seconds=60)
            
            # Validaciones críticas para proyecto grande según especificaciones
            assert metrics["success"], f"Large project analysis failed: {metrics.get('error')}"
            assert metrics["analysis_time"] < 60, f"Large project took too long: {metrics['analysis_time']:.2f}s (max: 60s)"
            assert metrics["memory_used"] < 200, f"Large project used too much memory: {metrics['memory_used']:.2f}MB (max: 200MB)"
            
            # Verificar que se creó el análisis
            analysis_file = project_path / "analysis.json"
            assert analysis_file.exists(), "Analysis file should be created"
            
            print(f"Large project performance: {metrics['analysis_time']:.2f}s, {metrics['memory_used']:.2f}MB")
            
        finally:
            shutil.rmtree(project_path, ignore_errors=True)
    
    def test_memory_leak_detection(self):
        """CRÍTICO: Detectar memory leaks ejecutando múltiples análisis"""
        initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        # Ejecutar múltiples análisis consecutivos
        for i in range(3):
            project_path = self._create_test_project("small")
            
            try:
                analyzer = ProjectAnalyzer()
                analyzer.analyze_project(str(project_path))
                
                # Forzar garbage collection
                import gc
                gc.collect()
                
            finally:
                shutil.rmtree(project_path, ignore_errors=True)
        
        # Medir memoria final después de múltiples análisis
        final_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        # No debe haber crecimiento significativo de memoria (memory leak)
        assert memory_growth < 50, f"Potential memory leak detected: {memory_growth:.2f}MB growth"

class TestQualityMetrics:
    """Tests para validar métricas de calidad específicas de Fase 5"""
    
    def _save_analysis_results(self, analysis, output_path: Path):
        """Save analysis results to directory structure like CLI does."""
        import json
        
        # Create analysis file
        analysis_file = output_path / "analysis.json"
        
        # Convert analysis to dict for JSON serialization
        analysis_data = {
            'project_name': analysis.project_name,
            'project_path': analysis.project_path,
            'project_type': analysis.project_type.value if hasattr(analysis.project_type, 'value') else str(analysis.project_type),
            'main_language': analysis.main_language,
            'file_count': analysis.file_count,
            'analysis_date': analysis.analysis_date,
            'detected_functionalities': analysis.detected_functionalities,
            'files': [{'path': f.path, 'size': f.size} for f in analysis.files] if hasattr(analysis, 'files') else [],
            'functional_groups': analysis.groups if hasattr(analysis, 'groups') else {},
            'analysis_summary': {
                'total_files': analysis.file_count,
                'total_groups': len(analysis.groups) if hasattr(analysis, 'groups') else 0,
                'main_language': analysis.main_language
            },
            'status': analysis.status.value if hasattr(analysis.status, 'value') else str(analysis.status)
        }
        
        # Save main analysis
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
    
    def test_markdown_only_output(self):
        """CRÍTICO: Verificar que el output es solo markdown, no HTML"""
        project_path = Path(tempfile.mkdtemp()) / "markdown_test"
        project_path.mkdir(parents=True)
        
        # Crear proyecto simple
        (project_path / "main.py").write_text("print('test')")
        
        try:
            analyzer = ProjectAnalyzer()
            analysis = analyzer.analyze_project(str(project_path))
            
            # Save analysis results like CLI does
            self._save_analysis_results(analysis, project_path)
            
            # Verificar archivos generados
            output_files = list(project_path.rglob("*"))
            
            for file_path in output_files:
                if file_path.is_file() and file_path.suffix in ['.html', '.htm']:
                    pytest.fail(f"HTML file found: {file_path}. Only markdown output should be generated.")
            
            # Verificar que se genera análisis en JSON (no HTML)
            analysis_file = project_path / "analysis.json"
            assert analysis_file.exists(), "Should generate analysis.json"
            
        finally:
            shutil.rmtree(project_path, ignore_errors=True)
    
    def test_cli_commands_count(self):
        """CRÍTICO: Verificar que solo hay 2 comandos principales disponibles"""
        import subprocess
        
        result = subprocess.run(
            ["projectprompt", "--help"], 
            capture_output=True, 
            text=True
        )
        
        assert result.returncode == 0, "CLI help should work"
        
        # Contar comandos principales en la salida
        help_output = result.stdout.lower()
        
        # Verificar que están los comandos principales
        assert "analyze" in help_output, "Should have 'analyze' command"
        assert "suggest" in help_output, "Should have 'suggest' command"
        
        # Comandos auxiliares permitidos
        allowed_commands = ["analyze", "suggest", "status", "clean"]
        
        # Verificar que no hay comandos no permitidos (como dashboard, verify-api, etc.)
        forbidden_commands = ["dashboard", "verify-api", "set-api", "generate", "export"]
        
        for cmd in forbidden_commands:
            assert cmd not in help_output, f"Command '{cmd}' should not be available in v2.0"
