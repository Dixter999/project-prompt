"""
Suggestions generator for ProjectPrompt.
Generates improvement suggestions based on project analysis.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

try:
    from ..ai.client import AIClient
    from ..models.project import ProjectAnalysis, Suggestion, SuggestionReport
except ImportError:
    # Fallback for direct execution
    from ai.client import AIClient
    from models.project import ProjectAnalysis, Suggestion, SuggestionReport
    low_priority_count: int


class SuggestionsGenerator:
    """Generates project improvement suggestions."""
    
    def __init__(self, ai_client: AIClient):
        """Initialize with AI client.
        
        Args:
            ai_client: AI client for generating suggestions
        """
        self.ai_client = ai_client
    
    def generate_suggestions(
        self, 
        analysis: ProjectAnalysis, 
        focus_areas: Optional[List[str]] = None,
        max_suggestions: int = 10
    ) -> SuggestionReport:
        """Generate improvement suggestions for a project.
        
        Args:
            analysis: Project analysis results
            focus_areas: Specific areas to focus on
            max_suggestions: Maximum number of suggestions to generate
            
        Returns:
            Complete suggestions report
        """
        # Build context for AI
        context = self._build_context(analysis)
        
        # Generate suggestions using AI
        ai_response = self.ai_client.generate_suggestions(context, focus_areas)
        
        if not ai_response.get('success', False):
            # Fallback to basic suggestions if AI fails
            return self._generate_basic_suggestions(analysis)
        
        # Parse AI response into structured suggestions
        suggestions = self._parse_ai_suggestions(ai_response['suggestions'])
        
        # Limit suggestions if needed
        if len(suggestions) > max_suggestions:
            suggestions = sorted(suggestions, key=lambda x: x.priority, reverse=True)[:max_suggestions]
        
        # Generate summary
        summary = self._generate_summary(analysis, suggestions)
        
        # Count priorities
        priority_counts = self._count_priorities(suggestions)
        
        return SuggestionReport(
            project_name=analysis.project_name,
            suggestions=suggestions,
            summary=summary,
            high_priority_count=priority_counts['high'],
            medium_priority_count=priority_counts['medium'],
            low_priority_count=priority_counts['low']
        )
    
    def _build_context(self, analysis: ProjectAnalysis) -> str:
        """Build context string for AI analysis."""
        context_parts = [
            f"Project: {analysis.project_name}",
            f"Main Language: {analysis.main_language}",
            f"File Count: {analysis.file_count}",
            f"Directory Count: {analysis.directory_count}",
            ""
        ]
        
        if analysis.detected_functionalities:
            context_parts.extend([
                "Detected Functionalities:",
                *[f"- {func}" for func in analysis.detected_functionalities],
                ""
            ])
        
        if analysis.important_files:
            context_parts.extend([
                "Important Files:",
                *[f"- {file}" for file in analysis.important_files[:10]],  # Limit to 10
                ""
            ])
        
        if analysis.ai_context:
            context_parts.extend([
                "Project Structure:",
                analysis.ai_context[:2000],  # Limit context size
                ""
            ])
        
        return "\n".join(context_parts)
    
    def _parse_ai_suggestions(self, ai_text: str) -> List[Suggestion]:
        """Parse AI-generated suggestions text into structured suggestions.
        
        This is a simplified parser. In a production system, you might want
        to use more sophisticated parsing or ask the AI to return JSON.
        """
        suggestions = []
        
        # Basic parsing - look for numbered items or bullet points
        lines = ai_text.split('\n')
        current_suggestion = None
        current_category = "General"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for category headers
            if any(keyword in line.lower() for keyword in ['code quality', 'performance', 'security', 'testing', 'architecture']):
                if 'code quality' in line.lower():
                    current_category = "Code Quality"
                elif 'performance' in line.lower():
                    current_category = "Performance"
                elif 'security' in line.lower():
                    current_category = "Security"
                elif 'testing' in line.lower():
                    current_category = "Testing"
                elif 'architecture' in line.lower():
                    current_category = "Architecture"
                continue
            
            # Check for suggestion items (numbered or bulleted)
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '*')) and len(line) > 10:
                if current_suggestion:
                    suggestions.append(current_suggestion)
                
                # Extract title and description
                content = line[2:].strip() if line[1] == '.' else line[1:].strip()
                
                # Determine priority based on keywords
                priority = self._determine_priority(content)
                impact = self._determine_impact(content)
                effort = self._determine_effort(content)
                
                current_suggestion = Suggestion(
                    category=current_category,
                    title=content[:100],  # First 100 chars as title
                    description=content,
                    impact=impact,
                    effort=effort,
                    priority=priority,
                    implementation_steps=[]
                )
            
            # Add implementation steps
            elif current_suggestion and line.startswith(('-', '*', '•')):
                step = line[1:].strip()
                if step and len(step) > 5:
                    current_suggestion.implementation_steps.append(step)
        
        # Add the last suggestion
        if current_suggestion:
            suggestions.append(current_suggestion)
        
        return suggestions
    
    def _determine_priority(self, text: str) -> int:
        """Determine priority based on text content."""
        text_lower = text.lower()
        
        # High priority keywords
        if any(keyword in text_lower for keyword in ['security', 'vulnerability', 'critical', 'urgent', 'bug']):
            return 9
        
        # Medium-high priority
        if any(keyword in text_lower for keyword in ['performance', 'optimization', 'refactor']):
            return 7
        
        # Medium priority
        if any(keyword in text_lower for keyword in ['test', 'documentation', 'maintainability']):
            return 5
        
        # Low priority
        return 3
    
    def _determine_impact(self, text: str) -> str:
        """Determine impact level based on text content."""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ['security', 'performance', 'critical', 'architecture']):
            return "High"
        elif any(keyword in text_lower for keyword in ['refactor', 'optimization', 'structure']):
            return "Medium"
        else:
            return "Low"
    
    def _determine_effort(self, text: str) -> str:
        """Determine effort level based on text content."""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ['rewrite', 'redesign', 'migrate', 'refactor']):
            return "High"
        elif any(keyword in text_lower for keyword in ['update', 'improve', 'optimize']):
            return "Medium"
        else:
            return "Low"
    
    def _generate_basic_suggestions(self, analysis: ProjectAnalysis) -> SuggestionReport:
        """Generate basic suggestions when AI is not available."""
        suggestions = []
        
        # Basic suggestions based on analysis
        if analysis.file_count > 100:
            suggestions.append(Suggestion(
                category="Architecture",
                title="Consider project modularization",
                description="Large number of files detected. Consider organizing into modules or packages.",
                impact="Medium",
                effort="Medium",
                priority=6,
                implementation_steps=[
                    "Analyze current file structure",
                    "Group related files into modules",
                    "Create clear module boundaries",
                    "Update import statements"
                ]
            ))
        
        if 'web' in analysis.detected_functionalities:
            suggestions.append(Suggestion(
                category="Security",
                title="Review web security practices",
                description="Web functionality detected. Review security best practices.",
                impact="High",
                effort="Medium",
                priority=8,
                implementation_steps=[
                    "Audit input validation",
                    "Check authentication mechanisms",
                    "Review HTTPS configuration",
                    "Validate CSRF protection"
                ]
            ))
        
        if 'api' in analysis.detected_functionalities:
            suggestions.append(Suggestion(
                category="Documentation",
                title="Add API documentation",
                description="API functionality detected. Ensure comprehensive documentation exists.",
                impact="Medium",
                effort="Low",
                priority=5,
                implementation_steps=[
                    "Document all endpoints",
                    "Add request/response examples",
                    "Include authentication details",
                    "Set up automated doc generation"
                ]
            ))
        
        summary = f"Generated {len(suggestions)} basic suggestions for {analysis.project_name}"
        priority_counts = self._count_priorities(suggestions)
        
        return SuggestionReport(
            project_name=analysis.project_name,
            suggestions=suggestions,
            summary=summary,
            high_priority_count=priority_counts['high'],
            medium_priority_count=priority_counts['medium'],
            low_priority_count=priority_counts['low']
        )
    
    def _generate_summary(self, analysis: ProjectAnalysis, suggestions: List[Suggestion]) -> str:
        """Generate summary of suggestions."""
        if not suggestions:
            return f"No suggestions generated for {analysis.project_name}"
        
        priority_counts = self._count_priorities(suggestions)
        top_categories = self._get_top_categories(suggestions)
        
        return f"""
Analysis complete for {analysis.project_name}:
- Generated {len(suggestions)} improvement suggestions
- {priority_counts['high']} high priority, {priority_counts['medium']} medium priority, {priority_counts['low']} low priority
- Main focus areas: {', '.join(top_categories[:3])}
- Recommended to start with high priority security and performance items
""".strip()
    
    def _count_priorities(self, suggestions: List[Suggestion]) -> Dict[str, int]:
        """Count suggestions by priority level."""
        counts = {'high': 0, 'medium': 0, 'low': 0}
        
        for suggestion in suggestions:
            if suggestion.priority >= 8:
                counts['high'] += 1
            elif suggestion.priority >= 5:
                counts['medium'] += 1
            else:
                counts['low'] += 1
        
        return counts
    
    def _get_top_categories(self, suggestions: List[Suggestion]) -> List[str]:
        """Get most common suggestion categories."""
        category_counts = {}
        for suggestion in suggestions:
            category_counts[suggestion.category] = category_counts.get(suggestion.category, 0) + 1
        
        return sorted(category_counts.keys(), key=lambda x: category_counts[x], reverse=True)
