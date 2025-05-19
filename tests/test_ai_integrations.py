#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests para las integraciones avanzadas de Anthropic y GitHub Copilot.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import json

from src.utils.config import ConfigManager
from src.integrations.anthropic_advanced import AdvancedAnthropicClient, get_advanced_anthropic_client
from src.integrations.copilot_advanced import AdvancedCopilotClient, get_advanced_copilot_client
from src.utils.prompt_optimizer import PromptOptimizer, get_prompt_optimizer


class TestPromptOptimizer(unittest.TestCase):
    """Pruebas para el optimizador de prompts."""
    
    def setUp(self):
        """Inicializar para cada test."""
        self.config = MagicMock(spec=ConfigManager)
        
        # Simular suscripción premium
        subscription_patcher = patch('src.utils.subscription_manager.get_subscription_manager')
        self.mock_subscription = subscription_patcher.start()
        self.mock_subscription_instance = MagicMock()
        self.mock_subscription_instance.is_premium_feature_available.return_value = True
        self.mock_subscription.return_value = self.mock_subscription_instance
        
        self.addCleanup(subscription_patcher.stop)
        
        # Crear instancia para pruebas
        self.optimizer = PromptOptimizer(config=self.config)
    
    def test_basic_optimization(self):
        """Probar optimización básica de prompts."""
        prompt = "Create a function to calculate Fibonacci numbers"
        
        # Probar con diferentes proveedores
        optimized_anthropic = self.optimizer.optimize(prompt, "anthropic", "code_generation")
        optimized_copilot = self.optimizer.optimize(prompt, "copilot", "code_generation")
        
        # Verificar que el prompt se modificó
        self.assertNotEqual(prompt, optimized_anthropic)
        self.assertNotEqual(prompt, optimized_copilot)
        self.assertIn("code", optimized_anthropic.lower())
        self.assertIn("code", optimized_copilot.lower())
    
    def test_format_code_blocks(self):
        """Probar formateo de bloques de código."""
        code_prompt = "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)"
        
        optimized = self.optimizer._apply_format_code_blocks(code_prompt, {})
        
        # Verificar que se añadieron marcadores de bloque de código
        self.assertIn("```python", optimized)
        self.assertIn("```", optimized)


class TestAdvancedAnthropicClient(unittest.TestCase):
    """Pruebas para el cliente avanzado de Anthropic."""
    
    def setUp(self):
        """Inicializar para cada test."""
        self.config = MagicMock(spec=ConfigManager)
        
        # Simular cliente base
        base_client_patcher = patch('src.integrations.anthropic_advanced.get_anthropic_client')
        self.mock_base_client = base_client_patcher.start()
        self.mock_base_instance = MagicMock()
        self.mock_base_instance.is_configured = True
        self.mock_base_instance.api_key = "test_key"
        self.mock_base_client.return_value = self.mock_base_instance
        
        # Simular suscripción premium
        subscription_patcher = patch('src.integrations.anthropic_advanced.get_subscription_manager')
        self.mock_subscription = subscription_patcher.start()
        self.mock_subscription_instance = MagicMock()
        self.mock_subscription_instance.is_premium_feature_available.return_value = True
        self.mock_subscription.return_value = self.mock_subscription_instance
        
        # Simular optimizador de prompts
        optimizer_patcher = patch('src.integrations.anthropic_advanced.get_prompt_optimizer')
        self.mock_optimizer = optimizer_patcher.start()
        self.mock_optimizer_instance = MagicMock()
        self.mock_optimizer_instance.optimize.return_value = "Optimized prompt"
        self.mock_optimizer.return_value = self.mock_optimizer_instance
        
        # Simular llamadas a API
        requests_patcher = patch('src.integrations.anthropic_advanced.requests.post')
        self.mock_requests = requests_patcher.start()
        self.mock_response = MagicMock()
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = {
            "content": [{"text": "Sample response with code\n```python\ndef sample():\n    return 'test'\n```"}]
        }
        self.mock_requests.return_value = self.mock_response
        
        self.addCleanup(base_client_patcher.stop)
        self.addCleanup(subscription_patcher.stop)
        self.addCleanup(optimizer_patcher.stop)
        self.addCleanup(requests_patcher.stop)
        
        # Crear instancia para pruebas
        self.client = AdvancedAnthropicClient(config=self.config)
    
    def test_verify_premium_access(self):
        """Verificar comprobación de acceso premium."""
        # Con acceso
        self.assertTrue(self.client.verify_premium_access())
        
        # Sin subscripción premium
        self.mock_subscription_instance.is_premium_feature_available.return_value = False
        self.assertFalse(self.client.verify_premium_access())
    
    def test_generate_code(self):
        """Probar generación de código."""
        result = self.client.generate_code("Create a sorting function", "python")
        
        self.assertTrue(result["success"])
        self.assertIn("def sample", result["code"])
        self.assertEqual("python", result["language"])
    
    def test_detect_errors(self):
        """Probar detección de errores."""
        code = "def buggy_function():\n    print(undefined_var)"
        result = self.client.detect_errors(code, "python")
        
        self.assertTrue(result["success"])
        # No probamos el contenido exacto porque depende de la implementación


class TestAdvancedCopilotClient(unittest.TestCase):
    """Pruebas para el cliente avanzado de GitHub Copilot."""
    
    def setUp(self):
        """Inicializar para cada test."""
        self.config = MagicMock(spec=ConfigManager)
        
        # Simular cliente base
        base_client_patcher = patch('src.integrations.copilot_advanced.get_copilot_client')
        self.mock_base_client = base_client_patcher.start()
        self.mock_base_instance = MagicMock()
        self.mock_base_instance.is_configured = True
        self.mock_base_instance.api_token = "test_token"
        self.mock_base_instance.get_usage_info.return_value = {
            "valid": True,
            "copilot_enabled": True
        }
        self.mock_base_client.return_value = self.mock_base_instance
        
        # Simular suscripción premium
        subscription_patcher = patch('src.integrations.copilot_advanced.get_subscription_manager')
        self.mock_subscription = subscription_patcher.start()
        self.mock_subscription_instance = MagicMock()
        self.mock_subscription_instance.is_premium_feature_available.return_value = True
        self.mock_subscription.return_value = self.mock_subscription_instance
        
        # Simular optimizador de prompts
        optimizer_patcher = patch('src.integrations.copilot_advanced.get_prompt_optimizer')
        self.mock_optimizer = optimizer_patcher.start()
        self.mock_optimizer_instance = MagicMock()
        self.mock_optimizer_instance.optimize.return_value = "Optimized prompt"
        self.mock_optimizer.return_value = self.mock_optimizer_instance
        
        self.addCleanup(base_client_patcher.stop)
        self.addCleanup(subscription_patcher.stop)
        self.addCleanup(optimizer_patcher.stop)
        
        # Crear instancia para pruebas
        self.client = AdvancedCopilotClient(config=self.config)
    
    def test_verify_premium_access(self):
        """Verificar comprobación de acceso premium."""
        # Con acceso
        self.assertTrue(self.client.verify_premium_access())
        
        # Sin Copilot habilitado
        self.mock_base_instance.get_usage_info.return_value = {"copilot_enabled": False}
        self.assertFalse(self.client.verify_premium_access())
        
        # Restaurar para otros tests
        self.mock_base_instance.get_usage_info.return_value = {"copilot_enabled": True}
    
    def test_generate_code(self):
        """Probar generación de código."""
        result = self.client.generate_code("Create a sorting function", "python")
        
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["code"])
        self.assertEqual("python", result["language"])
    
    def test_suggest_refactoring(self):
        """Probar sugerencias de refactorización."""
        code = "def ugly_function():\n    x = 1\n    y = 2\n    return x + y"
        result = self.client.suggest_refactoring(code, "python")
        
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["refactored_code"])
        self.assertIsInstance(result["suggestions"], list)


if __name__ == '__main__':
    unittest.main()
