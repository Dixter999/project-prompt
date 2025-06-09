"""
Prompt Enricher - FASE 1: Pre-procesamiento y Enriquecimiento
Enriches prompts with project context and optimization strategies for better API responses.
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml


class PromptEnricher:
    """
    Intelligent prompt enricher that enhances prompts with project context
    and optimization strategies for better Anthropic API responses.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.templates = self._load_prompt_templates()
        self.strategies = self._load_api_strategies()
        
    def _get_default_config_path(self) -> str:
        """Get default configuration path."""
        return os.path.join(os.path.dirname(__file__), '..', '..', 'config')
    
    def _load_prompt_templates(self) -> Dict[str, Any]:
        """Load prompt templates from configuration."""
        template_file = os.path.join(self.config_path, 'prompt_templates.yaml')
        
        # Default templates if file doesn't exist
        default_templates = {
            'implementation': {
                'prefix': "You are an expert software engineer implementing a feature in a {language} project using {framework}.",
                'context_section': "## Project Context\n{context}",
                'requirements_section': "## Implementation Requirements\n{requirements}",
                'constraints_section': "## Constraints and Guidelines\n{constraints}",
                'output_format': "## Expected Output\n{output_format}"
            },
            'analysis': {
                'prefix': "You are a senior software architect analyzing a {language} codebase.",
                'context_section': "## Codebase Analysis\n{context}",
                'focus_section': "## Analysis Focus\n{focus}",
                'output_format': "## Analysis Format\n{output_format}"
            },
            'optimization': {
                'prefix': "You are a performance expert optimizing {language} code.",
                'context_section': "## Current Implementation\n{context}",
                'metrics_section': "## Performance Metrics\n{metrics}",
                'goals_section': "## Optimization Goals\n{goals}"
            }
        }
        
        try:
            if os.path.exists(template_file):
                with open(template_file, 'r', encoding='utf-8') as f:
                    loaded_templates = yaml.safe_load(f)
                    return {**default_templates, **loaded_templates}
        except (yaml.YAMLError, FileNotFoundError):
            pass
            
        return default_templates
    
    def _load_api_strategies(self) -> Dict[str, Any]:
        """Load API request strategies from configuration."""
        strategy_file = os.path.join(self.config_path, 'api_strategies.yaml')
        
        # Default strategies
        default_strategies = {
            'temperature_by_task': {
                'creative': 0.8,
                'implementation': 0.3,
                'analysis': 0.1,
                'debugging': 0.2
            },
            'max_tokens_by_complexity': {
                'simple': 2000,
                'medium': 4000,
                'complex': 8000,
                'very_complex': 12000
            },
            'system_prompts': {
                'implementation': "You are a senior software engineer focused on writing clean, maintainable, and well-documented code. Always follow best practices and explain your decisions.",
                'analysis': "You are an expert code reviewer with deep knowledge of software architecture patterns. Provide thorough, actionable feedback.",
                'optimization': "You are a performance engineering specialist. Focus on measurable improvements while maintaining code readability."
            }
        }
        
        try:
            if os.path.exists(strategy_file):
                with open(strategy_file, 'r', encoding='utf-8') as f:
                    loaded_strategies = yaml.safe_load(f)
                    return {**default_strategies, **loaded_strategies}
        except (yaml.YAMLError, FileNotFoundError):
            pass
            
        return default_strategies
    
    def enrich_prompt(self, 
                     base_prompt: str, 
                     context: Dict[str, Any], 
                     task_type: str = 'implementation',
                     complexity_level: str = 'medium',
                     additional_constraints: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Enrich a base prompt with project context and optimization strategies.
        
        Args:
            base_prompt: The original prompt to enrich
            context: Project context from ContextBuilder
            task_type: Type of task (implementation, analysis, optimization)
            complexity_level: Complexity level (simple, medium, complex, very_complex)
            additional_constraints: Additional constraints to include
            
        Returns:
            Enriched prompt configuration for API request
        """
        # Build enriched prompt
        enriched_prompt = self._build_enriched_prompt(
            base_prompt, context, task_type, additional_constraints
        )
        
        # Get API configuration
        api_config = self._get_api_configuration(task_type, complexity_level, context)
        
        # Add context-aware instructions
        context_instructions = self._generate_context_instructions(context)
        
        return {
            'prompt': enriched_prompt,
            'system_prompt': api_config['system_prompt'],
            'temperature': api_config['temperature'],
            'max_tokens': api_config['max_tokens'],
            'context_instructions': context_instructions,
            'metadata': {
                'task_type': task_type,
                'complexity_level': complexity_level,
                'project_type': context['project_metadata']['type'],
                'language': context['project_metadata']['language'],
                'framework': context['project_metadata'].get('framework')
            }
        }
    
    def _build_enriched_prompt(self, 
                              base_prompt: str, 
                              context: Dict[str, Any], 
                              task_type: str,
                              additional_constraints: Optional[List[str]] = None) -> str:
        """Build the enriched prompt with context and templates."""
        template = self.templates.get(task_type, self.templates['implementation'])
        metadata = context['project_metadata']
        
        # Build prompt sections
        sections = []
        
        # Add prefix with project info
        prefix = template['prefix'].format(
            language=metadata.get('language', 'unknown'),
            framework=metadata.get('framework', 'standard')
        )
        sections.append(prefix)
        
        # Add context section
        if 'context_section' in template:
            context_summary = self._build_context_summary(context)
            context_section = template['context_section'].format(context=context_summary)
            sections.append(context_section)
        
        # Add original prompt as requirements
        if 'requirements_section' in template:
            requirements_section = template['requirements_section'].format(requirements=base_prompt)
            sections.append(requirements_section)
        
        # Add constraints
        if 'constraints_section' in template:
            constraints = self._build_constraints(context, additional_constraints)
            constraints_section = template['constraints_section'].format(constraints=constraints)
            sections.append(constraints_section)
        
        # Add output format instructions
        if 'output_format' in template:
            output_format = self._build_output_format(context, task_type)
            output_section = template['output_format'].format(output_format=output_format)
            sections.append(output_section)
        
        return '\n\n'.join(sections)
    
    def _build_context_summary(self, context: Dict[str, Any]) -> str:
        """Build a concise context summary for the prompt."""
        metadata = context['project_metadata']
        structure = context['file_structure']
        dependencies = context['dependencies']
        complexity = context['complexity_metrics']
        
        summary_parts = [
            f"**Project Type**: {metadata['type']} ({metadata['language']})"
        ]
        
        if metadata.get('framework'):
            summary_parts.append(f"**Framework**: {metadata['framework']}")
        
        summary_parts.extend([
            f"**Project Size**: {structure['total_files']} files, {structure['organization_pattern']} organization",
            f"**Key Dependencies**: {', '.join(list(dependencies['external'].keys())[:5])}",
            f"**Complexity Level**: {complexity['technical_debt']} technical debt"
        ])
        
        # Add integration points if available
        integration = context.get('integration_points', {})
        if integration.get('cli_commands'):
            summary_parts.append(f"**CLI Commands**: {len(integration['cli_commands'])} commands defined")
        
        if integration.get('entry_points'):
            summary_parts.append(f"**Entry Points**: {', '.join(integration['entry_points'][:3])}")
        
        return '\n'.join(summary_parts)
    
    def _build_constraints(self, context: Dict[str, Any], additional_constraints: Optional[List[str]] = None) -> str:
        """Build implementation constraints based on project context."""
        constraints = []
        
        # Language-specific constraints
        language = context['project_metadata'].get('language')
        if language == 'python':
            constraints.extend([
                "Follow PEP 8 style guidelines",
                "Use type hints where appropriate",
                "Include proper docstrings for functions and classes",
                "Handle exceptions appropriately"
            ])
        elif language == 'javascript':
            constraints.extend([
                "Use modern ES6+ syntax",
                "Follow consistent naming conventions",
                "Include proper error handling",
                "Use appropriate async/await patterns"
            ])
        
        # Framework-specific constraints
        framework = context['project_metadata'].get('framework')
        if framework == 'react':
            constraints.extend([
                "Use functional components with hooks",
                "Follow React best practices",
                "Implement proper prop validation"
            ])
        
        # Project structure constraints
        structure = context['file_structure']
        if structure['organization_pattern'] == 'src_based':
            constraints.append("Place new files in appropriate src/ subdirectories")
        
        # Complexity-based constraints
        complexity = context['complexity_metrics']
        if complexity['technical_debt'] == 'high':
            constraints.extend([
                "Prioritize code simplicity and readability",
                "Avoid increasing cyclomatic complexity",
                "Consider refactoring opportunities"
            ])
        
        # Add custom constraints
        if additional_constraints:
            constraints.extend(additional_constraints)
        
        return '\n'.join(f"- {constraint}" for constraint in constraints)
    
    def _build_output_format(self, context: Dict[str, Any], task_type: str) -> str:
        """Build output format instructions based on task type and context."""
        base_format = [
            "Provide clear, actionable implementation steps",
            "Include code examples with proper formatting",
            "Explain the reasoning behind key decisions"
        ]
        
        if task_type == 'implementation':
            base_format.extend([
                "Structure response as: Overview, Implementation Steps, Code Changes, Testing Approach",
                "Include file paths for all changes",
                "Provide import statements and dependencies if needed"
            ])
        elif task_type == 'analysis':
            base_format.extend([
                "Structure response as: Current State, Issues Identified, Recommendations",
                "Include specific line numbers and file references",
                "Prioritize findings by impact and effort"
            ])
        elif task_type == 'optimization':
            base_format.extend([
                "Structure response as: Performance Analysis, Bottlenecks, Optimization Strategy",
                "Include before/after comparisons where relevant",
                "Provide measurable improvement targets"
            ])
        
        # Add language-specific format requirements
        language = context['project_metadata'].get('language')
        if language == 'python':
            base_format.append("Use Python docstring format for documentation")
        elif language == 'javascript':
            base_format.append("Use JSDoc format for documentation")
        
        return '\n'.join(f"- {format_item}" for format_item in base_format)
    
    def _get_api_configuration(self, task_type: str, complexity_level: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get optimized API configuration based on task and context."""
        config = {
            'temperature': self.strategies['temperature_by_task'].get(task_type, 0.3),
            'max_tokens': self.strategies['max_tokens_by_complexity'].get(complexity_level, 4000),
            'system_prompt': self.strategies['system_prompts'].get(task_type, 
                                                                 self.strategies['system_prompts']['implementation'])
        }
        
        # Adjust based on project complexity
        complexity_metrics = context.get('complexity_metrics', {})
        if complexity_metrics.get('technical_debt') == 'high':
            # Use lower temperature for high-complexity projects
            config['temperature'] = max(0.1, config['temperature'] - 0.2)
            # Increase tokens for more detailed explanations
            config['max_tokens'] = min(12000, config['max_tokens'] + 2000)
        
        return config
    
    def _generate_context_instructions(self, context: Dict[str, Any]) -> List[str]:
        """Generate context-aware instructions for the API."""
        instructions = []
        
        # Instructions based on project structure
        structure = context['file_structure']
        if structure['organization_pattern'] == 'src_based':
            instructions.append("Follow the existing src/ directory structure")
        
        # Instructions based on dependencies
        dependencies = context['dependencies']['external']
        if 'click' in dependencies:
            instructions.append("Use Click framework patterns for CLI commands")
        if 'pytest' in dependencies:
            instructions.append("Include pytest-compatible test cases")
        if 'fastapi' in dependencies:
            instructions.append("Follow FastAPI patterns and conventions")
        
        # Instructions based on integration points
        integration = context.get('integration_points', {})
        if integration.get('cli_commands'):
            instructions.append("Integrate with existing CLI command structure")
        
        # Instructions based on complexity
        complexity = context.get('complexity_metrics', {})
        if complexity.get('maintainability_index', 0) < 50:
            instructions.append("Focus on improving code maintainability")
        
        return instructions
    
    def create_api_request_payload(self, enriched_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create the final API request payload."""
        return {
            'model': 'claude-3-sonnet-20240229',  # Default to Sonnet for good balance
            'max_tokens': enriched_config['max_tokens'],
            'temperature': enriched_config['temperature'],
            'system': enriched_config['system_prompt'],
            'messages': [
                {
                    'role': 'user',
                    'content': enriched_config['prompt']
                }
            ],
            'metadata': enriched_config['metadata']
        }
    
    def optimize_for_task_type(self, task_type: str, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize API configuration for specific task types."""
        optimized = base_config.copy()
        
        if task_type == 'debugging':
            optimized['temperature'] = 0.1  # Very low for precise debugging
            optimized['model'] = 'claude-3-opus-20240229'  # Use most capable model
        elif task_type == 'creative':
            optimized['temperature'] = 0.8  # Higher for creative solutions
        elif task_type == 'refactoring':
            optimized['temperature'] = 0.2  # Low but not too rigid
            optimized['max_tokens'] = min(optimized['max_tokens'] + 2000, 12000)  # More space for explanations
        
        return optimized
    
    def validate_enriched_prompt(self, enriched_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and provide feedback on the enriched prompt configuration."""
        validation = {
            'is_valid': True,
            'warnings': [],
            'suggestions': [],
            'estimated_cost': self._estimate_api_cost(enriched_config)
        }
        
        # Check prompt length
        prompt_length = len(enriched_config['prompt'])
        if prompt_length > 10000:
            validation['warnings'].append(f"Prompt is quite long ({prompt_length} chars). Consider breaking into smaller requests.")
        
        # Check temperature settings
        temp = enriched_config['temperature']
        task_type = enriched_config['metadata']['task_type']
        if task_type == 'implementation' and temp > 0.5:
            validation['suggestions'].append("Consider lower temperature for implementation tasks for more consistent results.")
        
        # Check token allocation
        max_tokens = enriched_config['max_tokens']
        if max_tokens < 2000:
            validation['warnings'].append("Low max_tokens setting might truncate complex responses.")
        
        return validation
    
    def _estimate_api_cost(self, enriched_config: Dict[str, Any]) -> Dict[str, float]:
        """Estimate API cost for the enriched request."""
        # Rough estimates based on Claude pricing (as of 2024)
        input_tokens = len(enriched_config['prompt']) // 4  # Rough approximation
        output_tokens = enriched_config['max_tokens']
        
        # Pricing per 1K tokens (approximate)
        model = enriched_config.get('model', 'claude-3-sonnet-20240229')
        
        if 'opus' in model:
            input_cost = (input_tokens / 1000) * 0.015
            output_cost = (output_tokens / 1000) * 0.075
        elif 'sonnet' in model:
            input_cost = (input_tokens / 1000) * 0.003
            output_cost = (output_tokens / 1000) * 0.015
        else:  # haiku or default
            input_cost = (input_tokens / 1000) * 0.00025
            output_cost = (output_tokens / 1000) * 0.00125
        
        return {
            'estimated_input_cost': input_cost,
            'estimated_output_cost': output_cost,
            'estimated_total_cost': input_cost + output_cost
        }
