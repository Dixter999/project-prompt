"""
Fallback Cascade System for Multi-Agent Execution

Implements intelligent fallback strategies with cascading agent alternatives,
parameter adjustments, and context preservation during transitions.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Callable, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
import logging
import copy

if TYPE_CHECKING:
    from .execution_coordinator import ExecutionContext, Any, ResponseQuality

from .adaptive_decision_engine import ExecutionDecision, ExecutionStrategy
from .agent_specializations import AgentType, AgentConfiguration
from .fault_detector import FailureEvent, FailureType, FailureSeverity


class FallbackStrategy(Enum):
    """Types of fallback strategies."""
    RETRY_SAME_AGENT = "retry_same_agent"
    SWITCH_AGENT_TYPE = "switch_agent_type"
    ADJUST_PARAMETERS = "adjust_parameters"
    SIMPLIFY_REQUEST = "simplify_request"
    ESCALATE_TO_MULTIPLE = "escalate_to_multiple"
    CHANGE_STRATEGY = "change_strategy"
    ABORT_EXECUTION = "abort_execution"


@dataclass
class FallbackOption:
    """Represents a fallback option with priority and configuration."""
    strategy: FallbackStrategy
    priority: int  # Lower number = higher priority
    agent_type: Optional[AgentType] = None
    execution_strategy: Optional[ExecutionStrategy] = None
    parameter_adjustments: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[Callable[[FailureEvent], bool]] = None
    max_attempts: int = 1
    delay_seconds: float = 0
    description: str = ""


@dataclass
class FallbackAttempt:
    """Records an attempted fallback."""
    attempt_id: str
    original_failure: FailureEvent
    fallback_option: FallbackOption
    timestamp: datetime
    success: bool = False
    result_response: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0


class FallbackCascade:
    """Manages cascading fallback strategies for failed agent executions."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.fallback_history: List[FallbackAttempt] = []
        self.agent_priorities: Dict[AgentType, List[AgentType]] = {}
        self.strategy_alternatives: Dict[ExecutionStrategy, List[ExecutionStrategy]] = {}
        self._initialize_default_cascades()
    
    def _initialize_default_cascades(self):
        """Initialize default fallback cascades for different scenarios."""
        
        # Agent type alternatives (ordered by priority)
        self.agent_priorities = {
            AgentType.PLANNER: [AgentType.ANALYST, AgentType.ARCHITECT],
            AgentType.CODER: [AgentType.CODE_IMPLEMENTER, AgentType.PROBLEM_SOLVER, AgentType.OPTIMIZER],
            AgentType.REVIEWER: [AgentType.QUALITY_ASSURANCE, AgentType.TESTER, AgentType.VALIDATOR],
            AgentType.OPTIMIZER: [AgentType.CODER, AgentType.PERFORMANCE_ENGINEER],
            AgentType.DEBUGGER: [AgentType.PROBLEM_SOLVER, AgentType.TESTER, AgentType.REVIEWER],
            AgentType.TESTER: [AgentType.QUALITY_ASSURANCE, AgentType.VALIDATOR, AgentType.REVIEWER],
            AgentType.DOCUMENTER: [AgentType.TECHNICAL_WRITER, AgentType.ANALYST]
        }
        
        # Strategy alternatives
        self.strategy_alternatives = {
            ExecutionStrategy.PARALLEL_MULTI: [ExecutionStrategy.SEQUENTIAL_MULTI, ExecutionStrategy.SINGLE_AGENT],
            ExecutionStrategy.SEQUENTIAL_MULTI: [ExecutionStrategy.SINGLE_AGENT, ExecutionStrategy.FALLBACK_CHAIN],
            ExecutionStrategy.SINGLE_AGENT: [ExecutionStrategy.FALLBACK_CHAIN],
            ExecutionStrategy.COLLABORATIVE_MULTI: [ExecutionStrategy.SEQUENTIAL_MULTI, ExecutionStrategy.PARALLEL_MULTI]
        }
    
    def get_fallback_options(self, failure: FailureEvent, 
                           current_decision: ExecutionDecision,
                           context: Any) -> List[FallbackOption]:
        """Get prioritized list of fallback options for a failure."""
        
        options = []
        failure_type = failure.failure_type
        severity = failure.severity
        
        # Strategy 1: Retry same agent with adjustments
        if failure.retry_count < failure.max_retries and failure_type in [
            FailureType.API_TIMEOUT, FailureType.RATE_LIMIT_EXCEEDED, 
            FailureType.LOW_QUALITY_RESPONSE
        ]:
            options.append(FallbackOption(
                strategy=FallbackStrategy.RETRY_SAME_AGENT,
                priority=1,
                agent_type=failure.agent_type,
                parameter_adjustments=self._get_retry_adjustments(failure),
                delay_seconds=self._calculate_retry_delay(failure),
                max_attempts=failure.max_retries - failure.retry_count,
                description=f"Retry same agent with adjusted parameters"
            ))
        
        # Strategy 2: Switch to alternative agent type
        if failure.agent_type and failure.agent_type in self.agent_priorities:
            alternatives = self.agent_priorities[failure.agent_type]
            for i, alt_agent in enumerate(alternatives[:2]):  # Top 2 alternatives
                options.append(FallbackOption(
                    strategy=FallbackStrategy.SWITCH_AGENT_TYPE,
                    priority=2 + i,
                    agent_type=alt_agent,
                    parameter_adjustments=self._get_agent_switch_adjustments(failure, alt_agent),
                    description=f"Switch to {alt_agent.value} agent"
                ))
        
        # Strategy 3: Adjust parameters for current setup
        if failure_type in [FailureType.LOW_QUALITY_RESPONSE, FailureType.INCOMPLETE_RESPONSE]:
            options.append(FallbackOption(
                strategy=FallbackStrategy.ADJUST_PARAMETERS,
                priority=4,
                agent_type=failure.agent_type,
                parameter_adjustments=self._get_parameter_adjustments(failure),
                description="Adjust execution parameters for better results"
            ))
        
        # Strategy 4: Simplify request
        if context.iteration_count > 3 or failure_type == FailureType.CONTEXT_INCOMPATIBLE:
            options.append(FallbackOption(
                strategy=FallbackStrategy.SIMPLIFY_REQUEST,
                priority=5,
                agent_type=failure.agent_type,
                parameter_adjustments={'simplify_context': True},
                description="Simplify request to reduce complexity"
            ))
        
        # Strategy 5: Escalate to multiple agents
        if severity in [FailureSeverity.MEDIUM, FailureSeverity.HIGH]:
            options.append(FallbackOption(
                strategy=FallbackStrategy.ESCALATE_TO_MULTIPLE,
                priority=6,
                execution_strategy=ExecutionStrategy.SEQUENTIAL_MULTI,
                parameter_adjustments={'redundancy': True},
                description="Use multiple agents for redundancy"
            ))
        
        # Strategy 6: Change execution strategy
        current_strategy = current_decision.strategy
        if current_strategy in self.strategy_alternatives:
            alternatives = self.strategy_alternatives[current_strategy]
            for i, alt_strategy in enumerate(alternatives[:2]):
                options.append(FallbackOption(
                    strategy=FallbackStrategy.CHANGE_STRATEGY,
                    priority=7 + i,
                    execution_strategy=alt_strategy,
                    description=f"Change to {alt_strategy.value} strategy"
                ))
        
        # Strategy 7: Abort execution (last resort)
        if severity == FailureSeverity.CRITICAL or failure.retry_count >= 5:
            options.append(FallbackOption(
                strategy=FallbackStrategy.ABORT_EXECUTION,
                priority=10,
                description="Abort execution due to critical failures"
            ))
        
        # Filter options based on conditions
        filtered_options = []
        for option in options:
            if option.condition is None or option.condition(failure):
                filtered_options.append(option)
        
        # Sort by priority
        filtered_options.sort(key=lambda x: x.priority)
        
        return filtered_options
    
    async def execute_fallback(self, 
                             failure: FailureEvent,
                             fallback_option: FallbackOption,
                             context: Any,
                             original_decision: ExecutionDecision,
                             executor_callback: Callable) -> FallbackAttempt:
        """Execute a specific fallback option."""
        
        attempt_id = f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        start_time = time.time()
        
        attempt = FallbackAttempt(
            attempt_id=attempt_id,
            original_failure=failure,
            fallback_option=fallback_option,
            timestamp=datetime.now()
        )
        
        self.logger.info(f"Executing fallback: {fallback_option.strategy.value} - {fallback_option.description}")
        
        try:
            # Apply delay if specified
            if fallback_option.delay_seconds > 0:
                await asyncio.sleep(fallback_option.delay_seconds)
            
            # Prepare modified context and decision
            modified_context = self._prepare_fallback_context(context, fallback_option, failure)
            modified_decision = self._prepare_fallback_decision(original_decision, fallback_option)
            
            # Execute based on fallback strategy
            result = await self._execute_fallback_strategy(
                fallback_option, modified_context, modified_decision, executor_callback
            )
            
            if result:
                attempt.success = True
                attempt.result_response = result
                self.logger.info(f"Fallback successful: {attempt_id}")
            else:
                attempt.success = False
                attempt.error = "No valid response from fallback execution"
                self.logger.warning(f"Fallback failed: {attempt_id}")
            
        except Exception as e:
            attempt.success = False
            attempt.error = str(e)
            self.logger.error(f"Fallback execution error: {attempt_id} - {e}")
        
        finally:
            attempt.execution_time = time.time() - start_time
            self.fallback_history.append(attempt)
        
        return attempt
    
    async def _execute_fallback_strategy(self,
                                       option: FallbackOption,
                                       context: Any,
                                       decision: ExecutionDecision,
                                       executor_callback: Callable) -> Optional[Any]:
        """Execute the specific fallback strategy."""
        
        strategy = option.strategy
        
        if strategy == FallbackStrategy.RETRY_SAME_AGENT:
            return await self._retry_same_agent(context, decision, executor_callback)
        
        elif strategy == FallbackStrategy.SWITCH_AGENT_TYPE:
            return await self._switch_agent_type(option, context, decision, executor_callback)
        
        elif strategy == FallbackStrategy.ADJUST_PARAMETERS:
            return await self._adjust_parameters(option, context, decision, executor_callback)
        
        elif strategy == FallbackStrategy.SIMPLIFY_REQUEST:
            return await self._simplify_request(context, decision, executor_callback)
        
        elif strategy == FallbackStrategy.ESCALATE_TO_MULTIPLE:
            return await self._escalate_to_multiple(context, decision, executor_callback)
        
        elif strategy == FallbackStrategy.CHANGE_STRATEGY:
            return await self._change_strategy(option, context, decision, executor_callback)
        
        elif strategy == FallbackStrategy.ABORT_EXECUTION:
            self.logger.warning("Aborting execution as fallback strategy")
            return None
        
        return None
    
    async def _retry_same_agent(self, context: Any, 
                              decision: ExecutionDecision,
                              executor_callback: Callable) -> Optional[Any]:
        """Retry with the same agent configuration."""
        return await executor_callback(decision, context)
    
    async def _switch_agent_type(self, option: FallbackOption,
                               context: Any,
                               decision: ExecutionDecision,
                               executor_callback: Callable) -> Optional[Any]:
        """Switch to an alternative agent type."""
        
        if not option.agent_type:
            return None
        
        # Create new decision with different agent
        new_decision = copy.deepcopy(decision)
        
        # Update selected agents to use the fallback agent type
        if new_decision.selected_agents:
            # Replace the first agent with the fallback agent
            new_decision.selected_agents[0] = AgentConfiguration(
                agent_type=option.agent_type,
                specialization="fallback"
            )
        
        return await executor_callback(new_decision, context)
    
    async def _adjust_parameters(self, option: FallbackOption,
                               context: Any,
                               decision: ExecutionDecision,
                               executor_callback: Callable) -> Optional[Any]:
        """Adjust execution parameters."""
        
        # Apply parameter adjustments to context
        for key, value in option.parameter_adjustments.items():
            context.execution_metadata[f'fallback_{key}'] = value
        
        return await executor_callback(decision, context)
    
    async def _simplify_request(self, context: Any,
                              decision: ExecutionDecision,
                              executor_callback: Callable) -> Optional[Any]:
        """Simplify the request to reduce complexity."""
        
        # Create simplified context
        simplified_context = copy.deepcopy(context)
        
        # Simplify user query by taking first sentence
        sentences = simplified_context.user_query.split('.')
        if len(sentences) > 1:
            simplified_context.user_query = sentences[0] + "."
        
        # Reduce conversation history
        simplified_context.conversation_history = simplified_context.conversation_history[-3:]
        
        # Mark as simplified
        simplified_context.execution_metadata['simplified_request'] = True
        
        return await executor_callback(decision, simplified_context)
    
    async def _escalate_to_multiple(self, context: Any,
                                  decision: ExecutionDecision,
                                  executor_callback: Callable) -> Optional[Any]:
        """Escalate to multiple agents for redundancy."""
        
        # Create new decision with multiple agents
        new_decision = copy.deepcopy(decision)
        new_decision.strategy = ExecutionStrategy.SEQUENTIAL_MULTI
        
        # Add redundant agents if not already present
        if len(new_decision.selected_agents) == 1:
            original_agent = new_decision.selected_agents[0]
            
            # Add alternative agent types
            if original_agent.agent_type in self.agent_priorities:
                alternatives = self.agent_priorities[original_agent.agent_type][:2]
                for alt_type in alternatives:
                    new_decision.selected_agents.append(
                        AgentConfiguration(agent_type=alt_type, specialization="redundant")
                    )
        
        return await executor_callback(new_decision, context)
    
    async def _change_strategy(self, option: FallbackOption,
                             context: Any,
                             decision: ExecutionDecision,
                             executor_callback: Callable) -> Optional[Any]:
        """Change the execution strategy."""
        
        if not option.execution_strategy:
            return None
        
        new_decision = copy.deepcopy(decision)
        new_decision.strategy = option.execution_strategy
        
        return await executor_callback(new_decision, context)
    
    def _prepare_fallback_context(self, context: Any,
                                option: FallbackOption,
                                failure: FailureEvent) -> Any:
        """Prepare context for fallback execution."""
        
        fallback_context = copy.deepcopy(context)
        
        # Add fallback metadata
        fallback_context.execution_metadata.update({
            'fallback_strategy': option.strategy.value,
            'fallback_reason': failure.failure_type.value,
            'fallback_attempt': failure.retry_count + 1,
            'original_failure_id': failure.failure_id
        })
        
        # Apply parameter adjustments
        fallback_context.execution_metadata.update(option.parameter_adjustments)
        
        # Preserve context across transition
        fallback_context.shared_variables['fallback_context'] = {
            'original_agent': failure.agent_type.value if failure.agent_type else None,
            'failure_reason': failure.error_message,
            'transition_time': datetime.now().isoformat()
        }
        
        return fallback_context
    
    def _prepare_fallback_decision(self, decision: ExecutionDecision,
                                 option: FallbackOption) -> ExecutionDecision:
        """Prepare decision for fallback execution."""
        
        fallback_decision = copy.deepcopy(decision)
        
        # Update strategy if specified
        if option.execution_strategy:
            fallback_decision.strategy = option.execution_strategy
        
        # Update agent type if specified
        if option.agent_type and fallback_decision.selected_agents:
            fallback_decision.selected_agents[0].agent_type = option.agent_type
        
        return fallback_decision
    
    def _get_retry_adjustments(self, failure: FailureEvent) -> Dict[str, Any]:
        """Get parameter adjustments for retry attempts."""
        
        adjustments = {}
        
        if failure.failure_type == FailureType.API_TIMEOUT:
            adjustments.update({
                'timeout_multiplier': 1.5,
                'reduce_complexity': True
            })
        
        elif failure.failure_type == FailureType.RATE_LIMIT_EXCEEDED:
            adjustments.update({
                'request_delay': 2.0,
                'batch_size_reduction': 0.5
            })
        
        elif failure.failure_type == FailureType.LOW_QUALITY_RESPONSE:
            adjustments.update({
                'quality_threshold_reduction': 0.1,
                'add_examples': True,
                'increase_detail': True
            })
        
        return adjustments
    
    def _get_agent_switch_adjustments(self, failure: FailureEvent, 
                                    new_agent: AgentType) -> Dict[str, Any]:
        """Get adjustments when switching agent types."""
        
        adjustments = {
            'agent_switch_reason': failure.failure_type.value,
            'preserve_context': True
        }
        
        # Agent-specific adjustments
        if new_agent in [AgentType.PROBLEM_SOLVER, AgentType.ANALYST]:
            adjustments['increase_analysis_depth'] = True
        
        elif new_agent in [AgentType.CODE_IMPLEMENTER, AgentType.OPTIMIZER]:
            adjustments['focus_on_implementation'] = True
        
        return adjustments
    
    def _get_parameter_adjustments(self, failure: FailureEvent) -> Dict[str, Any]:
        """Get general parameter adjustments based on failure type."""
        
        adjustments = {}
        
        if failure.failure_type == FailureType.INCOMPLETE_RESPONSE:
            adjustments.update({
                'request_completion': True,
                'max_tokens_increase': 1.5
            })
        
        elif failure.failure_type == FailureType.FORMAT_ERROR:
            adjustments.update({
                'explicit_format_request': True,
                'add_format_examples': True
            })
        
        return adjustments
    
    def _calculate_retry_delay(self, failure: FailureEvent) -> float:
        """Calculate exponential backoff delay for retries."""
        
        base_delay = {
            FailureType.API_TIMEOUT: 5.0,
            FailureType.RATE_LIMIT_EXCEEDED: 30.0,
            FailureType.API_UNAVAILABLE: 60.0,
        }.get(failure.failure_type, 2.0)
        
        # Exponential backoff
        return base_delay * (2 ** failure.retry_count)
    
    def get_fallback_statistics(self) -> Dict[str, Any]:
        """Get statistics about fallback usage."""
        
        if not self.fallback_history:
            return {'total_attempts': 0}
        
        total_attempts = len(self.fallback_history)
        successful_attempts = sum(1 for attempt in self.fallback_history if attempt.success)
        
        # Strategy success rates
        strategy_stats = {}
        for attempt in self.fallback_history:
            strategy = attempt.fallback_option.strategy.value
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {'total': 0, 'successful': 0}
            
            strategy_stats[strategy]['total'] += 1
            if attempt.success:
                strategy_stats[strategy]['successful'] += 1
        
        # Add success rates
        for strategy, stats in strategy_stats.items():
            stats['success_rate'] = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
        
        return {
            'total_attempts': total_attempts,
            'successful_attempts': successful_attempts,
            'overall_success_rate': successful_attempts / total_attempts if total_attempts > 0 else 0,
            'strategy_statistics': strategy_stats,
            'average_execution_time': sum(a.execution_time for a in self.fallback_history) / total_attempts if total_attempts > 0 else 0
        }
    
    def add_agent_priority(self, primary: AgentType, alternatives: List[AgentType]):
        """Add or update agent priority cascade."""
        self.agent_priorities[primary] = alternatives
    
    def add_strategy_alternative(self, primary: ExecutionStrategy, 
                               alternatives: List[ExecutionStrategy]):
        """Add or update strategy alternatives."""
        self.strategy_alternatives[primary] = alternatives
