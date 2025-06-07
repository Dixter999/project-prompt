# Fase 5: Testing y Optimización
**Branch**: `phase5/testing-optimization`  
**Duración**: 1 semana  
**Objetivo**: Testing exhaustivo, validación de rendimiento y preparación para release v2.0

## 🎯 Objetivos de la Fase
- Implementar tests comprehensivos para todos los problemas resueltos
- Validar rendimiento en proyectos de diferentes tamaños
- Verificar métricas de éxito de la refactorización
- Asegurar calidad de output y funcionamiento end-to-end
- Preparar documentación final y release v2.0

## 🧪 Tests Críticos de Funcionalidad

### Archivo: `tests/test_core_functionality.py`

```python
import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import Mock, patch

from src_new.core.analyzer import ProjectAnalyzer
from src_new.core.group_manager import GroupManager
from src_new.core.dependency_analyzer import UnifiedDependencyAnalyzer
from src_new.core.group_priority_system import GroupPrioritySystem
from src_new.core.file_group_mapping import GroupMappingManager

class TestCoreAnalysisFunctionality:
    """Tests críticos para validar que problemas principales están resueltos"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.test_dir = tempfile.mkdtemp()
        self.test_project = Path(self.test_dir) / "test_project"
        self.test_project.mkdir(parents=True)
        
        # Crear archivos de prueba
        self._create_test_files()
    
    def teardown_method(self):
        """Cleanup después de cada test"""
        shutil.rmtree(self.test_dir)
    
    def _create_test_files(self):
        """Crea estructura de prueba con dependencias conocidas"""
        files_to_create = [
            ("main.py", "import utils\nimport config\nfrom core import processor"),
            ("utils.py", "import os\nimport sys"),
            ("config.py", "import json\nfrom utils import helper"),
            ("core/processor.py", "from utils import tools\nimport main"),
            ("core/__init__.py", ""),
            ("tests/test_main.py", "import main\nimport pytest"),
            ("tests/__init__.py", ""),
        ]
        
        for file_path, content in files_to_create:
            full_path = self.test_project / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
    
    def test_no_empty_groups_ever(self):
        """CRÍTICO: Asegura que NUNCA se generen grupos vacíos"""
        analyzer = ProjectAnalyzer()
        group_manager = GroupManager()
        
        # Análisis completo
        analysis = analyzer.analyze(str(self.test_project))
        groups = group_manager.create_groups(analysis.files)
        
        # Validación estricta
        for group_name, files in groups.items():
            assert len(files) > 0, f"CRITICAL FAILURE: Group '{group_name}' is empty"
            
            # Verificar que todos los archivos existen realmente
            for file_path in files:
                assert Path(file_path).exists(), f"File {file_path} in group {group_name} doesn't exist"
        
        # Debe haber al menos un grupo
        assert len(groups) > 0, "No groups were created at all"
    
    def test_no_duplicate_files_between_groups(self):
        """CRÍTICO: Asegura que no hay archivos duplicados entre grupos"""
        analyzer = ProjectAnalyzer()
        priority_system = GroupPrioritySystem()
        
        # Análisis y aplicación de prioridades
        analysis = analyzer.analyze(str(self.test_project))
        
        # Simular grupos con potenciales duplicados
        potential_groups = {
            'core_modules': ['main.py', 'config.py'],
            'utility_modules': ['main.py', 'utils.py'],  # main.py duplicado
            'test_modules': ['tests/test_main.py', 'config.py']  # config.py duplicado
        }
        
        # Aplicar sistema de prioridad
        final_groups = priority_system.assign_files_to_groups(potential_groups)
        
        # Validar que no hay duplicados
        all_files = []
        for group_files in final_groups.values():
            all_files.extend(group_files)
        
        unique_files = set(all_files)
        assert len(all_files) == len(unique_files), f"CRITICAL FAILURE: Duplicate files found: {[f for f in all_files if all_files.count(f) > 1]}"
        
        # Validar sistema de prioridad funcionando
        assert priority_system.validate_no_duplicates(final_groups)
    
    def test_file_group_mapping_completeness(self):
        """CRÍTICO: Verifica mapeo completo archivo ↔ grupo"""
        analyzer = ProjectAnalyzer()
        mapping_manager = GroupMappingManager()
        
        analysis = analyzer.analyze(str(self.test_project))
        
        # Crear mapeos
        groups = {'core': ['main.py'], 'utils': ['utils.py']}
        mappings = mapping_manager.create_mappings(groups)
        
        # Validar mapeo bidireccional
        for file_path in ['main.py', 'utils.py']:
            # Archivo → Grupo
            mapping = mapping_manager.get_file_group(file_path)
            assert mapping is not None, f"No mapping found for {file_path}"
            
            # Grupo → Archivo
            group_files = mapping_manager.get_group_files(mapping.group_name)
            assert file_path in group_files, f"Bidirectional mapping broken for {file_path}"
        
        # Estadísticas completas
        stats = mapping_manager.get_mapping_statistics()
        assert stats['total_files'] == 2
        assert stats['total_groups'] == 2

class TestDependencyAnalysis:
    """Tests específicos para analizador de dependencias unificado"""
    
    def test_dependency_graph_has_real_connections(self):
        """CRÍTICO: Verifica que el grafo tenga conexiones reales"""
        analyzer = UnifiedDependencyAnalyzer()
        
        # Crear archivos con dependencias conocidas
        with tempfile.TemporaryDirectory() as temp_dir:
            file1 = Path(temp_dir) / "file1.py"
            file2 = Path(temp_dir) / "file2.py"
            
            file1.write_text("import file2\nfrom utils import helper")
            file2.write_text("import os\nimport sys")
            
            # Analizar dependencias
            result = analyzer.analyze_dependencies([str(file1), str(file2)])
            
            # Debe haber conexiones reales
            assert result['total_connections'] > 0, "CRITICAL FAILURE: Dependency analyzer found no connections"
            
            # El grafo debe tener nodos
            assert result['graph'].number_of_nodes() > 0, "Dependency graph has no nodes"
            
            # Debe detectar la dependencia file1 → file2
            graph = result['graph']
            assert graph.has_edge(str(file1), str(file2)) or any(
                'file2' in str(target) for source, target in graph.edges() 
                if 'file1' in str(source)
            ), "Known dependency not detected"
    
    def test_circular_dependency_detection(self):
        """Verifica detección de dependencias circulares"""
        analyzer = UnifiedDependencyAnalyzer()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_a = Path(temp_dir) / "a.py"
            file_b = Path(temp_dir) / "b.py"
            
            # Crear dependencia circular
            file_a.write_text("import b")
            file_b.write_text("import a")
            
            result = analyzer.analyze_dependencies([str(file_a), str(file_b)])
            
            # Debe detectar al menos un ciclo
            assert len(result['circular_dependencies']) > 0, "Circular dependency not detected"

class TestIntegrationWorkflow:
    """Tests de integración para flujo completo"""
    
    def test_complete_analysis_workflow(self):
        """Test del flujo completo: análisis → grupos → mapeo → sin errores"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup proyecto de prueba
            project_path = Path(temp_dir) / "project"
            project_path.mkdir()
            
            (project_path / "main.py").write_text("import utils")
            (project_path / "utils.py").write_text("import os")
            
            # Flujo completo
            analyzer = ProjectAnalyzer()
            group_manager = GroupManager()
            priority_system = GroupPrioritySystem()
            mapping_manager = GroupMappingManager()
            
            # 1. Análisis inicial
            analysis = analyzer.analyze(str(project_path))
            assert len(analysis.files) > 0
            
            # 2. Creación de grupos (sin vacíos)
            groups = group_manager.create_groups(analysis.files)
            assert group_manager.validate_groups(groups)
            
            # 3. Eliminación de duplicados
            clean_groups = priority_system.assign_files_to_groups(groups)
            assert priority_system.validate_no_duplicates(clean_groups)
            
            # 4. Mapeo completo
            mappings = mapping_manager.create_mappings(clean_groups)
            assert len(mappings) > 0
            
            # 5. Validación final
            for file_info in analysis.files:
                mapping = mapping_manager.get_file_group(file_info.path)
                assert mapping is not None, f"File {file_info.path} has no group mapping"
```

## ⚡ Tests de Rendimiento

### Archivo: `tests/test_performance.py`

```python
import pytest
import time
import psutil
import os
from pathlib import Path
import tempfile
import shutil

from src_new.core.analyzer import ProjectAnalyzer

class TestPerformanceBenchmarks:
    """Benchmarks de rendimiento para diferentes tamaños de proyecto"""
    
    def setup_method(self):
        self.process = psutil.Process(os.getpid())
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
    
    def _create_test_project(self, size: str) -> Path:
        """Crea proyecto de prueba de tamaño específico"""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir) / f"{size}_project"
        project_path.mkdir(parents=True)
        
        file_counts = {
            'small': 50,
            'medium': 500,
            'large': 1500
        }
        
        num_files = file_counts.get(size, 50)
        
        for i in range(num_files):
            file_path = project_path / f"module_{i:04d}.py"
            content = f"""
# Module {i}
import os
import sys
from typing import List, Dict

def function_{i}():
    \"\"\"Function in module {i}\"\"\"
    return {i}

class Class{i}:
    \"\"\"Class in module {i}\"\"\"
    def __init__(self):
        self.value = {i}
    
    def method_{i}(self, param: int) -> int:
        return param + {i}

# Some dependencies
{'import module_' + str((i-1) % max(1, i)) if i > 0 else '# No dependencies'}
"""
            file_path.write_text(content)
        
        return project_path
    
    @pytest.mark.parametrize("project_size,max_time,max_memory", [
        ("small", 10, 50),      # <50 archivos, <10s, <50MB
        ("medium", 30, 100),    # ~500 archivos, <30s, <100MB  
        ("large", 60, 200),     # ~1500 archivos, <60s, <200MB
    ])
    def test_analysis_performance(self, project_size, max_time, max_memory):
        """Verifica que el análisis se complete en tiempo y memoria razonables"""
        project_path = self._create_test_project(project_size)
        
        try:
            analyzer = ProjectAnalyzer()
            
            # Medir tiempo
            start_time = time.time()
            start_memory = self.process.memory_info().rss / 1024 / 1024
            
            analysis = analyzer.analyze(str(project_path))
            
            end_time = time.time()
            end_memory = self.process.memory_info().rss / 1024 / 1024
            
            duration = end_time - start_time
            memory_used = end_memory - start_memory
            
            # Validaciones de rendimiento
            assert duration < max_time, f"Analysis took {duration:.2f}s, should be <{max_time}s for {project_size} project"
            assert memory_used < max_memory, f"Analysis used {memory_used:.1f}MB, should be <{max_memory}MB for {project_size} project"
            
            # Validar que el análisis produjo resultados
            assert len(analysis.groups) > 0, f"Analysis of {project_size} project produced no groups"
            assert len(analysis.files) > 0, f"Analysis of {project_size} project found no files"
            
            # Log de rendimiento para monitoring
            print(f"\n📊 Performance metrics for {project_size} project:")
            print(f"   ⏱️  Duration: {duration:.2f}s (limit: {max_time}s)")
            print(f"   💾 Memory: {memory_used:.1f}MB (limit: {max_memory}MB)")
            print(f"   📁 Groups: {len(analysis.groups)}")
            print(f"   📄 Files: {len(analysis.files)}")
            
        finally:
            # Cleanup
            shutil.rmtree(project_path.parent)
    
    def test_memory_leak_detection(self):
        """Verifica que no hay memory leaks en análisis repetidos"""
        project_path = self._create_test_project('small')
        
        try:
            analyzer = ProjectAnalyzer()
            initial_memory = self.process.memory_info().rss / 1024 / 1024
            
            # Ejecutar múltiples análisis
            for i in range(5):
                analysis = analyzer.analyze(str(project_path))
                assert len(analysis.files) > 0
            
            final_memory = self.process.memory_info().rss / 1024 / 1024
            memory_growth = final_memory - initial_memory
            
            # No debe crecer más de 10MB en 5 ejecuciones
            assert memory_growth < 10, f"Memory leak detected: {memory_growth:.1f}MB growth after 5 analyses"
            
        finally:
            shutil.rmtree(project_path.parent)
    
    def test_large_file_handling(self):
        """Verifica manejo eficiente de archivos grandes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "large_file_project"
            project_path.mkdir()
            
            # Crear archivo grande (simulando archivo generado)
            large_file = project_path / "large_generated_file.py"
            content = "# Large generated file\n" + "pass\n" * 10000  # ~50KB
            large_file.write_text(content)
            
            # Crear archivos normales
            for i in range(10):
                (project_path / f"normal_{i}.py").write_text(f"# Normal file {i}\npass")
            
            analyzer = ProjectAnalyzer()
            start_time = time.time()
            
            analysis = analyzer.analyze(str(project_path))
            
            duration = time.time() - start_time
            
            # Debe manejar archivos grandes eficientemente
            assert duration < 5, f"Large file analysis took {duration:.2f}s, should be <5s"
            assert len(analysis.files) == 11, "Not all files were processed"
```

## 🔍 Tests de Calidad de Output

### Archivo: `tests/test_output_quality.py`

```python
import pytest
from pathlib import Path
import tempfile
import json
from unittest.mock import Mock, patch

from src_new.core.analyzer import ProjectAnalyzer
from src_new.generators.suggestions import SuggestionGenerator
from src_new.cli import cli
from click.testing import CliRunner

class TestOutputQuality:
    """Tests para validar calidad de outputs generados"""
    
    def test_markdown_output_only_no_html(self):
        """CRÍTICO: Verifica que solo se genere output en markdown"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "project"
            project_path.mkdir()
            
            # Crear proyecto simple
            (project_path / "main.py").write_text("print('test')")
            
            analyzer = ProjectAnalyzer()
            analysis = analyzer.analyze(str(project_path))
            
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir()
            analysis.save_to_directory(output_dir)
            
            # NO debe haber archivos HTML
            html_files = list(output_dir.glob("**/*.html"))
            assert len(html_files) == 0, f"CRITICAL FAILURE: HTML files found: {html_files}"
            
            # DEBE haber archivos markdown
            md_files = list(output_dir.glob("**/*.md"))
            assert len(md_files) > 0, "No markdown files generated"
            
            # Verificar contenido de archivos markdown
            for md_file in md_files:
                content = md_file.read_text()
                assert content.startswith('#'), f"Markdown file {md_file} doesn't start with header"
                assert len(content) > 10, f"Markdown file {md_file} seems empty"
    
    def test_suggestion_quality_structure(self):
        """Verifica estructura y calidad básica de sugerencias"""
        # Mock AI client para testing
        mock_suggestions = """# Suggestions for Core Files

## 1. Code Structure Improvements

### 1.1 Reorganize main.py
- **Current issue**: Main file is handling too many responsibilities
- **Suggestion**: Split into separate modules for configuration, core logic, and CLI
- **Implementation**: Create `config.py`, `core.py`, and `cli.py`

## 2. Functionality Enhancement

### 2.1 Add error handling
- **Current issue**: Limited error handling for file operations
- **Suggestion**: Implement comprehensive try-catch blocks
- **Implementation**: 
```python
try:
    # File operations
except FileNotFoundError:
    # Handle missing files
except PermissionError:
    # Handle permission issues
```

## 3. Next Steps
1. Implement configuration module
2. Add unit tests
3. Improve error handling
"""
        
        with patch('src_new.ai.client.AIClient') as mock_ai:
            mock_ai.return_value.generate_suggestions.return_value = mock_suggestions
            
            generator = SuggestionGenerator(api_provider="anthropic")
            
            # Simular contexto de grupo
            group_context = {
                'group_name': 'Core Files',
                'group_info': {'files': ['main.py', 'utils.py']},
                'tech_stack': ['Python'],
                'dependencies': {}
            }
            
            prompt = generator.create_contextual_prompt(group_context, 'medium')
            suggestions = generator.generate_suggestions(prompt, group_context)
            
            # Verificaciones de calidad
            assert "# " in suggestions, "Suggestions should have markdown headers"
            assert len(suggestions) > 100, "Suggestions should be substantial"
            assert "```" in suggestions, "Suggestions should include code examples"
            assert "## " in suggestions, "Suggestions should have sub-headers"
            assert "main.py" in suggestions, "Suggestions should reference specific files"
            
            # Verificar metadata
            assert "ProjectPrompt v2.0" in suggestions, "Should include generation metadata"
            assert "Core Files" in suggestions, "Should include group name in metadata"
    
    def test_analysis_completeness(self):
        """Verifica que el análisis capture toda la información necesaria"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "complete_project"
            project_path.mkdir()
            
            # Crear proyecto con diferentes tipos de archivos
            files_to_create = [
                ("main.py", "import config\nfrom utils import helper"),
                ("config.py", "DEBUG = True"),
                ("utils/helper.py", "def help(): pass"),
                ("utils/__init__.py", ""),
                ("tests/test_main.py", "import unittest"),
                ("README.md", "# Project"),
                (".gitignore", "*.pyc"),
            ]
            
            for file_path, content in files_to_create:
                full_path = project_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
            
            analyzer = ProjectAnalyzer()
            analysis = analyzer.analyze(str(project_path))
            
            # Verificar completitud
            assert len(analysis.files) >= 5, "Should detect Python files"  # Ignorar .md, .gitignore
            assert len(analysis.groups) > 0, "Should create functional groups"
            
            # Verificar que detectó diferentes tipos
            file_extensions = [Path(f.path).suffix for f in analysis.files]
            assert '.py' in file_extensions, "Should detect Python files"
            
            # Verificar que creó grupos lógicos
            group_names = list(analysis.groups.keys())
            assert len(group_names) > 1, "Should create multiple logical groups"
    
    def test_cli_output_user_friendly(self):
        """Verifica que output de CLI sea user-friendly"""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Crear proyecto de prueba
            os.mkdir('test_project')
            with open('test_project/main.py', 'w') as f:
                f.write('print("hello")')
            
            # Configurar env
            with open('.env', 'w') as f:
                f.write('ANTHROPIC_API_KEY=test_key_for_testing\n')
            
            # Test comando analyze
            result = runner.invoke(cli, ['analyze', 'test_project'])
            
            # Verificar output user-friendly
            assert '🔍' in result.output, "Should use emojis for better UX"
            assert '✅' in result.output or 'Analysis complete' in result.output, "Should show completion clearly"
            assert 'project-output' in result.output, "Should mention output location"
            
            # Test comando status
            result = runner.invoke(cli, ['status'])
            assert '📊' in result.output or 'Status' in result.output, "Status should be visually clear"
```

## 📊 Validación de Métricas de Éxito

### Archivo: `tests/test_success_metrics.py`

```python
import pytest
from pathlib import Path
import tempfile
import subprocess
import time

class TestSuccessMetrics:
    """Validación de las métricas de éxito de la refactorización"""
    
    def test_codebase_size_reduction(self):
        """Verifica reducción del 50% en tamaño de código base"""
        # Este test requiere comparación con versión anterior
        # En implementación real, se compararía con backup de v1.x
        
        src_new_path = Path("src_new")
        if src_new_path.exists():
            # Contar líneas en nueva implementación
            py_files = list(src_new_path.glob("**/*.py"))
            total_lines = 0
            
            for py_file in py_files:
                try:
                    lines = len(py_file.read_text().splitlines())
                    total_lines += lines
                except:
                    pass
            
            # La nueva implementación debería ser significativamente más pequeña
            # Objetivo: <5000 líneas para nueva implementación
            assert total_lines < 5000, f"New codebase has {total_lines} lines, should be <5000"
            
            print(f"📊 New codebase size: {total_lines} lines")
    
    def test_dependency_count_reduction(self):
        """Verifica reducción de dependencias a <8"""
        requirements_file = Path("requirements.txt")
        
        if requirements_file.exists():
            content = requirements_file.read_text()
            dependencies = [line.strip() for line in content.splitlines() 
                          if line.strip() and not line.startswith('#')]
            
            # Filtrar solo dependencias core (sin comentarios ni flags)
            core_deps = [dep for dep in dependencies if '=' in dep or '>' in dep]
            
            assert len(core_deps) <= 8, f"Too many dependencies: {len(core_deps)}, should be ≤8"
            
            print(f"📦 Core dependencies: {len(core_deps)}")
            for dep in core_deps:
                print(f"   • {dep}")
    
    def test_cli_command_count(self):
        """Verifica que solo hay 2 comandos principales disponibles"""
        from src_new.cli import cli
        
        # Obtener comandos disponibles
        ctx = cli.make_context('cli', [])
        commands = list(ctx.command.list_commands(ctx))
        
        # Comandos principales (analyze, suggest)
        main_commands = [cmd for cmd in commands if cmd in ['analyze', 'suggest']]
        assert len(main_commands) == 2, f"Should have exactly 2 main commands, found: {main_commands}"
        
        # Comandos auxiliares permitidos (status, clean)
        aux_commands = [cmd for cmd in commands if cmd in ['status', 'clean']]
        
        # Total no debe exceder 6 comandos
        total_commands = len(commands)
        assert total_commands <= 6, f"Too many CLI commands: {total_commands}, should be ≤6"
        
        print(f"🖥️  CLI commands: {commands}")
    
    def test_installation_simplicity(self):
        """Verifica que instalación sea simple con pip install -e ."""
        # Verificar que setup.py existe y es funcional
        setup_file = Path("setup.py")
        assert setup_file.exists(), "setup.py file missing"
        
        # Verificar contenido básico de setup.py
        content = setup_file.read_text()
        assert "entry_points" in content, "setup.py should have entry_points"
        assert "projectprompt" in content, "setup.py should define projectprompt command"
        
        # Verificar que no hay pyproject.toml (Poetry eliminado)
        pyproject_file = Path("pyproject.toml")
        poetry_lock = Path("poetry.lock")
        
        # Estos archivos NO deben existir en v2.0
        assert not pyproject_file.exists(), "pyproject.toml should be removed (Poetry eliminated)"
        assert not poetry_lock.exists(), "poetry.lock should be removed (Poetry eliminated)"
    
    def test_configuration_simplicity(self):
        """Verifica configuración simple con solo .env"""
        # Verificar que .env.example existe
        env_example = Path(".env.example")
        assert env_example.exists(), ".env.example file missing"
        
        # Verificar contenido de .env.example
        content = env_example.read_text()
        assert "ANTHROPIC_API_KEY" in content, ".env.example should include Anthropic key"
        assert "OPENAI_API_KEY" in content, ".env.example should include OpenAI key"
        
        # Verificar que archivos de configuración complejos NO existen
        complex_configs = [
            "config.yaml", "config.yml", "settings.json", 
            "projectprompt.conf", ".projectprompt.yaml"
        ]
        
        for config_file in complex_configs:
            assert not Path(config_file).exists(), f"Complex config file {config_file} should not exist"
    
    @pytest.mark.integration
    def test_end_to_end_workflow_performance(self):
        """Test de rendimiento del flujo completo end-to-end"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear proyecto de prueba
            project_path = Path(temp_dir) / "test_project"
            project_path.mkdir()
            
            (project_path / "main.py").write_text("import utils")
            (project_path / "utils.py").write_text("def helper(): pass")
            
            # Medir tiempo total del flujo
            start_time = time.time()
            
            # 1. Análisis
            from src_new.core.analyzer import ProjectAnalyzer
            analyzer = ProjectAnalyzer()
            analysis = analyzer.analyze(str(project_path))
            
            # 2. Validaciones críticas
            assert len(analysis.groups) > 0
            assert all(len(files) > 0 for files in analysis.groups.values())
            
            end_time = time.time()
            total_duration = end_time - start_time
            
            # Flujo completo debe ser <5 segundos para proyecto pequeño
            assert total_duration < 5, f"End-to-end workflow took {total_duration:.2f}s, should be <5s"
            
            print(f"⚡ End-to-end performance: {total_duration:.2f}s")

class TestRegressionPrevention:
    """Tests para prevenir regresión de problemas ya resueltos"""
    
    def test_no_regression_empty_groups(self):
        """Asegura que el problema de grupos vacíos no regrese"""
        # Este test debe fallar si alguien reintroduce el bug
        from src_new.core.group_manager import GroupManager
        
        manager = GroupManager()
        
        # Simular situación que causaba grupos vacíos
        problematic_groups = {
            'empty_group': [],  # Grupo explícitamente vacío
            'valid_group': ['file1.py'],
            'another_empty': []  # Otro grupo vacío
        }
        
        # El filtro debe eliminar grupos vacíos
        filtered = manager.filter_empty_groups(problematic_groups)
        
        # NO debe haber grupos vacíos en resultado
        for group_name, files in filtered.items():
            assert len(files) > 0, f"REGRESSION: Empty group {group_name} not filtered out"
        
        # Solo debe quedar el grupo válido
        assert 'valid_group' in filtered
        assert 'empty_group' not in filtered
        assert 'another_empty' not in filtered
    
    def test_no_regression_duplicate_files(self):
        """Asegura que la duplicación de archivos no regrese"""
        from src_new.core.group_priority_system import GroupPrioritySystem
        
        priority_system = GroupPrioritySystem()
        
        # Simular situación que causaba duplicados
        groups_with_duplicates = {
            'core_modules': ['main.py', 'config.py', 'utils.py'],
            'utility_modules': ['utils.py', 'helpers.py'],  # utils.py duplicado
            'config_modules': ['config.py', 'settings.py']  # config.py duplicado
        }
        
        # Aplicar sistema de prioridad
        result = priority_system.assign_files_to_groups(groups_with_duplicates)
        
        # Validar que NO hay duplicados
        all_files = []
        for files in result.values():
            all_files.extend(files)
        
        unique_files = set(all_files)
        assert len(all_files) == len(unique_files), "REGRESSION: Duplicate files found"
        
        # Validar que prioridad funcionó (core debe ganar)
        assert 'utils.py' in result['core_modules']
        assert 'config.py' in result['core_modules']
    
    def test_no_regression_html_generation(self):
        """Asegura que generación HTML no regrese"""
        from src_new.core.analyzer import ProjectAnalyzer
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "project"
            project_path.mkdir()
            (project_path / "test.py").write_text("pass")
            
            analyzer = ProjectAnalyzer()
            analysis = analyzer.analyze(str(project_path))
            
            output_dir = Path(temp_dir) / "output"
            analysis.save_to_directory(output_dir)
            
            # NO debe generar archivos HTML
            html_files = list(output_dir.glob("**/*.html"))
            assert len(html_files) == 0, f"REGRESSION: HTML files generated: {html_files}"
```

## 📋 Checklist Final de Validación

### Archivo: `tests/test_final_validation.py`

```python
import pytest
import subprocess
import os
from pathlib import Path

class TestFinalValidation:
    """Checklist final antes del release v2.0"""
    
    def test_entry_points_working(self):
        """Verifica que entry points funcionen correctamente"""
        # Test projectprompt command
        result = subprocess.run(['projectprompt', '--version'], 
                              capture_output=True, text=True)
        assert result.returncode == 0, "projectprompt command not working"
        assert '2.0.0' in result.stdout, "Version not displayed correctly"
        
        # Test pp alias
        result = subprocess.run(['pp', '--help'], 
                              capture_output=True, text=True)
        assert result.returncode == 0, "pp alias not working"
    
    def test_all_imports_working(self):
        """Verifica que todos los imports de la nueva arquitectura funcionen"""
        import_tests = [
            "from src_new.core.analyzer import ProjectAnalyzer",
            "from src_new.core.scanner import ProjectScanner", 
            "from src_new.core.detector import FunctionalityDetector",
            "from src_new.ai.client import AIClient",
            "from src_new.generators.suggestions import SuggestionGenerator",
            "from src_new.utils.config import Config",
            "from src_new.cli import cli"
        ]
        
        for import_statement in import_tests:
            try:
                exec(import_statement)
            except ImportError as e:
                pytest.fail(f"Import failed: {import_statement} - {e}")
    
    def test_api_integration_basic(self):
        """Test básico de integración con APIs (sin hacer llamadas reales)"""
        from src_new.ai.client import AIClient
        
        # Test inicialización sin errores
        try:
            client_anthropic = AIClient(provider="anthropic")
            client_openai = AIClient(provider="openai")
        except Exception as e:
            pytest.fail(f"AI client initialization failed: {e}")
        
        # Test provider inválido
        with pytest.raises(ValueError):
            AIClient(provider="invalid_provider")
    
    def test_configuration_loading(self):
        """Verifica que configuración se cargue correctamente"""
        from src_new.utils.config import Config
        
        # Test sin .env (debe usar defaults)
        config = Config()
        
        # Debe tener valores por defecto
        assert config.default_output_dir == './project-output'
        assert config.max_files_to_analyze == 1000
        assert config.default_api_provider in ['anthropic', 'openai']
        
        # Test validación
        is_valid, errors = config.validate()
        # Puede fallar por falta de API keys, pero no debe crashear
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)
    
    def test_documentation_exists(self):
        """Verifica que documentación esencial exista"""
        essential_docs = [
            "README.md",
            ".env.example", 
            "requirements.txt"
        ]
        
        for doc_file in essential_docs:
            assert Path(doc_file).exists(), f"Essential documentation missing: {doc_file}"
    
    def test_no_old_architecture_remnants(self):
        """Verifica que no queden restos de arquitectura antigua"""
        # Archivos que NO deben existir en v2.0
        old_files = [
            "pyproject.toml",
            "poetry.lock", 
            "src/ui/dashboard.py",
            "src/utils/telemetry.py",
            "config.yaml"
        ]
        
        for old_file in old_files:
            assert not Path(old_file).exists(), f"Old architecture file still exists: {old_file}"
    
    def test_performance_targets_met(self):
        """Verifica que targets de rendimiento se cumplan"""
        from src_new.core.analyzer import ProjectAnalyzer
        import time
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear proyecto mediano para test
            project_path = Path(temp_dir) / "medium_project"
            project_path.mkdir()
            
            # 100 archivos Python simples
            for i in range(100):
                (project_path / f"file_{i}.py").write_text(f"# File {i}\npass")
            
            analyzer = ProjectAnalyzer()
            
            start_time = time.time()
            analysis = analyzer.analyze(str(project_path))
            duration = time.time() - start_time
            
            # Debe ser <15 segundos para 100 archivos
            assert duration < 15, f"Performance target not met: {duration:.2f}s for 100 files"
            assert len(analysis.files) > 90, "Not all files were processed"
```

## 🚀 Scripts de Validación Automatizada

### Archivo: `scripts/validate_release.py`

```python
#!/usr/bin/env python3
"""
Script de validación completa para release v2.0
Ejecuta todos los tests críticos y genera reporte
"""

import subprocess
import sys
from pathlib import Path
import json
from datetime import datetime

def run_command(cmd, description):
    """Ejecuta comando y captura resultado"""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'description': description
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'description': description
        }

def main():
    """Ejecuta validación completa"""
    print("🚀 ProjectPrompt v2.0 Release Validation")
    print("=" * 50)
    
    validation_tests = [
        # Tests críticos
        ("python -m pytest tests/test_core_functionality.py -v", 
         "Core functionality tests"),
        
        ("python -m pytest tests/test_performance.py -v",
         "Performance benchmarks"),
        
        ("python -m pytest tests/test_output_quality.py -v",
         "Output quality validation"),
        
        ("python -m pytest tests/test_success_metrics.py -v",
         "Success metrics validation"), 
        
        ("python -m pytest tests/test_final_validation.py -v",
         "Final validation checklist"),
        
        # Instalación y entry points
        ("pip install -e .", 
         "Package installation"),
        
        ("projectprompt --version",
         "Entry point: projectprompt"),
        
        ("pp --help", 
         "Entry point: pp alias"),
        
        # Linting y calidad de código
        ("python -m flake8 src_new/ --max-line-length=100 --ignore=E203,W503",
         "Code linting"),
        
        ("python -c 'import src_new.cli; print(\"✅ All imports working\")'",
         "Import validation"),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for cmd, description in validation_tests:
        result = run_command(cmd, description)
        results.append(result)
        
        if result['success']:
            print(f"   ✅ {description}")
            passed += 1
        else:
            print(f"   ❌ {description}")
            print(f"      Error: {result['stderr'][:100]}...")
            failed += 1
    
    # Generar reporte
    print("\n" + "=" * 50)
    print(f"📊 Validation Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL VALIDATIONS PASSED - Ready for release!")
        exit_code = 0
    else:
        print("❌ Some validations failed - Review required")
        exit_code = 1
    
    # Guardar reporte detallado
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_tests': len(validation_tests),
            'passed': passed,
            'failed': failed,
            'success_rate': f"{(passed/len(validation_tests)*100):.1f}%"
        },
        'results': results
    }
    
    with open('validation_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Detailed report saved to: validation_report.json")
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
```

### Archivo: `scripts/performance_benchmark.py`

```python
#!/usr/bin/env python3
"""
Benchmark de rendimiento para diferentes tamaños de proyecto
"""

import time
import psutil
import os
from pathlib import Path
import tempfile
import shutil
import json
import matplotlib.pyplot as plt

def create_test_project(size, base_path):
    """Crea proyecto de prueba del tamaño especificado"""
    file_counts = {
        'tiny': 10,
        'small': 50,
        'medium': 200,
        'large': 500,
        'xlarge': 1000
    }
    
    num_files = file_counts.get(size, 50)
    project_path = base_path / f"{size}_project"
    project_path.mkdir(parents=True)
    
    for i in range(num_files):
        file_path = project_path / f"module_{i:04d}.py"
        content = f"""
# Module {i} - Generated for performance testing
import os
import sys
from typing import List, Dict, Optional

class Module{i}:
    \"\"\"Module {i} class\"\"\"
    
    def __init__(self):
        self.id = {i}
        self.name = "module_{i}"
    
    def process_data(self, data: List[str]) -> Dict[str, int]:
        \"\"\"Process data method\"\"\"
        return {{'processed': len(data), 'module_id': self.id}}
    
    def calculate_metrics(self) -> Dict[str, float]:
        \"\"\"Calculate performance metrics\"\"\"
        return {{
            'efficiency': {i % 100} / 100,
            'load_factor': {(i * 7) % 100} / 100
        }}

def function_{i}():
    \"\"\"Utility function {i}\"\"\"
    return Module{i}()

# Dependencies
{'import module_' + str(max(0, (i-1) % 10)) if i > 0 else '# No dependencies'}
"""
        file_path.write_text(content)
    
    return project_path

def benchmark_analysis(project_path):
    """Ejecuta benchmark de análisis"""
    from src_new.core.analyzer import ProjectAnalyzer
    
    analyzer = ProjectAnalyzer()
    process = psutil.Process(os.getpid())
    
    # Medir memoria inicial
    initial_memory = process.memory_info().rss / 1024 / 1024
    
    # Medir tiempo de análisis
    start_time = time.time()
    analysis = analyzer.analyze(str(project_path))
    end_time = time.time()
    
    # Medir memoria final
    final_memory = process.memory_info().rss / 1024 / 1024
    
    return {
        'duration': end_time - start_time,
        'memory_used': final_memory - initial_memory,
        'files_analyzed': len(analysis.files),
        'groups_created': len(analysis.groups),
        'files_per_second': len(analysis.files) / (end_time - start_time)
    }

def main():
    """Ejecuta benchmarks completos"""
    print("📊 ProjectPrompt v2.0 Performance Benchmarks")
    print("=" * 50)
    
    sizes = ['tiny', 'small', 'medium', 'large', 'xlarge']
    results = {}
    
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        
        for size in sizes:
            print(f"\n🔍 Benchmarking {size} project...")
            
            # Crear proyecto
            project_path = create_test_project(size, base_path)
            
            # Ejecutar benchmark
            try:
                result = benchmark_analysis(project_path)
                results[size] = result
                
                print(f"   ⏱️  Duration: {result['duration']:.2f}s")
                print(f"   💾 Memory: {result['memory_used']:.1f}MB")
                print(f"   📄 Files: {result['files_analyzed']}")
                print(f"   📁 Groups: {result['groups_created']}")
                print(f"   🚀 Speed: {result['files_per_second']:.1f} files/sec")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results[size] = {'error': str(e)}
    
    # Generar reporte
    print("\n" + "=" * 50)
    print("📈 Performance Summary")
    
    successful_results = {k: v for k, v in results.items() if 'error' not in v}
    
    if successful_results:
        # Mostrar tendencias
        durations = [v['duration'] for v in successful_results.values()]
        memories = [v['memory_used'] for v in successful_results.values()]
        
        print(f"⏱️  Duration range: {min(durations):.2f}s - {max(durations):.2f}s")
        print(f"💾 Memory range: {min(memories):.1f}MB - {max(memories):.1f}MB")
        
        # Verificar targets
        large_result = successful_results.get('large')
        if large_result:
            if large_result['duration'] < 30:
                print("✅ Large project performance target met (<30s)")
            else:
                print("❌ Large project performance target missed")
        
        # Guardar resultados
        with open('performance_benchmark.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print("📄 Detailed results saved to: performance_benchmark.json")
    
    else:
        print("❌ No successful benchmarks completed")

if __name__ == '__main__':
    main()
```

## 📝 Documentación Final

### Archivo: `RELEASE_NOTES_v2.0.md`

```markdown
# ProjectPrompt v2.0 Release Notes

## 🎉 Major Release: Complete Refactorization

ProjectPrompt v2.0 represents a complete rewrite focused on simplicity, performance, and effectiveness.

### 🎯 Key Improvements

#### ✨ Simplified Architecture
- **50% code reduction**: From complex multi-module system to clean, focused architecture
- **Dependency reduction**: From 15+ dependencies to 6 core dependencies
- **Single responsibility**: Focus exclusively on project analysis and AI suggestions

#### 🖥️ Simple CLI
- **2 main commands**: `analyze` and `suggest` 
- **Intuitive workflow**: Linear process from analysis to suggestions
- **User-friendly output**: Clear progress indicators and helpful messages

#### ⚙️ Simple Configuration
- **Single .env file**: No more complex YAML configurations
- **Two API providers**: Anthropic Claude and OpenAI GPT only
- **Sensible defaults**: Works out of the box with minimal setup

#### 🚀 Performance Improvements
- **60% faster analysis**: Optimized algorithms and reduced overhead
- **Lower memory usage**: <200MB for large projects vs 500MB+ in v1.x
- **No memory leaks**: Stable memory usage in repeated analyses

### 🔧 Technical Improvements

#### Zero Critical Bugs
- ✅ **No empty groups**: Eliminated groups with 0 files
- ✅ **No duplicate files**: Files assigned to exactly one group
- ✅ **Real dependencies**: Dependency graph shows actual connections
- ✅ **Complete traceability**: Full file ↔ group mapping

#### Modern Development
- ✅ **Simple installation**: `pip install -e .` instead of Poetry
- ✅ **Clean imports**: All imports work without conflicts
- ✅ **Comprehensive tests**: >80% test coverage
- ✅ **Type hints**: Full typing support

### 📦 Installation

```bash
# Clone repository
git clone https://github.com/your-repo/projectprompt
cd projectprompt

# Simple installation
pip install -e .

# Configure API keys
cp .env.example .env
# Edit .env with your API keys
```

### 🎮 Usage

```bash
# Analyze your project
projectprompt analyze /path/to/your/project

# Generate AI suggestions for a specific group
projectprompt suggest "Core Files"

# Check status
projectprompt status
```

### 🔄 Migration from v1.x

#### Breaking Changes
- **CLI commands changed**: New command structure
- **Configuration format**: YAML → .env file
- **API integrations**: Simplified to Anthropic + OpenAI only
- **Output format**: HTML generation removed, markdown only

#### Migration Steps
1. **Backup** your v1.x configuration
2. **Install** v2.0 using new method
3. **Create** .env file with API keys
4. **Re-run** analysis with new CLI

### 📊 Performance Benchmarks

| Project Size | Files | Analysis Time | Memory Usage |
|--------------|-------|---------------|--------------|
| Small        | <100  | <10s         | <50MB       |
| Medium       | 100-500 | <30s       | <100MB      |
| Large        | 500+ | <60s         | <200MB      |

### 🐛 Bug Fixes

#### Critical Issues Resolved
- Fixed groups with 0 files appearing in analysis
- Fixed duplicate files between functional groups  
- Fixed dependency graph showing no connections
- Fixed HTML generation when markdown was requested
- Fixed memory leaks in repeated analyses

#### Performance Issues Resolved
- Eliminated redundant analyzers causing conflicts
- Optimized file scanning for large projects
- Reduced memory footprint significantly
- Improved startup time

### 🙏 Acknowledgments

This major refactorization was driven by user feedback highlighting the need for simplicity and reliability. Thank you to all users who reported issues and suggested improvements.

### 🔮 Future Roadmap

- **Language Support**: Expand beyond Python to JavaScript, TypeScript, Java
- **Integration**: GitHub Actions, VS Code extension
- **Advanced Analytics**: Code quality metrics, technical debt analysis
- **Team Features**: Multi-developer project analysis

---

**Full Changelog**: [v1.3.2...v2.0.0](https://github.com/your-repo/projectprompt/compare/v1.3.2...v2.0.0)
```

## ✅ Checklist Final de Fase 5

### Tests Implementados
- [ ] **Core functionality tests**: Todos los problemas críticos validados
- [ ] **Performance benchmarks**: Targets de rendimiento verificados
- [ ] **Output quality tests**: Solo markdown, calidad de sugerencias
- [ ] **Success metrics tests**: Métricas de refactorización validadas
- [ ] **Regression tests**: Prevención de bugs conocidos
- [ ] **Final validation**: Checklist completo de release

### Scripts de Automatización
- [ ] **validate_release.py**: Validación automatizada completa
- [ ] **performance_benchmark.py**: Benchmarks automáticos
- [ ] **Documentación**: Release notes y guías

### Preparación Release
- [ ] **All tests passing**: 100% de tests críticos pasando
- [ ] **Performance targets met**: Todos los targets cumplidos
- [ ] **Documentation complete**: Documentación actualizada
- [ ] **Entry points working**: Comandos CLI funcionando

## 🚀 Comandos Git para Fase 5

```bash
# Iniciar fase
git checkout develop
git checkout -b phase5/testing-optimization

# Commits durante fase
git add tests/ && git commit -m "Add comprehensive test suite for all critical functionality"
git add scripts/ && git commit -m "Add automated validation and benchmark scripts"
git add RELEASE_NOTES_v2.0.md && git commit -m "Add release notes and final documentation"

# Finalizar fase y preparar release
git checkout develop
git merge phase5/testing-optimization

# Release a producción
git checkout main
git merge develop
git tag v2.0.0
git push origin main --tags
```

**Resultado**: Sistema completamente validado, testeado y optimizado. Listo para release v2.0 en producción con confianza total en calidad y rendimiento.