"""
Anthropic Client - FASE 1: API Integration
Handles all interactions with the Anthropic Claude API for intelligent responses.
"""

import os
import time
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import anthropic
from anthropic import APIError, APITimeoutError, RateLimitError


class AnthropicClient:
    """
    Intelligent Anthropic API client with optimization, caching, and error handling.
    """
    
    def __init__(self, api_key: Optional[str] = None, cache_enabled: bool = True):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.cache_enabled = cache_enabled
        self.cache = {}
        self.request_history = []
        self.cost_tracker = {
            'daily_cost': 0.0,
            'monthly_cost': 0.0,
            'last_reset': datetime.now()
        }
        
    def send_enriched_request(self, 
                            enriched_config: Dict[str, Any], 
                            use_cache: bool = True,
                            fallback_model: Optional[str] = None) -> Dict[str, Any]:
        """
        Send an enriched request to the Anthropic API.
        
        Args:
            enriched_config: Configuration from PromptEnricher
            use_cache: Whether to use caching
            fallback_model: Fallback model if primary fails
            
        Returns:
            API response with metadata
        """
        # Generate cache key
        cache_key = self._generate_cache_key(enriched_config) if use_cache else None
        
        # Check cache first
        if cache_key and cache_key in self.cache:
            cached_response = self.cache[cache_key]
            if self._is_cache_valid(cached_response):
                return {
                    **cached_response['response'],
                    'from_cache': True,
                    'cache_timestamp': cached_response['timestamp']
                }
        
        # Check cost limits
        if not self._check_cost_limits(enriched_config):
            if fallback_model:
                enriched_config = self._apply_fallback_model(enriched_config, fallback_model)
            else:
                raise Exception("Cost limit exceeded and no fallback model specified")
        
        # Send request with retry logic
        response = self._send_request_with_retry(enriched_config)
        
        # Update cost tracking
        self._update_cost_tracking(enriched_config, response)
        
        # Cache response
        if cache_key and self.cache_enabled:
            self.cache[cache_key] = {
                'response': response,
                'timestamp': datetime.now(),
                'config': enriched_config
            }
        
        # Track request history
        self._track_request(enriched_config, response)
        
        return response
    
    def _generate_cache_key(self, config: Dict[str, Any]) -> str:
        """Generate a cache key for the request configuration."""
        # Create a stable hash of the important configuration elements
        cache_elements = {
            'prompt': config.get('prompt', ''),
            'system_prompt': config.get('system_prompt', ''),
            'model': config.get('model', ''),
            'temperature': config.get('temperature', 0.0),
            'max_tokens': config.get('max_tokens', 0)
        }
        
        cache_string = json.dumps(cache_elements, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _is_cache_valid(self, cached_entry: Dict[str, Any]) -> bool:
        """Check if a cached entry is still valid."""
        # Cache expires after 1 hour by default
        cache_duration = timedelta(hours=1)
        return datetime.now() - cached_entry['timestamp'] < cache_duration
    
    def _check_cost_limits(self, config: Dict[str, Any]) -> bool:
        """Check if the request is within cost limits."""
        estimated_cost = self._estimate_request_cost(config)
        
        # Reset daily/monthly counters if needed
        self._reset_cost_counters()
        
        # Check limits
        daily_limit = 50.0  # $50 daily limit
        monthly_limit = 500.0  # $500 monthly limit
        
        return (self.cost_tracker['daily_cost'] + estimated_cost <= daily_limit and
                self.cost_tracker['monthly_cost'] + estimated_cost <= monthly_limit)
    
    def _estimate_request_cost(self, config: Dict[str, Any]) -> float:
        """Estimate the cost of a request."""
        prompt_tokens = len(config.get('prompt', '')) // 4  # Rough approximation
        max_output_tokens = config.get('max_tokens', 4000)
        model = config.get('model', 'claude-3-sonnet-20240229')
        
        # Pricing per 1K tokens (approximate as of 2024)
        if 'opus' in model:
            input_rate = 0.015
            output_rate = 0.075
        elif 'sonnet' in model:
            input_rate = 0.003
            output_rate = 0.015
        else:  # haiku
            input_rate = 0.00025
            output_rate = 0.00125
        
        input_cost = (prompt_tokens / 1000) * input_rate
        output_cost = (max_output_tokens / 1000) * output_rate
        
        return input_cost + output_cost
    
    def _reset_cost_counters(self):
        """Reset cost counters if time periods have elapsed."""
        now = datetime.now()
        last_reset = self.cost_tracker['last_reset']
        
        # Reset daily counter if it's a new day
        if now.date() > last_reset.date():
            self.cost_tracker['daily_cost'] = 0.0
        
        # Reset monthly counter if it's a new month
        if now.month != last_reset.month or now.year != last_reset.year:
            self.cost_tracker['monthly_cost'] = 0.0
            
        self.cost_tracker['last_reset'] = now
    
    def _apply_fallback_model(self, config: Dict[str, Any], fallback_model: str) -> Dict[str, Any]:
        """Apply fallback model configuration."""
        fallback_config = config.copy()
        fallback_config['model'] = fallback_model
        
        # Adjust parameters for fallback model
        if 'haiku' in fallback_model:
            # Reduce max_tokens for the smaller model
            fallback_config['max_tokens'] = min(fallback_config.get('max_tokens', 4000), 4000)
        
        return fallback_config
    
    def _send_request_with_retry(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Send request with retry logic for better reliability."""
        max_retries = 3
        backoff_factor = 2.0
        
        for attempt in range(max_retries + 1):
            try:
                # Create the request payload
                request_payload = {
                    'model': config.get('model', 'claude-3-sonnet-20240229'),
                    'max_tokens': config.get('max_tokens', 4000),
                    'temperature': config.get('temperature', 0.3),
                    'system': config.get('system_prompt', ''),
                    'messages': [
                        {
                            'role': 'user',
                            'content': config['prompt']
                        }
                    ]
                }
                
                # Send the request
                start_time = time.time()
                response = self.client.messages.create(**request_payload)
                end_time = time.time()
                
                # Process response
                response_text = ''.join([block.text for block in response.content if hasattr(block, 'text')])
                
                return {
                    'content': response_text,
                    'model': response.model,
                    'usage': {
                        'input_tokens': response.usage.input_tokens,
                        'output_tokens': response.usage.output_tokens
                    },
                    'request_time': end_time - start_time,
                    'attempt': attempt + 1,
                    'from_cache': False
                }
                
            except RateLimitError as e:
                if attempt < max_retries:
                    wait_time = backoff_factor ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"Rate limit exceeded after {max_retries} retries: {str(e)}")
                    
            except APITimeoutError as e:
                if attempt < max_retries:
                    wait_time = backoff_factor ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"API timeout after {max_retries} retries: {str(e)}")
                    
            except APIError as e:
                if attempt < max_retries and e.status_code >= 500:
                    # Retry on server errors
                    wait_time = backoff_factor ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"API error: {str(e)}")
                    
            except Exception as e:
                raise Exception(f"Unexpected error: {str(e)}")
        
        raise Exception("Max retries exceeded")
    
    def _update_cost_tracking(self, config: Dict[str, Any], response: Dict[str, Any]):
        """Update cost tracking based on actual usage."""
        if response.get('from_cache'):
            return  # No cost for cached responses
            
        usage = response.get('usage', {})
        input_tokens = usage.get('input_tokens', 0)
        output_tokens = usage.get('output_tokens', 0)
        model = response.get('model', config.get('model', 'claude-3-sonnet-20240229'))
        
        # Calculate actual cost
        if 'opus' in model:
            input_rate = 0.015
            output_rate = 0.075
        elif 'sonnet' in model:
            input_rate = 0.003
            output_rate = 0.015
        else:  # haiku
            input_rate = 0.00025
            output_rate = 0.00125
        
        actual_cost = ((input_tokens / 1000) * input_rate + 
                      (output_tokens / 1000) * output_rate)
        
        self.cost_tracker['daily_cost'] += actual_cost
        self.cost_tracker['monthly_cost'] += actual_cost
    
    def _track_request(self, config: Dict[str, Any], response: Dict[str, Any]):
        """Track request for analytics and optimization."""
        request_record = {
            'timestamp': datetime.now().isoformat(),
            'model': response.get('model'),
            'task_type': config.get('metadata', {}).get('task_type'),
            'complexity_level': config.get('metadata', {}).get('complexity_level'),
            'input_tokens': response.get('usage', {}).get('input_tokens', 0),
            'output_tokens': response.get('usage', {}).get('output_tokens', 0),
            'request_time': response.get('request_time', 0),
            'from_cache': response.get('from_cache', False),
            'success': True
        }
        
        self.request_history.append(request_record)
        
        # Keep only recent history (last 1000 requests)
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the API client."""
        if not self.request_history:
            return {'message': 'No requests recorded yet'}
        
        recent_requests = [r for r in self.request_history 
                          if datetime.fromisoformat(r['timestamp']) > datetime.now() - timedelta(hours=24)]
        
        if not recent_requests:
            return {'message': 'No recent requests (last 24 hours)'}
        
        total_requests = len(recent_requests)
        cache_hits = sum(1 for r in recent_requests if r.get('from_cache', False))
        avg_response_time = sum(r.get('request_time', 0) for r in recent_requests) / total_requests
        total_input_tokens = sum(r.get('input_tokens', 0) for r in recent_requests)
        total_output_tokens = sum(r.get('output_tokens', 0) for r in recent_requests)
        
        return {
            'period': '24 hours',
            'total_requests': total_requests,
            'cache_hit_rate': cache_hits / total_requests if total_requests > 0 else 0,
            'average_response_time': avg_response_time,
            'total_input_tokens': total_input_tokens,
            'total_output_tokens': total_output_tokens,
            'daily_cost': self.cost_tracker['daily_cost'],
            'monthly_cost': self.cost_tracker['monthly_cost']
        }
    
    def optimize_request_batch(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize a batch of requests for better performance and cost."""
        optimized_requests = []
        
        for request in requests:
            # Check for similar requests that can be combined
            combined_request = self._try_combine_similar_requests(request, optimized_requests)
            
            if combined_request:
                optimized_requests.append(combined_request)
            else:
                optimized_requests.append(request)
        
        # Sort by priority (lower temperature = higher priority)
        optimized_requests.sort(key=lambda x: x.get('temperature', 0.5))
        
        return optimized_requests
    
    def _try_combine_similar_requests(self, request: Dict[str, Any], existing_requests: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Try to combine similar requests for efficiency."""
        # For now, return None (no combination)
        # Future implementation could combine similar prompts
        return None
    
    def clear_cache(self):
        """Clear the response cache."""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.cache:
            return {'cache_size': 0, 'message': 'Cache is empty'}
        
        now = datetime.now()
        valid_entries = sum(1 for entry in self.cache.values() 
                           if self._is_cache_valid(entry))
        
        return {
            'total_entries': len(self.cache),
            'valid_entries': valid_entries,
            'invalid_entries': len(self.cache) - valid_entries,
            'cache_hit_rate': self._calculate_cache_hit_rate()
        }
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate from recent requests."""
        if not self.request_history:
            return 0.0
        
        recent_requests = [r for r in self.request_history 
                          if datetime.fromisoformat(r['timestamp']) > datetime.now() - timedelta(hours=1)]
        
        if not recent_requests:
            return 0.0
        
        cache_hits = sum(1 for r in recent_requests if r.get('from_cache', False))
        return cache_hits / len(recent_requests)
