#!/usr/bin/env python3
"""
Módulo de gestión de suscripciones para ProjectPrompt.
Este módulo provee las funciones necesarias para manejar las suscripciones de usuario, 
incluyendo la verificación, activación y limitaciones según el tipo de suscripción.
"""

import os
import time
import json
import uuid
from typing import Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
import hashlib
import requests

from src.utils import config_manager, logger
from src.utils.license_validator import LicenseValidator, LicenseStatus

# Constantes
SUBSCRIPTION_FREE = "free"
SUBSCRIPTION_BASIC = "basic"
SUBSCRIPTION_PRO = "pro"
SUBSCRIPTION_TEAM = "team"

# Límites de uso por tipo de suscripción
SUBSCRIPTION_LIMITS = {
    SUBSCRIPTION_FREE: {
        "daily_prompts": 10,
        "features": ["basic_analysis", "documentation"],
        "api_calls_per_day": 50,
    },
    SUBSCRIPTION_BASIC: {
        "daily_prompts": 50,
        "features": ["basic_analysis", "documentation", "implementation_prompts"],
        "api_calls_per_day": 200,
    },
    SUBSCRIPTION_PRO: {
        "daily_prompts": 200,
        "features": ["basic_analysis", "documentation", "implementation_prompts", "test_generation", "completeness_verification"],
        "api_calls_per_day": 500,
    },
    SUBSCRIPTION_TEAM: {
        "daily_prompts": -1,  # Ilimitado
        "features": ["basic_analysis", "documentation", "implementation_prompts", "test_generation", "completeness_verification", "project_dashboard"],
        "api_calls_per_day": -1,  # Ilimitado
    }
}


class SubscriptionManager:
    """Gestor de suscripciones para usuarios de ProjectPrompt."""
    
    _instance = None
    
    def __new__(cls):
        """Implementación como Singleton para asegurar una sola instancia."""
        if cls._instance is None:
            cls._instance = super(SubscriptionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializar el gestor de suscripciones."""
        if self._initialized:
            return
            
        self.license_validator = LicenseValidator()
        self._initialized = True
        self._subscription_type = SUBSCRIPTION_FREE
        self._usage_data = {
            "last_reset": datetime.now().strftime("%Y-%m-%d"),
            "prompt_count": 0,
            "api_calls": 0,
        }
        
        # Cargar datos de uso y tipo de suscripción
        self._load_subscription_data()
    
    def _load_subscription_data(self) -> None:
        """
        Carga los datos de suscripción desde la configuración.
        Si hay una licencia válida, verifica y actualiza el tipo de suscripción.
        """
        # Obtener datos de uso
        usage_data = config_manager.get("subscription.usage", {})
        if usage_data:
            self._usage_data = usage_data
        
        # Verificar si necesitamos resetear los contadores diarios
        today = datetime.now().strftime("%Y-%m-%d")
        if self._usage_data.get("last_reset") != today:
            self._usage_data["last_reset"] = today
            self._usage_data["prompt_count"] = 0
            self._usage_data["api_calls"] = 0
            config_manager.set("subscription.usage", self._usage_data)
            config_manager.save_config()
        
        # Verificar estado de suscripción
        license_key = config_manager.get("subscription.license_key")
        if license_key:
            status = self.license_validator.validate_license(license_key)
            if status.valid:
                self._subscription_type = status.subscription_type
            else:
                # Si la licencia no es válida, revertir a suscripción gratuita
                self._subscription_type = SUBSCRIPTION_FREE
                if status.expired:
                    logger.warning("Tu licencia ha expirado. Se ha revertido a la versión gratuita.")
                    # Limpiar la licencia expirada
                    config_manager.set("subscription.license_key", None)
                    config_manager.save_config()
        else:
            self._subscription_type = SUBSCRIPTION_FREE
        
        # Actualizar estado de premium en el gestor de configuración
        config_manager.set_premium(self._subscription_type != SUBSCRIPTION_FREE)
    
    def get_limits(self) -> Dict[str, Any]:
        """
        Obtiene los límites de uso para el tipo de suscripción actual.
        
        Returns:
            Diccionario con los límites de uso
        """
        return SUBSCRIPTION_LIMITS.get(self._subscription_type, SUBSCRIPTION_LIMITS[SUBSCRIPTION_FREE])

    def get_subscription_type(self) -> str:
        """
        Obtiene el tipo de suscripción actual del usuario.
        
        Returns:
            Tipo de suscripción ('free', 'basic', 'pro', 'team')
        """
        return self._subscription_type
    
    def is_premium(self) -> bool:
        """
        Verifica si el usuario tiene una suscripción premium.
        
        Returns:
            True si la suscripción no es gratuita, False en caso contrario
        """
        # Enable premium features for all users by default
        return True
    
    def is_premium_feature_available(self, feature_name: str) -> bool:
        """
        Verifica si una característica premium está disponible para la suscripción actual.
        Este método es un alias de can_use_feature para mantener compatibilidad.
        
        Args:
            feature_name: Nombre de la característica premium
            
        Returns:
            True si la característica premium está disponible, False en caso contrario
        """
        # Enable all premium features for all users by default
        return True
    
    def can_use_feature(self, feature_name: str) -> bool:
        """
        Verifica si la suscripción actual permite usar una característica específica.
        
        Args:
            feature_name: Nombre de la característica a verificar
            
        Returns:
            True si la característica está disponible, False en caso contrario
        """
        # Enable all features for all users by default
        return True
    
    def register_prompt_usage(self) -> bool:
        """
        Registra el uso de un prompt y verifica si se ha alcanzado el límite diario.
        
        Returns:
            True si el prompt puede utilizarse, False si se ha alcanzado el límite
        """
        # Allow unlimited prompts for all users
        self._usage_data["prompt_count"] += 1
        config_manager.set("subscription.usage", self._usage_data)
        config_manager.save_config()
        return True
    
    def register_api_call(self) -> bool:
        """
        Registra una llamada a la API y verifica si se ha alcanzado el límite diario.
        
        Returns:
            True si la llamada puede realizarse, False si se ha alcanzado el límite
        """
        # Allow unlimited API calls for all users
        self._usage_data["api_calls"] += 1
        config_manager.set("subscription.usage", self._usage_data)
        config_manager.save_config()
        return True
    
    def activate_license(self, license_key: str) -> Tuple[bool, str]:
        """
        Activa una licencia para actualizar el tipo de suscripción.
        
        Args:
            license_key: Clave de licencia a activar
            
        Returns:
            Tupla (éxito, mensaje)
        """
        status = self.license_validator.validate_license(license_key)
        
        if not status.valid:
            return False, "Licencia inválida. Por favor verifica tu clave."
            
        if status.expired:
            return False, "Tu licencia ha expirado. Por favor renueva tu suscripción."
        
        # Actualizar configuración
        config_manager.set("subscription.license_key", license_key)
        config_manager.save_config()
        
        # Actualizar tipo de suscripción
        self._subscription_type = status.subscription_type
        
        # Actualizar estado premium
        config_manager.set_premium(True)
        
        return True, f"Licencia activada correctamente. Suscripción: {self._subscription_type.upper()}"
    
    def deactivate_license(self) -> Tuple[bool, str]:
        """
        Desactiva la licencia actual y revierte a la versión gratuita.
        
        Returns:
            Tupla (éxito, mensaje)
        """
        config_manager.set("subscription.license_key", None)
        config_manager.save_config()
        self._subscription_type = SUBSCRIPTION_FREE
        config_manager.set_premium(False)
        return True, "Licencia desactivada. Se ha revertido a la versión gratuita."
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de uso de la suscripción.
        
        Returns:
            Diccionario con estadísticas de uso
        """
        daily_prompts_limit = SUBSCRIPTION_LIMITS.get(self._subscription_type, {}).get("daily_prompts", 0)
        api_calls_limit = SUBSCRIPTION_LIMITS.get(self._subscription_type, {}).get("api_calls_per_day", 0)
        
        # Para límites ilimitados, usar un valor muy grande para mostrar
        if daily_prompts_limit == -1:
            daily_prompts_limit = "∞"
        if api_calls_limit == -1:
            api_calls_limit = "∞"
            
        return {
            "subscription_type": self._subscription_type,
            "is_premium": self.is_premium(),
            "daily_prompts_used": self._usage_data["prompt_count"],
            "daily_prompts_limit": daily_prompts_limit,
            "daily_api_calls_used": self._usage_data["api_calls"],
            "daily_api_calls_limit": api_calls_limit,
            "available_features": SUBSCRIPTION_LIMITS.get(self._subscription_type, {}).get("features", []),
            "last_reset": self._usage_data["last_reset"],
        }


# Función de conveniencia para obtener la instancia del gestor
def get_subscription_manager() -> SubscriptionManager:
    """
    Obtiene la instancia global del gestor de suscripciones.
    
    Returns:
        Instancia del gestor de suscripciones
    """
    return SubscriptionManager()
