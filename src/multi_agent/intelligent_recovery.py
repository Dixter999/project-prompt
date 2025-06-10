"""
Intelligent Recovery System for Multi-Agent Execution

Provides comprehensive recovery mechanisms including root cause analysis,
strategy adjustment, exponential backoff, and user notification systems.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Callable, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
import logging
import statistics
import json

if TYPE_CHECKING:
    from .execution_coordinator import ExecutionContext, Any, Any

from .adaptive_decision_engine import ExecutionDecision, ExecutionStrategy
from .agent_specializations import AgentType
from .fault_detector import FailureEvent, FailureType, FailureSeverity, FaultDetector
from .fallback_cascade import FallbackCascade, FallbackOption, FallbackAttempt, FallbackStrategy


class RecoveryAction(Enum):
    """Types of recovery actions."""
    IMMEDIATE_RETRY = "immediate_retry"
    DELAYED_RETRY = "delayed_retry"
    PARAMETER_ADJUSTMENT = "parameter_adjustment"
    AGENT_SUBSTITUTION = "agent_substitution"
    STRATEGY_CHANGE = "strategy_change"
    ESCALATION = "escalation"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    USER_INTERVENTION = "user_intervention"
    ABORT_WITH_PARTIAL = "abort_with_partial"


class RecoveryStatus(Enum):
    """Status of recovery operations."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    ESCALATED = "escalated"
    USER_REQUIRED = "user_required"


@dataclass
class RecoveryPlan:
    """Represents a comprehensive recovery plan."""
    plan_id: str
    original_failure: FailureEvent
    root_cause_analysis: Dict[str, Any]
    recommended_actions: List[RecoveryAction]
    fallback_options: List[FallbackOption]
    estimated_success_probability: float
    estimated_recovery_time: float
    user_notification_required: bool = False
    max_recovery_attempts: int = 3
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RecoverySession:
    """Tracks a complete recovery session."""
    session_id: str
    recovery_plan: RecoveryPlan
    attempts: List[FallbackAttempt] = field(default_factory=list)
    status: RecoveryStatus = RecoveryStatus.NOT_STARTED
    final_result: Optional[Any] = None
    user_feedback: Optional[Dict[str, Any]] = None
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class UserNotification:
    """Notification to user about recovery status."""
    notification_id: str
    severity: FailureSeverity
    title: str
    message: str
    options: List[Dict[str, Any]] = field(default_factory=list)
    requires_response: bool = False
    timeout_seconds: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)


class IntelligentRecoverySystem:
    """Manages intelligent recovery from multi-agent execution failures."""
    
    def __init__(self, fault_detector: FaultDetector, fallback_cascade: FallbackCascade):
        self.fault_detector = fault_detector
        self.fallback_cascade = fallback_cascade
        self.logger = logging.getLogger(__name__)
        
        # Recovery tracking
        self.active_sessions: Dict[str, RecoverySession] = {}
        self.recovery_history: List[RecoverySession] = []
        self.user_notifications: List[UserNotification] = []
        
        # Configuration
        self.max_concurrent_recoveries = 5
        self.default_recovery_timeout = 300  # 5 minutes
        self.user_response_timeout = 60  # 1 minute
        
        # Pattern learning
        self.success_patterns: Dict[str, Any] = {}
        self.failure_patterns: Dict[str, Any] = {}
    
    async def initiate_recovery(self, 
                              failure: FailureEvent,
                              context: Any,
                              decision: ExecutionDecision,
                              executor_callback: Callable) -> RecoverySession:
        """Initiate intelligent recovery from a failure."""
        
        session_id = f"recovery_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        self.logger.info(f"Initiating recovery session: {session_id} for failure: {failure.failure_type.value}")
        
        # Analyze root cause
        root_cause = await self._analyze_root_cause(failure, context)
        
        # Create recovery plan
        recovery_plan = await self._create_recovery_plan(failure, root_cause, context, decision)
        
        # Create recovery session
        session = RecoverySession(
            session_id=session_id,
            recovery_plan=recovery_plan,
            status=RecoveryStatus.IN_PROGRESS
        )
        
        self.active_sessions[session_id] = session
        
        # Check if user notification is required
        if recovery_plan.user_notification_required:
            await self._notify_user_about_recovery(session)
        
        # Execute recovery
        try:
            result = await self._execute_recovery_plan(session, context, decision, executor_callback)
            session.final_result = result
            session.status = RecoveryStatus.SUCCESSFUL if result else RecoveryStatus.FAILED
            
        except Exception as e:
            self.logger.error(f"Recovery execution failed: {session_id} - {e}")
            session.status = RecoveryStatus.FAILED
        
        finally:
            session.completed_at = datetime.now()
            self._finalize_recovery_session(session)
        
        return session
    
    async def _analyze_root_cause(self, failure: FailureEvent, 
                                context: Any) -> Dict[str, Any]:
        """Perform comprehensive root cause analysis."""
        
        analysis = {
            'primary_cause': failure.failure_type.value,
            'severity': failure.severity.value,
            'contributing_factors': [],
            'system_state': {},
            'patterns': {},
            'recommendations': []
        }
        
        # Analyze system state
        analysis['system_state'] = {
            'iteration_count': context.iteration_count,
            'conversation_length': len(context.conversation_history),
            'shared_variables_count': len(context.shared_variables),
            'agent_states_count': len(context.agent_states),
            'execution_metadata': dict(context.execution_metadata)
        }
        
        # Look for contributing factors
        contributing_factors = []
        
        # High iteration count
        if context.iteration_count > 7:
            contributing_factors.append({
                'factor': 'high_iteration_count',
                'description': 'Execution has exceeded normal iteration limits',
                'impact': 'medium',
                'suggestion': 'Consider simplifying the request or breaking into smaller tasks'
            })
        
        # Complex conversation history
        if len(context.conversation_history) > 20:
            contributing_factors.append({
                'factor': 'complex_conversation_history',
                'description': 'Conversation history is becoming unwieldy',
                'impact': 'low',
                'suggestion': 'Consider context pruning or summarization'
            })
        
        # Recent failure patterns
        recent_failures = self.fault_detector.get_recent_failure_pattern(failure.failure_type, hours=1)
        if len(recent_failures) >= 3:
            contributing_factors.append({
                'factor': 'recurring_failure_pattern',
                'description': f'Similar failures occurred {len(recent_failures)} times in the last hour',
                'impact': 'high',
                'suggestion': 'Systemic issue may require different approach or escalation'
            })
        
        # Agent-specific issues
        if failure.agent_id and self.fault_detector.is_agent_problematic(failure.agent_id):
            contributing_factors.append({
                'factor': 'problematic_agent',
                'description': f'Agent {failure.agent_id} has consistent failure patterns',
                'impact': 'high',
                'suggestion': 'Switch to alternative agent or review agent configuration'
            })
        
        analysis['contributing_factors'] = contributing_factors
        
        # Analyze patterns from history
        patterns = self._analyze_failure_patterns(failure)
        analysis['patterns'] = patterns
        
        # Generate recommendations
        recommendations = self._generate_recovery_recommendations(failure, contributing_factors, patterns)
        analysis['recommendations'] = recommendations
        
        return analysis
    
    def _analyze_failure_patterns(self, failure: FailureEvent) -> Dict[str, Any]:
        """Analyze patterns in failure history."""
        
        patterns = {
            'frequency': 'normal',
            'time_pattern': None,
            'agent_correlation': None,
            'escalation_trend': False
        }
        
        # Analyze frequency
        recent_same_type = self.fault_detector.get_recent_failure_pattern(failure.failure_type, hours=24)
        if len(recent_same_type) > 5:
            patterns['frequency'] = 'high'
        elif len(recent_same_type) > 2:
            patterns['frequency'] = 'elevated'
        
        # Analyze time patterns
        if len(recent_same_type) >= 3:
            timestamps = [f.timestamp for f in recent_same_type]
            intervals = [(timestamps[i+1] - timestamps[i]).total_seconds() for i in range(len(timestamps)-1)]
            
            if all(interval < 300 for interval in intervals):  # Less than 5 minutes apart
                patterns['time_pattern'] = 'rapid_succession'
            elif statistics.stdev(intervals) < 60:  # Low variance
                patterns['time_pattern'] = 'regular_intervals'
        
        # Check for escalation trend
        recent_all_failures = [f for f in self.fault_detector.failure_history[-10:]]
        if len(recent_all_failures) >= 5:
            severity_trend = [f.severity for f in recent_all_failures[-5:]]
            severity_values = {
                FailureSeverity.LOW: 1,
                FailureSeverity.MEDIUM: 2,
                FailureSeverity.HIGH: 3,
                FailureSeverity.CRITICAL: 4
            }
            values = [severity_values[s] for s in severity_trend]
            if all(values[i] <= values[i+1] for i in range(len(values)-1)):
                patterns['escalation_trend'] = True
        
        return patterns
    
    def _generate_recovery_recommendations(self, failure: FailureEvent,
                                         contributing_factors: List[Dict[str, Any]],
                                         patterns: Dict[str, Any]) -> List[str]:
        """Generate specific recovery recommendations."""
        
        recommendations = []
        
        # Based on failure type
        type_recommendations = {
            FailureType.API_UNAVAILABLE: [
                "Switch to backup API endpoint",
                "Implement circuit breaker pattern",
                "Consider offline mode capabilities"
            ],
            FailureType.RATE_LIMIT_EXCEEDED: [
                "Implement exponential backoff",
                "Reduce request frequency",
                "Consider request batching"
            ],
            FailureType.LOW_QUALITY_RESPONSE: [
                "Refine prompt engineering",
                "Switch to specialized agent",
                "Add quality validation checks"
            ],
            FailureType.CONTEXT_INCOMPATIBLE: [
                "Simplify context",
                "Break down complex requests",
                "Use context-aware agent selection"
            ]
        }
        
        recommendations.extend(type_recommendations.get(failure.failure_type, []))
        
        # Based on contributing factors
        for factor in contributing_factors:
            if factor['impact'] == 'high':
                recommendations.append(f"Priority: {factor['suggestion']}")
            else:
                recommendations.append(factor['suggestion'])
        
        # Based on patterns
        if patterns['frequency'] == 'high':
            recommendations.append("Investigate systemic issues causing high failure frequency")
        
        if patterns['escalation_trend']:
            recommendations.append("Implement preventive measures to stop failure escalation")
        
        if patterns['time_pattern'] == 'rapid_succession':
            recommendations.append("Add circuit breaker to prevent cascading failures")
        
        return list(set(recommendations))  # Remove duplicates
    
    async def _create_recovery_plan(self, failure: FailureEvent,
                                  root_cause: Dict[str, Any],
                                  context: Any,
                                  decision: ExecutionDecision) -> RecoveryPlan:
        """Create a comprehensive recovery plan."""
        
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Get fallback options from cascade system
        fallback_options = self.fallback_cascade.get_fallback_options(failure, decision, context)
        
        # Determine recommended actions
        recommended_actions = self._determine_recovery_actions(failure, root_cause, fallback_options)
        
        # Estimate success probability
        success_probability = self._estimate_success_probability(failure, fallback_options, root_cause)
        
        # Estimate recovery time
        recovery_time = self._estimate_recovery_time(failure, fallback_options)
        
        # Determine if user notification is required
        user_notification_required = self._should_notify_user(failure, root_cause)
        
        return RecoveryPlan(
            plan_id=plan_id,
            original_failure=failure,
            root_cause_analysis=root_cause,
            recommended_actions=recommended_actions,
            fallback_options=fallback_options,
            estimated_success_probability=success_probability,
            estimated_recovery_time=recovery_time,
            user_notification_required=user_notification_required
        )
    
    def _determine_recovery_actions(self, failure: FailureEvent,
                                  root_cause: Dict[str, Any],
                                  fallback_options: List[FallbackOption]) -> List[RecoveryAction]:
        """Determine the sequence of recovery actions to take."""
        
        actions = []
        
        # Immediate retry for transient issues
        if failure.failure_type in [FailureType.API_TIMEOUT, FailureType.RATE_LIMIT_EXCEEDED]:
            if failure.retry_count < 2:
                actions.append(RecoveryAction.IMMEDIATE_RETRY)
            else:
                actions.append(RecoveryAction.DELAYED_RETRY)
        
        # Parameter adjustment for quality issues
        if failure.failure_type in [FailureType.LOW_QUALITY_RESPONSE, FailureType.INCOMPLETE_RESPONSE]:
            actions.append(RecoveryAction.PARAMETER_ADJUSTMENT)
        
        # Agent substitution for agent-specific issues
        if any(factor['factor'] == 'problematic_agent' for factor in root_cause['contributing_factors']):
            actions.append(RecoveryAction.AGENT_SUBSTITUTION)
        
        # Strategy change for systemic issues
        if any(factor['factor'] == 'recurring_failure_pattern' for factor in root_cause['contributing_factors']):
            actions.append(RecoveryAction.STRATEGY_CHANGE)
        
        # Escalation for high severity or multiple failures
        if failure.severity in [FailureSeverity.HIGH, FailureSeverity.CRITICAL]:
            actions.append(RecoveryAction.ESCALATION)
        
        # Graceful degradation as fallback
        if len(actions) == 0 or failure.retry_count >= 3:
            actions.append(RecoveryAction.GRACEFUL_DEGRADATION)
        
        # User intervention for critical issues
        if failure.severity == FailureSeverity.CRITICAL:
            actions.append(RecoveryAction.USER_INTERVENTION)
        
        return actions
    
    def _estimate_success_probability(self, failure: FailureEvent,
                                    fallback_options: List[FallbackOption],
                                    root_cause: Dict[str, Any]) -> float:
        """Estimate the probability of successful recovery."""
        
        base_probability = 0.7  # Base optimistic assumption
        
        # Adjust based on failure type
        type_adjustments = {
            FailureType.API_UNAVAILABLE: -0.3,
            FailureType.COST_LIMIT_EXCEEDED: -0.5,
            FailureType.CONTEXT_INCOMPATIBLE: -0.1,
            FailureType.LOW_QUALITY_RESPONSE: 0.1,
            FailureType.PARSING_ERROR: 0.2
        }
        
        base_probability += type_adjustments.get(failure.failure_type, 0)
        
        # Adjust based on retry count
        base_probability -= failure.retry_count * 0.15
        
        # Adjust based on available fallback options
        if len(fallback_options) > 3:
            base_probability += 0.2
        elif len(fallback_options) < 2:
            base_probability -= 0.2
        
        # Adjust based on contributing factors
        high_impact_factors = sum(1 for factor in root_cause['contributing_factors'] 
                                if factor['impact'] == 'high')
        base_probability -= high_impact_factors * 0.1
        
        # Adjust based on patterns
        if root_cause['patterns'].get('escalation_trend', False):
            base_probability -= 0.2
        
        if root_cause['patterns'].get('frequency') == 'high':
            base_probability -= 0.15
        
        return max(0.1, min(0.95, base_probability))
    
    def _estimate_recovery_time(self, failure: FailureEvent,
                              fallback_options: List[FallbackOption]) -> float:
        """Estimate recovery time in seconds."""
        
        base_time = 30.0  # Base 30 seconds
        
        # Add time based on failure type
        type_times = {
            FailureType.API_UNAVAILABLE: 60.0,
            FailureType.RATE_LIMIT_EXCEEDED: 90.0,
            FailureType.AGENT_OVERLOAD: 45.0,
            FailureType.LOW_QUALITY_RESPONSE: 20.0
        }
        
        base_time += type_times.get(failure.failure_type, 15.0)
        
        # Add time for each fallback option
        for option in fallback_options[:3]:  # Consider first 3 options
            base_time += option.delay_seconds
            if option.strategy == FallbackStrategy.ESCALATE_TO_MULTIPLE:
                base_time += 60.0  # Multiple agents take longer
            elif option.strategy == FallbackStrategy.CHANGE_STRATEGY:
                base_time += 30.0  # Strategy change overhead
        
        # Add exponential backoff time
        if failure.retry_count > 0:
            base_time += min(300, 10 * (2 ** failure.retry_count))
        
        return base_time
    
    def _should_notify_user(self, failure: FailureEvent, 
                          root_cause: Dict[str, Any]) -> bool:
        """Determine if user notification is required."""
        
        # Always notify for critical failures
        if failure.severity == FailureSeverity.CRITICAL:
            return True
        
        # Notify for cost-related issues
        if failure.failure_type == FailureType.COST_LIMIT_EXCEEDED:
            return True
        
        # Notify for recurring patterns
        if any(factor['factor'] == 'recurring_failure_pattern' 
               for factor in root_cause['contributing_factors']):
            return True
        
        # Notify if escalation trend detected
        if root_cause['patterns'].get('escalation_trend', False):
            return True
        
        # Notify if multiple high-impact factors
        high_impact_count = sum(1 for factor in root_cause['contributing_factors']
                               if factor['impact'] == 'high')
        if high_impact_count >= 2:
            return True
        
        return False
    
    async def _execute_recovery_plan(self, session: RecoverySession,
                                   context: Any,
                                   decision: ExecutionDecision,
                                   executor_callback: Callable) -> Optional[Any]:
        """Execute the recovery plan with exponential backoff and smart retries."""
        
        plan = session.recovery_plan
        timeout_time = datetime.now() + timedelta(seconds=self.default_recovery_timeout)
        
        self.logger.info(f"Executing recovery plan: {plan.plan_id}")
        
        # Try each fallback option in priority order
        for i, fallback_option in enumerate(plan.fallback_options):
            if datetime.now() > timeout_time:
                self.logger.warning(f"Recovery timeout reached for session: {session.session_id}")
                break
            
            try:
                self.logger.info(f"Attempting fallback option {i+1}/{len(plan.fallback_options)}: {fallback_option.strategy.value}")
                
                # Execute fallback with exponential backoff
                attempt = await self._execute_with_backoff(
                    session, fallback_option, context, decision, executor_callback
                )
                
                session.attempts.append(attempt)
                
                if attempt.success and attempt.result_response:
                    self.logger.info(f"Recovery successful with option: {fallback_option.strategy.value}")
                    await self._learn_from_success(session, attempt)
                    return attempt.result_response
                
                else:
                    self.logger.warning(f"Fallback option failed: {fallback_option.strategy.value}")
                    await self._learn_from_failure(session, attempt)
            
            except Exception as e:
                self.logger.error(f"Error executing fallback option: {e}")
                continue
        
        # If all options failed, try graceful degradation
        self.logger.warning(f"All fallback options failed for session: {session.session_id}")
        degraded_result = await self._attempt_graceful_degradation(session, context)
        
        if degraded_result:
            self.logger.info("Graceful degradation successful")
            return degraded_result
        
        self.logger.error(f"Complete recovery failure for session: {session.session_id}")
        return None
    
    async def _execute_with_backoff(self, session: RecoverySession,
                                  fallback_option: FallbackOption,
                                  context: Any,
                                  decision: ExecutionDecision,
                                  executor_callback: Callable) -> FallbackAttempt:
        """Execute fallback with exponential backoff."""
        
        max_attempts = fallback_option.max_attempts
        base_delay = fallback_option.delay_seconds
        
        for attempt_num in range(max_attempts):
            if attempt_num > 0:
                # Exponential backoff
                delay = base_delay * (2 ** (attempt_num - 1))
                self.logger.info(f"Waiting {delay:.1f}s before retry attempt {attempt_num + 1}")
                await asyncio.sleep(delay)
            
            try:
                attempt = await self.fallback_cascade.execute_fallback(
                    session.recovery_plan.original_failure,
                    fallback_option,
                    context,
                    decision,
                    executor_callback
                )
                
                if attempt.success:
                    return attempt
                
            except Exception as e:
                self.logger.warning(f"Retry attempt {attempt_num + 1} failed: {e}")
                continue
        
        # Return the last attempt if all retries failed
        return attempt if 'attempt' in locals() else FallbackAttempt(
            attempt_id=f"failed_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            original_failure=session.recovery_plan.original_failure,
            fallback_option=fallback_option,
            timestamp=datetime.now(),
            success=False,
            error="All retry attempts exhausted"
        )
    
    async def _attempt_graceful_degradation(self, session: RecoverySession,
                                          context: Any) -> Optional[Any]:
        """Attempt graceful degradation when all else fails."""
        
        self.logger.info("Attempting graceful degradation")
        
        # Create a minimal response based on available context
        degraded_response = Any(
            agent_id="recovery_system",
            agent_type=AgentType.SYSTEM_COORDINATOR,
            raw_response=self._generate_degraded_response(session, context),
            quality_score=0.3,  # Low quality but functional
            quality_assessment=ResponseQuality.ACCEPTABLE,
            metadata={
                'recovery_session': session.session_id,
                'degraded_response': True,
                'original_failure': session.recovery_plan.original_failure.failure_type.value
            }
        )
        
        return degraded_response
    
    def _generate_degraded_response(self, session: RecoverySession, 
                                  context: Any) -> str:
        """Generate a degraded but useful response."""
        
        failure = session.recovery_plan.original_failure
        
        response_parts = [
            f"I encountered difficulties processing your request due to {failure.failure_type.value}.",
            "",
            "Based on the available information, here's what I can provide:",
            ""
        ]
        
        # Add context-based suggestions
        if context.user_query:
            response_parts.extend([
                f"Your request: {context.user_query[:200]}{'...' if len(context.user_query) > 200 else ''}",
                ""
            ])
        
        # Add recommendations from recovery plan
        if session.recovery_plan.root_cause_analysis.get('recommendations'):
            response_parts.extend([
                "Recommendations for proceeding:",
                ""
            ])
            for i, rec in enumerate(session.recovery_plan.root_cause_analysis['recommendations'][:3], 1):
                response_parts.append(f"{i}. {rec}")
            response_parts.append("")
        
        # Add next steps
        response_parts.extend([
            "Suggested next steps:",
            "1. Try simplifying your request",
            "2. Break complex tasks into smaller parts", 
            "3. Check system status and try again later",
            "",
            "This is a degraded response due to system recovery. Please try again or contact support if issues persist."
        ])
        
        return "\n".join(response_parts)
    
    async def _notify_user_about_recovery(self, session: RecoverySession):
        """Notify user about recovery process."""
        
        failure = session.recovery_plan.original_failure
        plan = session.recovery_plan
        
        notification = UserNotification(
            notification_id=f"notify_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            severity=failure.severity,
            title=f"Recovery in Progress: {failure.failure_type.value.replace('_', ' ').title()}",
            message=self._create_user_notification_message(session),
            options=self._create_user_notification_options(session),
            requires_response=failure.severity == FailureSeverity.CRITICAL,
            timeout_seconds=self.user_response_timeout if failure.severity == FailureSeverity.CRITICAL else None
        )
        
        self.user_notifications.append(notification)
        self.logger.info(f"User notification created: {notification.notification_id}")
    
    def _create_user_notification_message(self, session: RecoverySession) -> str:
        """Create user notification message."""
        
        failure = session.recovery_plan.original_failure
        plan = session.recovery_plan
        
        message_parts = [
            f"I'm experiencing a {failure.severity.value} issue: {failure.failure_type.value.replace('_', ' ')}",
            "",
            f"Root cause: {plan.root_cause_analysis.get('primary_cause', 'Unknown')}",
            f"Estimated recovery time: {plan.estimated_recovery_time:.0f} seconds",
            f"Success probability: {plan.estimated_success_probability:.1%}",
            ""
        ]
        
        if plan.root_cause_analysis.get('recommendations'):
            message_parts.extend([
                "Recommended actions:",
                ""
            ])
            for rec in plan.root_cause_analysis['recommendations'][:2]:
                message_parts.append(f"• {rec}")
            message_parts.append("")
        
        message_parts.append("I'm working on recovering automatically. You'll be notified of the outcome.")
        
        return "\n".join(message_parts)
    
    def _create_user_notification_options(self, session: RecoverySession) -> List[Dict[str, Any]]:
        """Create user notification options."""
        
        options = [
            {
                'id': 'continue',
                'label': 'Continue automatic recovery',
                'description': 'Let the system attempt recovery automatically'
            },
            {
                'id': 'simplify',
                'label': 'Simplify request',
                'description': 'Reduce complexity and try a simpler approach'
            }
        ]
        
        if session.recovery_plan.original_failure.severity in [FailureSeverity.HIGH, FailureSeverity.CRITICAL]:
            options.extend([
                {
                    'id': 'abort',
                    'label': 'Abort and get partial results',
                    'description': 'Stop execution and return any partial results'
                },
                {
                    'id': 'manual',
                    'label': 'Switch to manual mode',
                    'description': 'Get step-by-step guidance for manual completion'
                }
            ])
        
        return options
    
    async def _learn_from_success(self, session: RecoverySession, attempt: FallbackAttempt):
        """Learn from successful recovery for future improvements."""
        
        success_key = f"{session.recovery_plan.original_failure.failure_type.value}_{attempt.fallback_option.strategy.value}"
        
        if success_key not in self.success_patterns:
            self.success_patterns[success_key] = {
                'count': 0,
                'total_time': 0.0,
                'success_rate': 0.0
            }
        
        pattern = self.success_patterns[success_key]
        pattern['count'] += 1
        pattern['total_time'] += attempt.execution_time
        pattern['average_time'] = pattern['total_time'] / pattern['count']
        
        self.logger.debug(f"Learned from success: {success_key}")
    
    async def _learn_from_failure(self, session: RecoverySession, attempt: FallbackAttempt):
        """Learn from failed recovery attempts."""
        
        failure_key = f"{session.recovery_plan.original_failure.failure_type.value}_{attempt.fallback_option.strategy.value}"
        
        if failure_key not in self.failure_patterns:
            self.failure_patterns[failure_key] = {
                'count': 0,
                'common_errors': []
            }
        
        pattern = self.failure_patterns[failure_key]
        pattern['count'] += 1
        
        if attempt.error:
            pattern['common_errors'].append(attempt.error)
            # Keep only last 10 errors
            pattern['common_errors'] = pattern['common_errors'][-10:]
        
        self.logger.debug(f"Learned from failure: {failure_key}")
    
    def _finalize_recovery_session(self, session: RecoverySession):
        """Finalize and archive recovery session."""
        
        # Remove from active sessions
        if session.session_id in self.active_sessions:
            del self.active_sessions[session.session_id]
        
        # Add to history
        self.recovery_history.append(session)
        
        # Keep history manageable
        if len(self.recovery_history) > 100:
            self.recovery_history = self.recovery_history[-50:]
        
        # Log summary
        duration = (session.completed_at - session.started_at).total_seconds() if session.completed_at else 0
        self.logger.info(
            f"Recovery session finalized: {session.session_id} "
            f"Status: {session.status.value} "
            f"Duration: {duration:.1f}s "
            f"Attempts: {len(session.attempts)}"
        )
    
    def get_recovery_statistics(self) -> Dict[str, Any]:
        """Get comprehensive recovery statistics."""
        
        if not self.recovery_history:
            return {'total_sessions': 0}
        
        total_sessions = len(self.recovery_history)
        successful_sessions = sum(1 for s in self.recovery_history if s.status == RecoveryStatus.SUCCESSFUL)
        
        # Calculate average metrics
        total_duration = sum((s.completed_at - s.started_at).total_seconds() 
                           for s in self.recovery_history if s.completed_at)
        avg_duration = total_duration / total_sessions if total_sessions > 0 else 0
        
        total_attempts = sum(len(s.attempts) for s in self.recovery_history)
        avg_attempts = total_attempts / total_sessions if total_sessions > 0 else 0
        
        return {
            'total_sessions': total_sessions,
            'successful_sessions': successful_sessions,
            'success_rate': successful_sessions / total_sessions if total_sessions > 0 else 0,
            'average_duration_seconds': avg_duration,
            'average_attempts_per_session': avg_attempts,
            'active_sessions': len(self.active_sessions),
            'success_patterns_learned': len(self.success_patterns),
            'failure_patterns_learned': len(self.failure_patterns),
            'pending_notifications': len([n for n in self.user_notifications if n.requires_response])
        }
    
    def get_user_notifications(self, unread_only: bool = True) -> List[UserNotification]:
        """Get user notifications."""
        
        if unread_only:
            # Return notifications from last hour that might still be relevant
            cutoff = datetime.now() - timedelta(hours=1)
            return [n for n in self.user_notifications if n.created_at > cutoff]
        
        return self.user_notifications.copy()
    
    async def handle_user_response(self, notification_id: str, 
                                 response_option: str, 
                                 additional_data: Optional[Dict[str, Any]] = None):
        """Handle user response to notification."""
        
        notification = next((n for n in self.user_notifications if n.notification_id == notification_id), None)
        
        if not notification:
            self.logger.warning(f"Unknown notification ID: {notification_id}")
            return
        
        self.logger.info(f"User response to notification {notification_id}: {response_option}")
        
        # Find associated recovery session
        related_sessions = [s for s in self.active_sessions.values() 
                          if s.recovery_plan.user_notification_required]
        
        for session in related_sessions:
            session.user_feedback = {
                'option': response_option,
                'additional_data': additional_data,
                'timestamp': datetime.now().isoformat()
            }
            
            # Handle specific responses
            if response_option == 'abort':
                session.status = RecoveryStatus.ESCALATED
            elif response_option == 'simplify':
                # Mark for simplified retry
                session.recovery_plan.fallback_options.insert(0, FallbackOption(
                    strategy=FallbackStrategy.SIMPLIFY_REQUEST,
                    priority=0,
                    description="User requested simplification"
                ))
