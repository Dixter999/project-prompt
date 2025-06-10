"""
Sistema Multi-Agente - FASE 1: Analizador de Patrones Lingüísticos
Componente especializado para análisis de lenguaje natural del usuario.
"""

import re
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from collections import Counter


class LinguisticIntensity(Enum):
    """Niveles de intensidad lingüística"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class LinguisticAnalysisResult:
    """Resultado del análisis lingüístico"""
    action_verbs: Dict[str, int]
    technical_objects: Dict[str, int]
    complexity_indicators: Dict[str, int]
    urgency_indicators: Dict[str, int]
    creativity_indicators: Dict[str, int]
    precision_indicators: Dict[str, int]
    explanation_indicators: Dict[str, int]
    overall_score: float
    detected_language: str
    text_complexity: LinguisticIntensity
    sentiment_indicators: Dict[str, float]


class LinguisticPatternAnalyzer:
    """
    Analizador de patrones lingüísticos para clasificación inteligente de tasks.
    Identifica intenciones, complejidad y características especiales del input del usuario.
    """
    
    def __init__(self):
        self._initialize_dictionaries()
        self._initialize_patterns()
        
    def _initialize_dictionaries(self):
        """Inicializa los diccionarios de palabras clave categorizadas"""
        
        # Verbos de acción categorizados por tipo de task
        self.action_verbs = {
            'analysis': {
                'analizar', 'examinar', 'revisar', 'auditar', 'verificar', 'evaluar',
                'inspeccionar', 'investigar', 'estudiar', 'explorar', 'identificar',
                'analyze', 'examine', 'review', 'audit', 'verify', 'evaluate',
                'inspect', 'investigate', 'study', 'explore', 'identify'
            },
            'generation': {
                'crear', 'generar', 'desarrollar', 'construir', 'implementar', 'diseñar',
                'programar', 'codificar', 'escribir', 'producir', 'fabricar',
                'create', 'generate', 'develop', 'build', 'implement', 'design',
                'program', 'code', 'write', 'produce', 'make'
            },
            'modification': {
                'modificar', 'cambiar', 'actualizar', 'editar', 'ajustar', 'alterar',
                'refactorizar', 'mejorar', 'transformar', 'adaptar', 'convertir',
                'modify', 'change', 'update', 'edit', 'adjust', 'alter',
                'refactor', 'improve', 'transform', 'adapt', 'convert'
            },
            'documentation': {
                'documentar', 'explicar', 'comentar', 'describir', 'especificar',
                'detallar', 'clarificar', 'ilustrar', 'ejemplificar',
                'document', 'explain', 'comment', 'describe', 'specify',
                'detail', 'clarify', 'illustrate', 'exemplify'
            },
            'debugging': {
                'corregir', 'arreglar', 'reparar', 'solucionar', 'debuggear',
                'resolver', 'eliminar', 'quitar', 'limpiar', 'subsanar',
                'correct', 'fix', 'repair', 'solve', 'debug',
                'resolve', 'eliminate', 'remove', 'clean', 'remedy'
            },
            'optimization': {
                'optimizar', 'acelerar', 'mejorar', 'eficientizar', 'perfeccionar',
                'agilizar', 'streamline', 'pulir', 'refinar',
                'optimize', 'accelerate', 'improve', 'enhance', 'perfect',
                'streamline', 'polish', 'refine'
            },
            'testing': {
                'probar', 'testear', 'validar', 'verificar', 'comprobar',
                'ejecutar', 'ensayar', 'simular', 'chequear',
                'test', 'validate', 'verify', 'check', 'run',
                'execute', 'simulate', 'assess'
            }
        }
        
        # Objetos técnicos y entidades de programación
        self.technical_objects = {
            'code_elements': {
                'código', 'script', 'función', 'método', 'clase', 'variable',
                'algoritmo', 'procedimiento', 'rutina', 'módulo', 'componente',
                'code', 'script', 'function', 'method', 'class', 'variable',
                'algorithm', 'procedure', 'routine', 'module', 'component'
            },
            'file_types': {
                'archivo', 'fichero', 'documento', 'proyecto', 'aplicación',
                'sistema', 'programa', 'software', 'biblioteca', 'librería',
                'file', 'document', 'project', 'application', 'system',
                'program', 'software', 'library', 'package'
            },
            'data_structures': {
                'base de datos', 'tabla', 'consulta', 'esquema', 'modelo',
                'entidad', 'relación', 'índice', 'vista', 'procedimiento',
                'database', 'table', 'query', 'schema', 'model',
                'entity', 'relationship', 'index', 'view', 'procedure'
            },
            'web_technologies': {
                'API', 'endpoint', 'servicio', 'servidor', 'cliente',
                'interfaz', 'frontend', 'backend', 'middleware', 'framework',
                'service', 'server', 'client', 'interface', 'framework'
            }
        }
        
        # Indicadores de complejidad
        self.complexity_indicators = {
            'simple': {
                'simple', 'básico', 'fácil', 'rápido', 'directo', 'sencillo',
                'pequeño', 'corto', 'mínimo', 'básico',
                'simple', 'basic', 'easy', 'quick', 'direct', 'straightforward',
                'small', 'short', 'minimal', 'basic'
            },
            'moderate': {
                'moderado', 'normal', 'estándar', 'regular', 'típico',
                'común', 'habitual', 'convencional',
                'moderate', 'normal', 'standard', 'regular', 'typical',
                'common', 'usual', 'conventional'
            },
            'complex': {
                'complejo', 'complicado', 'avanzado', 'sofisticado', 'elaborado',
                'detallado', 'extenso', 'amplio', 'profundo', 'comprehensivo',
                'complex', 'complicated', 'advanced', 'sophisticated', 'elaborate',
                'detailed', 'extensive', 'comprehensive', 'deep', 'thorough'
            },
            'very_complex': {
                'muy complejo', 'extremadamente', 'altamente', 'súper', 'ultra',
                'máximo', 'total', 'completo', 'integral', 'exhaustivo',
                'very complex', 'extremely', 'highly', 'super', 'ultra',
                'maximum', 'total', 'complete', 'integral', 'exhaustive'
            }
        }
        
        # Indicadores de urgencia y velocidad
        self.urgency_indicators = {
            'high_urgency': {
                'urgente', 'rápido', 'inmediato', 'ya', 'ahora', 'pronto',
                'cuanto antes', 'asap', 'prioritario', 'crítico',
                'urgent', 'fast', 'immediate', 'now', 'soon', 'quickly',
                'asap', 'priority', 'critical', 'rush'
            },
            'time_constraints': {
                'deadline', 'fecha límite', 'tiempo límite', 'plazo',
                'entrega', 'vencimiento', 'término', 'fin',
                'deadline', 'time limit', 'due date', 'delivery',
                'expiration', 'term', 'end'
            }
        }
        
        # Indicadores de creatividad
        self.creativity_indicators = {
            'innovation': {
                'innovador', 'creativo', 'original', 'único', 'nuevo',
                'diferente', 'alternativo', 'experimental', 'novedoso',
                'innovative', 'creative', 'original', 'unique', 'new',
                'different', 'alternative', 'experimental', 'novel'
            },
            'exploration': {
                'explorar', 'experimentar', 'probar', 'intentar', 'descubrir',
                'inventar', 'idear', 'concebir', 'imaginar',
                'explore', 'experiment', 'try', 'attempt', 'discover',
                'invent', 'devise', 'conceive', 'imagine'
            }
        }
        
        # Indicadores de precisión
        self.precision_indicators = {
            'accuracy': {
                'preciso', 'exacto', 'correcto', 'perfecto', 'sin errores',
                'detallado', 'minucioso', 'cuidadoso', 'riguroso',
                'precise', 'exact', 'correct', 'perfect', 'error-free',
                'detailed', 'meticulous', 'careful', 'rigorous'
            },
            'quality': {
                'calidad', 'profesional', 'producción', 'estable', 'robusto',
                'confiable', 'seguro', 'validado', 'probado',
                'quality', 'professional', 'production', 'stable', 'robust',
                'reliable', 'secure', 'validated', 'tested'
            }
        }
        
        # Indicadores de necesidad de explicación
        self.explanation_indicators = {
            'learning': {
                'aprender', 'entender', 'comprender', 'explicar', 'enseñar',
                'tutorial', 'guía', 'paso a paso', 'detallado',
                'learn', 'understand', 'comprehend', 'explain', 'teach',
                'tutorial', 'guide', 'step by step', 'detailed'
            },
            'documentation': {
                'documentar', 'comentar', 'describir', 'especificar',
                'manual', 'instrucciones', 'ejemplos', 'demos',
                'document', 'comment', 'describe', 'specify',
                'manual', 'instructions', 'examples', 'demos'
            }
        }
    
    def _initialize_patterns(self):
        """Inicializa patrones regex para análisis avanzado"""
        self.patterns = {
            'question_words': re.compile(r'\b(qué|cómo|por qué|cuándo|dónde|cuál|what|how|why|when|where|which)\b', re.IGNORECASE),
            'negative_words': re.compile(r'\b(no|never|nothing|none|neither|without|lack|missing|broken|error|problem|issue|bug|fail|wrong)\b', re.IGNORECASE),
            'positive_words': re.compile(r'\b(yes|good|great|excellent|perfect|amazing|awesome|love|like|best|better|improve|enhance|optimize)\b', re.IGNORECASE),
            'technical_syntax': re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*\([^)]*\)|[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*|\b[A-Z][a-zA-Z0-9]*[A-Z][a-zA-Z0-9]*\b'),
            'file_extensions': re.compile(r'\.[a-zA-Z0-9]{1,10}\b'),
            'numbers': re.compile(r'\b\d+\b'),
            'code_snippets': re.compile(r'```[\s\S]*?```|`[^`]+`'),
            'urls': re.compile(r'https?://[^\s]+'),
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        }
    
    def analyze_text(self, text: str, additional_context: Optional[Dict] = None) -> LinguisticAnalysisResult:
        """
        Realiza análisis completo de patrones lingüísticos en el texto.
        
        Args:
            text: Texto del usuario a analizar
            additional_context: Contexto adicional (archivos, proyecto, etc.)
            
        Returns:
            LinguisticAnalysisResult con todos los indicadores detectados
        """
        if not text or not text.strip():
            return self._empty_result()
            
        text_lower = text.lower()
        
        # Análisis de verbos de acción
        action_verbs = self._analyze_action_verbs(text_lower)
        
        # Análisis de objetos técnicos
        technical_objects = self._analyze_technical_objects(text_lower)
        
        # Análisis de indicadores de complejidad
        complexity_indicators = self._analyze_complexity_indicators(text_lower)
        
        # Análisis de indicadores especiales
        urgency_indicators = self._analyze_urgency_indicators(text_lower)
        creativity_indicators = self._analyze_creativity_indicators(text_lower)
        precision_indicators = self._analyze_precision_indicators(text_lower)
        explanation_indicators = self._analyze_explanation_indicators(text_lower)
        
        # Análisis de sentimiento
        sentiment_indicators = self._analyze_sentiment(text_lower)
        
        # Detección de idioma
        detected_language = self._detect_language(text_lower)
        
        # Análisis de complejidad textual
        text_complexity = self._analyze_text_complexity(text)
        
        # Cálculo de score general
        overall_score = self._calculate_overall_score(
            action_verbs, technical_objects, complexity_indicators,
            urgency_indicators, creativity_indicators, precision_indicators
        )
        
        return LinguisticAnalysisResult(
            action_verbs=action_verbs,
            technical_objects=technical_objects,
            complexity_indicators=complexity_indicators,
            urgency_indicators=urgency_indicators,
            creativity_indicators=creativity_indicators,
            precision_indicators=precision_indicators,
            explanation_indicators=explanation_indicators,
            overall_score=overall_score,
            detected_language=detected_language,
            text_complexity=text_complexity,
            sentiment_indicators=sentiment_indicators
        )
    
    def _analyze_action_verbs(self, text: str) -> Dict[str, int]:
        """Analiza verbos de acción en el texto"""
        results = {}
        
        for category, verbs in self.action_verbs.items():
            count = 0
            for verb in verbs:
                # Búsqueda con flexibilidad para formas verbales
                pattern = rf'\b{re.escape(verb)}\w*\b'
                matches = re.findall(pattern, text, re.IGNORECASE)
                count += len(matches)
            results[category] = count
            
        return results
    
    def _analyze_technical_objects(self, text: str) -> Dict[str, int]:
        """Analiza objetos técnicos mencionados"""
        results = {}
        
        for category, objects in self.technical_objects.items():
            count = 0
            for obj in objects:
                pattern = rf'\b{re.escape(obj)}\w*\b'
                matches = re.findall(pattern, text, re.IGNORECASE)
                count += len(matches)
            results[category] = count
            
        return results
    
    def _analyze_complexity_indicators(self, text: str) -> Dict[str, int]:
        """Analiza indicadores de complejidad"""
        results = {}
        
        for level, indicators in self.complexity_indicators.items():
            count = 0
            for indicator in indicators:
                pattern = rf'\b{re.escape(indicator)}\w*\b'
                matches = re.findall(pattern, text, re.IGNORECASE)
                count += len(matches)
            results[level] = count
            
        return results
    
    def _analyze_urgency_indicators(self, text: str) -> Dict[str, int]:
        """Analiza indicadores de urgencia"""
        results = {}
        
        for category, indicators in self.urgency_indicators.items():
            count = 0
            for indicator in indicators:
                pattern = rf'\b{re.escape(indicator)}\w*\b'
                matches = re.findall(pattern, text, re.IGNORECASE)
                count += len(matches)
            results[category] = count
            
        return results
    
    def _analyze_creativity_indicators(self, text: str) -> Dict[str, int]:
        """Analiza indicadores de creatividad"""
        results = {}
        
        for category, indicators in self.creativity_indicators.items():
            count = 0
            for indicator in indicators:
                pattern = rf'\b{re.escape(indicator)}\w*\b'
                matches = re.findall(pattern, text, re.IGNORECASE)
                count += len(matches)
            results[category] = count
            
        return results
    
    def _analyze_precision_indicators(self, text: str) -> Dict[str, int]:
        """Analiza indicadores de precisión"""
        results = {}
        
        for category, indicators in self.precision_indicators.items():
            count = 0
            for indicator in indicators:
                pattern = rf'\b{re.escape(indicator)}\w*\b'
                matches = re.findall(pattern, text, re.IGNORECASE)
                count += len(matches)
            results[category] = count
            
        return results
    
    def _analyze_explanation_indicators(self, text: str) -> Dict[str, int]:
        """Analiza indicadores de necesidad de explicación"""
        results = {}
        
        for category, indicators in self.explanation_indicators.items():
            count = 0
            for indicator in indicators:
                pattern = rf'\b{re.escape(indicator)}\w*\b'
                matches = re.findall(pattern, text, re.IGNORECASE)
                count += len(matches)
            results[category] = count
            
        return results
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analiza sentimiento básico del texto"""
        positive_matches = len(self.patterns['positive_words'].findall(text))
        negative_matches = len(self.patterns['negative_words'].findall(text))
        question_matches = len(self.patterns['question_words'].findall(text))
        
        total_words = len(text.split())
        
        return {
            'positive': positive_matches / max(total_words, 1),
            'negative': negative_matches / max(total_words, 1),
            'questioning': question_matches / max(total_words, 1)
        }
    
    def _detect_language(self, text: str) -> str:
        """Detecta el idioma principal del texto (básico)"""
        spanish_indicators = ['el', 'la', 'de', 'que', 'y', 'es', 'en', 'un', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'está', 'todo', 'pero', 'más', 'hacer', 'muy', 'puede', 'tiempo', 'si', 'ya']
        english_indicators = ['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their']
        
        words = text.lower().split()
        
        spanish_count = sum(1 for word in words if word in spanish_indicators)
        english_count = sum(1 for word in words if word in english_indicators)
        
        if spanish_count > english_count:
            return 'spanish'
        elif english_count > spanish_count:
            return 'english'
        else:
            return 'unknown'
    
    def _analyze_text_complexity(self, text: str) -> LinguisticIntensity:
        """Analiza la complejidad sintáctica del texto"""
        sentences = text.split('.')
        words = text.split()
        
        avg_sentence_length = len(words) / max(len(sentences), 1)
        technical_matches = len(self.patterns['technical_syntax'].findall(text))
        code_snippets = len(self.patterns['code_snippets'].findall(text))
        
        complexity_score = 0
        
        # Longitud promedio de oraciones
        if avg_sentence_length > 20:
            complexity_score += 2
        elif avg_sentence_length > 15:
            complexity_score += 1
        
        # Contenido técnico
        if technical_matches > 5:
            complexity_score += 2
        elif technical_matches > 2:
            complexity_score += 1
        
        # Snippets de código
        if code_snippets > 0:
            complexity_score += 1
        
        # Total de palabras
        if len(words) > 100:
            complexity_score += 1
        
        if complexity_score >= 5:
            return LinguisticIntensity.VERY_HIGH
        elif complexity_score >= 3:
            return LinguisticIntensity.HIGH
        elif complexity_score >= 1:
            return LinguisticIntensity.MEDIUM
        else:
            return LinguisticIntensity.LOW
    
    def _calculate_overall_score(self, action_verbs: Dict, technical_objects: Dict, 
                               complexity_indicators: Dict, urgency_indicators: Dict,
                               creativity_indicators: Dict, precision_indicators: Dict) -> float:
        """Calcula score general del análisis lingüístico"""
        
        # Pesos para cada categoría
        weights = {
            'action_verbs': 0.25,
            'technical_objects': 0.20,
            'complexity_indicators': 0.15,
            'urgency_indicators': 0.15,
            'creativity_indicators': 0.15,
            'precision_indicators': 0.10
        }
        
        # Normalización de scores
        action_score = min(sum(action_verbs.values()) / 10.0, 1.0)
        technical_score = min(sum(technical_objects.values()) / 15.0, 1.0)
        complexity_score = min(sum(complexity_indicators.values()) / 8.0, 1.0)
        urgency_score = min(sum(urgency_indicators.values()) / 5.0, 1.0)
        creativity_score = min(sum(creativity_indicators.values()) / 5.0, 1.0)
        precision_score = min(sum(precision_indicators.values()) / 5.0, 1.0)
        
        overall_score = (
            action_score * weights['action_verbs'] +
            technical_score * weights['technical_objects'] +
            complexity_score * weights['complexity_indicators'] +
            urgency_score * weights['urgency_indicators'] +
            creativity_score * weights['creativity_indicators'] +
            precision_score * weights['precision_indicators']
        )
        
        return min(overall_score, 1.0)
    
    def _empty_result(self) -> LinguisticAnalysisResult:
        """Retorna resultado vacío para textos inválidos"""
        return LinguisticAnalysisResult(
            action_verbs={},
            technical_objects={},
            complexity_indicators={},
            urgency_indicators={},
            creativity_indicators={},
            precision_indicators={},
            explanation_indicators={},
            overall_score=0.0,
            detected_language='unknown',
            text_complexity=LinguisticIntensity.LOW,
            sentiment_indicators={'positive': 0.0, 'negative': 0.0, 'questioning': 0.0}
        )
    
    def get_dominant_characteristics(self, result: LinguisticAnalysisResult, 
                                   threshold: float = 0.3) -> List[str]:
        """
        Extrae las características dominantes del análisis lingüístico.
        
        Args:
            result: Resultado del análisis lingüístico
            threshold: Umbral mínimo para considerar una característica como dominante
            
        Returns:
            Lista de características dominantes detectadas
        """
        characteristics = []
        
        # Verificar urgencia
        total_urgency = sum(result.urgency_indicators.values())
        if total_urgency >= 2:
            characteristics.append('urgent')
        
        # Verificar creatividad
        total_creativity = sum(result.creativity_indicators.values())
        if total_creativity >= 2:
            characteristics.append('creative')
        
        # Verificar precisión
        total_precision = sum(result.precision_indicators.values())
        if total_precision >= 2:
            characteristics.append('precision_required')
        
        # Verificar necesidad de explicación
        total_explanation = sum(result.explanation_indicators.values())
        if total_explanation >= 2:
            characteristics.append('explanation_needed')
        
        # Verificar complejidad alta
        if result.text_complexity in [LinguisticIntensity.HIGH, LinguisticIntensity.VERY_HIGH]:
            characteristics.append('high_complexity')
        
        return characteristics
