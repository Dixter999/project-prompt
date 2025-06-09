"""
Response Processor - FASE 2 Component
Processes API responses and extracts actionable implementation content.
"""

import re
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
import ast

class ContentType(Enum):
    """Types of content that can be extracted from responses"""
    CODE = "code"
    FILE_MODIFICATION = "file_modification"
    COMMAND = "command"
    EXPLANATION = "explanation"
    VALIDATION = "validation"
    ERROR = "error"
    DEPENDENCY = "dependency"
    CONFIGURATION = "configuration"

@dataclass
class ExtractedContent:
    """Represents extracted content from an API response"""
    content_type: ContentType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    file_path: Optional[str] = None
    language: Optional[str] = None
    priority: int = 0  # 0=high, 1=medium, 2=low
    dependencies: List[str] = field(default_factory=list)
    validation_notes: Optional[str] = None

@dataclass
class FileModification:
    """Represents a file modification instruction"""
    file_path: str
    action: str  # 'create', 'modify', 'delete', 'rename'
    content: Optional[str] = None
    line_range: Optional[Tuple[int, int]] = None  # For partial modifications
    backup_original: bool = True
    description: str = ""

@dataclass
class ProcessedResponse:
    """Complete processed response with all extracted content"""
    response_id: str
    original_response: str
    extracted_content: List[ExtractedContent]
    file_modifications: List[FileModification]
    commands_to_run: List[Dict[str, Any]]
    dependencies_to_install: List[str]
    validation_steps: List[str]
    implementation_plan: Optional[Dict[str, Any]] = None
    confidence_score: float = 0.0
    warnings: List[str] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)

class ResponseProcessor:
    """
    Processes API responses and extracts actionable implementation content.
    Identifies code blocks, file modifications, commands, and validation steps.
    """
    
    def __init__(self):
        """Initialize the response processor"""
        self.code_patterns = {
            'python': [r'```python\n(.*?)```', r'```py\n(.*?)```'],
            'javascript': [r'```javascript\n(.*?)```', r'```js\n(.*?)```'],
            'typescript': [r'```typescript\n(.*?)```', r'```ts\n(.*?)```'],
            'bash': [r'```bash\n(.*?)```', r'```shell\n(.*?)```', r'```sh\n(.*?)```'],
            'yaml': [r'```yaml\n(.*?)```', r'```yml\n(.*?)```'],
            'json': [r'```json\n(.*?)```'],
            'html': [r'```html\n(.*?)```'],
            'css': [r'```css\n(.*?)```'],
            'sql': [r'```sql\n(.*?)```'],
            'markdown': [r'```markdown\n(.*?)```', r'```md\n(.*?)```'],
            'generic': [r'```\n(.*?)```']
        }
        
        self.command_patterns = [
            r'(?:Run|Execute|Type):\s*`([^`]+)`',
            r'(?:Command|Shell):\s*`([^`]+)`',
            r'\$\s*([^\n]+)',
            r'npm (?:install|run|start|build|test)\s+[^\n]+',
            r'pip install\s+[^\n]+',
            r'git (?:add|commit|push|pull)\s+[^\n]+',
            r'python\s+[^\n]+\.py',
            r'node\s+[^\n]+\.js'
        ]
        
        self.file_patterns = [
            r'(?:Create|Modify|Update|Edit)\s+(?:file\s+)?`([^`]+)`',
            r'File:\s*`([^`]+)`',
            r'Path:\s*`([^`]+)`',
            r'In\s+`([^`]+)`,?\s+(?:add|modify|update|change)',
            r'`([^`]+\.(?:py|js|ts|html|css|json|yaml|yml|md|txt))`'
        ]
        
        self.dependency_patterns = [
            r'(?:Install|Add|Use)\s+(?:dependency|package|library):\s*`([^`]+)`',
            r'npm install\s+([^\s\n]+)',
            r'pip install\s+([^\s\n]+)',
            r'yarn add\s+([^\s\n]+)',
            r'requirements\.txt.*:\s*([^\n]+)',
            r'package\.json.*:\s*"([^"]+)"'
        ]
    
    def process_response(self, 
                        response: str, 
                        response_id: Optional[str] = None,
                        context: Optional[Dict[str, Any]] = None) -> ProcessedResponse:
        """
        Process an API response and extract actionable content.
        
        Args:
            response: The API response text
            response_id: Optional unique identifier for the response
            context: Optional context information
            
        Returns:
            ProcessedResponse with all extracted content
        """
        if not response_id:
            import hashlib
            response_id = hashlib.md5(response.encode()).hexdigest()[:8]
        
        # Extract different types of content
        extracted_content = []
        
        # Extract code blocks
        code_content = self._extract_code_blocks(response)
        extracted_content.extend(code_content)
        
        # Extract file modifications
        file_modifications = self._extract_file_modifications(response)
        
        # Extract commands
        commands = self._extract_commands(response)
        
        # Extract dependencies
        dependencies = self._extract_dependencies(response)
        
        # Extract explanations and notes
        explanations = self._extract_explanations(response)
        extracted_content.extend(explanations)
        
        # Extract validation steps
        validation_steps = self._extract_validation_steps(response)
        
        # Generate implementation plan
        implementation_plan = self._generate_implementation_plan(
            code_content, file_modifications, commands, dependencies
        )
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(response, extracted_content)
        
        # Identify warnings and next actions
        warnings = self._identify_warnings(response, extracted_content)
        next_actions = self._suggest_next_actions(implementation_plan, context)
        
        return ProcessedResponse(
            response_id=response_id,
            original_response=response,
            extracted_content=extracted_content,
            file_modifications=file_modifications,
            commands_to_run=commands,
            dependencies_to_install=dependencies,
            validation_steps=validation_steps,
            implementation_plan=implementation_plan,
            confidence_score=confidence_score,
            warnings=warnings,
            next_actions=next_actions
        )
    
    def extract_implementation_steps(self, response: str) -> List[Dict[str, Any]]:
        """
        Extract step-by-step implementation instructions.
        
        Args:
            response: API response text
            
        Returns:
            List of implementation steps with details
        """
        steps = []
        
        # Look for numbered steps
        step_patterns = [
            r'(\d+)\.\s+([^\n]+(?:\n(?!\d+\.)[^\n]*)*)',
            r'Step\s+(\d+):\s*([^\n]+(?:\n(?!Step\s+\d+:)[^\n]*)*)',
            r'Phase\s+(\d+):\s*([^\n]+(?:\n(?!Phase\s+\d+:)[^\n]*)*)'
        ]
        
        for pattern in step_patterns:
            matches = re.finditer(pattern, response, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                step_num = int(match.group(1))
                step_content = match.group(2).strip()
                
                # Extract components from step content
                step_info = {
                    'step_number': step_num,
                    'description': step_content,
                    'commands': self._extract_commands_from_text(step_content),
                    'files': self._extract_file_references_from_text(step_content),
                    'code_snippets': self._extract_code_blocks_from_text(step_content),
                    'estimated_time': self._estimate_step_time(step_content),
                    'complexity': self._assess_step_complexity(step_content)
                }
                
                steps.append(step_info)
        
        return sorted(steps, key=lambda x: x['step_number'])
    
    def validate_response_completeness(self, processed: ProcessedResponse) -> Dict[str, Any]:
        """
        Validate that the processed response contains complete information.
        
        Args:
            processed: ProcessedResponse to validate
            
        Returns:
            Validation results with completeness assessment
        """
        validation = {
            'is_complete': True,
            'missing_elements': [],
            'quality_score': 0.0,
            'recommendations': []
        }
        
        # Check for essential elements
        if not processed.extracted_content:
            validation['missing_elements'].append('No actionable content extracted')
            validation['is_complete'] = False
        
        # Check for implementation guidance
        has_code = any(c.content_type == ContentType.CODE for c in processed.extracted_content)
        has_files = bool(processed.file_modifications)
        has_commands = bool(processed.commands_to_run)
        
        if not (has_code or has_files or has_commands):
            validation['missing_elements'].append('No implementation instructions found')
            validation['is_complete'] = False
        
        # Check for validation steps
        if not processed.validation_steps:
            validation['missing_elements'].append('No validation steps provided')
            validation['recommendations'].append('Request validation steps for the implementation')
        
        # Calculate quality score
        quality_factors = [
            len(processed.extracted_content) * 0.2,  # Content richness
            processed.confidence_score * 0.3,       # Confidence
            len(processed.validation_steps) * 0.1,  # Validation coverage
            (1.0 if processed.implementation_plan else 0.0) * 0.2,  # Has plan
            (1.0 if has_code and has_files else 0.5) * 0.2  # Implementation completeness
        ]
        
        validation['quality_score'] = min(1.0, sum(quality_factors))
        
        # Add recommendations based on missing elements
        if len(processed.extracted_content) < 3:
            validation['recommendations'].append('Request more detailed implementation guidance')
        
        if processed.confidence_score < 0.7:
            validation['recommendations'].append('Consider asking for clarification or more context')
        
        return validation
    
    def format_for_implementation(self, processed: ProcessedResponse, format_type: str = "markdown") -> str:
        """
        Format processed response for implementation use.
        
        Args:
            processed: ProcessedResponse to format
            format_type: Output format ('markdown', 'json', 'text')
            
        Returns:
            Formatted implementation guide
        """
        if format_type == "json":
            return json.dumps({
                'response_id': processed.response_id,
                'implementation_plan': processed.implementation_plan,
                'file_modifications': [
                    {
                        'file_path': fm.file_path,
                        'action': fm.action,
                        'description': fm.description,
                        'has_content': bool(fm.content)
                    }
                    for fm in processed.file_modifications
                ],
                'commands': processed.commands_to_run,
                'dependencies': processed.dependencies_to_install,
                'validation_steps': processed.validation_steps,
                'confidence_score': processed.confidence_score,
                'warnings': processed.warnings,
                'next_actions': processed.next_actions
            }, indent=2)
        
        elif format_type == "markdown":
            return self._format_markdown_implementation(processed)
        
        else:  # text format
            return self._format_text_implementation(processed)
    
    # Private methods
    
    def _extract_code_blocks(self, response: str) -> List[ExtractedContent]:
        """Extract code blocks from response"""
        content = []
        
        for language, patterns in self.code_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, response, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    code_content = match.group(1).strip()
                    if code_content:
                        extracted = ExtractedContent(
                            content_type=ContentType.CODE,
                            content=code_content,
                            language=language if language != 'generic' else None,
                            metadata={'pattern_used': pattern, 'match_start': match.start()}
                        )
                        content.append(extracted)
        
        return content
    
    def _extract_file_modifications(self, response: str) -> List[FileModification]:
        """Extract file modification instructions"""
        modifications = []
        
        # Look for explicit file creation/modification instructions
        file_section_pattern = r'(?:Files?|Create|Modify|Update).*?:(.*?)(?=\n\n|\n(?:[A-Z]|$)|$)'
        file_sections = re.finditer(file_section_pattern, response, re.DOTALL | re.IGNORECASE)
        
        for section in file_sections:
            section_text = section.group(1)
            
            # Extract individual file references
            for pattern in self.file_patterns:
                matches = re.finditer(pattern, section_text, re.IGNORECASE)
                for match in matches:
                    file_path = match.group(1).strip()
                    
                    # Determine action based on context
                    action = "modify"  # default
                    if "create" in match.group(0).lower():
                        action = "create"
                    elif "delete" in match.group(0).lower():
                        action = "delete"
                    
                    # Look for associated code content
                    content = self._find_associated_code(response, file_path)
                    
                    modification = FileModification(
                        file_path=file_path,
                        action=action,
                        content=content,
                        description=match.group(0)
                    )
                    modifications.append(modification)
        
        return modifications
    
    def _extract_commands(self, response: str) -> List[Dict[str, Any]]:
        """Extract command-line instructions"""
        commands = []
        
        for pattern in self.command_patterns:
            matches = re.finditer(pattern, response, re.MULTILINE)
            for match in matches:
                command = match.group(1).strip() if match.groups() else match.group(0).strip()
                
                # Clean up command
                command = command.replace('$', '').strip()
                
                if command:
                    cmd_info = {
                        'command': command,
                        'type': self._classify_command(command),
                        'description': self._get_command_context(response, match.start()),
                        'working_directory': self._infer_working_directory(command)
                    }
                    commands.append(cmd_info)
        
        return commands
    
    def _extract_dependencies(self, response: str) -> List[str]:
        """Extract dependency installation requirements"""
        dependencies = []
        
        for pattern in self.dependency_patterns:
            matches = re.finditer(pattern, response, re.IGNORECASE)
            for match in matches:
                dep = match.group(1).strip()
                if dep and dep not in dependencies:
                    dependencies.append(dep)
        
        return dependencies
    
    def _extract_explanations(self, response: str) -> List[ExtractedContent]:
        """Extract explanatory text and documentation"""
        explanations = []
        
        # Look for explanation sections
        explanation_patterns = [
            r'(?:Explanation|Note|Important|Warning):(.*?)(?=\n\n|\n(?:[A-Z]|$)|$)',
            r'(?:This|Here\'s|The following).*?(?:explains?|shows?|demonstrates?).*?[.!]',
            r'(?:To|In order to).*?(?:you|we).*?(?:need to|should|must).*?[.!]'
        ]
        
        for pattern in explanation_patterns:
            matches = re.finditer(pattern, response, re.DOTALL | re.IGNORECASE)
            for match in matches:
                explanation_text = match.group(0).strip()
                if len(explanation_text) > 20:  # Filter out very short matches
                    extracted = ExtractedContent(
                        content_type=ContentType.EXPLANATION,
                        content=explanation_text,
                        metadata={'pattern_used': pattern}
                    )
                    explanations.append(extracted)
        
        return explanations
    
    def _extract_validation_steps(self, response: str) -> List[str]:
        """Extract validation and testing steps"""
        steps = []
        
        validation_patterns = [
            r'(?:Test|Verify|Check|Validate):\s*([^\n]+)',
            r'To (?:test|verify|check|validate).*?:\s*([^\n]+)',
            r'(?:Testing|Validation) steps?:\s*(.*?)(?=\n\n|\n(?:[A-Z]|$)|$)'
        ]
        
        for pattern in validation_patterns:
            matches = re.finditer(pattern, response, re.DOTALL | re.IGNORECASE)
            for match in matches:
                step_text = match.group(1).strip()
                if step_text:
                    steps.append(step_text)
        
        return steps
    
    def _generate_implementation_plan(self, 
                                    code_content: List[ExtractedContent],
                                    file_modifications: List[FileModification],
                                    commands: List[Dict[str, Any]],
                                    dependencies: List[str]) -> Dict[str, Any]:
        """Generate a structured implementation plan"""
        plan = {
            'phases': [],
            'estimated_time': '30-60 minutes',
            'complexity': 'medium',
            'prerequisites': dependencies
        }
        
        # Phase 1: Dependencies
        if dependencies:
            plan['phases'].append({
                'phase': 1,
                'name': 'Install Dependencies',
                'description': 'Install required packages and dependencies',
                'actions': [f"Install {dep}" for dep in dependencies],
                'estimated_time': '5-10 minutes'
            })
        
        # Phase 2: File modifications
        if file_modifications:
            plan['phases'].append({
                'phase': 2,
                'name': 'Modify Files',
                'description': 'Create and modify required files',
                'actions': [f"{fm.action.title()} {fm.file_path}" for fm in file_modifications],
                'estimated_time': '15-30 minutes'
            })
        
        # Phase 3: Commands
        if commands:
            plan['phases'].append({
                'phase': 3,
                'name': 'Execute Commands',
                'description': 'Run necessary commands',
                'actions': [cmd['command'] for cmd in commands],
                'estimated_time': '5-15 minutes'
            })
        
        # Phase 4: Validation
        plan['phases'].append({
            'phase': len(plan['phases']) + 1,
            'name': 'Validation',
            'description': 'Test and validate the implementation',
            'actions': ['Run tests', 'Verify functionality', 'Check for errors'],
            'estimated_time': '10-15 minutes'
        })
        
        return plan
    
    def _calculate_confidence_score(self, response: str, content: List[ExtractedContent]) -> float:
        """Calculate confidence score based on response quality"""
        score = 0.0
        
        # Length and detail factor
        if len(response) > 500:
            score += 0.2
        if len(response) > 1500:
            score += 0.1
        
        # Content richness factor
        code_count = sum(1 for c in content if c.content_type == ContentType.CODE)
        if code_count > 0:
            score += 0.3
        if code_count > 2:
            score += 0.1
        
        # Specific language indicators
        if any(lang in response.lower() for lang in ['python', 'javascript', 'typescript']):
            score += 0.1
        
        # Command and file indicators
        if any(cmd in response.lower() for cmd in ['install', 'create', 'modify', 'run']):
            score += 0.1
        
        # Structure indicators
        if re.search(r'\d+\.\s+', response):  # Numbered steps
            score += 0.1
        
        if '```' in response:  # Code blocks
            score += 0.1
        
        return min(1.0, score)
    
    def _identify_warnings(self, response: str, content: List[ExtractedContent]) -> List[str]:
        """Identify potential warnings or issues"""
        warnings = []
        
        # Check for incomplete code blocks
        if response.count('```') % 2 != 0:
            warnings.append("Incomplete code block detected")
        
        # Check for vague instructions
        vague_indicators = ['maybe', 'might', 'could', 'possibly', 'perhaps']
        if any(indicator in response.lower() for indicator in vague_indicators):
            warnings.append("Response contains uncertain language")
        
        # Check for missing error handling
        if 'try' not in response.lower() and 'error' not in response.lower():
            warnings.append("No error handling mentioned")
        
        return warnings
    
    def _suggest_next_actions(self, plan: Dict[str, Any], context: Optional[Dict[str, Any]]) -> List[str]:
        """Suggest logical next actions"""
        actions = []
        
        if plan.get('phases'):
            first_phase = plan['phases'][0]
            actions.append(f"Start with: {first_phase['name']}")
        
        actions.append("Review the implementation plan")
        actions.append("Prepare the development environment")
        
        if context and context.get('has_tests', False):
            actions.append("Run existing tests before making changes")
        
        return actions
    
    def _find_associated_code(self, response: str, file_path: str) -> Optional[str]:
        """Find code content associated with a specific file"""
        # Look for code blocks near file mentions
        file_mentions = [m.start() for m in re.finditer(re.escape(file_path), response)]
        
        for mention_pos in file_mentions:
            # Search forward and backward for code blocks
            before_text = response[max(0, mention_pos - 500):mention_pos]
            after_text = response[mention_pos:mention_pos + 1000]
            
            # Look for code blocks
            code_match = re.search(r'```(?:\w+)?\n(.*?)```', after_text, re.DOTALL)
            if not code_match:
                code_match = re.search(r'```(?:\w+)?\n(.*?)```', before_text, re.DOTALL)
            
            if code_match:
                return code_match.group(1).strip()
        
        return None
    
    def _classify_command(self, command: str) -> str:
        """Classify the type of command"""
        command_lower = command.lower()
        
        if any(pkg in command_lower for pkg in ['npm', 'yarn', 'pip']):
            return 'package_management'
        elif any(git in command_lower for git in ['git']):
            return 'version_control'
        elif any(run in command_lower for run in ['python', 'node', 'run']):
            return 'execution'
        elif any(test in command_lower for test in ['test', 'pytest', 'jest']):
            return 'testing'
        else:
            return 'general'
    
    def _get_command_context(self, response: str, position: int) -> str:
        """Get contextual description for a command"""
        # Look for explanation text around the command
        context_start = max(0, position - 100)
        context_end = min(len(response), position + 100)
        context = response[context_start:context_end]
        
        # Extract sentences containing the command
        sentences = re.split(r'[.!?]', context)
        relevant_sentence = max(sentences, key=len, default="")
        
        return relevant_sentence.strip()
    
    def _infer_working_directory(self, command: str) -> Optional[str]:
        """Infer the working directory for a command"""
        if 'cd ' in command:
            match = re.search(r'cd\s+([^\s&;|]+)', command)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_commands_from_text(self, text: str) -> List[str]:
        """Extract commands from a specific text block"""
        commands = []
        for pattern in self.command_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                command = match.group(1).strip() if match.groups() else match.group(0).strip()
                command = command.replace('$', '').strip()
                if command:
                    commands.append(command)
        return commands
    
    def _extract_file_references_from_text(self, text: str) -> List[str]:
        """Extract file references from a specific text block"""
        files = []
        for pattern in self.file_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                file_path = match.group(1).strip()
                if file_path:
                    files.append(file_path)
        return files
    
    def _extract_code_blocks_from_text(self, text: str) -> List[str]:
        """Extract code blocks from a specific text block"""
        code_blocks = []
        for patterns in self.code_patterns.values():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.DOTALL)
                for match in matches:
                    code_content = match.group(1).strip()
                    if code_content:
                        code_blocks.append(code_content)
        return code_blocks
    
    def _estimate_step_time(self, step_content: str) -> str:
        """Estimate time required for a step"""
        # Simple heuristic based on content complexity
        if len(step_content) < 100:
            return "5-10 minutes"
        elif len(step_content) < 300:
            return "10-20 minutes"
        else:
            return "20-30 minutes"
    
    def _assess_step_complexity(self, step_content: str) -> str:
        """Assess the complexity of a step"""
        complexity_indicators = {
            'simple': ['create', 'add', 'install', 'copy'],
            'medium': ['modify', 'update', 'configure', 'implement'],
            'complex': ['refactor', 'migrate', 'optimize', 'debug', 'integrate']
        }
        
        content_lower = step_content.lower()
        
        for complexity, indicators in complexity_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                return complexity
        
        return 'medium'  # default
    
    def _format_markdown_implementation(self, processed: ProcessedResponse) -> str:
        """Format processed response as markdown implementation guide"""
        lines = [
            f"# Implementation Guide",
            f"*Response ID: {processed.response_id}*",
            f"*Confidence Score: {processed.confidence_score:.1%}*",
            "",
        ]
        
        if processed.warnings:
            lines.extend([
                "## ⚠️ Warnings",
                "",
                *[f"- {warning}" for warning in processed.warnings],
                ""
            ])
        
        if processed.dependencies_to_install:
            lines.extend([
                "## 📦 Dependencies",
                "",
                "Install the following dependencies first:",
                "",
                *[f"```bash\n{dep}\n```" for dep in processed.dependencies_to_install],
                ""
            ])
        
        if processed.file_modifications:
            lines.extend([
                "## 📁 File Modifications",
                ""
            ])
            
            for fm in processed.file_modifications:
                lines.extend([
                    f"### {fm.action.title()}: `{fm.file_path}`",
                    f"{fm.description}",
                    ""
                ])
                
                if fm.content:
                    lines.extend([
                        "```",
                        fm.content,
                        "```",
                        ""
                    ])
        
        if processed.commands_to_run:
            lines.extend([
                "## 🔧 Commands to Run",
                ""
            ])
            
            for cmd in processed.commands_to_run:
                lines.extend([
                    f"```bash\n{cmd['command']}\n```",
                    f"*{cmd.get('description', 'Execute this command')}*",
                    ""
                ])
        
        if processed.validation_steps:
            lines.extend([
                "## ✅ Validation Steps",
                "",
                *[f"- {step}" for step in processed.validation_steps],
                ""
            ])
        
        if processed.next_actions:
            lines.extend([
                "## 🎯 Next Actions",
                "",
                *[f"- {action}" for action in processed.next_actions],
                ""
            ])
        
        return "\n".join(lines)
    
    def _format_text_implementation(self, processed: ProcessedResponse) -> str:
        """Format processed response as plain text implementation guide"""
        lines = [
            f"IMPLEMENTATION GUIDE (ID: {processed.response_id})",
            f"Confidence: {processed.confidence_score:.1%}",
            "=" * 50,
            ""
        ]
        
        if processed.dependencies_to_install:
            lines.extend([
                "DEPENDENCIES:",
                *[f"  - {dep}" for dep in processed.dependencies_to_install],
                ""
            ])
        
        if processed.file_modifications:
            lines.extend(["FILE MODIFICATIONS:"])
            for fm in processed.file_modifications:
                lines.extend([
                    f"  {fm.action.upper()}: {fm.file_path}",
                    f"    {fm.description}",
                    ""
                ])
        
        if processed.commands_to_run:
            lines.extend([
                "COMMANDS:",
                *[f"  $ {cmd['command']}" for cmd in processed.commands_to_run],
                ""
            ])
        
        if processed.validation_steps:
            lines.extend([
                "VALIDATION:",
                *[f"  - {step}" for step in processed.validation_steps],
                ""
            ])
        
        return "\n".join(lines)
