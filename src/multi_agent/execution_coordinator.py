"""
Multi-Agent Execution Coordinator

Orchestrates the execution of multi-agent strategies with comprehensive
context management, response processing, and state handling.
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

from .adaptive_decision_engine import (
    ExecutionDecision, ExecutionStrategy, AgentConfigurationOverride,
    AdaptiveDecisionEngine
)
from .intelligent_scoring_engine import DetailedScore
from .agent_specializations import AgentType, AgentConfiguration
from .system_prompt_generator import SystemPromptGenerator
from .api_health_monitor import ApiHealthMonitor
from .fault_detector import FaultDetector, FailureEvent, FailureType, FailureSeverity
from .fallback_cascade import FallbackCascade, FallbackOption, FallbackAttempt
from .intelligent_recovery import IntelligentRecoverySystem, RecoverySession


class ExecutionStatus(Enum):
    """Status of execution coordination."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIAL_SUCCESS = "partial_success"


class SynchronizationStatus(Enum):
    """Status of agent synchronization."""
    SYNCHRONIZED = "synchronized"
    DIVERGENT = "divergent"
    CONFLICTED = "conflicted"
    PENDING_RESOLUTION = "pending_resolution"


class ResponseQuality(Enum):
    """Quality assessment of responses."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    INVALID = "invalid"


@dataclass
class ExecutionContext:
    """Maintains conversational and execution context."""
    user_query: str
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    execution_metadata: Dict[str, Any] = field(default_factory=dict)
    shared_variables: Dict[str, Any] = field(default_factory=dict)
    agent_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    iteration_count: int = 0
    max_iterations: int = 10
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ProcessedResponse:
    """Processed response from an agent."""
    agent_id: str
    agent_type: AgentType
    raw_response: str
    extracted_code: List[Dict[str, str]] = field(default_factory=list)
    instructions: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    quality_assessment: ResponseQuality = ResponseQuality.ACCEPTABLE
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ExecutionCheckpoint:
    """Checkpoint for state recovery."""
    execution_id: str
    strategy: ExecutionStrategy
    context: ExecutionContext
    agent_responses: List[ProcessedResponse]
    status: ExecutionStatus
    timestamp: datetime
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionMetrics:
    """Metrics for execution performance."""
    total_execution_time: float = 0.0
    agent_execution_times: Dict[str, float] = field(default_factory=dict)
    response_quality_scores: List[float] = field(default_factory=list)
    error_count: int = 0
    retry_count: int = 0
    context_switches: int = 0
    memory_usage: float = 0.0


class ContextManager:
    """Manages conversational and execution context preservation."""
    
    def __init__(self, max_history_length: int = 50):
        self.max_history_length = max_history_length
        self.logger = logging.getLogger(__name__)
    
    def preserve_context(self, context: ExecutionContext, 
                        new_interaction: Dict[str, Any]) -> ExecutionContext:
        """Preserve conversational context across interactions."""
        # Add new interaction to history
        context.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'interaction': new_interaction
        })
        
        # Trim history if it exceeds max length
        if len(context.conversation_history) > self.max_history_length:
            context.conversation_history = context.conversation_history[-self.max_history_length:]
        
        # Update iteration count
        context.iteration_count += 1
        
        return context
    
    def extract_relevant_context(self, context: ExecutionContext, 
                                agent_type: AgentType) -> Dict[str, Any]:
        """Extract context relevant to specific agent type."""
        relevant_context = {
            'user_query': context.user_query,
            'shared_variables': context.shared_variables,
            'iteration_count': context.iteration_count
        }
        
        # Filter conversation history for relevance
        relevant_history = []
        for entry in context.conversation_history[-10:]:  # Last 10 interactions
            if self._is_relevant_to_agent(entry, agent_type):
                relevant_history.append(entry)
        
        relevant_context['conversation_history'] = relevant_history
        
        # Include agent-specific state
        agent_key = agent_type.value
        if agent_key in context.agent_states:
            relevant_context['agent_state'] = context.agent_states[agent_key]
        
        return relevant_context
    
    def _is_relevant_to_agent(self, entry: Dict[str, Any], 
                             agent_type: AgentType) -> bool:
        """Determine if a conversation entry is relevant to an agent type."""
        interaction = entry.get('interaction', {})
        
        # Check if the entry involves the specific agent type
        if interaction.get('agent_type') == agent_type.value:
            return True
        
        # Check for keywords relevant to the agent type
        content = str(interaction.get('content', '')).lower()
        agent_keywords = {
            AgentType.PLANNER: ['plan', 'strategy', 'approach', 'steps'],
            AgentType.CODER: ['code', 'implement', 'function', 'class'],
            AgentType.REVIEWER: ['review', 'check', 'validate', 'quality'],
            AgentType.OPTIMIZER: ['optimize', 'improve', 'performance', 'efficiency'],
            AgentType.DEBUGGER: ['debug', 'error', 'fix', 'issue'],
            AgentType.TESTER: ['test', 'verify', 'validate', 'coverage'],
            AgentType.DOCUMENTER: ['document', 'explain', 'describe', 'comment']
        }
        
        keywords = agent_keywords.get(agent_type, [])
        return any(keyword in content for keyword in keywords)


class ResponseProcessor:
    """Processes and validates agent responses."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.code_patterns = [
            re.compile(r'```(?:python|py)?\n(.*?)\n```', re.DOTALL),
            re.compile(r'<code[^>]*>(.*?)</code>', re.DOTALL),
            re.compile(r'def\s+\w+\([^)]*\):[^}]+', re.DOTALL),
            re.compile(r'class\s+\w+[^:]*:[^}]+', re.DOTALL)
        ]
    
    def process_response(self, agent_id: str, agent_type: AgentType, 
                        response: str) -> ProcessedResponse:
        """Process a raw agent response into structured format."""
        processed = ProcessedResponse(
            agent_id=agent_id,
            agent_type=agent_type,
            raw_response=response
        )
        
        # Extract code blocks
        processed.extracted_code = self._extract_code_blocks(response)
        
        # Extract instructions and action items
        processed.instructions = self._extract_instructions(response)
        
        # Assess response quality
        processed.quality_score, processed.quality_assessment = self._assess_quality(
            response, agent_type
        )
        
        # Extract metadata
        processed.metadata = self._extract_metadata(response, agent_type)
        
        return processed
    
    def _extract_code_blocks(self, response: str) -> List[Dict[str, str]]:
        """Extract code blocks from response."""
        code_blocks = []
        
        for pattern in self.code_patterns:
            matches = pattern.findall(response)
            for match in matches:
                code_blocks.append({
                    'language': self._detect_language(match),
                    'code': match.strip(),
                    'type': self._classify_code_type(match)
                })
        
        return code_blocks
    
    def _extract_instructions(self, response: str) -> List[str]:
        """Extract action items and instructions from response."""
        instructions = []
        
        # Look for numbered lists
        numbered_pattern = re.compile(r'^\d+\.\s+(.+)$', re.MULTILINE)
        instructions.extend(numbered_pattern.findall(response))
        
        # Look for bullet points
        bullet_pattern = re.compile(r'^\s*[-*]\s+(.+)$', re.MULTILINE)
        instructions.extend(bullet_pattern.findall(response))
        
        # Look for imperative statements
        imperative_pattern = re.compile(r'(Create|Add|Implement|Update|Modify|Remove|Fix|Test)\s+[^.]+', re.IGNORECASE)
        instructions.extend(imperative_pattern.findall(response))
        
        return list(set(instructions))  # Remove duplicates
    
    def _assess_quality(self, response: str, agent_type: AgentType) -> Tuple[float, ResponseQuality]:
        """Assess the quality of a response."""
        score = 0.0
        
        # Length check
        if len(response) < 50:
            score -= 0.2
        elif len(response) > 200:
            score += 0.1
        
        # Completeness check
        if any(keyword in response.lower() for keyword in ['complete', 'done', 'finished']):
            score += 0.2
        
        # Code quality for coding agents
        if agent_type in [AgentType.CODER, AgentType.OPTIMIZER]:
            code_blocks = self._extract_code_blocks(response)
            if code_blocks:
                score += 0.3
                # Check for comments and documentation
                for block in code_blocks:
                    if '#' in block['code'] or '"""' in block['code']:
                        score += 0.1
        
        # Error indicators
        error_keywords = ['error', 'failed', 'cannot', 'unable', 'impossible']
        if any(keyword in response.lower() for keyword in error_keywords):
            score -= 0.3
        
        # Normalize score
        score = max(0.0, min(1.0, score + 0.5))
        
        # Determine quality assessment
        if score >= 0.8:
            quality = ResponseQuality.EXCELLENT
        elif score >= 0.6:
            quality = ResponseQuality.GOOD
        elif score >= 0.4:
            quality = ResponseQuality.ACCEPTABLE
        elif score >= 0.2:
            quality = ResponseQuality.POOR
        else:
            quality = ResponseQuality.INVALID
        
        return score, quality
    
    def _detect_language(self, code: str) -> str:
        """Detect programming language of code block."""
        if 'def ' in code or 'import ' in code or 'class ' in code:
            return 'python'
        elif 'function' in code or 'const ' in code or 'let ' in code:
            return 'javascript'
        elif '#include' in code or 'int main' in code:
            return 'c++'
        else:
            return 'unknown'
    
    def _classify_code_type(self, code: str) -> str:
        """Classify the type of code block."""
        if 'class ' in code:
            return 'class_definition'
        elif 'def ' in code or 'function' in code:
            return 'function_definition'
        elif 'test' in code.lower() or 'assert' in code:
            return 'test_code'
        elif 'import ' in code or '#include' in code:
            return 'imports'
        else:
            return 'general'
    
    def _extract_metadata(self, response: str, agent_type: AgentType) -> Dict[str, Any]:
        """Extract metadata from response."""
        metadata = {
            'word_count': len(response.split()),
            'line_count': len(response.split('\n')),
            'has_code': bool(self._extract_code_blocks(response)),
            'agent_type': agent_type.value
        }
        
        # Extract confidence indicators
        confidence_words = ['confident', 'certain', 'sure', 'likely', 'probably', 'maybe', 'uncertain']
        for word in confidence_words:
            if word in response.lower():
                metadata['confidence_indicator'] = word
                break
        
        return metadata


class BaseStrategyProcessor:
    """Base class for strategy processors."""
    
    def __init__(self, context_manager: ContextManager, 
                 response_processor: ResponseProcessor):
        self.context_manager = context_manager
        self.response_processor = response_processor
        self.logger = logging.getLogger(__name__)
    
    async def process(self, decision: ExecutionDecision, 
                     context: ExecutionContext) -> List[ProcessedResponse]:
        """Process execution decision. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement process method")
    
    def handle_error(self, error: Exception, context: ExecutionContext) -> Optional[ExecutionContext]:
        """Handle errors during execution."""
        self.logger.error(f"Error in strategy processor: {error}")
        context.execution_metadata['last_error'] = str(error)
        context.execution_metadata['error_timestamp'] = datetime.now().isoformat()
        return context


class ExecutionCoordinator:
    """Main coordinator for multi-agent execution strategies with fault tolerance."""
    
    def __init__(self, api_health_monitor: Optional[ApiHealthMonitor] = None):
        self.context_manager = ContextManager()
        self.response_processor = ResponseProcessor()
        self.api_health_monitor = api_health_monitor or ApiHealthMonitor()
        self.decision_engine = AdaptiveDecisionEngine()
        self.checkpoints: Dict[str, ExecutionCheckpoint] = {}
        self.metrics: Dict[str, ExecutionMetrics] = {}
        self.logger = logging.getLogger(__name__)
        
        # FASE 5: Fault tolerance components
        self.fault_detector = FaultDetector()
        self.fallback_cascade = FallbackCascade()
        self.recovery_system = IntelligentRecoverySystem(
            self.fault_detector, 
            self.fallback_cascade
        )
        
        # Strategy processors will be registered here
        self.strategy_processors: Dict[ExecutionStrategy, BaseStrategyProcessor] = {}
        
        # Initialize strategy processors
        self.initialize_processors()
    
    def register_processor(self, strategy: ExecutionStrategy, 
                          processor: BaseStrategyProcessor):
        """Register a strategy processor."""
        self.strategy_processors[strategy] = processor
        self.logger.info(f"Registered processor for strategy: {strategy.value}")
    
    async def execute(self, decision: ExecutionDecision, 
                     user_query: str) -> Tuple[List[ProcessedResponse], ExecutionStatus]:
        """Execute a multi-agent decision with comprehensive coordination and fault tolerance."""
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize context
        context = ExecutionContext(
            user_query=user_query,
            execution_metadata={'execution_id': execution_id}
        )
        
        # Initialize metrics
        self.metrics[execution_id] = ExecutionMetrics()
        start_time = datetime.now()
        
        try:
            # Create checkpoint
            await self._create_checkpoint(execution_id, decision, context, [])
            
            # Get appropriate processor
            processor = self._get_processor(decision.strategy)
            if not processor:
                raise ValueError(f"No processor registered for strategy: {decision.strategy}")
            
            # Execute strategy with fault tolerance
            responses, status = await self._execute_with_fault_tolerance(
                processor, decision, context, execution_id
            )
            
            # Update metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            self.metrics[execution_id].total_execution_time = execution_time
            
            # Final checkpoint
            await self._create_checkpoint(execution_id, decision, context, responses, status)
            
            self.logger.info(f"Execution {execution_id} completed with status: {status.value}")
            return responses, status
            
        except Exception as e:
            self.logger.error(f"Execution {execution_id} failed: {e}")
            self.metrics[execution_id].error_count += 1
            
            # Attempt recovery for critical system failures
            try:
                recovered_responses = await self._handle_critical_failure(
                    e, decision, context, execution_id
                )
                if recovered_responses:
                    return recovered_responses, ExecutionStatus.PARTIAL_SUCCESS
            except Exception as recovery_error:
                self.logger.error(f"Recovery also failed: {recovery_error}")
            
            return [], ExecutionStatus.FAILED
    
    def _get_processor(self, strategy: ExecutionStrategy) -> Optional[BaseStrategyProcessor]:
        """Get the appropriate processor for a strategy."""
        return self.strategy_processors.get(strategy)
    
    def _determine_execution_status(self, responses: List[ProcessedResponse]) -> ExecutionStatus:
        """Determine the overall execution status based on responses."""
        if not responses:
            return ExecutionStatus.FAILED
        
        quality_scores = [r.quality_score for r in responses]
        avg_quality = sum(quality_scores) / len(quality_scores)
        
        invalid_responses = sum(1 for r in responses 
                               if r.quality_assessment == ResponseQuality.INVALID)
        
        if invalid_responses > len(responses) / 2:
            return ExecutionStatus.FAILED
        elif invalid_responses > 0:
            return ExecutionStatus.PARTIAL_SUCCESS
        elif avg_quality >= 0.7:
            return ExecutionStatus.COMPLETED
        else:
            return ExecutionStatus.PARTIAL_SUCCESS
    
    async def _create_checkpoint(self, execution_id: str, decision: ExecutionDecision,
                               context: ExecutionContext, responses: List[ProcessedResponse],
                               status: ExecutionStatus = ExecutionStatus.IN_PROGRESS):
        """Create an execution checkpoint."""
        checkpoint = ExecutionCheckpoint(
            execution_id=execution_id,
            strategy=decision.strategy,
            context=context,
            agent_responses=responses,
            status=status,
            timestamp=datetime.now(),
            metrics=self.metrics.get(execution_id, ExecutionMetrics()).__dict__
        )
        
        self.checkpoints[execution_id] = checkpoint
    
    def get_checkpoint(self, execution_id: str) -> Optional[ExecutionCheckpoint]:
        """Retrieve an execution checkpoint."""
        return self.checkpoints.get(execution_id)
    
    def get_metrics(self, execution_id: str) -> Optional[ExecutionMetrics]:
        """Get execution metrics."""
        return self.metrics.get(execution_id)
    
    async def resolve_conflicts(self, responses: List[ProcessedResponse]) -> List[ProcessedResponse]:
        """Resolve conflicts between agent responses."""
        if len(responses) <= 1:
            return responses
        
        # Group responses by quality
        high_quality = [r for r in responses if r.quality_score >= 0.7]
        medium_quality = [r for r in responses if 0.4 <= r.quality_score < 0.7]
        
        # If we have high-quality responses, prefer those
        if high_quality:
            return high_quality
        
        # Otherwise, take the best medium-quality responses
        if medium_quality:
            return sorted(medium_quality, key=lambda r: r.quality_score, reverse=True)[:2]
        
        # Fall back to all responses
        return responses
    
    def integrate_responses(self, responses: List[ProcessedResponse]) -> Dict[str, Any]:
        """Integrate multiple agent responses into a cohesive result."""
        integrated_result = {
            'combined_code': [],
            'consolidated_instructions': [],
            'quality_summary': {},
            'agent_contributions': []
        }
        
        # Combine code blocks
        for response in responses:
            for code_block in response.extracted_code:
                code_block['source_agent'] = response.agent_id
                integrated_result['combined_code'].append(code_block)
        
        # Consolidate instructions
        all_instructions = []
        for response in responses:
            all_instructions.extend(response.instructions)
        
        # Remove duplicates while preserving order
        seen = set()
        for instruction in all_instructions:
            if instruction not in seen:
                integrated_result['consolidated_instructions'].append(instruction)
                seen.add(instruction)
        
        # Quality summary
        quality_scores = [r.quality_score for r in responses]
        integrated_result['quality_summary'] = {
            'average_quality': sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            'min_quality': min(quality_scores) if quality_scores else 0,
            'max_quality': max(quality_scores) if quality_scores else 0,
            'total_responses': len(responses)
        }
        
        # Agent contributions
        for response in responses:
            contribution = {
                'agent_id': response.agent_id,
                'agent_type': response.agent_type.value,
                'quality_score': response.quality_score,
                'code_blocks': len(response.extracted_code),
                'instructions': len(response.instructions)
            }
            integrated_result['agent_contributions'].append(contribution)
        
        return integrated_result

    def _initialize_default_processors(self):
        """Initialize and register default strategy processors."""
        try:
            # Import here to avoid circular imports
            from .sequential_processor import SequentialProcessor
            from .parallel_processor import ParallelProcessor
            
            # Register sequential processor
            sequential_processor = SequentialProcessor(
                self.context_manager, 
                self.response_processor
            )
            self.register_processor(ExecutionStrategy.SEQUENTIAL_MULTI, sequential_processor)
            
            # Register parallel processor  
            parallel_processor = ParallelProcessor(
                self.context_manager,
                self.response_processor
            )
            self.register_processor(ExecutionStrategy.PARALLEL_MULTI, parallel_processor)
            
            self.logger.info("Default strategy processors initialized successfully")
            
        except ImportError as e:
            self.logger.error(f"Failed to import strategy processors: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize strategy processors: {e}")
            raise

    def initialize_processors(self):
        """Public method to initialize strategy processors."""
        if not self.strategy_processors:
            self._initialize_default_processors()
        return self

    # FASE 5: Fault Tolerance Integration Methods
    
    async def _execute_with_fault_tolerance(self, processor: BaseStrategyProcessor, 
                                          decision: ExecutionDecision, 
                                          context: ExecutionContext,
                                          execution_id: str) -> Tuple[List[ProcessedResponse], ExecutionStatus]:
        """Execute strategy with comprehensive fault tolerance."""
        max_retry_attempts = 3
        retry_count = 0
        responses = []
        
        while retry_count < max_retry_attempts:
            try:
                # Execute the strategy
                responses = await processor.process(decision, context)
                
                # Check for failures in responses
                failure_detected = False
                for response in responses:
                    failure_event = await self.fault_detector.detect_failure(
                        response=response,
                        context=context,
                        agent_id=response.agent_id,
                        agent_type=response.agent_type
                    )
                    
                    if failure_event:
                        self.logger.warning(f"Failure detected in response: {failure_event.failure_type.value}")
                        
                        # Attempt recovery
                        recovery_result = await self._attempt_recovery(
                            failure_event, decision, context, execution_id
                        )
                        
                        if recovery_result:
                            # Replace failed response with recovered one
                            for i, resp in enumerate(responses):
                                if resp.agent_id == response.agent_id:
                                    responses[i] = recovery_result
                        else:
                            failure_detected = True
                            break
                
                if not failure_detected:
                    # Success - determine final status
                    status = self._determine_execution_status(responses)
                    return responses, status
                
                retry_count += 1
                if retry_count < max_retry_attempts:
                    self.logger.info(f"Retrying execution (attempt {retry_count + 1}/{max_retry_attempts})")
                    await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                
            except Exception as e:
                self.logger.error(f"Exception in fault-tolerant execution: {e}")
                
                # Detect failure from exception
                failure_event = await self.fault_detector.detect_failure(
                    error=e,
                    context=context,
                    agent_id=getattr(decision, 'primary_agent_type', AgentType.PLANNER).value
                )
                
                if failure_event:
                    recovery_result = await self._attempt_recovery(
                        failure_event, decision, context, execution_id
                    )
                    
                    if recovery_result:
                        return [recovery_result], ExecutionStatus.PARTIAL_SUCCESS
                
                retry_count += 1
                if retry_count < max_retry_attempts:
                    await asyncio.sleep(2 ** retry_count)
                else:
                    # Final attempt failed
                    return responses, ExecutionStatus.FAILED
        
        return responses, ExecutionStatus.FAILED
    
    async def _attempt_recovery(self, failure_event: FailureEvent, 
                              decision: ExecutionDecision, 
                              context: ExecutionContext,
                              execution_id: str) -> Optional[ProcessedResponse]:
        """Attempt to recover from a failure using the intelligent recovery system."""
        try:
            # Create a dummy executor callback for recovery
            async def dummy_executor(recovery_decision, recovery_context):
                # This would normally call back to the actual execution logic
                # For now, create a basic response
                return ProcessedResponse(
                    agent_id=f"recovery_{failure_event.agent_id}",
                    agent_type=failure_event.agent_type or AgentType.PLANNER,
                    raw_response="Recovery response generated by fallback",
                    quality_score=0.6,
                    quality_assessment=ResponseQuality.ACCEPTABLE
                )
            
            # Initiate recovery session
            recovery_session = await self.recovery_system.initiate_recovery(
                failure_event, context, decision, dummy_executor
            )
            
            if recovery_session and recovery_session.status.value == 'SUCCESSFUL':
                self.logger.info(f"Successfully recovered from {failure_event.failure_type.value}")
                return recovery_session.final_result
            
            return None
            
        except Exception as e:
            self.logger.error(f"Recovery attempt failed: {e}")
            return None
    
    async def _handle_critical_failure(self, error: Exception, 
                                     decision: ExecutionDecision, 
                                     context: ExecutionContext,
                                     execution_id: str) -> List[ProcessedResponse]:
        """Handle critical system failures with emergency recovery."""
        self.logger.critical(f"Critical failure in execution {execution_id}: {error}")
        
        try:
            # Create emergency failure event
            failure_event = FailureEvent(
                failure_id=f"critical_{execution_id}",
                failure_type=FailureType.UNKNOWN_ERROR,
                severity=FailureSeverity.CRITICAL,
                agent_id=execution_id,
                agent_type=None,
                timestamp=datetime.now(),
                error_message=f"Critical system failure: {str(error)}",
                is_recoverable=False
            )
            
            # Attempt emergency recovery
            emergency_response = await self._create_emergency_response(
                context, failure_event
            )
            
            if emergency_response:
                return [emergency_response]
            
            return []
            
        except Exception as recovery_error:
            self.logger.error(f"Emergency recovery failed: {recovery_error}")
            return []
    
    async def _create_emergency_response(self, context: ExecutionContext, 
                                       failure_event: FailureEvent) -> Optional[ProcessedResponse]:
        """Create an emergency response when all else fails."""
        try:
            emergency_message = (
                f"System encountered a critical failure during execution. "
                f"Failure type: {failure_event.failure_type.value}. "
                f"User query: {context.user_query[:100]}... "
                f"Please try a simpler request or contact support."
            )
            
            return ProcessedResponse(
                agent_id="emergency_system",
                agent_type=AgentType.PLANNER,
                raw_response=emergency_message,
                instructions=["Try a simpler request", "Contact support if issue persists"],
                quality_score=0.3,
                quality_assessment=ResponseQuality.POOR,
                metadata={'emergency_response': True, 'failure_id': failure_event.failure_id}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create emergency response: {e}")
            return None
    
    def get_fault_tolerance_status(self) -> Dict[str, Any]:
        """Get comprehensive fault tolerance system status."""
        return {
            'fault_detector': {
                'statistics': self.fault_detector.get_failure_statistics(),
                'active': True
            },
            'fallback_cascade': {
                'statistics': self.fallback_cascade.get_fallback_statistics(),
                'active': True
            },
            'recovery_system': {
                'active_sessions': len(self.recovery_system.active_sessions),
                'total_recoveries': len(self.recovery_system.recovery_history),
                'active': True
            }
        }
    
    async def reset_fault_tolerance_state(self, agent_id: Optional[str] = None):
        """Reset fault tolerance state for testing or recovery."""
        if agent_id:
            self.fault_detector.clear_agent_failures(agent_id)
            self.logger.info(f"Reset fault tolerance state for agent: {agent_id}")
        else:
            # Reset all fault tolerance components
            self.fault_detector = FaultDetector()
            self.logger.info("Reset all fault tolerance state")