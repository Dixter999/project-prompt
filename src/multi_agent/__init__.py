"""
Multi-Agent System with Intelligent API Selection
Sistema Multi-Agente con Selección Inteligente de APIs
"""

from .task_classifier import (
    TaskClassifier, 
    TaskType, 
    SpecialCharacteristics,
    TaskAnalysisResult
)
from .linguistic_analyzer import (
    LinguisticPatternAnalyzer,
    LinguisticAnalysisResult,
    LinguisticIntensity
)
from .file_analyzer import (
    FileContextAnalyzer,
    FileContextAnalysisResult,
    ProjectType,
    TechnologyStack,
    FileMetadata,
    ProjectStructure
)
from .complexity_estimator import (
    ComplexityEstimator,
    ComplexityAnalysisResult,
    ComplexityDimension,
    RiskLevel,
    ComplexityMetrics
)
from .agent_specializations import (
    AgentSpecializationManager,
    AgentType,
    SpecializationArea,
    UseCaseCategory,
    AgentConfiguration,
    AgentStrength,
    AgentSpecialization
)
from .agent_selector import (
    AgentSelector,
    AgentOrchestrator,
    CollaborationEngine,
    AgentSelection,
    CollaborationPlan,
    OrchestrationResult,
    CollaborationStrategy,
    HandoffType
)

# FASE 3: Intelligent Scoring and Adaptive Decision System
from .intelligent_scoring_engine import (
    IntelligentScoringEngine,
    SpecializationScorer,
    PerformanceHistoryAnalyzer,
    TaskCharacteristicsEvaluator,
    ApiAvailabilityMonitor as ScoringApiMonitor,
    CostOptimizer,
    ScoreComponent,
    DetailedScore,
    PerformanceRecord,
    ApiHealthStatus
)

from .adaptive_decision_engine import (
    AdaptiveDecisionEngine,
    AgentSelectionFilter,
    StrategyDeterminer,
    ConfigurationOptimizer,
    FallbackDeterminer,
    ExecutionStrategy,
    DecisionConfidence,
    ExecutionDecision,
    AgentConfigurationOverride
)

from .api_health_monitor import (
    ApiHealthMonitor,
    HealthCheckResult,
    HealthCheckStatus,
    ApiEndpointConfig,
    api_health_monitor
)

from .system_prompt_generator import (
    SystemPromptGenerator,
    PromptGenerationContext,
    PromptTemplate,
    PromptComponent,
    system_prompt_generator
)

__all__ = [
    # Task Classifier
    'TaskClassifier',
    'TaskType', 
    'SpecialCharacteristics',
    'TaskAnalysisResult',
    
    # Linguistic Analyzer
    'LinguisticPatternAnalyzer',
    'LinguisticAnalysisResult',
    'LinguisticIntensity',
    
    # File Context Analyzer
    'FileContextAnalyzer',
    'FileContextAnalysisResult',
    'ProjectType',
    'TechnologyStack',
    'FileMetadata',
    'ProjectStructure',
    
    # Complexity Estimator
    'ComplexityEstimator',
    'ComplexityAnalysisResult',
    'ComplexityDimension',
    'RiskLevel',
    'ComplexityMetrics',
    
    # Agent Specializations (FASE 2)
    'AgentSpecializationManager',
    'AgentType',
    'SpecializationArea',
    'UseCaseCategory',
    'AgentConfiguration',
    'AgentStrength',
    'AgentSpecialization',
    
    # Agent Selector & Orchestrator (FASE 2)
    'AgentSelector',
    'AgentOrchestrator',
    'CollaborationEngine',
    'AgentSelection',
    'CollaborationPlan',
    'OrchestrationResult',
    'CollaborationStrategy',
    'HandoffType',
    
    # Intelligent Scoring Engine (FASE 3)
    'IntelligentScoringEngine',
    'SpecializationScorer',
    'PerformanceHistoryAnalyzer',
    'TaskCharacteristicsEvaluator',
    'ScoringApiMonitor',
    'CostOptimizer',
    'ScoreComponent',
    'DetailedScore',
    'PerformanceRecord',
    'ApiHealthStatus',
    
    # Adaptive Decision Engine (FASE 3)
    'AdaptiveDecisionEngine',
    'AgentSelectionFilter',
    'StrategyDeterminer',
    'ConfigurationOptimizer',
    'FallbackDeterminer',
    'ExecutionStrategy',
    'DecisionConfidence',
    'ExecutionDecision',
    'AgentConfigurationOverride',
    
    # API Health Monitor (FASE 3)
    'ApiHealthMonitor',
    'HealthCheckResult',
    'HealthCheckStatus',
    'ApiEndpointConfig',
    'api_health_monitor',
    
    # System Prompt Generator (FASE 3)
    'SystemPromptGenerator',
    'PromptGenerationContext',
    'PromptTemplate',
    'PromptComponent',
    'system_prompt_generator'
]
