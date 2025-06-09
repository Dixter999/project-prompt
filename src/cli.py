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
from datetime import datetime

from .core.analyzer import ProjectAnalyzer
from .generators.suggestions import SuggestionGenerator
from .utils.config import Config
from .api_manager import APIDiagnostics, run_quick_diagnosis
# Importar módulo de diagnósticos
from .api_manager.api_diagnostics import APIDiagnostics, run_quick_diagnosis

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
    
    📖 Documentation: https://github.com/Dixter999/project-prompt
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

@cli.command()
@click.argument('suggestion_name')
@click.option('--phase', '-p', type=int, help='Generate prompt for specific phase only')
@click.option('--analysis-dir', '-a', default=None, help='Analysis directory (default: ./project-prompt-output)')
def generate_prompts(suggestion_name: str, phase: Optional[int], analysis_dir: Optional[str]):
    """Generate implementation prompts from suggestion file.
    
    Creates detailed prompts for each phase of suggestions that can be used
    with AI assistants to implement the recommended improvements.
    
    Examples:
      projectprompt generate-prompts "feature_modules"
      projectprompt generate-prompts "core_modules" --phase 2
      projectprompt generate-prompts "utility_modules" --analysis-dir ./custom-output
    """
    from .generators import ImplementationPromptGenerator
    
    # Determine analysis directory
    analysis_path = Path(analysis_dir) if analysis_dir else Path('./project-prompt-output')
    
    # Validate that analysis exists
    if not analysis_path.exists():
        click.echo("❌ Analysis directory not found.", err=True)
        click.echo("💡 Run 'projectprompt analyze' first to create analysis data.")
        return
    
    # Initialize prompt generator
    generator = ImplementationPromptGenerator(analysis_path)
    
    try:
        if phase:
            # Generate prompt for specific phase only
            click.echo(f"🤖 Generating implementation prompt for {suggestion_name} - Phase {phase}")
            with click.progressbar(length=100, label='Generating prompt') as bar:
                bar.update(50)
                prompt_file = generator.generate_single_phase_prompt(suggestion_name, phase)
                bar.update(50)
            click.echo(f"✅ Generated prompt for phase {phase}: {prompt_file}")
        else:
            # Generate prompts for all phases
            click.echo(f"🤖 Generating implementation prompts for: {suggestion_name}")
            with click.progressbar(length=100, label='Generating prompts') as bar:
                bar.update(20)
                prompt_files = generator.generate_prompts_for_suggestion(suggestion_name)
                bar.update(80)
            
            click.echo(f"✅ Generated {len(prompt_files)} implementation prompts:")
            for file in prompt_files:
                file_path = Path(file)
                click.echo(f"   • {file_path.name}")
        
        click.echo(f"\n📁 Prompts saved to: {analysis_path}/prompts/")
        click.echo("\n🚀 Next steps:")
        click.echo("   1. Review the generated prompts")
        click.echo("   2. Use each prompt with your AI assistant to implement the phases")
        click.echo("   3. Follow the implementation steps in order")
        click.echo("   4. Test and validate each phase before moving to the next")
        
    except FileNotFoundError as e:
        click.echo(f"❌ Suggestion file not found: {suggestion_name}", err=True)
        
        # Show available suggestions
        available_suggestions = generator.list_available_suggestions()
        if available_suggestions:
            click.echo(f"📋 Available suggestions: {', '.join(available_suggestions)}")
        else:
            click.echo("💡 Run 'projectprompt suggest \"group_name\"' first to generate suggestions")
    except ValueError as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"❌ Error generating prompts: {str(e)}", err=True)

@cli.command()
@click.option('--force', '-f', is_flag=True, help='Force uninstall without confirmation')
@click.option('--keep-data', is_flag=True, help='Keep analysis data files (only remove the tool)')
def uninstall(force: bool, keep_data: bool):
    """
    Uninstall ProjectPrompt from your system.
    
    This command will:
    - Remove the installed ProjectPrompt package
    - Optionally clean up analysis data in the current directory
    - Show manual cleanup steps for remaining files
    
    Examples:
      projectprompt uninstall
      projectprompt uninstall --force
      projectprompt uninstall --keep-data
    """
    import subprocess
    import sys
    
    click.echo("🗑️  ProjectPrompt Uninstall")
    click.echo("=" * 40)
    
    if not force:
        click.echo("This will remove ProjectPrompt from your system.")
        if not keep_data:
            click.echo("⚠️  This will also clean up analysis data in the current directory.")
        if not click.confirm('Do you want to continue?'):
            click.echo("👋 Uninstall cancelled.")
            return
    
    try:
        # Step 1: Remove analysis data (unless keep-data is specified)
        if not keep_data:
            current_dir = Path('.')
            analysis_dirs = []
            
            # Find analysis directories in current path
            for item in current_dir.rglob('project-prompt-output'):
                if item.is_dir():
                    analysis_dirs.append(item)
            
            if analysis_dirs:
                click.echo(f"\n🧹 Found {len(analysis_dirs)} analysis directories to clean:")
                for dir_path in analysis_dirs:
                    click.echo(f"   • {dir_path}")
                
                if force or click.confirm('\nRemove these analysis directories?'):
                    for dir_path in analysis_dirs:
                        try:
                            shutil.rmtree(dir_path)
                            click.echo(f"✅ Removed: {dir_path}")
                        except Exception as e:
                            click.echo(f"⚠️  Could not remove {dir_path}: {e}")
            else:
                click.echo("\n📭 No analysis directories found in current path.")
        
        # Step 2: Uninstall the package
        click.echo("\n📦 Uninstalling ProjectPrompt package...")
        
        try:
            # Try to uninstall using pip
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'uninstall', 'projectprompt', '-y'
            ], capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                click.echo("✅ ProjectPrompt package uninstalled successfully.")
            else:
                # Try alternative package names
                for pkg_name in ['project-prompt', 'ProjectPrompt']:
                    result = subprocess.run([
                        sys.executable, '-m', 'pip', 'uninstall', pkg_name, '-y'
                    ], capture_output=True, text=True, check=False)
                    if result.returncode == 0:
                        click.echo(f"✅ {pkg_name} package uninstalled successfully.")
                        break
                else:
                    click.echo("⚠️  Could not uninstall via pip. Package might be installed differently.")
                    
        except Exception as e:
            click.echo(f"⚠️  Error during pip uninstall: {e}")
        
        # Step 3: Show manual cleanup instructions
        click.echo("\n🧹 Manual Cleanup (if needed):")
        click.echo("   If ProjectPrompt was installed from source, you may need to:")
        click.echo("   1. Remove the ProjectPrompt installation directory:")
        click.echo("      rm -rf /path/to/project-prompt")
        click.echo("   2. Remove .env files with API keys:")
        click.echo("      rm /path/to/project-prompt/.env")
        click.echo("   3. Check for remaining analysis directories:")
        click.echo("      find ~ -name 'project-prompt-output' -type d")
        
        # Step 4: Verify uninstall
        click.echo("\n🔍 Verifying uninstall...")
        try:
            result = subprocess.run([
                'which', 'projectprompt'
            ], capture_output=True, text=True, check=False)
            
            if result.returncode != 0:
                click.echo("✅ ProjectPrompt command is no longer available.")
            else:
                click.echo(f"⚠️  ProjectPrompt command still found at: {result.stdout.strip()}")
                click.echo("   You may need to restart your terminal or manually remove it.")
                
        except Exception:
            # 'which' command might not be available on all systems
            click.echo("   (Could not verify command removal)")
        
        click.echo("\n🎉 Uninstall completed!")
        click.echo("   Thank you for using ProjectPrompt! 👋")
        
    except Exception as e:
        click.echo(f"❌ Error during uninstall: {str(e)}", err=True)
        click.echo("\n💡 Manual uninstall options:")
        click.echo("   1. pip uninstall projectprompt")
        click.echo("   2. rm -rf /path/to/project-prompt (if installed from source)")
        raise click.ClickException(f"Uninstall failed: {str(e)}")

@cli.command()
@click.argument('task_description')
@click.option('--project-path', '-p', default='.',
              help='Path to project directory (default: current directory)')
@click.option('--target', '-t', 
              type=click.Choice(['speed', 'cost', 'quality', 'balanced']),
              default='balanced',
              help='Optimization target (default: balanced)')
@click.option('--task-type', 
              type=click.Choice(['implementation', 'analysis', 'debugging', 'optimization', 'testing']),
              default='implementation',
              help='Type of task (default: implementation)')
@click.option('--complexity', 
              type=click.Choice(['simple', 'medium', 'complex', 'very_complex']),
              default='medium',
              help='Task complexity level (default: medium)')
@click.option('--dry-run', is_flag=True,
              help='Show what would be done without making API calls')
@click.option('--api-key', 
              help='Anthropic API key (or set ANTHROPIC_API_KEY env var)')
@click.option('--use-workflow', is_flag=True,
              help='Use advanced workflow management (FASE 2)')
@click.option('--max-requests', default=5, type=int,
              help='Maximum number of API requests for complex tasks')
@click.option('--conversation-mode', is_flag=True,
              help='Enable multi-turn conversation mode')
def adaptive_implement(task_description: str,
                      project_path: str,
                      target: str,
                      task_type: str,
                      complexity: str,
                      dry_run: bool,
                      api_key: Optional[str],
                      use_workflow: bool,
                      max_requests: int,
                      conversation_mode: bool):
    """
    🤖 ADAPTIVE IMPLEMENTATION - Sistema de Implementación Adaptativa
    
    Uses AI-driven intelligent implementation with context-aware optimization.
    
    📚 FASE 1 (Standard): Single-request implementation with:
    • Intelligent project context analysis
    • Advanced prompt enhancement and optimization
    • Multi-target request optimization (speed/cost/quality)
    • Caching and performance tracking
    
    🚀 FASE 2 (Advanced Workflow): Multi-request intelligent orchestration with:
    • Advanced workflow management and coordination
    • Multi-turn conversation handling with context tracking
    • Parallel request processing and dependency resolution
    • Response processing and implementation plan generation
    • Comprehensive analytics and performance optimization
    
    Examples:
      # Standard FASE 1 implementation
      projectprompt adaptive-implement "Add user authentication system"
      projectprompt adaptive-implement "Optimize database queries" --target cost
      projectprompt adaptive-implement "Fix login bug" --task-type debugging
      
      # Advanced FASE 2 workflow implementation  
      projectprompt adaptive-implement "Refactor API" --use-workflow
      projectprompt adaptive-implement "Complex feature" --use-workflow --conversation-mode
      projectprompt adaptive-implement "Large refactor" --use-workflow --max-requests 10
    """
    try:
        from .api_manager.context_builder import ContextBuilder
        from .api_manager.prompt_enricher import PromptEnricher
        from .api_manager.anthropic_client import AnthropicClient
        from .api_manager.request_optimizer import RequestOptimizer
        from .api_manager.conversation_manager import ConversationManager
        from .api_manager.response_processor import ResponseProcessor
        from .api_manager.implementation_coordinator import ImplementationCoordinator
        from datetime import datetime
    except ImportError as e:
        click.echo(f"❌ Missing API manager components: {str(e)}", err=True)
        click.echo("💡 Run: pip install pyyaml anthropic")
        return
    
    # Validate project path
    project_path = Path(project_path).resolve()
    if not project_path.exists() or not project_path.is_dir():
        click.echo(f"❌ Project path does not exist: {project_path}", err=True)
        return
    
    click.echo(f"🎯 Sistema de Implementación Adaptativa")
    click.echo(f"   Task: {task_description}")
    click.echo(f"   Project: {project_path}")
    click.echo(f"   Target: {target} | Type: {task_type} | Complexity: {complexity}")
    
    if use_workflow:
        click.echo(f"🚀 FASE 2: Advanced Workflow Mode")
        click.echo(f"   Max Requests: {max_requests}")
        if conversation_mode:
            click.echo(f"   Conversation Mode: Enabled")
    else:
        click.echo(f"📋 FASE 1: Standard Implementation Mode")
    
    if dry_run:
        click.echo("🔍 DRY RUN - No API calls will be made")
    
    try:
        # FASE 1: Build project context
        with click.progressbar(length=4, label="📊 Building project context") as bar:
            context_builder = ContextBuilder(str(project_path))
            bar.update(1)
            
            context = context_builder.build_complete_context()
            bar.update(1)
            
            # Display context summary
            summary = context_builder.get_context_summary(context)
            bar.update(2)
        
        click.echo("\n📋 Project Context Summary:")
        click.echo(summary)
        
        # FASE 1: Enrich prompt
        with click.progressbar(length=3, label="🎨 Enriching prompt") as bar:
            prompt_enricher = PromptEnricher()
            bar.update(1)
            
            enriched_config = prompt_enricher.enrich_prompt(
                base_prompt=task_description,
                context=context,
                task_type=task_type,
                complexity_level=complexity
            )
            bar.update(1)
            
            # Validate enriched prompt
            validation = prompt_enricher.validate_enriched_prompt(enriched_config)
            bar.update(1)
        
        # Display validation results
        if validation['warnings']:
            click.echo("\n⚠️  Prompt Warnings:")
            for warning in validation['warnings']:
                click.echo(f"   • {warning}")
        
        if validation['suggestions']:
            click.echo("\n💡 Suggestions:")
            for suggestion in validation['suggestions']:
                click.echo(f"   • {suggestion}")
        
        click.echo(f"\n💰 Estimated Cost: ${validation['estimated_cost']['estimated_total_cost']:.4f}")
        
        # FASE 1: Optimize request
        with click.progressbar(length=2, label="⚡ Optimizing request") as bar:
            request_optimizer = RequestOptimizer()
            bar.update(1)
            
            optimized_config = request_optimizer.optimize_request_strategy(
                enriched_config=enriched_config,
                context=context,
                performance_target=target
            )
            bar.update(1)
        
        click.echo(f"\n🔧 Optimization Applied:")
        click.echo(f"   Model: {optimized_config.get('model', 'N/A')}")
        click.echo(f"   Temperature: {optimized_config.get('temperature', 'N/A')}")
        click.echo(f"   Max Tokens: {optimized_config.get('max_tokens', 'N/A')}")
        
        if dry_run:
            click.echo("\n📝 Generated Prompt Preview:")
            click.echo("-" * 50)
            preview = optimized_config['prompt'][:500]
            click.echo(preview + "..." if len(optimized_config['prompt']) > 500 else preview)
            click.echo("-" * 50)
            if use_workflow:
                click.echo("🔀 Would use advanced workflow management")
            if conversation_mode:
                click.echo("💬 Would use multi-turn conversation mode")
            click.echo("✅ Dry run completed - no API calls made")
            return
        
        # Check for API key
        if not api_key and not os.getenv('ANTHROPIC_API_KEY'):
            click.echo("\n❌ No API key provided. Set ANTHROPIC_API_KEY environment variable or use --api-key option.")
            return
        
        # FASE 2: Advanced Workflow Execution (if enabled)
        if use_workflow:
            click.echo("\n🔀 FASE 2: Advanced Workflow Management Enabled")
            
            # Initialize FASE 2 components
            client = AnthropicClient(api_key=api_key)
            coordinator = ImplementationCoordinator(client, max_concurrent_requests=3)
            response_processor = ResponseProcessor()
            
            # Initialize conversation manager if enabled
            conversation_manager = None
            if conversation_mode:
                conversation_manager = ConversationManager()
                session_id = conversation_manager.create_session(
                    initial_task=task_description,
                    project_context=context,
                    metadata={
                        'task_type': task_type,
                        'complexity': complexity,
                        'target': target,
                        'project_path': str(project_path)
                    }
                )
                click.echo(f"💬 Conversation session created: {session_id}")
            
            # Create workflow with optimized configuration
            workflow_metadata = {
                'task_description': task_description,
                'task_type': task_type,
                'complexity': complexity,
                'target': target,
                'max_requests': max_requests,
                'conversation_mode': conversation_mode
            }
            
            with click.progressbar(length=5, label="🚀 Creating workflow") as bar:
                workflow_id = coordinator.create_workflow(
                    initial_request=optimized_config,
                    metadata=workflow_metadata
                )
                bar.update(2)
                
                click.echo(f"\n🔧 Workflow created: {workflow_id}")
                
                # Execute workflow with progress tracking
                results = coordinator.execute_workflow(workflow_id)
                bar.update(3)
            
            # Process results with ResponseProcessor
            click.echo("\n📊 Processing workflow results...")
            processed_results = []
            
            for i, result in enumerate(results):
                with click.progressbar(length=3, label=f"Processing response {i+1}/{len(results)}") as bar:
                    # Extract content and implementation steps
                    extracted_content = response_processor.extract_content(result['response'])
                    bar.update(1)
                    
                    # Generate implementation plan
                    implementation_plan = response_processor.generate_implementation_plan(
                        response=result['response'],
                        context=context
                    )
                    bar.update(1)
                    
                    # Detect file modifications
                    file_modifications = response_processor.detect_file_modifications(result['response'])
                    bar.update(1)
                    
                    processed_result = {
                        'request_id': result['request_id'],
                        'content': extracted_content,
                        'implementation_plan': implementation_plan,
                        'file_modifications': file_modifications,
                        'performance_metrics': result.get('performance_metrics', {}),
                        'timestamp': result.get('timestamp')
                    }
                    processed_results.append(processed_result)
            
            # Handle conversation mode updates
            if conversation_mode and conversation_manager:
                for result in processed_results:
                    conversation_manager.add_turn(
                        session_id=session_id,
                        user_message=f"Processing result for {result['request_id']}",
                        assistant_response=result['content']['extracted_text'],
                        metadata={
                            'implementation_plan': result['implementation_plan'],
                            'file_modifications': result['file_modifications']
                        }
                    )
            
            # Save comprehensive results
            output_dir = project_path / 'project-prompt-output' / 'adaptive-implementation'
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save workflow results
            workflow_file = output_dir / f"workflow_{timestamp}.json"
            workflow_results = {
                'workflow_id': workflow_id,
                'task_description': task_description,
                'metadata': workflow_metadata,
                'processed_results': processed_results,
                'workflow_analytics': coordinator.get_workflow_analytics(workflow_id),
                'timestamp': datetime.now().isoformat()
            }
            
            with open(workflow_file, 'w', encoding='utf-8') as f:
                json.dump(workflow_results, f, indent=2, ensure_ascii=False)
            
            # Save markdown summary
            markdown_file = output_dir / f"workflow_summary_{timestamp}.md"
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(f"# Advanced Workflow Implementation Result\n\n")
                f.write(f"**Task**: {task_description}\n")
                f.write(f"**Type**: {task_type}\n")
                f.write(f"**Complexity**: {complexity}\n")
                f.write(f"**Target**: {target}\n")
                f.write(f"**Workflow ID**: {workflow_id}\n")
                f.write(f"**Timestamp**: {datetime.now().isoformat()}\n\n")
                
                if conversation_mode:
                    f.write(f"**Conversation Session**: {session_id}\n\n")
                
                f.write(f"## Workflow Summary\n\n")
                f.write(f"- **Total Requests**: {len(processed_results)}\n")
                f.write(f"- **File Modifications Detected**: {sum(len(r['file_modifications']) for r in processed_results)}\n")
                f.write(f"- **Implementation Steps**: {sum(len(r['implementation_plan']['steps']) for r in processed_results)}\n\n")
                
                f.write(f"## Project Context\n\n```\n{summary}\n```\n\n")
                
                for i, result in enumerate(processed_results, 1):
                    f.write(f"## Response {i} - {result['request_id']}\n\n")
                    f.write(f"### Implementation Plan\n\n")
                    for step in result['implementation_plan']['steps']:
                        f.write(f"- {step}\n")
                    f.write(f"\n### File Modifications\n\n")
                    for mod in result['file_modifications']:
                        f.write(f"- **{mod['file_path']}**: {mod['modification_type']}\n")
                    f.write(f"\n### Content\n\n{result['content']['extracted_text']}\n\n")
            
            # Save conversation session if enabled
            if conversation_mode and conversation_manager:
                conversation_file = output_dir / f"conversation_{session_id}_{timestamp}.json"
                conversation_data = conversation_manager.get_session(session_id)
                with open(conversation_file, 'w', encoding='utf-8') as f:
                    json.dump(conversation_data, f, indent=2, ensure_ascii=False, default=str)
            
            # Display workflow results
            click.echo(f"\n✅ Advanced Workflow Completed:")
            click.echo(f"   Workflow ID: {workflow_id}")
            click.echo(f"   Requests Processed: {len(processed_results)}")
            click.echo(f"   Total File Modifications: {sum(len(r['file_modifications']) for r in processed_results)}")
            click.echo(f"   Implementation Steps: {sum(len(r['implementation_plan']['steps']) for r in processed_results)}")
            
            if conversation_mode:
                click.echo(f"   Conversation Session: {session_id}")
            
            # Display workflow analytics
            analytics = coordinator.get_workflow_analytics(workflow_id)
            if analytics:
                click.echo(f"\n📊 Workflow Analytics:")
                click.echo(f"   Total Execution Time: {analytics.get('total_execution_time', 0):.2f}s")
                click.echo(f"   Average Response Time: {analytics.get('average_response_time', 0):.2f}s")
                click.echo(f"   Success Rate: {analytics.get('success_rate', 0):.1%}")
                click.echo(f"   Total Cost: ${analytics.get('total_cost', 0):.4f}")
            
            click.echo(f"\n📁 Results saved to:")
            click.echo(f"   Workflow Data: {workflow_file}")
            click.echo(f"   Summary: {markdown_file}")
            if conversation_mode:
                click.echo(f"   Conversation: {conversation_file}")
            
        else:
            # FASE 1: Standard single-request execution
            with click.progressbar(length=3, label="🚀 Sending API request") as bar:
                client = AnthropicClient(api_key=api_key)
                bar.update(1)
                
                response = client.send_enriched_request(optimized_config)
                bar.update(2)
        
            # Display standard results
            click.echo(f"\n✅ API Response Received:")
            click.echo(f"   Model: {response.get('model', 'N/A')}")
            click.echo(f"   Input Tokens: {response.get('usage', {}).get('input_tokens', 'N/A')}")
            click.echo(f"   Output Tokens: {response.get('usage', {}).get('output_tokens', 'N/A')}")
            click.echo(f"   Response Time: {response.get('request_time', 0):.2f}s")
            
            if response.get('from_cache'):
                click.echo("   📦 Response served from cache")
            
            # Save standard response to file
            output_dir = project_path / 'project-prompt-output' / 'adaptive-implementation'
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"implementation_{timestamp}.md"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Adaptive Implementation Result\n\n")
                f.write(f"**Task**: {task_description}\n")
                f.write(f"**Type**: {task_type}\n")
                f.write(f"**Complexity**: {complexity}\n")
                f.write(f"**Target**: {target}\n")
                f.write(f"**Timestamp**: {datetime.now().isoformat()}\n\n")
                f.write(f"## Project Context\n\n")
                f.write(f"```\n{summary}\n```\n\n")
                f.write(f"## Implementation Response\n\n")
                f.write(response['content'])
            
            click.echo(f"\n📁 Result saved to: {output_file}")
            
            # Display performance metrics if available
            metrics = client.get_performance_metrics()
            if 'total_requests' in metrics:
                click.echo(f"\n📊 API Performance (24h):")
                click.echo(f"   Requests: {metrics['total_requests']}")
                click.echo(f"   Cache Hit Rate: {metrics['cache_hit_rate']:.1%}")
                click.echo(f"   Avg Response Time: {metrics['average_response_time']:.2f}s")
                click.echo(f"   Daily Cost: ${metrics['daily_cost']:.4f}")
            
            # Display optimization metrics
            opt_metrics = request_optimizer.get_optimization_metrics()
            if 'total_optimizations' in opt_metrics:
                click.echo(f"\n⚡ Optimization Performance (24h):")
                click.echo(f"   Optimizations: {opt_metrics['total_optimizations']}")
                click.echo(f"   Cost Savings: ${opt_metrics['total_cost_savings']:.4f}")
                click.echo(f"   Reduction: {opt_metrics['cost_reduction_percentage']:.1f}%")
        
        click.echo(f"\n🎉 Adaptive implementation completed successfully!")
        
    except Exception as e:
        click.echo(f"\n💥 Error during adaptive implementation: {str(e)}", err=True)
        if '--verbose' in click.get_current_context().params:
            import traceback
            click.echo(traceback.format_exc(), err=True)

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

@cli.command()
@click.option('--api-key', help='Clave API de Anthropic')
@click.option('--save-report', help='Guardar reporte en archivo')
@click.option('--quick', is_flag=True, help='Ejecutar diagnóstico rápido')
def diagnose_api(api_key, save_report, quick):
    """🔍 Diagnosticar el estado del sistema API"""
    
    if quick:
        success = run_quick_diagnosis(api_key=api_key)
        if success:
            click.echo("✅ Diagnóstico rápido: Sistema funcionando correctamente")
        else:
            click.echo("❌ Diagnóstico rápido: Se encontraron problemas")
            click.echo("   Ejecuta 'projectprompt diagnose-api' (sin --quick) para más detalles")
        return
    
    # Diagnóstico completo
    diagnostics = APIDiagnostics(api_key=api_key)
    report = diagnostics.run_complete_diagnosis(verbose=True)
    
    # Guardar reporte si se solicita
    if save_report:
        saved_path = diagnostics.save_report_to_file(report, save_report)
        click.echo(f"\n💾 Reporte guardado en: {saved_path}")

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