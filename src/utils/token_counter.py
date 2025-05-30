#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Token counter utility for Anthropic API cost estimation.

This module provides functionality to estimate token counts for text
and calculate costs based on Anthropic Claude model pricing.
"""

import re
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from src.utils.logger import get_logger

logger = get_logger()


@dataclass
class TokenEstimate:
    """Token count estimation with details."""
    input_tokens: int
    estimated_output_tokens: int
    total_tokens: int
    model: str
    input_cost: float
    output_cost: float
    total_cost: float


class AnthropicTokenCounter:
    """Token counter and cost estimator for Anthropic Claude models."""
    
    # Claude pricing (as of 2024) - per million tokens
    MODEL_PRICING = {
        "claude-3-haiku-20240307": {
            "input": 0.25,    # $0.25 per million input tokens
            "output": 1.25    # $1.25 per million output tokens
        },
        "claude-3-sonnet-20240229": {
            "input": 3.0,     # $3.00 per million input tokens
            "output": 15.0    # $15.00 per million output tokens
        },
        "claude-3-opus-20240229": {
            "input": 15.0,    # $15.00 per million input tokens
            "output": 75.0    # $75.00 per million output tokens
        }
    }
    
    def __init__(self, model: str = "claude-3-haiku-20240307"):
        """
        Initialize token counter.
        
        Args:
            model: Claude model name for pricing calculations
        """
        self.model = model
        if model not in self.MODEL_PRICING:
            logger.warning(f"Unknown model {model}, using haiku pricing")
            self.model = "claude-3-haiku-20240307"
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        This is a rough approximation based on Claude's tokenization patterns.
        Real token counting would require the actual tokenizer.
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        if not text:
            return 0
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Basic estimation: roughly 0.75 tokens per word for English text
        # For code, it tends to be closer to 1:1 ratio
        words = len(text.split())
        
        # Adjust for code content (more tokens per word)
        code_indicators = len(re.findall(r'[{}()\[\];=]', text))
        code_ratio = min(code_indicators / max(len(text), 1), 0.3)
        
        # Estimate tokens with code adjustment
        base_tokens = words * 0.75
        code_adjustment = words * code_ratio * 0.5
        
        estimated_tokens = int(base_tokens + code_adjustment)
        
        # Add buffer for formatting and structure
        return max(estimated_tokens, len(text) // 4)
    
    def estimate_group_analysis_tokens(self, project_path: str, group_data: Dict) -> TokenEstimate:
        """
        Estimate tokens needed for group analysis.
        
        Args:
            project_path: Path to the project root
            group_data: Group data containing files and metadata
            
        Returns:
            Token estimation with cost breakdown
        """
        import os
        
        # Estimate input tokens
        input_tokens = 0
        
        # Base prompt overhead (system prompt, instructions)
        input_tokens += 500  # Base system prompt
        
        # Group metadata
        group_name = group_data.get('name', '')
        group_files = group_data.get('files', [])
        
        input_tokens += self.estimate_tokens(f"Group: {group_name}")
        input_tokens += 100  # Metadata overhead
        
        # File content estimation
        files_processed = 0
        max_files = 10  # Limit to prevent excessive costs
        
        for file_info in group_files:
            if files_processed >= max_files:
                break
                
            if isinstance(file_info, dict):
                file_path = file_info.get('path', '')
                file_size = file_info.get('size', 0)
            else:
                file_path = str(file_info)
                file_size = 1000  # Default estimate
            
            # Try to read actual file content for better estimation
            full_path = os.path.join(project_path, file_path)
            actual_tokens = 0
            
            try:
                if os.path.exists(full_path) and os.path.isfile(full_path):
                    # Check file size limit (50KB max)
                    if os.path.getsize(full_path) <= 50000:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            actual_tokens = self.estimate_tokens(content)
                    else:
                        # File too large, use size-based estimation
                        actual_tokens = min(file_size // 3, 2000)
                else:
                    # File doesn't exist, use size-based estimation
                    actual_tokens = min(file_size // 3, 1000)
            except Exception:
                # Error reading file, use conservative estimate
                actual_tokens = min(file_size // 3, 1000)
            
            # Cap per file to prevent excessive costs
            file_tokens = min(actual_tokens, 2000)
            input_tokens += file_tokens
            
            # File path and metadata
            input_tokens += self.estimate_tokens(file_path) + 20
            files_processed += 1
        
        # Add estimation for remaining files if any
        remaining_files = len(group_files) - files_processed
        if remaining_files > 0:
            input_tokens += remaining_files * 200  # Conservative estimate for remaining files
        
        # Estimate output tokens (analysis response)
        estimated_output_tokens = min(1500 + (files_processed * 100), 3000)  # Scale with file count
        
        total_tokens = input_tokens + estimated_output_tokens
        
        # Calculate costs
        pricing = self.MODEL_PRICING[self.model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (estimated_output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        return TokenEstimate(
            input_tokens=input_tokens,
            estimated_output_tokens=estimated_output_tokens,
            total_tokens=total_tokens,
            model=self.model,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost
        )
    
    def estimate_file_analysis_tokens(self, file_path: str, content: str) -> TokenEstimate:
        """
        Estimate tokens for analyzing a single file.
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            Token estimation with cost breakdown
        """
        # Input tokens
        input_tokens = 300  # Base system prompt
        input_tokens += self.estimate_tokens(file_path)
        input_tokens += self.estimate_tokens(content)
        
        # Output tokens (file analysis)
        estimated_output_tokens = 800
        
        total_tokens = input_tokens + estimated_output_tokens
        
        # Calculate costs
        pricing = self.MODEL_PRICING[self.model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (estimated_output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        return TokenEstimate(
            input_tokens=input_tokens,
            estimated_output_tokens=estimated_output_tokens,
            total_tokens=total_tokens,
            model=self.model,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost
        )
    
    def format_cost_estimate(self, estimate: TokenEstimate) -> str:
        """
        Format cost estimate for display.
        
        Args:
            estimate: Token estimate to format
            
        Returns:
            Formatted cost string
        """
        return (
            f"📊 Token Estimate:\n"
            f"  • Input tokens: {estimate.input_tokens:,}\n"
            f"  • Output tokens: ~{estimate.estimated_output_tokens:,}\n"
            f"  • Total tokens: ~{estimate.total_tokens:,}\n"
            f"  • Model: {estimate.model}\n"
            f"💰 Cost Estimate:\n"
            f"  • Input cost: ${estimate.input_cost:.4f}\n"
            f"  • Output cost: ${estimate.output_cost:.4f}\n"
            f"  • Total cost: ${estimate.total_cost:.4f}"
        )
    
    def get_cost_warning_threshold(self) -> float:
        """
        Get cost threshold for showing warnings.
        
        Returns:
            Cost threshold in USD
        """
        return 0.10  # Warn if cost exceeds $0.10
    
    def should_warn_about_cost(self, estimate: TokenEstimate) -> bool:
        """
        Check if cost estimate warrants a warning.
        
        Args:
            estimate: Token estimate to check
            
        Returns:
            True if cost is high enough to warn about
        """
        return estimate.total_cost > self.get_cost_warning_threshold()


def get_token_counter(model: str = "claude-3-haiku-20240307") -> AnthropicTokenCounter:
    """
    Get a token counter instance.
    
    Args:
        model: Claude model name
        
    Returns:
        Token counter instance
    """
    return AnthropicTokenCounter(model)
