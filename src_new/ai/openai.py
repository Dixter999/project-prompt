"""
OpenAI integration for ProjectPrompt.
Provides OpenAI-specific implementation of the AI client interface.
"""

import os
from typing import Optional, Dict, Any, List
from openai import OpenAI
from .client import BaseAIClient


class OpenAIClient(BaseAIClient):
    """OpenAI client implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key. If None, uses OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI API.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional parameters for the API call
            
        Returns:
            Generated response text
        """
        try:
            # Prepare messages
            messages = [{"role": "user", "content": prompt}]
            
            # API parameters
            params = {
                "model": kwargs.get('model', self.model),
                "messages": messages,
                "max_tokens": kwargs.get('max_tokens', 4000),
                "temperature": kwargs.get('temperature', 0.7),
            }
            
            # Make API call
            response = self.client.chat.completions.create(**params)
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
    
    def analyze_project(self, project_context: str, analysis_type: str = "general") -> Dict[str, Any]:
        """Analyze project using OpenAI.
        
        Args:
            project_context: Project analysis context
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results dictionary
        """
        prompt = self._build_analysis_prompt(project_context, analysis_type)
        
        try:
            response = self.generate_response(
                prompt,
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=3000
            )
            
            return {
                "provider": "openai",
                "model": self.model,
                "analysis_type": analysis_type,
                "response": response,
                "success": True
            }
            
        except Exception as e:
            return {
                "provider": "openai",
                "model": self.model,
                "analysis_type": analysis_type,
                "error": str(e),
                "success": False
            }
    
    def generate_suggestions(self, project_context: str, focus_areas: List[str] = None) -> Dict[str, Any]:
        """Generate project improvement suggestions.
        
        Args:
            project_context: Project analysis context
            focus_areas: Specific areas to focus on
            
        Returns:
            Suggestions dictionary
        """
        focus_text = ""
        if focus_areas:
            focus_text = f"\nFocus specifically on: {', '.join(focus_areas)}"
        
        prompt = f"""
Analyze this project and provide specific improvement suggestions:

{project_context}
{focus_text}

Please provide suggestions in the following categories:
1. Code Quality & Structure
2. Performance Optimizations
3. Security Improvements
4. Testing & Documentation
5. Dependencies & Architecture

For each suggestion, include:
- Clear description
- Impact level (High/Medium/Low)
- Implementation effort (High/Medium/Low)
- Specific steps to implement

Format as structured text with clear sections.
"""

        try:
            response = self.generate_response(
                prompt,
                temperature=0.4,
                max_tokens=3500
            )
            
            return {
                "provider": "openai",
                "model": self.model,
                "suggestions": response,
                "focus_areas": focus_areas or [],
                "success": True
            }
            
        except Exception as e:
            return {
                "provider": "openai",
                "model": self.model,
                "error": str(e),
                "success": False
            }
    
    def _build_analysis_prompt(self, project_context: str, analysis_type: str) -> str:
        """Build analysis prompt based on type."""
        base_prompt = f"""
Analyze this project thoroughly:

{project_context}

"""
        
        if analysis_type == "architecture":
            base_prompt += """
Focus on:
- Overall architecture and design patterns
- Code organization and structure
- Module dependencies and coupling
- Scalability considerations
"""
        elif analysis_type == "quality":
            base_prompt += """
Focus on:
- Code quality and maintainability
- Best practices adherence
- Potential bugs or issues
- Refactoring opportunities
"""
        elif analysis_type == "security":
            base_prompt += """
Focus on:
- Security vulnerabilities
- Input validation issues
- Authentication and authorization
- Data protection concerns
"""
        else:  # general
            base_prompt += """
Provide a comprehensive analysis covering:
- Overall project structure
- Code quality assessment
- Potential improvements
- Architecture recommendations
"""
        
        base_prompt += "\nProvide specific, actionable insights with examples where relevant."
        
        return base_prompt
