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

# Importar configuración
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

# Importar validador de APIs
from src.utils.api_validator import APIValidator, get_api_validator

# Importar gestor de markdown
from src.utils.markdown_manager import MarkdownManager, get_markdown_manager

# Importar sistema de documentación
from src.utils.documentation_system import DocumentationSystem, get_documentation_system

# Importar gestor de estructura de proyecto
from src.utils.project_structure import ProjectStructure, get_project_structure

# Importar sistema de subscripción
from src.utils.license_validator import LicenseValidator, get_license_validator, LicenseStatus
from src.utils.subscription_manager import (
    SubscriptionManager, 
    get_subscription_manager,
    SUBSCRIPTION_FREE,
    SUBSCRIPTION_BASIC,
    SUBSCRIPTION_PRO,
    SUBSCRIPTION_TEAM,
    SUBSCRIPTION_LIMITS
)

__all__ = [
    'logger', 'debug', 'info', 'warning', 'error', 'critical', 'set_level', 'LogLevel',
    'config_manager', 'get_config', 'set_config', 'save_config',
    'get_api_key', 'set_api_key', 'delete_api_key', 'is_premium', 'set_premium',
    'MarkdownManager', 'get_markdown_manager',
    'DocumentationSystem', 'get_documentation_system',
    'APIValidator', 'get_api_validator',
    'ProjectStructure', 'get_project_structure',
    'LicenseValidator', 'get_license_validator', 'LicenseStatus',
    'SubscriptionManager', 'get_subscription_manager',
    'SUBSCRIPTION_FREE', 'SUBSCRIPTION_BASIC', 'SUBSCRIPTION_PRO', 'SUBSCRIPTION_TEAM',
    'SUBSCRIPTION_LIMITS',
]
