"""
Request Optimizer - FASE 1: Pre-procesamiento y Enriquecimiento
Optimizes API requests for better performance, cost-efficiency, and response quality.
"""

import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import hashlib


class RequestOptimizer:
    """
    Intelligent request optimizer that enhances API performance through
    smart batching, caching strategies, and dynamic configuration adjustment.
    """
    
    def __init__(self):
        self.optimization_history = []
        self.performance_metrics = {}
        self.cost_tracking = {
            'session_cost': 0.0,
            'optimization_savings': 0.0
        }
    
    def optimize_request_strategy(self, 
                                 enriched_config: Dict[str, Any], 
                                 context: Dict[str, Any],
                                 performance_target: str = 'balanced') -> Dict[str, Any]:
        """
        Optimize request strategy based on context and performance targets.
        
        Args:
            enriched_config: Configuration from PromptEnricher
            context: Project context from ContextBuilder
            performance_target: 'speed', 'cost', 'quality', or 'balanced'
            
        Returns:
            Optimized configuration
        """
        optimized_config = enriched_config.copy()
        
        # Apply target-specific optimizations
        if performance_target == 'speed':
            optimized_config = self._optimize_for_speed(optimized_config, context)
        elif performance_target == 'cost':
            optimized_config = self._optimize_for_cost(optimized_config, context)
        elif performance_target == 'quality':
            optimized_config = self._optimize_for_quality(optimized_config, context)
        else:  # balanced
            optimized_config = self._optimize_balanced(optimized_config, context)
        
        # Apply context-aware optimizations
        optimized_config = self._apply_context_optimizations(optimized_config, context)
        
        # Apply historical optimizations
        optimized_config = self._apply_historical_optimizations(optimized_config)
        
        # Track optimization
        self._track_optimization(enriched_config, optimized_config, performance_target)
        
        return optimized_config
    
    def _optimize_for_speed(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize configuration for fastest response times."""
        optimized = config.copy()
        
        # Use fastest model
        optimized['model'] = 'claude-3-haiku-20240307'
        
        # Reduce max_tokens for faster generation
        current_tokens = optimized.get('max_tokens', 4000)
        optimized['max_tokens'] = min(current_tokens, 3000)
        
        # Slightly increase temperature for faster, less deliberate responses
        optimized['temperature'] = min(optimized.get('temperature', 0.3) + 0.1, 0.8)
        
        # Optimize prompt for conciseness
        optimized['prompt'] = self._compress_prompt_for_speed(optimized['prompt'])
        
        return optimized
    
    def _optimize_for_cost(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize configuration for lowest cost."""
        optimized = config.copy()
        
        # Use most cost-effective model
        optimized['model'] = 'claude-3-haiku-20240307'
        
        # Reduce max_tokens to minimum viable
        task_type = config.get('metadata', {}).get('task_type', 'implementation')
        
        min_tokens = {
            'analysis': 1500,
            'implementation': 2000,
            'debugging': 1000,
            'testing': 1500,
            'optimization': 2000
        }
        
        optimized['max_tokens'] = min_tokens.get(task_type, 1500)
        
        # Compress prompt to reduce input costs
        optimized['prompt'] = self._compress_prompt_for_cost(optimized['prompt'])
        
        # Lower temperature for more predictable (shorter) responses
        optimized['temperature'] = max(optimized.get('temperature', 0.3) - 0.1, 0.0)
        
        return optimized
    
    def _optimize_for_quality(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize configuration for highest quality responses."""
        optimized = config.copy()
        
        # Use highest quality model
        complexity = context.get('complexity_metrics', {}).get('technical_debt', 'medium')
        
        if complexity == 'high' or config.get('metadata', {}).get('task_type') == 'debugging':
            optimized['model'] = 'claude-3-opus-20240229'
        else:
            optimized['model'] = 'claude-3-sonnet-20240229'
        
        # Increase max_tokens for detailed responses
        current_tokens = optimized.get('max_tokens', 4000)
        optimized['max_tokens'] = min(current_tokens + 2000, 12000)
        
        # Enhance prompt with additional context
        optimized['prompt'] = self._enhance_prompt_for_quality(optimized['prompt'], context)
        
        # Optimal temperature for thoughtful responses
        task_type = config.get('metadata', {}).get('task_type', 'implementation')
        optimal_temps = {
            'implementation': 0.2,
            'analysis': 0.1,
            'debugging': 0.05,
            'testing': 0.25,
            'optimization': 0.15
        }
        optimized['temperature'] = optimal_temps.get(task_type, 0.2)
        
        return optimized
    
    def _optimize_balanced(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize configuration for balanced performance."""
        optimized = config.copy()
        
        # Use balanced model (Sonnet)
        optimized['model'] = 'claude-3-sonnet-20240229'
        
        # Adjust tokens based on complexity
        complexity = context.get('complexity_metrics', {}).get('technical_debt', 'medium')
        base_tokens = optimized.get('max_tokens', 4000)
        
        if complexity == 'high':
            optimized['max_tokens'] = min(base_tokens + 1000, 8000)
        elif complexity == 'low':
            optimized['max_tokens'] = max(base_tokens - 1000, 2000)
        
        # Optimize prompt for balance
        optimized['prompt'] = self._balance_prompt_optimization(optimized['prompt'], context)
        
        return optimized
    
    def _apply_context_optimizations(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply optimizations based on project context."""
        optimized = config.copy()
        
        # Optimize based on project size
        file_count = context.get('file_structure', {}).get('total_files', 0)
        
        if file_count > 100:  # Large project
            # More context needed for large projects
            optimized['max_tokens'] = min(optimized.get('max_tokens', 4000) + 1000, 10000)
        elif file_count < 20:  # Small project
            # Less context needed for small projects
            optimized['max_tokens'] = max(optimized.get('max_tokens', 4000) - 500, 2000)
        
        # Optimize based on language and framework
        language = context.get('project_metadata', {}).get('language')
        framework = context.get('project_metadata', {}).get('framework')
        
        if language == 'python' and framework is None:
            # Standard Python project - moderate complexity
            pass
        elif framework in ['react', 'vue', 'angular']:
            # Frontend frameworks - often need more detailed responses
            optimized['max_tokens'] = min(optimized.get('max_tokens', 4000) + 500, 8000)
        elif framework == 'fastapi':
            # API framework - structured responses needed
            optimized['temperature'] = max(optimized.get('temperature', 0.3) - 0.1, 0.1)
        
        return optimized
    
    def _apply_historical_optimizations(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply optimizations based on historical performance."""
        if not self.optimization_history:
            return config
        
        optimized = config.copy()
        task_type = config.get('metadata', {}).get('task_type')
        
        # Find similar historical requests
        similar_requests = [
            opt for opt in self.optimization_history 
            if opt.get('task_type') == task_type and 
               opt.get('success_score', 0) > 0.8
        ]
        
        if similar_requests:
            # Use average successful configuration
            avg_temp = sum(req.get('temperature', 0.3) for req in similar_requests) / len(similar_requests)
            avg_tokens = sum(req.get('max_tokens', 4000) for req in similar_requests) / len(similar_requests)
            
            # Apply with smoothing
            current_temp = optimized.get('temperature', 0.3)
            current_tokens = optimized.get('max_tokens', 4000)
            
            optimized['temperature'] = (current_temp + avg_temp) / 2
            optimized['max_tokens'] = int((current_tokens + avg_tokens) / 2)
        
        return optimized
    
    def _compress_prompt_for_speed(self, prompt: str) -> str:
        """Compress prompt for faster processing while preserving meaning."""
        # Remove extra whitespace and verbose sections
        lines = prompt.split('\n')
        compressed_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('##'):  # Keep section headers
                # Remove verbose phrases
                line = line.replace('Please note that', '')
                line = line.replace('It is important to', '')
                line = line.replace('Make sure to', '')
                line = ' '.join(line.split())  # Normalize whitespace
                compressed_lines.append(line)
            elif line.startswith('##'):
                compressed_lines.append(line)
        
        return '\n'.join(compressed_lines)
    
    def _compress_prompt_for_cost(self, prompt: str) -> str:
        """Compress prompt for cost optimization."""
        # More aggressive compression
        lines = prompt.split('\n')
        essential_lines = []
        
        # Keep only essential sections
        essential_keywords = [
            'requirements', 'implementation', 'context', 'constraints',
            'output', 'format', 'project', 'code'
        ]
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in essential_keywords) or line.startswith('##'):
                essential_lines.append(line)
        
        # Further compress by removing redundant phrases
        compressed = '\n'.join(essential_lines)
        compressed = compressed.replace('Implementation Requirements', 'Requirements')
        compressed = compressed.replace('Expected Output', 'Output')
        compressed = compressed.replace('Constraints and Guidelines', 'Constraints')
        
        return compressed
    
    def _enhance_prompt_for_quality(self, prompt: str, context: Dict[str, Any]) -> str:
        """Enhance prompt for higher quality responses."""
        enhanced = prompt
        
        # Add quality-focused instructions
        quality_instructions = [
            "\n## Quality Requirements",
            "- Provide detailed explanations for all decisions",
            "- Include error handling and edge cases",
            "- Follow industry best practices",
            "- Ensure code is production-ready"
        ]
        
        # Add context-specific quality requirements
        complexity = context.get('complexity_metrics', {}).get('technical_debt', 'medium')
        if complexity == 'high':
            quality_instructions.extend([
                "- Focus on reducing technical debt",
                "- Prioritize maintainability over performance",
                "- Include refactoring suggestions"
            ])
        
        enhanced += '\n'.join(quality_instructions)
        return enhanced
    
    def _balance_prompt_optimization(self, prompt: str, context: Dict[str, Any]) -> str:
        """Optimize prompt for balanced performance."""
        # Light compression with selective enhancement
        lines = prompt.split('\n')
        optimized_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Keep important content, compress verbose explanations
                if len(line) > 100 and not line.startswith('##'):
                    # Compress long lines
                    line = '. '.join(sent.strip() for sent in line.split('.') if sent.strip())[:80] + '...'
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def batch_optimize_requests(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize a batch of requests for efficient processing."""
        if not requests:
            return []
        
        optimized_batch = []
        
        # Group similar requests
        request_groups = self._group_similar_requests(requests)
        
        for group in request_groups:
            # Optimize each group
            optimized_group = self._optimize_request_group(group)
            optimized_batch.extend(optimized_group)
        
        # Sort by priority (complexity and urgency)
        optimized_batch.sort(key=self._calculate_request_priority, reverse=True)
        
        return optimized_batch
    
    def _group_similar_requests(self, requests: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group similar requests for batch optimization."""
        groups = []
        ungrouped = requests.copy()
        
        while ungrouped:
            current_request = ungrouped.pop(0)
            current_group = [current_request]
            
            # Find similar requests
            similar_indices = []
            for i, request in enumerate(ungrouped):
                if self._are_requests_similar(current_request, request):
                    similar_indices.append(i)
            
            # Add similar requests to group (in reverse order to maintain indices)
            for i in reversed(similar_indices):
                current_group.append(ungrouped.pop(i))
            
            groups.append(current_group)
        
        return groups
    
    def _are_requests_similar(self, req1: Dict[str, Any], req2: Dict[str, Any]) -> bool:
        """Check if two requests are similar enough to group together."""
        # Compare task types
        task1 = req1.get('metadata', {}).get('task_type')
        task2 = req2.get('metadata', {}).get('task_type')
        
        if task1 != task2:
            return False
        
        # Compare complexity levels
        complexity1 = req1.get('metadata', {}).get('complexity_level')
        complexity2 = req2.get('metadata', {}).get('complexity_level')
        
        if complexity1 != complexity2:
            return False
        
        # Compare prompt similarity (rough)
        prompt1 = req1.get('prompt', '')
        prompt2 = req2.get('prompt', '')
        
        # Simple similarity check based on length and common words
        len_diff = abs(len(prompt1) - len(prompt2)) / max(len(prompt1), len(prompt2), 1)
        
        return len_diff < 0.5  # Within 50% length difference
    
    def _optimize_request_group(self, group: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize a group of similar requests."""
        if len(group) == 1:
            return group
        
        # Find optimal configuration for the group
        temperatures = [req.get('temperature', 0.3) for req in group]
        max_tokens = [req.get('max_tokens', 4000) for req in group]
        
        # Use median values for stability
        optimal_temp = sorted(temperatures)[len(temperatures) // 2]
        optimal_tokens = sorted(max_tokens)[len(max_tokens) // 2]
        
        # Apply optimal configuration to all requests in group
        optimized_group = []
        for request in group:
            optimized_request = request.copy()
            optimized_request['temperature'] = optimal_temp
            optimized_request['max_tokens'] = optimal_tokens
            optimized_group.append(optimized_request)
        
        return optimized_group
    
    def _calculate_request_priority(self, request: Dict[str, Any]) -> float:
        """Calculate priority score for request ordering."""
        priority = 0.0
        
        # Task type priority
        task_priorities = {
            'debugging': 10.0,
            'implementation': 8.0,
            'analysis': 6.0,
            'optimization': 4.0,
            'testing': 5.0
        }
        
        task_type = request.get('metadata', {}).get('task_type', 'implementation')
        priority += task_priorities.get(task_type, 5.0)
        
        # Complexity priority (simpler tasks first for quick wins)
        complexity_priorities = {
            'simple': 9.0,
            'medium': 7.0,
            'complex': 5.0,
            'very_complex': 3.0
        }
        
        complexity = request.get('metadata', {}).get('complexity_level', 'medium')
        priority += complexity_priorities.get(complexity, 5.0)
        
        # Cost factor (lower cost = higher priority for batching)
        estimated_cost = self._estimate_request_cost(request)
        if estimated_cost < 0.01:
            priority += 3.0
        elif estimated_cost < 0.05:
            priority += 1.0
        
        return priority
    
    def _estimate_request_cost(self, request: Dict[str, Any]) -> float:
        """Estimate the cost of a single request."""
        prompt_tokens = len(request.get('prompt', '')) // 4
        max_tokens = request.get('max_tokens', 4000)
        model = request.get('model', 'claude-3-sonnet-20240229')
        
        # Pricing estimates
        if 'opus' in model:
            input_rate, output_rate = 0.015, 0.075
        elif 'sonnet' in model:
            input_rate, output_rate = 0.003, 0.015
        else:  # haiku
            input_rate, output_rate = 0.00025, 0.00125
        
        return (prompt_tokens / 1000) * input_rate + (max_tokens / 1000) * output_rate
    
    def _track_optimization(self, original: Dict[str, Any], optimized: Dict[str, Any], target: str):
        """Track optimization results for future improvements."""
        optimization_record = {
            'timestamp': datetime.now().isoformat(),
            'target': target,
            'original_config': {
                'model': original.get('model'),
                'temperature': original.get('temperature'),
                'max_tokens': original.get('max_tokens'),
                'estimated_cost': self._estimate_request_cost(original)
            },
            'optimized_config': {
                'model': optimized.get('model'),
                'temperature': optimized.get('temperature'),
                'max_tokens': optimized.get('max_tokens'),
                'estimated_cost': self._estimate_request_cost(optimized)
            },
            'task_type': original.get('metadata', {}).get('task_type'),
            'complexity_level': original.get('metadata', {}).get('complexity_level')
        }
        
        # Calculate potential savings
        cost_savings = (optimization_record['original_config']['estimated_cost'] - 
                       optimization_record['optimized_config']['estimated_cost'])
        optimization_record['cost_savings'] = cost_savings
        
        self.optimization_history.append(optimization_record)
        self.cost_tracking['optimization_savings'] += max(0, cost_savings)
        
        # Keep only recent history
        if len(self.optimization_history) > 500:
            self.optimization_history = self.optimization_history[-500:]
    
    def get_optimization_metrics(self) -> Dict[str, Any]:
        """Get optimization performance metrics."""
        if not self.optimization_history:
            return {'message': 'No optimizations recorded yet'}
        
        recent_optimizations = [
            opt for opt in self.optimization_history 
            if datetime.fromisoformat(opt['timestamp']) > datetime.now() - timedelta(hours=24)
        ]
        
        if not recent_optimizations:
            return {'message': 'No recent optimizations (last 24 hours)'}
        
        total_original_cost = sum(opt['original_config']['estimated_cost'] for opt in recent_optimizations)
        total_optimized_cost = sum(opt['optimized_config']['estimated_cost'] for opt in recent_optimizations)
        total_savings = total_original_cost - total_optimized_cost
        
        # Performance by target
        target_performance = {}
        for target in ['speed', 'cost', 'quality', 'balanced']:
            target_opts = [opt for opt in recent_optimizations if opt['target'] == target]
            if target_opts:
                target_savings = sum(opt['cost_savings'] for opt in target_opts)
                target_performance[target] = {
                    'optimizations': len(target_opts),
                    'total_savings': target_savings,
                    'avg_savings': target_savings / len(target_opts)
                }
        
        return {
            'period': '24 hours',
            'total_optimizations': len(recent_optimizations),
            'total_cost_savings': total_savings,
            'cost_reduction_percentage': (total_savings / total_original_cost * 100) if total_original_cost > 0 else 0,
            'session_savings': self.cost_tracking['optimization_savings'],
            'performance_by_target': target_performance
        }
