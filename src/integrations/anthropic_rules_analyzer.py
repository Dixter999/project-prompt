#!/usr/bin/env python3
"""
Anthropic-powered Rules Analyzer for ProjectPrompt

This module provides specialized AI analysis using Anthropic's Claude API
for advanced rules suggestions and pattern recognition.
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

from src.models.rule_models import RuleItem, RuleCategory, RulePriority
from src.models.suggestion_models import PatternAnalysis, RuleSuggestion
from src.utils.logger import get_logger

logger = get_logger()


@dataclass
class AIAnalysisResult:
    """Result from AI analysis"""
    suggestions: List[RuleSuggestion]
    reasoning: str
    confidence: float
    analysis_metadata: Dict[str, Any]


class AnthropicRulesAnalyzer:
    """Specialized AI analyzer using Anthropic's Claude for rules suggestions"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Anthropic analyzer"""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            logger.warning("Anthropic API key not found. AI analysis will be simulated.")
        
        self.analysis_cache: Dict[str, AIAnalysisResult] = {}
        
    async def analyze_for_rules(self, pattern_analysis: PatternAnalysis, 
                               code_samples: List[str],
                               project_context: Dict[str, Any]) -> AIAnalysisResult:
        """Analyze patterns and code samples to suggest rules using AI"""
        logger.info("Starting AI-powered rules analysis...")
        
        try:
            # Create cache key
            cache_key = self._create_cache_key(pattern_analysis, code_samples, project_context)
            
            # Check cache first
            if cache_key in self.analysis_cache:
                logger.info("Returning cached AI analysis")
                return self.analysis_cache[cache_key]
            
            # Prepare analysis prompt
            analysis_prompt = self._prepare_analysis_prompt(
                pattern_analysis, code_samples, project_context
            )
            
            # Get AI analysis
            if self.api_key:
                ai_response = await self._call_anthropic_api(analysis_prompt)
            else:
                ai_response = self._simulate_ai_analysis(pattern_analysis, project_context)
            
            # Parse AI response into structured suggestions
            result = self._parse_ai_response(ai_response, pattern_analysis)
            
            # Cache the result
            self.analysis_cache[cache_key] = result
            
            logger.info(f"AI analysis completed with {len(result.suggestions)} suggestions")
            return result
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return self._fallback_analysis(pattern_analysis)
    
    def analyze_code_quality(self, code_samples: List[str]) -> List[RuleSuggestion]:
        """Analyze code quality and suggest improvement rules"""
        suggestions = []
        
        for code_sample in code_samples:
            # Analyze specific quality issues
            quality_issues = self._detect_quality_issues(code_sample)
            
            for issue in quality_issues:
                suggestion = self._create_quality_suggestion(issue, code_sample)
                if suggestion:
                    suggestions.append(suggestion)
        
        return suggestions
    
    def suggest_best_practices(self, technologies: List[str], 
                             project_type: str) -> List[RuleSuggestion]:
        """Suggest best practice rules for specific technologies"""
        suggestions = []
        
        best_practices_db = self._get_best_practices_database()
        
        for tech in technologies:
            if tech in best_practices_db:
                tech_practices = best_practices_db[tech]
                
                for practice in tech_practices:
                    if self._is_relevant_for_project(practice, project_type):
                        suggestion = RuleSuggestion(
                            suggested_rule=RuleItem(
                                content=practice['rule'],
                                priority=RulePriority(practice['priority']),
                                category=RuleCategory(practice['category']),
                                description=practice['description']
                            ),
                            reasoning=practice['reasoning'],
                            confidence=practice['confidence'],
                            detected_patterns=[tech]
                        )
                        suggestions.append(suggestion)
        
        return suggestions
    
    def _prepare_analysis_prompt(self, pattern_analysis: PatternAnalysis,
                               code_samples: List[str],
                               project_context: Dict[str, Any]) -> str:
        """Prepare the analysis prompt for AI"""
        prompt = f"""You are an expert software architect and code quality analyst. 
Please analyze the following project information and suggest appropriate development rules.

PROJECT CONTEXT:
- Type: {project_context.get('project_type', 'unknown')}
- Size: {project_context.get('size_category', 'unknown')}
- Technologies: {', '.join(pattern_analysis.technology_stack)}
- Architectural Patterns: {', '.join(pattern_analysis.architectural_patterns)}

DETECTED PATTERNS:
- Testing: {', '.join(pattern_analysis.testing_patterns) if pattern_analysis.testing_patterns else 'None detected'}
- Documentation: {', '.join(pattern_analysis.documentation_patterns) if pattern_analysis.documentation_patterns else 'None detected'}
- Security: {', '.join(pattern_analysis.security_patterns) if pattern_analysis.security_patterns else 'None detected'}

INCONSISTENCIES FOUND:
{chr(10).join(f'- {inc}' for inc in pattern_analysis.inconsistencies) if pattern_analysis.inconsistencies else 'None detected'}

CODE SAMPLES:
{chr(10).join(f'Sample {i+1}:' + chr(10) + sample[:500] + '...' if len(sample) > 500 else sample 
              for i, sample in enumerate(code_samples[:3]))}

Please suggest 5-10 specific, actionable development rules that would:
1. Address the inconsistencies found
2. Reinforce good practices already in use
3. Prevent common issues for this technology stack
4. Improve code quality and maintainability

For each rule, provide:
- Rule content (specific and actionable)
- Category (technology, architecture, code_style, testing, documentation, security)
- Priority (mandatory, recommended, optional)
- Reasoning for why this rule is important
- Confidence level (0.0-1.0)

Format your response as JSON with this structure:
{{
  "suggestions": [
    {{
      "content": "Rule description",
      "category": "category_name",
      "priority": "priority_level",
      "reasoning": "Why this rule is important",
      "confidence": 0.8,
      "description": "Brief description"
    }}
  ],
  "overall_reasoning": "Overall analysis summary",
  "confidence": 0.85
}}
"""
        return prompt
    
    async def _call_anthropic_api(self, prompt: str) -> Dict[str, Any]:
        """Call Anthropic API (placeholder for actual implementation)"""
        # This would implement the actual Anthropic API call
        # For now, return a simulated response
        logger.info("Calling Anthropic API...")
        
        # Simulate API delay
        await asyncio.sleep(0.1)
        
        return {
            "suggestions": [
                {
                    "content": "Follow consistent naming conventions throughout the codebase",
                    "category": "code_style",
                    "priority": "recommended",
                    "reasoning": "Consistent naming improves code readability and maintainability",
                    "confidence": 0.9,
                    "description": "Naming convention consistency"
                },
                {
                    "content": "Implement comprehensive error handling for all external API calls",
                    "category": "architecture",
                    "priority": "mandatory",
                    "reasoning": "Proper error handling prevents application crashes and improves user experience",
                    "confidence": 0.95,
                    "description": "Error handling requirement"
                }
            ],
            "overall_reasoning": "The project shows good structure but would benefit from consistency improvements",
            "confidence": 0.85
        }
    
    def _simulate_ai_analysis(self, pattern_analysis: PatternAnalysis, 
                            project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate AI analysis when API is not available"""
        logger.info("Simulating AI analysis (no API key provided)")
        
        suggestions = []
        
        # Generate suggestions based on detected patterns
        if 'python' in pattern_analysis.technology_stack:
            suggestions.append({
                "content": "Use type hints for all function parameters and return values",
                "category": "code_style",
                "priority": "recommended",
                "reasoning": "Type hints improve code clarity and enable better IDE support",
                "confidence": 0.8,
                "description": "Python type hints requirement"
            })
        
        if pattern_analysis.inconsistencies:
            suggestions.append({
                "content": "Establish and enforce consistent coding standards",
                "category": "code_style",
                "priority": "mandatory",
                "reasoning": "Inconsistencies detected that could impact maintainability",
                "confidence": 0.9,
                "description": "Coding standards enforcement"
            })
        
        if not pattern_analysis.testing_patterns:
            suggestions.append({
                "content": "Implement comprehensive unit testing with minimum 80% coverage",
                "category": "testing",
                "priority": "mandatory",
                "reasoning": "No testing framework detected, essential for code quality",
                "confidence": 0.95,
                "description": "Unit testing requirement"
            })
        
        if 'django' in pattern_analysis.technology_stack:
            suggestions.append({
                "content": "Use Django's built-in authentication and authorization system",
                "category": "security",
                "priority": "mandatory",
                "reasoning": "Django provides robust security features that should be utilized",
                "confidence": 0.9,
                "description": "Django security best practices"
            })
        
        return {
            "suggestions": suggestions,
            "overall_reasoning": "Analysis based on detected patterns and common best practices",
            "confidence": 0.8
        }
    
    def _parse_ai_response(self, ai_response: Dict[str, Any], 
                          pattern_analysis: PatternAnalysis) -> AIAnalysisResult:
        """Parse AI response into structured result"""
        suggestions = []
        
        for suggestion_data in ai_response.get('suggestions', []):
            try:
                rule_item = RuleItem(
                    content=suggestion_data['content'],
                    priority=RulePriority(suggestion_data['priority']),
                    category=RuleCategory(suggestion_data['category']),
                    description=suggestion_data.get('description', '')
                )
                
                suggestion = RuleSuggestion(
                    suggested_rule=rule_item,
                    reasoning=suggestion_data['reasoning'],
                    confidence=suggestion_data['confidence'],
                    detected_patterns=list(pattern_analysis.technology_stack)
                )
                
                suggestions.append(suggestion)
                
            except (KeyError, ValueError) as e:
                logger.warning(f"Failed to parse suggestion: {e}")
                continue
        
        return AIAnalysisResult(
            suggestions=suggestions,
            reasoning=ai_response.get('overall_reasoning', ''),
            confidence=ai_response.get('confidence', 0.5),
            analysis_metadata={
                'timestamp': datetime.now().isoformat(),
                'pattern_analysis': pattern_analysis,
                'suggestions_count': len(suggestions)
            }
        )
    
    def _fallback_analysis(self, pattern_analysis: PatternAnalysis) -> AIAnalysisResult:
        """Fallback analysis when AI fails"""
        logger.info("Using fallback analysis")
        
        # Basic rule suggestions based on patterns
        suggestions = []
        
        if 'python' in pattern_analysis.technology_stack:
            suggestions.append(RuleSuggestion(
                suggested_rule=RuleItem(
                    content="Follow PEP 8 guidelines for Python code formatting",
                    priority=RulePriority.RECOMMENDED,
                    category=RuleCategory.CODE_STYLE,
                    description="Python PEP 8 compliance"
                ),
                reasoning="Python detected, PEP 8 is the standard style guide",
                confidence=0.8,
                detected_patterns=['python']
            ))
        
        return AIAnalysisResult(
            suggestions=suggestions,
            reasoning="Fallback analysis based on basic pattern recognition",
            confidence=0.6,
            analysis_metadata={
                'timestamp': datetime.now().isoformat(),
                'fallback': True
            }
        )
    
    def _detect_quality_issues(self, code_sample: str) -> List[Dict[str, Any]]:
        """Detect code quality issues in a sample"""
        issues = []
        
        lines = code_sample.split('\n')
        
        # Check for long lines
        for i, line in enumerate(lines):
            if len(line) > 120:
                issues.append({
                    'type': 'long_line',
                    'line': i + 1,
                    'severity': 'medium',
                    'message': f"Line {i + 1} exceeds 120 characters"
                })
        
        # Check for missing docstrings
        if 'def ' in code_sample and '"""' not in code_sample:
            issues.append({
                'type': 'missing_docstring',
                'severity': 'low',
                'message': "Function lacks docstring"
            })
        
        # Check for hardcoded values
        if any(pattern in code_sample for pattern in ['http://localhost', 'password123', 'api_key = ']):
            issues.append({
                'type': 'hardcoded_values',
                'severity': 'high',
                'message': "Hardcoded values detected"
            })
        
        return issues
    
    def _create_quality_suggestion(self, issue: Dict[str, Any], 
                                 code_sample: str) -> Optional[RuleSuggestion]:
        """Create a rule suggestion based on a quality issue"""
        if issue['type'] == 'long_line':
            return RuleSuggestion(
                suggested_rule=RuleItem(
                    content="Limit line length to 120 characters maximum",
                    priority=RulePriority.RECOMMENDED,
                    category=RuleCategory.CODE_STYLE,
                    description="Line length limit"
                ),
                reasoning=f"Long lines detected: {issue['message']}",
                confidence=0.7,
                detected_patterns=['long_lines']
            )
        
        elif issue['type'] == 'missing_docstring':
            return RuleSuggestion(
                suggested_rule=RuleItem(
                    content="All functions must include descriptive docstrings",
                    priority=RulePriority.RECOMMENDED,
                    category=RuleCategory.DOCUMENTATION,
                    description="Function documentation requirement"
                ),
                reasoning="Functions without docstrings detected",
                confidence=0.8,
                detected_patterns=['missing_docstrings']
            )
        
        elif issue['type'] == 'hardcoded_values':
            return RuleSuggestion(
                suggested_rule=RuleItem(
                    content="Never hardcode sensitive values, use environment variables",
                    priority=RulePriority.MANDATORY,
                    category=RuleCategory.SECURITY,
                    description="Sensitive data protection"
                ),
                reasoning="Hardcoded sensitive values pose security risks",
                confidence=0.95,
                detected_patterns=['hardcoded_values']
            )
        
        return None
    
    def _get_best_practices_database(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get database of best practices for different technologies"""
        return {
            'python': [
                {
                    'rule': 'Use virtual environments for dependency management',
                    'category': 'technology',
                    'priority': 'mandatory',
                    'description': 'Virtual environment requirement',
                    'reasoning': 'Prevents dependency conflicts and ensures reproducible builds',
                    'confidence': 0.9
                },
                {
                    'rule': 'Follow the principle of least privilege in code access',
                    'category': 'security',
                    'priority': 'recommended',
                    'description': 'Access control principle',
                    'reasoning': 'Reduces security risks by limiting access permissions',
                    'confidence': 0.8
                }
            ],
            'django': [
                {
                    'rule': 'Always use Django ORM for database operations',
                    'category': 'architecture',
                    'priority': 'recommended',
                    'description': 'Django ORM usage',
                    'reasoning': 'ORM provides security and maintainability benefits',
                    'confidence': 0.85
                },
                {
                    'rule': 'Enable CSRF protection for all forms',
                    'category': 'security',
                    'priority': 'mandatory',
                    'description': 'CSRF protection requirement',
                    'reasoning': 'CSRF attacks are a serious security threat',
                    'confidence': 0.95
                }
            ],
            'react': [
                {
                    'rule': 'Use functional components with hooks over class components',
                    'category': 'code_style',
                    'priority': 'recommended',
                    'description': 'React component style',
                    'reasoning': 'Functional components are more concise and testable',
                    'confidence': 0.8
                }
            ]
        }
    
    def _is_relevant_for_project(self, practice: Dict[str, Any], 
                               project_type: str) -> bool:
        """Check if a best practice is relevant for the project type"""
        # Simple relevance check - could be made more sophisticated
        relevant_categories = {
            'web_application': ['architecture', 'security', 'code_style'],
            'api_service': ['architecture', 'security', 'testing'],
            'data_science': ['code_style', 'documentation', 'testing']
        }
        
        return practice['category'] in relevant_categories.get(project_type, 
                                                             ['code_style', 'testing'])
    
    def _create_cache_key(self, pattern_analysis: PatternAnalysis,
                         code_samples: List[str], 
                         project_context: Dict[str, Any]) -> str:
        """Create a cache key for the analysis"""
        import hashlib
        
        # Create a hash based on the input parameters
        content = json.dumps({
            'technologies': sorted(pattern_analysis.technology_stack),
            'patterns': sorted(pattern_analysis.architectural_patterns),
            'inconsistencies': sorted(pattern_analysis.inconsistencies),
            'project_type': project_context.get('project_type', ''),
            'code_samples_hash': hashlib.md5(
                ''.join(code_samples).encode()).hexdigest()[:8]
        }, sort_keys=True)
        
        return hashlib.md5(content.encode()).hexdigest()


def get_anthropic_rules_analyzer(api_key: Optional[str] = None) -> AnthropicRulesAnalyzer:
    """Factory function to create an AnthropicRulesAnalyzer instance"""
    return AnthropicRulesAnalyzer(api_key)
