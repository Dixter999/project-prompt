#!/usr/bin/env python3
"""
Rules Commands for ProjectPrompt

This module provides comprehensive CLI commands for managing project rules
including initialization, validation, application, and reporting.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from src.utils.enhanced_rules_manager import EnhancedRulesManager
from src.utils.logger import get_logger

# Try to import optional components with fallbacks
try:
    from src.ui.rules_wizard import RulesWizard
except ImportError:
    RulesWizard = None

try:
    from src.generators.rules_report_generator import RulesReportGenerator
except ImportError:
    RulesReportGenerator = None

try:
    from src.analyzers.rules_suggester import get_rules_suggester, SuggestionContext
except ImportError:
    def get_rules_suggester(*args, **kwargs):
        raise ImportError("Rules suggester not available")
    SuggestionContext = None

try:
    from src.integrations.anthropic_rules_analyzer import get_anthropic_rules_analyzer
except ImportError:
    def get_anthropic_rules_analyzer(*args, **kwargs):
        raise ImportError("Anthropic analyzer not available")

try:
    from src.analyzers.structured_rules_suggester import StructuredRulesSuggester
except ImportError:
    StructuredRulesSuggester = None

import asyncio
import jinja2

# Initialize components
console = Console()
logger = get_logger()

# Create Typer app for rules commands
rules_app = typer.Typer(help="Interactive rules management commands")


def get_project_root() -> str:
    """Get the current project root directory"""
    return os.getcwd()


def print_header(title: str):
    """Print a formatted header"""
    console.print(f"\n[bold cyan]{title}[/bold cyan]")
    console.print("─" * len(title))


def print_success(message: str):
    """Print a success message"""
    console.print(f"[green]✅[/green] {message}")


def print_error(message: str):
    """Print an error message"""
    console.print(f"[red]❌[/red] {message}")


def print_warning(message: str):
    """Print a warning message"""
    console.print(f"[yellow]⚠️[/yellow] {message}")


def print_info(message: str):
    """Print an info message"""
    console.print(f"[cyan]ℹ️[/cyan] {message}")


@rules_app.command("init")
def rules_init(
    project_type: Optional[str] = typer.Argument(None, help="Project type (web_app, data_science, api_service, cli_tool)"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", "-i/-ni", 
                                   help="Use interactive wizard for configuration"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing rules file"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Custom output file path"),
    template_only: bool = typer.Option(False, "--template-only", "-t", help="Generate template without interactive wizard")
):
    """Initialize project rules with interactive wizard or template"""
    try:
        print_header("Rules Initialization")
        
        project_root = get_project_root()
        manager = EnhancedRulesManager(project_root=project_root)
        
        # Check for existing rules file
        existing_rules = manager.find_rules_file()
        if existing_rules and not force:
            print_warning(f"Rules file already exists: {existing_rules}")
            if not typer.confirm("Do you want to overwrite it?"):
                print_info("Operation cancelled")
                return
        
        # Use interactive wizard if requested and not template-only
        if interactive and not template_only:
            print_info("Starting interactive rules configuration wizard...")
            wizard = RulesWizard(manager)
            success = wizard.run(project_type=project_type, output_path=output)
            
            if success:
                print_success("Rules file created successfully with interactive wizard!")
                wizard.show_summary()
            else:
                print_error("Failed to create rules file with wizard")
                return
        
        else:
            # Use template-based approach
            if not project_type:
                print_error("Project type is required when not using interactive mode")
                print_info("Available types: web_app, data_science, api_service, cli_tool")
                return
            
            # Auto-detect project context if possible
            context = _detect_project_context(project_root)
            context.update({
                'project_name': os.path.basename(project_root),
                'created_date': datetime.now().strftime('%Y-%m-%d'),
                'created_by': 'ProjectPrompt Interactive Rules'
            })
            
            print_info(f"Creating rules for {project_type} project...")
            success = manager.create_rules_file(project_type=project_type, context=context)
            
            if success:
                print_success(f"Rules file created: {manager.rules_file_path}")
                
                # Load and show summary
                if manager.load_rules():
                    rules = manager.get_all_rules()
                    print_info(f"Generated {len(rules)} rules across multiple categories")
                    _show_rules_summary(manager)
                
            else:
                print_error("Failed to create rules file")
        
    except Exception as e:
        print_error(f"Error during rules initialization: {e}")
        logger.error(f"Rules init error: {e}", exc_info=True)


@rules_app.command("validate")
def rules_validate(
    file_path: Optional[str] = typer.Option(None, "--file", "-f", help="Path to rules file to validate"),
    fix: bool = typer.Option(False, "--fix", help="Automatically fix common issues"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed validation results")
):
    """Validate rules file syntax and check for conflicts"""
    try:
        print_header("Rules Validation")
        
        project_root = get_project_root()
        manager = EnhancedRulesManager(project_root=project_root)
        
        # Use provided file or find existing one
        if file_path:
            if not os.path.exists(file_path):
                print_error(f"Rules file not found: {file_path}")
                return
            manager.rules_file_path = file_path
        else:
            rules_file = manager.find_rules_file()
            if not rules_file:
                print_error("No rules file found in project")
                print_info("Use 'pp rules init' to create one")
                return
            manager.rules_file_path = rules_file
        
        print_info(f"Validating rules file: {manager.rules_file_path}")
        
        # Validate syntax
        validation_results = manager.validate_rules()
        
        if validation_results['is_valid']:
            print_success("✅ Rules file is valid!")
            
            # Show detailed results if requested
            if detailed:
                _show_validation_details(validation_results)
            
            # Show summary statistics
            if manager.load_rules():
                _show_rules_summary(manager)
                
        else:
            print_error("❌ Rules file has validation errors:")
            
            # Show errors
            for error in validation_results.get('errors', []):
                print_error(f"  • {error}")
            
            # Show warnings
            for warning in validation_results.get('warnings', []):
                print_warning(f"  • {warning}")
            
            # Offer to fix if requested
            if fix and validation_results.get('fixable_issues'):
                print_info("Attempting to fix common issues...")
                # Implement auto-fix logic here
                print_info("Auto-fix feature coming soon!")
        
    except Exception as e:
        print_error(f"Error during validation: {e}")
        logger.error(f"Rules validation error: {e}", exc_info=True)


@rules_app.command("apply")
def rules_apply(
    target_path: Optional[str] = typer.Argument(None, help="Path to apply rules to (default: current directory)"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would be done without making changes"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Apply only rules from specific category"),
    priority: Optional[str] = typer.Option(None, "--priority", "-p", help="Apply only rules of specific priority"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Confirm each rule application"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Save application results to file")
):
    """Apply rules to existing codebase with analysis and suggestions"""
    try:
        print_header("Rules Application")
        
        project_root = get_project_root()
        target = target_path or project_root
        
        if not os.path.exists(target):
            print_error(f"Target path does not exist: {target}")
            return
        
        manager = EnhancedRulesManager(project_root=project_root)
        
        # Load rules
        if not manager.load_rules():
            print_error("Failed to load rules file")
            print_info("Use 'pp rules init' to create one")
            return
        
        print_info(f"Applying rules to: {target}")
        
        # Filter rules if requested
        rules = manager.get_all_rules()
        if category:
            try:
                from src.models.rule_models import RuleCategory
                cat_enum = RuleCategory(category.lower())
                rules = manager.get_rules_by_category(cat_enum)
                print_info(f"Filtering by category: {category}")
            except ValueError:
                print_error(f"Invalid category: {category}")
                return
        
        if priority:
            try:
                from src.models.rule_models import RulePriority
                pri_enum = RulePriority(priority.lower())
                rules = manager.get_rules_by_priority(pri_enum)
                print_info(f"Filtering by priority: {priority}")
            except ValueError:
                print_error(f"Invalid priority: {priority}")
                return
        
        if not rules:
            print_warning("No rules to apply with current filters")
            return
        
        print_info(f"Found {len(rules)} applicable rules")
        
        if dry_run:
            print_info("DRY RUN MODE - No changes will be made")
        
        # Apply rules with progress tracking
        application_results = _apply_rules_to_project(
            manager, rules, target, dry_run, interactive
        )
        
        # Show results
        _show_application_results(application_results)
        
        # Save results if requested
        if output:
            _save_application_results(application_results, output)
            print_success(f"Results saved to: {output}")
        
    except Exception as e:
        print_error(f"Error during rules application: {e}")
        logger.error(f"Rules application error: {e}", exc_info=True)


@rules_app.command("report")
def rules_report(
    target_path: Optional[str] = typer.Argument(None, help="Path to analyze (default: current directory)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path (default: stdout)"),
    format: str = typer.Option("markdown", "--format", "-f", help="Report format (markdown, json, html)"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Include detailed violation information"),
    categories: Optional[str] = typer.Option(None, "--categories", "-c", help="Comma-separated list of categories to include"),
    threshold: Optional[str] = typer.Option(None, "--threshold", "-t", help="Minimum priority level (mandatory, recommended, optional)")
):
    """Generate comprehensive rules compliance report"""
    try:
        print_header("Rules Compliance Report")
        
        project_root = get_project_root()
        target = target_path or project_root
        
        if not os.path.exists(target):
            print_error(f"Target path does not exist: {target}")
            return
        
        manager = EnhancedRulesManager(project_root=project_root)
        
        # Load rules
        if not manager.load_rules():
            print_error("Failed to load rules file")
            print_info("Use 'pp rules init' to create one")
            return
        
        print_info(f"Generating compliance report for: {target}")
        
        # Initialize report generator
        generator = RulesReportGenerator(manager)
        
        # Set filters
        filter_options = {}
        if categories:
            filter_options['categories'] = [cat.strip() for cat in categories.split(',')]
        if threshold:
            filter_options['min_priority'] = threshold
        
        # Generate report
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing project compliance...", total=100)
            
            report_data = generator.generate_report(
                target_path=target,
                format=format,
                detailed=detailed,
                filters=filter_options,
                progress_callback=lambda p: progress.update(task, completed=p)
            )
        
        # Output report
        if output:
            generator.save_report(report_data, output, format)
            print_success(f"Report saved to: {output}")
        else:
            # Display to console
            if format == "json":
                console.print_json(json.dumps(report_data, indent=2))
            else:
                console.print(report_data['content'])
        
        # Show summary
        summary = report_data.get('summary', {})
        if summary:
            print_success(f"Compliance Score: {summary.get('compliance_score', 0):.1%}")
            print_info(f"Total Rules: {summary.get('total_rules', 0)}")
            print_info(f"Violations: {summary.get('total_violations', 0)}")
        
    except Exception as e:
        print_error(f"Error generating report: {e}")
        logger.error(f"Rules report error: {e}", exc_info=True)


@rules_app.command("template")
def rules_template(
    project_type: str = typer.Argument(..., help="Project type (web_app, data_science, api_service, cli_tool)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    show_content: bool = typer.Option(False, "--show", "-s", help="Display template content"),
    list_types: bool = typer.Option(False, "--list", "-l", help="List available project types")
):
    """Generate rules template for specific project type"""
    try:
        if list_types:
            print_header("Available Project Types")
            types = ["web_app", "data_science", "api_service", "cli_tool"]
            for ptype in types:
                console.print(f"  • [cyan]{ptype}[/cyan] - {_get_project_type_description(ptype)}")
            return
        
        print_header(f"Rules Template: {project_type}")
        
        project_root = get_project_root()
        manager = EnhancedRulesManager(project_root=project_root)
        
        # Generate template
        context = {
            'project_name': 'example_project',
            'description': f'Example {project_type} project',
            'created_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        template_content = manager.generate_rules_template(project_type, context)
        
        if not template_content:
            print_error(f"Unknown project type: {project_type}")
            print_info("Use --list to see available types")
            return
        
        # Output template
        if output:
            with open(output, 'w') as f:
                f.write(template_content)
            print_success(f"Template saved to: {output}")
        
        if show_content or not output:
            console.print("\n[bold]Template Content:[/bold]")
            console.print(Panel(template_content, title=f"{project_type} Rules Template"))
        
        print_info(f"Template generated with {len(template_content.split('##'))-1} rule categories")
        
    except Exception as e:
        print_error(f"Error generating template: {e}")
        logger.error(f"Template generation error: {e}", exc_info=True)


@rules_app.command("suggest")
def suggest_rules(
    target_path: Optional[str] = typer.Argument(None, help="Path to analyze (default: current directory)"),
    output: Optional[str] = typer.Option(None, "-o", "--output", help="Output file for suggestions"),
    format: str = typer.Option("markdown", "-f", "--format", help="Output format (markdown, yaml, json)"),
    ai_enhanced: bool = typer.Option(False, "--ai", help="Use AI-enhanced analysis (requires API key)"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Interactive review of suggestions"),
    confidence_threshold: float = typer.Option(0.7, "--threshold", help="Minimum confidence threshold for suggestions"),
    categories: Optional[str] = typer.Option(None, "-c", "--categories", help="Comma-separated categories to focus on")
):
    """Generate AI-powered rule suggestions based on project analysis"""
    print_header("🤖 AI-Powered Rules Suggestions")
    
    project_path = target_path or get_project_root()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
        ) as progress:
            
            # Step 1: Analyze project patterns
            task1 = progress.add_task("Analyzing project patterns...", total=100)
            suggester = get_rules_suggester(project_path)
            pattern_analysis = suggester.analyze_project_patterns()
            progress.update(task1, advance=50)
            
            # Step 2: Generate basic suggestions
            suggestions = suggester.suggest_rules()
            progress.update(task1, advance=30)
            
            # Step 3: AI enhancement (if requested)
            if ai_enhanced:
                task2 = progress.add_task("Enhancing with AI analysis...", total=100)
                try:
                    ai_analyzer = get_anthropic_rules_analyzer()
                    
                    # Collect code samples for AI analysis
                    code_samples = _collect_code_samples(project_path)
                    progress.update(task2, advance=40)
                    
                    # Get AI analysis
                    project_context = {
                        'project_type': 'general',
                        'size_category': 'medium'
                    }
                    
                    ai_result = asyncio.run(ai_analyzer.analyze_for_rules(
                        pattern_analysis, code_samples, project_context
                    ))
                    progress.update(task2, advance=40)
                    
                    # Merge AI suggestions with basic suggestions
                    suggestions.extend(ai_result.suggestions)
                    progress.update(task2, advance=20)
                    
                except Exception as e:
                    console.print(f"[yellow]⚠️[/yellow] AI enhancement failed: {e}")
                    console.print("[yellow]Continuing with basic analysis...[/yellow]")
            
            progress.update(task1, advance=20)
        
        # Filter by confidence threshold
        filtered_suggestions = [s for s in suggestions if s.confidence >= confidence_threshold]
        
        # Filter by categories if specified
        if categories:
            category_list = [cat.strip().lower() for cat in categories.split(',')]
            filtered_suggestions = [
                s for s in filtered_suggestions 
                if s.suggested_rule.category.value.lower() in category_list
            ]
        
        console.print(f"\n[green]✅[/green] Analysis complete! Found {len(filtered_suggestions)} suggestions")
        
        # Interactive review
        if interactive and filtered_suggestions:
            reviewed_suggestions = _interactive_suggestion_review(filtered_suggestions)
        else:
            reviewed_suggestions = filtered_suggestions
        
        # Generate output
        if output or format != "markdown":
            _generate_suggestions_output(
                reviewed_suggestions, pattern_analysis, output, format, project_path
            )
        else:
            _display_suggestions_summary(reviewed_suggestions, pattern_analysis)
        
        print_success(f"Generated {len(reviewed_suggestions)} rule suggestions")
        
    except Exception as e:
        print_error(f"Failed to generate suggestions: {e}")
        logger.error(f"Error in suggest_rules: {e}")
        raise typer.Exit(1)


@rules_app.command("analyze-patterns")
def analyze_patterns(
    target_path: Optional[str] = typer.Argument(None, help="Path to analyze (default: current directory)"),
    detailed: bool = typer.Option(False, "-d", "--detailed", help="Show detailed pattern analysis"),
    export: Optional[str] = typer.Option(None, "--export", help="Export analysis to JSON file")
):
    """Analyze project patterns for rule suggestions"""
    print_header("🔍 Project Pattern Analysis")
    
    project_path = target_path or get_project_root()
    
    try:
        with console.status("[bold green]Analyzing project patterns..."):
            suggester = get_rules_suggester(project_path)
            analysis = suggester.analyze_project_patterns()
        
        # Display analysis results
        _display_pattern_analysis(analysis, detailed)
        
        # Export if requested
        if export:
            analysis_data = {
                'timestamp': datetime.now().isoformat(),
                'project_path': project_path,
                'technology_stack': analysis.technology_stack,
                'architectural_patterns': analysis.architectural_patterns,
                'code_style_patterns': analysis.code_style_patterns,
                'testing_patterns': analysis.testing_patterns,
                'documentation_patterns': analysis.documentation_patterns,
                'security_patterns': analysis.security_patterns,
                'inconsistencies': analysis.inconsistencies,
                'confidence_score': analysis.confidence_score
            }
            
            with open(export, 'w') as f:
                json.dump(analysis_data, f, indent=2)
            
            print_success(f"Analysis exported to {export}")
        
    except Exception as e:
        print_error(f"Failed to analyze patterns: {e}")
        logger.error(f"Error in analyze_patterns: {e}")
        raise typer.Exit(1)


@rules_app.command("auto-generate")
def auto_generate_rules(
    target_path: Optional[str] = typer.Argument(None, help="Path to analyze (default: current directory)"),
    output: Optional[str] = typer.Option("auto_rules.yaml", "-o", "--output", help="Output rules file"),
    template_type: Optional[str] = typer.Option(None, "--template", help="Use specific template (web_app, api_service, data_science)"),
    confidence_threshold: float = typer.Option(0.8, "--threshold", help="Minimum confidence for auto-inclusion"),
    review: bool = typer.Option(True, "--review/--no-review", help="Review suggestions before generating file")
):
    """Auto-generate a complete rules file based on project analysis"""
    print_header("🚀 Auto-Generate Rules File")
    
    project_path = target_path or get_project_root()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
        ) as progress:
            
            # Analyze project
            task = progress.add_task("Analyzing project...", total=100)
            suggester = get_rules_suggester(project_path)
            
            # Get suggestions
            if template_type:
                # Use template-based suggestions
                context = SuggestionContext(
                    project_type=template_type,
                    size_category="medium",
                    complexity_level="moderate",
                    team_size="small"
                )
                suggestions = suggester.suggest_rules(context)
            else:
                # Use analysis-based suggestions
                suggestions = suggester.suggest_rules()
            
            progress.update(task, advance=50)
            
            # Filter by confidence
            high_confidence_suggestions = [
                s for s in suggestions if s.confidence >= confidence_threshold
            ]
            
            progress.update(task, advance=30)
            
            # Generate rules file
            if review:
                console.print(f"\n[cyan]Found {len(high_confidence_suggestions)} high-confidence suggestions[/cyan]")
                reviewed_suggestions = _interactive_suggestion_review(high_confidence_suggestions)
            else:
                reviewed_suggestions = high_confidence_suggestions
            
            # Generate the file
            rules_file_path = suggester.generate_draft_rules_file(reviewed_suggestions, output)
            progress.update(task, advance=20)
        
        print_success(f"Generated rules file: {rules_file_path}")
        console.print(f"[cyan]📝[/cyan] Review and customize the generated rules before applying them")
        
    except Exception as e:
        print_error(f"Failed to auto-generate rules: {e}")
        logger.error(f"Error in auto_generate_rules: {e}")
        raise typer.Exit(1)


@rules_app.command("generate-project-rules")
def generate_project_rules(
    target_path: Optional[str] = typer.Argument(None, help="Path to analyze (default: current directory)"),
    output: Optional[str] = typer.Option(None, "-o", "--output", help="Output file for project rules"),
    ai_enhanced: bool = typer.Option(False, "--ai", help="Use AI-enhanced analysis (requires API key)"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Interactive review of suggestions"),
    confidence_threshold: float = typer.Option(0.7, "--threshold", help="Minimum confidence threshold for suggestions"),
    template: str = typer.Option("project_rules", "--template", help="Template to use (project_rules, detailed)")
):
    """Generate a clean project-rules.md file with organized sections"""
    print_header("📋 Generate Project Rules File")
    
    project_path = target_path or get_project_root()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
        ) as progress:
            
            # Step 1: Analyze project patterns
            task1 = progress.add_task("Analyzing project patterns...", total=100)
            suggester = get_rules_suggester(project_path)
            pattern_analysis = suggester.analyze_project_patterns()
            progress.update(task1, advance=40)
            
            # Step 2: Generate basic suggestions
            suggestions = suggester.suggest_rules()
            progress.update(task1, advance=30)
            
            # Step 3: AI enhancement (if requested)
            if ai_enhanced:
                task2 = progress.add_task("Enhancing with AI analysis...", total=100)
                try:
                    ai_analyzer = get_anthropic_rules_analyzer()
                    
                    # Collect code samples for AI analysis
                    code_samples = _collect_code_samples(project_path)
                    progress.update(task2, advance=40)
                    
                    # Get AI analysis
                    project_context = {
                        'project_type': 'general',
                        'size_category': 'medium'
                    }
                    
                    ai_result = asyncio.run(ai_analyzer.analyze_for_rules(
                        pattern_analysis, code_samples, project_context
                    ))
                    progress.update(task2, advance=40)
                    
                    # Merge AI suggestions with basic suggestions
                    suggestions.extend(ai_result.suggestions)
                    progress.update(task2, advance=20)
                    
                except Exception as e:
                    console.print(f"[yellow]⚠️[/yellow] AI enhancement failed: {e}")
                    console.print("[yellow]Continuing with basic analysis...[/yellow]")
            
            progress.update(task1, advance=30)
        
        # Filter by confidence threshold
        filtered_suggestions = [s for s in suggestions if s.confidence >= confidence_threshold]
        
        console.print(f"\n[green]✅[/green] Analysis complete! Found {len(filtered_suggestions)} suggestions")
        
        # Interactive review
        if interactive and filtered_suggestions:
            reviewed_suggestions = _interactive_suggestion_review(filtered_suggestions)
        else:
            reviewed_suggestions = filtered_suggestions
        
        # Generate project rules file
        if not output:
            output = f"{Path(project_path).name}-rules.md"
        
        _generate_project_rules_file(
            reviewed_suggestions, pattern_analysis, output, project_path, template
        )
        
        print_success(f"Generated project rules file: {output}")
        console.print(f"[dim]Use this file as your project's development guidelines[/dim]")
        
    except Exception as e:
        print_error(f"Failed to generate project rules: {e}")
        logger.error(f"Error in generate_project_rules: {e}")
        raise typer.Exit(1)


def _generate_project_rules_file(suggestions: List, pattern_analysis, 
                               output_path: str, project_path: str, template_name: str = "project_rules") -> None:
    """Generate a project rules file using the appropriate template"""
    
    # Choose template file
    if template_name == "project_rules":
        template_file = "project_rules_template.md"
    else:
        template_file = "suggested_rules_template.md"
    
    template_path = Path(__file__).parent.parent / "templates" / template_file
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        template = jinja2.Template(template_content)
        
        # Prepare enhanced data for project rules template
        template_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'project_name': Path(project_path).name,
            'project_description': f"AI-analyzed {Path(project_path).name} project with detected technologies: {', '.join(pattern_analysis.technology_stack[:3])}{'...' if len(pattern_analysis.technology_stack) > 3 else ''}",
            'confidence_score': pattern_analysis.confidence_score,
            'executive_summary': _generate_executive_summary(suggestions, pattern_analysis),
            'technology_stack': pattern_analysis.technology_stack,
            'tech_details': _generate_tech_details(pattern_analysis),
            'architectural_patterns': pattern_analysis.architectural_patterns,
            'current_practices': _extract_current_practices(pattern_analysis),
            'inconsistencies': _format_inconsistencies(pattern_analysis.inconsistencies),
            'suggestions': suggestions,
            'metrics': _calculate_project_metrics(pattern_analysis),
            'project_structure': _generate_project_structure(pattern_analysis)
        }
        
        # Render template
        rendered_content = template.render(**template_data)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered_content)
            
    except Exception as e:
        logger.error(f"Failed to generate project rules file: {e}")
        # Fallback to simple rules file
        _generate_simple_project_rules(suggestions, pattern_analysis, output_path, project_path)


def _generate_tech_details(pattern_analysis) -> Dict[str, str]:
    """Generate detailed descriptions for detected technologies"""
    tech_details = {}
    
    for tech in pattern_analysis.technology_stack:
        if 'python' in tech.lower():
            tech_details[tech] = "Primary language - follow PEP 8 standards"
        elif 'javascript' in tech.lower() or 'js' in tech.lower():
            tech_details[tech] = "Frontend/backend language - use modern ES6+ features"
        elif 'react' in tech.lower():
            tech_details[tech] = "Frontend framework - use functional components and hooks"
        elif 'django' in tech.lower():
            tech_details[tech] = "Web framework - follow Django best practices"
        elif 'flask' in tech.lower():
            tech_details[tech] = "Micro web framework - keep it simple and modular"
        elif 'fastapi' in tech.lower():
            tech_details[tech] = "Modern API framework - leverage async capabilities"
        elif 'node' in tech.lower():
            tech_details[tech] = "JavaScript runtime - use npm/yarn for dependencies"
        elif 'docker' in tech.lower():
            tech_details[tech] = "Containerization - maintain consistent environments"
        elif 'git' in tech.lower():
            tech_details[tech] = "Version control - follow conventional commit messages"
        else:
            tech_details[tech] = "Detected in project structure"
    
    return tech_details


def _generate_project_structure(pattern_analysis) -> str:
    """Generate a suggested project structure based on detected patterns"""
    structure_lines = []
    
    if 'python' in str(pattern_analysis.technology_stack).lower():
        structure_lines.append("src/")
        structure_lines.append("  ├── models/       # Data models and schemas")
        structure_lines.append("  ├── services/     # Business logic")
        structure_lines.append("  ├── utils/        # Helper functions")
        structure_lines.append("  ├── tests/        # Test files")
        structure_lines.append("  └── config/       # Configuration files")
        
        if 'django' in str(pattern_analysis.technology_stack).lower():
            structure_lines.append("  ├── apps/         # Django applications")
            structure_lines.append("  ├── templates/    # HTML templates")
            structure_lines.append("  └── static/       # Static files")
        elif 'flask' in str(pattern_analysis.technology_stack).lower():
            structure_lines.append("  ├── routes/       # Flask routes")
            structure_lines.append("  ├── templates/    # Jinja2 templates")
            structure_lines.append("  └── static/       # Static assets")
        elif 'fastapi' in str(pattern_analysis.technology_stack).lower():
            structure_lines.append("  ├── routers/      # API routers")
            structure_lines.append("  ├── dependencies/ # Dependency injection")
            structure_lines.append("  └── schemas/      # Pydantic models")
    
    elif 'javascript' in str(pattern_analysis.technology_stack).lower():
        structure_lines.append("src/")
        structure_lines.append("  ├── components/   # Reusable components")
        structure_lines.append("  ├── services/     # API and business logic")
        structure_lines.append("  ├── utils/        # Helper functions")
        structure_lines.append("  ├── tests/        # Test files")
        structure_lines.append("  └── assets/       # Static assets")
        
        if 'react' in str(pattern_analysis.technology_stack).lower():
            structure_lines.append("  ├── hooks/        # Custom React hooks")
            structure_lines.append("  ├── context/      # React context providers")
            structure_lines.append("  └── pages/        # Page components")
    
    else:
        # Generic structure
        structure_lines.append("src/")
        structure_lines.append("  ├── core/         # Core functionality")
        structure_lines.append("  ├── utils/        # Utilities")
        structure_lines.append("  ├── tests/        # Tests")
        structure_lines.append("  └── docs/         # Documentation")
    
    return "\n".join(structure_lines)


def _generate_simple_project_rules(suggestions: List, pattern_analysis, 
                                 output_path: str, project_path: str) -> None:
    """Generate a simple fallback project rules file"""
    content = f"""# {Path(project_path).name} - Development Rules

## Project Overview
Generated by AI analysis on {datetime.now().strftime('%Y-%m-%d')}

## Technology Constraints

### Detected Technologies
{chr(10).join(f'- {tech}' for tech in pattern_analysis.technology_stack)}

## Suggested Rules

{chr(10).join(f'### {s.suggested_rule.description}{chr(10)}{s.suggested_rule.content}{chr(10)}' for s in suggestions)}

---
*Generated by ProjectPrompt AI Rules Suggester*
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


# Helper functions

def _detect_project_context(project_root: str) -> Dict[str, Any]:
    """Auto-detect project context from files and structure"""
    context = {}
    
    # Check for common files
    if os.path.exists(os.path.join(project_root, "package.json")):
        context['has_nodejs'] = True
    if os.path.exists(os.path.join(project_root, "requirements.txt")) or os.path.exists(os.path.join(project_root, "pyproject.toml")):
        context['has_python'] = True
    if os.path.exists(os.path.join(project_root, "Dockerfile")):
        context['has_docker'] = True
    if os.path.exists(os.path.join(project_root, ".github")):
        context['has_github_actions'] = True
    
    return context


def _show_rules_summary(manager: EnhancedRulesManager):
    """Show a summary of loaded rules"""
    table = Table(title="Rules Summary", show_header=True, header_style="bold magenta")
    table.add_column("Category", style="cyan")
    table.add_column("Mandatory", justify="center", style="red")
    table.add_column("Recommended", justify="center", style="yellow")
    table.add_column("Optional", justify="center", style="green")
    table.add_column("Total", justify="center", style="bold")
    
    from src.models.rule_models import RuleCategory, RulePriority
    
    categories = [RuleCategory.TECHNOLOGY, RuleCategory.ARCHITECTURE, RuleCategory.CODE_STYLE, 
                 RuleCategory.TESTING, RuleCategory.DOCUMENTATION]
    
    for category in categories:
        cat_rules = manager.get_rules_by_category(category)
        if not cat_rules:
            continue
            
        mandatory = len([r for r in cat_rules if r.priority == RulePriority.MANDATORY])
        recommended = len([r for r in cat_rules if r.priority == RulePriority.RECOMMENDED])
        optional = len([r for r in cat_rules if r.priority == RulePriority.OPTIONAL])
        total = len(cat_rules)
        
        table.add_row(
            category.value.title(),
            str(mandatory),
            str(recommended),
            str(optional),
            str(total)
        )
    
    console.print(table)


def _show_validation_details(validation_results: Dict[str, Any]):
    """Show detailed validation results"""
    console.print("\n[bold]Validation Details:[/bold]")
    
    if validation_results.get('syntax_valid'):
        print_success("Syntax is valid")
    
    if validation_results.get('structure_valid'):
        print_success("Structure is valid")
    
    conflicts = validation_results.get('conflicts', [])
    if conflicts:
        print_warning(f"Found {len(conflicts)} potential rule conflicts:")
        for conflict in conflicts:
            console.print(f"  • {conflict}")


def _apply_rules_to_project(manager: EnhancedRulesManager, rules: List, target: str, dry_run: bool, interactive: bool) -> Dict[str, Any]:
    """Apply rules to project and return results"""
    results = {
        'applied_rules': [],
        'violations': [],
        'suggestions': [],
        'files_processed': 0,
        'total_rules': len(rules)
    }
    
    # This is a simplified implementation
    # In a real scenario, this would analyze each file and apply rules
    print_info("Rule application analysis complete")
    print_warning("Full rule application engine coming in next iteration")
    
    return results


def _show_application_results(results: Dict[str, Any]):
    """Display rule application results"""
    print_header("Application Results")
    
    print_info(f"Processed {results['files_processed']} files")
    print_info(f"Applied {len(results['applied_rules'])} rules")
    
    if results['violations']:
        print_warning(f"Found {len(results['violations'])} violations")
    else:
        print_success("No violations found!")


def _save_application_results(results: Dict[str, Any], output_path: str):
    """Save application results to file"""
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)


def _get_project_type_description(project_type: str) -> str:
    """Get description for project type"""
    descriptions = {
        'web_app': 'Frontend/backend web applications',
        'data_science': 'Data analysis and machine learning projects',
        'api_service': 'REST APIs and microservices',
        'cli_tool': 'Command-line tools and utilities'
    }
    return descriptions.get(project_type, 'Unknown project type')


def _collect_code_samples(project_path: str, max_samples: int = 5) -> List[str]:
    """Collect representative code samples for AI analysis"""
    samples = []
    
    # Common file patterns to sample
    patterns = ['*.py', '*.js', '*.ts', '*.java', '*.cpp', '*.c']
    
    for pattern in patterns:
        files = list(Path(project_path).rglob(pattern))
        if files:
            # Sample a few files
            for file_path in files[:max_samples // len(patterns) + 1]:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if len(content) > 100:  # Skip very small files
                            samples.append(content[:2000])  # Limit sample size
                except Exception:
                    continue
        
        if len(samples) >= max_samples:
            break
    
    return samples


def _interactive_suggestion_review(suggestions: List) -> List:
    """Interactive review of suggestions"""
    console.print("\n[cyan]📋 Review AI Suggestions[/cyan]")
    console.print("Review each suggestion and choose to accept, reject, or modify it.\n")
    
    accepted_suggestions = []
    
    for i, suggestion in enumerate(suggestions, 1):
        console.print(f"\n[bold cyan]Suggestion {i}/{len(suggestions)}[/bold cyan]")
        
        # Display suggestion details
        panel_content = f"""[bold]{suggestion.suggested_rule.description}[/bold]

[yellow]Rule:[/yellow] {suggestion.suggested_rule.content}

[yellow]Category:[/yellow] {suggestion.suggested_rule.category.value.title()}
[yellow]Priority:[/yellow] {suggestion.suggested_rule.priority.value.title()}
[yellow]Confidence:[/yellow] {suggestion.confidence:.2f}/1.0

[yellow]Reasoning:[/yellow] {suggestion.reasoning}"""
        
        console.print(Panel(panel_content, title="Suggestion Details"))
        
        # Get user choice
        choice = typer.prompt(
            "Accept this suggestion? (y)es/(n)o/(m)odify/(s)kip remaining",
            type=str,
            default="y"
        ).lower()
        
        if choice == 'y':
            accepted_suggestions.append(suggestion)
        elif choice == 'm':
            # Allow modification
            new_content = typer.prompt("Enter modified rule content", 
                                     default=suggestion.suggested_rule.content)
            suggestion.suggested_rule.content = new_content
            accepted_suggestions.append(suggestion)
        elif choice == 's':
            # Skip remaining and keep what we have
            break
        # 'n' just skips this suggestion
    
    console.print(f"\n[green]✅[/green] Accepted {len(accepted_suggestions)} out of {len(suggestions)} suggestions")
    return accepted_suggestions


def _display_suggestions_summary(suggestions: List, pattern_analysis) -> None:
    """Display a summary of suggestions"""
    console.print("\n[bold cyan]📊 Suggestions Summary[/bold cyan]")
    
    # Group by category
    by_category = {}
    for suggestion in suggestions:
        category = suggestion.suggested_rule.category.value
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(suggestion)
    
    # Create summary table
    table = Table(title="Rule Suggestions by Category")
    table.add_column("Category", style="cyan")
    table.add_column("Count", justify="right", style="magenta")
    table.add_column("Avg Confidence", justify="right", style="green")
    table.add_column("Top Priority", style="yellow")
    
    for category, cat_suggestions in by_category.items():
        count = len(cat_suggestions)
        avg_conf = sum(s.confidence for s in cat_suggestions) / count
        priorities = [s.suggested_rule.priority.value for s in cat_suggestions]
        top_priority = max(priorities, key=lambda x: {'mandatory': 3, 'recommended': 2, 'optional': 1}[x])
        
        table.add_row(
            category.title(),
            str(count),
            f"{avg_conf:.2f}",
            top_priority.title()
        )
    
    console.print(table)
    
    # Display pattern analysis summary
    console.print(f"\n[bold cyan]🔍 Pattern Analysis[/bold cyan]")
    console.print(f"Technologies: {', '.join(pattern_analysis.technology_stack) or 'None detected'}")
    console.print(f"Architecture: {', '.join(pattern_analysis.architectural_patterns) or 'None detected'}")
    console.print(f"Confidence: {pattern_analysis.confidence_score:.2f}/1.0")


def _display_pattern_analysis(analysis, detailed: bool) -> None:
    """Display pattern analysis results"""
    # Technology stack
    if analysis.technology_stack:
        table = Table(title="Detected Technologies")
        table.add_column("Technology", style="cyan")
        table.add_column("Status", style="green")
        
        for tech in analysis.technology_stack:
            table.add_row(tech.title(), "✅ Detected")
        console.print(table)
    
    # Architectural patterns
    if analysis.architectural_patterns:
        console.print(f"\n[bold cyan]🏗️ Architectural Patterns[/bold cyan]")
        for pattern in analysis.architectural_patterns:
            console.print(f"  • {pattern.replace('_', ' ').title()}")
    
    # Inconsistencies
    if analysis.inconsistencies:
        console.print(f"\n[bold yellow]⚠️ Inconsistencies Found[/bold yellow]")
        for inconsistency in analysis.inconsistencies:
            console.print(f"  • {inconsistency}")
    
    # Detailed analysis
    if detailed:
        console.print(f"\n[bold cyan]📋 Detailed Analysis[/bold cyan]")
        
        if analysis.code_style_patterns:
            console.print("\n[yellow]Code Style Patterns:[/yellow]")
            for key, value in analysis.code_style_patterns.items():
                console.print(f"  • {key}: {value}")
        
        if analysis.testing_patterns:
            console.print(f"\n[yellow]Testing Patterns:[/yellow]")
            for pattern in analysis.testing_patterns:
                console.print(f"  • {pattern}")
        
        if analysis.documentation_patterns:
            console.print(f"\n[yellow]Documentation Patterns:[/yellow]")
            for pattern in analysis.documentation_patterns:
                console.print(f"  • {pattern}")
        
        if analysis.security_patterns:
            console.print(f"\n[yellow]Security Patterns:[/yellow]")
            for pattern in analysis.security_patterns:
                console.print(f"  • {pattern}")
    
    console.print(f"\n[bold green]Overall Confidence: {analysis.confidence_score:.2f}/1.0[/bold green]")


def _generate_suggestions_output(suggestions: List, pattern_analysis, 
                               output_path: Optional[str], format: str, 
                               project_path: str) -> None:
    """Generate output file with suggestions"""
    
    # Create project-output/suggestions directory for rules
    project_suggestions_dir = os.path.join(project_path, "project-output", "suggestions", "rules")
    os.makedirs(project_suggestions_dir, exist_ok=True)
    
    if format == "yaml":
        # Generate YAML rules file
        suggester = get_rules_suggester(project_path)
        if not output_path:
            output_path = os.path.join(project_suggestions_dir, "suggested_rules.yaml")
        elif not os.path.isabs(output_path) and not output_path.startswith('project-output'):
            # Relative path - place in project-output structure
            output_path = os.path.join(project_suggestions_dir, output_path)
        suggester.generate_draft_rules_file(suggestions, output_path)
        
    elif format == "json":
        # Generate JSON output
        if not output_path:
            output_path = os.path.join(project_suggestions_dir, "suggestions.json")
        elif not os.path.isabs(output_path) and not output_path.startswith('project-output'):
            # Relative path - place in project-output structure
            output_path = os.path.join(project_suggestions_dir, output_path)
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'project_path': project_path,
            'pattern_analysis': {
                'technology_stack': pattern_analysis.technology_stack,
                'architectural_patterns': pattern_analysis.architectural_patterns,
                'confidence_score': pattern_analysis.confidence_score
            },
            'suggestions': [
                {
                    'rule': {
                        'content': s.suggested_rule.content,
                        'category': s.suggested_rule.category.value,
                        'priority': s.suggested_rule.priority.value,
                        'description': s.suggested_rule.description
                    },
                    'reasoning': s.reasoning,
                    'confidence': s.confidence
                }
                for s in suggestions
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    elif format == "markdown":
        # Generate detailed markdown report
        if not output_path:
            output_path = os.path.join(project_suggestions_dir, "suggestions_report.md")
        elif not os.path.isabs(output_path) and not output_path.startswith('project-output'):
            # Relative path - place in project-output structure
            output_path = os.path.join(project_suggestions_dir, output_path)
        
        _generate_markdown_report(suggestions, pattern_analysis, output_path, project_path)
    
    print_success(f"Suggestions saved to {output_path}")


def _generate_markdown_report(suggestions: List, pattern_analysis, 
                            output_path: str, project_path: str) -> None:
    """Generate a detailed markdown report"""
    
    # Load template
    template_path = Path(__file__).parent.parent / "templates" / "suggested_rules_template.md"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        template = jinja2.Template(template_content)
        
        # Prepare data for template
        template_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'project_name': Path(project_path).name,
            'confidence_score': pattern_analysis.confidence_score,
            'executive_summary': _generate_executive_summary(suggestions, pattern_analysis),
            'technology_stack': pattern_analysis.technology_stack,
            'architectural_patterns': pattern_analysis.architectural_patterns,
            'current_practices': _extract_current_practices(pattern_analysis),
            'inconsistencies': _format_inconsistencies(pattern_analysis.inconsistencies),
            'suggestions': suggestions,
            'metrics': _calculate_project_metrics(pattern_analysis)
        }
        
        # Render template
        rendered_content = template.render(**template_data)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered_content)
            
    except Exception as e:
        logger.error(f"Failed to generate markdown report: {e}")
        # Fallback to simple report
        _generate_simple_markdown_report(suggestions, pattern_analysis, output_path)


def _generate_executive_summary(suggestions: List, pattern_analysis) -> str:
    """Generate executive summary for the report"""
    high_priority = len([s for s in suggestions if s.suggested_rule.priority.value == 'mandatory'])
    medium_priority = len([s for s in suggestions if s.suggested_rule.priority.value == 'recommended'])
    
    return f"""Based on comprehensive analysis of your project, we identified {len(pattern_analysis.technology_stack)} 
technologies and {len(pattern_analysis.architectural_patterns)} architectural patterns. The analysis generated 
{len(suggestions)} actionable rule suggestions with an overall confidence of {pattern_analysis.confidence_score:.1f}/1.0.

Key findings include {high_priority} high-priority rules that should be implemented immediately, and 
{medium_priority} recommended improvements for enhanced code quality and maintainability."""


def _extract_current_practices(pattern_analysis) -> List[str]:
    """Extract current good practices from analysis"""
    practices = []
    
    if pattern_analysis.testing_patterns:
        practices.append(f"Testing framework in use: {', '.join(pattern_analysis.testing_patterns)}")
    
    if pattern_analysis.documentation_patterns:
        practices.append(f"Documentation practices: {', '.join(pattern_analysis.documentation_patterns)}")
    
    if pattern_analysis.security_patterns:
        practices.append(f"Security measures: {', '.join(pattern_analysis.security_patterns)}")
    
    return practices


def _format_inconsistencies(inconsistencies: List[str]) -> List[Dict[str, str]]:
    """Format inconsistencies for template"""
    formatted = []
    
    for inconsistency in inconsistencies:
        formatted.append({
            'type': 'Naming Convention',
            'description': inconsistency,
            'impact': 'Medium - affects code readability',
            'suggested_fix': 'Establish consistent naming standards'
        })
    
    return formatted


def _calculate_project_metrics(pattern_analysis) -> Dict[str, Any]:
    """Calculate project health metrics"""
    # Simple scoring based on detected patterns
    consistency_score = 8 if not pattern_analysis.inconsistencies else 6
    documentation_score = 7 if pattern_analysis.documentation_patterns else 4
    testing_score = 8 if pattern_analysis.testing_patterns else 3
    security_score = 7 if pattern_analysis.security_patterns else 5
    
    return {
        'consistency_score': consistency_score,
        'documentation_score': documentation_score,
        'testing_score': testing_score,
        'security_score': security_score,
        'projected_consistency': min(consistency_score + 2, 10),
        'projected_documentation': min(documentation_score + 3, 10),
        'projected_testing': min(testing_score + 4, 10),
        'projected_security': min(security_score + 2, 10),
        'consistency_improvement': 2,
        'documentation_improvement': 3,
        'testing_improvement': 4,
        'security_improvement': 2
    }


def _generate_simple_markdown_report(suggestions: List, pattern_analysis, output_path: str) -> None:
    """Generate a simple markdown report as fallback"""
    content = f"""# AI-Generated Rules Suggestions

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Analysis Summary

- **Technologies Detected**: {', '.join(pattern_analysis.technology_stack) or 'None'}
- **Architectural Patterns**: {', '.join(pattern_analysis.architectural_patterns) or 'None'}
- **Confidence Score**: {pattern_analysis.confidence_score:.2f}/1.0
- **Total Suggestions**: {len(suggestions)}

## Suggested Rules

"""
    
    for i, suggestion in enumerate(suggestions, 1):
        content += f"""### {i}. {suggestion.suggested_rule.description}

**Rule**: {suggestion.suggested_rule.content}

**Category**: {suggestion.suggested_rule.category.value.title()}  
**Priority**: {suggestion.suggested_rule.priority.value.title()}  
**Confidence**: {suggestion.confidence:.2f}/1.0

**Reasoning**: {suggestion.reasoning}

---

"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


@rules_app.command()
def generate_structured_rules(
    project_path: str = typer.Argument(".", help="Path to the project directory"),
    output_file: str = typer.Option("project_rules.yaml", "--output", "-o", help="Output file path"),
    confidence_threshold: float = typer.Option(0.7, "--confidence", "-c", help="Minimum confidence threshold (0.0-1.0)"),
    use_ai: bool = typer.Option(False, "--ai", help="Use AI-powered analysis (requires API key)"),
    project_type: Optional[str] = typer.Option(None, "--type", "-t", help="Project type (web_application, data_science, api_service, cli_tool)")
):
    """Generate structured rules using the sophisticated rule models system"""
    
    if StructuredRulesSuggester is None:
        print_error("Structured rules suggester not available")
        raise typer.Exit(1)
    
    print_header("🏗️  Generating Structured Rules")
    
    async def generate_rules():
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                
                # Initialize suggester
                task = progress.add_task("Initializing structured rules suggester...", total=100)
                suggester = StructuredRulesSuggester(project_path)
                progress.update(task, advance=20)
                
                # Generate structured rules
                progress.update(task, description="Analyzing project patterns...")
                progress.update(task, advance=30)
                
                rule_set = await suggester.suggest_structured_rules(
                    confidence_threshold=confidence_threshold,
                    use_ai=use_ai,
                    project_type=project_type
                )
                progress.update(task, advance=40)
                
                # Export to YAML
                progress.update(task, description="Exporting to YAML...")
                yaml_content = rule_set.to_yaml()
                progress.update(task, advance=10)
                
                # Save to file
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(yaml_content)
                
                progress.update(task, advance=10, description="Complete!")
            
            # Display results
            console.print(f"\n[green]✅[/green] Structured rules generated successfully!")
            
            # Show summary table
            table = Table(title="Generated Rule Set Summary")
            table.add_column("Property", style="cyan", no_wrap=True)
            table.add_column("Value", style="white")
            
            table.add_row("Rule Set Name", rule_set.name)
            table.add_row("Version", rule_set.version)
            table.add_row("Description", rule_set.description)
            table.add_row("Total Groups", str(len(rule_set.groups)))
            
            total_rules = sum(len(group.rules) for group in rule_set.groups)
            table.add_row("Total Rules", str(total_rules))
            
            if rule_set.metadata:
                table.add_row("Project Type", rule_set.metadata.get('project_type', 'Unknown'))
                table.add_row("AI Enhanced", str(rule_set.metadata.get('ai_enhanced', False)))
            
            console.print(table)
            
            # Show groups breakdown
            if rule_set.groups:
                console.print(f"\n[bold cyan]Rule Groups:[/bold cyan]")
                for group in rule_set.groups:
                    console.print(f"  • {group.name}: {len(group.rules)} rules ({group.category.value})")
            
            console.print(f"\n[bold]Output saved to:[/bold] {output_file}")
            
            # Show first few rules as examples
            if rule_set.groups and rule_set.groups[0].rules:
                console.print(f"\n[bold cyan]Example Rules:[/bold cyan]")
                for i, rule in enumerate(rule_set.groups[0].rules[:3], 1):
                    console.print(f"  {i}. [bold]{rule.content[:80]}{'...' if len(rule.content) > 80 else ''}[/bold]")
                    console.print(f"     Priority: {rule.priority.value}, Category: {rule.category.value}")
                
                if len(rule_set.groups[0].rules) > 3:
                    remaining = len(rule_set.groups[0].rules) - 3
                    console.print(f"     ... and {remaining} more rules in this group")
        
        except Exception as e:
            print_error(f"Failed to generate structured rules: {str(e)}")
            logger.error(f"Structured rules generation error: {e}", exc_info=True)
            raise typer.Exit(1)
    
    # Run the async function
    asyncio.run(generate_rules())


@rules_app.command()
def validate_structured_rules(
    rules_file: str = typer.Argument(..., help="Path to the YAML rules file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed validation results")
):
    """Validate a structured rules YAML file"""
    
    if StructuredRulesSuggester is None:
        print_error("Structured rules suggester not available")
        raise typer.Exit(1)
    
    print_header("🔍 Validating Structured Rules")
    
    try:
        from src.models.rule_models import RuleSet
        
        # Load and validate the rule set
        rule_set = RuleSet.from_yaml_file(rules_file)
        
        console.print(f"[green]✅[/green] Rules file is valid!")
        
        # Show summary
        table = Table(title="Validation Results")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Rule Set Name", rule_set.name)
        table.add_row("Version", rule_set.version)
        table.add_row("Groups", str(len(rule_set.groups)))
        
        total_rules = sum(len(group.rules) for group in rule_set.groups)
        table.add_row("Total Rules", str(total_rules))
        
        # Count by priority
        priority_counts = {}
        for group in rule_set.groups:
            for rule in group.rules:
                priority = rule.priority.value
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        for priority, count in priority_counts.items():
            table.add_row(f"{priority.title()} Priority", str(count))
        
        console.print(table)
        
        if verbose:
            console.print(f"\n[bold cyan]Detailed Breakdown:[/bold cyan]")
            for group in rule_set.groups:
                console.print(f"\n[bold]{group.name}[/bold] ({group.category.value})")
                console.print(f"  Description: {group.description}")
                console.print(f"  Rules: {len(group.rules)}")
                
                for rule in group.rules[:2]:  # Show first 2 rules
                    console.print(f"    • {rule.content[:60]}{'...' if len(rule.content) > 60 else ''}")
                
                if len(group.rules) > 2:
                    console.print(f"    ... and {len(group.rules) - 2} more rules")
    
    except FileNotFoundError:
        print_error(f"Rules file not found: {rules_file}")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Validation failed: {str(e)}")
        logger.error(f"Rules validation error: {e}", exc_info=True)
        raise typer.Exit(1)
