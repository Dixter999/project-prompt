#!/usr/bin/env python3
"""
Módulo de validación de licencias para ProjectPrompt.
Este módulo proporciona la funcionalidad para validar claves de licencia,
verificar su autenticidad y determinar el tipo de suscripción asociado.
"""

import os
import re
import json
import time
import base64
import hashlib
import hmac
import requests
from typing import Dict, Optional, Any, NamedTuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from src.utils import logger, config_manager

# URL del servicio de verificación (simulado para desarrollo)
LICENSE_VERIFICATION_URL = "https://api.projectprompt.dev/v1/license/verify"

# Clave secreta para verificación offline (solo para desarrollo)
# En producción, usar un servicio web seguro para validación
_VERIFICATION_SECRET = "projectprompt_dev_license_validation_2023"


@dataclass
class LicenseStatus:
    """Clase para representar el estado de una licencia."""
    valid: bool = False
    expired: bool = False
    subscription_type: str = "free"
    expiration_date: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None


class LicenseValidator:
    """Clase para validar licencias de ProjectPrompt."""
    
    def __init__(self):
        """Inicializa el validador de licencias."""
        self.cache = {}
        self._last_online_check = 0
        
        # Intervalo mínimo entre verificaciones online (24 horas)
        self._online_check_interval = 24 * 60 * 60
    
    def _should_check_online(self) -> bool:
        """
        Determina si se debe realizar una verificación online.
        
        Returns:
            True si debe realizarse una verificación online, False en caso contrario
        """
        current_time = time.time()
        return (current_time - self._last_online_check) > self._online_check_interval
    
    def _verify_online(self, license_key: str) -> Optional[Dict[str, Any]]:
        """
        Verifica una licencia mediante el servicio online.
        
        Args:
            license_key: Clave de licencia a verificar
            
        Returns:
            Diccionario con la respuesta del servidor o None si hay un error
        """
        try:
            response = requests.post(
                LICENSE_VERIFICATION_URL,
                json={"license_key": license_key},
                timeout=5  # Timeout de 5 segundos
            )
            
            if response.status_code == 200:
                self._last_online_check = time.time()
                return response.json()
                
            logger.warning(f"Error al verificar licencia online. Estado: {response.status_code}")
            return None
        except Exception as e:
            logger.warning(f"No se pudo contactar al servidor de licencias: {e}")
            return None
    
    def _verify_offline(self, license_key: str) -> LicenseStatus:
        """
        Verifica una licencia de forma local (offline).
        Esta verificación es menos segura pero permite usar el software sin conexión.
        
        Args:
            license_key: Clave de licencia a verificar
            
        Returns:
            Estado de la licencia
        """
        status = LicenseStatus()
        
        # Una licencia válida tiene el formato: PREFIX-TYPE-EXPIRATION-HASH
        # Ejemplo: PP-PRO-20241231-a1b2c3d4e5f6
        
        pattern = r'^PP-(BASIC|PRO|TEAM)-(\d{8})-([a-zA-Z0-9]{12,16})$'
        match = re.match(pattern, license_key)
        
        if not match:
            logger.debug("El formato de la licencia no es válido")
            return status
            
        subscription_type = match.group(1).lower()
        expiration_date_str = match.group(2)
        verification_hash = match.group(3)
        
        try:
            # Verificar la fecha de expiración
            year = int(expiration_date_str[0:4])
            month = int(expiration_date_str[4:6])
            day = int(expiration_date_str[6:8])
            expiration_date = datetime(year, month, day)
            
            # Verificar si ha expirado
            if expiration_date < datetime.now():
                status.expired = True
                logger.debug(f"La licencia ha expirado el {expiration_date_str}")
                return status
                
            # Verificar la integridad de la clave
            data_to_verify = f"PP-{subscription_type.upper()}-{expiration_date_str}"
            expected_hash = self._generate_license_hash(data_to_verify)
            
            if verification_hash != expected_hash[:len(verification_hash)]:
                logger.debug("El hash de verificación de la licencia no coincide")
                return status
                
            # Si llegamos aquí, la licencia es válida
            status.valid = True
            status.subscription_type = subscription_type
            status.expiration_date = f"{year}-{month:02d}-{day:02d}"
            
            return status
            
        except ValueError:
            logger.debug("Formato de fecha inválido en la licencia")
            return status
    
    def _generate_license_hash(self, data: str) -> str:
        """
        Genera un hash para verificar la integridad de la licencia.
        
        Args:
            data: Datos a hashear
            
        Returns:
            Hash hexadecimal truncado
        """
        key = _VERIFICATION_SECRET.encode('utf-8')
        data_bytes = data.encode('utf-8')
        hmac_sha256 = hmac.new(key, data_bytes, hashlib.sha256)
        digest = hmac_sha256.hexdigest()
        return digest[:15]  # Truncar a 15 caracteres
    
    def validate_license(self, license_key: str) -> LicenseStatus:
        """
        Valida una clave de licencia y devuelve su estado.
        Primero intenta validarla online si es posible, luego recurre a validación offline.
        
        Args:
            license_key: Clave de licencia a validar
            
        Returns:
            Estado de la licencia
        """
        # Verificar si tenemos una respuesta en caché
        if license_key in self.cache:
            cached_status, timestamp = self.cache[license_key]
            
            # Usar la caché si tiene menos de un día
            if (time.time() - timestamp) < 86400:  # 24 horas
                return cached_status
        
        status = LicenseStatus()
        
        # Intentar verificar online si corresponde
        if self._should_check_online():
            online_result = self._verify_online(license_key)
            
            if online_result:
                # Actualizar estado con la respuesta online
                status.valid = online_result.get("valid", False)
                status.expired = online_result.get("expired", False)
                status.subscription_type = online_result.get("subscription_type", "free")
                status.expiration_date = online_result.get("expiration_date")
                status.user_name = online_result.get("user_name")
                status.user_email = online_result.get("user_email")
                
                # Actualizar caché
                self.cache[license_key] = (status, time.time())
                return status
        
        # Si no pudimos verificar online, usar verificación offline
        offline_status = self._verify_offline(license_key)
        
        # Actualizar caché
        self.cache[license_key] = (offline_status, time.time())
        
        return offline_status


# Función de conveniencia para obtener la instancia del validador
def get_license_validator() -> LicenseValidator:
    """
    Obtiene una instancia del validador de licencias.
    
    Returns:
        Instancia del validador de licencias
    """
    return LicenseValidator()
