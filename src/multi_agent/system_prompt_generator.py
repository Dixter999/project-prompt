"""
FASE 3: Generador de System Prompts Dinámicos
Sistema avanzado para generar prompts personalizados basados en contexto, tarea y agente.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import json
from datetime import datetime

from .task_classifier import TaskType, TaskAnalysisResult, SpecialCharacteristics
from .agent_specializations import AgentType, AgentConfiguration


class PromptComponent(Enum):
    """Componentes de un system prompt"""
    ROLE_DEFINITION = "role_definition"
    TASK_CONTEXT = "task_context"
    BEHAVIORAL_GUIDELINES = "behavioral_guidelines"
    OUTPUT_FORMAT = "output_format"
    QUALITY_STANDARDS = "quality_standards"
    COLLABORATION_RULES = "collaboration_rules"
    ERROR_HANDLING = "error_handling"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"


@dataclass
class PromptTemplate:
    """Template para generación de prompts"""
    component_type: PromptComponent
    base_template: str
    variables: List[str]
    agent_specific_variations: Dict[AgentType, str]
    task_specific_variations: Dict[TaskType, str]
    priority: int = 1  # 1-5, donde 5 es más importante


@dataclass
class PromptGenerationContext:
    """Contexto para generación de prompts"""
    agent_type: AgentType
    task_analysis: TaskAnalysisResult
    collaboration_mode: bool = False
    performance_requirements: Optional[Dict[str, Any]] = None
    user_preferences: Optional[Dict[str, str]] = None
    previous_context: Optional[str] = None
    execution_constraints: Optional[Dict[str, Any]] = None


class SystemPromptGenerator:
    """Generador principal de system prompts dinámicos"""
    
    def __init__(self):
        self.prompt_templates = self._initialize_templates()
        self.role_definitions = self._initialize_role_definitions()
        self.behavioral_guidelines = self._initialize_behavioral_guidelines()
        self.output_formats = self._initialize_output_formats()
        self.quality_standards = self._initialize_quality_standards()
    
    def _initialize_templates(self) -> Dict[PromptComponent, PromptTemplate]:
        """Inicializa templates base para cada componente"""
        return {
            PromptComponent.ROLE_DEFINITION: PromptTemplate(
                component_type=PromptComponent.ROLE_DEFINITION,
                base_template="You are a {role_name} specialized in {specialization_area}. {role_description}",
                variables=["role_name", "specialization_area", "role_description"],
                agent_specific_variations={},
                task_specific_variations={},
                priority=5
            ),
            PromptComponent.TASK_CONTEXT: PromptTemplate(
                component_type=PromptComponent.TASK_CONTEXT,
                base_template="Your current task is: {task_description}. Task type: {task_type}. Complexity: {complexity_level}. {special_considerations}",
                variables=["task_description", "task_type", "complexity_level", "special_considerations"],
                agent_specific_variations={},
                task_specific_variations={},
                priority=4
            ),
            PromptComponent.BEHAVIORAL_GUIDELINES: PromptTemplate(
                component_type=PromptComponent.BEHAVIORAL_GUIDELINES,
                base_template="Follow these behavioral guidelines: {guidelines}. Communication style: {communication_style}.",
                variables=["guidelines", "communication_style"],
                agent_specific_variations={},
                task_specific_variations={},
                priority=3
            ),
            PromptComponent.OUTPUT_FORMAT: PromptTemplate(
                component_type=PromptComponent.OUTPUT_FORMAT,
                base_template="Structure your response as follows: {format_specification}. Include: {required_sections}.",
                variables=["format_specification", "required_sections"],
                agent_specific_variations={},
                task_specific_variations={},
                priority=4
            ),
            PromptComponent.QUALITY_STANDARDS: PromptTemplate(
                component_type=PromptComponent.QUALITY_STANDARDS,
                base_template="Maintain these quality standards: {quality_criteria}. Accuracy requirement: {accuracy_level}.",
                variables=["quality_criteria", "accuracy_level"],
                agent_specific_variations={},
                task_specific_variations={},
                priority=3
            ),
            PromptComponent.COLLABORATION_RULES: PromptTemplate(
                component_type=PromptComponent.COLLABORATION_RULES,
                base_template="Collaboration guidelines: {collaboration_instructions}. Coordination approach: {coordination_style}.",
                variables=["collaboration_instructions", "coordination_style"],
                agent_specific_variations={},
                task_specific_variations={},
                priority=2
            )
        }
    
    def _initialize_role_definitions(self) -> Dict[AgentType, Dict[str, str]]:
        """Inicializa definiciones de roles específicas por agente"""
        return {
            AgentType.GEMINI: {
                "role_name": "Gemini AI Assistant",
                "specialization_area": "multimodal analysis and comprehensive problem-solving",
                "role_description": "You provide sophisticated assistance leveraging multimodal capabilities, excelling at complex reasoning and detailed analysis."
            },
            AgentType.CLAUDE: {
                "role_name": "Claude AI Assistant",
                "specialization_area": "thoughtful analysis, writing, and reasoning",
                "role_description": "You excel at careful analysis, clear communication, and nuanced reasoning. Focus on being helpful, harmless, and honest."
            },
            AgentType.OPENAI: {
                "role_name": "OpenAI Assistant",
                "specialization_area": "versatile problem-solving and creative solutions",
                "role_description": "You provide reliable assistance across diverse domains, maintaining high quality and accuracy in all responses."
            }
        }
    
    def _initialize_behavioral_guidelines(self) -> Dict[AgentType, List[str]]:
        """Inicializa pautas de comportamiento específicas por agente"""
        return {
            AgentType.GEMINI: [
                "Leverage multimodal capabilities when relevant",
                "Provide comprehensive, well-reasoned responses",
                "Consider multiple perspectives and approaches",
                "Maintain accuracy and depth in analysis"
            ],
            AgentType.CLAUDE: [
                "Be helpful, harmless, and honest",
                "Provide thoughtful, nuanced responses",
                "Show reasoning process clearly",
                "Maintain respectful and professional tone"
            ],
            AgentType.OPENAI: [
                "Be helpful, accurate, and versatile",
                "Adapt communication style to context",
                "Provide practical, actionable solutions",
                "Maintain clarity and conciseness"
            ]
        }
    
    def _initialize_output_formats(self) -> Dict[TaskType, Dict[str, Any]]:
        """Inicializa formatos de salida específicos por tipo de tarea"""
        return {
            TaskType.CODE_GENERATION: {
                "format_specification": "Code blocks with language specification, explanatory comments, and usage examples",
                "required_sections": ["Code implementation", "Documentation", "Usage example", "Testing considerations"]
            },
            TaskType.CODE_ANALYSIS: {
                "format_specification": "Structured analysis with clear sections and supporting evidence",
                "required_sections": ["Executive summary", "Detailed analysis", "Key findings", "Recommendations"]
            },
            TaskType.CODE_MODIFICATION: {
                "format_specification": "Modified code with clear change documentation",
                "required_sections": ["Original code analysis", "Proposed changes", "Modified implementation", "Testing notes"]
            },
            TaskType.DOCUMENTATION: {
                "format_specification": "Comprehensive documentation with examples and clear structure",
                "required_sections": ["Overview", "Detailed documentation", "Examples", "Usage guidelines"]
            },
            TaskType.DEBUGGING: {
                "format_specification": "Debug analysis with step-by-step solution approach",
                "required_sections": ["Problem analysis", "Root cause identification", "Solution steps", "Prevention measures"]
            },
            TaskType.OPTIMIZATION: {
                "format_specification": "Performance analysis with optimization recommendations",
                "required_sections": ["Current performance analysis", "Optimization opportunities", "Implementation plan", "Expected improvements"]
            },
            TaskType.TESTING: {
                "format_specification": "Test implementation with coverage analysis",
                "required_sections": ["Test strategy", "Test implementation", "Coverage analysis", "Results validation"]
            },
            TaskType.ARCHITECTURE_REVIEW: {
                "format_specification": "Architecture analysis with design recommendations",
                "required_sections": ["Current architecture analysis", "Design patterns evaluation", "Recommendations", "Implementation roadmap"]
            }
        }
    
    def _initialize_quality_standards(self) -> Dict[str, Dict[str, Any]]:
        """Inicializa estándares de calidad por complejidad"""
        return {
            "low": {
                "accuracy_level": "Basic accuracy with essential facts correct",
                "quality_criteria": ["Factual correctness", "Clear communication", "Task completion"]
            },
            "medium": {
                "accuracy_level": "High accuracy with thorough fact-checking",
                "quality_criteria": ["Detailed accuracy", "Comprehensive coverage", "Professional presentation", "Source validation"]
            },
            "high": {
                "accuracy_level": "Expert-level precision with meticulous attention to detail",
                "quality_criteria": ["Expert-level accuracy", "Comprehensive analysis", "Professional excellence", "Innovation and creativity", "Rigorous validation"]
            }
        }
    
    def generate_system_prompt(self, context: PromptGenerationContext) -> str:
        """Genera un system prompt completo basado en el contexto"""
        prompt_sections = []
        
        # 1. Definición de rol
        role_section = self._generate_role_section(context)
        if role_section:
            prompt_sections.append(role_section)
        
        # 2. Contexto de tarea
        task_section = self._generate_task_section(context)
        if task_section:
            prompt_sections.append(task_section)
        
        # 3. Pautas de comportamiento
        behavioral_section = self._generate_behavioral_section(context)
        if behavioral_section:
            prompt_sections.append(behavioral_section)
        
        # 4. Formato de salida
        format_section = self._generate_format_section(context)
        if format_section:
            prompt_sections.append(format_section)
        
        # 5. Estándares de calidad
        quality_section = self._generate_quality_section(context)
        if quality_section:
            prompt_sections.append(quality_section)
        
        # 6. Reglas de colaboración (si aplica)
        if context.collaboration_mode:
            collab_section = self._generate_collaboration_section(context)
            if collab_section:
                prompt_sections.append(collab_section)
        
        # 7. Contexto adicional
        additional_section = self._generate_additional_context(context)
        if additional_section:
            prompt_sections.append(additional_section)
        
        return "\n\n".join(prompt_sections)
    
    def _generate_role_section(self, context: PromptGenerationContext) -> str:
        """Genera la sección de definición de rol"""
        role_info = self.role_definitions.get(context.agent_type, {})
        
        template = self.prompt_templates[PromptComponent.ROLE_DEFINITION]
        return template.base_template.format(**role_info)
    
    def _generate_task_section(self, context: PromptGenerationContext) -> str:
        """Genera la sección de contexto de tarea"""
        task_info = {
            "task_description": getattr(context.task_analysis, 'description', context.task_analysis.user_input) or "Complete the requested task",
            "task_type": context.task_analysis.primary_task_type.value,
            "complexity_level": getattr(context.task_analysis, 'complexity_score', context.task_analysis.complexity_level.value if hasattr(context.task_analysis.complexity_level, 'value') else str(context.task_analysis.complexity_level)),
            "special_considerations": self._get_special_considerations(context.task_analysis)
        }
        
        template = self.prompt_templates[PromptComponent.TASK_CONTEXT]
        return template.base_template.format(**task_info)
    
    def _generate_behavioral_section(self, context: PromptGenerationContext) -> str:
        """Genera la sección de pautas de comportamiento"""
        guidelines = self.behavioral_guidelines.get(context.agent_type, [])
        guidelines_text = "; ".join(guidelines)
        
        # Determinar estilo de comunicación basado en el agente y contexto
        communication_style = self._determine_communication_style(context)
        
        behavioral_info = {
            "guidelines": guidelines_text,
            "communication_style": communication_style
        }
        
        template = self.prompt_templates[PromptComponent.BEHAVIORAL_GUIDELINES]
        return template.base_template.format(**behavioral_info)
    
    def _generate_format_section(self, context: PromptGenerationContext) -> str:
        """Genera la sección de formato de salida"""
        format_info = self.output_formats.get(context.task_analysis.primary_task_type, {
            "format_specification": "Clear, well-structured response",
            "required_sections": ["Main content", "Summary"]
        })
        
        # Personalizar formato basado en preferencias del usuario
        if context.user_preferences and "output_format" in context.user_preferences:
            format_info["format_specification"] = context.user_preferences["output_format"]
        
        template = self.prompt_templates[PromptComponent.OUTPUT_FORMAT]
        return template.base_template.format(**format_info)
    
    def _generate_quality_section(self, context: PromptGenerationContext) -> str:
        """Genera la sección de estándares de calidad"""
        # Determinar nivel de calidad basado en complejidad
        complexity = getattr(context.task_analysis, 'complexity_score', None)
        if complexity is None and hasattr(context.task_analysis, 'complexity_level'):
            # Convert RiskLevel to a numeric score for compatibility
            complexity_mapping = {'LOW': 0.2, 'MODERATE': 0.5, 'HIGH': 0.8}
            complexity_str = str(context.task_analysis.complexity_level).split('.')[-1]  # Get enum value
            complexity = complexity_mapping.get(complexity_str, 0.5)
        if complexity >= 0.8:
            quality_level = "high"
        elif complexity >= 0.5:
            quality_level = "medium"
        else:
            quality_level = "low"
        
        quality_info = self.quality_standards[quality_level]
        quality_criteria_text = "; ".join(quality_info["quality_criteria"])
        
        quality_data = {
            "quality_criteria": quality_criteria_text,
            "accuracy_level": quality_info["accuracy_level"]
        }
        
        template = self.prompt_templates[PromptComponent.QUALITY_STANDARDS]
        return template.base_template.format(**quality_data)
    
    def _generate_collaboration_section(self, context: PromptGenerationContext) -> str:
        """Genera la sección de reglas de colaboración"""
        collaboration_instructions = [
            "Coordinate effectively with other agents",
            "Share relevant information and insights",
            "Avoid duplicate work and conflicting outputs",
            "Maintain consistency in style and approach"
        ]
        
        coordination_style = "Sequential handoff with clear deliverables"
        if context.execution_constraints and "parallel_execution" in context.execution_constraints:
            coordination_style = "Parallel execution with synchronized outputs"
        
        collab_info = {
            "collaboration_instructions": "; ".join(collaboration_instructions),
            "coordination_style": coordination_style
        }
        
        template = self.prompt_templates[PromptComponent.COLLABORATION_RULES]
        return template.base_template.format(**collab_info)
    
    def _generate_additional_context(self, context: PromptGenerationContext) -> str:
        """Genera contexto adicional específico"""
        additional_parts = []
        
        # Contexto previo
        if context.previous_context:
            additional_parts.append(f"Previous context: {context.previous_context}")
        
        # Requisitos de rendimiento
        if context.performance_requirements:
            perf_text = "; ".join([
                f"{k}: {v}" for k, v in context.performance_requirements.items()
            ])
            additional_parts.append(f"Performance requirements: {perf_text}")
        
        # Restricciones de ejecución
        if context.execution_constraints:
            constraints_text = "; ".join([
                f"{k}: {v}" for k, v in context.execution_constraints.items()
            ])
            additional_parts.append(f"Execution constraints: {constraints_text}")
        
        return "\n".join(additional_parts) if additional_parts else ""
    
    def _get_special_considerations(self, task_analysis: TaskAnalysisResult) -> str:
        """Extrae consideraciones especiales de la tarea"""
        considerations = []
        
        if task_analysis.special_characteristics:
            for characteristic in task_analysis.special_characteristics:
                if characteristic == SpecialCharacteristics.REQUIRES_PRECISION:
                    considerations.append("Requires high precision and accuracy")
                elif characteristic == SpecialCharacteristics.REQUIRES_CREATIVITY:
                    considerations.append("Emphasize creativity and original thinking")
                elif characteristic == SpecialCharacteristics.REQUIRES_SPEED:
                    considerations.append("Time-sensitive task requiring prompt completion")
                elif characteristic == SpecialCharacteristics.MULTI_FILE_ANALYSIS:
                    considerations.append("Multi-file analysis requiring careful coordination")
                elif characteristic == SpecialCharacteristics.COMPLEX_REASONING:
                    considerations.append("Complex reasoning requiring deep analysis")
                elif characteristic == SpecialCharacteristics.API_INTEGRATION:
                    considerations.append("API integration requiring technical expertise")
        
        # Check complexity level properly
        complexity_level = getattr(task_analysis, 'complexity_score', None)
        if complexity_level is None and hasattr(task_analysis, 'complexity_level'):
            if hasattr(task_analysis.complexity_level, 'value'):
                complexity_str = task_analysis.complexity_level.value.lower()
            else:
                complexity_str = str(task_analysis.complexity_level).lower()
            if complexity_str in ['high', 'critical']:
                considerations.append("High complexity requiring expert-level attention")
        elif isinstance(complexity_level, (int, float)) and complexity_level >= 0.8:
            considerations.append("High complexity requiring expert-level attention")
        
        return "; ".join(considerations) if considerations else "Standard execution requirements"
    
    def _determine_communication_style(self, context: PromptGenerationContext) -> str:
        """Determina el estilo de comunicación apropiado"""
        # Estilo base por tipo de agente
        base_styles = {
            AgentType.CLAUDE: "Thoughtful and comprehensive",
            AgentType.OPENAI: "Direct and efficient", 
            AgentType.GEMINI: "Analytical and structured"
        }
        
        base_style = base_styles.get(context.agent_type, "Professional")
        
        # Modificar basado en preferencias del usuario
        if context.user_preferences and "communication_style" in context.user_preferences:
            user_style = context.user_preferences["communication_style"]
            return f"{base_style}, adapted to be {user_style}"
        
        return base_style
    
    def generate_prompt_variations(self, context: PromptGenerationContext, 
                                 count: int = 3) -> List[str]:
        """Genera múltiples variaciones de prompts para A/B testing"""
        variations = []
        
        for i in range(count):
            # Crear contexto modificado para cada variación
            modified_context = context
            
            # Variación 1: Enfoque en eficiencia
            if i == 1:
                if not modified_context.performance_requirements:
                    modified_context.performance_requirements = {}
                modified_context.performance_requirements["emphasis"] = "efficiency"
            
            # Variación 2: Enfoque en calidad
            elif i == 2:
                if not modified_context.performance_requirements:
                    modified_context.performance_requirements = {}
                modified_context.performance_requirements["emphasis"] = "quality"
            
            prompt = self.generate_system_prompt(modified_context)
            variations.append(prompt)
        
        return variations
    
    def validate_prompt(self, prompt: str) -> Dict[str, Any]:
        """Valida la calidad y completitud de un prompt generado"""
        validation_results = {
            "is_valid": True,
            "issues": [],
            "suggestions": [],
            "score": 0.0
        }
        
        # Verificar longitud
        if len(prompt) < 100:
            validation_results["issues"].append("Prompt too short")
            validation_results["is_valid"] = False
        elif len(prompt) > 2000:
            validation_results["issues"].append("Prompt may be too long")
        
        # Verificar componentes esenciales
        essential_keywords = ["role", "task", "guidelines", "format"]
        missing_components = []
        
        for keyword in essential_keywords:
            if keyword.lower() not in prompt.lower():
                missing_components.append(keyword)
        
        if missing_components:
            validation_results["issues"].append(f"Missing components: {missing_components}")
            validation_results["is_valid"] = False
        
        # Calcular score
        score = 1.0
        score -= len(validation_results["issues"]) * 0.2
        score = max(0.0, min(1.0, score))
        validation_results["score"] = score
        
        # Generar sugerencias
        if score < 0.8:
            validation_results["suggestions"].append("Consider adding more specific behavioral guidelines")
        if len(prompt.split('.')) < 5:
            validation_results["suggestions"].append("Add more detailed instructions")
        
        return validation_results


# Instancia global del generador
system_prompt_generator = SystemPromptGenerator()
