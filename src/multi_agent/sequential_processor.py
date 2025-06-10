"""
Sequential Multi-Agent Strategy Processor

Handles sequential execution of agents with dependency management,
state passing, and iterative refinement capabilities.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import logging

from .execution_coordinator import (
    BaseStrategyProcessor, ExecutionContext, ProcessedResponse,
    ContextManager, ResponseProcessor
)
from .adaptive_decision_engine import ExecutionDecision, ExecutionStrategy
from .agent_specializations import AgentType, AgentConfiguration
from .system_prompt_generator import SystemPromptGenerator


class SequentialProcessor(BaseStrategyProcessor):
    """Processes sequential multi-agent execution strategy."""
    
    def __init__(self, context_manager: ContextManager, 
                 response_processor: ResponseProcessor,
                 prompt_generator: Optional[SystemPromptGenerator] = None):
        super().__init__(context_manager, response_processor)
        self.prompt_generator = prompt_generator or SystemPromptGenerator()
        self.logger = logging.getLogger(__name__)
    
    async def process(self, decision: ExecutionDecision, 
                     context: ExecutionContext) -> List[ProcessedResponse]:
        """Process sequential execution strategy."""
        responses = []
        
        try:
            # Get agents in execution order
            agents = self._determine_execution_order(decision.selected_agents)
            
            self.logger.info(f"Starting sequential execution with {len(agents)} agents")
            
            # Execute agents sequentially
            for i, (agent_type, config) in enumerate(agents):
                self.logger.info(f"Executing agent {i+1}/{len(agents)}: {agent_type.value}")
                
                # Extract relevant context for this agent
                agent_context = self.context_manager.extract_relevant_context(
                    context, agent_type
                )
                
                # Include previous agent outputs in context
                agent_context['previous_responses'] = [
                    {
                        'agent_type': r.agent_type.value,
                        'response': r.raw_response,
                        'extracted_code': r.extracted_code,
                        'instructions': r.instructions,
                        'quality_score': r.quality_score
                    }
                    for r in responses
                ]
                
                # Generate agent-specific prompt
                prompt = self._generate_sequential_prompt(
                    agent_type, agent_context, config, i, len(agents)
                )
                
                # Execute agent (simulate - in real implementation this would call the actual agent)
                response = await self._execute_agent(
                    agent_type, config, prompt, agent_context
                )
                
                # Process response
                processed_response = self.response_processor.process_response(
                    f"{agent_type.value}_{i}", agent_type, response
                )
                
                responses.append(processed_response)
                
                # Update shared state with agent output
                self._update_shared_state(context, processed_response)
                
                # Check for early termination conditions
                if self._should_terminate_early(processed_response, context):
                    self.logger.info(f"Early termination triggered by {agent_type.value}")
                    break
                
                # Add delay for rate limiting if needed
                await asyncio.sleep(0.1)
        
        except Exception as e:
            self.logger.error(f"Error in sequential processing: {e}")
            context = self.handle_error(e, context)
        
        return responses
    
    def _determine_execution_order(self, selected_agents: List[Tuple[AgentType, AgentConfiguration]]) -> List[Tuple[AgentType, AgentConfiguration]]:
        """Determine optimal execution order for agents."""
        # Define standard sequential order
        standard_order = [
            AgentType.PLANNER,
            AgentType.CODER,
            AgentType.REVIEWER,
            AgentType.TESTER,
            AgentType.OPTIMIZER,
            AgentType.DEBUGGER,
            AgentType.DOCUMENTER
        ]
        
        # Sort selected agents according to standard order
        ordered_agents = []
        agent_dict = {agent_type: config for agent_type, config in selected_agents}
        
        for agent_type in standard_order:
            if agent_type in agent_dict:
                ordered_agents.append((agent_type, agent_dict[agent_type]))
        
        # Add any remaining agents not in standard order
        for agent_type, config in selected_agents:
            if agent_type not in [a[0] for a in ordered_agents]:
                ordered_agents.append((agent_type, config))
        
        return ordered_agents
    
    def _generate_sequential_prompt(self, agent_type: AgentType, 
                                  context: Dict[str, Any],
                                  config: AgentConfiguration,
                                  position: int, total_agents: int) -> str:
        """Generate sequential-specific prompt for an agent."""
        base_prompt = self.prompt_generator.generate_system_prompt(agent_type, config)
        
        # Add sequential context
        sequential_context = f"""
        
SEQUENTIAL EXECUTION CONTEXT:
- You are agent {position + 1} of {total_agents} in a sequential workflow
- Position: {agent_type.value}
        """
        
        if position > 0:
            sequential_context += """
- Previous agents have already completed their work
- Build upon their outputs and recommendations
- Avoid duplicating work already done by previous agents
            """
        
        if position < total_agents - 1:
            sequential_context += """
- Subsequent agents will build upon your work
- Provide clear, actionable outputs for the next agents
- Include detailed explanations of your decisions
            """
        
        # Add previous responses context
        if context.get('previous_responses'):
            sequential_context += "\n\nPREVIOUS AGENT OUTPUTS:\n"
            for i, prev_response in enumerate(context['previous_responses']):
                sequential_context += f"""
Agent {i+1} ({prev_response['agent_type']}):
- Quality Score: {prev_response['quality_score']:.2f}
- Code Blocks: {len(prev_response['extracted_code'])}
- Instructions: {len(prev_response['instructions'])}
- Key Output: {prev_response['response'][:200]}...
                """
        
        # Add shared variables
        if context.get('shared_variables'):
            sequential_context += f"\n\nSHARED VARIABLES:\n{context['shared_variables']}"
        
        # Add iteration context
        sequential_context += f"\n\nITERATION: {context.get('iteration_count', 0)}"
        
        return base_prompt + sequential_context
    
    async def _execute_agent(self, agent_type: AgentType, 
                           config: AgentConfiguration, 
                           prompt: str, context: Dict[str, Any]) -> str:
        """Execute an individual agent (simulated implementation)."""
        # In a real implementation, this would call the actual LLM agent
        # For now, we'll simulate different agent behaviors
        
        await asyncio.sleep(0.5)  # Simulate processing time
        
        user_query = context.get('user_query', '')
        previous_responses = context.get('previous_responses', [])
        
        # Simulate agent-specific responses
        if agent_type == AgentType.PLANNER:
            return self._simulate_planner_response(user_query, context)
        elif agent_type == AgentType.CODER:
            return self._simulate_coder_response(user_query, previous_responses)
        elif agent_type == AgentType.REVIEWER:
            return self._simulate_reviewer_response(previous_responses)
        elif agent_type == AgentType.TESTER:
            return self._simulate_tester_response(previous_responses)
        elif agent_type == AgentType.OPTIMIZER:
            return self._simulate_optimizer_response(previous_responses)
        elif agent_type == AgentType.DEBUGGER:
            return self._simulate_debugger_response(previous_responses)
        elif agent_type == AgentType.DOCUMENTER:
            return self._simulate_documenter_response(previous_responses)
        else:
            return f"Response from {agent_type.value} agent for query: {user_query}"
    
    def _simulate_planner_response(self, user_query: str, context: Dict[str, Any]) -> str:
        """Simulate planner agent response."""
        return f"""
I'll create a comprehensive plan for: {user_query}

EXECUTION PLAN:
1. Analyze requirements and define scope
2. Design the solution architecture
3. Implement core functionality
4. Add error handling and validation
5. Optimize for performance
6. Create comprehensive tests
7. Document the solution

APPROACH:
- Break down the problem into manageable components
- Follow best practices and design patterns
- Ensure scalability and maintainability
- Include proper error handling throughout

This plan will guide the subsequent agents in their specialized tasks.
        """
    
    def _simulate_coder_response(self, user_query: str, previous_responses: List[Dict[str, Any]]) -> str:
        """Simulate coder agent response."""
        plan_info = ""
        if previous_responses:
            planner_response = previous_responses[0].get('response', '')
            if 'plan' in planner_response.lower():
                plan_info = "Following the established plan, "
        
        return f"""
{plan_info}I'll implement the solution for: {user_query}

```python
def solution_function(input_data):
    \"\"\"
    Main solution function based on requirements.
    \"\"\"
    try:
        # Process input data
        processed_data = process_input(input_data)
        
        # Apply core logic
        result = apply_core_logic(processed_data)
        
        # Validate and return result
        validated_result = validate_result(result)
        return validated_result
        
    except Exception as e:
        raise RuntimeError(f"Error in solution: {{e}}")

def process_input(data):
    \"\"\"Process and validate input data.\"\"\"
    if not data:
        raise ValueError("Input data cannot be empty")
    return data

def apply_core_logic(data):
    \"\"\"Apply the main business logic.\"\"\"
    # Implementation details here
    return data

def validate_result(result):
    \"\"\"Validate the result before returning.\"\"\"
    if result is None:
        raise ValueError("Result cannot be None")
    return result
```

IMPLEMENTATION NOTES:
- Added comprehensive error handling
- Included input validation
- Structured code for maintainability
- Ready for testing and optimization
        """
    
    def _simulate_reviewer_response(self, previous_responses: List[Dict[str, Any]]) -> str:
        """Simulate reviewer agent response."""
        code_quality = "good"
        if previous_responses:
            coder_response = next((r for r in previous_responses if 'code' in r.get('response', '')), None)
            if coder_response:
                code_quality = "excellent" if '"""' in coder_response['response'] else "good"
        
        return f"""
CODE REVIEW COMPLETED

QUALITY ASSESSMENT: {code_quality.upper()}

POSITIVE ASPECTS:
✓ Clear function structure and naming
✓ Comprehensive error handling implemented
✓ Good separation of concerns
✓ Proper input validation included
✓ Documentation strings present

RECOMMENDATIONS:
1. Add type hints for better code clarity
2. Consider adding logging for debugging
3. Include performance monitoring
4. Add unit test coverage indicators

SECURITY CONSIDERATIONS:
- Input validation is properly implemented
- Error messages don't expose sensitive information
- No obvious security vulnerabilities detected

OVERALL: Code is production-ready with minor enhancements recommended.
        """
    
    def _simulate_tester_response(self, previous_responses: List[Dict[str, Any]]) -> str:
        """Simulate tester agent response."""
        return """
COMPREHENSIVE TEST SUITE CREATED

```python
import unittest
import pytest
from unittest.mock import patch, MagicMock

class TestSolution(unittest.TestCase):
    def setUp(self):
        self.test_data = {"key": "value"}
    
    def test_solution_function_success(self):
        \"\"\"Test successful execution of main function.\"\"\"
        result = solution_function(self.test_data)
        self.assertIsNotNone(result)
    
    def test_solution_function_empty_input(self):
        \"\"\"Test handling of empty input.\"\"\"
        with self.assertRaises(ValueError):
            solution_function(None)
    
    def test_process_input_validation(self):
        \"\"\"Test input processing validation.\"\"\"
        result = process_input(self.test_data)
        self.assertEqual(result, self.test_data)
    
    def test_error_handling(self):
        \"\"\"Test error handling mechanisms.\"\"\"
        with patch('solution_function') as mock_func:
            mock_func.side_effect = Exception("Test error")
            with self.assertRaises(RuntimeError):
                solution_function(self.test_data)

if __name__ == '__main__':
    unittest.main()
```

TEST COVERAGE REPORT:
- Functions covered: 100%
- Lines covered: 95%
- Edge cases tested: 8/10
- Error scenarios: 5/5

TESTING RECOMMENDATIONS:
1. Add integration tests
2. Include performance benchmarks
3. Test with various data sizes
4. Add stress testing scenarios
        """
    
    def _simulate_optimizer_response(self, previous_responses: List[Dict[str, Any]]) -> str:
        """Simulate optimizer agent response."""
        return """
PERFORMANCE OPTIMIZATION ANALYSIS

CURRENT PERFORMANCE:
- Execution time: Baseline established
- Memory usage: Within acceptable limits
- Algorithmic complexity: O(n) - efficient

OPTIMIZATION OPPORTUNITIES:

```python
# Optimized version with caching
from functools import lru_cache
import asyncio

@lru_cache(maxsize=128)
def optimized_solution_function(input_data):
    \"\"\"
    Optimized version with caching for repeated calls.
    \"\"\"
    return solution_function(input_data)

async def async_solution_function(input_data):
    \"\"\"
    Asynchronous version for I/O bound operations.
    \"\"\"
    return await asyncio.to_thread(solution_function, input_data)

def batch_process(data_list):
    \"\"\"
    Batch processing for multiple inputs.
    \"\"\"
    return [solution_function(data) for data in data_list]
```

PERFORMANCE IMPROVEMENTS:
1. Added LRU caching for repeated calls (30% faster)
2. Asynchronous version for concurrent processing
3. Batch processing capability
4. Memory usage optimized

BENCHMARKS:
- Single call: 15ms → 10ms (33% improvement)
- Repeated calls: 15ms → 5ms (67% improvement)
- Batch processing: 50% reduction in total time
        """
    
    def _simulate_debugger_response(self, previous_responses: List[Dict[str, Any]]) -> str:
        """Simulate debugger agent response."""
        return """
DEBUGGING AND ERROR ANALYSIS COMPLETE

POTENTIAL ISSUES IDENTIFIED:
1. Edge case handling in input validation
2. Memory management in batch processing
3. Async operation timeout handling

DEBUGGING ENHANCEMENTS:

```python
import logging
from contextlib import contextmanager

# Enhanced logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@contextmanager
def debug_context(operation_name):
    \"\"\"Context manager for debugging operations.\"\"\"
    logger.info(f"Starting {operation_name}")
    try:
        yield
        logger.info(f"Completed {operation_name}")
    except Exception as e:
        logger.error(f"Error in {operation_name}: {e}")
        raise

def debug_solution_function(input_data):
    \"\"\"Enhanced version with debugging capabilities.\"\"\"
    with debug_context("solution_function"):
        logger.debug(f"Input data type: {type(input_data)}")
        result = solution_function(input_data)
        logger.debug(f"Result type: {type(result)}")
        return result
```

MONITORING RECOMMENDATIONS:
1. Add performance monitoring
2. Include memory usage tracking
3. Set up error alerting
4. Add health check endpoints

ERROR PREVENTION:
- Input sanitization enhanced
- Graceful degradation implemented
- Fallback mechanisms added
        """
    
    def _simulate_documenter_response(self, previous_responses: List[Dict[str, Any]]) -> str:
        """Simulate documenter agent response."""
        return """
COMPREHENSIVE DOCUMENTATION CREATED

# Solution Documentation

## Overview
This solution provides a robust, scalable implementation for the given requirements.

## Architecture
The solution follows a modular design pattern with clear separation of concerns:

- **Input Processing**: Validates and sanitizes input data
- **Core Logic**: Implements the main business functionality
- **Result Validation**: Ensures output quality and consistency
- **Error Handling**: Comprehensive error management

## Usage Examples

```python
# Basic usage
from solution import solution_function

# Simple case
result = solution_function({"data": "example"})

# With error handling
try:
    result = solution_function(input_data)
    print(f"Success: {result}")
except ValueError as e:
    print(f"Input error: {e}")
except RuntimeError as e:
    print(f"Processing error: {e}")
```

## API Reference

### solution_function(input_data)
Main entry point for the solution.

**Parameters:**
- `input_data` (dict): Input data to process

**Returns:**
- Processed result data

**Raises:**
- `ValueError`: For invalid input data
- `RuntimeError`: For processing errors

## Performance Characteristics
- Time Complexity: O(n)
- Space Complexity: O(1)
- Throughput: 1000+ operations/second

## Testing
Run tests with: `python -m pytest tests/`
Coverage report: `coverage run -m pytest && coverage report`

## Deployment
The solution is production-ready and includes:
- Comprehensive error handling
- Performance optimizations
- Monitoring capabilities
- Security considerations
        """
    
    def _update_shared_state(self, context: ExecutionContext, 
                           response: ProcessedResponse):
        """Update shared state with agent response."""
        agent_key = response.agent_type.value
        
        # Store agent state
        context.agent_states[agent_key] = {
            'last_response': response.raw_response,
            'quality_score': response.quality_score,
            'code_blocks': len(response.extracted_code),
            'instructions': len(response.instructions),
            'timestamp': response.timestamp.isoformat()
        }
        
        # Update shared variables with extracted information
        if response.extracted_code:
            if 'code_blocks' not in context.shared_variables:
                context.shared_variables['code_blocks'] = []
            context.shared_variables['code_blocks'].extend(response.extracted_code)
        
        if response.instructions:
            if 'instructions' not in context.shared_variables:
                context.shared_variables['instructions'] = []
            context.shared_variables['instructions'].extend(response.instructions)
        
        # Update execution metadata
        context.execution_metadata[f'{agent_key}_completed'] = True
        context.execution_metadata[f'{agent_key}_quality'] = response.quality_score
    
    def _should_terminate_early(self, response: ProcessedResponse, 
                              context: ExecutionContext) -> bool:
        """Determine if execution should terminate early."""
        # Terminate if response quality is too low
        if response.quality_score < 0.2:
            self.logger.warning(f"Low quality response from {response.agent_type.value}: {response.quality_score}")
            return True
        
        # Terminate if we've hit iteration limit
        if context.iteration_count >= context.max_iterations:
            self.logger.info(f"Reached maximum iterations: {context.max_iterations}")
            return True
        
        # Terminate if agent indicates completion
        completion_keywords = ['completed', 'finished', 'done', 'final']
        if any(keyword in response.raw_response.lower() for keyword in completion_keywords):
            return True
        
        return False