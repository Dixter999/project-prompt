#!/usr/bin/env python3
"""
Suggestion Models for ProjectPrompt Rules System

This module contains shared data models for rule suggestions and pattern analysis.
These models are used across different analyzers and integrations to avoid circular imports.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
from src.models.rule_models import RuleItem


@dataclass
class PatternAnalysis:
    """Analysis of detected patterns in the codebase"""
    technology_stack: List[str] = field(default_factory=list)
    architectural_patterns: List[str] = field(default_factory=list)
    code_style_patterns: Dict[str, Any] = field(default_factory=dict)
    testing_patterns: List[str] = field(default_factory=list)
    documentation_patterns: List[str] = field(default_factory=list)
    security_patterns: List[str] = field(default_factory=list)
    inconsistencies: List[str] = field(default_factory=list)
    confidence_score: float = 0.0


@dataclass
class RuleSuggestion:
    """Individual rule suggestion with context and confidence"""
    suggested_rule: RuleItem
    reasoning: str
    confidence: float
    detected_patterns: List[str] = field(default_factory=list)
    affected_files: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    anti_examples: List[str] = field(default_factory=list)


@dataclass
class SuggestionContext:
    """Context for rule suggestions"""
    project_type: str
    size_category: str  # small, medium, large
    complexity_level: str  # simple, moderate, complex
    team_size: str  # solo, small, medium, large
    existing_rules_count: int = 0
    user_preferences: Dict[str, Any] = field(default_factory=dict)
