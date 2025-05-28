#!/usr/bin/env python3
"""
Sistema de caché para análisis de proyecto.

Este módulo implementa un sistema de caché simple para evitar
análisis duplicados durante la ejecución del dashboard y comandos
de dependencias.
"""

import os
import time
import hashlib
from typing import Dict, Any, Optional
from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger()


class AnalysisCache:
    """
    Caché para resultados de análisis de proyecto.
    
    Mantiene resultados en memoria durante la sesión para evitar
    análisis duplicados.
    """
    
    def __init__(self):
        """Inicializar el caché de análisis."""
        self._cache = {}
        self._timestamps = {}
        self._max_age = 300  # 5 minutos
    
    def _get_cache_key(self, project_path: str, analysis_type: str, 
                      config: Optional[Dict[str, Any]] = None) -> str:
        """
        Generar clave única para el caché.
        
        Args:
            project_path: Ruta del proyecto
            analysis_type: Tipo de análisis ('dependencies', 'dashboard', etc.)
            config: Configuración adicional opcional
            
        Returns:
            Clave única para el caché
        """
        # Normalizar ruta
        normalized_path = os.path.abspath(project_path)
        
        # Crear hash basado en ruta, tipo y configuración
        content = f"{normalized_path}:{analysis_type}"
        if config:
            # Ordenar configuración para generar hash consistente
            config_str = str(sorted(config.items()))
            content += f":{config_str}"
        
        return hashlib.md5(content.encode()).hexdigest()
    
    def _is_expired(self, cache_key: str) -> bool:
        """
        Verificar si una entrada del caché ha expirado.
        
        Args:
            cache_key: Clave del caché
            
        Returns:
            True si la entrada ha expirado
        """
        if cache_key not in self._timestamps:
            return True
        
        return time.time() - self._timestamps[cache_key] > self._max_age
    
    def get(self, project_path: str, analysis_type: str, 
            config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Obtener resultado del caché.
        
        Args:
            project_path: Ruta del proyecto
            analysis_type: Tipo de análisis
            config: Configuración adicional
            
        Returns:
            Resultado del caché o None si no existe o ha expirado
        """
        cache_key = self._get_cache_key(project_path, analysis_type, config)
        
        if cache_key not in self._cache or self._is_expired(cache_key):
            return None
        
        logger.debug(f"Cache hit para {analysis_type} en {os.path.basename(project_path)}")
        return self._cache[cache_key]
    
    def set(self, project_path: str, analysis_type: str, result: Dict[str, Any],
            config: Optional[Dict[str, Any]] = None) -> None:
        """
        Almacenar resultado en el caché.
        
        Args:
            project_path: Ruta del proyecto
            analysis_type: Tipo de análisis
            result: Resultado a almacenar
            config: Configuración adicional
        """
        cache_key = self._get_cache_key(project_path, analysis_type, config)
        
        self._cache[cache_key] = result
        self._timestamps[cache_key] = time.time()
        
        logger.debug(f"Cache set para {analysis_type} en {os.path.basename(project_path)}")
    
    def clear(self, project_path: Optional[str] = None) -> None:
        """
        Limpiar el caché.
        
        Args:
            project_path: Ruta específica a limpiar, o None para limpiar todo
        """
        if project_path is None:
            self._cache.clear()
            self._timestamps.clear()
            logger.debug("Cache completamente limpiado")
        else:
            # Limpiar entradas específicas del proyecto
            normalized_path = os.path.abspath(project_path)
            keys_to_remove = [
                key for key in self._cache.keys()
                if key.startswith(hashlib.md5(normalized_path.encode()).hexdigest()[:8])
            ]
            
            for key in keys_to_remove:
                self._cache.pop(key, None)
                self._timestamps.pop(key, None)
            
            logger.debug(f"Cache limpiado para {os.path.basename(project_path)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del caché.
        
        Returns:
            Estadísticas del caché
        """
        current_time = time.time()
        valid_entries = sum(
            1 for timestamp in self._timestamps.values()
            if current_time - timestamp <= self._max_age
        )
        
        return {
            'total_entries': len(self._cache),
            'valid_entries': valid_entries,
            'expired_entries': len(self._cache) - valid_entries,
            'max_age_seconds': self._max_age
        }


# Instancia global del caché (lazy initialization)
_analysis_cache = None


def get_analysis_cache() -> AnalysisCache:
    """
    Obtener la instancia global del caché de análisis.
    
    Returns:
        Instancia del caché de análisis
    """
    global _analysis_cache
    if _analysis_cache is None:
        _analysis_cache = AnalysisCache()
    return _analysis_cache


def clear_analysis_cache(project_path: Optional[str] = None) -> None:
    """
    Limpiar el caché de análisis.
    
    Args:
        project_path: Ruta específica a limpiar, o None para limpiar todo
    """
    global _analysis_cache
    if _analysis_cache is not None:
        _analysis_cache.clear(project_path)
