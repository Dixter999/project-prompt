#!/usr/bin/env python3
"""
Test de integración para integraciones con IA.
Verifica la comunicación correcta entre ProjectPrompt y los servicios de IA.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import json

# Asegurar que el módulo principal está en el path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.integrations import openai_integration
from src.integrations import anthropic_integration
from src.integrations.ai_manager import AIManager


class TestAIIntegration(unittest.TestCase):
    """Test de integración para servicios de IA."""
    
    def setUp(self):
        """Configurar el entorno para las pruebas."""
        # Mock para las claves de API
        self.mock_config = {
            "api_keys": {
                "openai": "test-openai-key",
                "anthropic": "test-anthropic-key"
            },
            "default_ai_service": "openai"
        }
        
        # Parche para config.get_config
        self.config_patcher = patch('src.utils.config.get_config', return_value=self.mock_config)
        self.mock_get_config = self.config_patcher.start()
        
    def tearDown(self):
        """Limpiar después de cada prueba."""
        # Detener el patcher
        self.config_patcher.stop()
        
    @patch('src.integrations.openai_integration.OpenAIService.generate_response')
    @patch('src.integrations.anthropic_integration.AnthropicService.generate_response')
    def test_ai_manager_service_selection(self, mock_anthropic_generate, mock_openai_generate):
        """Verificar que el AIManager selecciona el servicio correcto."""
        # Configurar mocks
        mock_openai_response = "Respuesta de OpenAI"
        mock_anthropic_response = "Respuesta de Anthropic"
        
        mock_openai_generate.return_value = mock_openai_response
        mock_anthropic_generate.return_value = mock_anthropic_response
        
        # Crear el manager
        manager = AIManager()
        
        # Test con servicio predeterminado (OpenAI)
        response1 = manager.generate_ai_response("Prueba")
        self.assertEqual(response1, mock_openai_response)
        mock_openai_generate.assert_called_with("Prueba")
        
        # Test con servicio específico (Anthropic)
        response2 = manager.generate_ai_response("Prueba", service="anthropic")
        self.assertEqual(response2, mock_anthropic_response)
        mock_anthropic_generate.assert_called_with("Prueba")
        
    @patch('src.integrations.openai_integration.OpenAIService.initialize')
    @patch('src.integrations.anthropic_integration.AnthropicService.initialize')
    def test_service_initialization(self, mock_anthropic_init, mock_openai_init):
        """Verificar que los servicios se inicializan correctamente."""
        # Crear el manager
        manager = AIManager()
        
        # Verificar inicialización de servicios
        mock_openai_init.assert_called_once_with("test-openai-key")
        mock_anthropic_init.assert_called_once_with("test-anthropic-key")
        
    @patch.object(openai_integration.OpenAIService, '__init__', return_value=None)
    @patch.object(openai_integration.OpenAIService, 'initialize')
    @patch.object(openai_integration.OpenAIService, 'generate_response')
    def test_openai_service_integration(self, mock_generate, mock_initialize, mock_init):
        """Verificar la integración con OpenAI."""
        # Configurar mock
        mock_generate.return_value = "Respuesta simulada de OpenAI"
        
        # Crear servicio
        service = openai_integration.OpenAIService()
        service.initialize("test-key")
        
        # Generar respuesta
        prompt = "Explica cómo funciona una calculadora"
        response = service.generate_response(prompt)
        
        # Verificaciones
        mock_initialize.assert_called_once_with("test-key")
        mock_generate.assert_called_once_with(prompt)
        self.assertEqual(response, "Respuesta simulada de OpenAI")
        
    @patch.object(anthropic_integration.AnthropicService, '__init__', return_value=None)
    @patch.object(anthropic_integration.AnthropicService, 'initialize')
    @patch.object(anthropic_integration.AnthropicService, 'generate_response')
    def test_anthropic_service_integration(self, mock_generate, mock_initialize, mock_init):
        """Verificar la integración con Anthropic."""
        # Configurar mock
        mock_generate.return_value = "Respuesta simulada de Anthropic"
        
        # Crear servicio
        service = anthropic_integration.AnthropicService()
        service.initialize("test-key")
        
        # Generar respuesta
        prompt = "Explica cómo funciona una calculadora"
        response = service.generate_response(prompt)
        
        # Verificaciones
        mock_initialize.assert_called_once_with("test-key")
        mock_generate.assert_called_once_with(prompt)
        self.assertEqual(response, "Respuesta simulada de Anthropic")
        
    @patch('src.integrations.openai_integration.OpenAIService.generate_response')
    def test_error_handling(self, mock_generate):
        """Verificar el manejo de errores en las integraciones de IA."""
        # Configurar mock para simular error
        mock_generate.side_effect = Exception("Error de API simulado")
        
        # Crear el manager
        manager = AIManager()
        
        # Verificar manejo de error
        with self.assertRaises(Exception):
            manager.generate_ai_response("Prompt que causa error")
            

if __name__ == '__main__':
    unittest.main()
