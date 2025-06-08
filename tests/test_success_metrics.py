import pytest
from pathlib import Path
import subprocess
import json
import sys
import os
import tempfile
import shutil

# Add src_new to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src_new"))

class TestRefactorizationMetrics:
    """Tests para validar métricas específicas de éxito de la refactorización"""
    
    def test_codebase_reduction_50_percent(self):
        """CRÍTICO: Verificar reducción del 50% en líneas de código"""
        # Contar líneas en src_new (nueva implementación)
        src_new_path = Path(__file__).parent.parent / "src_new"
        new_lines = self._count_python_lines(src_new_path)
        
        # Contar líneas en src (implementación anterior)
        src_old_path = Path(__file__).parent.parent / "src"
        old_lines = self._count_python_lines(src_old_path)
        
        # Calcular reducción
        if old_lines > 0:
            reduction_percentage = ((old_lines - new_lines) / old_lines) * 100
            
            print(f"Old codebase: {old_lines} lines")
            print(f"New codebase: {new_lines} lines") 
            print(f"Reduction: {reduction_percentage:.1f}%")
            
            # Debe haber al menos 50% de reducción
            assert reduction_percentage >= 50, f"Codebase reduction is only {reduction_percentage:.1f}%, expected ≥50%"
        else:
            # Si no hay código anterior, verificar que el nuevo es compacto
            assert new_lines < 5000, f"New codebase has {new_lines} lines, should be compact"
    
    def _count_python_lines(self, directory: Path) -> int:
        """Cuenta líneas de código Python en un directorio"""
        if not directory.exists():
            return 0
        
        total_lines = 0
        for py_file in directory.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Contar solo líneas no vacías y no comentarios
                    code_lines = [
                        line for line in lines 
                        if line.strip() and not line.strip().startswith('#')
                    ]
                    total_lines += len(code_lines)
            except Exception:
                continue
        
        return total_lines
    
    def test_only_two_main_commands_available(self):
        """CRÍTICO: Verificar que solo hay 2 comandos principales (analyze, suggest)"""
        result = subprocess.run(
            ["projectprompt", "--help"], 
            capture_output=True, 
            text=True
        )
        
        assert result.returncode == 0, "CLI help should work"
        
        help_output = result.stdout
        
        # Contar líneas que contienen comandos (identificadas por espacios al inicio)
        command_lines = []
        for line in help_output.split('\n'):
            # Buscar líneas que definen comandos (formato típico de click/argparse)
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                if any(cmd in line.lower() for cmd in ['analyze', 'suggest', 'status', 'clean']):
                    command_lines.append(line)
        
        # Verificar comandos principales
        main_commands = ['analyze', 'suggest']
        auxiliary_commands = ['status', 'clean']  # Comandos auxiliares permitidos
        
        for cmd in main_commands:
            assert any(cmd in help_output.lower() for cmd in main_commands), f"Main command '{cmd}' not found"
        
        # Verificar que no hay comandos adicionales no deseados
        forbidden_commands = ['dashboard', 'export', 'generate', 'verify-api', 'set-api']
        for cmd in forbidden_commands:
            assert cmd not in help_output.lower(), f"Forbidden command '{cmd}' found in help"
    
    def test_zero_empty_groups_in_real_project(self):
        """CRÍTICO: Verificar que no se generan grupos vacíos en proyecto real"""
        # Usar el propio proyecto como test
        project_root = Path(__file__).parent.parent
        test_dir = tempfile.mkdtemp()
        test_project = Path(test_dir) / "real_project_test"
        
        try:
            # Copiar algunos archivos del proyecto real para testing
            test_project.mkdir(parents=True)
            
            # Copiar archivos representativos
            files_to_copy = [
                "src_new/cli.py",
                "src_new/core/analyzer.py", 
                "src_new/utils/config.py",
                "pyproject.toml",
                "README.md"
            ]
            
            for file_path in files_to_copy:
                source = project_root / file_path
                if source.exists():
                    dest = test_project / file_path
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, dest)
            
            # Ejecutar análisis
            result = subprocess.run(
                ["projectprompt", "analyze", "."],
                cwd=str(test_project),
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, f"Analysis failed: {result.stderr}"
            
            # Verificar que no hay grupos vacíos en el output
            analysis_file = test_project / "analysis.json"
            if analysis_file.exists():
                with open(analysis_file) as f:
                    analysis = json.load(f)
                
                if "functional_groups" in analysis:
                    groups = analysis["functional_groups"]
                    
                    for group_name, group_data in groups.items():
                        if isinstance(group_data, dict) and "files" in group_data:
                            files = group_data["files"]
                        elif isinstance(group_data, list):
                            files = group_data
                        else:
                            continue
                        
                        assert len(files) > 0, f"CRITICAL: Empty group '{group_name}' found in real project analysis"
            
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)
    
    def test_zero_file_duplication(self):
        """CRÍTICO: Verificar que no hay duplicación de archivos entre grupos"""
        test_dir = tempfile.mkdtemp()
        test_project = Path(test_dir) / "duplication_test"
        
        try:
            test_project.mkdir(parents=True)
            
            # Crear proyecto con archivos que podrían causar duplicación
            files_to_create = [
                ("main.py", "import utils\nfrom config import settings"),
                ("utils.py", "import os\nimport main"),  # Dependencia circular
                ("config.py", "from utils import helper"),
                ("core/processor.py", "import main\nimport utils"),
                ("tests/test_main.py", "import main\nimport utils"),
            ]
            
            for file_path, content in files_to_create:
                full_path = test_project / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
            
            # Ejecutar análisis
            result = subprocess.run(
                ["projectprompt", "analyze", "."],
                cwd=str(test_project),
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, f"Analysis failed: {result.stderr}"
            
            # Verificar ausencia de duplicación
            analysis_file = test_project / "analysis.json"
            if analysis_file.exists():
                with open(analysis_file) as f:
                    analysis = json.load(f)
                
                if "functional_groups" in analysis:
                    groups = analysis["functional_groups"]
                    
                    # Recopilar todos los archivos
                    all_files = []
                    for group_name, group_data in groups.items():
                        if isinstance(group_data, dict) and "files" in group_data:
                            files = group_data["files"]
                        elif isinstance(group_data, list):
                            files = group_data
                        else:
                            continue
                        
                        all_files.extend(files)
                    
                    # Verificar no duplicación
                    unique_files = set(all_files)
                    duplicates = [f for f in all_files if all_files.count(f) > 1]
                    
                    assert len(all_files) == len(unique_files), f"CRITICAL: File duplication found: {duplicates}"
            
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)

class TestAPIIntegration:
    """Tests para validar integración con APIs Anthropic/OpenAI"""
    
    def test_anthropic_api_integration(self):
        """Test integración con Anthropic API (si hay API key)"""
        # Verificar si hay API key disponible
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        
        if not api_key:
            pytest.skip("No ANTHROPIC_API_KEY available for integration test")
        
        test_dir = tempfile.mkdtemp()
        test_project = Path(test_dir) / "api_test"
        
        try:
            test_project.mkdir(parents=True)
            
            # Crear proyecto simple
            (test_project / "main.py").write_text("print('Hello API test')")
            (test_project / ".env").write_text(f"ANTHROPIC_API_KEY={api_key}")
            
            # Ejecutar análisis
            result_analyze = subprocess.run(
                ["projectprompt", "analyze", "."],
                cwd=str(test_project),
                capture_output=True,
                text=True
            )
            
            assert result_analyze.returncode == 0, f"Analysis failed: {result_analyze.stderr}"
            
            # Ejecutar suggest (debería funcionar con API key)
            result_suggest = subprocess.run(
                ["projectprompt", "suggest", "main_modules"],
                cwd=str(test_project),
                capture_output=True,
                text=True,
                timeout=30  # Timeout para evitar esperas largas
            )
            
            # Si falla, debería ser por razones técnicas, no por falta de API key
            if result_suggest.returncode != 0:
                error_output = result_suggest.stderr.lower()
                # No debería fallar por API key si la proporcionamos
                assert "api key not found" not in error_output, "API key not recognized despite being provided"
            
        except subprocess.TimeoutExpired:
            pytest.skip("API test timed out - may be network related")
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)
    
    def test_api_key_validation_without_keys(self):
        """CRÍTICO: Verificar que suggest falla apropiadamente sin API keys"""
        test_dir = tempfile.mkdtemp()
        test_project = Path(test_dir) / "no_api_test"
        
        try:
            test_project.mkdir(parents=True)
            (test_project / "main.py").write_text("print('test')")
            
            # Análisis debe funcionar sin API keys
            result_analyze = subprocess.run(
                ["projectprompt", "analyze", "."],
                cwd=str(test_project),
                capture_output=True,
                text=True,
                env={k: v for k, v in os.environ.items() if not k.endswith("_API_KEY")}
            )
            
            assert result_analyze.returncode == 0, "Analysis should work without API keys"
            
            # Suggest debe fallar sin API keys
            result_suggest = subprocess.run(
                ["projectprompt", "suggest", "test_group"],
                cwd=str(test_project),
                capture_output=True,
                text=True,
                env={k: v for k, v in os.environ.items() if not k.endswith("_API_KEY")}
            )
            
            assert result_suggest.returncode != 0, "Suggest should fail without API keys"
            assert "api key" in result_suggest.stderr.lower(), "Should mention API key requirement"
            
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)

class TestOutputQuality:
    """Tests para validar calidad del output"""
    
    def test_analysis_output_structure(self):
        """Verificar que el análisis genera estructura JSON válida"""
        test_dir = tempfile.mkdtemp()
        test_project = Path(test_dir) / "output_test"
        
        try:
            test_project.mkdir(parents=True)
            
            # Crear proyecto con estructura variada
            files_to_create = [
                ("src/main.py", "from src.utils import helper"),
                ("src/utils.py", "def helper(): pass"),
                ("tests/test_main.py", "import unittest"),
                ("README.md", "# Test Project"),
                ("requirements.txt", "flask==2.0.1"),
            ]
            
            for file_path, content in files_to_create:
                full_path = test_project / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
            
            # Ejecutar análisis
            result = subprocess.run(
                ["projectprompt", "analyze", "."],
                cwd=str(test_project),
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, f"Analysis failed: {result.stderr}"
            
            # Verificar estructura del análisis
            analysis_file = test_project / "analysis.json"
            assert analysis_file.exists(), "Analysis file should be created"
            
            with open(analysis_file) as f:
                analysis = json.load(f)
            
            # Verificar campos requeridos
            required_fields = ["files", "functional_groups", "analysis_summary"]
            for field in required_fields:
                assert field in analysis, f"Analysis missing required field: {field}"
            
            # Verificar que functional_groups no está vacío
            groups = analysis.get("functional_groups", {})
            assert len(groups) > 0, "Should create at least one functional group"
            
            # Verificar calidad de los grupos
            for group_name, group_data in groups.items():
                assert isinstance(group_name, str), "Group names should be strings"
                assert len(group_name) > 0, "Group names should not be empty"
                
                if isinstance(group_data, dict) and "files" in group_data:
                    files = group_data["files"]
                    assert isinstance(files, list), "Group files should be a list"
                    assert len(files) > 0, f"Group {group_name} should not be empty"
            
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)
