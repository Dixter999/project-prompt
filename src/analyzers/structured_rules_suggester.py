#!/usr/bin/env python3
"""
Enhanced AI Rules Suggester with Structured Rule Models

This module provides AI-powered rule suggestions using the structured RuleItem,
RuleGroup, and RuleSet models for better organization and management.
"""

import os
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from datetime import datetime

from src.models.rule_models import (
    RuleItem, RuleGroup, RuleSet, RuleContext, RuleTemplate,
    RulePriority, RuleCategory,
    get_web_app_template, get_data_science_template, get_api_service_template
)
from src.models.suggestion_models import PatternAnalysis, SuggestionContext
from src.analyzers.rules_suggester import get_rules_suggester
from src.integrations.anthropic_rules_analyzer import get_anthropic_rules_analyzer
from src.utils.logger import get_logger

logger = get_logger()


class StructuredRulesSuggester:
    """Enhanced AI rules suggester that generates structured RuleSet objects"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.base_suggester = get_rules_suggester(project_path)
        self._ai_analyzer = None
        
    async def suggest_structured_rules(
        self, 
        confidence_threshold: float = 0.7,
        use_ai: bool = False,
        project_type: Optional[str] = None
    ) -> RuleSet:
        """Generate a structured RuleSet with AI-powered suggestions"""
        
        logger.info("Starting structured rules generation...")
        
        # Analyze project patterns
        pattern_analysis = self.base_suggester.analyze_project_patterns()
        
        # Determine project type if not provided
        if not project_type:
            project_type = self._detect_project_type(pattern_analysis)
        
        # Create base rule set
        rule_set = RuleSet(
            name=f"{self.project_path.name}_rules",
            version="1.0.0",
            description=f"AI-generated rules for {self.project_path.name}",
            metadata={
                "generated_at": datetime.now().isoformat(),
                "project_type": project_type,
                "confidence_threshold": confidence_threshold,
                "ai_enhanced": use_ai,
                "detected_technologies": pattern_analysis.technology_stack,
                "architectural_patterns": pattern_analysis.architectural_patterns
            }
        )
        
        # Generate technology rules
        tech_group = await self._generate_technology_rules(pattern_analysis, use_ai)
        rule_set.add_group(tech_group)
        
        # Generate architecture rules
        arch_group = await self._generate_architecture_rules(pattern_analysis, use_ai)
        rule_set.add_group(arch_group)
        
        # Generate code style rules
        style_group = await self._generate_code_style_rules(pattern_analysis, use_ai)
        rule_set.add_group(style_group)
        
        # Generate testing rules
        testing_group = await self._generate_testing_rules(pattern_analysis, use_ai)
        rule_set.add_group(testing_group)
        
        # Generate security rules
        security_group = await self._generate_security_rules(pattern_analysis, use_ai)
        rule_set.add_group(security_group)
        
        # Generate documentation rules
        docs_group = await self._generate_documentation_rules(pattern_analysis, use_ai)
        rule_set.add_group(docs_group)
        
        # Generate performance rules
        perf_group = await self._generate_performance_rules(pattern_analysis, use_ai)
        rule_set.add_group(perf_group)
        
        # Filter by confidence if AI is used
        if use_ai:
            rule_set = self._filter_by_confidence(rule_set, confidence_threshold)
        
        logger.info(f"Generated {self._count_total_rules(rule_set)} structured rules")
        return rule_set
    
    def _detect_project_type(self, analysis: PatternAnalysis) -> str:
        """Detect project type based on pattern analysis"""
        tech_stack = set(tech.lower() for tech in analysis.technology_stack)
        
        # Web application patterns
        if any(tech in tech_stack for tech in ['react', 'vue', 'angular', 'streamlit', 'flask', 'django', 'fastapi']):
            return "web_application"
        
        # Data science patterns
        if any(tech in tech_stack for tech in ['pandas', 'numpy', 'jupyter', 'matplotlib', 'seaborn', 'scikit-learn']):
            return "data_science"
        
        # API service patterns
        if any(tech in tech_stack for tech in ['fastapi', 'flask', 'django-rest', 'express']):
            return "api_service"
        
        # CLI tool patterns
        if any(tech in tech_stack for tech in ['typer', 'click', 'argparse']):
            return "cli_tool"
        
        return "general"
    
    async def _generate_technology_rules(self, analysis: PatternAnalysis, use_ai: bool) -> RuleGroup:
        """Generate technology constraint rules"""
        group = RuleGroup(
            name="technology_constraints",
            description="Technology stack requirements and constraints",
            category=RuleCategory.TECHNOLOGY
        )
        
        # Mandatory technologies (detected with high confidence)
        for tech in analysis.technology_stack:
            if tech.lower() in ['python', 'typescript', 'react', 'django', 'fastapi']:
                rule = RuleItem(
                    content=f"Use {tech} as specified in project requirements",
                    priority=RulePriority.MANDATORY,
                    category=RuleCategory.TECHNOLOGY,
                    description=f"Mandatory use of {tech}",
                    tags={tech.lower(), "mandatory", "framework"},
                    examples=[f"All {tech} code must follow project conventions"]
                )
                group.rules.append(rule)
        
        # Add framework-specific rules
        if 'streamlit' in [t.lower() for t in analysis.technology_stack]:
            rule = RuleItem(
                content="Use Streamlit exclusively for all user interfaces",
                priority=RulePriority.MANDATORY,
                category=RuleCategory.TECHNOLOGY,
                description="UI framework constraint",
                context=RuleContext(
                    file_extensions=['.py'],
                    directories=['ui/', 'pages/', 'streamlit_app/']
                ),
                tags={'streamlit', 'ui', 'mandatory'},
                examples=["import streamlit as st", "st.write('Hello World')"]
            )
            group.rules.append(rule)
        
        # Prohibited technologies (if AI detects conflicts)
        if use_ai:
            prohibited_rules = await self._get_ai_prohibited_technologies(analysis)
            group.rules.extend(prohibited_rules)
        
        return group
    
    async def _generate_architecture_rules(self, analysis: PatternAnalysis, use_ai: bool) -> RuleGroup:
        """Generate architecture pattern rules"""
        group = RuleGroup(
            name="architecture_patterns", 
            description="Architectural patterns and structure requirements",
            category=RuleCategory.ARCHITECTURE
        )
        
        # Service pattern rules
        if 'service' in ' '.join(analysis.architectural_patterns).lower():
            rule = RuleItem(
                content="All services must inherit from BaseService class",
                priority=RulePriority.MANDATORY,
                category=RuleCategory.ARCHITECTURE,
                description="Service inheritance pattern",
                context=RuleContext(
                    directories=['services/', 'src/services/'],
                    file_patterns=['*service*.py']
                ),
                tags={'service', 'inheritance', 'architecture'},
                examples=["class UserService(BaseService):", "class DataService(BaseService):"]
            )
            group.rules.append(rule)
        
        # Dependency injection rules
        rule = RuleItem(
            content="Use dependency injection for external services",
            priority=RulePriority.MANDATORY,
            category=RuleCategory.ARCHITECTURE,
            description="Dependency injection pattern",
            tags={'dependency-injection', 'architecture'},
            examples=["def __init__(self, db_service: DatabaseService):"]
        )
        group.rules.append(rule)
        
        # File organization rules
        rule = RuleItem(
            content="Follow established directory structure for file organization",
            priority=RulePriority.MANDATORY,
            category=RuleCategory.ARCHITECTURE,
            description="File organization standards",
            tags={'organization', 'structure'},
            examples=[
                "models/ - Database models only",
                "services/ - Business logic",
                "api/ - API endpoints",
                "utils/ - Helper functions"
            ]
        )
        group.rules.append(rule)
        
        return group
    
    async def _generate_code_style_rules(self, analysis: PatternAnalysis, use_ai: bool) -> RuleGroup:
        """Generate code style and formatting rules"""
        group = RuleGroup(
            name="code_style",
            description="Code style and formatting requirements", 
            category=RuleCategory.CODE_STYLE
        )
        
        # Python-specific rules
        if 'python' in [t.lower() for t in analysis.technology_stack]:
            rules = [
                RuleItem(
                    content="Type hints required for all function parameters and returns",
                    priority=RulePriority.MANDATORY,
                    category=RuleCategory.CODE_STYLE,
                    description="Type annotation requirement",
                    context=RuleContext(file_extensions=['.py']),
                    tags={'python', 'type-hints', 'mandatory'},
                    examples=["def process_data(data: List[str]) -> Dict[str, Any]:"]
                ),
                RuleItem(
                    content="Docstrings mandatory for all public methods",
                    priority=RulePriority.MANDATORY,
                    category=RuleCategory.CODE_STYLE,
                    description="Documentation requirement",
                    context=RuleContext(file_extensions=['.py']),
                    tags={'python', 'docstrings', 'documentation'},
                    examples=['"""Process user data and return results."""']
                ),
                RuleItem(
                    content="Maximum function length: 50 lines",
                    priority=RulePriority.RECOMMENDED,
                    category=RuleCategory.CODE_STYLE,
                    description="Function length constraint",
                    context=RuleContext(file_extensions=['.py']),
                    tags={'python', 'length', 'maintainability'}
                ),
                RuleItem(
                    content="Maximum file length: 500 lines",
                    priority=RulePriority.RECOMMENDED,
                    category=RuleCategory.CODE_STYLE,
                    description="File length constraint",
                    context=RuleContext(file_extensions=['.py']),
                    tags={'python', 'length', 'maintainability'}
                )
            ]
            group.rules.extend(rules)
        
        # Naming convention rules
        naming_rules = [
            RuleItem(
                content="Services: *Service (e.g., UserService, DataService)",
                priority=RulePriority.MANDATORY,
                category=RuleCategory.CODE_STYLE,
                description="Service naming convention",
                context=RuleContext(
                    directories=['services/'],
                    file_patterns=['*service*.py']
                ),
                tags={'naming', 'services'},
                examples=["class UserService:", "class DataService:"]
            ),
            RuleItem(
                content="Models: Singular nouns (e.g., User, Transaction)",
                priority=RulePriority.MANDATORY,
                category=RuleCategory.CODE_STYLE,
                description="Model naming convention",
                context=RuleContext(
                    directories=['models/'],
                    file_patterns=['*model*.py']
                ),
                tags={'naming', 'models'},
                examples=["class User:", "class Transaction:"]
            )
        ]
        group.rules.extend(naming_rules)
        
        return group
    
    async def _generate_testing_rules(self, analysis: PatternAnalysis, use_ai: bool) -> RuleGroup:
        """Generate testing requirement rules"""
        group = RuleGroup(
            name="testing_requirements",
            description="Testing standards and requirements",
            category=RuleCategory.TESTING
        )
        
        base_rules = [
            RuleItem(
                content="Minimum 80% code coverage",
                priority=RulePriority.MANDATORY,
                category=RuleCategory.TESTING,
                description="Coverage requirement",
                tags={'coverage', 'quality'},
                examples=["pytest --cov=src --cov-report=term-missing --cov-fail-under=80"]
            ),
            RuleItem(
                content="Test files must mirror source structure",
                priority=RulePriority.MANDATORY,
                category=RuleCategory.TESTING,
                description="Test organization",
                context=RuleContext(
                    directories=['tests/'],
                    file_patterns=['test_*.py']
                ),
                tags={'organization', 'structure'},
                examples=["src/services/user_service.py → tests/services/test_user_service.py"]
            ),
            RuleItem(
                content="Use fixtures for common test data",
                priority=RulePriority.RECOMMENDED,
                category=RuleCategory.TESTING,
                description="Test data management",
                context=RuleContext(file_patterns=['test_*.py']),
                tags={'fixtures', 'data'},
                examples=["@pytest.fixture", "def sample_user():"]
            ),
            RuleItem(
                content="Mock all external dependencies",
                priority=RulePriority.MANDATORY,
                category=RuleCategory.TESTING,
                description="Isolation requirement",
                context=RuleContext(file_patterns=['test_*.py']),
                tags={'mocking', 'isolation'},
                examples=["@patch('external_service.call')", "mock_service = Mock()"]
            )
        ]
        group.rules.extend(base_rules)
        
        # Framework-specific testing rules
        test_frameworks = [t for t in analysis.testing_patterns if t.lower() in ['pytest', 'unittest', 'jest']]
        if test_frameworks:
            for framework in test_frameworks:
                rule = RuleItem(
                    content=f"Use {framework} for all testing",
                    priority=RulePriority.MANDATORY,
                    category=RuleCategory.TESTING,
                    description=f"Testing framework requirement",
                    tags={framework.lower(), 'framework'},
                    examples=[f"# Use {framework} patterns and conventions"]
                )
                group.rules.append(rule)
        
        return group
    
    async def _generate_security_rules(self, analysis: PatternAnalysis, use_ai: bool) -> RuleGroup:
        """Generate security requirement rules"""
        group = RuleGroup(
            name="security_requirements",
            description="Security standards and practices",
            category=RuleCategory.SECURITY
        )
        
        base_rules = [
            RuleItem(
                content="Never hardcode API keys or secrets",
                priority=RulePriority.MANDATORY,
                category=RuleCategory.SECURITY,
                description="Secret management",
                tags={'secrets', 'api-keys', 'security'},
                examples=["api_key = os.getenv('API_KEY')", "Use environment variables"],
                violations=["api_key = 'sk-1234567890'", "password = 'hardcoded123'"]
            ),
            RuleItem(
                content="Validate all user input",
                priority=RulePriority.MANDATORY,
                category=RuleCategory.SECURITY,
                description="Input validation",
                tags={'validation', 'input', 'security'},
                examples=["if not isinstance(user_id, int):", "validate_email(email)"]
            ),
            RuleItem(
                content="Use HTTPS for all external API calls",
                priority=RulePriority.MANDATORY,
                category=RuleCategory.SECURITY,
                description="Transport security",
                tags={'https', 'api', 'security'},
                examples=["requests.get('https://api.example.com')"]
            )
        ]
        group.rules.extend(base_rules)
        
        return group
    
    async def _generate_documentation_rules(self, analysis: PatternAnalysis, use_ai: bool) -> RuleGroup:
        """Generate documentation requirement rules"""
        group = RuleGroup(
            name="documentation_standards",
            description="Documentation requirements and standards",
            category=RuleCategory.DOCUMENTATION
        )
        
        base_rules = [
            RuleItem(
                content="All public functions must have docstrings",
                priority=RulePriority.MANDATORY,
                category=RuleCategory.DOCUMENTATION,
                description="Function documentation",
                tags={'docstrings', 'functions'},
                examples=['"""Process user data and return results."""']
            ),
            RuleItem(
                content="Complex algorithms need inline comments",
                priority=RulePriority.RECOMMENDED,
                category=RuleCategory.DOCUMENTATION,
                description="Code explanation",
                tags={'comments', 'algorithms'},
                examples=["# Calculate weighted average using exponential decay"]
            ),
            RuleItem(
                content="README required for each major module",
                priority=RulePriority.RECOMMENDED,
                category=RuleCategory.DOCUMENTATION,
                description="Module documentation",
                tags={'readme', 'modules'},
                examples=["services/README.md", "utils/README.md"]
            )
        ]
        group.rules.extend(base_rules)
        
        return group
    
    async def _generate_performance_rules(self, analysis: PatternAnalysis, use_ai: bool) -> RuleGroup:
        """Generate performance requirement rules"""
        group = RuleGroup(
            name="performance_guidelines",
            description="Performance optimization guidelines",
            category=RuleCategory.PERFORMANCE
        )
        
        # Data processing performance rules
        if any('data' in tech.lower() for tech in analysis.technology_stack):
            rule = RuleItem(
                content="Prefer pandas operations over pure Python loops for data processing",
                priority=RulePriority.RECOMMENDED,
                category=RuleCategory.PERFORMANCE,
                description="Data processing optimization",
                tags={'pandas', 'optimization', 'data'},
                examples=["df.apply(func) instead of for loops", "df.groupby().agg()"]
            )
            group.rules.append(rule)
        
        # Caching rules
        rule = RuleItem(
            content="Implement caching for expensive operations",
            priority=RulePriority.RECOMMENDED,
            category=RuleCategory.PERFORMANCE,
            description="Caching strategy",
            tags={'caching', 'optimization'},
            examples=["@lru_cache(maxsize=128)", "@functools.cache"]
        )
        group.rules.append(rule)
        
        # Async rules
        if any('async' in pattern.lower() for pattern in analysis.architectural_patterns):
            rule = RuleItem(
                content="Use async patterns for I/O operations",
                priority=RulePriority.RECOMMENDED,
                category=RuleCategory.PERFORMANCE,
                description="Asynchronous operations",
                tags={'async', 'io', 'performance'},
                examples=["async def fetch_data():", "await client.get()"]
            )
            group.rules.append(rule)
        
        return group
    
    async def _get_ai_prohibited_technologies(self, analysis: PatternAnalysis) -> List[RuleItem]:
        """Use AI to suggest prohibited technologies based on detected stack"""
        if not self._ai_analyzer:
            try:
                self._ai_analyzer = get_anthropic_rules_analyzer()
            except Exception:
                return []
        
        prohibited_rules = []
        
        # Example: If Streamlit is detected, prohibit other UI frameworks
        if 'streamlit' in [t.lower() for t in analysis.technology_stack]:
            prohibited = ['flask', 'django', 'fastapi']
            for tech in prohibited:
                if tech not in [t.lower() for t in analysis.technology_stack]:
                    rule = RuleItem(
                        content=f"Do NOT use {tech.title()} - use Streamlit for UI instead",
                        priority=RulePriority.MANDATORY,
                        category=RuleCategory.TECHNOLOGY,
                        description=f"Prohibition of {tech} in favor of Streamlit",
                        tags={'prohibited', tech, 'ui'},
                        violations=[f"from {tech} import"]
                    )
                    prohibited_rules.append(rule)
        
        return prohibited_rules
    
    def _filter_by_confidence(self, rule_set: RuleSet, threshold: float) -> RuleSet:
        """Filter rules by confidence threshold (placeholder for AI integration)"""
        # In a full implementation, this would use AI confidence scores
        # For now, we keep all rules as they're generated with high confidence
        return rule_set
    
    def _count_total_rules(self, rule_set: RuleSet) -> int:
        """Count total number of rules in the rule set"""
        return sum(len(group.rules) for group in rule_set.groups.values())
    
    def export_to_yaml(self, rule_set: RuleSet, output_path: str) -> None:
        """Export structured rules to YAML format"""
        import yaml
        
        export_data = {
            'name': rule_set.name,
            'version': rule_set.version,
            'description': rule_set.description,
            'metadata': rule_set.metadata,
            'rule_groups': {}
        }
        
        for group_name, group in rule_set.groups.items():
            group_data = {
                'name': group.name,
                'description': group.description,
                'category': group.category.value if group.category else None,
                'rules': []
            }
            
            for rule in group.rules:
                rule_data = {
                    'content': rule.content,
                    'priority': rule.priority.value,
                    'category': rule.category.value,
                    'description': rule.description,
                    'tags': list(rule.tags),
                    'examples': rule.examples,
                    'violations': rule.violations
                }
                
                if rule.context:
                    rule_data['context'] = {
                        'directories': rule.context.directories,
                        'file_patterns': rule.context.file_patterns,
                        'file_extensions': rule.context.file_extensions,
                        'exclude_patterns': rule.context.exclude_patterns,
                        'environments': rule.context.environments
                    }
                
                group_data['rules'].append(rule_data)
            
            export_data['rule_groups'][group_name] = group_data
        
        with open(output_path, 'w') as f:
            yaml.dump(export_data, f, default_flow_style=False, sort_keys=False, indent=2)
        
        logger.info(f"Exported structured rules to {output_path}")


def get_structured_rules_suggester(project_path: str) -> StructuredRulesSuggester:
    """Factory function to create structured rules suggester"""
    return StructuredRulesSuggester(project_path)


# Example usage and testing
async def demo_structured_rules():
    """Demonstrate structured rules generation"""
    suggester = get_structured_rules_suggester('.')
    
    # Generate structured rules
    rule_set = await suggester.suggest_structured_rules(
        confidence_threshold=0.8,
        use_ai=True,
        project_type="cli_tool"
    )
    
    print(f"Generated rule set: {rule_set.name}")
    print(f"Total groups: {len(rule_set.groups)}")
    print(f"Total rules: {suggester._count_total_rules(rule_set)}")
    
    # Export to YAML
    suggester.export_to_yaml(rule_set, "structured_rules.yaml")
    
    # Validate rules
    validation_errors = rule_set.validate()
    if validation_errors:
        print(f"Validation errors: {validation_errors}")
    else:
        print("All rules validated successfully!")
    
    return rule_set


if __name__ == "__main__":
    asyncio.run(demo_structured_rules())
