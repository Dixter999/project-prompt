"""Módulo para utilidades y funciones auxiliares."""

from src.utils.logger import ProjectPromptLogger, LogLevel, get_logger, create_logger

# Inicializamos el logger
logger = get_logger()

# Funciones de conveniencia para el logging
debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error
critical = logger.critical
set_level = logger.set_level
from src.utils.config import (
    config_manager,
    get_config,
    set_config,
    save_config,
    get_api_key,
    set_api_key,
    delete_api_key,
    is_premium,
    set_premium,
)

__all__ = [
    'logger', 'debug', 'info', 'warning', 'error', 'critical', 'set_level', 'LogLevel',
    'config_manager', 'get_config', 'set_config', 'save_config',
    'get_api_key', 'set_api_key', 'delete_api_key', 'is_premium', 'set_premium',
]
