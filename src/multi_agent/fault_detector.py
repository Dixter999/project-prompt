# filepath: /mnt/h/Projects/project-prompt/src/multi_agent/fault_detector.py
"""
Fault Detection System for Multi-Agent Execution - FASE 5

Detects and classifies different types of failures during agent execution
to enable appropriate fallback strategies.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
import logging
import re
import json

if TYPE_CHECKING:
    from .execution_coordinator import ExecutionContext, ProcessedResponse, ResponseQuality

from .agent_specializations import AgentType


class FailureType(Enum):
    """Types of failures that can occur during execution."""
    API_UNAVAILABLE = "api_unavailable"
    API_TIMEOUT = "api_timeout"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    COST_LIMIT_EXCEEDED = "cost_limit_exceeded"
    LOW_QUALITY_RESPONSE = "low_quality_response"
    INCOMPLETE_RESPONSE = "incomplete_response"
    PARSING_ERROR = "parsing_error"
    FORMAT_ERROR = "format_error"
    CONTEXT_INCOMPATIBLE = "context_incompatible"
    AUTHENTICATION_ERROR = "authentication_error"
    QUOTA_EXCEEDED = "quota_exceeded"
    NETWORK_ERROR = "network_error"
    UNKNOWN_ERROR = "unknown_error"


class FailureSeverity(Enum):
    """Severity levels for failures."""
    LOW = "low"          # Minor issues, can continue with degraded performance
    MEDIUM = "medium"    # Significant issues, requires fallback
    HIGH = "high"        # Critical issues, requires immediate recovery
    CRITICAL = "critical"  # System-breaking issues, may require abort


@dataclass
class FailureEvent:
    """Represents a detected failure event."""
    failure_id: str
    failure_type: FailureType
    severity: FailureSeverity
    agent_id: Optional[str]
    agent_type: Optional[AgentType]
    timestamp: datetime
    error_message: str
    context: Dict[str, Any] = field(default_factory=dict)
    root_cause: Optional[str] = None
    suggested_action: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    is_recoverable: bool = True


class FaultDetector:
    """Detects and analyzes faults in multi-agent execution."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.failure_history: List[FailureEvent] = []
        self.agent_failure_counts: Dict[str, int] = {}
        self.failure_patterns: Dict[FailureType, Dict[str, Any]] = {}
        self._initialize_failure_patterns()
    
    def _initialize_failure_patterns(self):
        """Initialize known failure patterns for detection."""
        self.failure_patterns = {
            FailureType.API_UNAVAILABLE: {
                'keywords': ['connection refused', 'service unavailable', 'network error', '503', '502'],
                'severity': FailureSeverity.HIGH,
                'retry_delay': 30,
                'max_retries': 2
            },
            FailureType.API_TIMEOUT: {
                'keywords': ['timeout', 'request timeout', 'connection timeout'],
                'severity': FailureSeverity.MEDIUM,
                'retry_delay': 10,
                'max_retries': 3
            },
            FailureType.RATE_LIMIT_EXCEEDED: {
                'keywords': ['rate limit', 'too many requests', '429', 'quota exceeded'],
                'severity': FailureSeverity.MEDIUM,
                'retry_delay': 60,
                'max_retries': 5
            },
            FailureType.COST_LIMIT_EXCEEDED: {
                'keywords': ['cost limit', 'billing limit', 'usage exceeded', 'insufficient credits'],
                'severity': FailureSeverity.HIGH,
                'retry_delay': 0,  # No retry for cost issues
                'max_retries': 0
            },
            FailureType.LOW_QUALITY_RESPONSE: {
                'keywords': ['unclear', 'incomplete', 'vague', 'not specific'],
                'quality_threshold': 0.3,
                'severity': FailureSeverity.LOW,
                'retry_delay': 5,
                'max_retries': 2
            },
            FailureType.INCOMPLETE_RESPONSE: {
                'keywords': ['truncated', 'cut off', 'partial', 'incomplete'],
                'min_length': 50,
                'severity': FailureSeverity.MEDIUM,
                'retry_delay': 5,
                'max_retries': 3
            },
            FailureType.PARSING_ERROR: {
                'keywords': ['parse error', 'syntax error', 'invalid json', 'malformed'],
                'severity': FailureSeverity.MEDIUM,
                'retry_delay': 2,
                'max_retries': 2
            },
            FailureType.FORMAT_ERROR: {
                'keywords': ['format error', 'invalid format', 'unexpected format'],
                'severity': FailureSeverity.LOW,
                'retry_delay': 2,
                'max_retries': 2
            },
            FailureType.CONTEXT_INCOMPATIBLE: {
                'keywords': ['context error', 'incompatible', 'out of scope', 'not applicable'],
                'severity': FailureSeverity.MEDIUM,
                'retry_delay': 0,
                'max_retries': 1
            }
        }
    
    async def detect_failure(self, 
                           error: Optional[Exception] = None,
                           response: Optional[Any] = None,  # Using Any to avoid circular import
                           context: Optional[Any] = None,   # Using Any to avoid circular import
                           agent_id: Optional[str] = None,
                           agent_type: Optional[AgentType] = None) -> Optional[FailureEvent]:
        """Detect and classify a failure event."""
        
        failure_id = f"fail_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Detect failure type and severity
        failure_type, severity = await self._classify_failure(error, response, context)
        
        if failure_type == FailureType.UNKNOWN_ERROR and not error and not response:
            return None  # No detectable failure
        
        # Create failure event
        failure_event = FailureEvent(
            failure_id=failure_id,
            failure_type=failure_type,
            severity=severity,
            agent_id=agent_id,
            agent_type=agent_type,
            timestamp=datetime.now(),
            error_message=str(error) if error else "Response quality issue"
        )
        
        # Add context information
        if context:
            failure_event.context = {
                'iteration_count': getattr(context, 'iteration_count', 0),
                'user_query': getattr(context, 'user_query', '')[:100],  # Truncate for storage
                'execution_metadata': getattr(context, 'execution_metadata', {}).copy()
            }
        
        if response:
            failure_event.context.update({
                'quality_score': getattr(response, 'quality_score', 0.0),
                'quality_assessment': getattr(response, 'quality_assessment', None),
                'response_length': len(getattr(response, 'raw_response', '')),
                'has_code': bool(getattr(response, 'extracted_code', [])),
                'instruction_count': len(getattr(response, 'instructions', []))
            })
        
        # Analyze root cause
        failure_event.root_cause = await self._analyze_root_cause(failure_event)
        
        # Suggest action
        failure_event.suggested_action = self._suggest_action(failure_event)
        
        # Set retry parameters
        pattern = self.failure_patterns.get(failure_type, {})
        failure_event.max_retries = pattern.get('max_retries', 1)
        
        # Update failure tracking
        self._track_failure(failure_event)
        
        self.logger.warning(f"Detected failure: {failure_type.value} (severity: {severity.value}) - {failure_event.error_message}")
        
        return failure_event
    
    async def _classify_failure(self, 
                              error: Optional[Exception],
                              response: Optional[Any],
                              context: Optional[Any]) -> Tuple[FailureType, FailureSeverity]:
        """Classify the type and severity of a failure."""
        
        # Analyze exception-based failures
        if error:
            error_msg = str(error).lower()
            
            for failure_type, pattern in self.failure_patterns.items():
                keywords = pattern.get('keywords', [])
                if any(keyword in error_msg for keyword in keywords):
                    return failure_type, pattern.get('severity', FailureSeverity.MEDIUM)
            
            # Check for specific exception types
            if isinstance(error, asyncio.TimeoutError):
                return FailureType.API_TIMEOUT, FailureSeverity.MEDIUM
            elif isinstance(error, ConnectionError):
                return FailureType.API_UNAVAILABLE, FailureSeverity.HIGH
            elif isinstance(error, (json.JSONDecodeError, ValueError)):
                return FailureType.PARSING_ERROR, FailureSeverity.MEDIUM
            
            return FailureType.UNKNOWN_ERROR, FailureSeverity.MEDIUM
        
        # Analyze response-based failures
        if response:
            quality_score = getattr(response, 'quality_score', 1.0)
            raw_response = getattr(response, 'raw_response', '')
            quality_assessment = getattr(response, 'quality_assessment', None)
            agent_type = getattr(response, 'agent_type', None)
            extracted_code = getattr(response, 'extracted_code', [])
            
            # Check quality threshold
            if quality_score < 0.3:
                return FailureType.LOW_QUALITY_RESPONSE, FailureSeverity.LOW
            
            # Check response completeness
            if len(raw_response) < 50:
                return FailureType.INCOMPLETE_RESPONSE, FailureSeverity.MEDIUM
            
            # Check for quality indicators using string comparison
            if hasattr(quality_assessment, 'value'):
                if quality_assessment.value == 'INVALID':
                    return FailureType.LOW_QUALITY_RESPONSE, FailureSeverity.MEDIUM
                elif quality_assessment.value == 'POOR':
                    return FailureType.LOW_QUALITY_RESPONSE, FailureSeverity.LOW
            
            # Check for format issues in code responses
            from .agent_specializations import AgentType
            if agent_type in [AgentType.CODER, AgentType.OPTIMIZER] and not extracted_code:
                response_lower = raw_response.lower()
                if any(keyword in response_lower for keyword in ['code', 'implement', 'function', 'class']):
                    return FailureType.FORMAT_ERROR, FailureSeverity.LOW
            
            # Check context compatibility
            if context and self._is_context_incompatible(response, context):
                return FailureType.CONTEXT_INCOMPATIBLE, FailureSeverity.MEDIUM
        
        return FailureType.UNKNOWN_ERROR, FailureSeverity.LOW
    
    def _is_context_incompatible(self, response: Any, context: Any) -> bool:
        """Check if response is incompatible with execution context."""
        
        user_query = getattr(context, 'user_query', '')
        raw_response = getattr(response, 'raw_response', '')
        
        if not user_query or not raw_response:
            return False
        
        # Check if response addresses the user query
        query_keywords = set(user_query.lower().split())
        response_keywords = set(raw_response.lower().split())
        
        # Calculate keyword overlap
        overlap = len(query_keywords.intersection(response_keywords))
        overlap_ratio = overlap / len(query_keywords) if query_keywords else 0
        
        # If very low overlap, might be incompatible
        if overlap_ratio < 0.1 and len(user_query) > 20:
            return True
        
        # Check for explicit incompatibility indicators
        incompatible_phrases = [
            'out of scope', 'not applicable', 'cannot help', 'not relevant',
            'unrelated', 'different topic', 'not my expertise'
        ]
        
        response_lower = raw_response.lower()
        return any(phrase in response_lower for phrase in incompatible_phrases)
    
    async def _analyze_root_cause(self, failure_event: FailureEvent) -> str:
        """Analyze the root cause of a failure."""
        
        failure_type = failure_event.failure_type
        context = failure_event.context
        
        root_causes = {
            FailureType.API_UNAVAILABLE: "External API service is down or unreachable",
            FailureType.API_TIMEOUT: "Network latency or API response time exceeded limits",
            FailureType.RATE_LIMIT_EXCEEDED: "API request rate exceeded service limits",
            FailureType.COST_LIMIT_EXCEEDED: "Usage costs exceeded configured budget limits",
            FailureType.LOW_QUALITY_RESPONSE: "Agent response did not meet quality thresholds",
            FailureType.INCOMPLETE_RESPONSE: "Agent response was truncated or incomplete",
            FailureType.PARSING_ERROR: "Response format could not be parsed correctly",
            FailureType.FORMAT_ERROR: "Response format did not match expected structure",
            FailureType.CONTEXT_INCOMPATIBLE: "Agent response not relevant to execution context"
        }
        
        base_cause = root_causes.get(failure_type, "Unknown error occurred")
        
        # Add specific context if available
        if context:
            if context.get('quality_score') is not None:
                base_cause += f" (quality: {context['quality_score']:.2f})"
            
            if context.get('iteration_count', 0) > 5:
                base_cause += " - High iteration count may indicate systemic issues"
        
        # Check for recurring patterns
        recent_failures = [f for f in self.failure_history[-10:] 
                          if f.failure_type == failure_type]
        if len(recent_failures) >= 3:
            base_cause += " - Recurring failure pattern detected"
        
        return base_cause
    
    def _suggest_action(self, failure_event: FailureEvent) -> str:
        """Suggest appropriate action for a failure."""
        
        failure_type = failure_event.failure_type
        severity = failure_event.severity
        
        suggestions = {
            FailureType.API_UNAVAILABLE: "Switch to backup API endpoint or alternative agent",
            FailureType.API_TIMEOUT: "Retry with exponential backoff or reduce request complexity",
            FailureType.RATE_LIMIT_EXCEEDED: "Implement request throttling and retry after delay",
            FailureType.COST_LIMIT_EXCEEDED: "Switch to more cost-effective model or abort execution",
            FailureType.LOW_QUALITY_RESPONSE: "Retry with refined prompt or escalate to different agent",
            FailureType.INCOMPLETE_RESPONSE: "Retry with request for completion or use partial result",
            FailureType.PARSING_ERROR: "Retry with format specification or manual parsing",
            FailureType.FORMAT_ERROR: "Retry with explicit format requirements",
            FailureType.CONTEXT_INCOMPATIBLE: "Switch to more appropriate agent type or refine context"
        }
        
        base_suggestion = suggestions.get(failure_type, "Review error and retry if appropriate")
        
        # Adjust suggestion based on severity
        if severity == FailureSeverity.CRITICAL:
            base_suggestion = f"CRITICAL: {base_suggestion} - Consider aborting execution"
        elif severity == FailureSeverity.HIGH:
            base_suggestion = f"HIGH PRIORITY: {base_suggestion}"
        
        # Add retry guidance
        pattern = self.failure_patterns.get(failure_type, {})
        max_retries = pattern.get('max_retries', 1)
        
        if failure_event.retry_count >= max_retries:
            base_suggestion += " - Maximum retries exceeded, escalate to fallback strategy"
        elif max_retries > 0:
            base_suggestion += f" - Retry allowed ({failure_event.retry_count}/{max_retries})"
        
        return base_suggestion
    
    def _track_failure(self, failure_event: FailureEvent):
        """Track failure for pattern analysis."""
        
        # Add to failure history
        self.failure_history.append(failure_event)
        
        # Update agent failure counts
        if failure_event.agent_id:
            self.agent_failure_counts[failure_event.agent_id] = (
                self.agent_failure_counts.get(failure_event.agent_id, 0) + 1
            )
        
        # Keep history manageable
        if len(self.failure_history) > 1000:
            self.failure_history = self.failure_history[-500:]
    
    def get_failure_statistics(self) -> Dict[str, Any]:
        """Get failure statistics and patterns."""
        
        if not self.failure_history:
            return {'total_failures': 0}
        
        # Calculate statistics
        total_failures = len(self.failure_history)
        recent_failures = [f for f in self.failure_history 
                          if f.timestamp > datetime.now() - timedelta(hours=24)]
        
        # Failure type distribution
        type_counts = {}
        for failure in self.failure_history:
            type_counts[failure.failure_type.value] = (
                type_counts.get(failure.failure_type.value, 0) + 1
            )
        
        # Severity distribution
        severity_counts = {}
        for failure in self.failure_history:
            severity_counts[failure.severity.value] = (
                severity_counts.get(failure.severity.value, 0) + 1
            )
        
        # Agent failure rates
        agent_stats = {}
        for agent_id, count in self.agent_failure_counts.items():
            agent_stats[agent_id] = {
                'failure_count': count,
                'recent_failures': len([f for f in recent_failures if f.agent_id == agent_id])
            }
        
        return {
            'total_failures': total_failures,
            'recent_failures_24h': len(recent_failures),
            'failure_types': type_counts,
            'severity_distribution': severity_counts,
            'agent_failure_stats': agent_stats,
            'most_common_failure': max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else None
        }
    
    def is_agent_problematic(self, agent_id: str, threshold: int = 5) -> bool:
        """Check if an agent has excessive failures."""
        return self.agent_failure_counts.get(agent_id, 0) >= threshold
    
    def get_recent_failure_pattern(self, failure_type: FailureType, 
                                  hours: int = 1) -> List[FailureEvent]:
        """Get recent failures of a specific type."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [f for f in self.failure_history 
                if f.failure_type == failure_type and f.timestamp > cutoff_time]
    
    def clear_agent_failures(self, agent_id: str):
        """Clear failure count for an agent (after successful recovery)."""
        if agent_id in self.agent_failure_counts:
            del self.agent_failure_counts[agent_id]
