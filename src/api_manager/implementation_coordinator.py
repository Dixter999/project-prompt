"""
Implementation Coordinator - FASE 2 Component
Coordinates multiple API requests and manages complex implementation workflows.
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum
import json
import logging

from .conversation_manager import ConversationManager, ConversationSession
from .response_processor import ResponseProcessor, ProcessedResponse
from .anthropic_client import AnthropicClient
from .request_optimizer import RequestOptimizer

class WorkflowStatus(Enum):
    """Status of implementation workflow"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class RequestPriority(Enum):
    """Priority levels for API requests"""
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class ImplementationRequest:
    """Represents a single implementation request in a workflow"""
    request_id: str
    session_id: str
    prompt: str
    request_type: str  # 'implementation', 'clarification', 'validation', 'debugging'
    priority: RequestPriority
    dependencies: List[str] = field(default_factory=list)  # IDs of requests that must complete first
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    # Status tracking
    status: WorkflowStatus = WorkflowStatus.PENDING
    assigned_turn_id: Optional[str] = None
    processed_response: Optional[ProcessedResponse] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # Performance tracking
    request_time: Optional[datetime] = None
    response_time: Optional[datetime] = None
    processing_duration: Optional[float] = None
    cost: Optional[float] = None

@dataclass
class ImplementationWorkflow:
    """Represents a complete implementation workflow"""
    workflow_id: str
    project_path: str
    task_description: str
    complexity_level: str
    target_optimization: str
    
    # Request management
    requests: List[ImplementationRequest] = field(default_factory=list)
    completed_requests: List[str] = field(default_factory=list)
    failed_requests: List[str] = field(default_factory=list)
    
    # Status and timing
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Performance metrics
    total_cost: float = 0.0
    total_requests: int = 0
    successful_requests: int = 0
    average_response_time: float = 0.0
    
    # Session and context
    conversation_session_id: Optional[str] = None
    context_snapshot: Dict[str, Any] = field(default_factory=dict)
    final_implementation_plan: Optional[Dict[str, Any]] = None

class ImplementationCoordinator:
    """
    Coordinates complex implementation workflows with multiple API requests.
    Manages request dependencies, error handling, and workflow optimization.
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 conversation_manager: Optional[ConversationManager] = None,
                 response_processor: Optional[ResponseProcessor] = None,
                 cache_dir: Optional[str] = None):
        """
        Initialize the implementation coordinator.
        
        Args:
            api_key: Optional Anthropic API key
            conversation_manager: Optional ConversationManager instance
            response_processor: Optional ResponseProcessor instance  
            cache_dir: Optional cache directory for workflows
        """
        self.api_client = AnthropicClient(api_key=api_key)
        self.conversation_manager = conversation_manager or ConversationManager(cache_dir)
        self.response_processor = response_processor or ResponseProcessor()
        self.request_optimizer = RequestOptimizer()
        
        # Workflow management
        self.active_workflows: Dict[str, ImplementationWorkflow] = {}
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / '.project-prompt' / 'workflows'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Performance tracking
        self.performance_metrics = {
            'total_workflows': 0,
            'successful_workflows': 0,
            'failed_workflows': 0,
            'average_workflow_duration': 0.0,
            'total_api_cost': 0.0,
            'cache_hit_rate': 0.0
        }
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def create_workflow(self,
                       project_path: str,
                       task_description: str,
                       complexity_level: str = "medium",
                       target_optimization: str = "balanced",
                       context_snapshot: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new implementation workflow.
        
        Args:
            project_path: Path to the project
            task_description: Description of the implementation task
            complexity_level: Complexity level (simple, medium, complex, very_complex)
            target_optimization: Optimization target (speed, cost, quality, balanced)
            context_snapshot: Project context snapshot
            
        Returns:
            workflow_id: Unique identifier for the workflow
        """
        import uuid
        workflow_id = str(uuid.uuid4())
        
        # Create conversation session
        session_id = self.conversation_manager.create_session(
            project_path=project_path,
            task_description=task_description,
            task_type="implementation",
            complexity_level=complexity_level,
            context_snapshot=context_snapshot
        )
        
        workflow = ImplementationWorkflow(
            workflow_id=workflow_id,
            project_path=project_path,
            task_description=task_description,
            complexity_level=complexity_level,
            target_optimization=target_optimization,
            conversation_session_id=session_id,
            context_snapshot=context_snapshot or {}
        )
        
        self.active_workflows[workflow_id] = workflow
        self._save_workflow(workflow)
        
        self.logger.info(f"Created workflow {workflow_id} for task: {task_description}")
        return workflow_id
    
    def add_request(self,
                   workflow_id: str,
                   prompt: str,
                   request_type: str = "implementation",
                   priority: RequestPriority = RequestPriority.MEDIUM,
                   dependencies: Optional[List[str]] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a request to an existing workflow.
        
        Args:
            workflow_id: ID of the workflow to add to
            prompt: The prompt/request text
            request_type: Type of request (implementation, clarification, etc.)
            priority: Priority level for the request
            dependencies: List of request IDs that must complete first
            metadata: Additional metadata for the request
            
        Returns:
            request_id: Unique identifier for the request
        """
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.active_workflows[workflow_id]
        
        import uuid
        request_id = str(uuid.uuid4())
        
        request = ImplementationRequest(
            request_id=request_id,
            session_id=workflow.conversation_session_id,
            prompt=prompt,
            request_type=request_type,
            priority=priority,
            dependencies=dependencies or [],
            metadata=metadata or {}
        )
        
        workflow.requests.append(request)
        self._save_workflow(workflow)
        
        self.logger.info(f"Added request {request_id} to workflow {workflow_id}")
        return request_id
    
    def execute_workflow(self,
                        workflow_id: str,
                        max_concurrent_requests: int = 3,
                        request_delay: float = 1.0,
                        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict[str, Any]:
        """
        Execute a complete implementation workflow.
        
        Args:
            workflow_id: ID of the workflow to execute
            max_concurrent_requests: Maximum number of concurrent API requests
            request_delay: Delay between requests in seconds
            progress_callback: Optional callback for progress updates
            
        Returns:
            Execution results with performance metrics
        """
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.active_workflows[workflow_id]
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now()
        
        self.logger.info(f"Starting execution of workflow {workflow_id}")
        
        try:
            # Plan execution order based on dependencies
            execution_plan = self._plan_execution_order(workflow)
            
            # Execute requests in planned order
            results = self._execute_requests(
                workflow,
                execution_plan,
                max_concurrent_requests,
                request_delay,
                progress_callback
            )
            
            # Finalize workflow
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            
            # Generate final implementation plan
            workflow.final_implementation_plan = self._generate_final_plan(workflow)
            
            self._update_performance_metrics(workflow)
            self._save_workflow(workflow)
            
            self.logger.info(f"Completed workflow {workflow_id} successfully")
            
            return {
                'workflow_id': workflow_id,
                'status': 'completed',
                'total_requests': len(workflow.requests),
                'successful_requests': workflow.successful_requests,
                'failed_requests': len(workflow.failed_requests),
                'total_cost': workflow.total_cost,
                'duration': (workflow.completed_at - workflow.started_at).total_seconds(),
                'implementation_plan': workflow.final_implementation_plan,
                'results': results
            }
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = datetime.now()
            self._save_workflow(workflow)
            
            self.logger.error(f"Workflow {workflow_id} failed: {str(e)}")
            
            return {
                'workflow_id': workflow_id,
                'status': 'failed',
                'error': str(e),
                'partial_results': getattr(e, 'partial_results', [])
            }
    
    def pause_workflow(self, workflow_id: str) -> bool:
        """Pause an active workflow"""
        if workflow_id not in self.active_workflows:
            return False
        
        workflow = self.active_workflows[workflow_id]
        if workflow.status == WorkflowStatus.RUNNING:
            workflow.status = WorkflowStatus.PAUSED
            self._save_workflow(workflow)
            self.logger.info(f"Paused workflow {workflow_id}")
            return True
        
        return False
    
    def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow"""
        if workflow_id not in self.active_workflows:
            return False
        
        workflow = self.active_workflows[workflow_id]
        if workflow.status == WorkflowStatus.PAUSED:
            workflow.status = WorkflowStatus.RUNNING
            self._save_workflow(workflow)
            self.logger.info(f"Resumed workflow {workflow_id}")
            return True
        
        return False
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a workflow"""
        if workflow_id not in self.active_workflows:
            return False
        
        workflow = self.active_workflows[workflow_id]
        workflow.status = WorkflowStatus.CANCELLED
        workflow.completed_at = datetime.now()
        self._save_workflow(workflow)
        
        self.logger.info(f"Cancelled workflow {workflow_id}")
        return True
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get detailed status of a workflow"""
        if workflow_id not in self.active_workflows:
            return {"error": "Workflow not found"}
        
        workflow = self.active_workflows[workflow_id]
        
        # Calculate progress
        total_requests = len(workflow.requests)
        completed_requests = len(workflow.completed_requests)
        progress_percent = (completed_requests / total_requests * 100) if total_requests > 0 else 0
        
        # Calculate estimated remaining time
        if workflow.started_at and completed_requests > 0:
            elapsed_time = (datetime.now() - workflow.started_at).total_seconds()
            avg_time_per_request = elapsed_time / completed_requests
            remaining_requests = total_requests - completed_requests
            estimated_remaining = avg_time_per_request * remaining_requests
        else:
            estimated_remaining = None
        
        return {
            'workflow_id': workflow_id,
            'status': workflow.status.value,
            'progress': {
                'total_requests': total_requests,
                'completed_requests': completed_requests,
                'failed_requests': len(workflow.failed_requests),
                'progress_percent': progress_percent,
                'estimated_remaining_seconds': estimated_remaining
            },
            'performance': {
                'total_cost': workflow.total_cost,
                'successful_requests': workflow.successful_requests,
                'average_response_time': workflow.average_response_time
            },
            'timing': {
                'created_at': workflow.created_at.isoformat(),
                'started_at': workflow.started_at.isoformat() if workflow.started_at else None,
                'completed_at': workflow.completed_at.isoformat() if workflow.completed_at else None
            }
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary of the coordinator"""
        return {
            'coordinator_metrics': self.performance_metrics,
            'api_client_metrics': self.api_client.get_performance_metrics(),
            'conversation_analytics': self._get_conversation_analytics(),
            'active_workflows': len(self.active_workflows),
            'cache_statistics': self._get_cache_statistics()
        }
    
    def optimize_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Optimize a workflow for better performance"""
        if workflow_id not in self.active_workflows:
            return {"error": "Workflow not found"}
        
        workflow = self.active_workflows[workflow_id]
        
        optimization_suggestions = []
        
        # Analyze request patterns
        request_types = {}
        for request in workflow.requests:
            request_types[request.request_type] = request_types.get(request.request_type, 0) + 1
        
        # Suggest batching similar requests
        if request_types.get('clarification', 0) > 3:
            optimization_suggestions.append({
                'type': 'batch_clarifications',
                'description': 'Batch multiple clarification requests to reduce API calls',
                'potential_savings': '20-30% cost reduction'
            })
        
        # Suggest priority reordering
        high_priority_count = sum(1 for req in workflow.requests if req.priority == RequestPriority.HIGH)
        if high_priority_count > len(workflow.requests) * 0.7:
            optimization_suggestions.append({
                'type': 'rebalance_priorities',
                'description': 'Too many high-priority requests - consider rebalancing',
                'potential_savings': '10-15% time reduction'
            })
        
        # Suggest dependency optimization
        circular_deps = self._detect_circular_dependencies(workflow)
        if circular_deps:
            optimization_suggestions.append({
                'type': 'fix_dependencies',
                'description': 'Circular dependencies detected - needs manual review',
                'affected_requests': circular_deps
            })
        
        return {
            'workflow_id': workflow_id,
            'current_efficiency': self._calculate_workflow_efficiency(workflow),
            'optimization_suggestions': optimization_suggestions,
            'estimated_improvements': {
                'cost_reduction': '15-25%',
                'time_reduction': '10-20%',
                'success_rate_improvement': '5-10%'
            }
        }
    
    # Private methods
    
    def _plan_execution_order(self, workflow: ImplementationWorkflow) -> List[List[str]]:
        """Plan execution order respecting dependencies"""
        # Topological sort considering dependencies
        remaining_requests = {req.request_id: req for req in workflow.requests}
        execution_batches = []
        
        while remaining_requests:
            # Find requests with no unmet dependencies
            ready_requests = []
            for request_id, request in remaining_requests.items():
                unmet_deps = [dep for dep in request.dependencies if dep in remaining_requests]
                if not unmet_deps:
                    ready_requests.append(request_id)
            
            if not ready_requests:
                # Circular dependency detected
                self.logger.warning(f"Circular dependency detected in workflow {workflow.workflow_id}")
                # Break the cycle by taking the highest priority request
                priority_request = max(
                    remaining_requests.values(),
                    key=lambda r: r.priority.value
                )
                ready_requests = [priority_request.request_id]
            
            # Sort by priority within the batch
            ready_requests.sort(
                key=lambda rid: remaining_requests[rid].priority.value,
                reverse=True
            )
            
            execution_batches.append(ready_requests)
            
            # Remove ready requests from remaining
            for request_id in ready_requests:
                del remaining_requests[request_id]
        
        return execution_batches
    
    def _execute_requests(self,
                         workflow: ImplementationWorkflow,
                         execution_plan: List[List[str]],
                         max_concurrent: int,
                         delay: float,
                         progress_callback: Optional[Callable]) -> List[Dict[str, Any]]:
        """Execute requests according to the execution plan"""
        all_results = []
        
        for batch_num, batch in enumerate(execution_plan):
            self.logger.info(f"Executing batch {batch_num + 1}/{len(execution_plan)} with {len(batch)} requests")
            
            # Process batch with concurrency limit
            batch_results = []
            for i in range(0, len(batch), max_concurrent):
                concurrent_batch = batch[i:i + max_concurrent]
                
                # Execute concurrent requests
                for request_id in concurrent_batch:
                    result = self._execute_single_request(workflow, request_id)
                    batch_results.append(result)
                    
                    # Call progress callback if provided
                    if progress_callback:
                        progress_callback({
                            'workflow_id': workflow.workflow_id,
                            'completed_requests': len(workflow.completed_requests),
                            'total_requests': len(workflow.requests),
                            'current_request_id': request_id,
                            'current_batch': batch_num + 1,
                            'total_batches': len(execution_plan)
                        })
                    
                    # Delay between requests
                    if delay > 0:
                        time.sleep(delay)
            
            all_results.extend(batch_results)
        
        return all_results
    
    def _execute_single_request(self, workflow: ImplementationWorkflow, request_id: str) -> Dict[str, Any]:
        """Execute a single request within a workflow"""
        # Find the request
        request = None
        for req in workflow.requests:
            if req.request_id == request_id:
                request = req
                break
        
        if not request:
            return {'request_id': request_id, 'error': 'Request not found'}
        
        try:
            request.status = WorkflowStatus.RUNNING
            request.request_time = datetime.now()
            
            # Add turn to conversation
            turn_id = self.conversation_manager.add_turn(
                session_id=request.session_id,
                request_type=request.request_type,
                prompt=request.prompt,
                metadata=request.metadata
            )
            request.assigned_turn_id = turn_id
            
            # Get conversation context
            context = self.conversation_manager.get_conversation_context(request.session_id)
            
            # Optimize request
            optimized_config = self.request_optimizer.optimize_request_strategy(
                enriched_config={
                    'prompt': f"{context}\n\n{request.prompt}",
                    'task_type': request.request_type,
                    'complexity_level': workflow.complexity_level
                },
                context=workflow.context_snapshot,
                performance_target=workflow.target_optimization
            )
            
            # Send API request
            api_response = self.api_client.send_enriched_request(optimized_config)
            
            request.response_time = datetime.now()
            request.processing_duration = (request.response_time - request.request_time).total_seconds()
            request.cost = api_response.get('cost', 0.0)
            
            # Process response
            processed = self.response_processor.process_response(
                response=api_response['content'],
                context=workflow.context_snapshot
            )
            
            request.processed_response = processed
            request.status = WorkflowStatus.COMPLETED
            
            # Complete conversation turn
            self.conversation_manager.complete_turn(
                session_id=request.session_id,
                turn_id=turn_id,
                response=api_response['content'],
                success=True,
                tokens_used=api_response.get('usage', {}).get('total_tokens', 0),
                cost=request.cost,
                model_used=api_response.get('model')
            )
            
            # Update workflow metrics
            workflow.completed_requests.append(request_id)
            workflow.successful_requests += 1
            workflow.total_cost += request.cost
            workflow.total_requests += 1
            
            # Update average response time
            total_duration = sum(
                req.processing_duration for req in workflow.requests 
                if req.processing_duration is not None
            )
            completed_count = len([req for req in workflow.requests if req.status == WorkflowStatus.COMPLETED])
            workflow.average_response_time = total_duration / completed_count if completed_count > 0 else 0
            
            self.logger.info(f"Successfully executed request {request_id}")
            
            return {
                'request_id': request_id,
                'status': 'completed',
                'processed_response': processed,
                'cost': request.cost,
                'duration': request.processing_duration
            }
            
        except Exception as e:
            request.status = WorkflowStatus.FAILED
            request.error = str(e)
            request.retry_count += 1
            
            workflow.failed_requests.append(request_id)
            
            # Complete conversation turn with error
            if request.assigned_turn_id:
                self.conversation_manager.complete_turn(
                    session_id=request.session_id,
                    turn_id=request.assigned_turn_id,
                    response="",
                    success=False,
                    error=str(e)
                )
            
            self.logger.error(f"Failed to execute request {request_id}: {str(e)}")
            
            # Retry logic
            if request.retry_count < request.max_retries:
                self.logger.info(f"Retrying request {request_id} (attempt {request.retry_count + 1})")
                time.sleep(2 ** request.retry_count)  # Exponential backoff
                return self._execute_single_request(workflow, request_id)
            
            return {
                'request_id': request_id,
                'status': 'failed',
                'error': str(e),
                'retry_count': request.retry_count
            }
    
    def _generate_final_plan(self, workflow: ImplementationWorkflow) -> Dict[str, Any]:
        """Generate final implementation plan from all successful responses"""
        plan = {
            'workflow_id': workflow.workflow_id,
            'task_description': workflow.task_description,
            'total_phases': 0,
            'phases': [],
            'all_file_modifications': [],
            'all_commands': [],
            'all_dependencies': [],
            'validation_steps': [],
            'estimated_total_time': '1-3 hours',
            'complexity_assessment': workflow.complexity_level,
            'success_rate': workflow.successful_requests / len(workflow.requests) if workflow.requests else 0
        }
        
        # Aggregate successful responses
        successful_responses = [
            req.processed_response for req in workflow.requests
            if req.status == WorkflowStatus.COMPLETED and req.processed_response
        ]
        
        phase_counter = 0
        for response in successful_responses:
            if response.implementation_plan:
                for phase in response.implementation_plan.get('phases', []):
                    phase_counter += 1
                    phase['phase'] = phase_counter
                    plan['phases'].append(phase)
            
            plan['all_file_modifications'].extend(response.file_modifications)
            plan['all_commands'].extend(response.commands_to_run)
            plan['all_dependencies'].extend(response.dependencies_to_install)
            plan['validation_steps'].extend(response.validation_steps)
        
        plan['total_phases'] = phase_counter
        
        # Remove duplicates
        plan['all_dependencies'] = list(set(plan['all_dependencies']))
        
        return plan
    
    def _calculate_workflow_efficiency(self, workflow: ImplementationWorkflow) -> float:
        """Calculate efficiency score for a workflow"""
        if not workflow.requests:
            return 0.0
        
        # Factor in success rate
        success_rate = workflow.successful_requests / len(workflow.requests)
        
        # Factor in cost efficiency (requests per dollar)
        cost_efficiency = len(workflow.requests) / max(workflow.total_cost, 0.01)
        cost_score = min(1.0, cost_efficiency / 10)  # Normalize to 0-1
        
        # Factor in time efficiency
        if workflow.average_response_time > 0:
            time_efficiency = min(1.0, 30 / workflow.average_response_time)  # 30s is ideal
        else:
            time_efficiency = 0.5
        
        # Factor in retry rate (lower is better)
        total_retries = sum(req.retry_count for req in workflow.requests)
        retry_rate = total_retries / len(workflow.requests)
        retry_score = max(0.0, 1.0 - retry_rate / 3)  # 3 retries = 0 score
        
        # Weighted combination
        efficiency = (
            success_rate * 0.4 +
            cost_score * 0.2 +
            time_efficiency * 0.2 +
            retry_score * 0.2
        )
        
        return efficiency
    
    def _detect_circular_dependencies(self, workflow: ImplementationWorkflow) -> List[str]:
        """Detect circular dependencies in workflow requests"""
        # Build dependency graph
        graph = {}
        for req in workflow.requests:
            graph[req.request_id] = req.dependencies
        
        # Use DFS to detect cycles
        visited = set()
        rec_stack = set()
        circular_deps = []
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        circular_deps.append(neighbor)
                        return True
                elif neighbor in rec_stack:
                    circular_deps.append(neighbor)
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                dfs(node)
        
        return circular_deps
    
    def _save_workflow(self, workflow: ImplementationWorkflow) -> None:
        """Save workflow to cache"""
        workflow_file = self.cache_dir / f"workflow_{workflow.workflow_id}.json"
        
        # Convert to serializable format
        workflow_dict = {
            'workflow_id': workflow.workflow_id,
            'project_path': workflow.project_path,
            'task_description': workflow.task_description,
            'complexity_level': workflow.complexity_level,
            'target_optimization': workflow.target_optimization,
            'status': workflow.status.value,
            'created_at': workflow.created_at.isoformat(),
            'started_at': workflow.started_at.isoformat() if workflow.started_at else None,
            'completed_at': workflow.completed_at.isoformat() if workflow.completed_at else None,
            'conversation_session_id': workflow.conversation_session_id,
            'context_snapshot': workflow.context_snapshot,
            'total_cost': workflow.total_cost,
            'total_requests': workflow.total_requests,
            'successful_requests': workflow.successful_requests,
            'average_response_time': workflow.average_response_time,
            'completed_requests': workflow.completed_requests,
            'failed_requests': workflow.failed_requests,
            'final_implementation_plan': workflow.final_implementation_plan,
            'requests': [
                {
                    'request_id': req.request_id,
                    'session_id': req.session_id,
                    'prompt': req.prompt,
                    'request_type': req.request_type,
                    'priority': req.priority.value,
                    'dependencies': req.dependencies,
                    'metadata': req.metadata,
                    'created_at': req.created_at.isoformat(),
                    'status': req.status.value,
                    'assigned_turn_id': req.assigned_turn_id,
                    'error': req.error,
                    'retry_count': req.retry_count,
                    'max_retries': req.max_retries,
                    'request_time': req.request_time.isoformat() if req.request_time else None,
                    'response_time': req.response_time.isoformat() if req.response_time else None,
                    'processing_duration': req.processing_duration,
                    'cost': req.cost
                }
                for req in workflow.requests
            ]
        }
        
        with open(workflow_file, 'w', encoding='utf-8') as f:
            json.dump(workflow_dict, f, indent=2, ensure_ascii=False)
    
    def _update_performance_metrics(self, workflow: ImplementationWorkflow) -> None:
        """Update coordinator performance metrics"""
        self.performance_metrics['total_workflows'] += 1
        
        if workflow.status == WorkflowStatus.COMPLETED:
            self.performance_metrics['successful_workflows'] += 1
        elif workflow.status == WorkflowStatus.FAILED:
            self.performance_metrics['failed_workflows'] += 1
        
        # Update average duration
        if workflow.started_at and workflow.completed_at:
            duration = (workflow.completed_at - workflow.started_at).total_seconds()
            total_duration = (
                self.performance_metrics['average_workflow_duration'] * 
                (self.performance_metrics['total_workflows'] - 1) + duration
            )
            self.performance_metrics['average_workflow_duration'] = (
                total_duration / self.performance_metrics['total_workflows']
            )
        
        self.performance_metrics['total_api_cost'] += workflow.total_cost
    
    def _get_conversation_analytics(self) -> Dict[str, Any]:
        """Get analytics from conversation manager"""
        sessions = self.conversation_manager.list_sessions()
        
        if not sessions:
            return {'total_sessions': 0}
        
        total_sessions = len(sessions)
        active_sessions = len([s for s in sessions if s.get('status') == 'active'])
        total_turns = sum(s.get('total_turns', 0) for s in sessions)
        total_cost = sum(s.get('total_cost', 0) for s in sessions)
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'average_turns_per_session': total_turns / total_sessions if total_sessions > 0 else 0,
            'total_conversation_cost': total_cost
        }
    
    def _get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        workflow_files = list(self.cache_dir.glob("workflow_*.json"))
        
        return {
            'cached_workflows': len(workflow_files),
            'cache_directory': str(self.cache_dir),
            'cache_size_mb': sum(f.stat().st_size for f in workflow_files) / (1024 * 1024)
        }
