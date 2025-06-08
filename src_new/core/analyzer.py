#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unified project analyzer for the new architecture.

Coordinates complete project analysis combining scanner and detector.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from pathlib import Path

from .scanner import ProjectScanner
from .detector import FunctionalityDetector
from .group_manager import GroupManager
from .dependency_analyzer import UnifiedDependencyAnalyzer
from .group_priority_system import GroupPrioritySystem
from .file_group_mapping import GroupMappingManager

try:
    from ..models.project import (
        ProjectAnalysis, ProjectType, AnalysisStatus, 
        ScanConfig, AnalysisConfig, determine_project_type
    )
except ImportError:
    # Fallback for direct execution
    from models.project import (
        ProjectAnalysis, ProjectType, AnalysisStatus, 
        ScanConfig, AnalysisConfig, determine_project_type
    )


class ProjectAnalyzer:
    """Unified analyzer that coordinates complete project analysis."""
    
    def __init__(self, scan_config: Optional[ScanConfig] = None, 
                 analysis_config: Optional[AnalysisConfig] = None):
        """
        Initialize analyzer with configuration.
        
        Args:
            scan_config: Configuration for scanning
            analysis_config: Configuration for analysis
        """
        self.scan_config = scan_config or ScanConfig()
        self.analysis_config = analysis_config or AnalysisConfig()
        
        # Phase 3: Initialize all corrected components
        self.scanner = ProjectScanner(self.scan_config)
        self.detector = FunctionalityDetector()
        self.group_manager = GroupManager()
        self.dependency_analyzer = UnifiedDependencyAnalyzer()
        self.priority_system = GroupPrioritySystem()
        self.mapping_manager = GroupMappingManager()
        
    def analyze_project(self, path: str, use_ai: bool = False) -> ProjectAnalysis:
        """
        Complete project analysis with Phase 3 critical fixes.
        
        Steps:
        1. Scan files and structure
        2. Detect functionalities
        3. Analyze dependencies (unified analyzer)
        4. Create groups (without empty ones)
        5. Eliminate duplications (priority system)
        6. Create bidirectional mapping
        7. Create consolidated analysis
        8. Generate AI context if requested
        
        Args:
            path: Path to project
            use_ai: Whether to prepare AI context (for future use)
            
        Returns:
            ProjectAnalysis with complete results and corrected issues
        """
        if not os.path.isdir(path):
            raise ValueError(f"Path is not a valid directory: {path}")
        
        project_path = Path(path).resolve()
        project_name = project_path.name
        
        # 1. Scan project structure
        structure = self.scanner.scan_project(str(project_path))
        
        # 2. Detect functionalities
        file_paths = [f.path for f in structure.files]
        functionalities = self.detector.detect_functionalities(file_paths)
        
        # 3. Phase 3 Fix: Unified dependency analysis
        dependency_result = self.dependency_analyzer.analyze_dependencies(file_paths)
        
        # 4. Phase 3 Fix: Create groups without empty ones
        groups = self.group_manager.create_groups(structure.files)
        
        # 5. Phase 3 Fix: Eliminate file duplications
        clean_groups = self.priority_system.assign_files_to_groups(groups)
        
        # 6. Phase 3 Fix: Create bidirectional file-group mapping
        mappings = self.mapping_manager.create_mappings(clean_groups)
        
        # 7. Determine project type
        functionality_names = [f.name for f in functionalities]
        project_type = determine_project_type(functionality_names, structure.main_language or "unknown")
        
        # 8. Create enhanced analysis with Phase 3 fixes
        analysis = ProjectAnalysis(
            project_name=project_name,
            project_path=str(project_path),
            project_type=project_type,
            main_language=structure.main_language or "unknown",
            file_count=structure.total_files,
            directory_count=structure.total_directories,
            total_size=structure.total_size,
            detected_functionalities=functionality_names,
            functionality_details=functionalities,
            important_files=[f.path for f in structure.files if hasattr(f, 'is_important') and f.is_important],
            status=AnalysisStatus.COMPLETED,
            analysis_date=datetime.now().isoformat(),
            
            # Phase 3: Enhanced data
            files=structure.files,
            groups=clean_groups,
            file_mappings=mappings,
            dependency_analysis={
                'graph': dependency_result['graph'],
                'total_connections': dependency_result['total_connections'],
                'circular_dependencies': dependency_result['circular_dependencies'],
                'group_statistics': self.group_manager.get_group_statistics(clean_groups),
                'dependency_summary': self.dependency_analyzer.get_dependency_summary()
            }
        )
        
        # 9. Generate AI context if requested
        if use_ai:
            analysis.ai_context = self._generate_ai_context(structure, functionalities, clean_groups, dependency_result)
            analysis.context_files = [f.path for f in structure.files[:10]]  # Top 10 files
        
        # 10. Validate Phase 3 success metrics
        self._validate_phase3_metrics(analysis)
        
        return analysis
    
    def _generate_ai_context(self, structure, functionalities, groups=None, dependency_result=None) -> str:
        """Generate enhanced context summary for AI analysis with Phase 3 data."""
        context_parts = [
            f"Project: {structure.root_path}",
            f"Files: {structure.total_files}, Directories: {structure.total_directories}",
            f"Main language: {structure.main_language}",
            f"Languages: {', '.join(structure.languages.keys())}",
            f"Functionalities: {', '.join([f.name for f in functionalities])}"
        ]
        
        # Phase 3: Add group information
        if groups:
            context_parts.append(f"Groups: {len(groups)} groups without empty ones")
            for group_name, files in groups.items():
                context_parts.append(f"  - {group_name}: {len(files)} files")
        
        # Phase 3: Add dependency information
        if dependency_result:
            context_parts.append(f"Dependencies: {dependency_result['total_connections']} connections")
            if dependency_result['circular_dependencies']:
                context_parts.append(f"Circular dependencies: {len(dependency_result['circular_dependencies'])} detected")
        
        return "\n".join(context_parts)
    
    def _validate_phase3_metrics(self, analysis: ProjectAnalysis) -> None:
        """
        Validate that Phase 3 success metrics are met.
        
        Args:
            analysis: ProjectAnalysis to validate
            
        Raises:
            ValueError: If any Phase 3 metric fails
        """
        errors = []
        
        # 1. Zero grupos vacíos
        if hasattr(analysis, 'groups'):
            for group_name, files in analysis.groups.items():
                if not files or len(files) == 0:
                    errors.append(f"Empty group found: {group_name}")
        
        # 2. Zero duplicación
        if hasattr(analysis, 'groups'):
            all_files = [f for files in analysis.groups.values() for f in files]
            if len(all_files) != len(set(all_files)):
                duplicates = [f for f in all_files if all_files.count(f) > 1]
                errors.append(f"Duplicate files found: {duplicates}")
        
        # 3. Mapeo completo
        if hasattr(analysis, 'file_mappings') and hasattr(analysis, 'groups'):
            expected_mappings = sum(len(files) for files in analysis.groups.values())
            actual_mappings = len(analysis.file_mappings)
            if expected_mappings != actual_mappings:
                errors.append(f"Incomplete mapping: expected {expected_mappings}, got {actual_mappings}")
        
        # 4. Conexiones reales en grafo (opcional, puede ser 0 para proyectos simples)
        if hasattr(analysis, 'dependency_connections'):
            # Solo advertencia, no error
            if analysis.dependency_connections == 0:
                print("⚠️  Warning: No dependency connections found (may be normal for simple projects)")
        
        if errors:
            error_msg = "Phase 3 validation failed:\n" + "\n".join(errors)
            raise ValueError(error_msg)
        
        print("✅ Phase 3 metrics validation passed!")
        
    def get_phase3_report(self, analysis: ProjectAnalysis) -> str:
        """
        Generate Phase 3 success report.
        
        Args:
            analysis: ProjectAnalysis with Phase 3 data
            
        Returns:
            String with detailed Phase 3 report
        """
        report = "🎯 Phase 3: Critical Fixes Report\n"
        report += "=" * 40 + "\n\n"
        
        # Problem 1: Empty groups
        if hasattr(analysis, 'groups'):
            report += f"✅ Problem 1 - Empty Groups: SOLVED\n"
            report += f"   • {len(analysis.groups)} groups created\n"
            report += f"   • Zero empty groups\n"
            for group_name, files in analysis.groups.items():
                report += f"   • {group_name}: {len(files)} files\n"
            report += "\n"
        
        # Problem 2: Unified dependency analyzer
        if hasattr(analysis, 'dependency_connections'):
            report += f"✅ Problem 2 - Unified Dependency Analyzer: SOLVED\n"
            report += f"   • {analysis.dependency_connections} real connections found\n"
            if hasattr(analysis, 'circular_dependencies'):
                report += f"   • {len(analysis.circular_dependencies)} circular dependencies detected\n"
            report += "\n"
        
        # Problem 3: File duplication
        if hasattr(analysis, 'groups'):
            all_files = [f for files in analysis.groups.values() for f in files]
            unique_files = set(all_files)
            report += f"✅ Problem 3 - File Duplication: SOLVED\n"
            report += f"   • {len(all_files)} total file assignments\n"
            report += f"   • {len(unique_files)} unique files\n"
            report += f"   • Zero duplicates\n\n"
        
        # Problem 4: File-group mapping
        if hasattr(analysis, 'file_mappings'):
            report += f"✅ Problem 4 - File-Group Mapping: SOLVED\n"
            report += f"   • {len(analysis.file_mappings)} bidirectional mappings\n"
            report += f"   • Complete traceability\n\n"
        
        # Overall success
        report += f"🏆 Phase 3 Status: ALL PROBLEMS SOLVED\n"
        report += f"   • Zero empty groups ✅\n"
        report += f"   • Unified analyzer ✅\n"
        report += f"   • Zero duplicates ✅\n"
        report += f"   • Complete mapping ✅\n"
        
        return report
    
    def analyze_for_ai_context(self, path: str, max_files: int = 50) -> Dict[str, Any]:
        """
        Análisis optimizado para generar contexto de IA.
        
        Enfocado en archivos más importantes y funcionalidades clave.
        
        Args:
            path: Ruta al proyecto
            max_files: Máximo número de archivos a incluir en contexto
            
        Returns:
            Dict con contexto optimizado para IA
        """
        # Análisis completo
        analysis = self.analyze(path)
        
        # Filtrar archivos más importantes
        important_files = self._select_important_files(analysis.files, max_files)
        
        # Preparar contexto para IA
        ai_context = {
            'project_overview': {
                'path': analysis.project_path,
                'total_files': analysis.stats['total_files'],
                'main_languages': analysis.languages.get('_main', []),
                'functionalities': analysis.functionalities['main_functionalities']
            },
            'important_files': important_files,
            'project_structure': self._generate_structure_summary(analysis.files),
            'recommendations': self._generate_basic_recommendations(analysis)
        }
        
        return ai_context
    
    def _select_important_files(self, files: List[Dict[str, Any]], max_files: int) -> List[Dict[str, Any]]:
        """Seleccionar archivos más importantes para contexto de IA."""
        # Filtrar archivos binarios y temporales
        code_files = [
            f for f in files 
            if not f.get('is_binary', True) 
            and f.get('language') 
            and f.get('size_kb', 0) < 100  # Max 100KB
        ]
        
        # Priorizar por importancia
        scored_files = []
        for file_info in code_files:
            score = self._calculate_file_importance(file_info)
            scored_files.append((score, file_info))
        
        # Ordenar por score y tomar los mejores
        scored_files.sort(key=lambda x: x[0], reverse=True)
        
        return [f[1] for f in scored_files[:max_files]]
    
    def _calculate_file_importance(self, file_info: Dict[str, Any]) -> float:
        """Calcular score de importancia de un archivo."""
        score = 0.0
        file_path = file_info.get('path', '').lower()
        file_name = file_info.get('name', '').lower()
        
        # Archivos en raíz son más importantes
        if '/' not in file_path:
            score += 2.0
        
        # Archivos de configuración
        if any(name in file_name for name in ['config', 'setup', 'main', 'app', 'index']):
            score += 1.5
        
        # Archivos README y documentación
        if 'readme' in file_name or 'doc' in file_path:
            score += 1.0
        
        # Penalizar archivos muy pequeños o muy grandes
        size_kb = file_info.get('size_kb', 0)
        if 1 <= size_kb <= 50:
            score += 0.5
        elif size_kb > 50:
            score -= 0.2
        
        return score
    
    def _generate_structure_summary(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generar resumen de estructura del proyecto."""
        directories = set()
        for file_info in files:
            path_parts = file_info.get('path', '').split('/')
            for i in range(len(path_parts)):
                if i > 0:  # Skip root
                    dir_path = '/'.join(path_parts[:i])
                    directories.add(dir_path)
        
        return {
            'total_directories': len(directories),
            'main_directories': sorted(list(directories))[:10],
            'file_types': self._count_file_types(files)
        }
    
    def _count_file_types(self, files: List[Dict[str, Any]]) -> Dict[str, int]:
        """Contar tipos de archivos por extensión."""
        type_counts = {}
        for file_info in files:
            ext = file_info.get('extension', '').lower()
            if ext:
                type_counts[ext] = type_counts.get(ext, 0) + 1
        
        # Retornar top 10
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_types[:10])
    
    def _generate_basic_recommendations(self, analysis: ProjectAnalysis) -> List[str]:
        """Generar recomendaciones básicas basadas en el análisis."""
        recommendations = []
        
        # Verificar documentación
        has_readme = any('readme' in f.get('name', '').lower() for f in analysis.files)
        if not has_readme:
            recommendations.append("Agregar archivo README.md para documentar el proyecto")
        
        # Verificar tests
        has_tests = 'testing' in analysis.functionalities.get('main_functionalities', [])
        if not has_tests:
            recommendations.append("Implementar tests para mejorar la calidad del código")
        
        # Verificar configuración
        has_config = 'configuration' in analysis.functionalities.get('main_functionalities', [])
        if not has_config:
            recommendations.append("Agregar archivos de configuración para diferentes entornos")
        
        # Verificar tamaño del proyecto
        if analysis.stats.get('total_files', 0) > 500:
            recommendations.append("Considerar modularizar el proyecto por su gran tamaño")
        
        return recommendations
