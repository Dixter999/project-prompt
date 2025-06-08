#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ProjectPrompt v2.0 - Simplified CLI
Simple project analysis and AI suggestions

Phase 4: Simplified CLI with only 2 main commands
"""

import click
import os
from pathlib import Path
from typing import Optional
import json
import shutil

from .core.analyzer import ProjectAnalyzer
from .generators.suggestions import SuggestionGenerator
from .utils.config import Config

# Global configuration
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
              help='Output directory (default: ./project-prompt-output)')
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
      projectprompt analyze /path/to/project --output ./project-prompt-output
      projectprompt analyze . --max-files 500 --exclude "*.log" --exclude "node_modules"
    """
    
    # Configure parameters with defaults
    if output:
        output_dir = output
    else:
        # Use project-prompt-output as default instead of project directory
        output_dir = str(Path(path) / "project-prompt-output")
    max_files_limit = max_files or min(config.max_files_to_analyze, 100)  # Limit for testing
    
    # Show initial information
    click.echo(f"🔍 Analyzing project: {Path(path).absolute()}")
    click.echo(f"📁 Output directory: {output_dir}")
    click.echo(f"📊 Max files to analyze: {max_files_limit}")
    
    if exclude:
        click.echo(f"🚫 Excluding patterns: {', '.join(exclude)}")
    
    try:
        # Perform analysis
        with click.progressbar(length=100, label='Analyzing project') as bar:
            bar.update(30)
            
            # Create scan config with limits
            from .models.project import ScanConfig
            scan_config = ScanConfig(max_files=max_files_limit)
            
            # Analyze project (includes scanning, grouping and validation)
            analyzer = ProjectAnalyzer(scan_config=scan_config)
            output_path = Path(output_dir)
            analysis = analyzer.analyze_project(Path(path), output_dir=output_path)
            bar.update(70)
        
        # Show results
        click.echo(f"✅ Analysis complete! Results saved to: {output_path}")
        click.echo(f"📊 Found {len(analysis.get('functional_groups', {}))} functional groups:")
        
        # Groups table
        _display_groups_table(analysis.get('functional_groups', {}))
        
        # Next steps
        click.echo("\n🚀 Next steps:")
        click.echo("   Choose a group to analyze with AI:")
        
        functional_groups = analysis.get('functional_groups', {})
        for group_name in functional_groups.keys():
            click.echo(f"   • projectprompt suggest \"{group_name}\"")
            
    except Exception as e:
        click.echo(f"❌ Error during analysis: {str(e)}", err=True)
        raise click.ClickException(f"Analysis failed: {str(e)}")

@cli.command()
@click.argument('group_name')
@click.option('--analysis-dir', '-a', 
              default=None,
              help='Analysis directory (default: ./project-prompt-output)')
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
              help='Save the created prompt to file')
@click.option('--test-mode', '-t',
              is_flag=True,
              help='Run in test mode without making API calls')
def suggest(group_name: str, analysis_dir: Optional[str], api: Optional[str], 
           detail_level: str, save_prompt: bool, test_mode: bool):
    """
    Create AI-powered suggestions for a specific functional group.
    
    This command takes a previously analyzed group and creates
    contextualized suggestions using AI APIs.
    
    Examples:
      projectprompt suggest "Core Files"
      projectprompt suggest "UI Components" --api openai --detail-level detailed
      projectprompt suggest "Utils" --save-prompt
    """
    
    # Configure parameters
    analysis_path = Path(analysis_dir) if analysis_dir else Path('./project-prompt-output')
    api_provider = api or config.default_api_provider
    
    # Validate that previous analysis exists
    if not analysis_path.exists():
        click.echo("❌ Analysis directory not found.", err=True)
        click.echo("💡 Run 'projectprompt analyze' first to create analysis data.")
        return
    
    # Validate API configuration
    if not _validate_api_config(api_provider):
        return
    
    # Verify that the group exists
    available_groups = _load_available_groups(analysis_path)
    if group_name not in available_groups:
        click.echo(f"❌ Group '{group_name}' not found.", err=True)
        click.echo(f"📋 Available groups: {', '.join(available_groups)}")
        return
    
    # Initialize generator
    use_test_mode = test_mode or not config.has_any_api_key()
    generator = SuggestionGenerator(api_provider=api_provider, test_mode=use_test_mode)
    
    click.echo(f"🤖 Generating suggestions for group: {group_name}")
    click.echo(f"🔧 Using API: {api_provider} (detail level: {detail_level})")
    if use_test_mode:
        click.echo("🧪 Running in test mode - no API calls will be made")
    
    try:
        with click.progressbar(length=100, label='Generating suggestions') as bar:
            bar.update(20)
            
            # Load group context
            group_context = generator.load_group_context(group_name, analysis_path)
            bar.update(30)
            
            # Generate contextualized prompt
            prompt = generator.create_contextual_prompt(group_context, detail_level)
            bar.update(20)
            
            # Generate suggestions with AI
            suggestions = generator.generate_suggestions(prompt, group_context)
            bar.update(20)
            
            # Save results
            suggestions_file = analysis_path / "suggestions" / f"{_sanitize_filename(group_name)}-suggestions.md"
            suggestions_file.parent.mkdir(parents=True, exist_ok=True)
            suggestions_file.write_text(suggestions, encoding='utf-8')
            
            # Save prompt if requested
            if save_prompt:
                prompt_file = analysis_path / "prompts" / f"{_sanitize_filename(group_name)}-prompt.md"
                prompt_file.parent.mkdir(parents=True, exist_ok=True)
                prompt_file.write_text(prompt, encoding='utf-8')
                click.echo(f"💾 Prompt saved to: {prompt_file}")
            
            bar.update(10)
        
        # Show results
        click.echo(f"✅ Suggestions created: {suggestions_file}")
        newline_char = '\n'
        click.echo(f"📄 {len(suggestions.split(newline_char))} lines of suggestions created")
        
        # Show suggestions preview
        _display_suggestions_preview(suggestions)
        
    except Exception as e:
        click.echo(f"❌ Error generating suggestions: {str(e)}", err=True)
        raise click.ClickException(f"Suggestion generation failed: {str(e)}")

# Additional utility commands

@cli.command()
@click.option('--analysis-dir', '-a', 
              default=None,
              help='Analysis directory to check')
def status(analysis_dir: Optional[str]):
    """Show current analysis status and available groups."""
    
    analysis_path = Path(analysis_dir) if analysis_dir else Path('./project-prompt-output')
    
    if not analysis_path.exists():
        click.echo("📭 No analysis found. Run 'projectprompt analyze' first.")
        return
    
    # Load status information
    available_groups = _load_available_groups(analysis_path)
    suggestions_dir = analysis_path / "suggestions"
    
    click.echo(f"📊 Analysis Status for: {analysis_path}")
    click.echo("=" * 50)
    
    # Available groups
    click.echo(f"📁 Available groups ({len(available_groups)}):")
    for group in available_groups:
        click.echo(f"   • {group}")
    
    # Generated suggestions
    if suggestions_dir.exists():
        suggestion_files = list(suggestions_dir.glob("*-suggestions.md"))
        click.echo(f"\n🤖 Created suggestions ({len(suggestion_files)}):")
        for file in suggestion_files:
            group_name = file.stem.replace("-suggestions", "")
            click.echo(f"   • {group_name}: {file}")
    else:
        click.echo("\n🤖 No suggestions created yet.")
    
    click.echo("\n🚀 Next actions:")
    if available_groups:
        click.echo("   Create suggestions with:")
        for group in available_groups[:3]:  # Show only first 3
            click.echo(f"   • projectprompt suggest \"{group}\"")

@cli.command()
@click.option('--analysis-dir', '-a',
              default=None, 
              help='Analysis directory to clean')
@click.confirmation_option(prompt='Are you sure you want to delete analysis data?')
def clean(analysis_dir: Optional[str]):
    """Clean analysis data and start fresh."""
    
    analysis_path = Path(analysis_dir) if analysis_dir else Path('./project-prompt-output')
    
    if analysis_path.exists():
        shutil.rmtree(analysis_path)
        click.echo(f"🧹 Cleaned analysis directory: {analysis_path}")
    else:
        click.echo("📭 No analysis directory found to clean.")

# Helper functions

def _validate_config() -> bool:
    """Validate basic configuration"""
    try:
        # Check that at least one API key is available
        if not config.has_any_api_key():
            click.echo("❌ No API keys found.", err=True)
            click.echo("💡 Please set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env file")
            return False
            
        return True
        
    except Exception as e:
        click.echo(f"❌ Configuration error: {str(e)}", err=True)
        return False

def _validate_api_config(provider: str) -> bool:
    """Validate specific API configuration"""
    try:
        if provider == "anthropic":
            if not config.has_anthropic_key():
                click.echo("⚠️  Anthropic API key not found - running in test mode.", err=False)
                click.echo("💡 Set ANTHROPIC_API_KEY in .env file for full functionality")
                return True  # Allow test mode
        elif provider == "openai":
            if not config.has_openai_key():
                click.echo("⚠️  OpenAI API key not found - running in test mode.", err=False)
                click.echo("💡 Set OPENAI_API_KEY in .env file for full functionality")
                return True  # Allow test mode
        else:
            click.echo(f"❌ Unsupported API provider: {provider}", err=True)
            return False
        return True
    except Exception as e:
        click.echo(f"❌ API configuration error: {str(e)}", err=True)
        return False

def _display_groups_table(groups: dict):
    """Display formatted table of groups"""
    click.echo()
    click.echo("┌─────────────────────────────┬───────────┐")
    click.echo("│ Group Name                  │ Files     │")
    click.echo("├─────────────────────────────┼───────────┤")
    
    for group_name, files in groups.items():
        # Truncate name if too long
        display_name = group_name[:27] + "..." if len(group_name) > 30 else group_name
        click.echo(f"│ {display_name:<27} │ {len(files):>9} │")
    
    click.echo("└─────────────────────────────┴───────────┘")

def _display_suggestions_preview(suggestions: str):
    """Display preview of generated suggestions"""
    lines = suggestions.split('\n')
    preview_lines = lines[:10]  # First 10 lines
    
    click.echo("\n📋 Suggestions preview:")
    click.echo("─" * 40)
    for line in preview_lines:
        if line.strip():
            # Truncate very long lines
            display_line = line[:75] + "..." if len(line) > 75 else line
            click.echo(display_line)
    
    if len(lines) > 10:
        click.echo("...")
        click.echo(f"({len(lines) - 10} more lines in full file)")

def _load_available_groups(analysis_path: Path) -> list:
    """Load available groups from previous analysis"""
    # Load from groups.json file (new structure)
    groups_file = analysis_path / "groups.json"
    if groups_file.exists():
        with open(groups_file) as f:
            data = json.load(f)
            groups = data.get('groups', {})
            return list(groups.keys())
    
    # Fallback to old analysis.json for backward compatibility
    analysis_file = analysis_path / "analysis.json"
    if analysis_file.exists():
        with open(analysis_file) as f:
            data = json.load(f)
            # Try both 'functional_groups' and 'groups' for compatibility
            groups = data.get('functional_groups', data.get('groups', {}))
            return list(groups.keys())
    return []

def _sanitize_filename(name: str) -> str:
    """Convert group name to valid filename"""
    import re
    # Replace spaces and special characters
    sanitized = re.sub(r'[^\w\s-]', '', name)
    sanitized = re.sub(r'[-\s]+', '-', sanitized)
    return sanitized.lower().strip('-')

def main():
    """Main entry point for CLI"""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n👋 Operation cancelled by user")
    except Exception as e:
        click.echo(f"💥 Unexpected error: {str(e)}", err=True)
        raise

if __name__ == '__main__':
    main()