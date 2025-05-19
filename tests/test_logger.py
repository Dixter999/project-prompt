#!/usr/bin/env python3
"""
Pruebas unitarias para el módulo de logging.
"""
import io
import logging
import sys
import unittest
from unittest.mock import patch

from src.utils.logger import ProjectPromptLogger, LogLevel


class TestLogger(unittest.TestCase):
    """Pruebas para el sistema de logging."""
    
    def setUp(self):
        """Configuración para cada prueba."""
        # Capturar la salida estándar para verificar los logs
        self.stdout_capture = io.StringIO()
        self.stderr_capture = io.StringIO()
        sys.stdout = self.stdout_capture
        sys.stderr = self.stderr_capture
        
        # Crear una instancia de logger para pruebas
        self.logger = ProjectPromptLogger(name="test-logger")
    
    def tearDown(self):
        """Limpieza después de cada prueba."""
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
    
    def test_log_levels(self):
        """Verificar los diferentes niveles de log."""
        # Establecer nivel de log en INFO
        self.logger.set_level(LogLevel.INFO)
        
        # Los mensajes DEBUG no deberían mostrarse
        self.logger.debug("Este es un mensaje DEBUG")
        self.assertNotIn("DEBUG", self.stdout_capture.getvalue())
        
        # Los mensajes INFO deberían mostrarse
        self.logger.info("Este es un mensaje INFO")
        self.assertIn("INFO", self.stdout_capture.getvalue())
        
        # Los mensajes WARNING deberían mostrarse
        self.logger.warning("Este es un mensaje WARNING")
        self.assertIn("WARNING", self.stdout_capture.getvalue())
        
        # Los mensajes ERROR deberían mostrarse
        self.logger.error("Este es un mensaje ERROR")
        self.assertIn("ERROR", self.stdout_capture.getvalue())
    
    def test_change_log_level(self):
        """Verificar el cambio de nivel de log."""
        # Establecer nivel en WARNING
        self.logger.set_level(LogLevel.WARNING)
        
        # Los mensajes INFO no deberían mostrarse
        self.logger.info("Este mensaje INFO no debería mostrarse")
        self.assertNotIn("INFO", self.stdout_capture.getvalue())
        
        # Cambiar a nivel DEBUG
        self.logger.set_level(LogLevel.DEBUG)
        
        # Ahora los mensajes DEBUG deberían mostrarse
        self.logger.debug("Este mensaje DEBUG debería mostrarse")
        self.assertIn("DEBUG", self.stdout_capture.getvalue())
    
    def test_string_log_level(self):
        """Verificar que se puede establecer el nivel con un string."""
        # Usar string para establecer nivel
        self.logger.set_level("debug")
        
        # Los mensajes DEBUG deberían mostrarse
        self.logger.debug("Este mensaje DEBUG debería mostrarse")
        self.assertIn("DEBUG", self.stdout_capture.getvalue())
        
        # Nivel inválido debería usar INFO por defecto
        self.logger.set_level("invalid_level")
        
        # Limpiar la captura para la siguiente prueba
        self.stdout_capture = io.StringIO()
        sys.stdout = self.stdout_capture
        
        # Los mensajes DEBUG no deberían mostrarse con nivel INFO
        self.logger.debug("Este mensaje DEBUG no debería mostrarse")
        self.assertNotIn("DEBUG", self.stdout_capture.getvalue())


if __name__ == "__main__":
    unittest.main()
