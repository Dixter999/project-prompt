"""
Task Classification System - FASE 1
Analizador y Clasificador Inteligente de Tasks

Componente principal que determina automáticamente las características del trabajo 
solicitado por el usuario para seleccionar el agente más apropiado.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple
import re
from pathlib import Path

from .linguistic_analyzer import LinguisticPatternAnalyzer, LinguisticAnalysisResult
from .file_analyzer import FileContextAnalyzer, FileContextAnalysisResult
from .complexity_estimator import ComplexityEstimator, ComplexityAnalysisResult, RiskLevel


class TaskType(Enum):
    """Categorías principales de tipos de tasks detectables"""
    CODE_ANALYSIS = "code_analysis"          # Revisión, auditoría, identificación de problemas
    CODE_GENERATION = "code_generation"      # Creación de nuevas funcionalidades
    CODE_MODIFICATION = "code_modification"  # Cambios en código existente
    DOCUMENTATION = "documentation"          # Creación de documentación y comentarios
    DEBUGGING = "debugging"                  # Solución de errores y problemas
    OPTIMIZATION = "optimization"            # Mejoras de rendimiento
    TESTING = "testing"                      # Creación y ejecución de pruebas
    ARCHITECTURE_REVIEW = "architecture_review"  # Evaluación de diseño y estructura


class SpecialCharacteristics(Enum):
    """Características especiales identificables"""
    REQUIRES_CREATIVITY = "requires_creativity"      # Proyectos nuevos, soluciones innovadoras
    REQUIRES_PRECISION = "requires_precision"        # Debugging crítico, código de producción
    REQUIRES_SPEED = "requires_speed"               # Urgencia o velocidad requerida
    REQUIRES_EXPLANATION = "requires_explanation"   # Contextos educativos, explicación detallada
    MULTI_FILE_ANALYSIS = "multi_file_analysis"     # Análisis de múltiples archivos
    REQUIRES_EXTERNAL_KNOWLEDGE = "requires_external_knowledge"  # Necesita conocimiento externo
    CROSS_PLATFORM_COMPATIBILITY = "cross_platform_compatibility"  # Compatibilidad entre plataformas


@dataclass
class TaskAnalysisResult:
    """Resultado completo del análisis de task"""
    primary_task_type: TaskType
    secondary_task_types: List[TaskType]
    complexity_level: RiskLevel  # Usar RiskLevel en lugar de ComplexityLevel
    special_characteristics: List[SpecialCharacteristics]
    confidence_score: float  # 0.0 - 1.0
    
    # Detalles del análisis
    linguistic_analysis: Dict[str, Any]
    file_analysis: Dict[str, Any]
    complexity_analysis: Dict[str, Any]
    
    # Estimaciones para selección de agente
    estimated_tokens: int
    estimated_processing_time: float  # segundos
    estimated_duration: float  # minutos estimados
    estimated_cost: float  # USD estimado
    
    # Recomendaciones
    recommended_agents: List[str]  # Nombres de agentes recomendados
    recommended_strategy: str      # 'single', 'sequential', 'parallel', 'collaborative'
    
    # Metadatos del análisis
    user_input: str  # Input original del usuario


class TaskClassifier:
    """
    Motor de Clasificación Inteligente de Tasks
    
    Componente principal que analiza el input del usuario y archivos adjuntos
    para determinar las características del trabajo y recomendar la mejor estrategia.
    """
    
    def __init__(self):
        """Inicializar el clasificador con todos sus componentes especializados"""
        self.linguistic_analyzer = LinguisticPatternAnalyzer()
        self.file_analyzer = FileContextAnalyzer()
        self.complexity_estimator = ComplexityEstimator()
        
        # Pesos para el sistema de scoring
        self.scoring_weights = {
            'linguistic_confidence': 0.4,      # Análisis lingüístico
            'file_context_confidence': 0.3,    # Contexto de archivos
            'complexity_indicators': 0.2,      # Indicadores de complejidad
            'historical_patterns': 0.1         # Patrones históricos (futuro)
        }
    
    def classify_task(self, 
                     user_input: str, 
                     file_paths: Optional[List[str]] = None,
                     project_context: Optional[Dict[str, Any]] = None) -> TaskAnalysisResult:
        """
        Clasificar un task basándose en input del usuario y archivos adjuntos
        
        Args:
            user_input: Texto del usuario describiendo el task
            file_paths: Lista de rutas a archivos adjuntos (opcional)
            project_context: Contexto del proyecto actual (opcional)
            
        Returns:
            TaskAnalysisResult con análisis completo y recomendaciones
        """
        # 1. Análisis lingüístico del input
        linguistic_result = self.linguistic_analyzer.analyze_text(user_input)
        
        # 2. Análisis contextual de archivos y proyecto
        file_result = self.file_analyzer.analyze_context(
            file_paths=file_paths,
            project_context=project_context
        )
        
            # 4. Estimación de complejidad multifactorial
        complexity_result = self.complexity_estimator.estimate_complexity(
            user_input=user_input,
            linguistic_result=linguistic_result,
            file_context_result=file_result
        )
        
        # 5. Determinación del tipo de task principal
        primary_task_type, confidence = self._determine_primary_task_type(
            linguistic_result, file_result
        )
        
        # 6. Identificación de tipos secundarios
        secondary_task_types = self._identify_secondary_task_types(
            linguistic_result, file_result, primary_task_type
        )
        
        # 7. Detección de características especiales
        special_characteristics = self._detect_special_characteristics(
            linguistic_result, file_result
        )
        
        # 8. Recomendaciones de agentes y estrategia
        agent_recommendations = self._recommend_agents_and_strategy(
            primary_task_type, secondary_task_types, complexity_result, special_characteristics
        )
        
        # 9. Construir resultado final
        return TaskAnalysisResult(
            primary_task_type=primary_task_type,
            secondary_task_types=secondary_task_types,
            complexity_level=complexity_result.risk_level,  # Usar risk_level como complexity_level
            special_characteristics=special_characteristics,
            confidence_score=confidence,
            
            linguistic_analysis=linguistic_result,
            file_analysis=file_result,
            complexity_analysis=complexity_result,
            
            estimated_tokens=complexity_result.estimated_tokens,
            estimated_processing_time=complexity_result.estimated_effort_hours * 3600,  # Convertir horas a segundos
            estimated_duration=complexity_result.estimated_effort_hours * 60,  # Convertir horas a minutos
            estimated_cost=complexity_result.estimated_effort_hours * 0.02,  # Estimación básica de costo
            
            recommended_agents=agent_recommendations['agents'],
            recommended_strategy=agent_recommendations['strategy'],
            user_input=user_input
        )
    
    def _determine_primary_task_type(self, 
                                   linguistic_result, 
                                   file_result) -> Tuple[TaskType, float]:
        """
        Determinar el tipo de task principal basándose en análisis combinado
        
        Returns:
            Tuple de (TaskType, confidence_score)
        """
        # Scores por tipo de task basados en análisis lingüístico
        task_scores = {}
        
        # Mapear verbos de acción a tipos de task
        task_type_mapping = {
            TaskType.CODE_ANALYSIS: 'analysis',
            TaskType.CODE_GENERATION: 'generation',
            TaskType.CODE_MODIFICATION: 'modification',
            TaskType.DOCUMENTATION: 'documentation',
            TaskType.DEBUGGING: 'debugging',
            TaskType.OPTIMIZATION: 'optimization',
            TaskType.TESTING: 'testing',
            TaskType.ARCHITECTURE_REVIEW: 'analysis'  # Mapear a analysis como fallback
        }
        
        # Calcular scores basados en verbos de acción detectados
        total_action_verbs = sum(linguistic_result.action_verbs.values()) or 1
        
        for task_type in TaskType:
            linguistic_score = 0.0
            file_score = 0.0
            
            # Score lingüístico basado en verbos de acción
            action_category = task_type_mapping.get(task_type, 'analysis')
            action_count = linguistic_result.action_verbs.get(action_category, 0)
            linguistic_score = action_count / total_action_verbs
            
            # Score de contexto de archivos basado en tipo de proyecto
            if hasattr(file_result, 'project_type'):
                # Mapear tipos de proyecto a probabilidades de task types
                project_task_affinity = {
                    'web_frontend': {TaskType.CODE_GENERATION: 0.4, TaskType.CODE_MODIFICATION: 0.3, TaskType.DEBUGGING: 0.2},
                    'web_backend': {TaskType.CODE_GENERATION: 0.3, TaskType.CODE_ANALYSIS: 0.3, TaskType.TESTING: 0.2},
                    'library': {TaskType.DOCUMENTATION: 0.4, TaskType.TESTING: 0.3, TaskType.CODE_ANALYSIS: 0.2}
                }
                
                project_type_str = file_result.project_type.value if hasattr(file_result.project_type, 'value') else str(file_result.project_type)
                affinity_scores = project_task_affinity.get(project_type_str, {})
                file_score = affinity_scores.get(task_type, 0.1)  # Score base pequeño
            
            # Score combinado ponderado
            combined_score = (
                linguistic_score * self.scoring_weights['linguistic_confidence'] +
                file_score * self.scoring_weights['file_context_confidence']
            )
            
            task_scores[task_type] = combined_score
        
        # Si no hay scores significativos, usar análisis de objetos técnicos
        if max(task_scores.values()) < 0.1:
            total_technical_objects = sum(linguistic_result.technical_objects.values()) or 1
            
            # Inferir tipo basado en objetos técnicos más comunes
            code_objects = linguistic_result.technical_objects.get('code_elements', 0)
            file_objects = linguistic_result.technical_objects.get('file_types', 0)
            system_objects = linguistic_result.technical_objects.get('system_components', 0)
            
            if code_objects > file_objects and code_objects > system_objects:
                task_scores[TaskType.CODE_MODIFICATION] = 0.7
            elif file_objects > 0:
                task_scores[TaskType.CODE_ANALYSIS] = 0.6
            else:
                task_scores[TaskType.CODE_GENERATION] = 0.5
        
        # Encontrar el task type con mayor score
        primary_task_type = max(task_scores, key=task_scores.get)
        confidence = min(task_scores[primary_task_type], 1.0)
        
        return primary_task_type, confidence
    
    def _identify_secondary_task_types(self, 
                                     linguistic_result,
                                     file_result,
                                     primary_task_type: TaskType) -> List[TaskType]:
        """
        Identificar tipos de task secundarios (para estrategias multi-agente)
        """
        secondary_types = []
        
        # Threshold para considerar un tipo como secundario
        secondary_threshold = 0.2
        
        # Analizar indicadores de complejidad para tasks secundarios
        complexity_indicators = linguistic_result.complexity_indicators
        
        # Si hay muchos indicadores de complejidad, es probable que requiera múltiples tipos
        total_complexity = sum(complexity_indicators.values())
        
        if total_complexity > 3:  # Más de 3 indicadores de complejidad
            # Agregar tipos complementarios basados en el tipo primario
            complementary_tasks = {
                TaskType.CODE_GENERATION: [TaskType.TESTING, TaskType.DOCUMENTATION],
                TaskType.CODE_MODIFICATION: [TaskType.TESTING, TaskType.CODE_ANALYSIS],
                TaskType.DEBUGGING: [TaskType.CODE_ANALYSIS, TaskType.TESTING],
                TaskType.CODE_ANALYSIS: [TaskType.DOCUMENTATION, TaskType.OPTIMIZATION],
                TaskType.OPTIMIZATION: [TaskType.TESTING, TaskType.CODE_ANALYSIS],
                TaskType.TESTING: [TaskType.CODE_ANALYSIS],
                TaskType.DOCUMENTATION: [TaskType.CODE_ANALYSIS],
                TaskType.ARCHITECTURE_REVIEW: [TaskType.DOCUMENTATION, TaskType.CODE_ANALYSIS]
            }
            
            potential_secondary = complementary_tasks.get(primary_task_type, [])
            
            # Agregar el primer tipo secundario si hay suficientes indicadores
            if potential_secondary and total_complexity > 5:
                secondary_types.append(potential_secondary[0])
                
                # Agregar segundo tipo si la complejidad es muy alta
                if len(potential_secondary) > 1 and total_complexity > 8:
                    secondary_types.append(potential_secondary[1])
        
        # Verificar indicadores específicos para types adicionales
        if linguistic_result.precision_indicators and sum(linguistic_result.precision_indicators.values()) > 2:
            if TaskType.TESTING not in secondary_types and primary_task_type != TaskType.TESTING:
                secondary_types.append(TaskType.TESTING)
        
        if linguistic_result.explanation_indicators and sum(linguistic_result.explanation_indicators.values()) > 2:
            if TaskType.DOCUMENTATION not in secondary_types and primary_task_type != TaskType.DOCUMENTATION:
                secondary_types.append(TaskType.DOCUMENTATION)
        
        return secondary_types
    
    def _detect_special_characteristics(self, 
                                      linguistic_result,
                                      file_result) -> List[SpecialCharacteristics]:
        """
        Detectar características especiales del task
        """
        characteristics = []
        
        # Threshold para detectar características
        characteristic_threshold = 2  # Número mínimo de indicadores
        
        # REQUIRES_CREATIVITY - basado en indicadores de creatividad
        creativity_score = sum(linguistic_result.creativity_indicators.values())
        if creativity_score >= characteristic_threshold:
            characteristics.append(SpecialCharacteristics.REQUIRES_CREATIVITY)
        
        # REQUIRES_PRECISION - basado en indicadores de precisión
        precision_score = sum(linguistic_result.precision_indicators.values())
        if precision_score >= characteristic_threshold:
            characteristics.append(SpecialCharacteristics.REQUIRES_PRECISION)
        
        # REQUIRES_SPEED - basado en indicadores de urgencia
        urgency_score = sum(linguistic_result.urgency_indicators.values())
        if urgency_score >= characteristic_threshold:
            characteristics.append(SpecialCharacteristics.REQUIRES_SPEED)
        
        # REQUIRES_EXPLANATION - basado en indicadores de explicación
        explanation_score = sum(linguistic_result.explanation_indicators.values())
        if explanation_score >= characteristic_threshold:
            characteristics.append(SpecialCharacteristics.REQUIRES_EXPLANATION)
        
        # Análisis adicional basado en complejidad del texto
        if linguistic_result.text_complexity.value in ['high', 'very_high']:
            if SpecialCharacteristics.REQUIRES_PRECISION not in characteristics:
                characteristics.append(SpecialCharacteristics.REQUIRES_PRECISION)
        
        # Análisis basado en contexto de archivos
        if hasattr(file_result, 'project_structure') and file_result.project_structure:
            # Si hay muchos archivos de test, probablemente requiere precisión
            if file_result.project_structure.test_files > 5:
                if SpecialCharacteristics.REQUIRES_PRECISION not in characteristics:
                    characteristics.append(SpecialCharacteristics.REQUIRES_PRECISION)
            
            # Si es un proyecto grande, probablemente requiere explicación
            if file_result.project_structure.total_files > 50:
                if SpecialCharacteristics.REQUIRES_EXPLANATION not in characteristics:
                    characteristics.append(SpecialCharacteristics.REQUIRES_EXPLANATION)
        
        return characteristics
    
    def _recommend_agents_and_strategy(self,
                                     primary_task_type: TaskType,
                                     secondary_task_types: List[TaskType],
                                     complexity_result,
                                     special_characteristics: List[SpecialCharacteristics]) -> Dict[str, Any]:
        """
        Recomendar agentes y estrategia de ejecución basándose en el análisis
        """
        # Mapeo de tipos de task a agentes especializados
        task_to_agents = {
            TaskType.CODE_ANALYSIS: ['gemini', 'claude'],
            TaskType.CODE_GENERATION: ['claude', 'openai'],
            TaskType.CODE_MODIFICATION: ['claude', 'gemini'],
            TaskType.DOCUMENTATION: ['openai', 'claude'],
            TaskType.DEBUGGING: ['claude', 'gemini'],
            TaskType.OPTIMIZATION: ['gemini', 'claude'],
            TaskType.TESTING: ['claude', 'openai'],
            TaskType.ARCHITECTURE_REVIEW: ['gemini', 'claude']
        }
        
        # Agente primario basado en task principal
        primary_agents = task_to_agents.get(primary_task_type, ['claude'])
        
        # Determinar estrategia
        if not secondary_task_types:
            # Single agent si no hay tasks secundarios
            strategy = 'single'
            recommended_agents = [primary_agents[0]]
        elif len(secondary_task_types) == 1:
            # Sequential si hay un task secundario
            strategy = 'sequential'
            secondary_agents = task_to_agents.get(secondary_task_types[0], ['claude'])
            recommended_agents = [primary_agents[0], secondary_agents[0]]
        else:
            # Parallel o collaborative para múltiples tasks
            if complexity_result.risk_level.value in ['high', 'critical']:
                strategy = 'collaborative'
            else:
                strategy = 'parallel'
            
            # Incluir agentes para todos los task types
            all_agents = set([primary_agents[0]])
            for task_type in secondary_task_types:
                agents = task_to_agents.get(task_type, ['claude'])
                all_agents.add(agents[0])
            
            recommended_agents = list(all_agents)
        
        # Ajustes basados en características especiales
        if SpecialCharacteristics.REQUIRES_SPEED in special_characteristics:
            # Priorizar agentes rápidos y estrategia single
            if 'gemini' in recommended_agents:
                recommended_agents = ['gemini']
            strategy = 'single'
        
        if SpecialCharacteristics.REQUIRES_PRECISION in special_characteristics:
            # Priorizar Claude para precisión y agregar validación
            if 'claude' not in recommended_agents:
                recommended_agents.insert(0, 'claude')
            if len(recommended_agents) == 1:
                strategy = 'single'
            else:
                strategy = 'collaborative'  # Para validación cruzada
        
        if SpecialCharacteristics.REQUIRES_CREATIVITY in special_characteristics:
            # Asegurar que OpenAI esté incluido para creatividad
            if 'openai' not in recommended_agents:
                recommended_agents.append('openai')
        
        return {
            'agents': recommended_agents,
            'strategy': strategy
        }
    
    def get_classification_summary(self, result: TaskAnalysisResult) -> str:
        """
        Generar resumen legible del análisis de clasificación
        
        Args:
            result: Resultado del análisis de task
            
        Returns:
            String con resumen formateado
        """
        summary = []
        summary.append(f"🎯 Tipo Principal: {result.primary_task_type.value.replace('_', ' ').title()}")
        summary.append(f"📊 Complejidad: {result.complexity_level.value.title()}")
        summary.append(f"🎲 Confianza: {result.confidence_score:.1%}")
        
        if result.secondary_task_types:
            secondary = [t.value.replace('_', ' ').title() for t in result.secondary_task_types]
            summary.append(f"📋 Tipos Secundarios: {', '.join(secondary)}")
        
        if result.special_characteristics:
            characteristics = [c.value.replace('_', ' ').title() for c in result.special_characteristics]
            summary.append(f"⭐ Características: {', '.join(characteristics)}")
        
        summary.append(f"🤖 Agentes Recomendados: {', '.join(result.recommended_agents)}")
        summary.append(f"🔄 Estrategia: {result.recommended_strategy.title()}")
        
        summary.append(f"💰 Costo Estimado: ${result.estimated_cost:.4f}")
        summary.append(f"⏱️ Tiempo Estimado: {result.estimated_processing_time:.1f}s")
        
        return "\n".join(summary)
