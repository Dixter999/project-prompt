"""
Base Strategy Processor

Contains base classes and shared data structures for strategy processors.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import re
import logging
from pathlib import Path

from .adaptive_decision_engine import ExecutionDecision, ExecutionStrategy, AgentConfigurationOverride
from .intelligent_scoring_engine import DetailedScore
from .agent_specializations import AgentType, AgentConfiguration


class ExecutionStatus(Enum):
    """Status of multi-agent execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_COMPLETED = "partially_completed"
    TIMEOUT = "timeout"


class SynchronizationStatus(Enum):
    """Synchronization status for parallel execution."""
    WAITING = "waiting"
    SYNCHRONIZED = "synchronized"
    DIVERGED = "diverged"
    CONFLICT = "conflict"


class ResponseQuality(Enum):
    """Quality assessment of agent responses."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    INVALID = "invalid"


@dataclass
class ExecutionContext:
    """Context for multi-agent execution."""
    user_query: str
    execution_metadata: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    shared_state: Dict[str, Any] = field(default_factory=dict)
    agent_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessedResponse:
    """Processed response from an agent."""
    agent_id: str
    agent_type: AgentType
    raw_response: str
    processed_content: str
    extracted_code: List[Dict[str, Any]]
    instructions: List[str]
    metadata: Dict[str, Any]
    quality_score: float
    confidence_score: float
    execution_time: float
    dependencies_satisfied: bool
    validation_errors: List[str] = field(default_factory=list)


@dataclass
class ExecutionCheckpoint:
    """Checkpoint for execution recovery."""
    execution_id: str
    timestamp: datetime
    decision: ExecutionDecision
    context: ExecutionContext
    responses: List[ProcessedResponse]
    status: ExecutionStatus
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionMetrics:
    """Metrics for execution performance."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_agents: int = 0
    successful_responses: int = 0
    failed_responses: int = 0
    average_response_time: float = 0.0
    quality_scores: List[float] = field(default_factory=list)
    synchronization_events: int = 0
    conflict_resolutions: int = 0


class BaseStrategyProcessor:
    """Base class for strategy processors."""
    
    def __init__(self, context_manager, response_processor):
        self.context_manager = context_manager
        self.response_processor = response_processor
        self.logger = logging.getLogger(__name__)
    
    async def process(self, decision: ExecutionDecision, 
                     context: ExecutionContext) -> Tuple[List[ProcessedResponse], ExecutionStatus]:
        """Process execution decision with given context."""
        raise NotImplementedError("Subclasses must implement process method")
    
    async def validate_prerequisites(self, decision: ExecutionDecision, 
                                   context: ExecutionContext) -> bool:
        """Validate prerequisites for execution."""
        return True
    
    async def cleanup(self, execution_id: str):
        """Cleanup after execution."""
        pass


class ContextManager:
    """Manages execution context and conversation history."""
    
    def __init__(self):
        self.contexts: Dict[str, ExecutionContext] = {}
        self.logger = logging.getLogger(__name__)
    
    def create_context(self, user_query: str, 
                      metadata: Optional[Dict[str, Any]] = None) -> ExecutionContext:
        """Create a new execution context."""
        return ExecutionContext(
            user_query=user_query,
            execution_metadata=metadata or {}
        )
    
    def update_context(self, context: ExecutionContext, 
                      agent_id: str, response: ProcessedResponse):
        """Update context with agent response."""
        # Add to conversation history
        context.conversation_history.append({
            'agent_id': agent_id,
            'agent_type': response.agent_type.value,
            'timestamp': datetime.now().isoformat(),
            'content': response.processed_content,
            'metadata': response.metadata
        })
        
        # Update agent state
        context.agent_states[agent_id] = {
            'last_response': response.processed_content,
            'confidence': response.confidence_score,
            'quality': response.quality_score,
            'timestamp': datetime.now().isoformat()
        }
        
        # Update shared state based on response
        if response.extracted_code:
            if 'code_artifacts' not in context.shared_state:
                context.shared_state['code_artifacts'] = []
            context.shared_state['code_artifacts'].extend(response.extracted_code)
        
        if response.instructions:
            if 'instructions' not in context.shared_state:
                context.shared_state['instructions'] = []
            context.shared_state['instructions'].extend(response.instructions)
    
    def get_relevant_history(self, context: ExecutionContext, 
                           agent_type: AgentType, max_entries: int = 5) -> List[Dict[str, Any]]:
        """Get relevant conversation history for an agent."""
        # Filter history for relevant entries
        relevant_entries = []
        for entry in context.conversation_history[-max_entries:]:
            # Include entries from the same agent type or dependencies
            if (entry['agent_type'] == agent_type.value or 
                self._is_dependency_relevant(entry, agent_type)):
                relevant_entries.append(entry)
        
        return relevant_entries
    
    def _is_dependency_relevant(self, entry: Dict[str, Any], 
                              agent_type: AgentType) -> bool:
        """Check if a history entry is relevant based on dependencies."""
        # Simple relevance check - can be enhanced with more sophisticated logic
        relevant_types = {
            AgentType.ARCHITECT: [AgentType.SENIOR_DEVELOPER],
            AgentType.SENIOR_DEVELOPER: [AgentType.ARCHITECT, AgentType.CODE_REVIEWER],
            AgentType.CODE_REVIEWER: [AgentType.SENIOR_DEVELOPER],
            AgentType.DOCUMENTATION_SPECIALIST: [AgentType.ARCHITECT, AgentType.SENIOR_DEVELOPER],
            AgentType.TESTING_SPECIALIST: [AgentType.SENIOR_DEVELOPER]
        }
        
        entry_type = AgentType(entry['agent_type'])
        return entry_type in relevant_types.get(agent_type, [])


class ResponseProcessor:
    """Processes and validates agent responses."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Patterns for extracting different types of content
        self.code_pattern = re.compile(r'```(\w+)?\n(.*?)\n```', re.DOTALL)
        self.instruction_pattern = re.compile(r'(?:^|\n)(?:\d+\.|[-*])\s+(.+?)(?=\n\d+\.|$|\n[-*])', re.MULTILINE)
        self.file_pattern = re.compile(r'(?:file|path):\s*([^\n]+)', re.IGNORECASE)
    
    async def process_response(self, agent_id: str, agent_type: AgentType,
                             raw_response: str, context: ExecutionContext) -> ProcessedResponse:
        """Process a raw agent response into structured format."""
        start_time = datetime.now()
        
        # Extract structured content
        extracted_code = self._extract_code_blocks(raw_response)
        instructions = self._extract_instructions(raw_response)
        
        # Clean and process content
        processed_content = self._clean_response_content(raw_response)
        
        # Calculate quality and confidence scores
        quality_score = self._calculate_quality_score(raw_response, extracted_code, instructions)
        confidence_score = self._calculate_confidence_score(raw_response, agent_type)
        
        # Validate response
        validation_errors = self._validate_response(raw_response, agent_type)
        
        # Check dependencies
        dependencies_satisfied = self._check_dependencies(context, agent_type)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return ProcessedResponse(
            agent_id=agent_id,
            agent_type=agent_type,
            raw_response=raw_response,
            processed_content=processed_content,
            extracted_code=extracted_code,
            instructions=instructions,
            metadata={
                'processing_time': execution_time,
                'word_count': len(raw_response.split()),
                'code_blocks': len(extracted_code),
                'instruction_count': len(instructions)
            },
            quality_score=quality_score,
            confidence_score=confidence_score,
            execution_time=execution_time,
            dependencies_satisfied=dependencies_satisfied,
            validation_errors=validation_errors
        )
    
    def _extract_code_blocks(self, response: str) -> List[Dict[str, Any]]:
        """Extract code blocks from response."""
        code_blocks = []
        matches = self.code_pattern.findall(response)
        
        for i, (language, code) in enumerate(matches):
            code_blocks.append({
                'id': f'code_block_{i}',
                'language': language or 'text',
                'code': code.strip(),
                'line_count': len(code.strip().split('\n'))
            })
        
        return code_blocks
    
    def _extract_instructions(self, response: str) -> List[str]:
        """Extract instructions from response."""
        instructions = []
        
        # Look for numbered or bulleted lists
        matches = self.instruction_pattern.findall(response)
        instructions.extend([match.strip() for match in matches])
        
        # Look for imperative sentences
        sentences = re.split(r'[.!]\s+', response)
        for sentence in sentences:
            if self._is_instruction(sentence.strip()):
                instructions.append(sentence.strip())
        
        return list(set(instructions))  # Remove duplicates
    
    def _is_instruction(self, sentence: str) -> bool:
        """Check if a sentence is likely an instruction."""
        instruction_verbs = [
            'create', 'make', 'build', 'implement', 'add', 'remove',
            'update', 'modify', 'change', 'install', 'configure',
            'run', 'execute', 'test', 'validate', 'check'
        ]
        
        words = sentence.lower().split()
        return len(words) > 3 and any(verb in words[:3] for verb in instruction_verbs)
    
    def _clean_response_content(self, response: str) -> str:
        """Clean and format response content."""
        # Remove excessive whitespace
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', response)
        
        # Remove code blocks for summary
        cleaned = re.sub(r'```[^`]*```', '[CODE BLOCK]', cleaned, flags=re.DOTALL)
        
        return cleaned.strip()
    
    def _calculate_quality_score(self, response: str, code_blocks: List[Dict], 
                               instructions: List[str]) -> float:
        """Calculate quality score for response."""
        score = 0.0
        
        # Length and structure
        word_count = len(response.split())
        if 50 <= word_count <= 1000:
            score += 0.2
        elif word_count > 1000:
            score += 0.1
        
        # Code presence and quality
        if code_blocks:
            score += 0.3
            avg_code_length = sum(block['line_count'] for block in code_blocks) / len(code_blocks)
            if avg_code_length > 10:
                score += 0.1
        
        # Instructions clarity
        if instructions:
            score += 0.2
            if len(instructions) >= 3:
                score += 0.1
        
        # Technical keywords
        technical_keywords = [
            'function', 'class', 'method', 'variable', 'parameter',
            'implementation', 'algorithm', 'architecture', 'design'
        ]
        keyword_count = sum(1 for keyword in technical_keywords if keyword in response.lower())
        score += min(0.1, keyword_count * 0.02)
        
        return min(1.0, score)
    
    def _calculate_confidence_score(self, response: str, agent_type: AgentType) -> float:
        """Calculate confidence score based on response and agent type."""
        score = 0.5  # Base score
        
        # Confidence indicators
        confident_phrases = ['definitely', 'certainly', 'clearly', 'obviously']
        uncertain_phrases = ['maybe', 'perhaps', 'might', 'possibly', 'unsure']
        
        confident_count = sum(1 for phrase in confident_phrases if phrase in response.lower())
        uncertain_count = sum(1 for phrase in uncertain_phrases if phrase in response.lower())
        
        score += confident_count * 0.1
        score -= uncertain_count * 0.1
        
        # Agent type specific adjustments
        if agent_type == AgentType.ARCHITECT and 'architecture' in response.lower():
            score += 0.1
        elif agent_type == AgentType.SENIOR_DEVELOPER and any(lang in response.lower() 
                                                            for lang in ['python', 'javascript', 'java']):
            score += 0.1
        elif agent_type == AgentType.CODE_REVIEWER and 'review' in response.lower():
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _validate_response(self, response: str, agent_type: AgentType) -> List[str]:
        """Validate response for common issues."""
        errors = []
        
        # Basic validation
        if len(response.strip()) < 20:
            errors.append("Response too short")
        
        if len(response) > 10000:
            errors.append("Response too long")
        
        # Agent-specific validation
        if agent_type == AgentType.SENIOR_DEVELOPER:
            if not self.code_pattern.search(response):
                errors.append("No code blocks found in developer response")
        
        elif agent_type == AgentType.ARCHITECT:
            if not any(keyword in response.lower() for keyword in ['design', 'architecture', 'structure']):
                errors.append("Missing architectural concepts")
        
        elif agent_type == AgentType.CODE_REVIEWER:
            if not any(keyword in response.lower() for keyword in ['review', 'analysis', 'feedback']):
                errors.append("Missing review elements")
        
        return errors
    
    def _check_dependencies(self, context: ExecutionContext, agent_type: AgentType) -> bool:
        """Check if agent dependencies are satisfied."""
        # Define dependency relationships
        dependencies = {
            AgentType.SENIOR_DEVELOPER: [AgentType.ARCHITECT],
            AgentType.CODE_REVIEWER: [AgentType.SENIOR_DEVELOPER],
            AgentType.TESTING_SPECIALIST: [AgentType.SENIOR_DEVELOPER],
            AgentType.DOCUMENTATION_SPECIALIST: [AgentType.ARCHITECT, AgentType.SENIOR_DEVELOPER]
        }
        
        required_deps = dependencies.get(agent_type, [])
        if not required_deps:
            return True
        
        # Check if required agents have responded
        responded_types = set()
        for entry in context.conversation_history:
            responded_types.add(AgentType(entry['agent_type']))
        
        return all(dep in responded_types for dep in required_deps)
