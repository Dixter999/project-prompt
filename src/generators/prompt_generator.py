#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Implementation Prompt Generator for ProjectPrompt v2.0
Generates specific implementation prompts from suggestion files

Parses structured suggestion files and creates detailed prompts
for each phase to help implement AI suggestions with external AI assistants.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import json


class ImplementationPromptGenerator:
    """Generates prompts specifically for implementing each phase of suggestions"""
    
    def __init__(self, base_output_dir: Optional[Path] = None):
        """Initialize the prompt generator
        
        Args:
            base_output_dir: Base output directory (defaults to ./project-prompt-output)
        """
        self.base_output_dir = base_output_dir or Path("./project-prompt-output")
        self.suggestions_dir = self.base_output_dir / "suggestions"
        self.prompts_dir = self.base_output_dir / "prompts"
    
    def generate_prompts_for_suggestion(self, suggestion_name: str) -> List[str]:
        """Generate prompts for all phases of a suggestion
        
        Args:
            suggestion_name: Name of the suggestion (e.g., "feature_modules")
            
        Returns:
            List of generated prompt file paths
            
        Raises:
            FileNotFoundError: If suggestion file doesn't exist
        """
        # Find suggestion file
        suggestion_file = self.suggestions_dir / f"{suggestion_name}-suggestions.md"
        if not suggestion_file.exists():
            raise FileNotFoundError(f"Suggestion file not found: {suggestion_file}")
        
        # Read and parse suggestion content
        suggestion_content = suggestion_file.read_text(encoding='utf-8')
        phases = self.parse_suggestion_phases(suggestion_content)
        
        if not phases:
            raise ValueError(f"No phases found in suggestion file: {suggestion_file}")
        
        # Create prompts directory
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate prompt for each phase
        generated_files = []
        for phase in phases:
            prompt_content = self.generate_phase_prompt(phase, suggestion_name, len(phases))
            
            # Save prompt file
            prompt_filename = f"{suggestion_name}-phase{phase['number']}-prompt.md"
            prompt_file = self.prompts_dir / prompt_filename
            prompt_file.write_text(prompt_content, encoding='utf-8')
            generated_files.append(str(prompt_file))
        
        return generated_files
    
    def generate_single_phase_prompt(self, suggestion_name: str, phase_number: int) -> str:
        """Generate prompt for a specific phase only
        
        Args:
            suggestion_name: Name of the suggestion
            phase_number: Phase number to generate prompt for
            
        Returns:
            Path to generated prompt file
            
        Raises:
            FileNotFoundError: If suggestion file doesn't exist
            ValueError: If phase number not found
        """
        # Find suggestion file
        suggestion_file = self.suggestions_dir / f"{suggestion_name}-suggestions.md"
        if not suggestion_file.exists():
            raise FileNotFoundError(f"Suggestion file not found: {suggestion_file}")
        
        # Read and parse suggestion content
        suggestion_content = suggestion_file.read_text(encoding='utf-8')
        phases = self.parse_suggestion_phases(suggestion_content)
        
        # Find the specific phase
        target_phase = None
        for phase in phases:
            if phase['number'] == phase_number:
                target_phase = phase
                break
        
        if not target_phase:
            available_phases = [str(p['number']) for p in phases]
            raise ValueError(f"Phase {phase_number} not found. Available phases: {', '.join(available_phases)}")
        
        # Create prompts directory
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate prompt for the specific phase
        prompt_content = self.generate_phase_prompt(target_phase, suggestion_name, len(phases))
        
        # Save prompt file
        prompt_filename = f"{suggestion_name}-phase{phase_number}-prompt.md"
        prompt_file = self.prompts_dir / prompt_filename
        prompt_file.write_text(prompt_content, encoding='utf-8')
        
        return str(prompt_file)
    
    def parse_suggestion_phases(self, suggestion_content: str) -> List[Dict[str, Any]]:
        """Extract structured information from each phase in the suggestion
        
        Args:
            suggestion_content: Full content of the suggestion file
            
        Returns:
            List of phase dictionaries with parsed information
        """
        phases = []
        
        # Pattern to find phases: ### [number]. [name] ✅
        phase_pattern = r'### (\d+)\.\s+([^✅\n]+)✅'
        
        phase_matches = list(re.finditer(phase_pattern, suggestion_content))
        
        for i, match in enumerate(phase_matches):
            phase_num = int(match.group(1))
            phase_name = match.group(2).strip()
            
            # Find the content for this phase (between this match and the next)
            start_pos = match.end()
            if i + 1 < len(phase_matches):
                end_pos = phase_matches[i + 1].start()
            else:
                end_pos = len(suggestion_content)
            
            phase_content = suggestion_content[start_pos:end_pos].strip()
            
            # Parse phase details
            phase_data = {
                'number': phase_num,
                'name': phase_name,
                'branch': self.extract_branch(phase_content),
                'description': self.extract_description(phase_content),
                'files': self.extract_files(phase_content),
                'libraries': self.extract_libraries(phase_content),
                'steps': self.extract_steps(phase_content)
            }
            
            phases.append(phase_data)
        
        return phases
    
    def extract_branch(self, phase_content: str) -> str:
        """Extract branch name from phase content"""
        branch_match = re.search(r'- \*\*Branch\*\*:\s*`([^`]+)`', phase_content)
        return branch_match.group(1) if branch_match else "feature/implementation"
    
    def extract_description(self, phase_content: str) -> str:
        """Extract description from phase content"""
        desc_match = re.search(r'- \*\*Description\*\*:\s*([^\n]+)', phase_content)
        return desc_match.group(1).strip() if desc_match else "Implementation phase"
    
    def extract_files(self, phase_content: str) -> List[Dict[str, str]]:
        """Extract files to modify/create from phase content"""
        files = []
        
        # Find the files section
        files_section_match = re.search(r'- \*\*Files to modify/create\*\*:(.*?)- \*\*Libraries/Tools', phase_content, re.DOTALL)
        if not files_section_match:
            return files
        
        files_text = files_section_match.group(1)
        
        # Extract individual file entries
        file_pattern = r'  - `([^`]+)` - ([^✅\n]+)✅?'
        for match in re.finditer(file_pattern, files_text):
            files.append({
                'path': match.group(1).strip(),
                'purpose': match.group(2).strip()
            })
        
        return files
    
    def extract_libraries(self, phase_content: str) -> List[Dict[str, str]]:
        """Extract libraries/tools from phase content"""
        libraries = []
        
        # Find the libraries section
        libs_section_match = re.search(r'- \*\*Libraries/Tools to use\*\*:(.*?)- \*\*Steps', phase_content, re.DOTALL)
        if not libs_section_match:
            return libraries
        
        libs_text = libs_section_match.group(1)
        
        # Extract individual library entries
        lib_pattern = r'  - `([^`]+)` - ([^✅\n]+)✅?'
        for match in re.finditer(lib_pattern, libs_text):
            libraries.append({
                'name': match.group(1).strip(),
                'purpose': match.group(2).strip()
            })
        
        return libraries
    
    def extract_steps(self, phase_content: str) -> List[str]:
        """Extract implementation steps from phase content"""
        steps = []
        
        # Find the steps section
        steps_section_match = re.search(r'- \*\*Steps to follow\*\*:(.*?)(?=\n### |\n\n|\Z)', phase_content, re.DOTALL)
        if not steps_section_match:
            return steps
        
        steps_text = steps_section_match.group(1)
        
        # Extract numbered steps
        step_pattern = r'  (\d+)\.\s+([^\n]+)'
        for match in re.finditer(step_pattern, steps_text):
            steps.append(match.group(2).strip())
        
        return steps
    
    def generate_phase_prompt(self, phase_data: Dict[str, Any], suggestion_name: str, total_phases: int) -> str:
        """Generate implementation prompt for a specific phase
        
        Args:
            phase_data: Parsed phase information
            suggestion_name: Name of the suggestion group
            total_phases: Total number of phases in the suggestion
            
        Returns:
            Complete prompt content as markdown string
        """
        phase_number = phase_data['number']
        phase_name = phase_data['name']
        branch_name = phase_data['branch']
        description = phase_data['description']
        files = phase_data['files']
        libraries = phase_data['libraries']
        steps = phase_data['steps']
        
        # Generate files section
        files_section = ""
        if files:
            files_section = "\n".join([f"- **`{file['path']}`** - {file['purpose']}" for file in files])
        else:
            files_section = "- No specific files mentioned"
        
        # Generate libraries section
        libraries_section = ""
        if libraries:
            libraries_section = "\n".join([f"- **`{lib['name']}`** - {lib['purpose']}" for lib in libraries])
        else:
            libraries_section = "- No specific libraries mentioned"
        
        # Generate steps section
        steps_section = ""
        if steps:
            steps_section = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)])
        else:
            steps_section = "1. Begin implementation based on the phase description"
        
        # Get relevant project context
        context_files = self.get_relevant_context_files()
        
        prompt_template = f"""# Implementation Prompt: {suggestion_name.title().replace('_', ' ')} - Phase {phase_number}

## Project Context

I am working on implementing improvements for my project based on AI-generated suggestions. I have completed the analysis phase and now need to implement **Phase {phase_number}: {phase_name}** from my improvement plan.

## Phase Details

**Branch to create**: `{branch_name}`
**Phase Description**: {description}

## Files to Modify/Create

{files_section}

## Libraries/Tools Required

{libraries_section}

## Implementation Steps

{steps_section}

## Specific Requirements

Based on the analysis of my project structure, please help me implement this phase by:

1. **Creating the branch**: Guide me through creating `{branch_name}` and setting up the development environment for this phase.

2. **File Implementation**: For each file listed above, provide specific implementation details including:
   - Complete code structure and architecture
   - Integration with existing codebase
   - Error handling and edge cases
   - Documentation and docstrings

3. **Dependencies Management**: Help me properly integrate the required libraries:
   - Installation commands
   - Configuration setup
   - Integration patterns
   - Version compatibility

4. **Testing Strategy**: Provide guidance on:
   - Unit tests for new functionality
   - Integration tests
   - Test data setup
   - Validation criteria

5. **Validation Steps**: Define how to verify this phase is correctly implemented:
   - Functional testing procedures
   - Performance validation
   - Integration verification
   - Code quality checks

## Context Files

The following files are particularly relevant to this implementation:
{context_files}

## Expected Outcome

By the end of this phase, I should have:
- Branch `{branch_name}` with all changes committed
- All specified files created/modified with proper functionality
- Dependencies installed and properly configured
- Tests passing and covering new functionality
- Documentation updated to reflect changes

Please provide detailed, step-by-step guidance to implement this phase successfully, including specific code examples and best practices for my project structure.

---

**Note**: This is Phase {phase_number} of {total_phases}. The previous phases have been completed as specified in the improvement plan.
"""
        
        return prompt_template
    
    def get_relevant_context_files(self) -> str:
        """Get list of relevant existing files for context"""
        # Try to get project structure information
        project_structure_file = self.base_output_dir / "analysis" / "project-structure.md"
        
        if project_structure_file.exists():
            return f"See project structure in: `{project_structure_file}`"
        else:
            return "Project structure files are available in the analysis directory"
    
    def list_available_suggestions(self) -> List[str]:
        """List all available suggestion files that can be used for prompt generation
        
        Returns:
            List of suggestion names (without -suggestions.md suffix)
        """
        if not self.suggestions_dir.exists():
            return []
        
        suggestion_files = self.suggestions_dir.glob("*-suggestions.md")
        return [file.stem.replace("-suggestions", "") for file in suggestion_files]
