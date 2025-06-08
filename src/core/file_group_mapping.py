#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de mapeo bidireccional archivo ↔ grupo.

Parte de la Fase 3: Corrección de Problemas Críticos
Resuelve: Problema 4 - Sin trazabilidad archivo ↔ grupo
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import json
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class FileGroupMapping:
    """Mapeo bidireccional archivo ↔ grupo"""
    file_path: str
    group_name: str
    group_type: str
    confidence: float
    assignment_reason: str
    timestamp: str


class GroupMappingManager:
    """Gestiona mapeo archivo-grupo con trazabilidad completa"""
    
    def __init__(self):
        """Initialize the group mapping manager."""
        self.mappings: List[FileGroupMapping] = []
        self.file_to_group: Dict[str, FileGroupMapping] = {}
        self.group_to_files: Dict[str, List[str]] = {}
        self.logger = logger
    
    def create_mappings(self, groups: Dict[str, List[str]], assignment_reasons: Dict[str, str] = None) -> List[FileGroupMapping]:
        """
        Crea mapeos con trazabilidad.
        
        Args:
            groups: Diccionario de grupos con sus archivos
            assignment_reasons: Razones de asignación por archivo (opcional)
            
        Returns:
            Lista de mapeos creados
        """
        assignment_reasons = assignment_reasons or {}
        mappings = []
        
        self.logger.info(f"Creating mappings for {len(groups)} groups")
        
        for group_name, files in groups.items():
            for file_path in files:
                mapping = FileGroupMapping(
                    file_path=file_path,
                    group_name=group_name,
                    group_type=self._detect_group_type(group_name),
                    confidence=1.0,  # Por ahora, confianza máxima
                    assignment_reason=assignment_reasons.get(file_path, "priority_based"),
                    timestamp=datetime.now().isoformat()
                )
                mappings.append(mapping)
        
        self._build_lookup_tables(mappings)
        
        self.logger.info(f"✅ Created {len(mappings)} file-group mappings")
        
        return mappings
    
    def get_file_group(self, file_path: str) -> Optional[FileGroupMapping]:
        """
        Encuentra el grupo de un archivo específico.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            FileGroupMapping o None si no se encuentra
        """
        mapping = self.file_to_group.get(file_path)
        
        if mapping:
            self.logger.debug(f"Found mapping for {file_path}: {mapping.group_name}")
        else:
            self.logger.warning(f"No mapping found for file: {file_path}")
        
        return mapping
    
    def get_group_files(self, group_name: str) -> List[str]:
        """
        Obtiene todos los archivos de un grupo.
        
        Args:
            group_name: Nombre del grupo
            
        Returns:
            Lista de rutas de archivos
        """
        files = self.group_to_files.get(group_name, [])
        
        self.logger.debug(f"Group {group_name} contains {len(files)} files")
        
        return files
    
    def get_mapping_statistics(self) -> Dict:
        """
        Estadísticas del mapeo.
        
        Returns:
            Diccionario con estadísticas
        """
        total_files = len(self.file_to_group)
        total_groups = len(self.group_to_files)
        
        group_sizes = [len(files) for files in self.group_to_files.values()]
        avg_group_size = sum(group_sizes) / len(group_sizes) if group_sizes else 0
        
        # Estadísticas por tipo de grupo
        type_stats = {}
        for mapping in self.mappings:
            group_type = mapping.group_type
            if group_type not in type_stats:
                type_stats[group_type] = {'files': 0, 'groups': set()}
            
            type_stats[group_type]['files'] += 1
            type_stats[group_type]['groups'].add(mapping.group_name)
        
        # Convertir sets a conteos
        for type_data in type_stats.values():
            type_data['groups'] = len(type_data['groups'])
        
        stats = {
            'total_files': total_files,
            'total_groups': total_groups,
            'average_group_size': round(avg_group_size, 1),
            'largest_group_size': max(group_sizes) if group_sizes else 0,
            'smallest_group_size': min(group_sizes) if group_sizes else 0,
            'group_type_distribution': type_stats,
            'mapping_completeness': self._calculate_completeness()
        }
        
        return stats
    
    def _calculate_completeness(self) -> Dict:
        """
        Calcula completitud del mapeo.
        
        Returns:
            Métricas de completitud
        """
        total_mappings = len(self.mappings)
        
        # Mappings con alta confianza
        high_confidence = len([m for m in self.mappings if m.confidence >= 0.8])
        
        # Mappings con razones específicas
        reasoned_mappings = len([m for m in self.mappings if m.assignment_reason != "unknown"])
        
        return {
            'total_mappings': total_mappings,
            'high_confidence_percentage': round((high_confidence / total_mappings) * 100, 1) if total_mappings > 0 else 0,
            'reasoned_mappings_percentage': round((reasoned_mappings / total_mappings) * 100, 1) if total_mappings > 0 else 0
        }
    
    def save_mappings(self, output_path: Path):
        """
        Guarda mapeos en archivo JSON para debugging.
        
        Args:
            output_path: Ruta donde guardar el archivo
        """
        mappings_data = []
        
        for mapping in self.mappings:
            mappings_data.append({
                'file_path': mapping.file_path,
                'group_name': mapping.group_name,
                'group_type': mapping.group_type,
                'confidence': mapping.confidence,
                'assignment_reason': mapping.assignment_reason,
                'timestamp': mapping.timestamp
            })
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'total_mappings': len(mappings_data),
                    'created_at': datetime.now().isoformat(),
                    'statistics': self.get_mapping_statistics()
                },
                'mappings': mappings_data
            }, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"✅ Saved {len(mappings_data)} mappings to {output_path}")
    
    def load_mappings(self, input_path: Path) -> bool:
        """
        Carga mapeos desde archivo JSON.
        
        Args:
            input_path: Ruta del archivo a cargar
            
        Returns:
            True si se cargó exitosamente
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            mappings = []
            for mapping_data in data.get('mappings', []):
                mapping = FileGroupMapping(
                    file_path=mapping_data['file_path'],
                    group_name=mapping_data['group_name'],
                    group_type=mapping_data['group_type'],
                    confidence=mapping_data['confidence'],
                    assignment_reason=mapping_data['assignment_reason'],
                    timestamp=mapping_data['timestamp']
                )
                mappings.append(mapping)
            
            self._build_lookup_tables(mappings)
            
            self.logger.info(f"✅ Loaded {len(mappings)} mappings from {input_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error loading mappings from {input_path}: {e}")
            return False
    
    def _build_lookup_tables(self, mappings: List[FileGroupMapping]):
        """
        Construye tablas de lookup para búsqueda rápida.
        
        Args:
            mappings: Lista de mapeos
        """
        self.mappings = mappings
        self.file_to_group = {m.file_path: m for m in mappings}
        
        self.group_to_files = {}
        for mapping in mappings:
            if mapping.group_name not in self.group_to_files:
                self.group_to_files[mapping.group_name] = []
            self.group_to_files[mapping.group_name].append(mapping.file_path)
    
    def _detect_group_type(self, group_name: str) -> str:
        """
        Detecta tipo de grupo basado en nombre.
        
        Args:
            group_name: Nombre del grupo
            
        Returns:
            Tipo de grupo detectado
        """
        name_lower = group_name.lower()
        
        if 'core' in name_lower:
            return 'core'
        elif 'test' in name_lower:
            return 'test'
        elif 'util' in name_lower:
            return 'utility'
        elif 'feature' in name_lower or 'component' in name_lower:
            return 'feature'
        elif 'config' in name_lower:
            return 'configuration'
        elif 'circular' in name_lower:
            return 'circular_dependency'
        else:
            return 'other'
    
    def validate_mapping_integrity(self) -> bool:
        """
        Valida la integridad del mapeo bidireccional.
        
        Returns:
            True si el mapeo es íntegro
            
        Raises:
            ValueError: Si hay inconsistencias
        """
        errors = []
        
        # Verificar que cada archivo en file_to_group existe en group_to_files
        for file_path, mapping in self.file_to_group.items():
            group_files = self.group_to_files.get(mapping.group_name, [])
            if file_path not in group_files:
                errors.append(f"File {file_path} mapped to {mapping.group_name} but not in group files list")
        
        # Verificar que cada archivo en group_to_files existe en file_to_group
        for group_name, files in self.group_to_files.items():
            for file_path in files:
                if file_path not in self.file_to_group:
                    errors.append(f"File {file_path} in group {group_name} but no mapping exists")
                elif self.file_to_group[file_path].group_name != group_name:
                    errors.append(f"File {file_path} has inconsistent group mapping")
        
        if errors:
            error_msg = "Mapping integrity errors:\n" + "\n".join(errors)
            self.logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)
        
        self.logger.info(f"✅ Mapping integrity validated: {len(self.mappings)} mappings are consistent")
        return True
    
    def find_orphaned_files(self, all_files: List[str]) -> List[str]:
        """
        Encuentra archivos que no tienen mapeo a ningún grupo.
        
        Args:
            all_files: Lista completa de archivos del proyecto
            
        Returns:
            Lista de archivos sin mapeo
        """
        mapped_files = set(self.file_to_group.keys())
        all_files_set = set(all_files)
        
        orphaned = list(all_files_set - mapped_files)
        
        if orphaned:
            self.logger.warning(f"⚠️  Found {len(orphaned)} orphaned files without group mapping")
        
        return orphaned
    
    def get_mapping_report(self) -> str:
        """
        Genera reporte detallado del mapeo.
        
        Returns:
            String con reporte completo
        """
        stats = self.get_mapping_statistics()
        
        report = "🗺️  File-Group Mapping Report\n"
        report += "=" * 40 + "\n\n"
        
        report += f"📊 Overall Statistics:\n"
        report += f"   • Total files mapped: {stats['total_files']}\n"
        report += f"   • Total groups: {stats['total_groups']}\n"
        report += f"   • Average group size: {stats['average_group_size']}\n"
        report += f"   • Largest group: {stats['largest_group_size']} files\n"
        report += f"   • Smallest group: {stats['smallest_group_size']} files\n\n"
        
        report += f"🎯 Mapping Quality:\n"
        completeness = stats['mapping_completeness']
        report += f"   • High confidence mappings: {completeness['high_confidence_percentage']}%\n"
        report += f"   • Reasoned mappings: {completeness['reasoned_mappings_percentage']}%\n\n"
        
        report += f"📁 Group Type Distribution:\n"
        for group_type, type_data in stats['group_type_distribution'].items():
            report += f"   • {group_type}: {type_data['files']} files in {type_data['groups']} groups\n"
        
        report += "\n📋 Group Details:\n"
        for group_name, files in self.group_to_files.items():
            group_type = self._detect_group_type(group_name)
            report += f"   📁 {group_name} ({group_type}): {len(files)} files\n"
            
            # Mostrar algunos archivos como ejemplo
            for i, file_path in enumerate(files[:3]):
                report += f"      • {file_path}\n"
            if len(files) > 3:
                report += f"      ... and {len(files) - 3} more\n"
        
        return report
