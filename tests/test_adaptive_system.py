#!/usr/bin/env python3
"""
Tests para el Sistema de Comportamiento Adaptativo en ProjectPrompt.
"""

import os
import sys
import unittest
import tempfile
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# Añadir directorio padre al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar sistema adaptativo
from src.utils.adaptive_system import AdaptiveSystem, get_adaptive_system

class TestAdaptiveSystem(unittest.TestCase):
    """Tests para AdaptiveSystem."""
    
    def setUp(self):
        """Configurar el entorno de pruebas."""
        # Crear directorio temporal para datos de prueba
        self.test_dir = tempfile.TemporaryDirectory()
        self.data_path = Path(self.test_dir.name)
        
        # Crear instancia del sistema adaptativo con datos en directorio temporal
        self.adaptive = AdaptiveSystem(self.data_path)
        
    def tearDown(self):
        """Limpiar después de cada test."""
        # Eliminar directorio temporal
        self.test_dir.cleanup()
        
    def test_initialization(self):
        """Verificar inicialización correcta del sistema."""
        # Verificar que los archivos de datos se crean
        self.assertTrue(self.data_path.exists())
        self.assertTrue(isinstance(self.adaptive.preferences, dict))
        self.assertTrue(isinstance(self.adaptive.command_history, dict))
        self.assertTrue("commands" in self.adaptive.command_history)
        
    def test_record_command(self):
        """Verificar el registro de comandos."""
        # Comando y contexto de prueba
        command = "Quiero implementar tests unitarios"
        context = {"project_type": "api", "languages": {"Python": 80}}
        
        # Registrar comando
        result = self.adaptive.record_command(command, context)
        
        # Verificar resultado
        self.assertTrue(result)
        self.assertEqual(len(self.adaptive.command_history["commands"]), 1)
        self.assertEqual(self.adaptive.command_history["commands"][0]["command"], command)
        
        # Verificar que se actualizaron las estadísticas
        self.assertIn("statistics", self.adaptive.preferences)
        self.assertIn("command_types", self.adaptive.preferences["statistics"])
        
        # Verificar que el comando se clasificó correctamente
        stats = self.adaptive.preferences["statistics"]["command_types"]
        self.assertIn("tests", stats)
        self.assertEqual(stats["tests"], 1)
        
    def test_command_classification(self):
        """Verificar clasificación de comandos."""
        # Probar diferentes tipos de comandos
        self.assertEqual(self.adaptive._classify_command("Quiero implementar tests"), "tests")
        self.assertEqual(self.adaptive._classify_command("Necesito limpiar archivos"), "cleanup")
        self.assertEqual(self.adaptive._classify_command("Implementar nueva feature"), "feature")
        self.assertEqual(self.adaptive._classify_command("Analizar código"), "analysis")
        self.assertEqual(self.adaptive._classify_command("Desplegar aplicación"), "deployment")
        self.assertEqual(self.adaptive._classify_command("Algo completamente diferente"), "other")
        
    def test_max_history_size(self):
        """Verificar que se limita el tamaño del historial."""
        # Sobreescribir tamaño máximo para la prueba
        self.adaptive.max_history_size = 3
        
        # Registrar más comandos que el límite
        for i in range(5):
            self.adaptive.record_command(f"Comando {i}", {"test": True})
            
        # Verificar que solo se mantienen los más recientes
        self.assertEqual(len(self.adaptive.command_history["commands"]), 3)
        self.assertEqual(self.adaptive.command_history["commands"][0]["command"], "Comando 4")
        
    def test_get_suggestions(self):
        """Verificar generación de sugerencias."""
        # Registrar comandos para crear historial
        self.adaptive.record_command("Implementar nueva funcionalidad", {"project_type": "api", "languages": {"Python": 80}})
        
        # Obtener sugerencias
        context = {"project_type": "api", "languages": {"Python": 80}}
        suggestions = self.adaptive.suggest_actions(context)
        
        # Verificar que se generaron sugerencias
        self.assertTrue(len(suggestions) > 0)
        # Verificar estructura de sugerencias
        for suggestion in suggestions:
            self.assertIn("description", suggestion)
            self.assertIn("confidence", suggestion)
            
    def test_project_specific_suggestions(self):
        """Verificar que se generan sugerencias específicas por tipo de proyecto."""
        # Probar sugerencias para diferentes tipos de proyectos
        api_suggestions = self.adaptive._get_project_specific_suggestions("api", "Python")
        frontend_suggestions = self.adaptive._get_project_specific_suggestions("frontend", "JavaScript")
        cli_suggestions = self.adaptive._get_project_specific_suggestions("cli", "Python")
        
        # Verificar que cada tipo genera sugerencias específicas
        self.assertTrue(len(api_suggestions) > 0)
        self.assertTrue(len(frontend_suggestions) > 0)
        self.assertTrue(len(cli_suggestions) > 0)
        
        # Verificar contenido de sugerencias
        self.assertIn("api_documentation", [s["template"] for s in api_suggestions])
        self.assertIn("responsive_check", [s["template"] for s in frontend_suggestions])
        self.assertIn("cli_help", [s["template"] for s in cli_suggestions])
        
    def test_learn_from_feedback(self):
        """Verificar aprendizaje a partir de feedback."""
        # Registrar feedback
        self.adaptive.learn_from_feedback("suggestion_1", True)  # Útil
        self.adaptive.learn_from_feedback("suggestion_2", False)  # No útil
        
        # Verificar que se guardó el feedback
        self.assertIn("feedback", self.adaptive.preferences)
        self.assertIn("suggestions", self.adaptive.preferences["feedback"])
        self.assertEqual(self.adaptive.preferences["feedback"]["suggestions"]["suggestion_1"]["helpful"], 1)
        self.assertEqual(self.adaptive.preferences["feedback"]["suggestions"]["suggestion_2"]["not_helpful"], 1)
        
    def test_helpful_ratio_calculation(self):
        """Verificar cálculo del ratio de sugerencias útiles."""
        # Registrar feedback mixto
        self.adaptive.learn_from_feedback("s1", True)  # Útil
        self.adaptive.learn_from_feedback("s2", True)  # Útil
        self.adaptive.learn_from_feedback("s3", False)  # No útil
        
        # Calcular ratio
        ratio = self.adaptive._calculate_helpful_ratio()
        
        # Verificar resultado (2 útiles de 3 total = 0.667)
        self.assertAlmostEqual(ratio, 2/3, places=2)
        
    def test_confidence_calculation(self):
        """Verificar cálculo de confianza para sugerencias."""
        # Inicializar estadísticas
        self.adaptive.preferences["statistics"] = {
            "command_types": {
                "tests": 5,
                "cleanup": 3,
                "feature": 2
            }
        }
        
        # Calcular confianza
        confidence = self.adaptive._calculate_confidence("tests")
        
        # Verificar resultado (5 de 10 total = 0.5 base)
        self.assertTrue(0.5 <= confidence <= 1.0)
        
    def test_get_adaptive_system_factory(self):
        """Verificar función factory get_adaptive_system."""
        # Obtener instancia usando factory
        system = get_adaptive_system(self.data_path)
        
        # Verificar que es la clase correcta
        self.assertIsInstance(system, AdaptiveSystem)
        self.assertEqual(system.user_data_path, self.data_path)
        
if __name__ == "__main__":
    unittest.main()
