#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI-Powered Insights Analyzer for Project Dashboard.

This module uses Anthropic's Claude API to generate intelligent insights
about project architecture, code quality, and actionable recommendations.
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from src.integrations.anthropic import AnthropicAPI
from src.analyzers.project_analyzer import ProjectAnalyzer
from src.analyzers.code_quality_analyzer import CodeQualityAnalyzer
from src.analyzers.dependency_graph import DependencyGraph
from src.analyzers.functionality_analyzer import FunctionalityAnalyzer
from src.utils.logger import get_logger
from src.utils.config import ConfigManager

logger = get_logger()


@dataclass
class AIInsight:
    """Structure for AI-generated insights."""
    category: str
    title: str
    description: str
    impact: str  # 'high', 'medium', 'low'
    effort: str  # 'high', 'medium', 'low'
    priority: int  # 1-5 scale
    tags: List[str]


@dataclass
class AIRecommendation:
    """Structure for AI-generated recommendations."""
    title: str
    description: str
    action_items: List[str]
    priority: str  # 'critical', 'high', 'medium', 'low'
    estimated_effort: str
    functional_groups: List[str]
    expected_benefits: List[str]


class AIInsightsAnalyzer:
    """
    AI-powered analyzer that generates intelligent insights and recommendations
    based on project code analysis using Anthropic's Claude API.
    """
    
    def __init__(self, project_path: str, config: Optional[ConfigManager] = None):
        """
        Initialize the AI insights analyzer.
        
        Args:
            project_path: Path to the project directory
            config: Optional configuration manager
        """
        self.project_path = os.path.abspath(project_path)
        self.config = config or ConfigManager()
        self.anthropic = AnthropicAPI(config=self.config)
        
        # Initialize other analyzers for data gathering with correct parameters
        # ProjectAnalyzer(max_file_size_mb, max_files, include_quality_analysis)
        self.project_analyzer = ProjectAnalyzer(
            max_file_size_mb=10,  # reasonable default
            max_files=1000,       # reasonable default
            include_quality_analysis=True
        )
        
        # CodeQualityAnalyzer(scanner=None)
        self.quality_analyzer = CodeQualityAnalyzer()
        
        # DependencyGraph() - no parameters
        self.dependency_analyzer = DependencyGraph()
        
        # FunctionalityAnalyzer(scanner=None, functionality_detector=None, code_quality_analyzer=None)
        self.functionality_analyzer = FunctionalityAnalyzer(
            code_quality_analyzer=self.quality_analyzer
        )
        
        # Cache for analysis results
        self._project_data_cache = None
        self._insights_cache = None
        self._recommendations_cache = None
    
    def _gather_project_data(self) -> Dict[str, Any]:
        """
        Gather comprehensive project data for AI analysis.
        
        Returns:
            Dictionary containing all relevant project analysis data
        """
        if self._project_data_cache is not None:
            return self._project_data_cache
        
        logger.info("Gathering comprehensive project data for AI analysis...")
        
        try:
            # Get basic project info - ProjectAnalyzer.analyze_project() takes a project path
            logger.info("Getting project overview...")
            project_overview = self.project_analyzer.analyze_project(self.project_path)
            
            # Get code quality metrics with timeout protection
            logger.info("Starting code quality analysis (this may take a while)...")
            quality_metrics = {}
            try:
                import signal
                import functools
                
                def timeout_handler(signum, frame):
                    raise TimeoutError("Code quality analysis timed out")
                
                # Set a timeout of 60 seconds for code quality analysis
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(60)
                
                quality_metrics = self.quality_analyzer.analyze_code_quality(self.project_path)
                signal.alarm(0)  # Cancel the alarm
                
                logger.info("Code quality analysis completed successfully")
                
            except (TimeoutError, Exception) as e:
                signal.alarm(0)  # Make sure to cancel alarm
                logger.warning(f"Code quality analysis failed or timed out: {e}")
                # Provide fallback data
                quality_metrics = {
                    "overall_score": 75,  # Default score
                    "maintainability": {"score": 7, "issues": []},
                    "complexity": {"average": 3, "max": 10},
                    "documentation": {"coverage": 60},
                    "test_coverage": {"percentage": 0},
                    "patterns": [],
                    "best_practices": {}
                }
            
            # Get dependency information with timeout protection
            logger.info("Analyzing dependencies...")
            dependencies = {}
            try:
                dependencies = self.dependency_analyzer.build_dependency_graph(
                    self.project_path, max_files=500, use_madge=False  # Reduced complexity
                )
                logger.info("Dependency analysis completed")
            except Exception as e:
                logger.warning(f"Dependency analysis failed: {e}")
                dependencies = {
                    "modules": {},
                    "complexity_score": 3,
                    "circular_dependencies": []
                }
            
            # Get functionality analysis with timeout protection
            logger.info("Detecting functionalities...")
            functionality_data = {}
            try:
                functionality_data = self.functionality_analyzer.functionality_detector.detect_functionalities(self.project_path)
                logger.info("Functionality detection completed")
            except Exception as e:
                logger.warning(f"Functionality detection failed: {e}")
                functionality_data = {
                    "detected": {},
                    "main_functionalities": [],
                    "frameworks": {},
                    "architectures": {}
                }
            
            # Extract useful functionality information
            detected_functionalities = functionality_data.get("detected", {})
            main_functionalities = functionality_data.get("main_functionalities", [])
            
            # Get frameworks and architectures from advanced detector results
            frameworks_detected = functionality_data.get('frameworks', {})
            architectures_detected = functionality_data.get('architectures', {})
            
            # Compile project data
            project_data = {
                "project_info": {
                    "name": os.path.basename(self.project_path),
                    "path": self.project_path,
                    "total_files": project_overview.get("total_files", 0),
                    "lines_of_code": project_overview.get("lines_of_code", 0),
                    "languages": project_overview.get("languages", {}),
                    "file_types": project_overview.get("file_types", {}),
                },
                "architecture": {
                    "directory_structure": project_overview.get("directory_structure", {}),
                    "module_organization": dependencies.get("modules", {}),
                    "dependency_complexity": dependencies.get("complexity_score", 0),
                    "circular_dependencies": dependencies.get("circular_dependencies", []),
                    "detected_architectures": architectures_detected,
                },
                "code_quality": {
                    "overall_score": quality_metrics.get("overall_score", 0),
                    "maintainability": quality_metrics.get("maintainability", {}),
                    "complexity": quality_metrics.get("complexity", {}),
                    "documentation": quality_metrics.get("documentation", {}),
                    "test_coverage": quality_metrics.get("test_coverage", {}),
                },
                "functionality": {
                    "detected_functionalities": detected_functionalities,
                    "main_functionalities": main_functionalities,
                    "frameworks_detected": frameworks_detected,
                    "functionality_count": len(main_functionalities),
                    "confidence_scores": {func: data.get("confidence", 0) 
                                        for func, data in detected_functionalities.items() 
                                        if data.get("present", False)},
                },
                "development_patterns": {
                    "frameworks_used": list(frameworks_detected.keys()) if frameworks_detected else project_overview.get("frameworks", []),
                    "design_patterns": quality_metrics.get("patterns", []),
                    "best_practices": quality_metrics.get("best_practices", {}),
                }
            }
            
            self._project_data_cache = project_data
            return project_data
            
        except Exception as e:
            logger.error(f"Error gathering project data: {e}")
            return {}
    
    def generate_ai_insights(self) -> List[AIInsight]:
        """
        Generate AI-powered insights about the project.
        
        Returns:
            List of AI-generated insights
        """
        if self._insights_cache is not None:
            return self._insights_cache
        
        if not self.anthropic.is_configured:
            logger.warning("Anthropic API not configured, cannot generate AI insights")
            return []
        
        logger.info("Generating AI-powered project insights...")
        
        project_data = self._gather_project_data()
        if not project_data:
            return []
        
        # Create analysis prompt for Claude
        prompt = self._create_insights_prompt(project_data)
        
        try:
            # Get AI analysis
            response = self.anthropic.generate_text(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.3
            )
            
            if not response or 'content' not in response:
                logger.error("Invalid response from Anthropic API")
                return []
            
            # Parse AI response into structured insights
            insights = self._parse_insights_response(response['content'])
            
            self._insights_cache = insights
            return insights
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return []
    
    def generate_ai_recommendations(self) -> List[AIRecommendation]:
        """
        Generate AI-powered actionable recommendations.
        
        Returns:
            List of AI-generated recommendations
        """
        if self._recommendations_cache is not None:
            return self._recommendations_cache
        
        if not self.anthropic.is_configured:
            logger.warning("Anthropic API not configured, cannot generate AI recommendations")
            return []
        
        logger.info("Generating AI-powered recommendations...")
        
        project_data = self._gather_project_data()
        if not project_data:
            return []
        
        # Create recommendations prompt for Claude
        prompt = self._create_recommendations_prompt(project_data)
        
        try:
            # Get AI analysis
            response = self.anthropic.generate_text(
                prompt=prompt,
                max_tokens=2500,
                temperature=0.2
            )
            
            if not response or 'content' not in response:
                logger.error("Invalid response from Anthropic API")
                return []
            
            # Parse AI response into structured recommendations
            recommendations = self._parse_recommendations_response(response['content'])
            
            self._recommendations_cache = recommendations
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating AI recommendations: {e}")
            return []
    
    def get_development_priorities(self) -> List[Dict[str, Any]]:
        """
        Generate AI-powered development priorities based on insights and recommendations.
        
        Returns:
            List of prioritized development tasks
        """
        insights = self.generate_ai_insights()
        recommendations = self.generate_ai_recommendations()
        
        # Combine and prioritize based on impact and effort
        priorities = []
        
        # Convert insights to priorities
        for insight in insights:
            if insight.impact == 'high' and insight.priority >= 4:
                priorities.append({
                    "title": f"Address: {insight.title}",
                    "description": insight.description,
                    "priority": insight.priority,
                    "effort": insight.effort,
                    "type": "insight",
                    "tags": insight.tags,
                    "category": insight.category
                })
        
        # Convert high-priority recommendations to priorities
        for rec in recommendations:
            if rec.priority in ['critical', 'high']:
                priority_score = 5 if rec.priority == 'critical' else 4
                priorities.append({
                    "title": rec.title,
                    "description": rec.description,
                    "priority": priority_score,
                    "effort": rec.estimated_effort,
                    "type": "recommendation",
                    "action_items": rec.action_items,
                    "functional_groups": rec.functional_groups,
                    "benefits": rec.expected_benefits
                })
        
        # Sort by priority (descending) then by effort (ascending for same priority)
        effort_order = {'low': 1, 'medium': 2, 'high': 3}
        priorities.sort(key=lambda x: (-x['priority'], effort_order.get(x['effort'], 2)))
        
        return priorities[:10]  # Return top 10 priorities
    
    def _create_insights_prompt(self, project_data: Dict[str, Any]) -> str:
        """Create a detailed prompt for AI insights generation."""
        
        project_summary = f"""
PROJECT ANALYSIS REQUEST

Project: {project_data['project_info']['name']}
Total Files: {project_data['project_info']['total_files']}
Lines of Code: {project_data['project_info']['lines_of_code']}
Primary Languages: {', '.join(project_data['project_info']['languages'].keys())}

ARCHITECTURE OVERVIEW:
- Module Organization: {len(project_data['architecture']['module_organization'])} modules
- Dependency Complexity Score: {project_data['architecture']['dependency_complexity']}/10
- Circular Dependencies: {len(project_data['architecture']['circular_dependencies'])} found

CODE QUALITY METRICS:
- Overall Score: {project_data['code_quality']['overall_score']}/100
- Maintainability: {project_data['code_quality']['maintainability']}
- Complexity: {project_data['code_quality']['complexity']}

FUNCTIONALITY ANALYSIS:
- Detected Functionalities: {len(project_data['functionality']['main_functionalities'])} found
- Main Features: {', '.join(project_data['functionality']['main_functionalities'])}
- Frameworks Detected: {', '.join(project_data['functionality']['frameworks_detected'].keys())}
- Architecture Patterns: {', '.join(project_data['architecture']['detected_architectures'].keys())}

ANALYSIS REQUEST:
Please analyze this project and provide specific, actionable insights in the following JSON format:

{{
  "insights": [
    {{
      "category": "architecture|quality|performance|security|maintainability",
      "title": "Brief descriptive title",
      "description": "Detailed explanation of the insight",
      "impact": "high|medium|low",
      "effort": "high|medium|low", 
      "priority": 1-5,
      "tags": ["tag1", "tag2"]
    }}
  ]
}}

Focus on:
1. Architectural patterns and potential improvements
2. Code quality issues and opportunities
3. Performance bottlenecks or optimization opportunities
4. Security considerations
5. Maintainability and scalability concerns

Provide specific, actionable insights based on the actual project data, not generic advice.
"""
        return project_summary
    
    def _create_recommendations_prompt(self, project_data: Dict[str, Any]) -> str:
        """Create a detailed prompt for AI recommendations generation."""
        
        functional_groups = list(project_data['functionality']['main_functionalities'])
        frameworks_detected = list(project_data['functionality']['frameworks_detected'].keys())
        
        prompt = f"""
PROJECT IMPROVEMENT RECOMMENDATIONS REQUEST

Based on the following project analysis, provide specific, actionable recommendations:

PROJECT CONTEXT:
- Name: {project_data['project_info']['name']}
- Size: {project_data['project_info']['total_files']} files, {project_data['project_info']['lines_of_code']} LOC
- Quality Score: {project_data['code_quality']['overall_score']}/100
- Dependency Complexity: {project_data['architecture']['dependency_complexity']}/10
- Main Functionalities: {', '.join(functional_groups)}
- Frameworks Used: {', '.join(frameworks_detected)}

AREAS FOR IMPROVEMENT:
- Circular Dependencies: {len(project_data['architecture']['circular_dependencies'])} found
- Code Quality Issues: {project_data['code_quality']}
- Documentation Coverage: {project_data['code_quality'].get('documentation', {})}
- Detected Functionality Count: {project_data['functionality']['functionality_count']}

Please provide recommendations in this JSON format:

{{
  "recommendations": [
    {{
      "title": "Clear, actionable recommendation title",
      "description": "Detailed explanation of what needs to be done and why",
      "action_items": ["Specific step 1", "Specific step 2", "Specific step 3"],
      "priority": "critical|high|medium|low",
      "estimated_effort": "low|medium|high",
      "functional_groups": ["group1", "group2"],
      "expected_benefits": ["benefit1", "benefit2"]
    }}
  ]
}}

Focus on:
1. Immediate fixes for critical issues
2. Architectural improvements
3. Code quality enhancements
4. Performance optimizations
5. Security hardening
6. Development workflow improvements

Prioritize recommendations that provide the highest impact with reasonable effort.
Each recommendation should be specific to this project, not generic advice.
"""
        return prompt
    
    def _parse_insights_response(self, response_text: str) -> List[AIInsight]:
        """Parse AI response into structured insights."""
        insights = []
        
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                data = json.loads(json_text)
                
                for insight_data in data.get('insights', []):
                    insight = AIInsight(
                        category=insight_data.get('category', 'general'),
                        title=insight_data.get('title', 'Unknown'),
                        description=insight_data.get('description', ''),
                        impact=insight_data.get('impact', 'medium'),
                        effort=insight_data.get('effort', 'medium'),
                        priority=insight_data.get('priority', 3),
                        tags=insight_data.get('tags', [])
                    )
                    insights.append(insight)
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI insights response as JSON: {e}")
            # Fallback: create a basic insight from the response
            insights.append(AIInsight(
                category='general',
                title='AI Analysis Available',
                description=response_text[:500] + '...' if len(response_text) > 500 else response_text,
                impact='medium',
                effort='medium',
                priority=3,
                tags=['ai-generated']
            ))
        
        return insights
    
    def _parse_recommendations_response(self, response_text: str) -> List[AIRecommendation]:
        """Parse AI response into structured recommendations."""
        recommendations = []
        
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                data = json.loads(json_text)
                
                for rec_data in data.get('recommendations', []):
                    recommendation = AIRecommendation(
                        title=rec_data.get('title', 'Unknown'),
                        description=rec_data.get('description', ''),
                        action_items=rec_data.get('action_items', []),
                        priority=rec_data.get('priority', 'medium'),
                        estimated_effort=rec_data.get('estimated_effort', 'medium'),
                        functional_groups=rec_data.get('functional_groups', []),
                        expected_benefits=rec_data.get('expected_benefits', [])
                    )
                    recommendations.append(recommendation)
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI recommendations response as JSON: {e}")
            # Fallback: create a basic recommendation from the response
            recommendations.append(AIRecommendation(
                title='AI Recommendations Available',
                description=response_text[:500] + '...' if len(response_text) > 500 else response_text,
                action_items=['Review AI analysis output'],
                priority='medium',
                estimated_effort='medium',
                functional_groups=['general'],
                expected_benefits=['Improved code quality']
            ))
        
        return recommendations
    
    def clear_cache(self):
        """Clear all cached analysis results."""
        self._project_data_cache = None
        self._insights_cache = None
        self._recommendations_cache = None
