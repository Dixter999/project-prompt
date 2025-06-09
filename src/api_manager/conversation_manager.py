"""
Conversation Manager - FASE 2 Component
Manages multi-turn conversations and context tracking for complex implementations.
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from uuid import uuid4
import hashlib

@dataclass
class ConversationTurn:
    """Represents a single turn in a conversation"""
    turn_id: str
    timestamp: datetime
    request_type: str  # 'implementation', 'clarification', 'validation', 'follow_up'
    prompt: str
    response: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = False
    error: Optional[str] = None
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    model_used: Optional[str] = None

@dataclass
class ConversationSession:
    """Represents a complete conversation session"""
    session_id: str
    project_path: str
    task_description: str
    task_type: str
    complexity_level: str
    created_at: datetime
    turns: List[ConversationTurn] = field(default_factory=list)
    context_snapshot: Dict[str, Any] = field(default_factory=dict)
    status: str = "active"  # 'active', 'completed', 'failed', 'paused'
    total_cost: float = 0.0
    total_tokens: int = 0
    implementation_plan: Optional[Dict[str, Any]] = None
    completed_phases: List[str] = field(default_factory=list)

class ConversationManager:
    """
    Manages conversation sessions and handles multi-turn API interactions.
    Provides intelligent context tracking and conversation flow management.
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize conversation manager with optional cache directory"""
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / '.project-prompt' / 'conversations'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.active_sessions: Dict[str, ConversationSession] = {}
        self.session_file_pattern = "session_{session_id}.json"
        
        # Load existing sessions
        self._load_existing_sessions()
    
    def create_session(self, 
                      project_path: str,
                      task_description: str, 
                      task_type: str = "implementation",
                      complexity_level: str = "medium",
                      context_snapshot: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new conversation session.
        
        Args:
            project_path: Path to the project being worked on
            task_description: Description of the task to implement
            task_type: Type of task (implementation, debugging, etc.)
            complexity_level: Complexity level (simple, medium, complex, very_complex)
            context_snapshot: Current project context snapshot
            
        Returns:
            session_id: Unique identifier for the session
        """
        session_id = str(uuid4())
        
        session = ConversationSession(
            session_id=session_id,
            project_path=project_path,
            task_description=task_description,
            task_type=task_type,
            complexity_level=complexity_level,
            created_at=datetime.now(),
            context_snapshot=context_snapshot or {}
        )
        
        self.active_sessions[session_id] = session
        self._save_session(session)
        
        return session_id
    
    def add_turn(self,
                session_id: str,
                request_type: str,
                prompt: str,
                metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a new turn to an existing conversation session.
        
        Args:
            session_id: ID of the conversation session
            request_type: Type of request (implementation, clarification, etc.)
            prompt: The prompt being sent
            metadata: Additional metadata for the turn
            
        Returns:
            turn_id: Unique identifier for the turn
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        turn_id = str(uuid4())
        
        turn = ConversationTurn(
            turn_id=turn_id,
            timestamp=datetime.now(),
            request_type=request_type,
            prompt=prompt,
            metadata=metadata or {}
        )
        
        session.turns.append(turn)
        self._save_session(session)
        
        return turn_id
    
    def complete_turn(self,
                     session_id: str,
                     turn_id: str,
                     response: str,
                     success: bool = True,
                     error: Optional[str] = None,
                     tokens_used: Optional[int] = None,
                     cost: Optional[float] = None,
                     model_used: Optional[str] = None) -> None:
        """
        Complete a conversation turn with the API response.
        
        Args:
            session_id: ID of the conversation session
            turn_id: ID of the turn to complete
            response: API response content
            success: Whether the request was successful
            error: Error message if request failed
            tokens_used: Number of tokens used in the request
            cost: Cost of the API request
            model_used: Model used for the request
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        # Find the turn
        turn = None
        for t in session.turns:
            if t.turn_id == turn_id:
                turn = t
                break
        
        if not turn:
            raise ValueError(f"Turn {turn_id} not found in session {session_id}")
        
        # Update turn with response
        turn.response = response
        turn.success = success
        turn.error = error
        turn.tokens_used = tokens_used or 0
        turn.cost = cost or 0.0
        turn.model_used = model_used
        
        # Update session totals
        session.total_tokens += turn.tokens_used
        session.total_cost += turn.cost
        
        self._save_session(session)
    
    def get_conversation_context(self, session_id: str, max_turns: int = 5) -> str:
        """
        Get formatted conversation context for the API.
        
        Args:
            session_id: ID of the conversation session
            max_turns: Maximum number of recent turns to include
            
        Returns:
            Formatted conversation context string
        """
        if session_id not in self.active_sessions:
            return ""
        
        session = self.active_sessions[session_id]
        recent_turns = session.turns[-max_turns:] if session.turns else []
        
        context_parts = [
            f"# Conversation Context",
            f"**Task**: {session.task_description}",
            f"**Type**: {session.task_type}",
            f"**Complexity**: {session.complexity_level}",
            f"**Started**: {session.created_at.strftime('%Y-%m-%d %H:%M')}",
            f"**Total Turns**: {len(session.turns)}",
            ""
        ]
        
        if recent_turns:
            context_parts.append("## Recent Conversation:")
            for i, turn in enumerate(recent_turns):
                context_parts.append(f"### Turn {i+1} ({turn.request_type})")
                context_parts.append(f"**Request**: {turn.prompt[:200]}...")
                if turn.response:
                    context_parts.append(f"**Response**: {turn.response[:200]}...")
                context_parts.append("")
        
        if session.completed_phases:
            context_parts.append("## Completed Phases:")
            for phase in session.completed_phases:
                context_parts.append(f"- {phase}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def analyze_conversation_flow(self, session_id: str) -> Dict[str, Any]:
        """
        Analyze conversation flow and provide insights.
        
        Args:
            session_id: ID of the conversation session
            
        Returns:
            Analysis results with insights and recommendations
        """
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        
        # Calculate metrics
        total_turns = len(session.turns)
        successful_turns = sum(1 for turn in session.turns if turn.success)
        failed_turns = total_turns - successful_turns
        
        # Analyze turn types
        turn_types = {}
        for turn in session.turns:
            turn_types[turn.request_type] = turn_types.get(turn.request_type, 0) + 1
        
        # Calculate average response time (if available)
        response_times = []
        for i in range(1, len(session.turns)):
            prev_turn = session.turns[i-1]
            curr_turn = session.turns[i]
            if prev_turn.timestamp and curr_turn.timestamp:
                delta = (curr_turn.timestamp - prev_turn.timestamp).total_seconds()
                response_times.append(delta)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Identify conversation patterns
        patterns = self._identify_patterns(session)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(session, patterns)
        
        return {
            "session_id": session_id,
            "duration": (datetime.now() - session.created_at).total_seconds() / 3600,  # hours
            "total_turns": total_turns,
            "successful_turns": successful_turns,
            "failed_turns": failed_turns,
            "success_rate": successful_turns / total_turns if total_turns > 0 else 0,
            "turn_types": turn_types,
            "total_cost": session.total_cost,
            "total_tokens": session.total_tokens,
            "avg_response_time": avg_response_time,
            "patterns": patterns,
            "recommendations": recommendations,
            "status": session.status
        }
    
    def suggest_next_action(self, session_id: str) -> Dict[str, Any]:
        """
        Suggest the next action based on conversation history.
        
        Args:
            session_id: ID of the conversation session
            
        Returns:
            Suggested next action with reasoning
        """
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        
        if not session.turns:
            return {
                "action": "start_implementation",
                "reason": "No previous turns found. Start with initial implementation request.",
                "suggested_request_type": "implementation"
            }
        
        last_turn = session.turns[-1]
        
        # Analyze last turn result
        if not last_turn.success:
            return {
                "action": "retry_with_clarification",
                "reason": f"Last turn failed: {last_turn.error}. Retry with more context.",
                "suggested_request_type": "clarification"
            }
        
        # Check if implementation is complete
        if last_turn.request_type == "validation" and last_turn.success:
            return {
                "action": "complete_session",
                "reason": "Validation successful. Implementation appears complete.",
                "suggested_request_type": None
            }
        
        # Suggest next logical step
        next_steps = {
            "implementation": "validation",
            "clarification": "implementation", 
            "debugging": "validation",
            "optimization": "validation",
            "testing": "validation"
        }
        
        suggested_next = next_steps.get(last_turn.request_type, "follow_up")
        
        return {
            "action": f"continue_with_{suggested_next}",
            "reason": f"Last turn was {last_turn.request_type}. Logical next step is {suggested_next}.",
            "suggested_request_type": suggested_next
        }
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a comprehensive summary of the conversation session"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        
        return {
            "session_id": session_id,
            "task_description": session.task_description,
            "task_type": session.task_type,
            "complexity_level": session.complexity_level,
            "status": session.status,
            "created_at": session.created_at.isoformat(),
            "duration_hours": (datetime.now() - session.created_at).total_seconds() / 3600,
            "total_turns": len(session.turns),
            "total_cost": session.total_cost,
            "total_tokens": session.total_tokens,
            "completed_phases": session.completed_phases,
            "latest_turn": {
                "request_type": session.turns[-1].request_type if session.turns else None,
                "timestamp": session.turns[-1].timestamp.isoformat() if session.turns else None,
                "success": session.turns[-1].success if session.turns else None
            } if session.turns else None
        }
    
    def close_session(self, session_id: str, status: str = "completed") -> bool:
        """
        Close a conversation session.
        
        Args:
            session_id: ID of the session to close
            status: Final status ('completed', 'failed', 'cancelled')
            
        Returns:
            True if session was closed successfully
        """
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        session.status = status
        
        self._save_session(session)
        
        # Remove from active sessions but keep in cache
        del self.active_sessions[session_id]
        
        return True
    
    def list_sessions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List conversation sessions with optional status filter.
        
        Args:
            status: Optional status filter ('active', 'completed', 'failed')
            
        Returns:
            List of session summaries
        """
        sessions = []
        
        # Include active sessions
        for session in self.active_sessions.values():
            if status is None or session.status == status:
                sessions.append(self.get_session_summary(session.session_id))
        
        # Load and include cached sessions
        for session_file in self.cache_dir.glob("session_*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                session_id = session_data.get('session_id')
                if session_id not in self.active_sessions:  # Avoid duplicates
                    session_status = session_data.get('status', 'unknown')
                    if status is None or session_status == status:
                        sessions.append({
                            "session_id": session_id,
                            "task_description": session_data.get('task_description', ''),
                            "task_type": session_data.get('task_type', ''),
                            "status": session_status,
                            "created_at": session_data.get('created_at', ''),
                            "total_turns": len(session_data.get('turns', [])),
                            "total_cost": session_data.get('total_cost', 0),
                            "is_cached": True
                        })
                        
            except (json.JSONDecodeError, IOError):
                continue
        
        return sorted(sessions, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """
        Clean up old conversation sessions.
        
        Args:
            days_old: Delete sessions older than this many days
            
        Returns:
            Number of sessions cleaned up
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cleaned_count = 0
        
        for session_file in self.cache_dir.glob("session_*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                created_at_str = session_data.get('created_at', '')
                if created_at_str:
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    if created_at < cutoff_date:
                        session_file.unlink()
                        cleaned_count += 1
                        
            except (json.JSONDecodeError, IOError, ValueError):
                continue
        
        return cleaned_count
    
    # Private methods
    
    def _save_session(self, session: ConversationSession) -> None:
        """Save session to cache file"""
        session_file = self.cache_dir / self.session_file_pattern.format(session_id=session.session_id)
        
        # Convert session to dict for JSON serialization
        session_dict = {
            "session_id": session.session_id,
            "project_path": session.project_path,
            "task_description": session.task_description,
            "task_type": session.task_type,
            "complexity_level": session.complexity_level,
            "created_at": session.created_at.isoformat(),
            "status": session.status,
            "total_cost": session.total_cost,
            "total_tokens": session.total_tokens,
            "context_snapshot": session.context_snapshot,
            "implementation_plan": session.implementation_plan,
            "completed_phases": session.completed_phases,
            "turns": [
                {
                    "turn_id": turn.turn_id,
                    "timestamp": turn.timestamp.isoformat(),
                    "request_type": turn.request_type,
                    "prompt": turn.prompt,
                    "response": turn.response,
                    "metadata": turn.metadata,
                    "success": turn.success,
                    "error": turn.error,
                    "tokens_used": turn.tokens_used,
                    "cost": turn.cost,
                    "model_used": turn.model_used
                }
                for turn in session.turns
            ]
        }
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_dict, f, indent=2, ensure_ascii=False)
    
    def _load_existing_sessions(self) -> None:
        """Load existing active sessions from cache"""
        for session_file in self.cache_dir.glob("session_*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                # Only load active sessions
                if session_data.get('status') == 'active':
                    session = self._dict_to_session(session_data)
                    self.active_sessions[session.session_id] = session
                    
            except (json.JSONDecodeError, IOError):
                continue
    
    def _dict_to_session(self, session_dict: Dict[str, Any]) -> ConversationSession:
        """Convert dictionary to ConversationSession object"""
        turns = []
        for turn_data in session_dict.get('turns', []):
            turn = ConversationTurn(
                turn_id=turn_data['turn_id'],
                timestamp=datetime.fromisoformat(turn_data['timestamp']),
                request_type=turn_data['request_type'],
                prompt=turn_data['prompt'],
                response=turn_data.get('response'),
                metadata=turn_data.get('metadata', {}),
                success=turn_data.get('success', False),
                error=turn_data.get('error'),
                tokens_used=turn_data.get('tokens_used'),
                cost=turn_data.get('cost'),
                model_used=turn_data.get('model_used')
            )
            turns.append(turn)
        
        session = ConversationSession(
            session_id=session_dict['session_id'],
            project_path=session_dict['project_path'],
            task_description=session_dict['task_description'],
            task_type=session_dict['task_type'],
            complexity_level=session_dict['complexity_level'],
            created_at=datetime.fromisoformat(session_dict['created_at']),
            turns=turns,
            context_snapshot=session_dict.get('context_snapshot', {}),
            status=session_dict.get('status', 'active'),
            total_cost=session_dict.get('total_cost', 0.0),
            total_tokens=session_dict.get('total_tokens', 0),
            implementation_plan=session_dict.get('implementation_plan'),
            completed_phases=session_dict.get('completed_phases', [])
        )
        
        return session
    
    def _identify_patterns(self, session: ConversationSession) -> List[str]:
        """Identify patterns in conversation flow"""
        patterns = []
        
        if len(session.turns) < 2:
            return patterns
        
        # Check for retry patterns
        retry_count = 0
        for i in range(1, len(session.turns)):
            if not session.turns[i-1].success and session.turns[i].request_type == session.turns[i-1].request_type:
                retry_count += 1
        
        if retry_count > 2:
            patterns.append("high_retry_rate")
        
        # Check for clarification requests
        clarification_count = sum(1 for turn in session.turns if turn.request_type == "clarification")
        if clarification_count > len(session.turns) * 0.3:
            patterns.append("frequent_clarifications")
        
        # Check for long conversation
        if len(session.turns) > 10:
            patterns.append("extended_conversation")
        
        # Check for cost efficiency
        if session.total_cost > 1.0:  # $1 threshold
            patterns.append("high_cost_session")
        
        return patterns
    
    def _generate_recommendations(self, session: ConversationSession, patterns: List[str]) -> List[str]:
        """Generate recommendations based on session analysis"""
        recommendations = []
        
        if "high_retry_rate" in patterns:
            recommendations.append("Consider breaking down the task into smaller, more specific requests")
        
        if "frequent_clarifications" in patterns:
            recommendations.append("Provide more detailed initial context and requirements")
        
        if "extended_conversation" in patterns:
            recommendations.append("Consider creating a new session for follow-up tasks")
        
        if "high_cost_session" in patterns:
            recommendations.append("Review optimization settings to reduce API costs")
        
        if session.total_tokens > 50000:
            recommendations.append("Monitor token usage to optimize conversation efficiency")
        
        # Task-specific recommendations
        if session.task_type == "debugging" and len(session.turns) > 5:
            recommendations.append("Consider providing more debugging context upfront")
        
        if session.complexity_level == "very_complex" and not recommendations:
            recommendations.append("Complex tasks are progressing well - maintain current approach")
        
        return recommendations
