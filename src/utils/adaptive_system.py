#!/usr/bin/env python3
"""
Sistema de Comportamiento Adaptativo para ProjectPrompt

Este módulo implementa el sistema de aprendizaje y adaptación que permite
que ProjectPrompt mejore con cada interacción del usuario, personalizando
su comportamiento según patrones de uso y preferencias detectadas.
"""

import os
import json
import time
import hashlib
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from collections import Counter, defaultdict

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("adaptive_system")

class AdaptiveSystem:
    """
    Sistema de comportamiento adaptativo que aprende de las interacciones
    del usuario y mejora sus respuestas con el tiempo.
    """
    
    def __init__(self, user_data_path: Optional[str] = None):
        """
        Inicializa el sistema adaptativo.
        
        Args:
            user_data_path: Ruta al directorio donde se almacenarán los datos de usuario.
                           Si es None, se utilizará ~/.project_prompt/user_data
        """
        if user_data_path is None:
            self.user_data_path = Path.home() / ".project_prompt" / "user_data"
        else:
            self.user_data_path = Path(user_data_path)
            
        self.user_data_path.mkdir(parents=True, exist_ok=True)
        self.preferences_file = self.user_data_path / "preferences.json"
        self.history_file = self.user_data_path / "command_history.json"
        
        # Cargar datos existentes o inicializar
        self.preferences = self._load_json(self.preferences_file, {})
        self.command_history = self._load_json(self.history_file, {"commands": []})
        
        # Configuraciones
        self.max_history_size = 100  # Máximo número de comandos a guardar
        self.suggestion_threshold = 0.7  # Umbral de confianza para sugerencias (0-1)
        
        logger.info(f"Sistema adaptativo iniciado, datos en: {self.user_data_path}")

    def _load_json(self, file_path: Path, default_value: Any) -> Any:
        """Carga datos JSON de un archivo o devuelve valor por defecto si no existe."""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return default_value
        except Exception as e:
            logger.warning(f"Error al cargar {file_path}: {e}")
            return default_value
            
    def _save_json(self, file_path: Path, data: Any) -> bool:
        """Guarda datos en formato JSON de forma segura."""
        try:
            # Crear una copia de seguridad si el archivo existe
            if file_path.exists():
                backup_path = file_path.with_suffix(f".json.bak")
                file_path.rename(backup_path)
                
            # Guardar nuevos datos
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            # Eliminar backup si todo fue bien
            backup_path = file_path.with_suffix(f".json.bak")
            if backup_path.exists():
                backup_path.unlink()
                
            return True
        except Exception as e:
            logger.error(f"Error al guardar {file_path}: {e}")
            return False

    def record_command(self, command: str, context: Dict[str, Any]) -> bool:
        """
        Registra un comando ejecutado por el usuario con su contexto.
        
        Args:
            command: El comando o solicitud del usuario
            context: Información contextual (tipo de proyecto, archivos, etc.)
            
        Returns:
            bool: True si el registro fue exitoso
        """
        # Añadir timestamp
        timestamp = time.time()
        
        # Crear entrada de historial
        entry = {
            "command": command,
            "timestamp": timestamp,
            "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)),
            "context": context
        }
        
        # Añadir al historial
        self.command_history["commands"].insert(0, entry)
        
        # Limitar tamaño del historial
        if len(self.command_history["commands"]) > self.max_history_size:
            self.command_history["commands"] = self.command_history["commands"][:self.max_history_size]
        
        # Actualizar estadísticas agregadas
        self._update_command_statistics(command, context)
        
        # Guardar cambios
        return self._save_json(self.history_file, self.command_history)

    def _update_command_statistics(self, command: str, context: Dict[str, Any]) -> None:
        """
        Actualiza estadísticas agregadas basadas en el comando y contexto.
        Esta información se utiliza para aprender patrones.
        """
        # Inicializar sección de estadísticas si no existe
        if "statistics" not in self.preferences:
            self.preferences["statistics"] = {
                "command_types": {},
                "project_types": {},
                "common_tasks": {},
                "language_preferences": {}
            }
            
        stats = self.preferences["statistics"]
        
        # Detectar tipo de comando
        command_type = self._classify_command(command)
        stats["command_types"][command_type] = stats["command_types"].get(command_type, 0) + 1
        
        # Registrar tipo de proyecto
        project_type = context.get("project_type", "unknown")
        stats["project_types"][project_type] = stats["project_types"].get(project_type, 0) + 1
        
        # Registrar lenguajes involucrados
        languages = context.get("languages", {})
        for lang, percentage in languages.items():
            if percentage > 5:  # Solo registrar lenguajes con presencia significativa
                stats["language_preferences"][lang] = stats["language_preferences"].get(lang, 0) + 1
                
        # Guardar cambios
        self._save_json(self.preferences_file, self.preferences)

    def _classify_command(self, command: str) -> str:
        """
        Clasifica un comando en categorías predefinidas.
        """
        command = command.lower()
        
        # Categorías comunes de comandos
        categories = {
            "tests": ["test", "prueba", "unittest", "cobertura"],
            "cleanup": ["limpiar", "organizar", "refactorizar", "eliminar", "innecesario"],
            "feature": ["implementar", "crear", "añadir", "desarrollar", "feature"],
            "analysis": ["analizar", "revisar", "evaluar", "auditar"],
            "deployment": ["desplegar", "publicar", "distribuir", "release"]
        }
        
        # Comprobar cada categoría
        for category, keywords in categories.items():
            if any(keyword in command for keyword in keywords):
                return category
                
        return "other"

    def get_user_preferences(self) -> Dict[str, Any]:
        """
        Obtiene un diccionario con las preferencias detectadas del usuario.
        """
        # Devolver copia para evitar modificaciones accidentales
        return dict(self.preferences)
        
    def suggest_actions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Genera sugerencias proactivas basadas en el contexto actual
        y el historial de acciones del usuario.
        
        Args:
            context: Información contextual actual (tipo de proyecto, etc.)
            
        Returns:
            List[Dict]: Lista de sugerencias ordenadas por relevancia
        """
        suggestions = []
        
        # Obtener tipo de proyecto actual
        project_type = context.get("project_type", "unknown")
        primary_language = self._get_primary_language(context.get("languages", {}))
        
        # 1. Sugerencias basadas en patrones temporales
        time_based = self._get_time_based_suggestions(project_type)
        suggestions.extend(time_based)
        
        # 2. Sugerencias basadas en frecuencia de comandos
        if "statistics" in self.preferences:
            stats = self.preferences["statistics"]
            
            # Si hay un patrón claro de comandos frecuentes
            if "command_types" in stats and stats["command_types"]:
                most_common = max(stats["command_types"].items(), key=lambda x: x[1])[0]
                
                if most_common == "tests" and self._calculate_confidence("tests") > self.suggestion_threshold:
                    suggestions.append({
                        "type": "action",
                        "action": "tests",
                        "description": "Implementar tests unitarios",
                        "confidence": self._calculate_confidence("tests"),
                        "context": f"Basado en tu historial de interés en testing para {primary_language}"
                    })
                    
                elif most_common == "cleanup" and self._calculate_confidence("cleanup") > self.suggestion_threshold:
                    suggestions.append({
                        "type": "action",
                        "action": "cleanup",
                        "description": "Organizar y limpiar archivos innecesarios",
                        "confidence": self._calculate_confidence("cleanup"),
                        "context": "Basado en tu historial de organización de proyectos"
                    })
        
        # 3. Sugerencias específicas por tipo de proyecto
        project_suggestions = self._get_project_specific_suggestions(project_type, primary_language)
        suggestions.extend(project_suggestions)
        
        # Ordenar por confianza y limitar número de sugerencias
        suggestions.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        return suggestions[:3]  # Devolver solo las 3 mejores sugerencias

    def _get_primary_language(self, languages: Dict[str, float]) -> str:
        """Determina el lenguaje principal basado en porcentajes."""
        if not languages:
            return "unknown"
        return max(languages.items(), key=lambda x: x[1])[0]
        
    def _calculate_confidence(self, command_type: str) -> float:
        """
        Calcula un valor de confianza (0-1) para una sugerencia
        basado en la frecuencia histórica.
        """
        if "statistics" not in self.preferences or "command_types" not in self.preferences["statistics"]:
            return 0.0
            
        stats = self.preferences["statistics"]["command_types"]
        if not stats:
            return 0.0
            
        # Si el tipo de comando no existe en el historial
        if command_type not in stats:
            return 0.0
            
        # Calcular porcentaje de este comando sobre el total
        total_commands = sum(stats.values())
        type_frequency = stats.get(command_type, 0)
        
        base_confidence = type_frequency / total_commands if total_commands > 0 else 0
        
        # Ajustar confianza según recencia (comandos recientes tienen más peso)
        recency_bonus = self._calculate_recency_bonus(command_type)
        
        return min(base_confidence + recency_bonus, 1.0)
        
    def _calculate_recency_bonus(self, command_type: str) -> float:
        """
        Calcula un bonus de confianza basado en cuán recientemente
        se utilizó un tipo de comando.
        """
        if not self.command_history.get("commands"):
            return 0.0
            
        # Analizar los últimos 10 comandos
        recent_commands = self.command_history["commands"][:10]
        
        for i, entry in enumerate(recent_commands):
            if self._classify_command(entry["command"]) == command_type:
                # Bonus inversamente proporcional a la posición (más reciente = más bonus)
                return 0.2 * (1.0 - (i / 10))
                
        return 0.0
        
    def _get_time_based_suggestions(self, project_type: str) -> List[Dict[str, Any]]:
        """
        Genera sugerencias basadas en patrones temporales de uso.
        """
        suggestions = []
        
        # Analizar si hay patrones en secuencias de comandos
        if len(self.command_history.get("commands", [])) >= 3:
            last_three = [self._classify_command(e["command"]) for e in self.command_history["commands"][:3]]
            
            # Patrón común: después de implementación, vienen tests
            if last_three[0] == "feature" and "tests" not in last_three:
                suggestions.append({
                    "type": "action",
                    "action": "tests",
                    "description": "Implementar tests para la nueva funcionalidad",
                    "confidence": 0.85,
                    "context": "Basado en la reciente implementación de características"
                })
                
            # Patrón común: después de analysis, viene feature o cleanup
            if last_three[0] == "analysis" and "feature" not in last_three and "cleanup" not in last_three:
                suggestions.append({
                    "type": "action",
                    "action": "feature",
                    "description": "Implementar mejoras basadas en el análisis",
                    "confidence": 0.75,
                    "context": "Basado en el análisis reciente del proyecto" 
                })
                
        return suggestions
        
    def _get_project_specific_suggestions(self, project_type: str, primary_language: str) -> List[Dict[str, Any]]:
        """
        Genera sugerencias específicas según el tipo de proyecto.
        """
        suggestions = []
        
        if project_type == "api":
            suggestions.append({
                "type": "template",
                "template": "api_documentation",
                "description": "Generar documentación de API con Swagger/OpenAPI",
                "confidence": 0.8,
                "context": f"API detectada en {primary_language}"
            })
            
        elif project_type == "frontend":
            suggestions.append({
                "type": "template",
                "template": "responsive_check",
                "description": "Verificar diseño responsive",
                "confidence": 0.75,
                "context": "Aplicación frontend detectada"
            })
            
        elif project_type == "cli":
            suggestions.append({
                "type": "template",
                "template": "cli_help",
                "description": "Generar documentación de ayuda para comandos",
                "confidence": 0.8,
                "context": "Aplicación CLI detectada"
            })
            
        return suggestions
        
    def learn_from_feedback(self, suggestion_id: str, was_helpful: bool) -> None:
        """
        Aprende de la retroalimentación del usuario sobre las sugerencias.
        
        Args:
            suggestion_id: Identificador de la sugerencia evaluada
            was_helpful: Si la sugerencia fue útil para el usuario
        """
        # Inicializar sección de feedback si no existe
        if "feedback" not in self.preferences:
            self.preferences["feedback"] = {"suggestions": {}}
            
        feedback = self.preferences["feedback"]
        
        # Registrar feedback
        if suggestion_id not in feedback["suggestions"]:
            feedback["suggestions"][suggestion_id] = {"helpful": 0, "not_helpful": 0}
            
        if was_helpful:
            feedback["suggestions"][suggestion_id]["helpful"] += 1
        else:
            feedback["suggestions"][suggestion_id]["not_helpful"] += 1
            
        # Ajustar umbrales basados en feedback
        helpful_ratio = self._calculate_helpful_ratio()
        if helpful_ratio is not None:
            # Ajustar umbral de sugerencia dinámicamente
            # Si muchas sugerencias son útiles, podemos ser más liberales
            # Si pocas son útiles, debemos ser más conservadores
            self.suggestion_threshold = max(0.5, min(0.9, 1.0 - (helpful_ratio * 0.3)))
            
        # Guardar cambios
        self._save_json(self.preferences_file, self.preferences)
            
    def _calculate_helpful_ratio(self) -> Optional[float]:
        """Calcula el ratio de sugerencias útiles sobre el total."""
        if "feedback" not in self.preferences or "suggestions" not in self.preferences["feedback"]:
            return None
            
        suggestions = self.preferences["feedback"]["suggestions"]
        if not suggestions:
            return None
            
        helpful = sum(s["helpful"] for s in suggestions.values())
        total = sum(s["helpful"] + s["not_helpful"] for s in suggestions.values())
        
        return helpful / total if total > 0 else None

# Función para obtener una instancia del sistema adaptativo
def get_adaptive_system(user_data_path: Optional[str] = None) -> AdaptiveSystem:
    """
    Obtiene una instancia del sistema adaptativo.
    
    Args:
        user_data_path: Ruta opcional para los datos de usuario
        
    Returns:
        AdaptiveSystem: Instancia del sistema adaptativo
    """
    return AdaptiveSystem(user_data_path)

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del sistema adaptativo
    adaptive = get_adaptive_system()
    
    # Simular un comando con contexto
    context = {
        "project_type": "api",
        "languages": {"Python": 80, "JavaScript": 15, "HTML": 5},
        "file_count": 32
    }
    
    # Registrar comandos de ejemplo
    adaptive.record_command("Quiero implementar tests unitarios para mi API", context)
    
    # Obtener sugerencias
    suggestions = adaptive.suggest_actions(context)
    
    # Mostrar sugerencias
    print("Sugerencias generadas:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion['description']} (Confianza: {suggestion['confidence']:.2f})")
        print(f"   Contexto: {suggestion['context']}")
