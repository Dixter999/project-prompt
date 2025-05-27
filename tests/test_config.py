#!/usr/bin/env python3
"""
Pruebas unitarias para el módulo de configuración.
"""
import os
import tempfile
import unittest
from pathlib import Path

from src.utils.config import ConfigManager, DEFAULT_CONFIG


class TestConfigManager(unittest.TestCase):
    """Pruebas para el ConfigManager."""
    
    def setUp(self):
        """Configuración para cada prueba."""
        # Usar un archivo temporal para las pruebas
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_file = os.path.join(self.temp_dir.name, "config.yaml")
        self.config_manager = ConfigManager(config_path=self.config_file)
    
    def tearDown(self):
        """Limpieza después de cada prueba."""
        self.temp_dir.cleanup()
    
    def test_default_config(self):
        """Verificar que se carga la configuración predeterminada."""
        self.assertEqual(self.config_manager.get("log_level"), DEFAULT_CONFIG["log_level"])
        self.assertEqual(self.config_manager.get("features.premium"), DEFAULT_CONFIG["features"]["premium"])
    
    def test_set_get_config(self):
        """Probar la configuración y recuperación de valores."""
        # Establecer y obtener un valor simple
        self.config_manager.set("log_level", "debug")
        self.assertEqual(self.config_manager.get("log_level"), "debug")
        
        # Establecer y obtener un valor anidado
        self.config_manager.set("features.premium", True)
        self.assertEqual(self.config_manager.get("features.premium"), True)
        
        # Valor predeterminado para clave inexistente
        self.assertEqual(self.config_manager.get("nonexistent", "default"), "default")
    
    def test_save_load_config(self):
        """Verificar que la configuración se guarda y carga correctamente."""
        # Cambiar valores
        self.config_manager.set("log_level", "error")
        self.config_manager.set("features.premium", True)
        
        # Guardar configuración
        self.config_manager.save_config()
        
        # Crear una nueva instancia para cargar desde el archivo
        new_config = ConfigManager(config_path=self.config_file)
        
        # Verificar que los valores se cargaron correctamente
        self.assertEqual(new_config.get("log_level"), "error")
        self.assertEqual(new_config.get("features.premium"), True)
    
    def test_api_key_management(self):
        """Verificar la gestión de claves API."""
        # Skip this test in CI environment - it requires keyring which is problematic in CI
        import os
        if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
            self.skipTest("Skipping test_api_key_management in CI environment")
            
        # Configurar clave API
        self.config_manager.set_api_key("openai", "sk-test-key")
        
        # Verificar que la clave se guardó correctamente
        self.assertEqual(self.config_manager.get_api_key("openai"), "sk-test-key")
        
        # Verificar que el servicio está habilitado
        self.assertTrue(self.config_manager.get("api.openai.enabled"))
        
        # Eliminar clave API
        self.config_manager.delete_api_key("openai")
        
        # Verificar que la clave se eliminó
        self.assertIsNone(self.config_manager.get_api_key("openai"))
    
    def test_premium_management(self):
        """Verificar la gestión de estado premium."""
        # Valor inicial
        self.assertFalse(self.config_manager.is_premium())
        
        # Activar premium
        self.config_manager.set_premium(True)
        self.assertTrue(self.config_manager.is_premium())
        
        # Desactivar premium
        self.config_manager.set_premium(False)
        self.assertFalse(self.config_manager.is_premium())


if __name__ == "__main__":
    unittest.main()
