# Fase 4: Simplificación CLI
**Branch**: `phase4/cli-simplification`  
**Duración**: 1 semana  
**Objetivo**: CLI simple con solo 2 comandos principales y configuración .env

## 🎯 Objetivos de la Fase
- Implementar CLI con solo 2 comandos: `analyze` y `suggest`
- Configuración simple con archivo .env únicamente
- UX intuitiva con flujo lineal
- Eliminación completa de menús y wizards
- Entry points funcionando: `projectprompt` y `pp`

## 🖥️ Nuevo CLI Principal

### Archivo: `src_new/cli.py`

```python
import click
import os
from pathlib import Path
from typing import Optional

from .core.analyzer import ProjectAnalyzer
from .generators.suggestions import SuggestionGenerator
from .utils.config import Config
from .core.group_manager import GroupManager

# Configuración global
config = Config()

@click.group()
@click.version_option(version="2.0.0")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def cli(verbose: bool):
    """
    ProjectPrompt v2.0 - Simple project analysis and AI suggestions
    
    🎯 Usage:
      1. projectprompt analyze /path/to/project
      2. projectprompt suggest "Group Name"
    
    📖 Documentation: https://github.com/your-repo/projectprompt
    """
    if verbose:
        click.echo("🔧 Verbose mode enabled")

@cli.command()
@click.argument('path', type=click.Path(exists=True), default='.')
@click.option('--output', '-o', 
              default=None, 
              help='Output directory (default: ./project-output)')
@click.option('--max-files', '-m', 
              default=None, 
              type=int,
              help='Maximum files to analyze (default: 1000)')
@click.option('--exclude', '-e', 
              multiple=True,
              help='Patterns to exclude (can be used multiple times)')
def analyze(path: str, output: Optional[str], max_files: Optional[int], exclude: tuple):
    """
    Analyze project structure and create functional groups.
    
    This command scans your project, identifies functional groups,
    and prepares data for AI-powered suggestions.
    
    Examples:
      projectprompt analyze .
      projectprompt analyze /path/to/project --output ./analysis
      projectprompt analyze . --max-files 500 --exclude "*.log" --exclude "node_modules"
    """
    
    # Configurar parámetros con defaults
    output_dir = output or config.default_output_dir
    max_files_limit = max_files or config.max_files_to_analyze
    
    # Validar configuración
    if not _validate_config():
        return
    
    # Inicializar analizador
    analyzer = ProjectAnalyzer()
    group_manager = GroupManager()
    
    # Mostrar información inicial
    click.echo(f"🔍 Analyzing project: {Path(path).absolute()}")
    click.echo(f"📁 Output directory: {output_dir}")
    click.echo(f"📊 Max files to analyze: {max_files_limit}")
    
    if exclude:
        click.echo(f"🚫 Excluding patterns: {', '.join(exclude)}")
    
    try:
        # Realizar análisis
        with click.progressbar(length=100, label='Analyzing project') as bar:
            bar.update(20)
            
            # Escanear archivos
            analysis = analyzer.analyze(
                path, 
                max_files=max_files_limit,
                exclude_patterns=list(exclude)
            )
            bar.update(40)
            
            # Procesar grupos
            clean_groups = group_manager.create_groups(analysis.files)
            analysis.groups = clean_groups
            bar.update(30)
            
            # Guardar resultados
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            analysis.save_to_directory(output_path)
            bar.update(10)
        
        # Mostrar resultados
        click.echo(f"✅ Analysis complete! Results saved to: {output_path}")
        click.echo(f"📊 Found {len(analysis.groups)} functional groups:")
        
        # Tabla de grupos
        _display_groups_table(analysis.groups)
        
        # Próximos pasos
        click.echo("\n🚀 Next steps:")
        click.echo("   Choose a group to analyze with AI:")
        
        for group_name in analysis.groups.keys():
            click.echo(f"   • projectprompt suggest \"{group_name}\"")
            
    except Exception as e:
        click.echo(f"❌ Error during analysis: {str(e)}", err=True)
        raise click.ClickException(f"Analysis failed: {str(e)}")

@cli.command()
@click.argument('group_name')
@click.option('--analysis-dir', '-a', 
              default=None,
              help='Analysis directory (default: ./project-output)')
@click.option('--api', '-p',
              default=None,
              type=click.Choice(['anthropic', 'openai']),
              help='AI API provider (default: from config)')
@click.option('--detail-level', '-d',
              default='medium',
              type=click.Choice(['basic', 'medium', 'detailed']),
              help='Detail level for suggestions')
@click.option('--save-prompt', '-s',
              is_flag=True,
              help='Save the generated prompt to file')
def suggest(group_name: str, analysis_dir: Optional[str], api: Optional[str], 
           detail_level: str, save_prompt: bool):
    """
    Generate AI-powered suggestions for a specific functional group.
    
    This command takes a previously analyzed group and generates
    contextualized suggestions using AI APIs.
    
    Examples:
      projectprompt suggest "Core Files"
      projectprompt suggest "UI Components" --api openai --detail-level detailed
      projectprompt suggest "Utils" --save-prompt
    """
    
    # Configurar parámetros
    analysis_path = Path(analysis_dir or config.default_output_dir)
    api_provider = api or config.default_api_provider
    
    # Validar que existe análisis previo
    if not analysis_path.exists():
        click.echo("❌ Analysis directory not found.", err=True)
        click.echo("💡 Run 'projectprompt analyze' first to create analysis data.")
        return
    
    # Validar configuración de API
    if not _validate_api_config(api_provider):
        return
    
    # Verificar que el grupo existe
    available_groups = _load_available_groups(analysis_path)
    if group_name not in available_groups:
        click.echo(f"❌ Group '{group_name}' not found.", err=True)
        click.echo(f"📋 Available groups: {', '.join(available_groups)}")
        return
    
    # Inicializar generador
    generator = SuggestionGenerator(api_provider=api_provider)
    
    click.echo(f"🤖 Generating suggestions for group: {group_name}")
    click.echo(f"🔧 Using API: {api_provider} (detail level: {detail_level})")
    
    try:
        with click.progressbar(length=100, label='Generating suggestions') as bar:
            bar.update(20)
            
            # Cargar contexto del grupo
            group_context = generator.load_group_context(group_name, analysis_path)
            bar.update(30)
            
            # Generar prompt contextualizado
            prompt = generator.create_contextual_prompt(group_context, detail_level)
            bar.update(20)
            
            # Generar sugerencias con IA
            suggestions = generator.generate_suggestions(prompt, group_context)
            bar.update(20)
            
            # Guardar resultados
            suggestions_file = analysis_path / "suggestions" / f"{_sanitize_filename(group_name)}-suggestions.md"
            suggestions_file.parent.mkdir(parents=True, exist_ok=True)
            suggestions_file.write_text(suggestions, encoding='utf-8')
            
            # Guardar prompt si se solicita
            if save_prompt:
                prompt_file = analysis_path / "prompts" / f"{_sanitize_filename(group_name)}-prompt.md"
                prompt_file.parent.mkdir(parents=True, exist_ok=True)
                prompt_file.write_text(prompt, encoding='utf-8')
                click.echo(f"💾 Prompt saved to: {prompt_file}")
            
            bar.update(10)
        
        # Mostrar resultados
        click.echo(f"✅ Suggestions generated: {suggestions_file}")
        click.echo(f"📄 {len(suggestions.split('\\n'))} lines of suggestions created")
        
        # Mostrar preview de sugerencias
        _display_suggestions_preview(suggestions)
        
    except Exception as e:
        click.echo(f"❌ Error generating suggestions: {str(e)}", err=True)
        raise click.ClickException(f"Suggestion generation failed: {str(e)}")

# Comandos de utilidad adicionales

@cli.command()
@click.option('--analysis-dir', '-a', 
              default=None,
              help='Analysis directory to check')
def status(analysis_dir: Optional[str]):
    """Show current analysis status and available groups."""
    
    analysis_path = Path(analysis_dir or config.default_output_dir)
    
    if not analysis_path.exists():
        click.echo("📭 No analysis found. Run 'projectprompt analyze' first.")
        return
    
    # Cargar información de estado
    available_groups = _load_available_groups(analysis_path)
    suggestions_dir = analysis_path / "suggestions"
    
    click.echo(f"📊 Analysis Status for: {analysis_path}")
    click.echo("=" * 50)
    
    # Grupos disponibles
    click.echo(f"📁 Available groups ({len(available_groups)}):")
    for group in available_groups:
        click.echo(f"   • {group}")
    
    # Sugerencias generadas
    if suggestions_dir.exists():
        suggestion_files = list(suggestions_dir.glob("*-suggestions.md"))
        click.echo(f"\\n🤖 Generated suggestions ({len(suggestion_files)}):")
        for file in suggestion_files:
            group_name = file.stem.replace("-suggestions", "")
            click.echo(f"   • {group_name}: {file}")
    else:
        click.echo("\\n🤖 No suggestions generated yet.")
    
    click.echo("\\n🚀 Next actions:")
    if available_groups:
        click.echo("   Generate suggestions with:")
        for group in available_groups[:3]:  # Mostrar solo primeros 3
            click.echo(f"   • projectprompt suggest \"{group}\"")

@cli.command()
@click.option('--analysis-dir', '-a',
              default=None, 
              help='Analysis directory to clean')
@click.confirmation_option(prompt='Are you sure you want to delete analysis data?')
def clean(analysis_dir: Optional[str]):
    """Clean analysis data and start fresh."""
    
    analysis_path = Path(analysis_dir or config.default_output_dir)
    
    if analysis_path.exists():
        import shutil
        shutil.rmtree(analysis_path)
        click.echo(f"🧹 Cleaned analysis directory: {analysis_path}")
    else:
        click.echo("📭 No analysis directory found to clean.")

# Funciones auxiliares

def _validate_config() -> bool:
    """Valida configuración básica"""
    try:
        # Verificar que al menos una API key está disponible
        has_anthropic = bool(config.anthropic_api_key)
        has_openai = bool(config.openai_api_key)
        
        if not has_anthropic and not has_openai:
            click.echo("❌ No API keys found.", err=True)
            click.echo("💡 Please set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env file")
            return False
            
        return True
        
    except Exception as e:
        click.echo(f"❌ Configuration error: {str(e)}", err=True)
        return False

def _validate_api_config(provider: str) -> bool:
    """Valida configuración específica de API"""
    try:
        if provider == "anthropic":
            config.anthropic_api_key  # Esto lanzará error si no existe
        elif provider == "openai":
            config.openai_api_key  # Esto lanzará error si no existe
        return True
    except ValueError as e:
        click.echo(f"❌ API configuration error: {str(e)}", err=True)
        click.echo("💡 Please check your .env file configuration")
        return False

def _display_groups_table(groups: dict):
    """Muestra tabla formateada de grupos"""
    click.echo()
    click.echo("┌─────────────────────────────┬───────────┐")
    click.echo("│ Group Name                  │ Files     │")
    click.echo("├─────────────────────────────┼───────────┤")
    
    for group_name, files in groups.items():
        # Truncar nombre si es muy largo
        display_name = group_name[:27] + "..." if len(group_name) > 30 else group_name
        click.echo(f"│ {display_name:<27} │ {len(files):>9} │")
    
    click.echo("└─────────────────────────────┴───────────┘")

def _display_suggestions_preview(suggestions: str):
    """Muestra preview de las sugerencias generadas"""
    lines = suggestions.split('\\n')
    preview_lines = lines[:10]  # Primeras 10 líneas
    
    click.echo("\\n📋 Suggestions preview:")
    click.echo("─" * 40)
    for line in preview_lines:
        if line.strip():
            # Truncar líneas muy largas
            display_line = line[:75] + "..." if len(line) > 75 else line
            click.echo(display_line)
    
    if len(lines) > 10:
        click.echo("...")
        click.echo(f"({len(lines) - 10} more lines in full file)")

def _load_available_groups(analysis_path: Path) -> list:
    """Carga grupos disponibles desde análisis previo"""
    # Implementar carga desde archivos de análisis
    groups_file = analysis_path / "groups.json"
    if groups_file.exists():
        import json
        with open(groups_file) as f:
            data = json.load(f)
            return list(data.get('groups', {}).keys())
    return []

def _sanitize_filename(name: str) -> str:
    """Convierte nombre de grupo a filename válido"""
    import re
    # Reemplazar espacios y caracteres especiales
    sanitized = re.sub(r'[^\w\s-]', '', name)
    sanitized = re.sub(r'[-\s]+', '-', sanitized)
    return sanitized.lower().strip('-')

def main():
    """Entry point principal para CLI"""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n👋 Operation cancelled by user")
    except Exception as e:
        click.echo(f"💥 Unexpected error: {str(e)}", err=True)
        raise

if __name__ == '__main__':
    main()
```

## 🔧 Configuración Simplificada

### Archivo: `src_new/utils/config.py`

```python
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

class Config:
    """Configuración simple basada exclusivamente en .env"""
    
    def __init__(self, env_file: Optional[Path] = None):
        # Buscar .env en múltiples ubicaciones
        env_paths = [
            env_file,
            Path.cwd() / '.env',
            Path.home() / '.projectprompt' / '.env',
            Path(__file__).parent.parent.parent / '.env'
        ]
        
        for env_path in env_paths:
            if env_path and env_path.exists():
                load_dotenv(env_path)
                self.env_file_used = env_path
                break
        else:
            self.env_file_used = None
    
    @property
    def anthropic_api_key(self) -> str:
        """API key para Anthropic Claude"""
        key = os.getenv('ANTHROPIC_API_KEY', '').strip()
        if not key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. "
                "Please set it in your .env file or environment variables."
            )
        return key
    
    @property 
    def openai_api_key(self) -> str:
        """API key para OpenAI GPT"""
        key = os.getenv('OPENAI_API_KEY', '').strip()
        if not key:
            raise ValueError(
                "OPENAI_API_KEY not found. "
                "Please set it in your .env file or environment variables."
            )
        return key
    
    @property
    def default_output_dir(self) -> str:
        """Directorio por defecto para outputs"""
        return os.getenv('DEFAULT_OUTPUT_DIR', './project-output')
    
    @property
    def max_files_to_analyze(self) -> int:
        """Máximo número de archivos a analizar"""
        try:
            return int(os.getenv('MAX_FILES_TO_ANALYZE', '1000'))
        except ValueError:
            return 1000
    
    @property
    def default_api_provider(self) -> str:
        """Proveedor de API por defecto"""
        provider = os.getenv('DEFAULT_API_PROVIDER', 'anthropic').lower()
        if provider not in ['anthropic', 'openai']:
            return 'anthropic'
        return provider
    
    @property
    def exclude_patterns(self) -> list:
        """Patrones de archivos/directorios a excluir"""
        patterns = os.getenv('EXCLUDE_PATTERNS', '')
        if patterns:
            return [p.strip() for p in patterns.split(',') if p.strip()]
        return [
            '*.pyc', '*.pyo', '*.pyd', '__pycache__',
            '.git', '.svn', '.hg', '.pytest_cache',
            'node_modules', '.venv', 'venv', '.env'
        ]
    
    def validate(self) -> tuple[bool, list]:
        """Valida configuración completa"""
        errors = []
        
        # Verificar que al menos una API key existe
        has_anthropic = False
        has_openai = False
        
        try:
            self.anthropic_api_key
            has_anthropic = True
        except ValueError:
            pass
        
        try:
            self.openai_api_key
            has_openai = True
        except ValueError:
            pass
        
        if not has_anthropic and not has_openai:
            errors.append("No API keys found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY.")
        
        # Verificar directorio de output
        output_dir = Path(self.default_output_dir)
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create output directory {output_dir}: {e}")
        
        return len(errors) == 0, errors
    
    def get_config_info(self) -> dict:
        """Información de configuración para debugging"""
        return {
            'env_file_used': str(self.env_file_used) if self.env_file_used else 'None',
            'has_anthropic_key': bool(os.getenv('ANTHROPIC_API_KEY')),
            'has_openai_key': bool(os.getenv('OPENAI_API_KEY')),
            'default_output_dir': self.default_output_dir,
            'max_files_to_analyze': self.max_files_to_analyze,
            'default_api_provider': self.default_api_provider,
            'exclude_patterns_count': len(self.exclude_patterns)
        }
```

### Archivo: `.env.example`

```bash
# ProjectPrompt v2.0 Configuration
# Copy this file to .env and fill in your API keys

# =============================================================================
# AI API KEYS (At least one required)
# =============================================================================

# Anthropic Claude API Key
# Get from: https://console.anthropic.com/
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# OpenAI GPT API Key  
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# =============================================================================
# OPTIONAL CONFIGURATION
# =============================================================================

# Default output directory for analysis results
DEFAULT_OUTPUT_DIR=./project-output

# Maximum number of files to analyze (prevents very large projects from consuming too many tokens)
MAX_FILES_TO_ANALYZE=1000

# Default AI provider to use (anthropic or openai)
DEFAULT_API_PROVIDER=anthropic

# Comma-separated patterns to exclude from analysis
EXCLUDE_PATTERNS=*.log,*.tmp,node_modules,__pycache__,.git,.venv

# =============================================================================
# ADVANCED OPTIONS (Usually not needed)
# =============================================================================

# Enable debug mode (more verbose logging)
# DEBUG=true

# Custom API endpoints (for testing)
# ANTHROPIC_API_BASE=https://api.anthropic.com
# OPENAI_API_BASE=https://api.openai.com
```

## 🧪 Testing de CLI

### Archivo: `tests/test_cli.py`

```python
import pytest
from click.testing import CliRunner
from pathlib import Path
import json
import os

from src_new.cli import cli

class TestCLI:
    
    def setup_method(self):
        """Setup para cada test"""
        self.runner = CliRunner()
        
    def test_analyze_command_basic(self):
        """Test básico del comando analyze"""
        with self.runner.isolated_filesystem():
            # Crear proyecto de prueba
            os.mkdir('test_project')
            with open('test_project/main.py', 'w') as f:
                f.write('import sys\nprint("Hello")')
            
            # Configurar API key de prueba
            with open('.env', 'w') as f:
                f.write('ANTHROPIC_API_KEY=test_key\n')
            
            # Ejecutar análisis
            result = self.runner.invoke(cli, ['analyze', 'test_project'])
            
            # Verificaciones
            assert result.exit_code == 0
            assert '✅ Analysis complete' in result.output
            assert Path('project-output').exists()
    
    def test_suggest_command_without_analysis(self):
        """Test comando suggest sin análisis previo"""
        with self.runner.isolated_filesystem():
            # Configurar API key
            with open('.env', 'w') as f:
                f.write('ANTHROPIC_API_KEY=test_key\n')
            
            result = self.runner.invoke(cli, ['suggest', 'core'])
            
            assert result.exit_code == 0
            assert '❌ Analysis directory not found' in result.output
    
    def test_status_command(self):
        """Test comando status"""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ['status'])
            
            assert result.exit_code == 0
            assert '📭 No analysis found' in result.output
    
    def test_cli_version(self):
        """Test que version se muestra correctamente"""
        result = self.runner.invoke(cli, ['--version'])
        
        assert result.exit_code == 0
        assert '2.0.0' in result.output
    
    def test_analyze_with_options(self):
        """Test analyze con opciones adicionales"""
        with self.runner.isolated_filesystem():
            # Setup
            os.mkdir('test_project')
            with open('test_project/main.py', 'w') as f:
                f.write('print("test")')
            with open('.env', 'w') as f:
                f.write('ANTHROPIC_API_KEY=test_key\n')
            
            # Test con opciones
            result = self.runner.invoke(cli, [
                'analyze', 'test_project',
                '--output', './custom_output',
                '--max-files', '100',
                '--exclude', '*.log'
            ])
            
            assert result.exit_code == 0
            assert Path('custom_output').exists()
```

## ⚙️ Integración con Nueva Arquitectura

### Archivo: `src_new/generators/suggestions.py`

```python
from typing import Dict, Any
from pathlib import Path
import json

from ..ai.client import AIClient
from ..utils.config import Config

class SuggestionGenerator:
    """Generador de sugerencias usando IA"""
    
    def __init__(self, api_provider: str = "anthropic"):
        self.config = Config()
        self.ai_client = AIClient(provider=api_provider)
        self.api_provider = api_provider
    
    def load_group_context(self, group_name: str, analysis_dir: Path) -> Dict[str, Any]:
        """Carga contexto del grupo desde análisis previo"""
        
        # Cargar información del grupo
        groups_file = analysis_dir / "groups.json"
        if not groups_file.exists():
            raise FileNotFoundError(f"Groups file not found: {groups_file}")
        
        with open(groups_file) as f:
            groups_data = json.load(f)
        
        if group_name not in groups_data.get('groups', {}):
            raise ValueError(f"Group '{group_name}' not found in analysis")
        
        group_info = groups_data['groups'][group_name]
        
        # Cargar contexto adicional
        context = {
            'group_name': group_name,
            'group_info': group_info,
            'project_context': groups_data.get('project_context', {}),
            'dependencies': self._load_group_dependencies(group_name, analysis_dir),
            'tech_stack': self._detect_tech_stack(group_info)
        }
        
        return context
    
    def create_contextual_prompt(self, group_context: Dict[str, Any], detail_level: str) -> str:
        """Crea prompt contextualizado para el grupo específico"""
        
        group_name = group_context['group_name']
        files = group_context['group_info'].get('files', [])
        tech_stack = group_context['tech_stack']
        
        prompt = f"""I am working on improving a software project and need specific suggestions for the "{group_name}" functional group.

## Project Context
- **Group**: {group_name}
- **Files in group**: {len(files)} files
- **Technology stack**: {', '.join(tech_stack)}
- **Detail level requested**: {detail_level}

## Files in this group:
"""
        
        for file_path in files[:10]:  # Limitar a 10 archivos para no saturar prompt
            prompt += f"- {file_path}\n"
        
        if len(files) > 10:
            prompt += f"... and {len(files) - 10} more files\n"
        
        prompt += f"""
## Dependencies
{self._format_dependencies(group_context.get('dependencies', {}))}

## What I need:
Please provide specific, actionable suggestions for improving this functional group. Focus on:

1. **Code Structure**: How to better organize the files in this group
2. **Functionality Enhancement**: What features or improvements could be added
3. **Code Quality**: Specific improvements for maintainability and readability
4. **Integration**: How this group could better integrate with the rest of the project
5. **Implementation Steps**: Concrete next steps I can take

## Output Format:
Please structure your response as a detailed markdown document with:
- Clear headers for each suggestion category
- Specific file names and code examples where relevant
- Prioritized action items
- Estimated implementation effort for each suggestion

Make your suggestions specific to this exact group and the files it contains. Avoid generic advice.
"""
        
        return prompt
    
    def generate_suggestions(self, prompt: str, group_context: Dict[str, Any]) -> str:
        """Genera sugerencias usando IA"""
        
        try:
            suggestions = self.ai_client.generate_suggestions(prompt, group_context)
            
            # Añadir metadata al final
            metadata = f"""

---

## Generation Metadata
- **Generated by**: ProjectPrompt v2.0
- **API Provider**: {self.api_provider}
- **Group**: {group_context['group_name']}
- **Files analyzed**: {len(group_context['group_info'].get('files', []))}
- **Generated at**: {self._get_timestamp()}
"""
            
            return suggestions + metadata
            
        except Exception as e:
            raise Exception(f"Failed to generate suggestions: {str(e)}")
    
    def _load_group_dependencies(self, group_name: str, analysis_dir: Path) -> Dict:
        """Carga dependencias específicas del grupo"""
        deps_file = analysis_dir / "dependencies.json"
        if deps_file.exists():
            with open(deps_file) as f:
                all_deps = json.load(f)
                return all_deps.get('groups', {}).get(group_name, {})
        return {}
    
    def _detect_tech_stack(self, group_info: Dict) -> list:
        """Detecta stack tecnológico basado en archivos del grupo"""
        files = group_info.get('files', [])
        tech_stack = set()
        
        for file_path in files:
            ext = Path(file_path).suffix.lower()
            
            if ext in ['.py']:
                tech_stack.add('Python')
            elif ext in ['.js', '.jsx']:
                tech_stack.add('JavaScript')
            elif ext in ['.ts', '.tsx']:
                tech_stack.add('TypeScript')
            elif ext in ['.java']:
                tech_stack.add('Java')
            elif ext in ['.cpp', '.c', '.h']:
                tech_stack.add('C/C++')
            elif ext in ['.rs']:
                tech_stack.add('Rust')
            elif ext in ['.go']:
                tech_stack.add('Go')
        
        return list(tech_stack) if tech_stack else ['Unknown']
    
    def _format_dependencies(self, dependencies: Dict) -> str:
        """Formatea dependencias para incluir en prompt"""
        if not dependencies:
            return "No specific dependencies identified for this group."
        
        formatted = ""
        if 'internal' in dependencies:
            formatted += f"**Internal dependencies**: {len(dependencies['internal'])} connections\n"
        if 'external' in dependencies:
            formatted += f"**External dependencies**: {len(dependencies['external'])} libraries\n"
        
        return formatted
    
    def _get_timestamp(self) -> str:
        """Obtiene timestamp actual"""
        from datetime import datetime
        return datetime.now().isoformat()
```

## ✅ Validación de Fase 4

### Checklist de Funcionalidades
- [ ] CLI con solo 2 comandos principales (`analyze`, `suggest`)
- [ ] Comandos auxiliares útiles (`status`, `clean`)
- [ ] Configuración .env simple y robusta
- [ ] Entry points funcionando (`projectprompt`, `pp`)
- [ ] UX intuitiva con progress bars y mensajes claros
- [ ] Manejo de errores graceful
- [ ] Integración con nueva arquitectura de Fases 1-3

### Tests de Aceptación
```bash
# Instalación
pip install -e .

# Entry points funcionan
projectprompt --version
pp --help

# Flujo completo
projectprompt analyze .
projectprompt suggest "Core Files"
projectprompt status
```

## 🚀 Comandos Git para Fase 4

```bash
# Iniciar fase
git checkout develop
git checkout -b phase4/cli-simplification

# Commits durante fase
git add src_new/cli.py && git commit -m "Implement main CLI with analyze and suggest commands"
git add src_new/utils/config.py && git commit -m "Create simple .env-based configuration system"
git add .env.example && git commit -m "Add comprehensive .env.example"
git add src_new/generators/suggestions.py && git commit -m "Implement AI suggestion generator"
git add tests/test_cli.py && git commit -m "Add CLI tests"

# Finalizar fase
git checkout develop
git merge phase4/cli-simplification
```

**Resultado**: CLI simple y funcional, configuración .env, UX intuitiva, integración completa con arquitectura de fases anteriores, listo para testing final en Fase 5.