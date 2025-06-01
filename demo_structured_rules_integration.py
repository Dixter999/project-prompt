#!/usr/bin/env python3
"""
Demonstration of Structured Rules Integration

This script shows how the new structured rules system works with the existing
ProjectPrompt rule models, providing a sophisticated way to generate and manage
project rules using AI-powered analysis.
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append('.')

from src.models.rule_models import (
    RuleSet, RuleGroup, RuleItem, RuleContext, 
    RulePriority, RuleCategory
)

def demonstrate_basic_rule_models():
    """Demonstrate the sophisticated rule models system"""
    print("🏗️  Basic Rule Models Demonstration")
    print("=" * 60)
    
    # Create a comprehensive rule set
    rule_set = RuleSet(
        name="projectprompt_demo_rules",
        version="1.0.0",
        description="Demonstration of structured rules for ProjectPrompt",
        metadata={
            "created_at": datetime.now().isoformat(),
            "demo_type": "comprehensive",
            "features": ["ai_integration", "structured_rules", "yaml_export"]
        }
    )
    
    # Technology Constraints Group
    tech_group = RuleGroup(
        name="technology_constraints",
        description="Technology stack requirements and constraints",
        category=RuleCategory.TECHNOLOGY,
        metadata={"importance": "critical", "scope": "project_wide"}
    )
    
    # Add technology rules
    python_rule = RuleItem(
        content="Use Python 3.8+ for all development work",
        priority=RulePriority.MANDATORY,
        category=RuleCategory.TECHNOLOGY,
        description="Python version requirement",
        context=RuleContext(
            file_extensions=['.py'],
            directories=['src/', 'tests/', 'examples/']
        ),
        tags={'python', 'version', 'mandatory'},
        examples=[
            "# pyproject.toml\nrequires-python = \">=3.8\"",
            "# CI/CD configuration\npython-version: '3.8'"
        ]
    )
    tech_group.rules.append(python_rule)
    
    streamlit_rule = RuleItem(
        content="Use Streamlit exclusively for all user interfaces",
        priority=RulePriority.MANDATORY,
        category=RuleCategory.TECHNOLOGY,
        description="UI framework constraint",
        context=RuleContext(
            file_extensions=['.py'],
            directories=['ui/', 'pages/', 'streamlit_app/'],
            file_patterns=['*_app.py', '*streamlit*.py']
        ),
        tags={'streamlit', 'ui', 'framework'},
        examples=[
            "import streamlit as st",
            "st.title('ProjectPrompt UI')",
            "if __name__ == '__main__':\n    st.run()"
        ]
    )
    tech_group.rules.append(streamlit_rule)
    
    rule_set.add_group(tech_group)
    
    # Architecture Group
    arch_group = RuleGroup(
        name="architecture_patterns",
        description="Architectural patterns and structure requirements",
        category=RuleCategory.ARCHITECTURE,
        metadata={"pattern_type": "layered_architecture"}
    )
    
    service_rule = RuleItem(
        content="All business logic services must inherit from BaseService class",
        priority=RulePriority.MANDATORY,
        category=RuleCategory.ARCHITECTURE,
        description="Service inheritance pattern",
        context=RuleContext(
            directories=['src/services/', 'services/'],
            file_patterns=['*service*.py', '*_service.py']
        ),
        tags={'service', 'inheritance', 'base_class'},
        examples=[
            "class UserService(BaseService):",
            "class DataProcessingService(BaseService):",
            "class RulesService(BaseService):"
        ]
    )
    arch_group.rules.append(service_rule)
    
    dependency_rule = RuleItem(
        content="Use dependency injection for external services and utilities",
        priority=RulePriority.RECOMMENDED,
        category=RuleCategory.ARCHITECTURE,
        description="Dependency injection pattern",
        tags={'dependency_injection', 'loose_coupling', 'testability'},
        examples=[
            "def __init__(self, db_service: DatabaseService, logger: Logger):",
            "class AnalysisService:",
            "    def __init__(self, file_analyzer: FileAnalyzer):"
        ]
    )
    arch_group.rules.append(dependency_rule)
    
    rule_set.add_group(arch_group)
    
    # Code Style Group
    style_group = RuleGroup(
        name="code_style",
        description="Code style and formatting requirements",
        category=RuleCategory.CODE_STYLE
    )
    
    type_hints_rule = RuleItem(
        content="Type hints are mandatory for all function parameters and return values",
        priority=RulePriority.MANDATORY,
        category=RuleCategory.CODE_STYLE,
        description="Type annotation requirement",
        context=RuleContext(file_extensions=['.py']),
        tags={'python', 'type_hints', 'mypy'},
        examples=[
            "def process_files(files: List[Path]) -> Dict[str, Any]:",
            "async def analyze_project(path: str) -> AnalysisResult:",
            "class RulesSuggester:",
            "    def __init__(self, project_path: Path) -> None:"
        ]
    )
    style_group.rules.append(type_hints_rule)
    
    docstring_rule = RuleItem(
        content="Comprehensive docstrings required for all public methods and classes",
        priority=RulePriority.MANDATORY,
        category=RuleCategory.CODE_STYLE,
        description="Documentation requirement",
        context=RuleContext(file_extensions=['.py']),
        tags={'documentation', 'docstrings', 'public_api'},
        examples=[
            '"""Generate AI-powered rule suggestions for a project."""',
            '"""',
            'Args:',
            '    project_path: Path to the project directory',
            '    confidence_threshold: Minimum confidence score (0.0-1.0)',
            '',
            'Returns:',
            '    RuleSet object with generated rules',
            '"""'
        ]
    )
    style_group.rules.append(docstring_rule)
    
    rule_set.add_group(style_group)
    
    # Testing Group
    testing_group = RuleGroup(
        name="testing_requirements",
        description="Testing standards and coverage requirements",
        category=RuleCategory.TESTING
    )
    
    coverage_rule = RuleItem(
        content="Maintain minimum 80% test coverage for all core modules",
        priority=RulePriority.MANDATORY,
        category=RuleCategory.TESTING,
        description="Code coverage requirement",
        context=RuleContext(
            directories=['src/', 'tests/'],
            file_patterns=['test_*.py', '*_test.py']
        ),
        tags={'coverage', 'testing', 'quality'},
        examples=[
            "# pytest configuration",
            "--cov=src --cov-report=html --cov-fail-under=80",
            "# Coverage badge in README",
            "![Coverage](https://img.shields.io/badge/coverage-85%25-green)"
        ]
    )
    testing_group.rules.append(coverage_rule)
    
    rule_set.add_group(testing_group)
    
    # Security Group
    security_group = RuleGroup(
        name="security_requirements",
        description="Security standards and best practices",
        category=RuleCategory.SECURITY
    )
    
    api_key_rule = RuleItem(
        content="Never hardcode API keys or sensitive credentials in source code",
        priority=RulePriority.MANDATORY,
        category=RuleCategory.SECURITY,
        description="Credential security requirement",
        tags={'api_keys', 'environment_variables', 'security'},
        examples=[
            "api_key = os.getenv('ANTHROPIC_API_KEY')",
            "# .env file (not committed)",
            "ANTHROPIC_API_KEY=your_key_here",
            "# Use python-dotenv for loading"
        ]
    )
    security_group.rules.append(api_key_rule)
    
    rule_set.add_group(security_group)
    
    return rule_set

def demonstrate_yaml_export(rule_set: RuleSet):
    """Demonstrate YAML export functionality"""
    print("\n📄 YAML Export Demonstration")
    print("=" * 60)
    
    yaml_content = rule_set.to_yaml()
    
    print(f"Generated YAML with {len(yaml_content)} characters")
    print("\nYAML Preview (first 1000 characters):")
    print("-" * 40)
    print(yaml_content[:1000])
    if len(yaml_content) > 1000:
        print("...")
        print(f"... and {len(yaml_content) - 1000} more characters")
    print("-" * 40)
    
    # Save to file
    output_file = "demo_structured_rules.yaml"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(yaml_content)
    
    print(f"\n✅ Full YAML saved to: {output_file}")
    return output_file

def demonstrate_rule_analysis(rule_set: RuleSet):
    """Demonstrate rule set analysis capabilities"""
    print("\n📊 Rule Set Analysis")
    print("=" * 60)
    
    # Count rules by category
    category_counts = {}
    priority_counts = {}
    
    for group in rule_set.groups:
        for rule in group.rules:
            cat = rule.category.value
            pri = rule.priority.value
            
            category_counts[cat] = category_counts.get(cat, 0) + 1
            priority_counts[pri] = priority_counts.get(pri, 0) + 1
    
    total_rules = sum(len(group.rules) for group in rule_set.groups)
    
    print(f"📈 Rule Set Statistics:")
    print(f"  • Total Groups: {len(rule_set.groups)}")
    print(f"  • Total Rules: {total_rules}")
    print(f"  • Version: {rule_set.version}")
    
    print(f"\n📊 Rules by Category:")
    for category, count in sorted(category_counts.items()):
        percentage = (count / total_rules) * 100
        print(f"  • {category.title()}: {count} rules ({percentage:.1f}%)")
    
    print(f"\n⚡ Rules by Priority:")
    for priority, count in sorted(priority_counts.items()):
        percentage = (count / total_rules) * 100
        print(f"  • {priority.title()}: {count} rules ({percentage:.1f}%)")
    
    print(f"\n🏷️  Most Common Tags:")
    all_tags = []
    for group in rule_set.groups:
        for rule in group.rules:
            all_tags.extend(rule.tags)
    
    tag_counts = {}
    for tag in all_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    for tag, count in sorted_tags[:10]:  # Top 10 tags
        print(f"  • {tag}: {count} occurrences")

def demonstrate_rule_filtering(rule_set: RuleSet):
    """Demonstrate rule filtering capabilities"""
    print("\n🔍 Rule Filtering Demonstration")
    print("=" * 60)
    
    # Filter mandatory rules
    mandatory_rules = []
    for group in rule_set.groups:
        for rule in group.rules:
            if rule.priority == RulePriority.MANDATORY:
                mandatory_rules.append(rule)
    
    print(f"🚨 Mandatory Rules ({len(mandatory_rules)} total):")
    for i, rule in enumerate(mandatory_rules, 1):
        print(f"  {i}. {rule.content}")
        print(f"     Category: {rule.category.value}, Group: {rule.description}")
    
    # Filter by file context
    python_rules = []
    for group in rule_set.groups:
        for rule in group.rules:
            if rule.context and rule.context.file_extensions:
                if '.py' in rule.context.file_extensions:
                    python_rules.append(rule)
    
    print(f"\n🐍 Python-Specific Rules ({len(python_rules)} total):")
    for i, rule in enumerate(python_rules, 1):
        print(f"  {i}. {rule.content}")
        if rule.context and rule.context.directories:
            print(f"     Applies to: {', '.join(rule.context.directories)}")

async def demonstrate_ai_integration():
    """Demonstrate AI integration capabilities"""
    print("\n🤖 AI Integration Demonstration")
    print("=" * 60)
    
    print("The structured rules system integrates with AI analysis:")
    print("• Pattern recognition from codebase analysis")
    print("• Confidence scoring for each suggested rule")
    print("• Context-aware rule generation")
    print("• Technology stack detection")
    print("• Architectural pattern recognition")
    
    print("\nExample AI-Generated Rule:")
    print("─" * 40)
    
    # Simulate an AI-generated rule
    ai_rule = RuleItem(
        content="Use async/await for all I/O operations to improve performance",
        priority=RulePriority.RECOMMENDED,
        category=RuleCategory.PERFORMANCE,
        description="Async I/O optimization (AI-suggested)",
        confidence_score=0.85,
        context=RuleContext(
            file_extensions=['.py'],
            file_patterns=['*api*.py', '*service*.py']
        ),
        tags={'async', 'performance', 'io', 'ai_suggested'},
        examples=[
            "async def fetch_data(url: str) -> Dict[str, Any]:",
            "    async with httpx.AsyncClient() as client:",
            "        response = await client.get(url)",
            "        return response.json()"
        ]
    )
    
    print(f"Rule: {ai_rule.content}")
    print(f"Confidence: {ai_rule.confidence_score:.2f}/1.0")
    print(f"Category: {ai_rule.category.value}")
    print(f"Priority: {ai_rule.priority.value}")
    print(f"Tags: {', '.join(ai_rule.tags)}")

def main():
    """Main demonstration function"""
    print("🚀 ProjectPrompt Structured Rules Integration")
    print("=" * 60)
    print("This demonstration shows the sophisticated rule modeling system")
    print("that integrates AI-powered suggestions with structured rule management.")
    print("=" * 60)
    
    # Demonstrate basic rule models
    rule_set = demonstrate_basic_rule_models()
    
    # Show YAML export
    yaml_file = demonstrate_yaml_export(rule_set)
    
    # Analyze the rule set
    demonstrate_rule_analysis(rule_set)
    
    # Show filtering capabilities
    demonstrate_rule_filtering(rule_set)
    
    # Show AI integration
    asyncio.run(demonstrate_ai_integration())
    
    print("\n🎉 Integration Demonstration Complete!")
    print("=" * 60)
    print(f"✅ Generated comprehensive rule set with {len(rule_set.groups)} groups")
    print(f"✅ Exported to YAML: {yaml_file}")
    print(f"✅ Demonstrated filtering and analysis capabilities")
    print(f"✅ Showed AI integration features")
    
    print("\n📚 Next Steps:")
    print("• Run the CLI commands to generate rules for your project")
    print("• Use 'python -m src.main rules generate-structured-rules'")
    print("• Integrate with your existing workflow")
    print("• Customize rule templates for your project type")

if __name__ == "__main__":
    main()
