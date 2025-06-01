#!/usr/bin/env python3
"""
Interactive Rules Wizard for ProjectPrompt

This module provides an interactive wizard for setting up and configuring
project rules with step-by-step guidance and smart defaults.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
from rich.columns import Columns

from src.models.rule_models import RuleItem, RuleCategory, RulePriority
from src.utils.enhanced_rules_manager import EnhancedRulesManager
from src.utils.logger import get_logger

console = Console()
logger = get_logger()


class RulesWizard:
    """Interactive wizard for rules configuration"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.rules_manager = EnhancedRulesManager(project_root)
        self.context = {}
        self.selected_rules = []
        
    def run(self) -> bool:
        """Run the complete rules wizard"""
        try:
            console.print(Panel.fit(
                "[bold cyan]🧙‍♂️ ProjectPrompt Rules Configuration Wizard[/bold cyan]\n\n"
                "This wizard will help you set up comprehensive rules for your project.\n"
                "We'll analyze your project structure and guide you through the configuration process.",
                title="Welcome",
                border_style="cyan"
            ))
            
            # Step 1: Project Analysis
            if not self._analyze_project():
                return False
                
            # Step 2: Project Type Selection
            if not self._select_project_type():
                return False
                
            # Step 3: Rules Category Selection
            if not self._configure_rule_categories():
                return False
                
            # Step 4: Template Selection and Customization
            if not self._customize_templates():
                return False
                
            # Step 5: Priority Configuration
            if not self._configure_priorities():
                return False
                
            # Step 6: Final Review and Confirmation
            if not self._final_review():
                return False
                
            # Step 7: Generate Rules File
            return self._generate_rules()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️ Wizard cancelled by user[/yellow]")
            return False
        except Exception as e:
            logger.error(f"Wizard error: {e}")
            console.print(f"[red]❌ Error: {e}[/red]")
            return False
    
    def _analyze_project(self) -> bool:
        """Analyze the current project structure"""
        console.print("\n[bold]📊 Step 1: Project Analysis[/bold]")
        
        # Detect project characteristics
        self.context = self._detect_project_context()
        
        # Display findings
        table = Table(title="Project Analysis Results", show_header=True, header_style="bold magenta")
        table.add_column("Aspect", style="cyan")
        table.add_column("Detection", style="green")
        table.add_column("Confidence", style="yellow")
        
        for aspect, details in self.context.items():
            if isinstance(details, dict):
                detection = details.get('detected', 'No')
                confidence = details.get('confidence', 'N/A')
                table.add_row(aspect.replace('_', ' ').title(), str(detection), str(confidence))
            else:
                table.add_row(aspect.replace('_', ' ').title(), str(details), "High")
        
        console.print(table)
        
        # Ask for confirmation or manual override
        if not Confirm.ask("\nDoes this analysis look correct?", default=True):
            return self._manual_project_setup()
        
        return True
    
    def _detect_project_context(self) -> Dict[str, Any]:
        """Detect project context from file system"""
        context = {
            'languages': [],
            'frameworks': [],
            'tools': [],
            'project_type': 'unknown',
            'has_tests': False,
            'has_docs': False,
            'has_ci': False,
            'package_managers': []
        }
        
        project_path = Path(self.project_root)
        
        # Check for common files and directories
        files_found = list(project_path.rglob("*"))
        file_names = [f.name.lower() for f in files_found if f.is_file()]
        dir_names = [f.name.lower() for f in files_found if f.is_dir()]
        
        # Language detection
        if any(f.endswith('.py') for f in file_names):
            context['languages'].append('Python')
        if any(f.endswith(('.js', '.ts', '.jsx', '.tsx')) for f in file_names):
            context['languages'].append('JavaScript/TypeScript')
        if any(f.endswith(('.java', '.kt')) for f in file_names):
            context['languages'].append('Java/Kotlin')
        if any(f.endswith(('.go')) for f in file_names):
            context['languages'].append('Go')
        if any(f.endswith(('.rs')) for f in file_names):
            context['languages'].append('Rust')
        
        # Framework detection
        if 'package.json' in file_names:
            context['frameworks'].extend(['Node.js'])
            context['package_managers'].append('npm/yarn')
        if 'requirements.txt' in file_names or 'pyproject.toml' in file_names:
            context['package_managers'].append('pip/poetry')
        if 'go.mod' in file_names:
            context['package_managers'].append('go modules')
        if 'cargo.toml' in file_names:
            context['package_managers'].append('cargo')
        
        # Framework-specific detection
        if 'next.config.js' in file_names or 'next.config.ts' in file_names:
            context['frameworks'].append('Next.js')
        if 'nuxt.config.js' in file_names or 'nuxt.config.ts' in file_names:
            context['frameworks'].append('Nuxt.js')
        if 'django' in dir_names or 'manage.py' in file_names:
            context['frameworks'].append('Django')
        if 'flask' in dir_names or any('flask' in f for f in file_names):
            context['frameworks'].append('Flask')
        
        # Tools detection
        if 'dockerfile' in file_names or '.dockerignore' in file_names:
            context['tools'].append('Docker')
        if '.github' in dir_names:
            context['tools'].append('GitHub Actions')
            context['has_ci'] = True
        if '.gitlab-ci.yml' in file_names:
            context['tools'].append('GitLab CI')
            context['has_ci'] = True
        if 'jenkins' in file_names or 'jenkinsfile' in file_names:
            context['tools'].append('Jenkins')
            context['has_ci'] = True
        
        # Test detection
        test_dirs = ['test', 'tests', '__tests__', 'spec', 'specs']
        test_files = [f for f in file_names if any(test_term in f for test_term in ['test', 'spec'])]
        context['has_tests'] = any(d in dir_names for d in test_dirs) or len(test_files) > 0
        
        # Documentation detection
        doc_files = ['readme.md', 'readme.rst', 'readme.txt', 'docs']
        context['has_docs'] = any(f in file_names for f in doc_files) or 'docs' in dir_names
        
        # Project type inference
        if 'next.js' in context['frameworks'] or 'nuxt.js' in context['frameworks']:
            context['project_type'] = 'web_app'
        elif 'flask' in context['frameworks'] or 'django' in context['frameworks']:
            context['project_type'] = 'api_service'
        elif any('notebook' in f or f.endswith('.ipynb') for f in file_names):
            context['project_type'] = 'data_science'
        elif 'cli' in dir_names or any('main.py' in f or 'cli.py' in f for f in file_names):
            context['project_type'] = 'cli_tool'
        else:
            context['project_type'] = 'web_app'  # Default
        
        return context
    
    def _manual_project_setup(self) -> bool:
        """Allow manual override of project detection"""
        console.print("\n[bold]✏️ Manual Project Configuration[/bold]")
        
        # Project type selection
        project_types = ['web_app', 'api_service', 'data_science', 'cli_tool', 'other']
        console.print("\nAvailable project types:")
        for i, ptype in enumerate(project_types, 1):
            console.print(f"  {i}. {ptype.replace('_', ' ').title()}")
        
        while True:
            choice = IntPrompt.ask("Select project type", default=1)
            if 1 <= choice <= len(project_types):
                self.context['project_type'] = project_types[choice - 1]
                break
            console.print("[red]Invalid choice. Please try again.[/red]")
        
        # Language selection
        languages = ['Python', 'JavaScript/TypeScript', 'Java/Kotlin', 'Go', 'Rust', 'Other']
        self.context['languages'] = self._multi_select("Select languages used", languages)
        
        # Framework selection (if applicable)
        if 'JavaScript/TypeScript' in self.context['languages']:
            js_frameworks = ['React', 'Vue.js', 'Angular', 'Next.js', 'Nuxt.js', 'Express.js']
            selected_frameworks = self._multi_select("Select JavaScript/TypeScript frameworks", js_frameworks)
            self.context['frameworks'].extend(selected_frameworks)
        
        if 'Python' in self.context['languages']:
            py_frameworks = ['Django', 'Flask', 'FastAPI', 'Tornado', 'Pyramid']
            selected_frameworks = self._multi_select("Select Python frameworks", py_frameworks)
            self.context['frameworks'].extend(selected_frameworks)
        
        # Additional tools
        tools = ['Docker', 'GitHub Actions', 'GitLab CI', 'Jenkins', 'Kubernetes']
        self.context['tools'] = self._multi_select("Select additional tools", tools)
        
        return True
    
    def _multi_select(self, prompt: str, options: List[str]) -> List[str]:
        """Helper for multi-selection prompts"""
        console.print(f"\n{prompt}:")
        for i, option in enumerate(options, 1):
            console.print(f"  {i}. {option}")
        
        selected = []
        while True:
            choice_str = Prompt.ask("Select options (comma-separated numbers, or 'done' to finish)", default="done")
            if choice_str.lower() == 'done':
                break
            
            try:
                choices = [int(x.strip()) for x in choice_str.split(',')]
                for choice in choices:
                    if 1 <= choice <= len(options) and options[choice - 1] not in selected:
                        selected.append(options[choice - 1])
                        console.print(f"[green]✅ Added: {options[choice - 1]}[/green]")
            except ValueError:
                console.print("[red]Invalid input. Please enter numbers separated by commas.[/red]")
        
        return selected
    
    def _select_project_type(self) -> bool:
        """Confirm or modify project type selection"""
        console.print("\n[bold]🎯 Step 2: Project Type Configuration[/bold]")
        
        current_type = self.context.get('project_type', 'unknown')
        console.print(f"Detected project type: [cyan]{current_type.replace('_', ' ').title()}[/cyan]")
        
        if not Confirm.ask("Is this correct?", default=True):
            project_types = ['web_app', 'api_service', 'data_science', 'cli_tool']
            console.print("\nAvailable project types:")
            for i, ptype in enumerate(project_types, 1):
                console.print(f"  {i}. {ptype.replace('_', ' ').title()}")
            
            while True:
                choice = IntPrompt.ask("Select correct project type", default=1)
                if 1 <= choice <= len(project_types):
                    self.context['project_type'] = project_types[choice - 1]
                    break
                console.print("[red]Invalid choice. Please try again.[/red]")
        
        return True
    
    def _configure_rule_categories(self) -> bool:
        """Configure which rule categories to include"""
        console.print("\n[bold]📂 Step 3: Rule Categories Configuration[/bold]")
        
        categories = [cat.value for cat in RuleCategory]
        console.print("Available rule categories:")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Category", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Recommended", style="green")
        
        category_descriptions = {
            'TECHNOLOGY': 'Technology stack and dependencies',
            'ARCHITECTURE': 'System design and structural patterns',
            'CODE_STYLE': 'Coding standards and formatting',
            'TESTING': 'Testing strategies and requirements',
            'DOCUMENTATION': 'Documentation standards and practices'
        }
        
        recommended = {
            'web_app': ['TECHNOLOGY', 'ARCHITECTURE', 'CODE_STYLE', 'TESTING'],
            'api_service': ['TECHNOLOGY', 'ARCHITECTURE', 'CODE_STYLE', 'TESTING', 'DOCUMENTATION'],
            'data_science': ['TECHNOLOGY', 'CODE_STYLE', 'DOCUMENTATION'],
            'cli_tool': ['TECHNOLOGY', 'CODE_STYLE', 'TESTING', 'DOCUMENTATION']
        }
        
        project_type = self.context.get('project_type', 'web_app')
        project_recommended = recommended.get(project_type, categories)
        
        for cat in categories:
            is_recommended = "Yes" if cat in project_recommended else "No"
            table.add_row(cat, category_descriptions.get(cat, ""), is_recommended)
        
        console.print(table)
        
        if Confirm.ask("\nUse recommended categories for your project type?", default=True):
            self.context['selected_categories'] = project_recommended
        else:
            self.context['selected_categories'] = self._multi_select("Select categories to include", categories)
        
        console.print(f"\n[green]✅ Selected categories: {', '.join(self.context['selected_categories'])}[/green]")
        return True
    
    def _customize_templates(self) -> bool:
        """Load and customize rule templates"""
        console.print("\n[bold]🎨 Step 4: Template Customization[/bold]")
        
        project_type = self.context.get('project_type', 'web_app')
        
        # Load template rules
        try:
            template_rules = self.rules_manager.load_template_rules(project_type)
            console.print(f"Loaded {len(template_rules)} template rules for {project_type}")
            
            # Filter by selected categories
            selected_categories = self.context.get('selected_categories', [])
            filtered_rules = [
                rule for rule in template_rules 
                if rule.category.value in selected_categories
            ]
            
            console.print(f"Filtered to {len(filtered_rules)} rules based on selected categories")
            
            # Display rules by category
            self._display_rules_by_category(filtered_rules)
            
            # Allow customization
            if Confirm.ask("\nWould you like to customize these rules?", default=False):
                filtered_rules = self._customize_rule_list(filtered_rules)
            
            self.selected_rules = filtered_rules
            return True
            
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
            console.print(f"[red]❌ Error loading templates: {e}[/red]")
            return False
    
    def _display_rules_by_category(self, rules: List[RuleItem]):
        """Display rules organized by category"""
        by_category = {}
        for rule in rules:
            category = rule.category.value
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(rule)
        
        for category, cat_rules in by_category.items():
            console.print(f"\n[bold cyan]{category} ({len(cat_rules)} rules)[/bold cyan]")
            
            table = Table(show_header=True, header_style="bold")
            table.add_column("Rule", style="white", width=30)
            table.add_column("Priority", style="yellow", width=12)
            table.add_column("Description", style="cyan")
            
            for rule in cat_rules:
                priority_color = {
                    'MANDATORY': 'red',
                    'RECOMMENDED': 'yellow',
                    'OPTIONAL': 'green'
                }.get(rule.priority.value, 'white')
                
                # Use content as rule name if no description, or truncate description
                rule_name = rule.description[:30] + "..." if rule.description and len(rule.description) > 30 else (rule.description or rule.content[:30] + "...")
                rule_desc = rule.content[:60] + "..." if len(rule.content) > 60 else rule.content
                
                table.add_row(
                    rule_name,
                    f"[{priority_color}]{rule.priority.value}[/{priority_color}]",
                    rule_desc
                )
            
            console.print(table)
    
    def _customize_rule_list(self, rules: List[RuleItem]) -> List[RuleItem]:
        """Allow interactive customization of rule list"""
        console.print("\n[bold]Rule Customization Options:[/bold]")
        console.print("1. Remove specific rules")
        console.print("2. Change rule priorities")
        console.print("3. Add custom rules")
        console.print("4. Done with customization")
        
        while True:
            choice = IntPrompt.ask("Select option", default=4)
            
            if choice == 1:
                rules = self._remove_rules(rules)
            elif choice == 2:
                rules = self._change_priorities(rules)
            elif choice == 3:
                rules = self._add_custom_rules(rules)
            elif choice == 4:
                break
            else:
                console.print("[red]Invalid choice[/red]")
        
        return rules
    
    def _remove_rules(self, rules: List[RuleItem]) -> List[RuleItem]:
        """Remove specific rules interactively"""
        console.print("\n[bold]Remove Rules[/bold]")
        
        for i, rule in enumerate(rules, 1):
            rule_name = rule.description[:40] + "..." if rule.description and len(rule.description) > 40 else (rule.description or rule.content[:40] + "...")
            console.print(f"{i}. {rule_name} ({rule.priority.value})")
        
        remove_str = Prompt.ask("Enter rule numbers to remove (comma-separated)", default="")
        if not remove_str:
            return rules
        
        try:
            to_remove = [int(x.strip()) - 1 for x in remove_str.split(',')]
            new_rules = [rule for i, rule in enumerate(rules) if i not in to_remove]
            console.print(f"[green]✅ Removed {len(rules) - len(new_rules)} rules[/green]")
            return new_rules
        except ValueError:
            console.print("[red]Invalid input[/red]")
            return rules
    
    def _change_priorities(self, rules: List[RuleItem]) -> List[RuleItem]:
        """Change rule priorities interactively"""
        console.print("\n[bold]Change Rule Priorities[/bold]")
        
        for i, rule in enumerate(rules, 1):
            rule_name = rule.description[:40] + "..." if rule.description and len(rule.description) > 40 else (rule.description or rule.content[:40] + "...")
            console.print(f"{i}. {rule_name} - Current: {rule.priority.value}")
        
        rule_num = IntPrompt.ask("Select rule number to change priority (0 to skip)", default=0)
        if rule_num == 0 or rule_num > len(rules):
            return rules
        
        priorities = [p.value for p in RulePriority]
        console.print("Available priorities:")
        for i, priority in enumerate(priorities, 1):
            console.print(f"  {i}. {priority}")
        
        priority_choice = IntPrompt.ask("Select new priority", default=1)
        if 1 <= priority_choice <= len(priorities):
            rules[rule_num - 1].priority = RulePriority(priorities[priority_choice - 1])
            console.print(f"[green]✅ Changed priority to {priorities[priority_choice - 1]}[/green]")
        
        return rules
    
    def _add_custom_rules(self, rules: List[RuleItem]) -> List[RuleItem]:
        """Add custom rules interactively"""
        console.print("\n[bold]Add Custom Rule[/bold]")
        
        name = Prompt.ask("Rule name")
        description = Prompt.ask("Rule description")
        
        categories = [cat.value for cat in RuleCategory]
        console.print("Available categories:")
        for i, cat in enumerate(categories, 1):
            console.print(f"  {i}. {cat}")
        
        cat_choice = IntPrompt.ask("Select category", default=1)
        if not (1 <= cat_choice <= len(categories)):
            return rules
        
        priorities = [p.value for p in RulePriority]
        console.print("Available priorities:")
        for i, priority in enumerate(priorities, 1):
            console.print(f"  {i}. {priority}")
        
        priority_choice = IntPrompt.ask("Select priority", default=2)
        if not (1 <= priority_choice <= len(priorities)):
            return rules
        
        # Create custom rule
        custom_rule = RuleItem(
            content=description,
            priority=RulePriority(priorities[priority_choice - 1]),
            category=RuleCategory(categories[cat_choice - 1]),
            description=description
        )
        
        rules.append(custom_rule)
        console.print(f"[green]✅ Added custom rule: {name}[/green]")
        
        return rules
    
    def _configure_priorities(self) -> bool:
        """Configure priority levels and enforcement"""
        console.print("\n[bold]⚖️ Step 5: Priority Configuration[/bold]")
        
        # Count rules by priority
        priority_counts = {}
        for rule in self.selected_rules:
            priority = rule.priority.value
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Display current distribution
        table = Table(title="Rule Priority Distribution", show_header=True, header_style="bold magenta")
        table.add_column("Priority", style="cyan")
        table.add_column("Count", style="green")
        table.add_column("Description", style="white")
        
        priority_descriptions = {
            'MANDATORY': 'Must be followed - will cause errors',
            'RECOMMENDED': 'Should be followed - will cause warnings',
            'OPTIONAL': 'Nice to have - informational only'
        }
        
        for priority in ['MANDATORY', 'RECOMMENDED', 'OPTIONAL']:
            count = priority_counts.get(priority, 0)
            description = priority_descriptions.get(priority, '')
            color = {'MANDATORY': 'red', 'RECOMMENDED': 'yellow', 'OPTIONAL': 'green'}.get(priority, 'white')
            table.add_row(f"[{color}]{priority}[/{color}]", str(count), description)
        
        console.print(table)
        
        # Configure enforcement levels
        self.context['enforcement'] = {
            'mandatory_fails_build': Confirm.ask("Should MANDATORY rule violations fail the build?", default=True),
            'recommended_shows_warnings': Confirm.ask("Should RECOMMENDED rule violations show warnings?", default=True),
            'optional_in_reports': Confirm.ask("Should OPTIONAL rule violations appear in reports?", default=True)
        }
        
        return True
    
    def _final_review(self) -> bool:
        """Final review of configuration before generation"""
        console.print("\n[bold]📋 Step 6: Final Review[/bold]")
        
        # Display configuration summary
        panel_content = []
        
        panel_content.append(f"[bold]Project Type:[/bold] {self.context.get('project_type', 'unknown').replace('_', ' ').title()}")
        panel_content.append(f"[bold]Languages:[/bold] {', '.join(self.context.get('languages', []))}")
        panel_content.append(f"[bold]Frameworks:[/bold] {', '.join(self.context.get('frameworks', []))}")
        panel_content.append(f"[bold]Tools:[/bold] {', '.join(self.context.get('tools', []))}")
        panel_content.append(f"[bold]Categories:[/bold] {', '.join(self.context.get('selected_categories', []))}")
        panel_content.append(f"[bold]Total Rules:[/bold] {len(self.selected_rules)}")
        
        # Priority breakdown
        priority_counts = {}
        for rule in self.selected_rules:
            priority = rule.priority.value
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        priority_text = ", ".join([f"{p}: {c}" for p, c in priority_counts.items()])
        panel_content.append(f"[bold]Priority Distribution:[/bold] {priority_text}")
        
        console.print(Panel("\n".join(panel_content), title="Configuration Summary", border_style="green"))
        
        if not Confirm.ask("\nProceed with rules generation?", default=True):
            console.print("[yellow]⚠️ Configuration cancelled[/yellow]")
            return False
        
        return True
    
    def _generate_rules(self) -> bool:
        """Generate the final rules configuration file"""
        console.print("\n[bold]🔧 Step 7: Generating Rules Configuration[/bold]")
        
        try:
            # Prepare rules data
            rules_data = {
                'metadata': {
                    'version': '1.0',
                    'generated_by': 'ProjectPrompt Rules Wizard',
                    'generated_at': datetime.now().isoformat(),
                    'project_type': self.context.get('project_type'),
                    'context': self.context
                },
                'rules': [
                    {
                        'content': rule.content,
                        'priority': rule.priority.value,
                        'category': rule.category.value,
                        'description': rule.description,
                        'tags': list(rule.tags) if rule.tags else [],
                        'examples': rule.examples if rule.examples else [],
                        'violations': rule.violations if rule.violations else []
                    }
                    for rule in self.selected_rules
                ]
            }
            
            # Save to rules file
            rules_file = Path(self.project_root) / 'project_rules.json'
            with open(rules_file, 'w', encoding='utf-8') as f:
                json.dump(rules_data, f, indent=2, ensure_ascii=False)
            
            console.print(f"[green]✅ Rules configuration saved to: {rules_file}[/green]")
            
            # Display next steps
            console.print(Panel(
                "[bold]Next Steps:[/bold]\n\n"
                "1. Review the generated rules in project_rules.json\n"
                "2. Run 'projectprompt rules validate' to check for issues\n"
                "3. Run 'projectprompt rules apply' to enforce rules\n"
                "4. Run 'projectprompt rules report' to generate compliance reports\n\n"
                "[italic]The rules are now ready to help maintain your project quality![/italic]",
                title="🎉 Setup Complete!",
                border_style="green"
            ))
            
            return True
            
        except Exception as e:
            logger.error(f"Error generating rules: {e}")
            console.print(f"[red]❌ Error generating rules: {e}[/red]")
            return False
