"""
FASE 3: Motor de Scoring Multi-Criterio y Selección Inteligente
Sistema avanzado de puntuación que considera múltiples factores para selección óptima de agentes.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import json
import time
from datetime import datetime, timedelta
import statistics

from .task_classifier import TaskType, TaskAnalysisResult, SpecialCharacteristics
from .agent_specializations import AgentType, AgentSpecializationManager


class ScoreComponent(Enum):
    """Componentes del score de selección"""
    SPECIALIZATION = "specialization"      # 40% del peso
    PERFORMANCE_HISTORY = "performance"    # 25% del peso
    TASK_CHARACTERISTICS = "characteristics"  # 15% del peso
    API_AVAILABILITY = "availability"      # 10% del peso
    COST_OPTIMIZATION = "cost"            # 10% del peso


@dataclass
class PerformanceRecord:
    """Registro de rendimiento de un agente"""
    agent_type: AgentType
    task_type: TaskType
    execution_time: float
    confidence_score: float
    success: bool
    timestamp: datetime
    cost: float
    user_feedback: Optional[float] = None  # 1-5 rating del usuario
    complexity_handled: str = "medium"
    tokens_used: int = 0


@dataclass
class ApiHealthStatus:
    """Estado de salud de una API"""
    agent_type: AgentType
    is_available: bool
    latency_ms: float
    rate_limit_remaining: int
    quota_remaining: int
    error_count_last_hour: int
    last_check: datetime
    consecutive_failures: int = 0


@dataclass
class ScoringWeights:
    """Pesos para los diferentes componentes del scoring"""
    specialization: float = 0.40
    performance_history: float = 0.25
    task_characteristics: float = 0.15
    api_availability: float = 0.10
    cost_optimization: float = 0.10
    
    def validate(self) -> bool:
        """Valida que los pesos sumen 1.0"""
        total = (self.specialization + self.performance_history + 
                self.task_characteristics + self.api_availability + 
                self.cost_optimization)
        return abs(total - 1.0) < 0.01


@dataclass
class DetailedScore:
    """Score detallado con breakdown por componente"""
    agent_type: AgentType
    total_score: float
    specialization_score: float
    performance_score: float
    characteristics_score: float
    availability_score: float
    cost_score: float
    breakdown: Dict[str, float]
    confidence_level: float
    explanation: List[str]


class SpecializationScorer:
    """Calculadora de scores de especialización (40% del peso total)"""
    
    def __init__(self):
        self.specialization_manager = AgentSpecializationManager()
        self._initialize_task_agent_matrix()
        self._initialize_characteristic_bonuses()
    
    def _initialize_task_agent_matrix(self):
        """Inicializa matriz de alineación agente-task"""
        self.task_agent_matrix = {
            TaskType.CODE_ANALYSIS: {
                AgentType.GEMINI: 0.95,    # Máximo en análisis
                AgentType.CLAUDE: 0.75,
                AgentType.OPENAI: 0.65
            },
            TaskType.CODE_GENERATION: {
                AgentType.CLAUDE: 0.95,    # Máximo en generación
                AgentType.GEMINI: 0.70,
                AgentType.OPENAI: 0.80
            },
            TaskType.CODE_MODIFICATION: {
                AgentType.CLAUDE: 0.90,
                AgentType.GEMINI: 0.85,
                AgentType.OPENAI: 0.65
            },
            TaskType.DEBUGGING: {
                AgentType.CLAUDE: 0.95,    # Máximo en debugging
                AgentType.GEMINI: 0.90,
                AgentType.OPENAI: 0.60
            },
            TaskType.DOCUMENTATION: {
                AgentType.OPENAI: 0.95,    # Máximo en documentación
                AgentType.CLAUDE: 0.70,
                AgentType.GEMINI: 0.60
            },
            TaskType.OPTIMIZATION: {
                AgentType.GEMINI: 0.90,    # Análisis para optimización
                AgentType.CLAUDE: 0.85,
                AgentType.OPENAI: 0.55
            },
            TaskType.TESTING: {
                AgentType.CLAUDE: 0.85,
                AgentType.GEMINI: 0.80,
                AgentType.OPENAI: 0.65
            },
            TaskType.ARCHITECTURE_REVIEW: {
                AgentType.GEMINI: 0.90,    # Análisis arquitectural
                AgentType.CLAUDE: 0.85,
                AgentType.OPENAI: 0.60
            }
        }
    
    def _initialize_characteristic_bonuses(self):
        """Inicializa bonificaciones por características especiales"""
        self.characteristic_bonuses = {
            SpecialCharacteristics.REQUIRES_PRECISION: {
                AgentType.CLAUDE: 0.20,
                AgentType.GEMINI: 0.15,
                AgentType.OPENAI: 0.05
            },
            SpecialCharacteristics.REQUIRES_CREATIVITY: {
                AgentType.OPENAI: 0.20,
                AgentType.CLAUDE: 0.10,
                AgentType.GEMINI: 0.05
            },
            SpecialCharacteristics.REQUIRES_SPEED: {
                AgentType.OPENAI: 0.20,
                AgentType.GEMINI: 0.15,
                AgentType.CLAUDE: 0.05
            },
            SpecialCharacteristics.REQUIRES_EXPLANATION: {
                AgentType.CLAUDE: 0.15,
                AgentType.OPENAI: 0.10,
                AgentType.GEMINI: 0.05
            },
            SpecialCharacteristics.MULTI_FILE_ANALYSIS: {
                AgentType.GEMINI: 0.15,
                AgentType.CLAUDE: 0.10,
                AgentType.OPENAI: 0.05
            },
            SpecialCharacteristics.REQUIRES_EXTERNAL_KNOWLEDGE: {
                AgentType.CLAUDE: 0.15,
                AgentType.GEMINI: 0.10,
                AgentType.OPENAI: 0.05
            },
            SpecialCharacteristics.CROSS_PLATFORM_COMPATIBILITY: {
                AgentType.OPENAI: 0.15,
                AgentType.GEMINI: 0.10,
                AgentType.CLAUDE: 0.05
            }
        }
    
    def calculate_specialization_score(self, agent_type: AgentType, 
                                     task_analysis: TaskAnalysisResult) -> Tuple[float, List[str]]:
        """Calcula el score de especialización para un agente específico"""
        
        explanations = []
        
        # Score base de la matriz agente-task
        base_score = self.task_agent_matrix.get(
            task_analysis.primary_task_type, {}
        ).get(agent_type, 0.5)
        
        explanations.append(f"Score base para {task_analysis.primary_task_type.value}: {base_score:.3f}")
        
        # Aplicar bonificaciones por características especiales
        total_bonus = 0.0
        for characteristic in task_analysis.special_characteristics:
            bonus = self.characteristic_bonuses.get(characteristic, {}).get(agent_type, 0.0)
            total_bonus += bonus
            if bonus > 0:
                explanations.append(f"Bonus por {characteristic.value}: +{bonus:.3f}")
        
        # Score final (asegurar que no exceda 1.0)
        final_score = min(base_score + total_bonus, 1.0)
        
        # Considerar tasks secundarios
        secondary_boost = 0.0
        for secondary_task in task_analysis.secondary_task_types:
            secondary_score = self.task_agent_matrix.get(secondary_task, {}).get(agent_type, 0.0)
            secondary_boost += secondary_score * 0.1  # 10% del score por task secundario
        
        final_score = min(final_score + secondary_boost, 1.0)
        
        if secondary_boost > 0:
            explanations.append(f"Boost por tasks secundarios: +{secondary_boost:.3f}")
        
        return final_score, explanations


class PerformanceHistoryAnalyzer:
    """Analizador de rendimiento histórico (25% del peso total)"""
    
    def __init__(self, performance_data_file: str = "agent_performance_history.json"):
        self.performance_data_file = performance_data_file
        self.performance_records: List[PerformanceRecord] = []
        self._load_performance_data()
    
    def _load_performance_data(self):
        """Carga datos de rendimiento histórico"""
        try:
            with open(self.performance_data_file, 'r') as f:
                data = json.load(f)
                for record_data in data:
                    record = PerformanceRecord(
                        agent_type=AgentType(record_data['agent_type']),
                        task_type=TaskType(record_data['task_type']),
                        execution_time=record_data['execution_time'],
                        confidence_score=record_data['confidence_score'],
                        success=record_data['success'],
                        timestamp=datetime.fromisoformat(record_data['timestamp']),
                        cost=record_data['cost'],
                        user_feedback=record_data.get('user_feedback'),
                        complexity_handled=record_data.get('complexity_handled', 'medium'),
                        tokens_used=record_data.get('tokens_used', 0)
                    )
                    self.performance_records.append(record)
        except FileNotFoundError:
            # Inicializar con datos simulados para desarrollo
            self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Inicializa con datos de muestra para desarrollo"""
        sample_data = [
            # Gemini - Excelente en análisis
            PerformanceRecord(AgentType.GEMINI, TaskType.CODE_ANALYSIS, 45.2, 0.92, True, 
                            datetime.now() - timedelta(days=1), 0.15, 4.5, "complex", 3200),
            PerformanceRecord(AgentType.GEMINI, TaskType.CODE_ANALYSIS, 38.7, 0.89, True, 
                            datetime.now() - timedelta(days=3), 0.12, 4.3, "medium", 2800),
            PerformanceRecord(AgentType.GEMINI, TaskType.OPTIMIZATION, 52.1, 0.91, True, 
                            datetime.now() - timedelta(days=2), 0.18, 4.4, "complex", 3500),
            
            # Claude - Excelente en generación y debugging
            PerformanceRecord(AgentType.CLAUDE, TaskType.CODE_GENERATION, 62.3, 0.88, True, 
                            datetime.now() - timedelta(days=1), 0.22, 4.6, "complex", 4100),
            PerformanceRecord(AgentType.CLAUDE, TaskType.DEBUGGING, 41.5, 0.90, True, 
                            datetime.now() - timedelta(days=2), 0.19, 4.5, "medium", 3300),
            PerformanceRecord(AgentType.CLAUDE, TaskType.CODE_MODIFICATION, 55.8, 0.87, True, 
                            datetime.now() - timedelta(days=4), 0.20, 4.2, "complex", 3800),
            
            # OpenAI - Excelente en documentación
            PerformanceRecord(AgentType.OPENAI, TaskType.DOCUMENTATION, 48.9, 0.85, True, 
                            datetime.now() - timedelta(days=1), 0.16, 4.7, "medium", 2900),
            PerformanceRecord(AgentType.OPENAI, TaskType.DOCUMENTATION, 56.2, 0.83, True, 
                            datetime.now() - timedelta(days=3), 0.18, 4.4, "complex", 3400),
        ]
        self.performance_records = sample_data
    
    def calculate_performance_score(self, agent_type: AgentType, 
                                  task_analysis: TaskAnalysisResult) -> Tuple[float, List[str]]:
        """Calcula score de rendimiento histórico"""
        
        explanations = []
        
        # Filtrar registros relevantes (últimos 30 días)
        cutoff_date = datetime.now() - timedelta(days=30)
        relevant_records = [
            r for r in self.performance_records 
            if r.agent_type == agent_type and r.timestamp >= cutoff_date
        ]
        
        if not relevant_records:
            explanations.append("Sin historial reciente - score neutral 0.5")
            return 0.5, explanations
        
        # Calcular métricas
        success_rate = sum(1 for r in relevant_records if r.success) / len(relevant_records)
        avg_confidence = statistics.mean(r.confidence_score for r in relevant_records)
        
        # Filtrar por tipo de task específico
        task_specific_records = [
            r for r in relevant_records 
            if r.task_type == task_analysis.primary_task_type
        ]
        
        task_specific_bonus = 0.0
        if task_specific_records:
            task_success_rate = sum(1 for r in task_specific_records if r.success) / len(task_specific_records)
            task_avg_confidence = statistics.mean(r.confidence_score for r in task_specific_records)
            task_specific_bonus = (task_success_rate * 0.3) + (task_avg_confidence * 0.2)
            explanations.append(f"Bonus específico por {task_analysis.primary_task_type.value}: +{task_specific_bonus:.3f}")
        
        # Calcular score base
        base_score = (success_rate * 0.4) + (avg_confidence * 0.4)
        
        # Aplicar bonus por feedback de usuario
        feedback_records = [r for r in relevant_records if r.user_feedback is not None]
        feedback_bonus = 0.0
        if feedback_records:
            avg_feedback = statistics.mean(r.user_feedback for r in feedback_records)
            feedback_bonus = (avg_feedback - 3.0) * 0.05  # Escala de -0.1 a +0.1
            explanations.append(f"Bonus por feedback usuario: {feedback_bonus:+.3f}")
        
        final_score = min(base_score + task_specific_bonus + feedback_bonus, 1.0)
        
        explanations.extend([
            f"Success rate últimos 30 días: {success_rate:.1%}",
            f"Confidence promedio: {avg_confidence:.3f}",
            f"Registros analizados: {len(relevant_records)}"
        ])
        
        return final_score, explanations
    
    def add_performance_record(self, record: PerformanceRecord):
        """Añade un nuevo registro de rendimiento"""
        self.performance_records.append(record)
        self._save_performance_data()
    
    def _save_performance_data(self):
        """Guarda datos de rendimiento a archivo"""
        try:
            data = []
            for record in self.performance_records:
                data.append({
                    'agent_type': record.agent_type.value,
                    'task_type': record.task_type.value,
                    'execution_time': record.execution_time,
                    'confidence_score': record.confidence_score,
                    'success': record.success,
                    'timestamp': record.timestamp.isoformat(),
                    'cost': record.cost,
                    'user_feedback': record.user_feedback,
                    'complexity_handled': record.complexity_handled,
                    'tokens_used': record.tokens_used
                })
            
            with open(self.performance_data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error guardando datos de rendimiento: {e}")


class TaskCharacteristicsEvaluator:
    """Evaluador de características del task (15% del peso total)"""
    
    def calculate_characteristics_score(self, agent_type: AgentType, 
                                      task_analysis: TaskAnalysisResult) -> Tuple[float, List[str]]:
        """Calcula score basado en características del task"""
        
        explanations = []
        base_score = 0.5  # Score neutral base
        
        # Bonificación por complejidad manejada
        complexity_bonuses = {
            'minimal': 0.0,
            'low': 0.1,
            'medium': 0.15,
            'high': 0.2,
            'critical': 0.25
        }
        
        complexity_bonus = complexity_bonuses.get(task_analysis.complexity_level.value, 0.0)
        
        # Ajustar bonus según la especialidad del agente para manejar complejidad
        complexity_handling = {
            AgentType.GEMINI: 0.95,    # Excelente con análisis complejos
            AgentType.CLAUDE: 0.90,    # Muy bueno con implementaciones complejas
            AgentType.OPENAI: 0.75     # Bueno con explicaciones complejas
        }
        
        adjusted_complexity_bonus = complexity_bonus * complexity_handling.get(agent_type, 0.8)
        explanations.append(f"Bonus por complejidad {task_analysis.complexity_level.value}: +{adjusted_complexity_bonus:.3f}")
        
        # Bonificación por número de archivos
        if hasattr(task_analysis, 'file_analysis') and task_analysis.file_analysis:
            file_count = len(task_analysis.file_analysis.relevant_files) if hasattr(task_analysis.file_analysis, 'relevant_files') else 1
            
            file_bonuses = {
                AgentType.GEMINI: {1: 0.0, 2: 0.05, 5: 0.1, 10: 0.15},
                AgentType.CLAUDE: {1: 0.0, 2: 0.03, 5: 0.08, 10: 0.12},
                AgentType.OPENAI: {1: 0.0, 2: 0.02, 5: 0.05, 10: 0.08}
            }
            
            # Encontrar el bonus apropiado
            file_bonus = 0.0
            for threshold in sorted(file_bonuses[agent_type].keys(), reverse=True):
                if file_count >= threshold:
                    file_bonus = file_bonuses[agent_type][threshold]
                    break
            
            if file_bonus > 0:
                explanations.append(f"Bonus por {file_count} archivos: +{file_bonus:.3f}")
        else:
            file_bonus = 0.0
        
        # Penalizaciones por requisitos no alineados
        penalties = 0.0
        
        # Si requiere creatividad pero el agente no es creativo
        if (SpecialCharacteristics.REQUIRES_CREATIVITY in task_analysis.special_characteristics and 
            agent_type != AgentType.OPENAI):
            creativity_penalty = 0.1 if agent_type == AgentType.CLAUDE else 0.15
            penalties += creativity_penalty
            explanations.append(f"Penalización por baja creatividad: -{creativity_penalty:.3f}")
        
        # Si requiere precisión extrema pero el agente es más creativo
        if (SpecialCharacteristics.REQUIRES_PRECISION in task_analysis.special_characteristics and 
            agent_type == AgentType.OPENAI):
            precision_penalty = 0.1
            penalties += precision_penalty
            explanations.append(f"Penalización por menor precisión: -{precision_penalty:.3f}")
        
        # Calcular score final
        final_score = max(base_score + adjusted_complexity_bonus + file_bonus - penalties, 0.0)
        final_score = min(final_score, 1.0)
        
        return final_score, explanations


class ApiAvailabilityMonitor:
    """Monitor de disponibilidad y performance de APIs (10% del peso total)"""
    
    def __init__(self):
        self.health_status: Dict[AgentType, ApiHealthStatus] = {}
        self._initialize_health_status()
    
    def _initialize_health_status(self):
        """Inicializa estado de salud con valores simulados"""
        # En implementación real, estos valores vendrían de health checks reales
        for agent_type in AgentType:
            self.health_status[agent_type] = ApiHealthStatus(
                agent_type=agent_type,
                is_available=True,
                latency_ms=250.0 + (hash(agent_type.value) % 100),  # Simular latencias diferentes
                rate_limit_remaining=1000,
                quota_remaining=50000,
                error_count_last_hour=0,
                last_check=datetime.now(),
                consecutive_failures=0
            )
    
    def calculate_availability_score(self, agent_type: AgentType) -> Tuple[float, List[str]]:
        """Calcula score de disponibilidad"""
        
        explanations = []
        status = self.health_status.get(agent_type)
        
        if not status:
            explanations.append("Estado desconocido - score neutral")
            return 0.5, explanations
        
        if not status.is_available:
            explanations.append("API no disponible")
            return 0.0, explanations
        
        base_score = 1.0
        
        # Penalización por alta latencia
        if status.latency_ms > 500:
            latency_penalty = min(0.3, (status.latency_ms - 500) / 1000)
            base_score -= latency_penalty
            explanations.append(f"Penalización por latencia ({status.latency_ms:.0f}ms): -{latency_penalty:.3f}")
        
        # Penalización por rate limit bajo
        if status.rate_limit_remaining < 100:
            rate_limit_penalty = 0.2
            base_score -= rate_limit_penalty
            explanations.append(f"Penalización por rate limit bajo: -{rate_limit_penalty:.3f}")
        
        # Penalización por errores recientes
        if status.error_count_last_hour > 0:
            error_penalty = min(0.1 * status.error_count_last_hour, 0.3)
            base_score -= error_penalty
            explanations.append(f"Penalización por {status.error_count_last_hour} errores: -{error_penalty:.3f}")
        
        final_score = max(base_score, 0.0)
        
        if final_score > 0.8:
            explanations.append(f"API en excelente estado (latencia: {status.latency_ms:.0f}ms)")
        
        return final_score, explanations
    
    def update_health_status(self, agent_type: AgentType, status: ApiHealthStatus):
        """Actualiza estado de salud de una API"""
        self.health_status[agent_type] = status
    
    def perform_health_check(self, agent_type: AgentType) -> bool:
        """Realiza un health check real (simplificado para demo)"""
        # En implementación real, esto haría requests reales a las APIs
        import random
        
        # Simular variaciones en el estado
        current_status = self.health_status.get(agent_type)
        if current_status:
            # Simular cambios ocasionales en latencia y disponibilidad
            new_latency = current_status.latency_ms + random.uniform(-50, 50)
            new_latency = max(100, min(1000, new_latency))  # Mantener en rango realista
            
            current_status.latency_ms = new_latency
            current_status.last_check = datetime.now()
            current_status.is_available = random.random() > 0.05  # 95% uptime
            
            return current_status.is_available
        
        return True


class CostOptimizer:
    """Optimizador de costos (10% del peso total)"""
    
    def __init__(self):
        # Costos por token para cada agente (valores aproximados en USD)
        self.token_costs = {
            AgentType.GEMINI: 0.0001,
            AgentType.CLAUDE: 0.0002,
            AgentType.OPENAI: 0.00015
        }
        
        # Límites de presupuesto
        self.daily_budget_limit = 10.0  # $10 por día
        self.monthly_budget_limit = 200.0  # $200 por mes
        self.current_daily_spend = 0.0
        self.current_monthly_spend = 0.0
    
    def calculate_cost_score(self, agent_type: AgentType, 
                           task_analysis: TaskAnalysisResult) -> Tuple[float, List[str]]:
        """Calcula score de optimización de costos"""
        
        explanations = []
        
        # Estimar tokens necesarios
        estimated_tokens = self._estimate_tokens_needed(task_analysis)
        
        # Calcular costo estimado
        token_cost = self.token_costs.get(agent_type, 0.00015)
        estimated_cost = estimated_tokens * token_cost
        
        explanations.append(f"Tokens estimados: {estimated_tokens}")
        explanations.append(f"Costo estimado: ${estimated_cost:.4f}")
        
        # Score base inversamente proporcional al costo
        base_score = 1.0 - min(estimated_cost / 1.0, 0.5)  # Máximo 50% de penalización
        
        # Penalizaciones por límites de presupuesto
        budget_penalty = 0.0
        
        # Verificar límite diario
        if self.current_daily_spend + estimated_cost > self.daily_budget_limit:
            daily_penalty = 0.3
            budget_penalty += daily_penalty
            explanations.append(f"Penalización por límite diario: -{daily_penalty:.3f}")
        
        # Verificar límite mensual
        if self.current_monthly_spend + estimated_cost > self.monthly_budget_limit:
            monthly_penalty = 0.2
            budget_penalty += monthly_penalty
            explanations.append(f"Penalización por límite mensual: -{monthly_penalty:.3f}")
        
        # Bonificación por ser el agente más económico
        cheapest_cost = min(self.token_costs.values())
        if token_cost == cheapest_cost:
            cost_bonus = 0.1
            base_score += cost_bonus
            explanations.append(f"Bonus por ser más económico: +{cost_bonus:.3f}")
        
        final_score = max(base_score - budget_penalty, 0.0)
        final_score = min(final_score, 1.0)
        
        return final_score, explanations
    
    def _estimate_tokens_needed(self, task_analysis: TaskAnalysisResult) -> int:
        """Estima tokens necesarios basado en análisis del task"""
        
        base_tokens = {
            'minimal': 2000,
            'low': 4000,
            'medium': 6000,
            'high': 10000,
            'critical': 15000
        }
        
        complexity = task_analysis.complexity_level.value
        estimated = base_tokens.get(complexity, 6000)
        
        # Ajustes por tipo de task
        task_multipliers = {
            TaskType.DOCUMENTATION: 1.2,
            TaskType.CODE_ANALYSIS: 1.3,
            TaskType.DEBUGGING: 1.15,
            TaskType.CODE_GENERATION: 1.1,
            TaskType.OPTIMIZATION: 1.25
        }
        
        multiplier = task_multipliers.get(task_analysis.primary_task_type, 1.0)
        estimated = int(estimated * multiplier)
        
        # Ajuste por características especiales
        for characteristic in task_analysis.special_characteristics:
            if characteristic == SpecialCharacteristics.REQUIRES_EXPLANATION:
                estimated = int(estimated * 1.15)
            elif characteristic == SpecialCharacteristics.MULTI_FILE_ANALYSIS:
                estimated = int(estimated * 1.25)
        
        return estimated
    
    def record_spend(self, amount: float):
        """Registra gasto realizado"""
        self.current_daily_spend += amount
        self.current_monthly_spend += amount


class IntelligentScoringEngine:
    """Motor principal de scoring multi-criterio"""
    
    def __init__(self, weights: Optional[ScoringWeights] = None):
        self.weights = weights or ScoringWeights()
        self.weights.validate()
        
        # Inicializar componentes
        self.specialization_scorer = SpecializationScorer()
        self.performance_analyzer = PerformanceHistoryAnalyzer()
        self.characteristics_evaluator = TaskCharacteristicsEvaluator()
        self.availability_monitor = ApiAvailabilityMonitor()
        self.cost_optimizer = CostOptimizer()
    
    def calculate_detailed_scores(self, task_analysis: TaskAnalysisResult) -> List[DetailedScore]:
        """Calcula scores detallados para todos los agentes"""
        
        detailed_scores = []
        
        for agent_type in AgentType:
            # Calcular cada componente del score
            spec_score, spec_explanations = self.specialization_scorer.calculate_specialization_score(
                agent_type, task_analysis
            )
            
            perf_score, perf_explanations = self.performance_analyzer.calculate_performance_score(
                agent_type, task_analysis
            )
            
            char_score, char_explanations = self.characteristics_evaluator.calculate_characteristics_score(
                agent_type, task_analysis
            )
            
            avail_score, avail_explanations = self.availability_monitor.calculate_availability_score(
                agent_type
            )
            
            cost_score, cost_explanations = self.cost_optimizer.calculate_cost_score(
                agent_type, task_analysis
            )
            
            # Calcular score total ponderado
            total_score = (
                spec_score * self.weights.specialization +
                perf_score * self.weights.performance_history +
                char_score * self.weights.task_characteristics +
                avail_score * self.weights.api_availability +
                cost_score * self.weights.cost_optimization
            )
            
            # Calcular nivel de confianza
            confidence_level = self._calculate_confidence_level(
                spec_score, perf_score, char_score, avail_score, cost_score
            )
            
            # Compilar explicaciones
            all_explanations = []
            all_explanations.extend([f"[Especialización] {exp}" for exp in spec_explanations])
            all_explanations.extend([f"[Rendimiento] {exp}" for exp in perf_explanations])
            all_explanations.extend([f"[Características] {exp}" for exp in char_explanations])
            all_explanations.extend([f"[Disponibilidad] {exp}" for exp in avail_explanations])
            all_explanations.extend([f"[Costo] {exp}" for exp in cost_explanations])
            
            detailed_score = DetailedScore(
                agent_type=agent_type,
                total_score=total_score,
                specialization_score=spec_score,
                performance_score=perf_score,
                characteristics_score=char_score,
                availability_score=avail_score,
                cost_score=cost_score,
                breakdown={
                    'specialization': spec_score * self.weights.specialization,
                    'performance': perf_score * self.weights.performance_history,
                    'characteristics': char_score * self.weights.task_characteristics,
                    'availability': avail_score * self.weights.api_availability,
                    'cost': cost_score * self.weights.cost_optimization
                },
                confidence_level=confidence_level,
                explanation=all_explanations
            )
            
            detailed_scores.append(detailed_score)
        
        # Ordenar por score total
        detailed_scores.sort(key=lambda x: x.total_score, reverse=True)
        
        return detailed_scores
    
    def _calculate_confidence_level(self, spec_score: float, perf_score: float, 
                                  char_score: float, avail_score: float, 
                                  cost_score: float) -> float:
        """Calcula nivel de confianza en la selección"""
        
        # Confianza basada en consistencia de scores
        scores = [spec_score, perf_score, char_score, avail_score, cost_score]
        avg_score = statistics.mean(scores)
        variance = statistics.variance(scores) if len(scores) > 1 else 0
        
        # Alta confianza si los scores son consistentemente altos
        # Baja confianza si hay mucha variación entre scores
        confidence = avg_score * (1.0 - min(variance, 0.3))
        
        return max(0.0, min(1.0, confidence))
    
    def get_best_agent(self, task_analysis: TaskAnalysisResult) -> DetailedScore:
        """Obtiene el mejor agente para un task específico"""
        
        detailed_scores = self.calculate_detailed_scores(task_analysis)
        return detailed_scores[0]  # El primer elemento es el mejor score
    
    def update_performance_record(self, record: PerformanceRecord):
        """Actualiza el historial de rendimiento"""
        self.performance_analyzer.add_performance_record(record)
    
    def calculate_agent_scores(self, task_analysis: TaskAnalysisResult, 
                             available_agents: List[AgentType]) -> List[DetailedScore]:
        """Calcula scores solo para agentes disponibles"""
        all_scores = self.calculate_detailed_scores(task_analysis)
        return [score for score in all_scores if score.agent_type in available_agents]
    
    def get_scoring_summary(self) -> Dict[str, Any]:
        """Genera resumen del estado del sistema de scoring"""
        return {
            "weights": {
                "specialization": self.weights.specialization,
                "performance_history": self.weights.performance_history,
                "task_characteristics": self.weights.task_characteristics,
                "api_availability": self.weights.api_availability,
                "cost_optimization": self.weights.cost_optimization
            },
            "performance_records_count": len(self.performance_analyzer.performance_history),
            "api_status_count": len(self.availability_monitor.current_status),
            "last_update": datetime.now().isoformat()
        }
