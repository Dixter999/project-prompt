#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de prioridad para grupos y eliminación de duplicación.

Parte de la Fase 3: Corrección de Problemas Críticos
Resuelve: Problema 3 - Mismos archivos aparecen en diferentes grupos
"""

from typing import Dict, List, Set
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class GroupPriority(Enum):
    """Prioridades para asignación de archivos a grupos"""
    CIRCULAR_DEPENDENCIES = 1    # Mayor prioridad
    CORE_MODULES = 2
    FEATURE_MODULES = 3
    UTILITY_MODULES = 4
    TEST_MODULES = 5             # Menor prioridad


class GroupPrioritySystem:
    """Sistema de prioridad para evitar archivos duplicados"""
    
    def __init__(self):
        """Initialize the group priority system."""
        self.priority_order = [
            'circular_dependencies',
            'core_modules',
            'feature_modules', 
            'utility_modules',
            'test_modules',
            'configuration'
        ]
        self.logger = logger
    
    def assign_files_to_groups(self, potential_groups: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Asigna cada archivo a exactamente un grupo basado en prioridad.
        
        Args:
            potential_groups: Diccionario con grupos potenciales que pueden tener duplicados
            
        Returns:
            Diccionario con grupos finales sin duplicados
        """
        assigned_files = set()
        final_groups = {}
        
        self.logger.info(f"Starting file assignment with {len(potential_groups)} potential groups")
        
        # Procesar grupos en orden de prioridad
        for group_type in self.priority_order:
            if group_type in potential_groups:
                # Solo archivos que no han sido asignados
                available_files = [
                    f for f in potential_groups[group_type] 
                    if f not in assigned_files
                ]
                
                if available_files:
                    final_groups[group_type] = available_files
                    assigned_files.update(available_files)
                    self.logger.info(f"✅ Assigned {len(available_files)} files to {group_type}")
                else:
                    self.logger.debug(f"No available files for {group_type}")
        
        # Reportar estadísticas
        total_original = sum(len(files) for files in potential_groups.values())
        total_final = sum(len(files) for files in final_groups.values())
        duplicates_removed = total_original - total_final
        
        if duplicates_removed > 0:
            self.logger.info(f"🎯 Removed {duplicates_removed} duplicate file assignments")
        
        return final_groups
    
    def validate_no_duplicates(self, groups: Dict[str, List[str]]) -> bool:
        """
        Valida que no hay archivos duplicados entre grupos.
        
        Args:
            groups: Diccionario de grupos a validar
            
        Returns:
            True si no hay duplicados
            
        Raises:
            ValueError: Si se encuentran duplicados
        """
        all_files = []
        for group_files in groups.values():
            all_files.extend(group_files)
        
        unique_files = set(all_files)
        
        if len(all_files) != len(unique_files):
            duplicates = [f for f in all_files if all_files.count(f) > 1]
            self.logger.error(f"❌ Duplicate files found: {duplicates}")
            raise ValueError(f"Duplicate files found: {duplicates}")
        
        self.logger.info(f"✅ No duplicates found in {len(groups)} groups with {len(all_files)} total files")
        return True
    
    def get_group_assignment_report(self, groups: Dict[str, List[str]]) -> str:
        """
        Genera reporte de asignación de grupos.
        
        Args:
            groups: Diccionario de grupos
            
        Returns:
            String con reporte detallado
        """
        report = "📊 Group Assignment Report:\n"
        report += "=" * 40 + "\n"
        
        total_files = sum(len(files) for files in groups.values())
        
        if total_files == 0:
            report += "No files assigned to any group.\n"
            return report
        
        for group_name, files in groups.items():
            percentage = (len(files) / total_files) * 100 if total_files > 0 else 0
            report += f"📁 {group_name}: {len(files)} files ({percentage:.1f}%)\n"
            
            # Mostrar algunos archivos de ejemplo
            for i, file_path in enumerate(files[:3]):
                report += f"   • {file_path}\n"
            if len(files) > 3:
                report += f"   ... and {len(files) - 3} more\n"
            report += "\n"
        
        report += f"Total: {total_files} files in {len(groups)} groups\n"
        
        return report
    
    def detect_potential_duplicates(self, groups: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Detecta archivos que aparecen en múltiples grupos.
        
        Args:
            groups: Diccionario de grupos
            
        Returns:
            Diccionario archivo -> lista de grupos donde aparece
        """
        file_occurrences = {}
        
        for group_name, files in groups.items():
            for file_path in files:
                if file_path not in file_occurrences:
                    file_occurrences[file_path] = []
                file_occurrences[file_path].append(group_name)
        
        # Filtrar solo duplicados
        duplicates = {
            file_path: group_list 
            for file_path, group_list in file_occurrences.items() 
            if len(group_list) > 1
        }
        
        if duplicates:
            self.logger.warning(f"⚠️  Found {len(duplicates)} files with multiple group assignments")
        
        return duplicates
    
    def resolve_conflicts_by_priority(self, conflicts: Dict[str, List[str]]) -> Dict[str, str]:
        """
        Resuelve conflictos usando el sistema de prioridad.
        
        Args:
            conflicts: Diccionario archivo -> lista de grupos en conflicto
            
        Returns:
            Diccionario archivo -> grupo asignado
        """
        resolutions = {}
        
        for file_path, conflicting_groups in conflicts.items():
            # Encontrar el grupo con mayor prioridad
            highest_priority_group = None
            highest_priority = float('inf')
            
            for group in conflicting_groups:
                if group in self.priority_order:
                    priority = self.priority_order.index(group)
                    if priority < highest_priority:
                        highest_priority = priority
                        highest_priority_group = group
            
            if highest_priority_group:
                resolutions[file_path] = highest_priority_group
                self.logger.debug(f"Resolved conflict for {file_path}: assigned to {highest_priority_group}")
            else:
                # Fallback: primer grupo en la lista
                resolutions[file_path] = conflicting_groups[0]
                self.logger.warning(f"No priority found for {file_path}, assigned to {conflicting_groups[0]}")
        
        return resolutions
    
    def get_priority_statistics(self, groups: Dict[str, List[str]]) -> Dict:
        """
        Genera estadísticas basadas en prioridad.
        
        Args:
            groups: Diccionario de grupos
            
        Returns:
            Estadísticas de distribución por prioridad
        """
        stats = {
            'total_files': sum(len(files) for files in groups.values()),
            'groups_by_priority': {},
            'priority_distribution': {}
        }
        
        for group_name, files in groups.items():
            priority = self.priority_order.index(group_name) if group_name in self.priority_order else 999
            
            stats['groups_by_priority'][group_name] = {
                'priority': priority,
                'file_count': len(files),
                'percentage': 0  # Se calculará después
            }
        
        # Calcular porcentajes
        total = stats['total_files']
        if total > 0:
            for group_data in stats['groups_by_priority'].values():
                group_data['percentage'] = round((group_data['file_count'] / total) * 100, 1)
        
        # Distribución por nivel de prioridad
        for priority_level in range(1, 6):
            priority_groups = [
                group for group, data in stats['groups_by_priority'].items()
                if data['priority'] == priority_level
            ]
            
            if priority_groups:
                priority_files = sum(
                    stats['groups_by_priority'][group]['file_count']
                    for group in priority_groups
                )
                stats['priority_distribution'][f'priority_{priority_level}'] = {
                    'groups': priority_groups,
                    'file_count': priority_files,
                    'percentage': round((priority_files / total) * 100, 1) if total > 0 else 0
                }
        
        return stats
    
    def optimize_group_distribution(self, groups: Dict[str, List[str]], target_sizes: Dict[str, int] = None) -> Dict[str, List[str]]:
        """
        Optimiza la distribución de archivos entre grupos.
        
        Args:
            groups: Grupos actuales
            target_sizes: Tamaños objetivo por grupo (opcional)
            
        Returns:
            Grupos optimizados
        """
        if not target_sizes:
            # Distribución equilibrada por defecto
            total_files = sum(len(files) for files in groups.values())
            avg_size = total_files // len(groups) if groups else 0
            target_sizes = {group: avg_size for group in groups.keys()}
        
        optimized_groups = {}
        
        # Por ahora, mantenemos la asignación original
        # En futuras versiones se puede implementar redistribución
        for group_name, files in groups.items():
            optimized_groups[group_name] = files.copy()
        
        self.logger.info(f"Group distribution optimization complete")
        
        return optimized_groups
