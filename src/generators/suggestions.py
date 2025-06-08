#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple AI Suggestion Generator for ProjectPrompt v2.0
Generates contextualized suggestions using AI APIs

Fase 4: Generador simplificado
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import anthropic
import openai


class SuggestionGenerator:
    """Generador simple de sugerencias con IA"""
    
    def __init__(self, api_provider: str = "anthropic", test_mode: bool = False):
        """
        Initialize the suggestion generator.
        
        Args:
            api_provider: "anthropic" or "openai"
            test_mode: If True, run in test mode without requiring API keys
        """
        self.api_provider = api_provider
        self.test_mode = test_mode
        self.client = None
        
        if not test_mode:
            self._init_client()
    
    def _init_client(self):
        """Initialize the AI client based on provider"""
        if self.api_provider == "anthropic":
            from ..utils.config import Config
            config = Config()
            if config.has_anthropic_key():
                self.client = anthropic.Anthropic(api_key=config.anthropic_api_key)
            else:
                self.test_mode = True
        elif self.api_provider == "openai":
            from ..utils.config import Config
            config = Config()
            if config.has_openai_key():
                self.client = openai.OpenAI(api_key=config.openai_api_key)
            else:
                self.test_mode = True
        else:
            raise ValueError(f"Unsupported API provider: {self.api_provider}")
    
    def load_group_context(self, group_name: str, analysis_path: Path) -> Dict[str, Any]:
        """
        Load context for a specific group from analysis files.
        
        Args:
            group_name: Name of the group to analyze
            analysis_path: Path to analysis directory
            
        Returns:
            Dictionary with group context information
        """
        context = {
            'group_name': group_name,
            'files': [],
            'dependencies': {},
            'statistics': {}
        }
        
        # Load groups data
        groups_file = analysis_path / "groups.json"
        if groups_file.exists():
            with open(groups_file) as f:
                groups_data = json.load(f)
                context['files'] = groups_data.get('groups', {}).get(group_name, [])
        
        # Load dependencies if available
        deps_file = analysis_path / "dependencies.json"
        if deps_file.exists():
            with open(deps_file) as f:
                deps_data = json.load(f)
                context['dependencies'] = deps_data.get(group_name, {})
        
        # Load file mappings
        mappings_file = analysis_path / "file_mappings.json"
        if mappings_file.exists():
            with open(mappings_file) as f:
                mappings_data = json.load(f)
                context['mappings'] = mappings_data
        
        return context
    
    def create_contextual_prompt(self, group_context: Dict[str, Any], detail_level: str = "medium") -> str:
        """
        Create a contextualized prompt for AI suggestions.
        
        Args:
            group_context: Context information for the group
            detail_level: Level of detail ("basic", "medium", "detailed")
            
        Returns:
            Formatted prompt string
        """
        group_name = group_context.get('group_name', 'Unknown Group')
        files = group_context.get('files', [])
        
        # Base prompt template
        prompt_parts = [
            f"# Code Analysis and Improvement Suggestions for '{group_name}' Group",
            "",
            "You are an expert software architect and code reviewer. Please analyze the following group of files and provide actionable improvement suggestions.",
            "",
            "## Group Information:",
            f"- **Group Name**: {group_name}",
            f"- **Number of Files**: {len(files)}",
            f"- **Detail Level**: {detail_level}",
            "",
            "## Files in this group:",
        ]
        
        # Add file list
        for i, file_path in enumerate(files[:20], 1):  # Limit to first 20 files
            prompt_parts.append(f"{i}. `{file_path}`")
        
        if len(files) > 20:
            prompt_parts.append(f"... and {len(files) - 20} more files")
        
        prompt_parts.extend([
            "",
            "## Please provide suggestions in the following areas:",
            "1. **Code Organization & Structure**",
            "2. **Performance Optimizations**", 
            "3. **Security Considerations**",
            "4. **Maintainability Improvements**",
            "5. **Testing Recommendations**",
            "6. **Documentation Needs**",
            ""
        ])
        
        # Adjust depth based on detail level
        if detail_level == "basic":
            prompt_parts.extend([
                "**Instructions**: Provide 3-5 high-impact suggestions with brief explanations.",
                "Focus on the most critical improvements that would provide immediate value."
            ])
        elif detail_level == "detailed":
            prompt_parts.extend([
                "**Instructions**: Provide comprehensive analysis with detailed explanations.",
                "Include specific code examples, implementation steps, and potential risks.",
                "Consider architectural patterns, design principles, and best practices."
            ])
        else:  # medium
            prompt_parts.extend([
                "**Instructions**: Provide balanced suggestions with clear explanations.",
                "Include practical implementation guidance and prioritization."
            ])
        
        prompt_parts.extend([
            "",
            "## Output Format:",
            "Please structure your response as:",
            "- Priority Level (High/Medium/Low)",
            "- Suggestion Title",
            "- Description and rationale",
            "- Implementation steps (if applicable)",
            "- Potential benefits",
            ""
        ])
        
        return "\n".join(prompt_parts)
    
    def generate_suggestions(self, prompt: str, group_context: Dict[str, Any]) -> str:
        """
        Generate AI suggestions using the configured provider.
        
        Args:
            prompt: The formatted prompt to send to AI
            group_context: Context information for the group
            
        Returns:
            Generated suggestions as markdown text
        """
        if self.test_mode:
            return self._generate_test_suggestions(group_context)
        
        if self.api_provider == "anthropic":
            return self._generate_anthropic(prompt)
        elif self.api_provider == "openai":
            return self._generate_openai(prompt)
        else:
            raise ValueError(f"Unsupported API provider: {self.api_provider}")
    
    def _generate_test_suggestions(self, group_context: Dict[str, Any]) -> str:
        """Generate mock suggestions for testing purposes"""
        group_name = group_context.get('name', 'Unknown Group')
        file_count = len(group_context.get('files', []))
        
        return f"""# AI Suggestions for {group_name} (Test Mode)

## 📊 Analysis Summary
- **Group**: {group_name}
- **Files analyzed**: {file_count}
- **Mode**: Test Mode (no API key required)

## 🚀 Improvement Suggestions

### 1. Code Organization
- Consider grouping related functionality together
- Review file naming conventions for consistency

### 2. Documentation
- Add docstrings to main functions and classes
- Create README files for complex modules

### 3. Testing
- Implement unit tests for core functionality
- Consider integration tests for critical paths

### 4. Performance
- Review algorithmic complexity
- Consider caching for expensive operations

### 5. Maintainability
- Extract magic numbers into constants
- Consider using configuration files for settings

---
*Note: This is a test mode response. Set API keys for full AI-powered suggestions.*
"""
    
    def _generate_anthropic(self, prompt: str) -> str:
        """Generate suggestions using Anthropic Claude"""
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )
            return response.content[0].text
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}")
    
    def _generate_openai(self, prompt: str) -> str:
        """Generate suggestions using OpenAI GPT"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert software architect and code reviewer. Provide detailed, actionable improvement suggestions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=4000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
