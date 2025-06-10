"""
FASE 3: Motor de Decisión Adaptativo
Sistema que determina automáticamente la estrategia óptima de ejecución y configuración de agentes.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import statistics

from .task_classifier import TaskType, TaskAnalysisResult, SpecialCharacteristics
from .agent_specializations import AgentType, AgentConfiguration
from .agent_selector import CollaborationStrategy, AgentSelection, CollaborationPlan
from .intelligent_scoring_engine import IntelligentScoringEngine, DetailedScore


class ExecutionStrategy(Enum):
    """Estrategias de ejecución disponibles"""
    SINGLE_AGENT = "single_agent"
    SEQUENTIAL_MULTI = "sequential_multi"
    PARALLEL_MULTI = "parallel_multi"
    COLLABORATIVE_MULTI = "collaborative_multi"
    FALLBACK_CHAIN = "fallback_chain"


class DecisionConfidence(Enum):
    """Niveles de confianza en la decisión"""
    VERY_LOW = "very_low"      # < 0.3
    LOW = "low"                # 0.3 - 0.5
    MEDIUM = "medium"          # 0.5 - 0.7
    HIGH = "high"              # 0.7 - 0.85
    VERY_HIGH = "very_high"    # > 0.85


@dataclass
class AgentConfigurationOverride:
    """Configuración específica para un agente en un contexto"""
    agent_type: AgentType
    temperature_override: Optional[float] = None
    max_tokens_override: Optional[int] = None
    system_prompt_additions: List[str] = None
    timeout_override: Optional[int] = None
    retry_strategy: Optional[str] = None


@dataclass
class ExecutionDecision:
    """Decisión completa de ejecución"""
    strategy: ExecutionStrategy
    primary_agent: DetailedScore
    secondary_agents: List[DetailedScore]
    configuration_overrides: List[AgentConfigurationOverride]
    estimated_duration: float
    estimated_cost: float
    confidence_level: DecisionConfidence
    reasoning: List[str]
    fallback_options: List[AgentType]
    success_probability: float
    quality_expectation: float


class AgentSelectionFilter:
    """Filtros para selección de agentes"""
    
    @staticmethod
    def filter_available_agents(detailed_scores: List[DetailedScore]) -> List[DetailedScore]:
        """Filtra agentes disponibles (availability_score > 0)"""
        return [score for score in detailed_scores if score.availability_score > 0]
    
    @staticmethod
    def filter_by_cost_threshold(detailed_scores: List[DetailedScore], 
                                max_cost: float) -> List[DetailedScore]:
        """Filtra agentes que excedan el umbral de costo"""
        # En implementación real, calcularíamos el costo estimado
        # Por ahora, usamos cost_score como proxy
        return [score for score in detailed_scores if score.cost_score >= 0.3]
    
    @staticmethod
    def filter_by_minimum_competence(detailed_scores: List[DetailedScore], 
                                   min_specialization: float = 0.5) -> List[DetailedScore]:
        """Filtra agentes con competencia mínima en especialización"""
        return [score for score in detailed_scores 
                if score.specialization_score >= min_specialization]
    
    @staticmethod
    def filter_by_success_probability(detailed_scores: List[DetailedScore], 
                                    min_performance: float = 0.4) -> List[DetailedScore]:
        """Filtra agentes con probabilidad mínima de éxito"""
        return [score for score in detailed_scores 
                if score.performance_score >= min_performance]


class StrategyDeterminer:
    """Determinador de estrategia de ejecución"""
    
    def __init__(self):
        self.strategy_rules = self._initialize_strategy_rules()
    
    def _initialize_strategy_rules(self) -> Dict[str, Any]:
        """Inicializa reglas para determinación de estrategia"""
        return {
            'single_agent_criteria': {
                'max_complexity': 'medium',
                'min_primary_score': 0.7,
                'max_secondary_score_diff': 0.2,
                'simple_task_types': [TaskType.DOCUMENTATION, TaskType.CODE_MODIFICATION]
            },
            'sequential_criteria': {
                'analysis_to_implementation': [TaskType.CODE_ANALYSIS, TaskType.CODE_GENERATION],
                'implementation_to_docs': [TaskType.CODE_GENERATION, TaskType.DOCUMENTATION],
                'min_synergy_score': 0.6
            },
            'parallel_criteria': {
                'multiple_perspectives_tasks': [TaskType.ARCHITECTURE_REVIEW, TaskType.OPTIMIZATION],
                'independent_components': True,
                'time_critical': True
            },
            'collaborative_criteria': {
                'min_complexity': 'high',
                'requires_iteration': True,
                'high_stakes': True,
                'min_agents': 2
            }
        }
    
    def determine_optimal_strategy(self, task_analysis: TaskAnalysisResult, 
                                 detailed_scores: List[DetailedScore]) -> ExecutionStrategy:
        """Determina la estrategia óptima de ejecución"""
        
        if not detailed_scores:
            return ExecutionStrategy.SINGLE_AGENT
        
        primary_score = detailed_scores[0]
        complexity = task_analysis.complexity_level.value
        task_type = task_analysis.primary_task_type
        
        # 1. Verificar criterios para agente único
        if self._should_use_single_agent(task_analysis, detailed_scores):
            return ExecutionStrategy.SINGLE_AGENT
        
        # 2. Verificar criterios para estrategia secuencial
        if self._should_use_sequential(task_analysis, detailed_scores):
            return ExecutionStrategy.SEQUENTIAL_MULTI
        
        # 3. Verificar criterios para estrategia paralela
        if self._should_use_parallel(task_analysis, detailed_scores):
            return ExecutionStrategy.PARALLEL_MULTI
        
        # 4. Verificar criterios para estrategia colaborativa
        if self._should_use_collaborative(task_analysis, detailed_scores):
            return ExecutionStrategy.COLLABORATIVE_MULTI
        
        # 5. Default: agente único si no hay criterios claros
        return ExecutionStrategy.SINGLE_AGENT
    
    def _should_use_single_agent(self, task_analysis: TaskAnalysisResult, 
                               detailed_scores: List[DetailedScore]) -> bool:
        """Determina si usar un solo agente"""
        
        primary_score = detailed_scores[0]
        complexity = task_analysis.complexity_level.value
        
        # Criterios para agente único
        conditions = [
            # Complejidad simple o media
            complexity in ['minimal', 'low', 'medium'],
            
            # Score alto del agente primario
            primary_score.total_score > 0.7,
            
            # Gran diferencia con el segundo agente
            len(detailed_scores) < 2 or (detailed_scores[0].total_score - detailed_scores[1].total_score) > 0.2,
            
            # Tipos de task simples
            task_analysis.primary_task_type in [TaskType.DOCUMENTATION, TaskType.CODE_MODIFICATION],
            
            # No requiere múltiples perspectivas
            SpecialCharacteristics.REQUIRES_EXPLANATION not in task_analysis.special_characteristics
        ]
        
        # Necesita al menos 2 condiciones verdaderas
        return sum(conditions) >= 2
    
    def _should_use_sequential(self, task_analysis: TaskAnalysisResult, 
                             detailed_scores: List[DetailedScore]) -> bool:
        """Determina si usar estrategia secuencial"""
        
        # Verificar si hay múltiples tasks secundarios que se benefician de secuencia
        has_analysis_implementation = (
            task_analysis.primary_task_type == TaskType.CODE_ANALYSIS and
            TaskType.CODE_GENERATION in task_analysis.secondary_task_types
        )
        
        has_implementation_docs = (
            task_analysis.primary_task_type == TaskType.CODE_GENERATION and
            TaskType.DOCUMENTATION in task_analysis.secondary_task_types
        )
        
        # Al menos 2 agentes con scores decentes
        good_agents = len([s for s in detailed_scores if s.total_score > 0.5])
        
        return (has_analysis_implementation or has_implementation_docs) and good_agents >= 2
    
    def _should_use_parallel(self, task_analysis: TaskAnalysisResult, 
                           detailed_scores: List[DetailedScore]) -> bool:
        """Determina si usar estrategia paralela"""
        
        # Tasks que se benefician de múltiples perspectivas
        multi_perspective_tasks = [
            TaskType.ARCHITECTURE_REVIEW,
            TaskType.OPTIMIZATION,
            TaskType.CODE_ANALYSIS
        ]
        
        # Requiere velocidad
        requires_speed = SpecialCharacteristics.REQUIRES_SPEED in task_analysis.special_characteristics
        
        # Múltiples agentes competentes
        competent_agents = len([s for s in detailed_scores if s.total_score > 0.6])
        
        return (
            (task_analysis.primary_task_type in multi_perspective_tasks or requires_speed) and
            competent_agents >= 2
        )
    
    def _should_use_collaborative(self, task_analysis: TaskAnalysisResult, 
                                detailed_scores: List[DetailedScore]) -> bool:
        """Determina si usar estrategia colaborativa"""
        
        complexity = task_analysis.complexity_level.value
        
        # Alta complejidad
        high_complexity = complexity in ['high', 'critical']
        
        # Múltiples características especiales que requieren especialización diversa
        special_count = len(task_analysis.special_characteristics)
        
        # Múltiples tasks secundarios
        multi_secondary = len(task_analysis.secondary_task_types) >= 2
        
        # Al menos 2 agentes muy competentes
        excellent_agents = len([s for s in detailed_scores if s.total_score > 0.75])
        
        return high_complexity and (special_count >= 3 or multi_secondary) and excellent_agents >= 2


class ConfigurationOptimizer:
    """Optimizador de configuración dinámica de agentes"""
    
    def __init__(self):
        self.base_configurations = self._initialize_base_configurations()
        self.task_type_adjustments = self._initialize_task_adjustments()
        self.characteristic_adjustments = self._initialize_characteristic_adjustments()
    
    def _initialize_base_configurations(self) -> Dict[AgentType, Dict[str, Any]]:
        """Configuraciones base por agente"""
        return {
            AgentType.GEMINI: {
                'temperature': 0.1,
                'max_tokens': 8000,
                'timeout': 60,
                'retry_attempts': 3,
                'system_prompt_style': 'analytical'
            },
            AgentType.CLAUDE: {
                'temperature': 0.25,
                'max_tokens': 6000,
                'timeout': 45,
                'retry_attempts': 2,
                'system_prompt_style': 'implementation_focused'
            },
            AgentType.OPENAI: {
                'temperature': 0.5,
                'max_tokens': 4000,
                'timeout': 30,
                'retry_attempts': 2,
                'system_prompt_style': 'explanatory'
            }
        }
    
    def _initialize_task_adjustments(self) -> Dict[TaskType, Dict[str, Any]]:
        """Ajustes de configuración por tipo de task"""
        return {
            TaskType.CODE_ANALYSIS: {
                'temperature_modifier': -0.05,  # Más precisión
                'max_tokens_modifier': 1.2,     # Más espacio para análisis
                'system_prompt_addition': 'Focus on thorough analysis and detailed findings.'
            },
            TaskType.CODE_GENERATION: {
                'temperature_modifier': 0.0,    # Mantener balance
                'max_tokens_modifier': 1.1,
                'system_prompt_addition': 'Generate clean, production-ready code with proper documentation.'
            },
            TaskType.DEBUGGING: {
                'temperature_modifier': -0.1,   # Máxima precisión
                'max_tokens_modifier': 1.15,
                'system_prompt_addition': 'Provide step-by-step debugging analysis and clear solutions.'
            },
            TaskType.DOCUMENTATION: {
                'temperature_modifier': 0.1,    # Más naturalidad
                'max_tokens_modifier': 1.3,     # Más espacio para explicaciones
                'system_prompt_addition': 'Create clear, comprehensive documentation that is easy to understand.'
            },
            TaskType.OPTIMIZATION: {
                'temperature_modifier': -0.05,
                'max_tokens_modifier': 1.25,
                'system_prompt_addition': 'Focus on performance improvements and measurable optimizations.'
            }
        }
    
    def _initialize_characteristic_adjustments(self) -> Dict[SpecialCharacteristics, Dict[str, Any]]:
        """Ajustes por características especiales"""
        return {
            SpecialCharacteristics.REQUIRES_PRECISION: {
                'temperature_modifier': -0.1,
                'system_prompt_addition': 'Prioritize accuracy and precision in all responses.'
            },
            SpecialCharacteristics.REQUIRES_CREATIVITY: {
                'temperature_modifier': 0.15,
                'system_prompt_addition': 'Think creatively and provide innovative solutions.'
            },
            SpecialCharacteristics.REQUIRES_SPEED: {
                'timeout_modifier': -15,  # Menos tiempo
                'max_tokens_modifier': 0.8,  # Respuestas más concisas
                'system_prompt_addition': 'Provide concise, direct responses quickly.'
            },
            SpecialCharacteristics.REQUIRES_EXPLANATION: {
                'max_tokens_modifier': 1.4,
                'system_prompt_addition': 'Provide detailed explanations for all decisions and processes.'
            },
            SpecialCharacteristics.MULTI_FILE_ANALYSIS: {
                'max_tokens_modifier': 1.5,
                'timeout_modifier': 30,  # Más tiempo para procesar
                'system_prompt_addition': 'Handle large codebases efficiently, focusing on key components.'
            }
        }
    
    def generate_optimized_configuration(self, agent_type: AgentType, 
                                       task_analysis: TaskAnalysisResult) -> AgentConfigurationOverride:
        """Genera configuración optimizada para un agente específico"""
        
        base_config = self.base_configurations.get(agent_type, {})
        
        # Comenzar con configuración base
        temperature = base_config.get('temperature', 0.3)
        max_tokens = base_config.get('max_tokens', 4000)
        timeout = base_config.get('timeout', 30)
        system_prompt_additions = []
        
        # Aplicar ajustes por tipo de task
        task_adjustments = self.task_type_adjustments.get(task_analysis.primary_task_type, {})
        
        temperature += task_adjustments.get('temperature_modifier', 0)
        max_tokens = int(max_tokens * task_adjustments.get('max_tokens_modifier', 1.0))
        timeout += task_adjustments.get('timeout_modifier', 0)
        
        if 'system_prompt_addition' in task_adjustments:
            system_prompt_additions.append(task_adjustments['system_prompt_addition'])
        
        # Aplicar ajustes por características especiales
        for characteristic in task_analysis.special_characteristics:
            char_adjustments = self.characteristic_adjustments.get(characteristic, {})
            
            temperature += char_adjustments.get('temperature_modifier', 0)
            max_tokens = int(max_tokens * char_adjustments.get('max_tokens_modifier', 1.0))
            timeout += char_adjustments.get('timeout_modifier', 0)
            
            if 'system_prompt_addition' in char_adjustments:
                system_prompt_additions.append(char_adjustments['system_prompt_addition'])
        
        # Ajustes por complejidad
        complexity_adjustments = {
            'minimal': {'temperature_modifier': 0, 'max_tokens_modifier': 0.8},
            'low': {'temperature_modifier': 0, 'max_tokens_modifier': 0.9},
            'medium': {'temperature_modifier': 0, 'max_tokens_modifier': 1.0},
            'high': {'temperature_modifier': -0.05, 'max_tokens_modifier': 1.2},
            'critical': {'temperature_modifier': -0.1, 'max_tokens_modifier': 1.4}
        }
        
        complexity_adj = complexity_adjustments.get(task_analysis.complexity_level.value, {})
        temperature += complexity_adj.get('temperature_modifier', 0)
        max_tokens = int(max_tokens * complexity_adj.get('max_tokens_modifier', 1.0))
        
        # Asegurar límites razonables
        temperature = max(0.01, min(1.0, temperature))
        max_tokens = max(1000, min(16000, max_tokens))
        timeout = max(15, min(300, timeout))
        
        return AgentConfigurationOverride(
            agent_type=agent_type,
            temperature_override=temperature,
            max_tokens_override=max_tokens,
            system_prompt_additions=system_prompt_additions,
            timeout_override=timeout,
            retry_strategy="exponential_backoff"
        )


class FallbackDeterminer:
    """Determinador de opciones de fallback"""
    
    def determine_fallback_chain(self, primary_agent: AgentType, 
                               detailed_scores: List[DetailedScore]) -> List[AgentType]:
        """Determina cadena de fallback basada en scores y complementariedad"""
        
        # Excluir agente primario
        fallback_candidates = [s for s in detailed_scores if s.agent_type != primary_agent]
        
        # Ordenar por score total
        fallback_candidates.sort(key=lambda x: x.total_score, reverse=True)
        
        # Tomar top 2 como fallbacks
        fallback_chain = [s.agent_type for s in fallback_candidates[:2]]
        
        # Asegurar diversidad en la cadena de fallback
        if len(fallback_chain) == 2 and self._are_too_similar(primary_agent, fallback_chain[0]):
            # Si el primer fallback es muy similar al primario, priorizar el segundo
            if len(fallback_candidates) > 1:
                fallback_chain = [fallback_chain[1], fallback_chain[0]]
        
        return fallback_chain
    
    def _are_too_similar(self, agent1: AgentType, agent2: AgentType) -> bool:
        """Determina si dos agentes son demasiado similares para fallback"""
        
        # Definir similaridades problemáticas
        similar_pairs = [
            (AgentType.GEMINI, AgentType.CLAUDE),  # Ambos técnicos
        ]
        
        return (agent1, agent2) in similar_pairs or (agent2, agent1) in similar_pairs


class AdaptiveDecisionEngine:
    """Motor principal de decisión adaptativo"""
    
    def __init__(self):
        self.scoring_engine = IntelligentScoringEngine()
        self.strategy_determiner = StrategyDeterminer()
        self.configuration_optimizer = ConfigurationOptimizer()
        self.fallback_determiner = FallbackDeterminer()
        self.agent_filter = AgentSelectionFilter()
    
    def make_execution_decision(self, task_analysis: TaskAnalysisResult, 
                              budget_limit: Optional[float] = None) -> ExecutionDecision:
        """Toma la decisión completa de ejecución"""
        
        reasoning = []
        
        # Paso 1: Calcular scores detallados
        detailed_scores = self.scoring_engine.calculate_detailed_scores(task_analysis)
        reasoning.append(f"Evaluados {len(detailed_scores)} agentes disponibles")
        
        # Paso 2: Aplicar filtros críticos
        available_agents = self.agent_filter.filter_available_agents(detailed_scores)
        if len(available_agents) != len(detailed_scores):
            reasoning.append(f"Filtrados por disponibilidad: {len(available_agents)} agentes disponibles")
        
        competent_agents = self.agent_filter.filter_by_minimum_competence(available_agents)
        if len(competent_agents) != len(available_agents):
            reasoning.append(f"Filtrados por competencia mínima: {len(competent_agents)} agentes competentes")
        
        if budget_limit:
            cost_filtered = self.agent_filter.filter_by_cost_threshold(competent_agents, budget_limit)
            if len(cost_filtered) != len(competent_agents):
                reasoning.append(f"Aplicado filtro de presupuesto: {len(cost_filtered)} agentes en presupuesto")
            competent_agents = cost_filtered
        
        if not competent_agents:
            # Fallback: usar el mejor agente disponible aunque no cumpla todos los criterios
            competent_agents = available_agents[:1] if available_agents else detailed_scores[:1]
            reasoning.append("FALLBACK: Usando mejor agente disponible a pesar de limitaciones")
        
        # Paso 3: Determinar estrategia de ejecución
        strategy = self.strategy_determiner.determine_optimal_strategy(task_analysis, competent_agents)
        reasoning.append(f"Estrategia seleccionada: {strategy.value}")
        
        # Paso 4: Seleccionar agentes
        primary_agent = competent_agents[0]
        secondary_agents = []
        
        if strategy != ExecutionStrategy.SINGLE_AGENT:
            # Determinar cuántos agentes secundarios necesitamos
            if strategy == ExecutionStrategy.SEQUENTIAL_MULTI:
                secondary_agents = competent_agents[1:2]  # Un agente secundario
            elif strategy in [ExecutionStrategy.PARALLEL_MULTI, ExecutionStrategy.COLLABORATIVE_MULTI]:
                secondary_agents = competent_agents[1:3]  # Hasta dos agentes secundarios
            
            reasoning.append(f"Agentes secundarios: {len(secondary_agents)}")
        
        # Paso 5: Generar configuraciones optimizadas
        configuration_overrides = []
        all_agents = [primary_agent] + secondary_agents
        
        for agent_score in all_agents:
            config_override = self.configuration_optimizer.generate_optimized_configuration(
                agent_score.agent_type, task_analysis
            )
            configuration_overrides.append(config_override)
        
        # Paso 6: Determinar fallbacks
        fallback_options = self.fallback_determiner.determine_fallback_chain(
            primary_agent.agent_type, detailed_scores
        )
        
        # Paso 7: Calcular métricas
        estimated_duration = self._estimate_execution_duration(strategy, all_agents, task_analysis)
        estimated_cost = self._estimate_execution_cost(all_agents, task_analysis)
        success_probability = self._calculate_success_probability(all_agents)
        quality_expectation = self._calculate_quality_expectation(all_agents, strategy)
        
        # Paso 8: Determinar nivel de confianza
        confidence_level = self._determine_confidence_level(primary_agent, secondary_agents, strategy)
        
        reasoning.extend([
            f"Duración estimada: {estimated_duration:.1f} segundos",
            f"Costo estimado: ${estimated_cost:.4f}",
            f"Probabilidad de éxito: {success_probability:.1%}",
            f"Expectativa de calidad: {quality_expectation:.1%}"
        ])
        
        return ExecutionDecision(
            strategy=strategy,
            primary_agent=primary_agent,
            secondary_agents=secondary_agents,
            configuration_overrides=configuration_overrides,
            estimated_duration=estimated_duration,
            estimated_cost=estimated_cost,
            confidence_level=confidence_level,
            reasoning=reasoning,
            fallback_options=fallback_options,
            success_probability=success_probability,
            quality_expectation=quality_expectation
        )
    
    def _estimate_execution_duration(self, strategy: ExecutionStrategy, 
                                   agents: List[DetailedScore], 
                                   task_analysis: TaskAnalysisResult) -> float:
        """Estima duración de ejecución en segundos"""
        
        base_duration = {
            'minimal': 30,
            'low': 60,
            'medium': 120,
            'high': 300,
            'critical': 600
        }.get(task_analysis.complexity_level.value, 120)
        
        strategy_multipliers = {
            ExecutionStrategy.SINGLE_AGENT: 1.0,
            ExecutionStrategy.SEQUENTIAL_MULTI: 1.8,  # Secuencial toma más tiempo
            ExecutionStrategy.PARALLEL_MULTI: 1.2,    # Paralelo es más eficiente
            ExecutionStrategy.COLLABORATIVE_MULTI: 2.5, # Colaborativo requiere iteraciones
            ExecutionStrategy.FALLBACK_CHAIN: 1.3
        }
        
        multiplier = strategy_multipliers.get(strategy, 1.0)
        
        # Ajustar por velocidad promedio de agentes
        if agents:
            avg_speed = statistics.mean(agent.performance_score for agent in agents)
            speed_multiplier = 2.0 - avg_speed  # Mejor performance = menos tiempo
            multiplier *= speed_multiplier
        
        return base_duration * multiplier
    
    def _estimate_execution_cost(self, agents: List[DetailedScore], 
                               task_analysis: TaskAnalysisResult) -> float:
        """Estima costo de ejecución en USD"""
        
        # Costos base por agente (por token estimado)
        token_costs = {
            AgentType.GEMINI: 0.0001,
            AgentType.CLAUDE: 0.0002,
            AgentType.OPENAI: 0.00015
        }
        
        # Estimar tokens por complejidad
        base_tokens = {
            'minimal': 1500,
            'low': 3000,
            'medium': 5000,
            'high': 8000,
            'critical': 12000
        }.get(task_analysis.complexity_level.value, 5000)
        
        total_cost = 0.0
        for agent in agents:
            agent_cost = token_costs.get(agent.agent_type, 0.00015)
            agent_tokens = base_tokens * (1.0 + (1.0 - agent.cost_score) * 0.5)  # Agentes menos eficientes usan más tokens
            total_cost += agent_cost * agent_tokens
        
        return total_cost
    
    def _calculate_success_probability(self, agents: List[DetailedScore]) -> float:
        """Calcula probabilidad de éxito basada en agentes seleccionados"""
        
        if not agents:
            return 0.5
        
        # Usar el score del agente primario como base
        primary_score = agents[0].total_score
        
        # Bonificación por agentes adicionales (redundancia)
        redundancy_bonus = min(0.1 * (len(agents) - 1), 0.2)
        
        success_prob = primary_score + redundancy_bonus
        return min(success_prob, 0.95)  # Máximo 95% para ser realista
    
    def _calculate_quality_expectation(self, agents: List[DetailedScore], 
                                     strategy: ExecutionStrategy) -> float:
        """Calcula expectativa de calidad del resultado"""
        
        if not agents:
            return 0.5
        
        # Calidad base del agente primario
        base_quality = agents[0].specialization_score
        
        # Bonificación por estrategia
        strategy_bonuses = {
            ExecutionStrategy.SINGLE_AGENT: 0.0,
            ExecutionStrategy.SEQUENTIAL_MULTI: 0.1,    # Refinamiento secuencial
            ExecutionStrategy.PARALLEL_MULTI: 0.05,     # Múltiples perspectivas
            ExecutionStrategy.COLLABORATIVE_MULTI: 0.15, # Iteración y mejora
            ExecutionStrategy.FALLBACK_CHAIN: 0.02
        }
        
        strategy_bonus = strategy_bonuses.get(strategy, 0.0)
        
        # Bonificación por múltiples agentes competentes
        if len(agents) > 1:
            secondary_quality = statistics.mean(agent.specialization_score for agent in agents[1:])
            multi_agent_bonus = secondary_quality * 0.1
        else:
            multi_agent_bonus = 0.0
        
        quality = base_quality + strategy_bonus + multi_agent_bonus
        return min(quality, 0.98)  # Máximo 98% para ser realista
    
    def _determine_confidence_level(self, primary_agent: DetailedScore, 
                                  secondary_agents: List[DetailedScore], 
                                  strategy: ExecutionStrategy) -> DecisionConfidence:
        """Determina nivel de confianza en la decisión"""
        
        # Factores que afectan la confianza
        primary_score = primary_agent.total_score
        primary_confidence = primary_agent.confidence_level
        
        # Confianza base del agente primario
        base_confidence = (primary_score + primary_confidence) / 2
        
        # Bonificaciones por agentes secundarios
        if secondary_agents:
            secondary_scores = [agent.total_score for agent in secondary_agents]
            if secondary_scores:
                avg_secondary = statistics.mean(secondary_scores)
                base_confidence += avg_secondary * 0.1
        
        # Ajuste por estrategia
        strategy_confidence_modifiers = {
            ExecutionStrategy.SINGLE_AGENT: 0.0,
            ExecutionStrategy.SEQUENTIAL_MULTI: 0.05,
            ExecutionStrategy.PARALLEL_MULTI: 0.03,
            ExecutionStrategy.COLLABORATIVE_MULTI: 0.1,
            ExecutionStrategy.FALLBACK_CHAIN: -0.05  # Menos confianza si necesitamos fallback
        }
        
        confidence_modifier = strategy_confidence_modifiers.get(strategy, 0.0)
        final_confidence = base_confidence + confidence_modifier
        
        # Mapear a enum
        if final_confidence < 0.3:
            return DecisionConfidence.VERY_LOW
        elif final_confidence < 0.5:
            return DecisionConfidence.LOW
        elif final_confidence < 0.7:
            return DecisionConfidence.MEDIUM
        elif final_confidence < 0.85:
            return DecisionConfidence.HIGH
        else:
            return DecisionConfidence.VERY_HIGH
