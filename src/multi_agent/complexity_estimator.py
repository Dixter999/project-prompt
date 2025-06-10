"""
Sistema Multi-Agente - FASE 1: Estimador de Complejidad
Componente especializado para análisis multifactorial de complejidad de tasks.
"""

import math
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum


class ComplexityDimension(Enum):
    """Dimensiones de complejidad analizadas"""
    COGNITIVE = "cognitive"          # Complejidad mental/conceptual
    COMPUTATIONAL = "computational"  # Complejidad computacional
    TECHNICAL = "technical"          # Complejidad técnica
    TEMPORAL = "temporal"           # Complejidad temporal/tiempo
    ARCHITECTURAL = "architectural" # Complejidad arquitectural
    INTEGRATION = "integration"     # Complejidad de integración


class RiskLevel(Enum):
    """Niveles de riesgo asociados a la complejidad"""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ComplexityMetrics:
    """Métricas específicas de complejidad"""
    cyclomatic_complexity: float
    cognitive_load: float
    technical_debt_factor: float
    integration_points: int
    dependency_depth: int
    abstraction_level: float
    change_impact_radius: float
    testing_complexity: float


@dataclass
class ComplexityAnalysisResult:
    """Resultado del análisis de complejidad"""
    overall_complexity: float  # 0.0 - 1.0
    dimension_scores: Dict[ComplexityDimension, float]
    metrics: ComplexityMetrics
    risk_level: RiskLevel
    complexity_factors: List[str]
    mitigation_strategies: List[str]
    estimated_effort_hours: float
    estimated_tokens: int
    confidence_score: float


class ComplexityEstimator:
    """
    Estimador de complejidad multifactorial para clasificación inteligente de tasks.
    Analiza múltiples dimensiones de complejidad para proporcionar estimaciones precisas.
    """
    
    def __init__(self):
        self._initialize_complexity_weights()
        self._initialize_factor_mappings()
        
    def _initialize_complexity_weights(self):
        """Inicializa pesos para diferentes dimensiones de complejidad"""
        
        self.dimension_weights = {
            ComplexityDimension.COGNITIVE: 0.25,
            ComplexityDimension.COMPUTATIONAL: 0.20,
            ComplexityDimension.TECHNICAL: 0.20,
            ComplexityDimension.TEMPORAL: 0.15,
            ComplexityDimension.ARCHITECTURAL: 0.15,
            ComplexityDimension.INTEGRATION: 0.05
        }
        
        # Factores que aumentan complejidad cognitiva
        self.cognitive_factors = {
            'abstract_concepts': 0.8,
            'multiple_paradigms': 0.7,
            'complex_algorithms': 0.9,
            'domain_expertise_required': 0.6,
            'creative_problem_solving': 0.7,
            'ambiguous_requirements': 0.8,
            'novel_technologies': 0.6,
            'cross_domain_knowledge': 0.5
        }
        
        # Factores de complejidad computacional
        self.computational_factors = {
            'large_data_processing': 0.8,
            'real_time_constraints': 0.9,
            'memory_optimization': 0.7,
            'parallel_processing': 0.8,
            'distributed_systems': 0.9,
            'performance_critical': 0.7,
            'scalability_requirements': 0.6,
            'resource_constraints': 0.5
        }
        
        # Factores de complejidad técnica
        self.technical_factors = {
            'legacy_system_integration': 0.8,
            'multiple_technologies': 0.6,
            'security_requirements': 0.7,
            'compliance_standards': 0.6,
            'error_handling_complexity': 0.5,
            'testing_complexity': 0.6,
            'deployment_complexity': 0.5,
            'monitoring_requirements': 0.4
        }
        
        # Factores temporales
        self.temporal_factors = {
            'tight_deadlines': 0.8,
            'milestone_dependencies': 0.6,
            'time_sensitive_operations': 0.7,
            'batch_processing': 0.4,
            'scheduled_tasks': 0.3,
            'event_driven_architecture': 0.5
        }
        
        # Factores arquitecturales
        self.architectural_factors = {
            'microservices_architecture': 0.7,
            'event_sourcing': 0.8,
            'cqrs_pattern': 0.7,
            'complex_state_management': 0.6,
            'multi_tenant_architecture': 0.8,
            'plugin_architecture': 0.6,
            'modular_design': 0.4,
            'layered_architecture': 0.3
        }
        
        # Factores de integración
        self.integration_factors = {
            'third_party_apis': 0.6,
            'database_integration': 0.4,
            'message_queues': 0.5,
            'external_services': 0.7,
            'data_transformation': 0.6,
            'protocol_translation': 0.8,
            'authentication_integration': 0.5
        }
    
    def _initialize_factor_mappings(self):
        """Inicializa mapeos de palabras clave a factores de complejidad"""
        
        self.keyword_to_factors = {
            # Cognitive complexity keywords
            'algorithm': ['complex_algorithms', 'abstract_concepts'],
            'ai': ['novel_technologies', 'complex_algorithms'],
            'machine learning': ['novel_technologies', 'complex_algorithms', 'domain_expertise_required'],
            'optimization': ['complex_algorithms', 'performance_critical'],
            'creative': ['creative_problem_solving'],
            'innovative': ['creative_problem_solving', 'novel_technologies'],
            'research': ['domain_expertise_required', 'abstract_concepts'],
            'experimental': ['novel_technologies', 'ambiguous_requirements'],
            
            # Computational complexity keywords
            'performance': ['performance_critical', 'memory_optimization'],
            'scale': ['scalability_requirements', 'large_data_processing'],
            'real-time': ['real_time_constraints'],
            'distributed': ['distributed_systems', 'parallel_processing'],
            'concurrent': ['parallel_processing'],
            'async': ['parallel_processing'],
            'big data': ['large_data_processing', 'scalability_requirements'],
            'streaming': ['real_time_constraints', 'large_data_processing'],
            
            # Technical complexity keywords
            'security': ['security_requirements'],
            'testing': ['testing_complexity'],
            'legacy': ['legacy_system_integration'],
            'integration': ['legacy_system_integration', 'third_party_apis'],
            'deployment': ['deployment_complexity'],
            'monitoring': ['monitoring_requirements'],
            'compliance': ['compliance_standards'],
            'error handling': ['error_handling_complexity'],
            
            # Temporal complexity keywords
            'urgent': ['tight_deadlines'],
            'deadline': ['tight_deadlines', 'milestone_dependencies'],
            'time-sensitive': ['time_sensitive_operations'],
            'scheduled': ['scheduled_tasks'],
            'batch': ['batch_processing'],
            'event': ['event_driven_architecture'],
            
            # Architectural complexity keywords
            'microservices': ['microservices_architecture'],
            'event sourcing': ['event_sourcing'],
            'cqrs': ['cqrs_pattern'],
            'state management': ['complex_state_management'],
            'multi-tenant': ['multi_tenant_architecture'],
            'plugin': ['plugin_architecture'],
            'modular': ['modular_design'],
            'layered': ['layered_architecture'],
            
            # Integration complexity keywords
            'api': ['third_party_apis', 'external_services'],
            'database': ['database_integration'],
            'queue': ['message_queues'],
            'service': ['external_services'],
            'transform': ['data_transformation'],
            'protocol': ['protocol_translation'],
            'auth': ['authentication_integration']
        }
    
    def estimate_complexity(self, 
                          user_input: str,
                          linguistic_result: Optional[object] = None,
                          file_context_result: Optional[object] = None,
                          task_type: Optional[str] = None,
                          additional_context: Optional[Dict] = None) -> ComplexityAnalysisResult:
        """
        Estima la complejidad de un task basándose en múltiples factores.
        
        Args:
            user_input: Input del usuario
            linguistic_result: Resultado del análisis lingüístico
            file_context_result: Resultado del análisis de contexto de archivos
            task_type: Tipo de task identificado
            additional_context: Contexto adicional
            
        Returns:
            ComplexityAnalysisResult con análisis completo de complejidad
        """
        
        # Análizar factores de complejidad desde el input del usuario
        detected_factors = self._detect_complexity_factors(user_input)
        
        # Calcular scores por dimensión
        dimension_scores = self._calculate_dimension_scores(
            detected_factors, linguistic_result, file_context_result, task_type
        )
        
        # Calcular métricas específicas
        metrics = self._calculate_complexity_metrics(
            detected_factors, dimension_scores, file_context_result
        )
        
        # Calcular complejidad general
        overall_complexity = self._calculate_overall_complexity(dimension_scores)
        
        # Determinar nivel de riesgo
        risk_level = self._determine_risk_level(overall_complexity, metrics)
        
        # Generar estrategias de mitigación
        mitigation_strategies = self._generate_mitigation_strategies(
            detected_factors, dimension_scores, risk_level
        )
        
        # Estimar esfuerzo
        estimated_effort_hours = self._estimate_effort_hours(overall_complexity, metrics, task_type)
        
        # Estimar tokens requeridos
        estimated_tokens = self._estimate_tokens(overall_complexity, user_input, file_context_result)
        
        # Calcular confianza del análisis
        confidence_score = self._calculate_confidence_score(
            linguistic_result, file_context_result, len(detected_factors)
        )
        
        return ComplexityAnalysisResult(
            overall_complexity=overall_complexity,
            dimension_scores=dimension_scores,
            metrics=metrics,
            risk_level=risk_level,
            complexity_factors=detected_factors,
            mitigation_strategies=mitigation_strategies,
            estimated_effort_hours=estimated_effort_hours,
            estimated_tokens=estimated_tokens,
            confidence_score=confidence_score
        )
    
    def _detect_complexity_factors(self, user_input: str) -> List[str]:
        """Detecta factores de complejidad en el input del usuario"""
        detected_factors = []
        user_input_lower = user_input.lower()
        
        for keyword, factors in self.keyword_to_factors.items():
            if keyword in user_input_lower:
                detected_factors.extend(factors)
        
        # Remover duplicados manteniendo orden
        return list(dict.fromkeys(detected_factors))
    
    def _calculate_dimension_scores(self, 
                                   detected_factors: List[str],
                                   linguistic_result: Optional[object],
                                   file_context_result: Optional[object],
                                   task_type: Optional[str]) -> Dict[ComplexityDimension, float]:
        """Calcula scores para cada dimensión de complejidad"""
        
        scores = {}
        
        # Complejidad cognitiva
        cognitive_score = self._calculate_cognitive_complexity(
            detected_factors, linguistic_result, task_type
        )
        scores[ComplexityDimension.COGNITIVE] = cognitive_score
        
        # Complejidad computacional
        computational_score = self._calculate_computational_complexity(
            detected_factors, task_type
        )
        scores[ComplexityDimension.COMPUTATIONAL] = computational_score
        
        # Complejidad técnica
        technical_score = self._calculate_technical_complexity(
            detected_factors, file_context_result, task_type
        )
        scores[ComplexityDimension.TECHNICAL] = technical_score
        
        # Complejidad temporal
        temporal_score = self._calculate_temporal_complexity(
            detected_factors, linguistic_result
        )
        scores[ComplexityDimension.TEMPORAL] = temporal_score
        
        # Complejidad arquitectural
        architectural_score = self._calculate_architectural_complexity(
            detected_factors, file_context_result
        )
        scores[ComplexityDimension.ARCHITECTURAL] = architectural_score
        
        # Complejidad de integración
        integration_score = self._calculate_integration_complexity(
            detected_factors, file_context_result
        )
        scores[ComplexityDimension.INTEGRATION] = integration_score
        
        return scores
    
    def _calculate_cognitive_complexity(self, 
                                      detected_factors: List[str],
                                      linguistic_result: Optional[object],
                                      task_type: Optional[str]) -> float:
        """Calcula complejidad cognitiva"""
        
        base_score = 0.0
        
        # Factores detectados
        for factor in detected_factors:
            if factor in self.cognitive_factors:
                base_score += self.cognitive_factors[factor]
        
        # Ajustes por análisis lingüístico
        if linguistic_result and hasattr(linguistic_result, 'creativity_indicators'):
            creativity_total = sum(linguistic_result.creativity_indicators.values())
            base_score += min(creativity_total * 0.1, 0.3)
        
        if linguistic_result and hasattr(linguistic_result, 'text_complexity'):
            if str(linguistic_result.text_complexity) == 'VERY_HIGH':
                base_score += 0.2
            elif str(linguistic_result.text_complexity) == 'HIGH':
                base_score += 0.1
        
        # Ajustes por tipo de task
        if task_type:
            cognitive_task_multipliers = {
                'code_analysis': 0.7,
                'code_generation': 0.9,
                'architecture_review': 1.0,
                'optimization': 0.8,
                'debugging': 0.6
            }
            multiplier = cognitive_task_multipliers.get(task_type, 0.5)
            base_score *= multiplier
        
        return min(base_score, 1.0)
    
    def _calculate_computational_complexity(self, 
                                          detected_factors: List[str],
                                          task_type: Optional[str]) -> float:
        """Calcula complejidad computacional"""
        
        base_score = 0.0
        
        # Factores detectados
        for factor in detected_factors:
            if factor in self.computational_factors:
                base_score += self.computational_factors[factor]
        
        # Ajustes por tipo de task
        if task_type:
            computational_task_multipliers = {
                'optimization': 1.0,
                'code_generation': 0.7,
                'code_analysis': 0.5,
                'testing': 0.6
            }
            multiplier = computational_task_multipliers.get(task_type, 0.4)
            base_score *= multiplier
        
        return min(base_score, 1.0)
    
    def _calculate_technical_complexity(self, 
                                      detected_factors: List[str],
                                      file_context_result: Optional[object],
                                      task_type: Optional[str]) -> float:
        """Calcula complejidad técnica"""
        
        base_score = 0.0
        
        # Factores detectados
        for factor in detected_factors:
            if factor in self.technical_factors:
                base_score += self.technical_factors[factor]
        
        # Ajustes por contexto de archivos
        if file_context_result and hasattr(file_context_result, 'complexity_factors'):
            avg_file_complexity = file_context_result.complexity_factors.get('target_file_complexity', 0)
            base_score += avg_file_complexity * 0.4
            
            framework_complexity = file_context_result.complexity_factors.get('framework_complexity', 0)
            base_score += framework_complexity * 0.3
        
        # Ajustes por tipo de task
        if task_type:
            technical_task_multipliers = {
                'code_modification': 1.0,
                'debugging': 0.9,
                'testing': 0.8,
                'documentation': 0.3
            }
            multiplier = technical_task_multipliers.get(task_type, 0.5)
            base_score *= multiplier
        
        return min(base_score, 1.0)
    
    def _calculate_temporal_complexity(self, 
                                     detected_factors: List[str],
                                     linguistic_result: Optional[object]) -> float:
        """Calcula complejidad temporal"""
        
        base_score = 0.0
        
        # Factores detectados
        for factor in detected_factors:
            if factor in self.temporal_factors:
                base_score += self.temporal_factors[factor]
        
        # Ajustes por análisis lingüístico
        if linguistic_result and hasattr(linguistic_result, 'urgency_indicators'):
            urgency_total = sum(linguistic_result.urgency_indicators.values())
            base_score += min(urgency_total * 0.15, 0.4)
        
        return min(base_score, 1.0)
    
    def _calculate_architectural_complexity(self, 
                                          detected_factors: List[str],
                                          file_context_result: Optional[object]) -> float:
        """Calcula complejidad arquitectural"""
        
        base_score = 0.0
        
        # Factores detectados
        for factor in detected_factors:
            if factor in self.architectural_factors:
                base_score += self.architectural_factors[factor]
        
        # Ajustes por contexto de archivos
        if file_context_result and hasattr(file_context_result, 'project_structure'):
            structure = file_context_result.project_structure
            
            # Complejidad por diversidad de lenguajes
            language_count = len(structure.languages_detected) if hasattr(structure, 'languages_detected') else 0
            base_score += min(language_count * 0.1, 0.3)
            
            # Complejidad por frameworks
            framework_count = len(structure.frameworks_detected) if hasattr(structure, 'frameworks_detected') else 0
            base_score += min(framework_count * 0.15, 0.4)
        
        return min(base_score, 1.0)
    
    def _calculate_integration_complexity(self, 
                                        detected_factors: List[str],
                                        file_context_result: Optional[object]) -> float:
        """Calcula complejidad de integración"""
        
        base_score = 0.0
        
        # Factores detectados
        for factor in detected_factors:
            if factor in self.integration_factors:
                base_score += self.integration_factors[factor]
        
        # Ajustes por contexto de archivos
        if file_context_result and hasattr(file_context_result, 'related_files'):
            related_count = len(file_context_result.related_files)
            base_score += min(related_count * 0.05, 0.2)
        
        return min(base_score, 1.0)
    
    def _calculate_complexity_metrics(self, 
                                    detected_factors: List[str],
                                    dimension_scores: Dict[ComplexityDimension, float],
                                    file_context_result: Optional[object]) -> ComplexityMetrics:
        """Calcula métricas específicas de complejidad"""
        
        # Complejidad ciclomática (basada en factores algorítmicos)
        cyclomatic_base = 1.0
        if 'complex_algorithms' in detected_factors:
            cyclomatic_base += 3.0
        if 'parallel_processing' in detected_factors:
            cyclomatic_base += 2.0
        if 'error_handling_complexity' in detected_factors:
            cyclomatic_base += 1.5
        
        cyclomatic_complexity = min(cyclomatic_base / 10.0, 1.0)
        
        # Carga cognitiva
        cognitive_load = dimension_scores[ComplexityDimension.COGNITIVE]
        
        # Factor de deuda técnica
        technical_debt_factor = 0.0
        if 'legacy_system_integration' in detected_factors:
            technical_debt_factor += 0.4
        if 'testing_complexity' in detected_factors:
            technical_debt_factor += 0.3
        technical_debt_factor = min(technical_debt_factor, 1.0)
        
        # Puntos de integración
        integration_points = len([f for f in detected_factors if f in self.integration_factors])
        
        # Profundidad de dependencias
        dependency_depth = 1
        if file_context_result and hasattr(file_context_result, 'related_files'):
            dependency_depth = min(len(file_context_result.related_files) + 1, 10)
        
        # Nivel de abstracción
        abstraction_level = 0.5  # Valor base
        if 'abstract_concepts' in detected_factors:
            abstraction_level += 0.3
        if 'domain_expertise_required' in detected_factors:
            abstraction_level += 0.2
        abstraction_level = min(abstraction_level, 1.0)
        
        # Radio de impacto de cambios
        change_impact_radius = dimension_scores[ComplexityDimension.INTEGRATION] * 0.7 + \
                              dimension_scores[ComplexityDimension.ARCHITECTURAL] * 0.3
        
        # Complejidad de testing
        testing_complexity = 0.0
        if 'testing_complexity' in detected_factors:
            testing_complexity = 0.8
        elif any(f in detected_factors for f in ['parallel_processing', 'real_time_constraints']):
            testing_complexity = 0.6
        else:
            testing_complexity = 0.3
        
        return ComplexityMetrics(
            cyclomatic_complexity=cyclomatic_complexity,
            cognitive_load=cognitive_load,
            technical_debt_factor=technical_debt_factor,
            integration_points=integration_points,
            dependency_depth=dependency_depth,
            abstraction_level=abstraction_level,
            change_impact_radius=change_impact_radius,
            testing_complexity=testing_complexity
        )
    
    def _calculate_overall_complexity(self, dimension_scores: Dict[ComplexityDimension, float]) -> float:
        """Calcula la complejidad general ponderada"""
        
        overall = 0.0
        for dimension, score in dimension_scores.items():
            weight = self.dimension_weights[dimension]
            overall += score * weight
        
        return min(overall, 1.0)
    
    def _determine_risk_level(self, overall_complexity: float, metrics: ComplexityMetrics) -> RiskLevel:
        """Determina el nivel de riesgo basado en complejidad y métricas"""
        
        risk_score = overall_complexity
        
        # Ajustes por métricas críticas
        if metrics.cyclomatic_complexity > 0.8:
            risk_score += 0.1
        if metrics.technical_debt_factor > 0.6:
            risk_score += 0.1
        if metrics.integration_points > 5:
            risk_score += 0.1
        if metrics.change_impact_radius > 0.8:
            risk_score += 0.1
        
        risk_score = min(risk_score, 1.0)
        
        if risk_score >= 0.9:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.7:
            return RiskLevel.HIGH
        elif risk_score >= 0.5:
            return RiskLevel.MODERATE
        elif risk_score >= 0.3:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL
    
    def _generate_mitigation_strategies(self, 
                                      detected_factors: List[str],
                                      dimension_scores: Dict[ComplexityDimension, float],
                                      risk_level: RiskLevel) -> List[str]:
        """Genera estrategias de mitigación de complejidad"""
        
        strategies = []
        
        # Estrategias por nivel de riesgo
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            strategies.append("Consider breaking down into smaller, manageable subtasks")
            strategies.append("Use collaborative multi-agent approach")
            strategies.append("Implement thorough testing and validation")
        
        # Estrategias por dimensión de complejidad alta
        if dimension_scores[ComplexityDimension.COGNITIVE] > 0.7:
            strategies.append("Provide detailed examples and step-by-step guidance")
            strategies.append("Focus on clear documentation and explanations")
        
        if dimension_scores[ComplexityDimension.TECHNICAL] > 0.7:
            strategies.append("Emphasize code quality and best practices")
            strategies.append("Include comprehensive error handling")
        
        if dimension_scores[ComplexityDimension.INTEGRATION] > 0.6:
            strategies.append("Plan for thorough integration testing")
            strategies.append("Consider API versioning and backward compatibility")
        
        # Estrategias por factores específicos
        if 'real_time_constraints' in detected_factors:
            strategies.append("Optimize for performance and latency")
        if 'security_requirements' in detected_factors:
            strategies.append("Implement security best practices and validation")
        if 'legacy_system_integration' in detected_factors:
            strategies.append("Plan for gradual migration and compatibility layers")
        
        return strategies
    
    def _estimate_effort_hours(self, 
                              overall_complexity: float,
                              metrics: ComplexityMetrics,
                              task_type: Optional[str]) -> float:
        """Estima las horas de esfuerzo requeridas"""
        
        # Tiempo base por tipo de task
        base_hours = {
            'code_analysis': 2.0,
            'code_generation': 4.0,
            'code_modification': 3.0,
            'documentation': 1.5,
            'debugging': 3.5,
            'optimization': 5.0,
            'testing': 2.5,
            'architecture_review': 6.0
        }
        
        base = base_hours.get(task_type, 3.0)
        
        # Multiplicador por complejidad
        complexity_multiplier = 1.0 + (overall_complexity * 2.0)
        
        # Ajustes por métricas específicas
        if metrics.cyclomatic_complexity > 0.7:
            complexity_multiplier += 0.5
        if metrics.integration_points > 3:
            complexity_multiplier += 0.3
        if metrics.technical_debt_factor > 0.6:
            complexity_multiplier += 0.4
        
        estimated_hours = base * complexity_multiplier
        
        # Limitar a rangos razonables
        return min(max(estimated_hours, 0.5), 40.0)
    
    def _estimate_tokens(self, 
                        overall_complexity: float,
                        user_input: str,
                        file_context_result: Optional[object]) -> int:
        """Estima los tokens requeridos para el procesamiento"""
        
        # Tokens base del input del usuario
        base_tokens = len(user_input.split()) * 1.3  # Factor de conversión palabra->token
        
        # Tokens adicionales por complejidad
        complexity_tokens = overall_complexity * 2000
        
        # Tokens por contexto de archivos
        context_tokens = 0
        if file_context_result and hasattr(file_context_result, 'target_files'):
            for file_meta in file_context_result.target_files:
                if hasattr(file_meta, 'complexity_estimate'):
                    context_tokens += file_meta.complexity_estimate * 2
        
        # Tokens por archivos relacionados
        if file_context_result and hasattr(file_context_result, 'related_files'):
            context_tokens += len(file_context_result.related_files) * 200
        
        total_tokens = base_tokens + complexity_tokens + context_tokens
        
        # Limitar a rangos razonables
        return int(min(max(total_tokens, 100), 50000))
    
    def _calculate_confidence_score(self, 
                                   linguistic_result: Optional[object],
                                   file_context_result: Optional[object],
                                   factor_count: int) -> float:
        """Calcula la confianza del análisis de complejidad"""
        
        confidence = 0.5  # Base
        
        # Incrementar confianza con más información disponible
        if linguistic_result:
            confidence += 0.2
        if file_context_result:
            confidence += 0.2
        if factor_count > 0:
            confidence += min(factor_count * 0.05, 0.3)
        
        # Penalizar falta de información
        if not linguistic_result and not file_context_result:
            confidence -= 0.2
        
        return min(max(confidence, 0.1), 1.0)
    
    def get_complexity_summary(self, result: ComplexityAnalysisResult) -> Dict[str, any]:
        """
        Genera un resumen ejecutivo del análisis de complejidad.
        
        Args:
            result: Resultado del análisis de complejidad
            
        Returns:
            Dictionary con resumen ejecutivo
        """
        
        return {
            'complexity_level': self._categorize_complexity_level(result.overall_complexity),
            'risk_assessment': result.risk_level.value,
            'primary_complexity_driver': self._identify_primary_driver(result.dimension_scores),
            'estimated_effort': f"{result.estimated_effort_hours:.1f} hours",
            'estimated_tokens': result.estimated_tokens,
            'confidence': f"{result.confidence_score:.0%}",
            'key_challenges': result.complexity_factors[:3],
            'recommended_approach': self._recommend_approach(result),
            'mitigation_priority': result.mitigation_strategies[:2]
        }
    
    def _categorize_complexity_level(self, overall_complexity: float) -> str:
        """Categoriza el nivel de complejidad en términos comprensibles"""
        if overall_complexity >= 0.8:
            return "Very High"
        elif overall_complexity >= 0.6:
            return "High"
        elif overall_complexity >= 0.4:
            return "Moderate"
        elif overall_complexity >= 0.2:
            return "Low"
        else:
            return "Simple"
    
    def _identify_primary_driver(self, dimension_scores: Dict[ComplexityDimension, float]) -> str:
        """Identifica la dimensión que más contribuye a la complejidad"""
        max_dimension = max(dimension_scores, key=dimension_scores.get)
        return max_dimension.value.replace('_', ' ').title()
    
    def _recommend_approach(self, result: ComplexityAnalysisResult) -> str:
        """Recomienda el enfoque basado en el análisis de complejidad"""
        if result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return "Multi-agent collaborative approach with careful coordination"
        elif result.overall_complexity > 0.6:
            return "Sequential multi-agent approach with specialized agents"
        elif result.overall_complexity > 0.3:
            return "Single specialized agent with comprehensive context"
        else:
            return "Single general-purpose agent should suffice"
