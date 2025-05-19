#!/usr/bin/env python3
"""
Sistema de logging para ProjectPrompt.
Proporciona logs coloridos y formateo avanzado usando Rich.
"""

import logging
import os
import sys
from enum import Enum
from typing import Dict, Optional, Union

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

# Definir niveles de log personalizados más amigables
class LogLevel(str, Enum):
    """Niveles de log soportados."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# Mapeo de niveles de log personalizados a niveles de Python
LOG_LEVEL_MAP = {
    LogLevel.DEBUG: logging.DEBUG,
    LogLevel.INFO: logging.INFO,
    LogLevel.WARNING: logging.WARNING,
    LogLevel.ERROR: logging.ERROR,
    LogLevel.CRITICAL: logging.CRITICAL,
}

# Tema personalizado para los logs
CUSTOM_THEME = Theme({
    "info": "bold green",
    "warning": "bold yellow",
    "error": "bold red",
    "critical": "bold white on red",
    "debug": "bold blue",
})

# Console para salida estándar
console = Console(theme=CUSTOM_THEME)
# Console para errores
error_console = Console(stderr=True, theme=CUSTOM_THEME)


class ProjectPromptLogger:
    """
    Logger personalizado para ProjectPrompt que usa Rich para formateo.
    Proporciona logs coloridos y legibles en la terminal.
    """

    def __init__(self, name: str = "project-prompt", level: Union[LogLevel, str] = LogLevel.INFO):
        """
        Inicializa el logger.
        
        Args:
            name: Nombre del logger
            level: Nivel de log (debug, info, warning, error, critical)
        """
        # Convertir string a LogLevel si es necesario
        if isinstance(level, str):
            try:
                level = LogLevel(level.lower())
            except ValueError:
                level = LogLevel.INFO
                console.print(f"[warning]Nivel de log inválido: {level}. Usando INFO.[/warning]")
        
        self.name = name
        
        # Configurar logger de Python
        self.logger = logging.getLogger(name)
        self.logger.setLevel(LOG_LEVEL_MAP[level])
        
        # Eliminar handlers existentes
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Configurar Rich handler
        rich_handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            show_time=True,
            omit_repeated_times=False,
            show_level=True,
            show_path=False,
        )
        rich_handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(rich_handler)
        
        # Para capturar errores no manejados
        sys.excepthook = self._handle_exception

    def set_level(self, level: Union[LogLevel, str]):
        """
        Cambia el nivel de log.
        
        Args:
            level: Nuevo nivel de log
        """
        # Convertir string a LogLevel si es necesario
        if isinstance(level, str):
            try:
                level = LogLevel(level.lower())
            except ValueError:
                level = LogLevel.INFO
                self.warning(f"Nivel de log inválido: {level}. Usando INFO.")
        
        self.logger.setLevel(LOG_LEVEL_MAP[level])
        self.debug(f"Nivel de log cambiado a {level.value.upper()}")
        
    def debug(self, message: str, **kwargs):
        """Log de nivel debug."""
        self.logger.debug(message, **kwargs)
        
    def info(self, message: str, **kwargs):
        """Log de nivel info."""
        self.logger.info(message, **kwargs)
        
    def warning(self, message: str, **kwargs):
        """Log de nivel warning."""
        self.logger.warning(message, **kwargs)
        
    def error(self, message: str, **kwargs):
        """Log de nivel error."""
        self.logger.error(message, **kwargs)
        
    def critical(self, message: str, **kwargs):
        """Log de nivel critical."""
        self.logger.critical(message, **kwargs)
    
    def _handle_exception(self, exc_type, exc_value, exc_traceback):
        """Captura excepciones no manejadas y las registra."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Permitir que KeyboardInterrupt funcione normalmente
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        self.logger.error(
            "Excepción no controlada:",
            exc_info=(exc_type, exc_value, exc_traceback)
        )


# Creamos estas funciones para facilitar la creación del logger y sus operaciones

def create_logger(name="project-prompt", level=LogLevel.INFO):
    """
    Crea una instancia del logger.
    """
    return ProjectPromptLogger(name, level)

def get_logger():
    """
    Obtiene una instancia global del logger.
    """
    # Lazy initialization
    if not hasattr(get_logger, "_logger"):
        get_logger._logger = create_logger()
    return get_logger._logger
