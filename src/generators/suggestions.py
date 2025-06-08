#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple AI Suggestion Generator for ProjectPrompt v2.0
Generates contextualized suggestions using AI APIs

Phase 4: Simplified generator
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import anthropic
import openai


class SuggestionGenerator:
    """Simple AI-powered suggestions generator"""
    
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
            'project_type': 'unknown',
            'main_language': 'unknown',
            'dependencies': {},
            'statistics': {}
        }
        
        # Load groups data
        groups_file = analysis_path / "groups.json"
        if groups_file.exists():
            with open(groups_file) as f:
                groups_data = json.load(f)
                context['files'] = groups_data.get('groups', {}).get(group_name, [])
        
        # Try to detect project type from files and structure
        context['project_type'] = self._detect_project_type(analysis_path)
        context['main_language'] = self._detect_main_language(context['files'])
        
        # Load group-specific analysis if available
        group_analysis_file = analysis_path / "analysis" / "functional-groups" / f"{group_name}-analysis.md"
        if group_analysis_file.exists():
            context['analysis_content'] = group_analysis_file.read_text(encoding='utf-8')
        
        return context
    
    def create_contextual_prompt(self, group_context: Dict[str, Any], detail_level: str = "medium") -> str:
        """
        Create a contextualized prompt for AI suggestions with standardized phase format.
        
        Args:
            group_context: Context information for the group
            detail_level: Level of detail ("basic", "medium", "detailed")
            
        Returns:
            Formatted prompt string
        """
        group_name = group_context.get('group_name', 'Unknown Group')
        files = group_context.get('files', [])
        project_type = group_context.get('project_type', 'unknown')
        main_language = group_context.get('main_language', 'unknown')
        
        # Base prompt template
        prompt_parts = [
            f"# Code Analysis and Improvement Suggestions for '{group_name}'",
            "",
            "You are an expert software architect and code reviewer. Analyze the following group of files and provide actionable improvement suggestions in standardized phase format.",
            "",
            "## Project Information:",
            f"- **Group**: {group_name}",
            f"- **Project Type**: {project_type}",
            f"- **Main Language**: {main_language}",
            f"- **File Count**: {len(files)}",
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
            "## REQUIRED FORMAT:",
            "",
            "Provide suggestions in the following standardized phase format:",
            "",
            "### [Number] [Phase Name] ✅",
            "- **Branch**: `[suggested-branch-name]`",
            "- **Description**: [concise phase description]",
            "- **Files to modify/create**:",
            "  - `[path/file]` - [purpose] ✅",
            "  - `[path/file]` - [purpose] ✅",
            "- **Libraries/Tools to use**:",
            "  - `[library]` - [purpose] ✅",
            "  - `[tool]` - [purpose] ✅",
            "- **Steps to follow**:",
            "  1. [step 1]",
            "  2. [step 2]",
            "",
            "## Areas of Improvement to Consider:",
            "1. **Code Organization and Structure**",
            "2. **Performance Optimizations**", 
            "3. **Security Considerations**",
            "4. **Maintainability Improvements**",
            "5. **Testing Recommendations**",
            "6. **Documentation Needs**",
            ""
        ])
        
        # Add project-specific considerations
        project_specific_template = self._get_project_specific_template(project_type)
        if project_specific_template:
            prompt_parts.extend([
                project_specific_template,
                ""
            ])
        
        # Adjust depth based on detail level
        if detail_level == "basic":
            prompt_parts.extend([
                "**Instructions**: Provide 2-3 high-impact phases with brief explanations.",
                "Focus on the most critical improvements that would provide immediate value."
            ])
        elif detail_level == "detailed":
            prompt_parts.extend([
                "**Instructions**: Provide comprehensive analysis with 4-6 detailed phases.",
                "Include specific code examples, implementation steps and potential risks.",
                "Consider architectural patterns, design principles and best practices."
            ])
        else:  # medium
            prompt_parts.extend([
                "**Instructions**: Provide 3-4 balanced phases with clear explanations.",
                "Include practical implementation guidance and prioritization."
            ])
        
        prompt_parts.extend([
            "",
            "**IMPORTANT**: Ensure each phase includes:",
            "- Specific and descriptive branch name",
            "- Specific list of files to modify/create",
            "- Concrete libraries and tools to use",
            "- Detailed implementation steps",
            "- Use the exact format shown above with ✅ at the end of each element",
            ""
        ])
        
        return "\n".join(prompt_parts)
    
    def _get_project_specific_template(self, project_type: str) -> str:
        """Get project-specific template based on detected project type"""
        templates = {
            'api': """## API-Specific Considerations

- **Documentation**: Ensure all endpoints are documented with Swagger/OpenAPI
- **Validation**: Implement validation schemas for all inputs
- **Security**: Verify authentication and authorization implementation
- **Performance**: Consider caching strategies and query optimization
- **Versioning**: Establish clear API versioning strategy""",
            
            'web_application': """## Frontend-Specific Considerations

- **Responsive**: Verify adaptability to different devices
- **Accessibility**: Implement WCAG standards for accessibility
- **Performance**: Optimize initial load and interaction times
- **State**: Manage state consistently and predictably
- **Componentization**: Ensure reusable and well-documented components""",
            
            'cli_tool': """## CLI-Specific Considerations

- **UX**: Design clear terminal user experience
- **Documentation**: Provide detailed help for each command
- **Errors**: Implement descriptive and helpful error handling
- **Configuration**: Allow customization through configuration files
- **Installation**: Facilitate installation and update process""",
            
            'library': """## Library-Specific Considerations

- **Public API**: Define clear and stable interface
- **Documentation**: Provide usage examples and detailed guides
- **Compatibility**: Maintain backward compatibility
- **Testing**: Implement comprehensive tests for all functionality
- **Distribution**: Configure appropriate packaging and distribution"""
        }
        
        return templates.get(project_type, "")
    
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
        """Generate mock suggestions for testing purposes using standardized phase format"""
        group_name = group_context.get('group_name', 'Unknown Group')
        file_count = len(group_context.get('files', []))
        project_type = group_context.get('project_type', 'unknown')
        
        return f"""# AI Suggestions for {group_name} (Test Mode)

## 📊 Analysis Summary
- **Group**: {group_name}
- **Files analyzed**: {file_count}
- **Project Type**: {project_type}
- **Mode**: Test Mode (no API key required)

## 🚀 Improvement Suggestions in Phases

### 1. Code Organization and Structure ✅
- **Branch**: `refactor/code-organization`
- **Description**: Reorganize code structure to improve modularity and maintainability
- **Files to modify/create**:
  - `src/core/` - Reorganize main modules ✅
  - `src/utils/helpers.py` - Create utilities module ✅
- **Libraries/Tools to use**:
  - `pylint` - Code quality analysis ✅
  - `black` - Automatic code formatting ✅
- **Steps to follow**:
  1. Analyze current code structure
  2. Identify responsibilities of each module
  3. Refactor to separate concerns
  4. Create clear interfaces between modules

### 2. Testing Implementation ✅
- **Branch**: `feature/comprehensive-testing`
- **Description**: Implement comprehensive test suite to ensure quality and stability
- **Files to modify/create**:
  - `tests/unit/` - Create unit tests ✅
  - `tests/integration/` - Create integration tests ✅
  - `conftest.py` - Pytest configuration ✅
- **Libraries/Tools to use**:
  - `pytest` - Testing framework ✅
  - `coverage` - Coverage measurement ✅
  - `pytest-mock` - Mocking for tests ✅
- **Steps to follow**:
  1. Install pytest and dependencies
  2. Configure test structure
  3. Implement unit tests for critical functions
  4. Add integration tests for main flows

### 3. Performance Optimization ✅
- **Branch**: `optimize/performance-improvements`
- **Description**: Optimize system performance through caching and better algorithms
- **Files to modify/create**:
  - `src/core/cache.py` - Caching system ✅
  - `src/utils/performance.py` - Performance utilities ✅
- **Libraries/Tools to use**:
  - `cachetools` - Cache implementation ✅
  - `memory_profiler` - Memory profiling ✅
- **Steps to follow**:
  1. Identify performance bottlenecks
  2. Implement caching system for expensive operations
  3. Optimize critical algorithms
  4. Measure and validate improvements

{self._get_project_specific_template(project_type)}

---
*Note: This is a test mode response. Configure API keys for complete AI suggestions.*
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
    
    def _detect_project_type(self, analysis_path: Path) -> str:
        """Detect project type from structure and files"""
        # Check if project structure file exists
        structure_file = analysis_path / "analysis" / "project-structure.md"
        if structure_file.exists():
            content = structure_file.read_text(encoding='utf-8')
            if "API" in content or "FastAPI" in content or "Flask" in content:
                return "API"
            elif "React" in content or "Vue" in content or "Angular" in content:
                return "Frontend"
            elif "CLI" in content or "command line" in content:
                return "CLI"
            elif "library" in content.lower() or "package" in content.lower():
                return "Library"
        return "unknown"
    
    def _detect_main_language(self, files: list) -> str:
        """Detect main language from file extensions"""
        extensions = {}
        for file in files:
            if '.' in file:
                ext = file.split('.')[-1].lower()
                extensions[ext] = extensions.get(ext, 0) + 1
        
        if extensions:
            main_ext = max(extensions, key=extensions.get)
            lang_map = {
                'py': 'Python',
                'js': 'JavaScript',
                'ts': 'TypeScript',
                'java': 'Java',
                'cpp': 'C++',
                'c': 'C',
                'go': 'Go',
                'rs': 'Rust'
            }
            return lang_map.get(main_ext, main_ext)
        return "unknown"
