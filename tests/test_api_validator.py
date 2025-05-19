#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests para el sistema de validación de APIs.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json

from src.utils.api_validator import APIValidator, get_api_validator
from src.utils.config import Config


class TestAPIValidator(unittest.TestCase):
    """Tests para el validador de APIs."""
    
    def setUp(self):
        """Configuración para los tests."""
        # Usar una configuración de prueba
        self.test_config = Config()
        self.test_config.config = {}
        self.validator = APIValidator(config=self.test_config)
        
    def test_get_api_validator(self):
        """Verificar que se puede obtener un validador de APIs."""
        validator = get_api_validator()
        self.assertIsInstance(validator, APIValidator)
        
    def test_validate_api_not_configured(self):
        """Verificar que una API no configurada se reporta como inválida."""
        result = self.validator.validate_api("anthropic")
        self.assertFalse(result.get("valid"))
        self.assertFalse(result.get("configured"))
        
    @patch("src.integrations.anthropic.AnthropicAPI.verify_api_key")
    def test_validate_anthropic_api(self, mock_verify):
        """Verificar validación de API de Anthropic."""
        # Simular una clave configurada pero inválida
        self.test_config.set("api.anthropic.key", "invalid_key")
        mock_verify.return_value = (False, "Clave API inválida")
        
        result = self.validator.validate_api("anthropic")
        self.assertTrue(result.get("configured"))
        self.assertFalse(result.get("valid"))
        self.assertEqual(result.get("message"), "Clave API inválida")
        
        # Ahora simular una clave válida
        mock_verify.return_value = (True, "Clave API válida")
        result = self.validator.validate_api("anthropic")
        self.assertTrue(result.get("valid"))
    
    @patch("src.integrations.copilot.CopilotAPI.verify_api_token")
    def test_validate_github_api(self, mock_verify):
        """Verificar validación de API de GitHub."""
        # Simular un token configurado pero inválido
        self.test_config.set("api.github.token", "invalid_token")
        mock_verify.return_value = (False, "Token inválido")
        
        result = self.validator.validate_api("github")
        self.assertTrue(result.get("configured"))
        self.assertFalse(result.get("valid"))
        self.assertEqual(result.get("message"), "Token inválido")
        
        # Ahora simular un token válido
        mock_verify.return_value = (True, "Token válido")
        result = self.validator.validate_api("github")
        self.assertTrue(result.get("valid"))
        
    def test_validate_unsupported_api(self):
        """Verificar comportamiento con APIs no soportadas."""
        result = self.validator.validate_api("unsupported")
        self.assertFalse(result.get("valid"))
        self.assertEqual(result.get("message"), "API no soportada: unsupported")
        
    @patch.object(APIValidator, "validate_api")
    def test_validate_all_apis(self, mock_validate):
        """Verificar que se puede validar todas las APIs."""
        # Simular diferentes resultados para diferentes APIs
        def mock_validate_side_effect(api_name):
            if api_name == "anthropic":
                return {"valid": True, "message": "Válida"}
            else:
                return {"valid": False, "message": "Inválida"}
            
        mock_validate.side_effect = mock_validate_side_effect
        
        results = self.validator.validate_all_apis()
        self.assertTrue("anthropic" in results)
        self.assertTrue("github" in results)
        self.assertTrue(results["anthropic"]["valid"])
        self.assertFalse(results["github"]["valid"])
        
    @patch("src.integrations.anthropic.AnthropicAPI.set_api_key")
    def test_set_api_key(self, mock_set_key):
        """Verificar que se puede establecer una clave de API."""
        mock_set_key.return_value = True
        
        with patch.object(self.validator, "validate_api") as mock_validate:
            mock_validate.return_value = {"valid": True, "message": "Clave válida"}
            
            success, _ = self.validator.set_api_key("anthropic", "test_key")
            self.assertTrue(success)
            mock_set_key.assert_called_once_with("test_key")
            
    def test_get_status_summary(self):
        """Verificar que se obtiene un resumen de estado correcto."""
        # Establecer un estado simulado
        self.validator._api_status = {
            "anthropic": {"valid": True},
            "github": {"valid": False}
        }
        
        summary = self.validator.get_status_summary()
        self.assertTrue(summary["anthropic"])
        self.assertFalse(summary["github"])


if __name__ == "__main__":
    unittest.main()
