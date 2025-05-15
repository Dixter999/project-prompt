#!/usr/bin/env python3
"""
Módulo para gestión de configuración en ProjectPrompt.
Permite cargar y guardar configuraciones desde archivos YAML,
y gestionar credenciales de APIs de forma segura.
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union
import yaml

# Try to import keyring, fall back to mock implementation if not available
try:
    import keyring
except ImportError:
    try:
        from src.utils import mock_keyring as keyring
    except ImportError:
        # If both fail, create a simple in-memory mock
        class MockKeyring:
            _storage = {}
            
            @staticmethod
            def get_password(service_name, username):
                return MockKeyring._storage.get((service_name, username))
                
            @staticmethod
            def set_password(service_name, username, password):
                MockKeyring._storage[(service_name, username)] = password
                
            @staticmethod
            def delete_password(service_name, username):
                if (service_name, username) in MockKeyring._storage:
                    del MockKeyring._storage[(service_name, username)]
                    return True
                return False
                
        keyring = MockKeyring

import logging

# Configure un logger básico para el módulo config
logger = logging.getLogger(__name__)

# Constantes
SERVICE_NAME = "project-prompt"
DEFAULT_CONFIG_DIR = os.path.expanduser("~/.config/project-prompt")
DEFAULT_CONFIG_FILE = "config.yaml"
DEFAULT_CONFIG_PATH = os.path.join(DEFAULT_CONFIG_DIR, DEFAULT_CONFIG_FILE)

# Valores por defecto de configuración
DEFAULT_CONFIG = {
    "log_level": "info",
    "api": {
        "anthropic": {
            "enabled": False,
            "key_name": "ANTHROPIC_API_KEY",
        },
        "openai": {
            "enabled": False,
            "key_name": "OPENAI_API_KEY",
        }
    },
    "features": {
        "premium": False
    }
}


class ConfigManager:
    """
    Gestor de configuración para ProjectPrompt.
    Maneja la carga, guardado y acceso a la configuración.
    """
    
    def __init__(
        self, 
        config_path: Optional[str] = None, 
        create_if_not_exists: bool = True
    ):
        """
        Inicializa el gestor de configuración.
        
        Args:
            config_path: Ruta al archivo de configuración
            create_if_not_exists: Si debe crear el archivo si no existe
        """
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.config = DEFAULT_CONFIG.copy()
        
        # Crear directorio de configuración si no existe
        config_dir = os.path.dirname(self.config_path)
        if not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir, exist_ok=True)
                logger.debug(f"Directorio de configuración creado: {config_dir}")
            except OSError as e:
                logger.error(f"Error al crear directorio de configuración: {e}")
        
        # Cargar configuración desde archivo o crear uno nuevo
        if os.path.exists(self.config_path):
            self.load_config()
        elif create_if_not_exists:
            logger.info(f"Archivo de configuración no encontrado, creando uno nuevo en {self.config_path}")
            self.save_config()
    
    def load_config(self) -> Dict:
        """
        Carga la configuración desde el archivo.
        
        Returns:
            Diccionario con la configuración
        """
        try:
            with open(self.config_path, 'r') as config_file:
                loaded_config = yaml.safe_load(config_file)
                
                # Asegurarse que las claves predeterminadas existan
                if loaded_config is None:
                    loaded_config = {}
                
                # Fusionar con la configuración predeterminada para asegurar que todas las claves existan
                self._merge_configs(self.config, loaded_config)
                logger.debug(f"Configuración cargada desde {self.config_path}")
        except Exception as e:
            logger.error(f"Error al cargar la configuración: {e}")
        
        return self.config
    
    def save_config(self) -> bool:
        """
        Guarda la configuración actual en el archivo.
        
        Returns:
            True si la operación fue exitosa, False en caso contrario
        """
        try:
            with open(self.config_path, 'w') as config_file:
                yaml.dump(self.config, config_file, default_flow_style=False)
                logger.debug(f"Configuración guardada en {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error al guardar la configuración: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de la configuración.
        
        Args:
            key: Clave a obtener, puede ser en formato 'section.key'
            default: Valor por defecto si la clave no existe
            
        Returns:
            Valor de la configuración o el valor predeterminado
        """
        if '.' in key:
            parts = key.split('.')
            current = self.config
            for part in parts:
                if part not in current:
                    return default
                current = current[part]
            return current
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Establece un valor en la configuración.
        
        Args:
            key: Clave a establecer, puede ser en formato 'section.key'
            value: Valor a establecer
        """
        if '.' in key:
            parts = key.split('.')
            current = self.config
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        else:
            self.config[key] = value
    
    def set_api_key(self, service: str, api_key: str) -> bool:
        """
        Almacena de forma segura la clave de API usando keyring.
        Si keyring no está disponible, almacena en la configuración (menos seguro).
        
        Args:
            service: Nombre del servicio (ej. 'anthropic', 'openai')
            api_key: Clave de API a almacenar
            
        Returns:
            True si la operación fue exitosa, False en caso contrario
        """
        try:
            # Intentar usar keyring
            try:
                keyring.set_password(SERVICE_NAME, service, api_key)
                logger.debug(f"Clave API para {service} almacenada en keyring")
            except Exception as ke:
                logger.warning(f"No se pudo usar keyring: {ke}. Almacenando en configuración (menos seguro).")
                # Fallback: almacenar en la configuración (menos seguro)
                key_section = f"api_keys.{service}"
                self.set(key_section, api_key)
            
            # Habilitar el servicio en la configuración
            if service == 'anthropic':
                self.set('api.anthropic.enabled', True)
            elif service == 'openai':
                self.set('api.openai.enabled', True)
            
            self.save_config()
            logger.info(f"Clave de API para {service} almacenada correctamente")
            return True
        except Exception as e:
            logger.error(f"Error al almacenar la clave de API para {service}: {e}")
            return False
    
    def get_api_key(self, service: str) -> Optional[str]:
        """
        Recupera la clave de API almacenada.
        Primero intenta desde keyring, luego desde la configuración.
        
        Args:
            service: Nombre del servicio (ej. 'anthropic', 'openai')
            
        Returns:
            La clave de API o None si no existe
        """
        api_key = None
        
        # Intentar obtener desde keyring
        try:
            api_key = keyring.get_password(SERVICE_NAME, service)
            if api_key:
                logger.debug(f"Clave API para {service} recuperada desde keyring")
                return api_key
        except Exception as e:
            logger.debug(f"No se pudo usar keyring: {e}")
        
        # Si no está en keyring, intentar desde la configuración
        key_section = f"api_keys.{service}"
        api_key = self.get(key_section)
        if api_key:
            logger.debug(f"Clave API para {service} recuperada desde configuración")
        else:
            logger.debug(f"No se encontró clave API para {service}")
            
        return api_key
    
    def delete_api_key(self, service: str) -> bool:
        """
        Elimina la clave de API almacenada tanto de keyring como de la configuración.
        
        Args:
            service: Nombre del servicio (ej. 'anthropic', 'openai')
            
        Returns:
            True si la operación fue exitosa, False en caso contrario
        """
        success = False
        
        # Intentar eliminar de keyring
        try:
            keyring.delete_password(SERVICE_NAME, service)
            success = True
            logger.debug(f"Clave API para {service} eliminada de keyring")
        except Exception as e:
            logger.debug(f"No se pudo eliminar clave de keyring: {e}")
        
        # También eliminar de la configuración por si acaso
        key_section = f"api_keys.{service}"
        if self.get(key_section):
            self.config.pop(key_section, None)
            success = True
            logger.debug(f"Clave API para {service} eliminada de configuración")
        
        # Deshabilitar el servicio en la configuración
        if service == 'anthropic':
            self.set('api.anthropic.enabled', False)
        elif service == 'openai':
            self.set('api.openai.enabled', False)
        
        self.save_config()
        
        if success:
            logger.info(f"Clave de API para {service} eliminada correctamente")
        else:
            logger.warning(f"No se encontró clave de API para {service} para eliminar")
            
        return success
            
    def is_premium(self) -> bool:
        """
        Verifica si el usuario tiene acceso a funciones premium.
        
        Returns:
            True si el usuario tiene acceso premium, False en caso contrario
        """
        return self.get('features.premium', False)
    
    def set_premium(self, value: bool) -> None:
        """
        Establece el estado de la cuenta premium.
        
        Args:
            value: True para activar premium, False para desactivar
        """
        self.set('features.premium', value)
        self.save_config()
        logger.info(f"Estado premium: {'Activado' if value else 'Desactivado'}")
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> None:
        """
        Fusiona la configuración cargada con la configuración predeterminada.
        
        Args:
            default: Configuración predeterminada
            loaded: Configuración cargada
        """
        # Crear una copia de las claves para evitar errores de "dictionary changed size during iteration"
        default_keys = list(default.keys())
        
        for key in default_keys:
            value = default[key]
            if key not in loaded:
                loaded[key] = value
            elif isinstance(value, dict) and isinstance(loaded[key], dict):
                self._merge_configs(value, loaded[key])
        
        # Actualizar la configuración con la versión fusionada
        self.config.update(loaded)


# Instancia global del gestor de configuración
config_manager = ConfigManager()

# Para uso más simple
get_config = config_manager.get
set_config = config_manager.set
save_config = config_manager.save_config
get_api_key = config_manager.get_api_key
set_api_key = config_manager.set_api_key
delete_api_key = config_manager.delete_api_key
is_premium = config_manager.is_premium
set_premium = config_manager.set_premium
