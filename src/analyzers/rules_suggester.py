#!/usr/bin/env python3
"""
AI-Powered Rules Suggester for ProjectPrompt

This module uses AI analysis to suggest appropriate rules based on project
structure, detected patterns, and best practices.
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime

from src.models.rule_models import (
    RuleItem, RuleCategory, RulePriority, RuleContext, 
    RuleGroup, RuleSet, RuleTemplate
)
from src.models.suggestion_models import PatternAnalysis, RuleSuggestion, SuggestionContext
from src.utils.logger import get_logger

logger = get_logger()

# Lazy imports to avoid circular dependencies
def _get_project_scanner():
    """Lazy import to avoid circular dependency"""
    from src.analyzers.project_scanner import get_project_scanner
    return get_project_scanner()

def _get_functionality_detector():
    """Lazy import to avoid circular dependency"""
    from src.analyzers.functionality_detector import get_functionality_detector
    return get_functionality_detector()


# Remove the duplicate dataclass definitions since they're now in suggestion_models


class RulesSuggester:
    """AI-powered rules suggester based on project analysis"""
    
    def __init__(self, project_root: str):
        """Initialize the rules suggester"""
        self.project_root = Path(project_root)
        self.project_scanner = _get_project_scanner()
        self.functionality_detector = _get_functionality_detector()
        self.suggestion_history: List[Dict[str, Any]] = []
        self.user_feedback: Dict[str, Any] = {}
        
    def analyze_project_patterns(self) -> PatternAnalysis:
        """Analyze the project to detect patterns and inconsistencies"""
        logger.info("Starting project pattern analysis...")
        
        analysis = PatternAnalysis()
        
        try:
            # Scan project structure
            scan_result = self.project_scanner.scan_project(str(self.project_root))
            
            # Detect technology stack
            analysis.technology_stack = self._detect_technologies(scan_result)
            
            # Analyze architectural patterns
            analysis.architectural_patterns = self._detect_architectural_patterns(scan_result)
            
            # Analyze code style patterns
            analysis.code_style_patterns = self._analyze_code_style(scan_result)
            
            # Detect testing patterns
            analysis.testing_patterns = self._detect_testing_patterns(scan_result)
            
            # Analyze documentation patterns
            analysis.documentation_patterns = self._analyze_documentation(scan_result)
            
            # Detect security patterns
            analysis.security_patterns = self._detect_security_patterns(scan_result)
            
            # Find inconsistencies
            analysis.inconsistencies = self._find_inconsistencies(scan_result)
            
            # Calculate confidence score
            analysis.confidence_score = self._calculate_confidence(analysis)
            
            logger.info(f"Pattern analysis completed with confidence: {analysis.confidence_score}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error during pattern analysis: {e}")
            return analysis
    
    def suggest_rules(self, context: Optional[SuggestionContext] = None) -> List[RuleSuggestion]:
        """Generate rule suggestions based on project analysis"""
        logger.info("Generating rule suggestions...")
        
        # Analyze project patterns
        pattern_analysis = self.analyze_project_patterns()
        
        # Infer context if not provided
        if not context:
            context = self._infer_suggestion_context(pattern_analysis)
        
        suggestions = []
        
        # Generate technology-specific rules
        suggestions.extend(self._suggest_technology_rules(pattern_analysis, context))
        
        # Generate architecture rules
        suggestions.extend(self._suggest_architecture_rules(pattern_analysis, context))
        
        # Generate code style rules
        suggestions.extend(self._suggest_code_style_rules(pattern_analysis, context))
        
        # Generate testing rules
        suggestions.extend(self._suggest_testing_rules(pattern_analysis, context))
        
        # Generate documentation rules
        suggestions.extend(self._suggest_documentation_rules(pattern_analysis, context))
        
        # Generate security rules
        suggestions.extend(self._suggest_security_rules(pattern_analysis, context))
        
        # Sort by confidence and priority
        suggestions.sort(key=lambda x: (x.suggested_rule.priority.value, -x.confidence))
        
        logger.info(f"Generated {len(suggestions)} rule suggestions")
        return suggestions
    
    def generate_draft_rules_file(self, suggestions: List[RuleSuggestion], 
                                 output_path: Optional[str] = None) -> str:
        """Generate a draft rules file from suggestions"""
        if not output_path:
            # Create project-output/suggestions/rules directory
            rules_dir = os.path.join(self.project_root, "project-output", "suggestions", "rules")
            os.makedirs(rules_dir, exist_ok=True)
            output_path = os.path.join(rules_dir, "suggested_rules.yaml")
        
        # Group suggestions by category
        grouped_suggestions = {}
        for suggestion in suggestions:
            category = suggestion.suggested_rule.category.value
            if category not in grouped_suggestions:
                grouped_suggestions[category] = []
            grouped_suggestions[category].append(suggestion)
        
        # Generate YAML content
        yaml_content = self._generate_yaml_from_suggestions(grouped_suggestions)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        logger.info(f"Draft rules file generated: {output_path}")
        return output_path
    
    def learn_from_feedback(self, suggestion_id: str, accepted: bool, 
                          modified_rule: Optional[RuleItem] = None) -> None:
        """Learn from user feedback on suggestions"""
        feedback = {
            'suggestion_id': suggestion_id,
            'accepted': accepted,
            'timestamp': datetime.now().isoformat(),
            'modified_rule': modified_rule.content if modified_rule else None
        }
        
        self.user_feedback[suggestion_id] = feedback
        self._update_suggestion_weights(feedback)
        
        logger.info(f"Learned from feedback: {suggestion_id} -> {'accepted' if accepted else 'rejected'}")
    
    def _detect_technologies(self, scan_result: Dict[str, Any]) -> List[str]:
        """Detect technologies used in the project"""
        technologies = set()
        
        # Analyze file extensions
        file_extensions = scan_result.get('file_extensions', {})
        
        # Python detection
        if '.py' in file_extensions:
            technologies.add('python')
            
            # Framework detection
            files = scan_result.get('files', [])
            for file_info in files:
                # Handle both string paths and file info dictionaries
                if isinstance(file_info, dict):
                    file_path = file_info.get('path', '')
                else:
                    file_path = str(file_info)
                
                content = self._read_file_safely(file_path)
                if content:
                    if 'django' in content.lower():
                        technologies.add('django')
                    elif 'flask' in content.lower():
                        technologies.add('flask')
                    elif 'fastapi' in content.lower():
                        technologies.add('fastapi')
                    elif 'pandas' in content.lower():
                        technologies.add('pandas')
                    elif 'numpy' in content.lower():
                        technologies.add('numpy')
        
        # JavaScript/TypeScript detection
        if any(ext in file_extensions for ext in ['.js', '.ts', '.jsx', '.tsx']):
            technologies.add('javascript')
            if any(ext in file_extensions for ext in ['.ts', '.tsx']):
                technologies.add('typescript')
        
        # Package.json analysis
        package_json = self.project_root / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    package_data = json.load(f)
                    dependencies = {**package_data.get('dependencies', {}), 
                                  **package_data.get('devDependencies', {})}
                    
                    if 'react' in dependencies:
                        technologies.add('react')
                    if 'vue' in dependencies:
                        technologies.add('vue')
                    if 'angular' in dependencies:
                        technologies.add('angular')
                    if 'express' in dependencies:
                        technologies.add('express')
            except Exception:
                pass
        
        # Requirements.txt analysis
        requirements = self.project_root / 'requirements.txt'
        if requirements.exists():
            try:
                with open(requirements, 'r') as f:
                    req_content = f.read().lower()
                    if 'django' in req_content:
                        technologies.add('django')
                    if 'flask' in req_content:
                        technologies.add('flask')
                    if 'fastapi' in req_content:
                        technologies.add('fastapi')
            except Exception:
                pass
        
        return list(technologies)
    
    def _detect_architectural_patterns(self, scan_result: Dict[str, Any]) -> List[str]:
        """Detect architectural patterns in the project"""
        patterns = set()
        
        directories = scan_result.get('directories', [])
        files = scan_result.get('files', [])
        
        # MVC pattern detection
        if any('models' in d for d in directories) and \
           any('views' in d for d in directories) and \
           any('controllers' in d for d in directories):
            patterns.add('mvc')
        
        # Clean architecture detection
        if any('entities' in d for d in directories) and \
           any('use_cases' in d or 'usecases' in d for d in directories):
            patterns.add('clean_architecture')
        
        # Microservices detection
        if len([d for d in directories if 'service' in d]) > 2:
            patterns.add('microservices')
        
        # API detection
        if any('api' in d for d in directories) or \
           any('endpoints' in d for d in directories):
            patterns.add('api_service')
        
        # Repository pattern detection
        if any('repository' in f or 'repositories' in f for f in files):
            patterns.add('repository_pattern')
        
        return list(patterns)
    
    def _analyze_code_style(self, scan_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code style patterns"""
        style_patterns = {
            'indentation': 'unknown',
            'naming_convention': 'unknown',
            'line_length': 'unknown',
            'import_style': 'unknown'
        }
        
        files = scan_result.get('files', [])
        
        # Extract file paths from file info dictionaries and filter Python files
        python_files = []
        for file_info in files:
            if isinstance(file_info, dict):
                file_path = file_info.get('path', '')
            else:
                file_path = str(file_info)
            
            if file_path.endswith('.py'):
                python_files.append(file_path)
        
        if python_files:
            # Sample a few files for analysis
            sample_files = python_files[:5]
            for file_path in sample_files:
                content = self._read_file_safely(file_path)
                if content:
                    lines = content.split('\n')
                    
                    # Analyze indentation
                    for line in lines:
                        if line.startswith('    '):
                            style_patterns['indentation'] = '4_spaces'
                            break
                        elif line.startswith('\t'):
                            style_patterns['indentation'] = 'tabs'
                            break
                    
                    # Analyze line length
                    long_lines = [line for line in lines if len(line) > 100]
                    if len(long_lines) / len(lines) > 0.1:
                        style_patterns['line_length'] = 'long_lines_common'
                    else:
                        style_patterns['line_length'] = 'standard_length'
        
        return style_patterns
    
    def _detect_testing_patterns(self, scan_result: Dict[str, Any]) -> List[str]:
        """Detect testing patterns and frameworks"""
        patterns = set()
        
        files = scan_result.get('files', [])
        
        # Extract file paths from file info dictionaries
        file_paths = []
        for file_info in files:
            if isinstance(file_info, dict):
                file_path = file_info.get('path', '')
            else:
                file_path = str(file_info)
            file_paths.append(file_path)
        
        # Test file detection
        test_files = [f for f in file_paths if 'test' in f.lower() or f.startswith('test_')]
        if test_files:
            patterns.add('unit_testing')
        
        # Framework detection
        for file_path in file_paths:
            content = self._read_file_safely(file_path)
            if content:
                content_lower = content.lower()
                if 'pytest' in content_lower:
                    patterns.add('pytest')
                elif 'unittest' in content_lower:
                    patterns.add('unittest')
                elif 'jest' in content_lower:
                    patterns.add('jest')
                elif 'mocha' in content_lower:
                    patterns.add('mocha')
        
        # Test directory structure
        directories = scan_result.get('directories', [])
        if any('tests' in d for d in directories):
            patterns.add('separate_test_directory')
        
        return list(patterns)
    
    def _analyze_documentation(self, scan_result: Dict[str, Any]) -> List[str]:
        """Analyze documentation patterns"""
        patterns = set()
        
        files = scan_result.get('files', [])
        
        # Extract file paths from file info dictionaries
        file_paths = []
        for file_info in files:
            if isinstance(file_info, dict):
                file_path = file_info.get('path', '')
            else:
                file_path = str(file_info)
            file_paths.append(file_path)
        
        # README detection
        if any('readme' in f.lower() for f in file_paths):
            patterns.add('readme_present')
        
        # API documentation
        if any('api' in f.lower() and any(ext in f for ext in ['.md', '.rst']) for f in file_paths):
            patterns.add('api_documentation')
        
        # Docstring analysis
        python_files = [f for f in file_paths if f.endswith('.py')]
        if python_files:
            for file_path in python_files[:3]:  # Sample analysis
                content = self._read_file_safely(file_path)
                if content and '"""' in content:
                    patterns.add('docstrings_present')
                    break
        
        # Documentation directory
        directories = scan_result.get('directories', [])
        if any('docs' in d or 'documentation' in d for d in directories):
            patterns.add('dedicated_docs_directory')
        
        return list(patterns)
    
    def _detect_security_patterns(self, scan_result: Dict[str, Any]) -> List[str]:
        """Detect security-related patterns"""
        patterns = set()
        
        files = scan_result.get('files', [])
        
        # Extract file paths from file info dictionaries
        file_paths = []
        for file_info in files:
            if isinstance(file_info, dict):
                file_path = file_info.get('path', '')
            else:
                file_path = str(file_info)
            file_paths.append(file_path)
        
        # Environment variables
        if any('.env' in f for f in file_paths):
            patterns.add('environment_variables')
        
        # Configuration files
        config_files = [f for f in file_paths if 'config' in f.lower()]
        if config_files:
            patterns.add('configuration_files')
        
        # Security-related imports
        for file_path in file_paths:
            if file_path.endswith('.py'):
                content = self._read_file_safely(file_path)
                if content:
                    content_lower = content.lower()
                    if any(security_term in content_lower for security_term in 
                          ['bcrypt', 'hashlib', 'secrets', 'cryptography']):
                        patterns.add('encryption_usage')
                        break
        
        return list(patterns)
    
    def _find_inconsistencies(self, scan_result: Dict[str, Any]) -> List[str]:
        """Find inconsistencies that could benefit from rules"""
        inconsistencies = []
        
        files = scan_result.get('files', [])
        
        # Extract file paths from file info dictionaries
        file_paths = []
        for file_info in files:
            if isinstance(file_info, dict):
                file_path = file_info.get('path', '')
            else:
                file_path = str(file_info)
            file_paths.append(file_path)
        
        # Naming convention inconsistencies
        python_files = [f for f in file_paths if f.endswith('.py')]
        if python_files:
            snake_case = [f for f in python_files if '_' in f]
            camel_case = [f for f in python_files if any(c.isupper() for c in f)]
            
            if snake_case and camel_case:
                inconsistencies.append("Mixed naming conventions in Python files")
        
        # Import style inconsistencies
        # This would require more detailed analysis of import statements
        
        return inconsistencies
    
    def _calculate_confidence(self, analysis: PatternAnalysis) -> float:
        """Calculate confidence score for the analysis"""
        factors = [
            len(analysis.technology_stack) * 0.2,
            len(analysis.architectural_patterns) * 0.15,
            len(analysis.testing_patterns) * 0.15,
            len(analysis.documentation_patterns) * 0.1,
            len(analysis.security_patterns) * 0.1,
            (5 - len(analysis.inconsistencies)) * 0.1,  # Fewer inconsistencies = higher confidence
            0.2  # Base confidence
        ]
        
        return min(sum(factors), 1.0)
    
    def _infer_suggestion_context(self, analysis: PatternAnalysis) -> SuggestionContext:
        """Infer suggestion context from analysis"""
        # Simple heuristics for context inference
        project_type = "general"
        if "django" in analysis.technology_stack or "flask" in analysis.technology_stack:
            project_type = "web_application"
        elif "pandas" in analysis.technology_stack or "numpy" in analysis.technology_stack:
            project_type = "data_science"
        elif "api_service" in analysis.architectural_patterns:
            project_type = "api_service"
        
        # Estimate project size (would need more sophisticated analysis)
        size_category = "medium"
        complexity_level = "moderate"
        team_size = "small"
        
        return SuggestionContext(
            project_type=project_type,
            size_category=size_category,
            complexity_level=complexity_level,
            team_size=team_size
        )
    
    def _suggest_technology_rules(self, analysis: PatternAnalysis, 
                                context: SuggestionContext) -> List[RuleSuggestion]:
        """Suggest technology-specific rules"""
        suggestions = []
        
        for tech in analysis.technology_stack:
            if tech == "python":
                suggestions.append(RuleSuggestion(
                    suggested_rule=RuleItem(
                        content="Follow PEP 8 style guidelines for Python code",
                        priority=RulePriority.RECOMMENDED,
                        category=RuleCategory.CODE_STYLE,
                        description="Python PEP 8 compliance"
                    ),
                    reasoning="Python detected in project, PEP 8 ensures consistent code style",
                    confidence=0.9,
                    detected_patterns=["python"]
                ))
                
                suggestions.append(RuleSuggestion(
                    suggested_rule=RuleItem(
                        content="Use type hints for all function parameters and return values",
                        priority=RulePriority.RECOMMENDED,
                        category=RuleCategory.CODE_STYLE,
                        description="Python type hints requirement"
                    ),
                    reasoning="Type hints improve code maintainability and IDE support",
                    confidence=0.8,
                    detected_patterns=["python"]
                ))
            
            elif tech == "django":
                suggestions.append(RuleSuggestion(
                    suggested_rule=RuleItem(
                        content="All Django models must include __str__ method",
                        priority=RulePriority.RECOMMENDED,
                        category=RuleCategory.CODE_STYLE,
                        description="Django model string representation"
                    ),
                    reasoning="Django framework detected, __str__ methods improve debugging",
                    confidence=0.85,
                    detected_patterns=["django"]
                ))
        
        return suggestions
    
    def _suggest_architecture_rules(self, analysis: PatternAnalysis, 
                                  context: SuggestionContext) -> List[RuleSuggestion]:
        """Suggest architecture-specific rules"""
        suggestions = []
        
        if "mvc" in analysis.architectural_patterns:
            suggestions.append(RuleSuggestion(
                suggested_rule=RuleItem(
                    content="Controllers should not contain business logic",
                    priority=RulePriority.MANDATORY,
                    category=RuleCategory.ARCHITECTURE,
                    description="MVC separation of concerns"
                ),
                reasoning="MVC pattern detected, maintaining separation of concerns is crucial",
                confidence=0.9,
                detected_patterns=["mvc"]
            ))
        
        if "api_service" in analysis.architectural_patterns:
            suggestions.append(RuleSuggestion(
                suggested_rule=RuleItem(
                    content="All API endpoints must include proper error handling",
                    priority=RulePriority.MANDATORY,
                    category=RuleCategory.ARCHITECTURE,
                    description="API error handling requirement"
                ),
                reasoning="API service detected, robust error handling is essential",
                confidence=0.95,
                detected_patterns=["api_service"]
            ))
        
        return suggestions
    
    def _suggest_code_style_rules(self, analysis: PatternAnalysis, 
                                context: SuggestionContext) -> List[RuleSuggestion]:
        """Suggest code style rules based on detected patterns"""
        suggestions = []
        
        style_patterns = analysis.code_style_patterns
        
        if style_patterns.get('indentation') == '4_spaces':
            suggestions.append(RuleSuggestion(
                suggested_rule=RuleItem(
                    content="Use 4 spaces for indentation, never tabs",
                    priority=RulePriority.RECOMMENDED,
                    category=RuleCategory.CODE_STYLE,
                    description="Consistent indentation style"
                ),
                reasoning="4-space indentation detected as the current pattern",
                confidence=0.8,
                detected_patterns=["4_spaces_indentation"]
            ))
        
        if "Mixed naming conventions in Python files" in analysis.inconsistencies:
            suggestions.append(RuleSuggestion(
                suggested_rule=RuleItem(
                    content="Use snake_case for Python file names and variables",
                    priority=RulePriority.RECOMMENDED,
                    category=RuleCategory.CODE_STYLE,
                    description="Consistent naming convention"
                ),
                reasoning="Inconsistent naming conventions detected, standardization needed",
                confidence=0.7,
                detected_patterns=["naming_inconsistency"]
            ))
        
        return suggestions
    
    def _suggest_testing_rules(self, analysis: PatternAnalysis, 
                             context: SuggestionContext) -> List[RuleSuggestion]:
        """Suggest testing-related rules"""
        suggestions = []
        
        if "unit_testing" in analysis.testing_patterns:
            suggestions.append(RuleSuggestion(
                suggested_rule=RuleItem(
                    content="All public functions must have corresponding unit tests",
                    priority=RulePriority.MANDATORY,
                    category=RuleCategory.TESTING,
                    description="Unit test coverage requirement"
                ),
                reasoning="Testing infrastructure detected, ensure comprehensive coverage",
                confidence=0.8,
                detected_patterns=["unit_testing"]
            ))
        else:
            suggestions.append(RuleSuggestion(
                suggested_rule=RuleItem(
                    content="Implement unit testing framework for the project",
                    priority=RulePriority.RECOMMENDED,
                    category=RuleCategory.TESTING,
                    description="Testing framework setup"
                ),
                reasoning="No testing framework detected, establishing testing is crucial",
                confidence=0.9,
                detected_patterns=["no_testing"]
            ))
        
        if "pytest" in analysis.testing_patterns:
            suggestions.append(RuleSuggestion(
                suggested_rule=RuleItem(
                    content="Use pytest fixtures for test data setup",
                    priority=RulePriority.RECOMMENDED,
                    category=RuleCategory.TESTING,
                    description="Pytest best practices"
                ),
                reasoning="Pytest framework detected, fixtures improve test maintainability",
                confidence=0.7,
                detected_patterns=["pytest"]
            ))
        
        return suggestions
    
    def _suggest_documentation_rules(self, analysis: PatternAnalysis, 
                                   context: SuggestionContext) -> List[RuleSuggestion]:
        """Suggest documentation-related rules"""
        suggestions = []
        
        if "readme_present" not in analysis.documentation_patterns:
            suggestions.append(RuleSuggestion(
                suggested_rule=RuleItem(
                    content="Project must include a comprehensive README.md file",
                    priority=RulePriority.MANDATORY,
                    category=RuleCategory.DOCUMENTATION,
                    description="README documentation requirement"
                ),
                reasoning="No README detected, essential for project understanding",
                confidence=0.95,
                detected_patterns=["missing_readme"]
            ))
        
        if "docstrings_present" in analysis.documentation_patterns:
            suggestions.append(RuleSuggestion(
                suggested_rule=RuleItem(
                    content="All public functions and classes must have docstrings",
                    priority=RulePriority.RECOMMENDED,
                    category=RuleCategory.DOCUMENTATION,
                    description="Code documentation requirement"
                ),
                reasoning="Docstrings detected in project, maintain consistency",
                confidence=0.8,
                detected_patterns=["docstrings_present"]
            ))
        
        return suggestions
    
    def _suggest_security_rules(self, analysis: PatternAnalysis, 
                              context: SuggestionContext) -> List[RuleSuggestion]:
        """Suggest security-related rules"""
        suggestions = []
        
        if "environment_variables" in analysis.security_patterns:
            suggestions.append(RuleSuggestion(
                suggested_rule=RuleItem(
                    content="Never commit .env files or credentials to version control",
                    priority=RulePriority.MANDATORY,
                    category=RuleCategory.SECURITY,
                    description="Credential security requirement"
                ),
                reasoning="Environment variables detected, prevent credential exposure",
                confidence=0.95,
                detected_patterns=["environment_variables"]
            ))
        
        if "configuration_files" in analysis.security_patterns:
            suggestions.append(RuleSuggestion(
                suggested_rule=RuleItem(
                    content="Validate and sanitize all configuration inputs",
                    priority=RulePriority.MANDATORY,
                    category=RuleCategory.SECURITY,
                    description="Configuration security requirement"
                ),
                reasoning="Configuration files detected, ensure input validation",
                confidence=0.8,
                detected_patterns=["configuration_files"]
            ))
        
        return suggestions
    
    def _generate_yaml_from_suggestions(self, grouped_suggestions: Dict[str, List[RuleSuggestion]]) -> str:
        """Generate YAML content from grouped suggestions"""
        yaml_lines = [
            "# AI-Generated Rules Suggestions",
            f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "# Review and modify these suggestions before applying",
            "",
            "rules:"
        ]
        
        for category, suggestions in grouped_suggestions.items():
            yaml_lines.append(f"  # {category.upper()} RULES")
            
            for suggestion in suggestions:
                rule = suggestion.suggested_rule
                yaml_lines.extend([
                    "  - description: |",
                    f"      {rule.description or 'No description'}",
                    f"    content: |",
                    f"      {rule.content}",
                    f"    category: \"{rule.category.value}\"",
                    f"    priority: \"{rule.priority.value}\"",
                    f"    # AI Reasoning: {suggestion.reasoning}",
                    f"    # Confidence: {suggestion.confidence:.2f}",
                    ""
                ])
        
        return "\n".join(yaml_lines)
    
    def _read_file_safely(self, file_path: str) -> Optional[str]:
        """Safely read file content"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return None
    
    def _update_suggestion_weights(self, feedback: Dict[str, Any]) -> None:
        """Update internal weights based on user feedback"""
        # This would implement machine learning to improve suggestions
        # For now, just log the feedback
        logger.info(f"Feedback recorded: {feedback}")


def get_rules_suggester(project_root: str) -> RulesSuggester:
    """Factory function to create a RulesSuggester instance"""
    return RulesSuggester(project_root)
