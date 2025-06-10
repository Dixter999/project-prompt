"""
Sistema Multi-Agente - FASE 2: Selector y Orquestador de Agentes
Componente que selecciona los agentes óptimos y orquesta su colaboración.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
import json
from datetime import datetime

from .agent_specializations import (
    AgentSpecializationManager, AgentType, SpecializationArea, 
    UseCaseCategory, AgentConfiguration
)
from .task_classifier import TaskType, TaskAnalysisResult, SpecialCharacteristics


class CollaborationStrategy(Enum):
    """Estrategias de colaboración entre agentes"""
    SINGLE = "single"                    # Un solo agente
    SEQUENTIAL = "sequential"            # Agentes en secuencia
    PARALLEL = "parallel"               # Agentes en paralelo
    COLLABORATIVE = "collaborative"      # Colaboración iterativa
    VALIDATION = "validation"           # Un agente valida el trabajo del otro


class HandoffType(Enum):
    """Tipos de handoff entre agentes"""
    ANALYSIS_TO_IMPLEMENTATION = "analysis_to_implementation"
    IMPLEMENTATION_TO_DOCUMENTATION = "implementation_to_documentation"
    ANALYSIS_TO_EXPLANATION = "analysis_to_explanation"
    GENERATION_TO_VALIDATION = "generation_to_validation"
    COMPLEX_TO_REFINEMENT = "complex_to_refinement"


@dataclass
class AgentSelection:
    """Selección de agente con justificación"""
    agent_type: AgentType
    confidence_score: float
    specialization_match: float
    configuration: AgentConfiguration
    reasoning: List[str]
    expected_performance: Dict[str, float]


@dataclass
class CollaborationPlan:
    """Plan de colaboración entre agentes"""
    strategy: CollaborationStrategy
    agents: List[AgentSelection]
    execution_sequence: List[AgentType]
    handoff_points: List[Tuple[AgentType, AgentType, HandoffType]]
    estimated_duration: float
    synergy_score: float
    risk_factors: List[str]
    success_metrics: Dict[str, float]


@dataclass
class OrchestrationResult:
    """Resultado de la orquestación de agentes"""
    primary_agent: AgentSelection
    collaboration_plan: Optional[CollaborationPlan]
    alternative_options: List[AgentSelection]
    optimization_suggestions: List[str]
    estimated_cost: float
    estimated_quality: float


class AgentSelector:
    """
    Selector inteligente de agentes basado en análisis de tasks y especializaciones
    """
    
    def __init__(self):
        self.specialization_manager = AgentSpecializationManager()
        self._initialize_selection_weights()
        self._initialize_task_to_specialization_mapping()
    
    def _initialize_selection_weights(self):
        """Inicializa pesos para la selección de agentes"""
        self.selection_weights = {
            'specialization_match': 0.35,      # Qué tan bien el agente se especializa en el área
            'task_complexity_fit': 0.25,       # Qué tan bien maneja la complejidad
            'performance_history': 0.20,       # Métricas históricas de rendimiento
            'collaboration_potential': 0.15,   # Potencial de colaboración con otros agentes
            'resource_efficiency': 0.05        # Eficiencia en uso de recursos
        }
    
    def _initialize_task_to_specialization_mapping(self):
        """Mapea tipos de task a áreas de especialización"""
        self.task_specialization_map = {
            TaskType.CODE_ANALYSIS: [
                SpecializationArea.CODE_ANALYSIS,
                SpecializationArea.SECURITY_AUDIT,
                SpecializationArea.PERFORMANCE_ANALYSIS
            ],
            TaskType.CODE_GENERATION: [
                SpecializationArea.CODE_GENERATION,
                SpecializationArea.ARCHITECTURE_DESIGN
            ],
            TaskType.CODE_MODIFICATION: [
                SpecializationArea.CODE_REFACTORING,
                SpecializationArea.CODE_GENERATION
            ],
            TaskType.DEBUGGING: [
                SpecializationArea.DEBUGGING,
                SpecializationArea.CODE_ANALYSIS
            ],
            TaskType.DOCUMENTATION: [
                SpecializationArea.DOCUMENTATION,
                SpecializationArea.TUTORIAL_CREATION
            ],
            TaskType.OPTIMIZATION: [
                SpecializationArea.PERFORMANCE_ANALYSIS,
                SpecializationArea.CODE_REFACTORING
            ],
            TaskType.TESTING: [
                SpecializationArea.CODE_ANALYSIS,
                SpecializationArea.CODE_GENERATION
            ],
            TaskType.ARCHITECTURE_REVIEW: [
                SpecializationArea.ARCHITECTURE_DESIGN,
                SpecializationArea.CODE_ANALYSIS
            ]
        }
    
    def select_optimal_agent(self, task_analysis: TaskAnalysisResult) -> AgentSelection:
        """
        Selecciona el agente óptimo para una tarea específica
        
        Args:
            task_analysis: Resultado del análisis de tarea de la Fase 1
            
        Returns:
            AgentSelection con el agente óptimo y justificación
        """
        # Obtener áreas de especialización relevantes
        specialization_areas = self.task_specialization_map.get(
            task_analysis.primary_task_type, []
        )
        
        agent_scores = {}
        
        for agent_type in AgentType:
            score = self._calculate_agent_score(
                agent_type, task_analysis, specialization_areas
            )
            agent_scores[agent_type] = score
        
        # Seleccionar el agente con mayor score
        best_agent = max(agent_scores, key=agent_scores.get)
        best_score = agent_scores[best_agent]
        
        # Obtener configuración óptima y construir selección
        config = self.specialization_manager.get_optimal_configuration(best_agent)
        
        # Generar reasoning
        reasoning = self._generate_selection_reasoning(
            best_agent, task_analysis, specialization_areas, best_score
        )
        
        # Calcular rendimiento esperado
        expected_performance = self._calculate_expected_performance(
            best_agent, task_analysis
        )
        
        return AgentSelection(
            agent_type=best_agent,
            confidence_score=best_score,
            specialization_match=self._get_specialization_match_score(
                best_agent, specialization_areas
            ),
            configuration=config,
            reasoning=reasoning,
            expected_performance=expected_performance
        )
    
    def _calculate_agent_score(self, agent_type: AgentType, 
                             task_analysis: TaskAnalysisResult,
                             specialization_areas: List[SpecializationArea]) -> float:
        """Calcula el score de idoneidad de un agente para una tarea"""
        
        # 1. Score de especialización
        specialization_score = self._get_specialization_match_score(
            agent_type, specialization_areas
        )
        
        # 2. Score de ajuste a complejidad
        complexity_score = self._get_complexity_fit_score(
            agent_type, task_analysis
        )
        
        # 3. Score de rendimiento histórico
        performance_score = self._get_performance_score(agent_type)
        
        # 4. Score de potencial de colaboración
        collaboration_score = self._get_collaboration_score(
            agent_type, task_analysis
        )
        
        # 5. Score de eficiencia de recursos
        efficiency_score = self._get_efficiency_score(
            agent_type, task_analysis
        )
        
        # Combinar scores con pesos
        total_score = (
            specialization_score * self.selection_weights['specialization_match'] +
            complexity_score * self.selection_weights['task_complexity_fit'] +
            performance_score * self.selection_weights['performance_history'] +
            collaboration_score * self.selection_weights['collaboration_potential'] +
            efficiency_score * self.selection_weights['resource_efficiency']
        )
        
        return min(total_score, 1.0)  # Asegurar que no exceda 1.0
    
    def _get_specialization_match_score(self, agent_type: AgentType,
                                      specialization_areas: List[SpecializationArea]) -> float:
        """Calcula qué tan bien las especializaciones del agente coinciden con las requeridas"""
        if not specialization_areas:
            return 0.5  # Score neutral si no hay áreas específicas
        
        agent_strengths = self.specialization_manager.get_agent_strengths(agent_type)
        
        max_score = 0.0
        for area in specialization_areas:
            area_strengths = [s for s in agent_strengths if s.area == area]
            if area_strengths:
                # Tomar la mejor fortaleza en esta área
                best_strength = max(area_strengths, key=lambda s: s.proficiency_score)
                area_score = best_strength.proficiency_score * best_strength.confidence_level
                max_score = max(max_score, area_score)
        
        return max_score
    
    def _get_complexity_fit_score(self, agent_type: AgentType,
                                task_analysis: TaskAnalysisResult) -> float:
        """Evalúa qué tan bien el agente maneja la complejidad de la tarea"""
        
        # Mapear complexity_level a score numérico
        complexity_map = {
            'minimal': 0.1,
            'low': 0.3,
            'moderate': 0.5,
            'high': 0.7,
            'critical': 0.9
        }
        
        task_complexity = complexity_map.get(
            task_analysis.complexity_level.value, 0.5
        )
        
        # Preferencias de complejidad por agente
        agent_complexity_preferences = {
            AgentType.GEMINI: {
                'optimal_range': (0.6, 1.0),    # Prefiere tareas complejas
                'tolerance': 0.9
            },
            AgentType.CLAUDE: {
                'optimal_range': (0.4, 0.8),    # Versátil en complejidad media-alta
                'tolerance': 0.95
            },
            AgentType.OPENAI: {
                'optimal_range': (0.1, 0.6),    # Mejor en tareas simples-medias
                'tolerance': 0.85
            }
        }
        
        prefs = agent_complexity_preferences.get(agent_type)
        if not prefs:
            return 0.5
        
        optimal_min, optimal_max = prefs['optimal_range']
        
        if optimal_min <= task_complexity <= optimal_max:
            return prefs['tolerance']
        else:
            # Calcular penalización por estar fuera del rango óptimo
            distance = min(
                abs(task_complexity - optimal_min),
                abs(task_complexity - optimal_max)
            )
            penalty = distance * 0.3
            return max(prefs['tolerance'] - penalty, 0.1)
    
    def _get_performance_score(self, agent_type: AgentType) -> float:
        """Obtiene el score de rendimiento histórico del agente"""
        spec = self.specialization_manager.get_agent_specialization(agent_type)
        if not spec:
            return 0.5
        
        # Promedio ponderado de métricas de rendimiento
        metrics = spec.performance_metrics
        weights = {
            'accuracy': 0.4,
            'depth': 0.3,
            'speed': 0.2,
            'consistency': 0.1
        }
        
        weighted_score = sum(
            metrics.get(metric, 0.5) * weight 
            for metric, weight in weights.items()
        )
        
        return weighted_score
    
    def _get_collaboration_score(self, agent_type: AgentType,
                               task_analysis: TaskAnalysisResult) -> float:
        """Evalúa el potencial de colaboración del agente"""
        
        # Si hay tipos de task secundarios, la colaboración es más valiosa
        if not task_analysis.secondary_task_types:
            return 0.5  # Score neutral para tareas individuales
        
        spec = self.specialization_manager.get_agent_specialization(agent_type)
        if not spec:
            return 0.5
        
        # Promedio de afinidad de colaboración con otros agentes
        collaboration_scores = list(spec.collaboration_affinity.values())
        if collaboration_scores:
            return sum(collaboration_scores) / len(collaboration_scores)
        
        return 0.5
    
    def _get_efficiency_score(self, agent_type: AgentType,
                            task_analysis: TaskAnalysisResult) -> float:
        """Evalúa la eficiencia de recursos del agente para la tarea"""
        
        # Mapear características especiales a requerimientos de eficiencia
        efficiency_requirements = {
            SpecialCharacteristics.REQUIRES_SPEED: 0.9,
            SpecialCharacteristics.REQUIRES_PRECISION: 0.7,
            SpecialCharacteristics.REQUIRES_CREATIVITY: 0.6,
            SpecialCharacteristics.REQUIRES_EXPLANATION: 0.5
        }
        
        # Eficiencia por agente (basada en configuración y características)
        agent_efficiency = {
            AgentType.GEMINI: 0.78,    # Algo más lento pero muy preciso
            AgentType.CLAUDE: 0.85,    # Balance entre velocidad y calidad
            AgentType.OPENAI: 0.92     # Rápido para tareas de documentación
        }
        
        base_efficiency = agent_efficiency.get(agent_type, 0.5)
        
        # Ajustar basado en características especiales
        if task_analysis.special_characteristics:
            for characteristic in task_analysis.special_characteristics:
                required_efficiency = efficiency_requirements.get(characteristic, 0.5)
                # Si el agente no cumple bien con el requerimiento de eficiencia, penalizar
                if base_efficiency < required_efficiency:
                    base_efficiency *= 0.8
        
        return base_efficiency
    
    def _generate_selection_reasoning(self, agent_type: AgentType,
                                    task_analysis: TaskAnalysisResult,
                                    specialization_areas: List[SpecializationArea],
                                    score: float) -> List[str]:
        """Genera las razones por las que se seleccionó este agente"""
        
        reasoning = []
        
        # Razón principal basada en especialización
        primary_area = specialization_areas[0] if specialization_areas else None
        if primary_area:
            area_name = primary_area.value.replace('_', ' ').title()
            reasoning.append(f"Especialización fuerte en {area_name}")
        
        # Razón basada en tipo de tarea
        task_name = task_analysis.primary_task_type.value.replace('_', ' ').title()
        reasoning.append(f"Óptimo para tareas de {task_name}")
        
        # Razón basada en complejidad
        complexity = task_analysis.complexity_level.value
        if agent_type == AgentType.GEMINI and complexity in ['high', 'critical']:
            reasoning.append("Excelente para análisis complejos y profundos")
        elif agent_type == AgentType.CLAUDE and complexity in ['moderate', 'high']:
            reasoning.append("Ideal para implementaciones estructuradas")
        elif agent_type == AgentType.OPENAI and complexity in ['minimal', 'low']:
            reasoning.append("Eficiente para documentación y explicaciones claras")
        
        # Razón basada en características especiales
        if task_analysis.special_characteristics:
            for characteristic in task_analysis.special_characteristics:
                if characteristic == SpecialCharacteristics.REQUIRES_PRECISION and agent_type == AgentType.GEMINI:
                    reasoning.append("Precisión excepcional en análisis detallados")
                elif characteristic == SpecialCharacteristics.REQUIRES_SPEED and agent_type == AgentType.OPENAI:
                    reasoning.append("Velocidad óptima para tareas rápidas")
                elif characteristic == SpecialCharacteristics.REQUIRES_CREATIVITY and agent_type == AgentType.OPENAI:
                    reasoning.append("Creatividad en documentación y explicaciones")
        
        # Razón basada en score
        if score > 0.8:
            reasoning.append("Score de confianza muy alto")
        elif score > 0.6:
            reasoning.append("Score de confianza sólido")
        
        return reasoning
    
    def _calculate_expected_performance(self, agent_type: AgentType,
                                      task_analysis: TaskAnalysisResult) -> Dict[str, float]:
        """Calcula el rendimiento esperado del agente para esta tarea"""
        
        spec = self.specialization_manager.get_agent_specialization(agent_type)
        base_metrics = spec.performance_metrics if spec else {
            'accuracy': 0.5, 'depth': 0.5, 'speed': 0.5, 'consistency': 0.5
        }
        
        # Ajustar métricas basadas en características de la tarea
        adjusted_metrics = base_metrics.copy()
        
        # Ajustar por complejidad
        complexity_level = task_analysis.complexity_level.value
        if complexity_level in ['high', 'critical']:
            # Tareas complejas pueden reducir velocidad pero aumentar profundidad
            adjusted_metrics['speed'] *= 0.9
            adjusted_metrics['depth'] *= 1.1
        elif complexity_level in ['minimal', 'low']:
            # Tareas simples pueden aumentar velocidad
            adjusted_metrics['speed'] *= 1.1
        
        # Ajustar por características especiales
        for characteristic in task_analysis.special_characteristics:
            if characteristic == SpecialCharacteristics.REQUIRES_PRECISION:
                adjusted_metrics['accuracy'] *= 1.1
                adjusted_metrics['speed'] *= 0.95
            elif characteristic == SpecialCharacteristics.REQUIRES_SPEED:
                adjusted_metrics['speed'] *= 1.15
                adjusted_metrics['depth'] *= 0.95
        
        # Asegurar que los valores no excedan 1.0
        for key in adjusted_metrics:
            adjusted_metrics[key] = min(adjusted_metrics[key], 1.0)
        
        return adjusted_metrics




class AgentOrchestrator:
    """
    Orquestador de colaboración entre múltiples agentes
    Gestiona la coordinación, handoffs y optimización de workflows multi-agente
    """
    
    def __init__(self):
        self.agent_selector = AgentSelector()
        self.specialization_manager = AgentSpecializationManager()
        self.collaboration_engine = CollaborationEngine()
    
    def orchestrate_collaboration(self, task_analysis: TaskAnalysisResult) -> OrchestrationResult:
        """
        Orquesta la colaboración óptima de agentes para una tarea
        
        Args:
            task_analysis: Resultado del análisis de tarea
            
        Returns:
            OrchestrationResult con plan de colaboración completo
        """
        
        # Paso 1: Seleccionar agente primario
        primary_agent = self.agent_selector.select_optimal_agent(task_analysis)
        
        # Paso 2: Determinar si se necesita colaboración
        collaboration_plan = None
        if self._requires_collaboration(task_analysis):
            collaboration_plan = self._create_collaboration_plan(task_analysis, primary_agent)
        
        # Paso 3: Generar alternativas
        alternatives = self._generate_alternatives(task_analysis, primary_agent.agent_type)
        
        # Paso 4: Generar sugerencias de optimización
        optimizations = self._generate_optimization_suggestions(
            task_analysis, primary_agent, collaboration_plan
        )
        
        # Paso 5: Estimar métricas
        estimated_cost = self._estimate_cost(primary_agent, collaboration_plan)
        estimated_quality = self._estimate_quality(primary_agent, collaboration_plan)
        
        return OrchestrationResult(
            primary_agent=primary_agent,
            collaboration_plan=collaboration_plan,
            alternative_options=alternatives,
            optimization_suggestions=optimizations,
            estimated_cost=estimated_cost,
            estimated_quality=estimated_quality
        )
    
    def _requires_collaboration(self, task_analysis: TaskAnalysisResult) -> bool:
        """Determina si la tarea requiere colaboración entre múltiples agentes"""
        
        # Factores que indican necesidad de colaboración
        collaboration_indicators = 0
        
        # Múltiples tipos de tarea
        if len(task_analysis.secondary_task_types) > 1:
            collaboration_indicators += 2
        
        # Alta complejidad
        if task_analysis.complexity_level.value in ['high', 'critical']:
            collaboration_indicators += 1
        
        # Características especiales que requieren múltiples enfoques
        multi_approach_characteristics = [
            SpecialCharacteristics.MULTI_FILE_ANALYSIS,
            SpecialCharacteristics.REQUIRES_EXTERNAL_KNOWLEDGE,
            SpecialCharacteristics.CROSS_PLATFORM_COMPATIBILITY
        ]
        
        for char in task_analysis.special_characteristics:
            if char in multi_approach_characteristics:
                collaboration_indicators += 1
        
        # Tareas mixtas (ej: análisis + implementación + documentación)
        mixed_task_keywords = [
            'analizar y implementar', 'crear y documentar', 'auditar y corregir',
            'refactorizar y explicar', 'optimizar y documentar'
        ]
        
        input_lower = task_analysis.user_input.lower()
        for keyword in mixed_task_keywords:
            if keyword in input_lower:
                collaboration_indicators += 2
                break
        
        return collaboration_indicators >= 2
    
    def _create_collaboration_plan(self, task_analysis: TaskAnalysisResult,
                                 primary_agent: AgentSelection) -> CollaborationPlan:
        """Crea un plan detallado de colaboración"""
        
        # Identificar agentes adicionales necesarios
        additional_agents = self._identify_additional_agents(task_analysis, primary_agent)
        all_agents = [primary_agent] + additional_agents
        
        # Determinar estrategia de colaboración
        strategy = self._determine_collaboration_strategy(task_analysis, all_agents)
        
        # Crear secuencia de ejecución
        execution_sequence = self._create_execution_sequence(all_agents, strategy)
        
        # Definir puntos de handoff
        handoff_points = self._define_handoff_points(execution_sequence, task_analysis)
        
        # Calcular métricas
        estimated_duration = self._estimate_duration(task_analysis, all_agents, strategy)
        synergy_score = self._calculate_synergy_score(all_agents)
        
        # Identificar riesgos
        risk_factors = self._identify_risk_factors(task_analysis, all_agents, strategy)
        
        # Definir métricas de éxito
        success_metrics = self._define_success_metrics(task_analysis)
        
        return CollaborationPlan(
            strategy=strategy,
            agents=all_agents,
            execution_sequence=execution_sequence,
            handoff_points=handoff_points,
            estimated_duration=estimated_duration,
            synergy_score=synergy_score,
            risk_factors=risk_factors,
            success_metrics=success_metrics
        )
    
    def _identify_additional_agents(self, task_analysis: TaskAnalysisResult,
                                  primary_agent: AgentSelection) -> List[AgentSelection]:
        """Identifica agentes adicionales necesarios para la tarea"""
        
        additional_agents = []
        primary_type = primary_agent.agent_type
        
        # Mapeo de tipos de tarea a agentes complementarios
        task_complement_map = {
            TaskType.CODE_ANALYSIS: {
                AgentType.GEMINI: [AgentType.CLAUDE],  # Análisis → Implementación
                AgentType.CLAUDE: [AgentType.OPENAI],  # Implementación → Documentación
                AgentType.OPENAI: [AgentType.GEMINI]   # Documentación → Análisis
            },
            TaskType.CODE_GENERATION: {
                AgentType.CLAUDE: [AgentType.OPENAI],  # Generación → Documentación
                AgentType.GEMINI: [AgentType.CLAUDE],  # Análisis → Generación
                AgentType.OPENAI: [AgentType.CLAUDE]   # Documentación → Generación
            },
            TaskType.DOCUMENTATION: {
                AgentType.OPENAI: [AgentType.GEMINI],  # Documentación → Revisión
                AgentType.CLAUDE: [AgentType.OPENAI],  # Implementación → Documentación
                AgentType.GEMINI: [AgentType.OPENAI]   # Análisis → Documentación
            }
        }
        
        # Obtener complementos para el tipo de tarea principal
        complements = task_complement_map.get(task_analysis.primary_task_type, {})
        suggested_agents = complements.get(primary_type, [])
        
        # Agregar agentes basado en tipos de tarea secundarios
        for secondary_type in task_analysis.secondary_task_types:
            secondary_complements = task_complement_map.get(secondary_type, {})
            for agent_type in secondary_complements.get(primary_type, []):
                if agent_type not in suggested_agents:
                    suggested_agents.append(agent_type)
        
        # Crear selecciones para agentes sugeridos
        for agent_type in suggested_agents[:2]:  # Máximo 2 agentes adicionales
            if agent_type != primary_type:
                agent_selection = self.agent_selector.select_optimal_agent(task_analysis)
                agent_selection.agent_type = agent_type
                agent_selection.configuration = self.specialization_manager.get_optimal_configuration(agent_type)
                additional_agents.append(agent_selection)
        
        return additional_agents
    
    def _determine_collaboration_strategy(self, task_analysis: TaskAnalysisResult,
                                        agents: List[AgentSelection]) -> CollaborationStrategy:
        """Determina la estrategia óptima de colaboración"""
        
        if len(agents) == 1:
            return CollaborationStrategy.SINGLE
        
        # Factores de decisión
        task_complexity = task_analysis.complexity_level.value
        has_dependencies = len(task_analysis.secondary_task_types) > 0
        requires_validation = SpecialCharacteristics.REQUIRES_PRECISION in task_analysis.special_characteristics
        
        # Estrategia secuencial para dependencias claras
        if has_dependencies and task_complexity in ['moderate', 'high']:
            return CollaborationStrategy.SEQUENTIAL
        
        # Estrategia de validación para alta precisión
        if requires_validation and len(agents) == 2:
            return CollaborationStrategy.VALIDATION
        
        # Estrategia paralela para tareas independientes
        if task_complexity in ['low', 'moderate'] and not has_dependencies:
            return CollaborationStrategy.PARALLEL
        
        # Estrategia colaborativa para casos complejos
        if task_complexity == 'critical' or len(agents) > 2:
            return CollaborationStrategy.COLLABORATIVE
        
        return CollaborationStrategy.SEQUENTIAL  # Default
    
    def _create_execution_sequence(self, agents: List[AgentSelection],
                                 strategy: CollaborationStrategy) -> List[AgentType]:
        """Crea la secuencia de ejecución óptima"""
        
        if strategy == CollaborationStrategy.SINGLE:
            return [agents[0].agent_type]
        
        if strategy == CollaborationStrategy.PARALLEL:
            return [agent.agent_type for agent in agents]
        
        # Para estrategias secuenciales, ordenar por fortalezas complementarias
        agent_types = [agent.agent_type for agent in agents]
        
        # Secuencias optimizadas conocidas
        optimal_sequences = {
            frozenset([AgentType.GEMINI, AgentType.CLAUDE]): [AgentType.GEMINI, AgentType.CLAUDE],
            frozenset([AgentType.CLAUDE, AgentType.OPENAI]): [AgentType.CLAUDE, AgentType.OPENAI],
            frozenset([AgentType.GEMINI, AgentType.OPENAI]): [AgentType.GEMINI, AgentType.OPENAI],
            frozenset([AgentType.GEMINI, AgentType.CLAUDE, AgentType.OPENAI]): [
                AgentType.GEMINI, AgentType.CLAUDE, AgentType.OPENAI
            ]
        }
        
        sequence_key = frozenset(agent_types)
        if sequence_key in optimal_sequences:
            return optimal_sequences[sequence_key]
        
        return agent_types  # Default order
    
    def _define_handoff_points(self, execution_sequence: List[AgentType],
                             task_analysis: TaskAnalysisResult) -> List[Tuple[AgentType, AgentType, HandoffType]]:
        """Define los puntos de handoff entre agentes"""
        
        handoff_points = []
        
        for i in range(len(execution_sequence) - 1):
            from_agent = execution_sequence[i]
            to_agent = execution_sequence[i + 1]
            
            # Determinar tipo de handoff basado en agentes
            handoff_type = self._get_handoff_type(from_agent, to_agent, task_analysis)
            handoff_points.append((from_agent, to_agent, handoff_type))
        
        return handoff_points
    
    def _get_handoff_type(self, from_agent: AgentType, to_agent: AgentType,
                        task_analysis: TaskAnalysisResult) -> HandoffType:
        """Determina el tipo de handoff entre dos agentes"""
        
        # Mapeo de transiciones conocidas
        handoff_map = {
            (AgentType.GEMINI, AgentType.CLAUDE): HandoffType.ANALYSIS_TO_IMPLEMENTATION,
            (AgentType.CLAUDE, AgentType.OPENAI): HandoffType.IMPLEMENTATION_TO_DOCUMENTATION,
            (AgentType.GEMINI, AgentType.OPENAI): HandoffType.ANALYSIS_TO_EXPLANATION,
            (AgentType.CLAUDE, AgentType.GEMINI): HandoffType.GENERATION_TO_VALIDATION,
            (AgentType.OPENAI, AgentType.CLAUDE): HandoffType.COMPLEX_TO_REFINEMENT,
            (AgentType.OPENAI, AgentType.GEMINI): HandoffType.GENERATION_TO_VALIDATION
        }
        
        return handoff_map.get((from_agent, to_agent), HandoffType.COMPLEX_TO_REFINEMENT)
    
    def _estimate_duration(self, task_analysis: TaskAnalysisResult,
                         agents: List[AgentSelection],
                         strategy: CollaborationStrategy) -> float:
        """Estima la duración total de la colaboración en minutos"""
        
        base_duration = task_analysis.estimated_duration
        
        # Factores de ajuste por estrategia
        strategy_multipliers = {
            CollaborationStrategy.SINGLE: 1.0,
            CollaborationStrategy.SEQUENTIAL: 1.3,  # Overhead secuencial
            CollaborationStrategy.PARALLEL: 0.7,    # Paralelización
            CollaborationStrategy.COLLABORATIVE: 1.5,  # Iteraciones
            CollaborationStrategy.VALIDATION: 1.2   # Validación adicional
        }
        
        multiplier = strategy_multipliers.get(strategy, 1.0)
        
        # Ajuste por número de agentes
        if len(agents) > 2:
            multiplier *= 1.1  # Pequeño overhead adicional
        
        # Ajuste por complejidad de coordinación
        if task_analysis.complexity_level.value == 'critical':
            multiplier *= 1.2
        
        return base_duration * multiplier
    
    def _calculate_synergy_score(self, agents: List[AgentSelection]) -> float:
        """Calcula el score de sinergia entre agentes"""
        
        if len(agents) <= 1:
            return 1.0
        
        total_synergy = 0.0
        pair_count = 0
        
        # Calcular sinergia promedio entre pares
        for i in range(len(agents)):
            for j in range(i + 1, len(agents)):
                agent1 = agents[i].agent_type
                agent2 = agents[j].agent_type
                
                # Obtener afinidad de colaboración
                spec1 = self.specialization_manager.get_agent_specialization(agent1)
                if spec1 and agent2 in spec1.collaboration_affinity:
                    pair_synergy = spec1.collaboration_affinity[agent2]
                    total_synergy += pair_synergy
                    pair_count += 1
        
        if pair_count == 0:
            return 0.7  # Score neutral para combinaciones no mapeadas
        
        return total_synergy / pair_count
    
    def _generate_alternatives(self, task_analysis: TaskAnalysisResult, primary_agent_type: AgentType) -> List[AgentSelection]:
        """Genera opciones alternativas de agentes"""
        
        alternatives = []
        
        # Obtener todos los agentes rankeados
        primary_task_areas = self.agent_selector.task_specialization_map.get(
            task_analysis.primary_task_type, []
        )
        
        if primary_task_areas:
            ranked_agents = self.specialization_manager.rank_agents_for_task(
                primary_task_areas[0],
                getattr(task_analysis.complexity_analysis, 'overall_complexity', 0.5)
            )
            
            # Tomar los top 3 excluyendo el agente primario
            for agent_type, score in ranked_agents:
                if agent_type != primary_agent_type and len(alternatives) < 2:
                    alt_selection = self.agent_selector.select_optimal_agent(task_analysis)
                    alt_selection.agent_type = agent_type
                    alt_selection.confidence_score = score
                    alt_selection.reasoning = [f"Alternativa viable con score {score:.2f}"]
                    alternatives.append(alt_selection)
        
        return alternatives
    
    def _generate_optimization_suggestions(self, task_analysis: TaskAnalysisResult,
                                         primary_agent: AgentSelection,
                                         collaboration_plan: Optional[CollaborationPlan]) -> List[str]:
        """Genera sugerencias de optimización"""
        
        suggestions = []
        
        # Sugerencias basadas en configuración del agente
        config = primary_agent.configuration
        if config.temperature > 0.3 and SpecialCharacteristics.REQUIRES_PRECISION in task_analysis.special_characteristics:
            suggestions.append("Considerar reducir temperature para mayor precisión")
        
        # Sugerencias basadas en colaboración
        if collaboration_plan:
            if collaboration_plan.synergy_score < 0.7:
                suggestions.append("Baja sinergia detectada - considerar agentes alternativos")
            
            if collaboration_plan.estimated_duration > 7200:  # Más de 2 horas
                suggestions.append("Duración elevada - considerar dividir la tarea")
            
            if len(collaboration_plan.risk_factors) > 2:
                suggestions.append("Múltiples riesgos identificados - implementar checkpoints")
        
        # Sugerencias basadas en complejidad
        if task_analysis.complexity_level.value in ['high', 'critical']:
            suggestions.append("Alta complejidad - considerar validación por segundo agente")
        
        return suggestions
    
    def _estimate_cost(self, primary_agent: AgentSelection,
                      collaboration_plan: Optional[CollaborationPlan]) -> float:
        """Estima el costo de la operación"""
        
        # Costos base por agente (USD por token aproximado)
        agent_costs = {
            AgentType.GEMINI: 0.0001,
            AgentType.CLAUDE: 0.0002,
            AgentType.OPENAI: 0.00015
        }
        
        # Costo del agente primario
        primary_cost = agent_costs.get(primary_agent.agent_type, 0.00015)
        estimated_tokens = primary_agent.configuration.max_tokens
        total_cost = primary_cost * estimated_tokens
        
        # Agregar costos de colaboración
        if collaboration_plan:
            for agent in collaboration_plan.agents[1:]:  # Excluir agente primario
                agent_cost = agent_costs.get(agent.agent_type, 0.00015)
                agent_tokens = agent.configuration.max_tokens
                total_cost += agent_cost * agent_tokens
            
            # Overhead de coordinación
            if collaboration_plan.strategy in [CollaborationStrategy.COLLABORATIVE, CollaborationStrategy.SEQUENTIAL]:
                total_cost *= 1.2  # 20% overhead
        
        return total_cost
    
    def _estimate_quality(self, primary_agent: AgentSelection,
                        collaboration_plan: Optional[CollaborationPlan]) -> float:
        """Estima la calidad esperada del resultado"""
        
        # Calidad base del agente primario
        base_quality = primary_agent.expected_performance.get('accuracy', 0.5)
        
        # Bonificación por colaboración
        if collaboration_plan:
            synergy_bonus = collaboration_plan.synergy_score * 0.1
            base_quality += synergy_bonus
            
            # Bonificación por múltiples perspectivas
            if len(collaboration_plan.agents) > 1:
                multi_agent_bonus = min(0.15, len(collaboration_plan.agents) * 0.05)
                base_quality += multi_agent_bonus
        
        return min(base_quality, 1.0)  # Asegurar que no exceda 1.0
    


class CollaborationEngine:
    """
    Motor de colaboración que maneja la ejecución de workflows multi-agente
    """
    
    def __init__(self):
        self.active_collaborations = {}
        self.collaboration_history = []
    
    def execute_collaboration_plan(self, plan: CollaborationPlan,
                                 task_analysis: TaskAnalysisResult) -> Dict[str, Any]:
        """Ejecuta un plan de colaboración"""
        
        execution_id = f"collab_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        collaboration_context = {
            'execution_id': execution_id,
            'plan': plan,
            'task_analysis': task_analysis,
            'status': 'initialized',
            'current_stage': 0,
            'results': {},
            'handoff_data': {}
        }
        
        self.active_collaborations[execution_id] = collaboration_context
        
        return {
            'execution_id': execution_id,
            'status': 'ready',
            'next_agent': plan.execution_sequence[0] if plan.execution_sequence else None,
            'estimated_duration': plan.estimated_duration,
            'success_metrics': plan.success_metrics
        }
    
    def get_collaboration_status(self, execution_id: str) -> Dict[str, Any]:
        """Obtiene el estado de una colaboración activa"""
        
        if execution_id not in self.active_collaborations:
            return {'error': 'Collaboration not found'}
        
        collaboration = self.active_collaborations[execution_id]
        
        return {
            'execution_id': execution_id,
            'status': collaboration['status'],
            'current_stage': collaboration['current_stage'],
            'total_stages': len(collaboration['plan'].execution_sequence),
            'progress': collaboration['current_stage'] / len(collaboration['plan'].execution_sequence) * 100,
            'current_agent': collaboration['plan'].execution_sequence[collaboration['current_stage']] if collaboration['current_stage'] < len(collaboration['plan'].execution_sequence) else None
        }
    
    def complete_agent_stage(self, execution_id: str, agent_result: Dict[str, Any]) -> Dict[str, Any]:
        """Marca una etapa de agente como completada"""
        
        if execution_id not in self.active_collaborations:
            return {'error': 'Collaboration not found'}
        
        collaboration = self.active_collaborations[execution_id]
        current_stage = collaboration['current_stage']
        
        # Guardar resultado de la etapa actual
        current_agent = collaboration['plan'].execution_sequence[current_stage]
        collaboration['results'][current_agent.value] = agent_result
        
        # Avanzar a la siguiente etapa
        collaboration['current_stage'] += 1
        
        # Verificar si la colaboración está completa
        if collaboration['current_stage'] >= len(collaboration['plan'].execution_sequence):
            collaboration['status'] = 'completed'
            self._finalize_collaboration(execution_id)
        
        return self.get_collaboration_status(execution_id)
    
    def _finalize_collaboration(self, execution_id: str):
        """Finaliza una colaboración y archiva los resultados"""
        
        collaboration = self.active_collaborations[execution_id]
        
        # Agregar a historial
        collaboration['completed_at'] = datetime.now().isoformat()
        self.collaboration_history.append(collaboration.copy())
        
        # Remover de colaboraciones activas
        del self.active_collaborations[execution_id]
