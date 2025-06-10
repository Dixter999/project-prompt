"""
Sistema Multi-Agente - FASE 2: Especializaciones de Agentes
Configuración detallada de fortalezas, configuraciones óptimas y casos de uso por agente.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import json


class AgentType(Enum):
    """Tipos de agentes funcionales disponibles en el sistema"""
    # API Types (legacy)
    GEMINI = "gemini"
    CLAUDE = "claude"
    OPENAI = "openai"
    
    # Functional Agent Types for FASE 5
    PLANNER = "planner"
    CODER = "coder"
    REVIEWER = "reviewer"
    OPTIMIZER = "optimizer"
    DEBUGGER = "debugger"
    TESTER = "tester"
    DOCUMENTER = "documenter"
    ARCHITECT = "architect"
    ANALYST = "analyst"
    PROBLEM_SOLVER = "problem_solver"
    CODE_IMPLEMENTER = "code_implementer"
    QUALITY_ASSURANCE = "quality_assurance"
    VALIDATOR = "validator"
    PERFORMANCE_ENGINEER = "performance_engineer"
    TECHNICAL_WRITER = "technical_writer"


class ApiType(Enum):
    """Tipos de APIs disponibles en el sistema"""
    GEMINI = "gemini"
    CLAUDE = "claude"
    OPENAI = "openai"


class SpecializationArea(Enum):
    """Áreas de especialización de los agentes"""
    CODE_ANALYSIS = "code_analysis"
    CODE_GENERATION = "code_generation"
    CODE_REFACTORING = "code_refactoring"
    DEBUGGING = "debugging"
    SECURITY_AUDIT = "security_audit"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    DOCUMENTATION = "documentation"
    ARCHITECTURE_DESIGN = "architecture_design"
    DATA_ANALYSIS = "data_analysis"
    TUTORIAL_CREATION = "tutorial_creation"


class UseCaseCategory(Enum):
    """Categorías de casos de uso"""
    COMPLEX_ANALYSIS = "complex_analysis"
    DETAILED_IMPLEMENTATION = "detailed_implementation"
    CREATIVE_DOCUMENTATION = "creative_documentation"
    SECURITY_FOCUSED = "security_focused"
    EDUCATIONAL_CONTENT = "educational_content"


@dataclass
class AgentConfiguration:
    """Configuración óptima para un agente específico"""
    temperature: float
    max_tokens: int
    top_p: float
    frequency_penalty: float
    presence_penalty: float
    system_prompt_focus: str
    context_window_usage: float  # Porcentaje del contexto a utilizar


@dataclass
class AgentStrength:
    """Fortaleza específica de un agente"""
    area: SpecializationArea
    proficiency_score: float  # 0.0 - 1.0
    confidence_level: float   # 0.0 - 1.0
    use_cases: List[str]
    optimal_conditions: List[str]


@dataclass
class AgentSpecialization:
    """Especialización completa de un agente"""
    agent_type: AgentType
    primary_strengths: List[AgentStrength]
    secondary_strengths: List[AgentStrength]
    optimal_configuration: AgentConfiguration
    preferred_use_cases: List[UseCaseCategory]
    collaboration_affinity: Dict[AgentType, float]  # Qué tan bien colabora con otros agentes
    performance_metrics: Dict[str, float]


class AgentSpecializationManager:
    """
    Gestor de especializaciones de agentes
    Administra las configuraciones, fortalezas y casos de uso óptimos para cada agente.
    """
    
    def __init__(self):
        self._initialize_agent_specializations()
        self._initialize_collaboration_matrix()
        
    def _initialize_agent_specializations(self):
        """Inicializa las especializaciones detalladas de cada agente"""
        
        # Especialización de Gemini
        gemini_strengths = [
            AgentStrength(
                area=SpecializationArea.CODE_ANALYSIS,
                proficiency_score=0.95,
                confidence_level=0.92,
                use_cases=[
                    "Análisis profundo de código complejo",
                    "Detección de patrones y anti-patrones",
                    "Evaluación de calidad de código",
                    "Identificación de dependencias circulares"
                ],
                optimal_conditions=[
                    "Archivos grandes con múltiples funcionalidades",
                    "Código legacy que requiere comprensión profunda",
                    "Sistemas con arquitectura compleja"
                ]
            ),
            AgentStrength(
                area=SpecializationArea.SECURITY_AUDIT,
                proficiency_score=0.90,
                confidence_level=0.88,
                use_cases=[
                    "Identificación de vulnerabilidades de seguridad",
                    "Análisis de exposición de datos sensibles",
                    "Evaluación de prácticas de autenticación",
                    "Detección de inyecciones SQL y XSS"
                ],
                optimal_conditions=[
                    "Aplicaciones web con manejo de usuarios",
                    "APIs con endpoints críticos",
                    "Sistemas con procesamiento de pagos"
                ]
            ),
            AgentStrength(
                area=SpecializationArea.PERFORMANCE_ANALYSIS,
                proficiency_score=0.88,
                confidence_level=0.85,
                use_cases=[
                    "Identificación de bottlenecks de rendimiento",
                    "Análisis de complejidad algorítmica",
                    "Optimización de queries de base de datos",
                    "Evaluación de uso de memoria"
                ],
                optimal_conditions=[
                    "Aplicaciones con problemas de escalabilidad",
                    "Algoritmos de procesamiento intensivo",
                    "Sistemas con alta concurrencia"
                ]
            ),
            AgentStrength(
                area=SpecializationArea.DATA_ANALYSIS,
                proficiency_score=0.85,
                confidence_level=0.82,
                use_cases=[
                    "Procesamiento de datasets complejos",
                    "Identificación de tendencias y patrones",
                    "Análisis estadístico de métricas",
                    "Visualización de datos complejos"
                ],
                optimal_conditions=[
                    "Archivos con grandes volúmenes de datos",
                    "Análisis de logs y métricas",
                    "Estudios de comportamiento de usuario"
                ]
            )
        ]
        
        gemini_config = AgentConfiguration(
            temperature=0.1,
            max_tokens=8000,
            top_p=0.95,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            system_prompt_focus="análisis_metodológico_profundo",
            context_window_usage=0.9
        )
        
        self.gemini_spec = AgentSpecialization(
            agent_type=AgentType.GEMINI,
            primary_strengths=gemini_strengths[:2],
            secondary_strengths=gemini_strengths[2:],
            optimal_configuration=gemini_config,
            preferred_use_cases=[
                UseCaseCategory.COMPLEX_ANALYSIS,
                UseCaseCategory.SECURITY_FOCUSED
            ],
            collaboration_affinity={
                AgentType.CLAUDE: 0.95,  # Excelente para análisis → implementación
                AgentType.OPENAI: 0.85   # Bueno para análisis → documentación
            },
            performance_metrics={
                "accuracy": 0.92,
                "depth": 0.95,
                "speed": 0.78,
                "consistency": 0.90
            }
        )
        
        # Especialización de Claude
        claude_strengths = [
            AgentStrength(
                area=SpecializationArea.CODE_GENERATION,
                proficiency_score=0.93,
                confidence_level=0.90,
                use_cases=[
                    "Generación de código limpio y estructurado",
                    "Implementación de funcionalidades complejas",
                    "Creación de APIs REST robustas",
                    "Desarrollo de componentes reutilizables"
                ],
                optimal_conditions=[
                    "Proyectos nuevos que requieren arquitectura sólida",
                    "Implementación de features complejas",
                    "Desarrollo de módulos críticos"
                ]
            ),
            AgentStrength(
                area=SpecializationArea.CODE_REFACTORING,
                proficiency_score=0.91,
                confidence_level=0.88,
                use_cases=[
                    "Refactoring manteniendo funcionalidad",
                    "Mejora de legibilidad de código",
                    "Aplicación de patrones de diseño",
                    "Optimización de estructura de clases"
                ],
                optimal_conditions=[
                    "Código legacy que necesita modernización",
                    "Sistemas con deuda técnica acumulada",
                    "Proyectos que requieren escalabilidad"
                ]
            ),
            AgentStrength(
                area=SpecializationArea.DEBUGGING,
                proficiency_score=0.89,
                confidence_level=0.87,
                use_cases=[
                    "Debugging sistemático de errores complejos",
                    "Resolución de race conditions",
                    "Identificación de memory leaks",
                    "Corrección de lógica de negocio"
                ],
                optimal_conditions=[
                    "Bugs intermitentes difíciles de reproducir",
                    "Errores en sistemas distribuidos",
                    "Problemas de concurrencia"
                ]
            ),
            AgentStrength(
                area=SpecializationArea.ARCHITECTURE_DESIGN,
                proficiency_score=0.87,
                confidence_level=0.85,
                use_cases=[
                    "Diseño de arquitecturas escalables",
                    "Implementación de patrones de software",
                    "Planificación de microservicios",
                    "Diseño de APIs consistentes"
                ],
                optimal_conditions=[
                    "Proyectos empresariales grandes",
                    "Sistemas que requieren alta disponibilidad",
                    "Arquitecturas distribuidas complejas"
                ]
            )
        ]
        
        claude_config = AgentConfiguration(
            temperature=0.25,
            max_tokens=6000,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.1,
            system_prompt_focus="ingeniería_software_estructurada",
            context_window_usage=0.85
        )
        
        self.claude_spec = AgentSpecialization(
            agent_type=AgentType.CLAUDE,
            primary_strengths=claude_strengths[:2],
            secondary_strengths=claude_strengths[2:],
            optimal_configuration=claude_config,
            preferred_use_cases=[
                UseCaseCategory.DETAILED_IMPLEMENTATION,
                UseCaseCategory.COMPLEX_ANALYSIS
            ],
            collaboration_affinity={
                AgentType.GEMINI: 0.90,  # Bueno para recibir análisis → implementar
                AgentType.OPENAI: 0.92   # Excelente para implementar → documentar
            },
            performance_metrics={
                "accuracy": 0.90,
                "depth": 0.88,
                "speed": 0.85,
                "consistency": 0.93
            }
        )
        
        # Especialización de OpenAI
        openai_strengths = [
            AgentStrength(
                area=SpecializationArea.DOCUMENTATION,
                proficiency_score=0.94,
                confidence_level=0.92,
                use_cases=[
                    "Creación de documentación clara y accesible",
                    "Generación de comentarios explicativos",
                    "Documentación de APIs con ejemplos",
                    "Guías de usuario comprensibles"
                ],
                optimal_conditions=[
                    "Proyectos que requieren documentación extensa",
                    "APIs públicas que necesitan ejemplos",
                    "Sistemas complejos que requieren explicación"
                ]
            ),
            AgentStrength(
                area=SpecializationArea.TUTORIAL_CREATION,
                proficiency_score=0.92,
                confidence_level=0.90,
                use_cases=[
                    "Creación de tutoriales paso a paso",
                    "Explicaciones adaptadas por nivel técnico",
                    "Contenido educativo interactivo",
                    "Guías de mejores prácticas"
                ],
                optimal_conditions=[
                    "Proyectos educativos o de formación",
                    "Onboarding de nuevos desarrolladores",
                    "Documentación para usuarios no técnicos"
                ]
            ),
            AgentStrength(
                area=SpecializationArea.CODE_GENERATION,
                proficiency_score=0.83,
                confidence_level=0.80,
                use_cases=[
                    "Generación de código con comentarios explicativos",
                    "Ejemplos de uso y implementación",
                    "Prototipos rápidos con documentación",
                    "Scripts utilitarios bien documentados"
                ],
                optimal_conditions=[
                    "Proyectos que priorizan legibilidad",
                    "Código destinado a ser compartido",
                    "Implementaciones que servirán como ejemplo"
                ]
            )
        ]
        
        openai_config = AgentConfiguration(
            temperature=0.5,
            max_tokens=4000,
            top_p=0.85,
            frequency_penalty=0.2,
            presence_penalty=0.3,
            system_prompt_focus="comunicación_técnica_clara",
            context_window_usage=0.75
        )
        
        self.openai_spec = AgentSpecialization(
            agent_type=AgentType.OPENAI,
            primary_strengths=openai_strengths[:2],
            secondary_strengths=openai_strengths[2:],
            optimal_configuration=openai_config,
            preferred_use_cases=[
                UseCaseCategory.CREATIVE_DOCUMENTATION,
                UseCaseCategory.EDUCATIONAL_CONTENT
            ],
            collaboration_affinity={
                AgentType.GEMINI: 0.88,  # Bueno para recibir análisis → explicar
                AgentType.CLAUDE: 0.93   # Excelente para recibir código → documentar
            },
            performance_metrics={
                "accuracy": 0.85,
                "depth": 0.78,
                "speed": 0.92,
                "consistency": 0.87
            }
        )
        
        # Registro de todas las especializaciones
        self.specializations = {
            AgentType.GEMINI: self.gemini_spec,
            AgentType.CLAUDE: self.claude_spec,
            AgentType.OPENAI: self.openai_spec
        }
    
    def _initialize_collaboration_matrix(self):
        """Inicializa la matriz de colaboración entre agentes"""
        self.collaboration_matrix = {
            (AgentType.GEMINI, AgentType.CLAUDE): {
                "synergy_score": 0.95,
                "optimal_sequence": "gemini_first",
                "handoff_strategy": "analysis_to_implementation",
                "common_use_cases": [
                    "Análisis profundo seguido de refactoring",
                    "Auditoría de seguridad seguida de correcciones",
                    "Evaluación de rendimiento seguida de optimizaciones"
                ]
            },
            (AgentType.CLAUDE, AgentType.OPENAI): {
                "synergy_score": 0.92,
                "optimal_sequence": "claude_first",
                "handoff_strategy": "implementation_to_documentation",
                "common_use_cases": [
                    "Desarrollo de features seguido de documentación",
                    "Refactoring seguido de explicación de cambios",
                    "Resolución de bugs seguida de guías preventivas"
                ]
            },
            (AgentType.GEMINI, AgentType.OPENAI): {
                "synergy_score": 0.85,
                "optimal_sequence": "gemini_first",
                "handoff_strategy": "analysis_to_explanation",
                "common_use_cases": [
                    "Análisis técnico seguido de documentación comprensible",
                    "Auditoría de código seguida de guías de mejores prácticas",
                    "Evaluación de arquitectura seguida de tutoriales"
                ]
            }
        }
    
    def get_agent_specialization(self, agent_type: AgentType) -> AgentSpecialization:
        """Obtiene la especialización completa de un agente"""
        return self.specializations.get(agent_type)
    
    def get_optimal_configuration(self, agent_type: AgentType) -> AgentConfiguration:
        """Obtiene la configuración óptima para un agente específico"""
        spec = self.get_agent_specialization(agent_type)
        return spec.optimal_configuration if spec else None
    
    def get_agent_strengths(self, agent_type: AgentType, 
                          specialization_area: Optional[SpecializationArea] = None) -> List[AgentStrength]:
        """Obtiene las fortalezas de un agente, opcionalmente filtradas por área"""
        spec = self.get_agent_specialization(agent_type)
        if not spec:
            return []
        
        all_strengths = spec.primary_strengths + spec.secondary_strengths
        
        if specialization_area:
            return [s for s in all_strengths if s.area == specialization_area]
        
        return all_strengths
    
    def get_collaboration_info(self, agent1: AgentType, agent2: AgentType) -> Dict[str, Any]:
        """Obtiene información de colaboración entre dos agentes"""
        key = (agent1, agent2)
        reverse_key = (agent2, agent1)
        
        if key in self.collaboration_matrix:
            return self.collaboration_matrix[key]
        elif reverse_key in self.collaboration_matrix:
            # Invertir la secuencia óptima
            info = self.collaboration_matrix[reverse_key].copy()
            if info["optimal_sequence"] == "gemini_first":
                info["optimal_sequence"] = "claude_first" if agent1 == AgentType.CLAUDE else "openai_first"
            elif info["optimal_sequence"] == "claude_first":
                info["optimal_sequence"] = "gemini_first" if agent1 == AgentType.GEMINI else "openai_first"
            return info
        
        return None
    
    def rank_agents_for_task(self, specialization_area: SpecializationArea, 
                           task_complexity: float = 0.5) -> List[Tuple[AgentType, float]]:
        """
        Rankea agentes por su idoneidad para un área de especialización específica
        
        Args:
            specialization_area: Área de especialización requerida
            task_complexity: Complejidad de la tarea (0.0 - 1.0)
            
        Returns:
            Lista de tuplas (agente, score) ordenadas por score descendente
        """
        agent_scores = []
        
        for agent_type, spec in self.specializations.items():
            base_score = 0.0
            
            # Buscar fortalezas en el área especificada
            for strength in spec.primary_strengths + spec.secondary_strengths:
                if strength.area == specialization_area:
                    # Score base de la fortaleza
                    strength_score = strength.proficiency_score * strength.confidence_level
                    
                    # Ajustar por complejidad de la tarea
                    complexity_bonus = 0.0
                    if task_complexity > 0.7:  # Tareas complejas
                        if agent_type == AgentType.GEMINI:
                            complexity_bonus = 0.1  # Gemini es mejor en tareas complejas
                    elif task_complexity < 0.3:  # Tareas simples
                        if agent_type == AgentType.OPENAI:
                            complexity_bonus = 0.05  # OpenAI es eficiente en tareas simples
                    
                    base_score = max(base_score, strength_score + complexity_bonus)
            
            if base_score > 0:
                agent_scores.append((agent_type, base_score))
        
        # Ordenar por score descendente
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        return agent_scores
    
    def suggest_collaboration_strategy(self, agents: List[AgentType], 
                                     task_type: str) -> Dict[str, Any]:
        """
        Sugiere la mejor estrategia de colaboración para un conjunto de agentes
        
        Args:
            agents: Lista de agentes que participarán
            task_type: Tipo de tarea a realizar
            
        Returns:
            Diccionario con estrategia recomendada y detalles
        """
        if len(agents) == 1:
            return {
                "strategy": "single",
                "sequence": agents,
                "reasoning": f"Agente único óptimo para {task_type}"
            }
        
        if len(agents) == 2:
            agent1, agent2 = agents
            collab_info = self.get_collaboration_info(agent1, agent2)
            
            if collab_info:
                sequence = [agent1, agent2] if collab_info["optimal_sequence"].startswith(agent1.value) else [agent2, agent1]
                return {
                    "strategy": "sequential",
                    "sequence": sequence,
                    "handoff_strategy": collab_info["handoff_strategy"],
                    "synergy_score": collab_info["synergy_score"],
                    "reasoning": f"Colaboración secuencial óptima con score {collab_info['synergy_score']:.2f}"
                }
        
        # Para más de 2 agentes, usar estrategia colaborativa
        return {
            "strategy": "collaborative",
            "sequence": agents,
            "reasoning": "Múltiples agentes requieren estrategia colaborativa"
        }
    
    def get_performance_comparison(self) -> Dict[str, Dict[str, float]]:
        """Obtiene comparación de métricas de rendimiento entre agentes"""
        comparison = {}
        
        for agent_type, spec in self.specializations.items():
            comparison[agent_type.value] = spec.performance_metrics
        
        return comparison
    
    def export_specializations(self) -> Dict[str, Any]:
        """Exporta todas las especializaciones a formato JSON serializable"""
        export_data = {}
        
        for agent_type, spec in self.specializations.items():
            export_data[agent_type.value] = {
                "primary_strengths": [
                    {
                        "area": strength.area.value,
                        "proficiency_score": strength.proficiency_score,
                        "confidence_level": strength.confidence_level,
                        "use_cases": strength.use_cases,
                        "optimal_conditions": strength.optimal_conditions
                    }
                    for strength in spec.primary_strengths
                ],
                "secondary_strengths": [
                    {
                        "area": strength.area.value,
                        "proficiency_score": strength.proficiency_score,
                        "confidence_level": strength.confidence_level,
                        "use_cases": strength.use_cases,
                        "optimal_conditions": strength.optimal_conditions
                    }
                    for strength in spec.secondary_strengths
                ],
                "optimal_configuration": {
                    "temperature": spec.optimal_configuration.temperature,
                    "max_tokens": spec.optimal_configuration.max_tokens,
                    "top_p": spec.optimal_configuration.top_p,
                    "frequency_penalty": spec.optimal_configuration.frequency_penalty,
                    "presence_penalty": spec.optimal_configuration.presence_penalty,
                    "system_prompt_focus": spec.optimal_configuration.system_prompt_focus,
                    "context_window_usage": spec.optimal_configuration.context_window_usage
                },
                "preferred_use_cases": [case.value for case in spec.preferred_use_cases],
                "collaboration_affinity": {k.value: v for k, v in spec.collaboration_affinity.items()},
                "performance_metrics": spec.performance_metrics
            }
        
        return export_data
