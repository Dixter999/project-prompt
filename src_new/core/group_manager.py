#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GroupManager para prevenir grupos vacíos.

Parte de la Fase 3: Corrección de Problemas Críticos
Resuelve: Problema 1 - Grupos con 0 archivos
"""

from typing import Dict, List, Optional
from pathlib import Path
import logging

try:
    from ..models.project import FileInfo
except ImportError:
    # Fallback for direct execution
    from models.project import FileInfo

logger = logging.getLogger(__name__)


class GroupManager:
    """Gestor de grupos que previene grupos vacíos"""
    
    def __init__(self, check_file_existence: bool = True):
        """Initialize the group manager.
        
        Args:
            check_file_existence: Whether to check if files actually exist on filesystem
        """
        self.logger = logger
        self.check_file_existence = check_file_existence
    
    def filter_empty_groups(self, groups: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Elimina grupos sin archivos o con archivos inexistentes.
        
        Args:
            groups: Diccionario de grupos con listas de archivos
            
        Returns:
            Diccionario filtrado sin grupos vacíos
        """
        filtered_groups = {}
        
        for group_name, files in groups.items():
            # Filtrar archivos que realmente existen (si está habilitado)
            if self.check_file_existence:
                existing_files = [f for f in files if self._file_exists(f)]
            else:
                # En modo test, asumir que todos los archivos existen
                existing_files = files
            
            # Solo añadir grupo si tiene archivos válidos
            if existing_files and len(existing_files) > 0:
                filtered_groups[group_name] = existing_files
                self.logger.info(f"✅ Group '{group_name}' has {len(existing_files)} valid files")
            else:
                self.logger.warning(f"⚠️  Skipping empty group: {group_name}")
        
        return filtered_groups
    
    def _file_exists(self, file_path: str) -> bool:
        """
        Verifica que el archivo existe realmente.
        
        Args:
            file_path: Ruta del archivo a verificar
            
        Returns:
            True si el archivo existe
        """
        try:
            return Path(file_path).exists()
        except Exception as e:
            self.logger.error(f"Error checking file existence for {file_path}: {e}")
            return False
    
    def create_groups(self, files: List[FileInfo]) -> Dict[str, List[str]]:
        """
        Crea grupos asegurando que no estén vacíos.
        
        Args:
            files: Lista de FileInfo para agrupar
            
        Returns:
            Diccionario de grupos válidos sin grupos vacíos
        """
        raw_groups = self._build_raw_groups(files)
        return self.filter_empty_groups(raw_groups)
    
    def _build_raw_groups(self, files: List[FileInfo]) -> Dict[str, List[str]]:
        """
        Construye grupos iniciales basado en patrones de archivos.
        
        Args:
            files: Lista de FileInfo
            
        Returns:
            Grupos iniciales (pueden estar vacíos)
        """
        groups = {
            'core_modules': [],
            'utility_modules': [],
            'test_modules': [],
            'feature_modules': [],
            'configuration': []
        }
        
        for file_info in files:
            file_path = file_info.path
            file_name = file_info.name.lower()
            
            # Lógica de agrupación
            if 'test' in file_path.lower() or file_name.startswith('test_'):
                groups['test_modules'].append(file_path)
            elif 'core' in file_path.lower() or 'main' in file_name:
                groups['core_modules'].append(file_path)
            elif 'util' in file_path.lower() or 'helper' in file_name:
                groups['utility_modules'].append(file_path)
            elif file_name in ['config.py', 'settings.py', 'config.yaml', 'config.json']:
                groups['configuration'].append(file_path)
            else:
                groups['feature_modules'].append(file_path)
        
        return groups
    
    def validate_groups(self, groups: Dict[str, List[str]]) -> bool:
        """
        Valida que no hay grupos vacíos.
        
        Args:
            groups: Diccionario de grupos a validar
            
        Returns:
            True si todos los grupos tienen archivos
            
        Raises:
            ValueError: Si se encuentra un grupo vacío
        """
        for group_name, files in groups.items():
            if not files or len(files) == 0:
                raise ValueError(f"Empty group detected: {group_name}")
        
        self.logger.info(f"✅ All {len(groups)} groups validated successfully")
        return True
    
    def get_group_statistics(self, groups: Dict[str, List[str]]) -> Dict:
        """
        Genera estadísticas de los grupos.
        
        Args:
            groups: Diccionario de grupos
            
        Returns:
            Estadísticas de agrupación
        """
        total_files = sum(len(files) for files in groups.values())
        
        stats = {
            'total_groups': len(groups),
            'total_files': total_files,
            'empty_groups': 0,
            'groups_detail': {}
        }
        
        for group_name, files in groups.items():
            file_count = len(files)
            percentage = (file_count / total_files * 100) if total_files > 0 else 0
            
            stats['groups_detail'][group_name] = {
                'file_count': file_count,
                'percentage': round(percentage, 1),
                'is_empty': file_count == 0
            }
            
            if file_count == 0:
                stats['empty_groups'] += 1
        
        return stats
