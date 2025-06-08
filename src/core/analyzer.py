#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simplified ProjectAnalyzer for ProjectPrompt v2.0
Streamlined analysis focusing on core functionality
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from pathlib import Path
import json

from .scanner import ProjectScanner
from .detector import FunctionalityDetector  
from .group_manager import GroupManager
from ..models.project import ScanConfig, ProjectAnalysis, ProjectType, AnalysisStatus


class ProjectAnalyzer:
    """Simplified project analyzer"""
    
    def __init__(self, scan_config: Optional[ScanConfig] = None):
        """Initialize analyzer with optional scan configuration"""
        self.scan_config = scan_config or ScanConfig()
        self.scanner = ProjectScanner()
        self.detector = FunctionalityDetector()
        self.group_manager = GroupManager()
    
    def analyze_project(self, path: Path, output_dir: Path = None) -> Dict:
        """
        Analyze project structure and create functional groups.
        
        Args:
            path: Path to project directory
            output_dir: Output directory for analysis files
            
        Returns:
            Dictionary with analysis results for CLI compatibility
        """
        if not os.path.isdir(path):
            raise ValueError(f"Path is not a valid directory: {path}")
        
        # Step 1: Scan project files
        scan_result = self.scanner.scan_project(str(path))
        
        # Step 2: Extract file paths for functionality detection
        file_paths = [f.path for f in scan_result.files]
        
        # Step 3: Detect functionalities
        functionality_result = self.detector.detect_functionalities(file_paths)
        
        # Step 4: Create functional groups using file info
        raw_groups = self.group_manager.create_groups(scan_result.files)
        groups = self.group_manager.filter_empty_groups(raw_groups)
        
        # Step 5: Build complete analysis result using proper model
        analysis = ProjectAnalysis(
            project_name=path.name,
            project_path=str(path),
            project_type=self._detect_project_type(file_paths, scan_result.main_language),
            main_language=scan_result.main_language,
            file_count=len(scan_result.files),
            directory_count=len(scan_result.directories),
            total_size=scan_result.total_size,
            detected_functionalities=[f.name for f in functionality_result],
            functionality_details=functionality_result,
            files=scan_result.files,
            groups=groups,
            analysis_date=datetime.now().isoformat(),
            status=AnalysisStatus.COMPLETED
        )
        
        # Save analysis if output directory specified
        if output_dir:
            self._save_analysis_files(analysis, output_dir)
        
        # Return CLI-compatible format
        return {
            'project_name': analysis.project_name,
            'project_path': analysis.project_path,
            'project_type': analysis.project_type.value,
            'main_language': analysis.main_language,
            'file_count': analysis.file_count,
            'analysis_date': analysis.analysis_date,
            'detected_functionalities': analysis.detected_functionalities,
            'files': analysis.files,
            'functional_groups': analysis.groups,
            'status': analysis.status.value
        }
    
    def _detect_project_type(self, file_paths: List[str], main_language: str) -> ProjectType:
        """Automatically detect project type based on file patterns and language"""
        # API patterns
        api_patterns = ['api', 'server', 'backend', 'service', 'endpoint', 'routes']
        if any(pattern in ' '.join(file_paths).lower() for pattern in api_patterns):
            return ProjectType.API
            
        # Frontend patterns  
        frontend_patterns = ['component', 'react', 'vue', 'angular', 'frontend', 'ui', 'views']
        if any(pattern in ' '.join(file_paths).lower() for pattern in frontend_patterns):
            return ProjectType.WEB_APPLICATION
            
        # CLI patterns
        cli_patterns = ['cli', 'command', 'main.py', 'console', 'terminal']
        if any(pattern in ' '.join(file_paths).lower() for pattern in cli_patterns):
            return ProjectType.CLI_TOOL
            
        # Library patterns
        lib_patterns = ['lib', 'library', 'package', 'module', '__init__.py']
        if any(pattern in ' '.join(file_paths).lower() for pattern in lib_patterns):
            return ProjectType.LIBRARY
            
        return ProjectType.UNKNOWN
    
    def _save_analysis_files(self, analysis: ProjectAnalysis, output_dir: Path):
        """Save analysis to proper directory structure"""
        # Create main structure
        output_dir.mkdir(parents=True, exist_ok=True)
        analysis_dir = output_dir / "analysis"
        analysis_dir.mkdir(parents=True, exist_ok=True)
        functional_groups_dir = analysis_dir / "functional-groups"
        functional_groups_dir.mkdir(parents=True, exist_ok=True)
        
        # Save project structure analysis
        project_structure_file = analysis_dir / "project-structure.md"
        project_structure_content = self._generate_project_structure_md(analysis)
        project_structure_file.write_text(project_structure_content, encoding='utf-8')
        
        # Save dependency map
        dependency_map_file = analysis_dir / "dependency-map.md"
        dependency_map_content = self._generate_dependency_map_md(analysis)
        dependency_map_file.write_text(dependency_map_content, encoding='utf-8')
        
        # Save individual group analysis files
        for group_name, files in analysis.groups.items():
            group_file = functional_groups_dir / f"{self._sanitize_filename(group_name)}-analysis.md"
            group_content = self._generate_group_analysis_md(group_name, files, analysis)
            group_file.write_text(group_content, encoding='utf-8')
        
        # Save JSON files for compatibility
        groups_file = output_dir / "groups.json"
        groups_data = {
            "groups": analysis.groups,
            "total_groups": len(analysis.groups)
        }
        with open(groups_file, 'w', encoding='utf-8') as f:
            json.dump(groups_data, f, indent=2)
    
    def _generate_project_structure_md(self, analysis: ProjectAnalysis) -> str:
        """Generate project structure markdown"""
        return f"""# Project Structure Analysis

## Project Information
- **Name**: {analysis.project_name}
- **Type**: {analysis.project_type.value}
- **Main Language**: {analysis.main_language}
- **Total Files**: {analysis.file_count}
- **Total Directories**: {analysis.directory_count}
- **Analysis Date**: {analysis.analysis_date}

## Detected Functionalities
{chr(10).join(f"- {func}" for func in analysis.detected_functionalities)}

## File Distribution by Language
{self._generate_language_stats(analysis.files)}

## Functional Groups Summary
{chr(10).join(f"- **{name}**: {len(files)} files" for name, files in analysis.groups.items())}
"""
    
    def _generate_dependency_map_md(self, analysis: ProjectAnalysis) -> str:
        """Generate dependency map markdown"""
        return f"""# Dependency Map

## Project Dependencies Analysis
- **Project**: {analysis.project_name}
- **Type**: {analysis.project_type.value}

## Internal Dependencies
{self._analyze_internal_dependencies(analysis.groups)}

## External Dependencies
{self._analyze_external_dependencies(analysis.files)}
"""
    
    def _generate_group_analysis_md(self, group_name: str, files: List[str], analysis: ProjectAnalysis) -> str:
        """Generate individual group analysis"""
        return f"""# {group_name} Analysis

## Group Overview
- **Group Name**: {group_name}
- **File Count**: {len(files)}
- **Project Type**: {analysis.project_type.value}

## Files in this Group
{chr(10).join(f"- `{file}`" for file in files)}

## Group Characteristics
{self._analyze_group_characteristics(group_name, files, analysis.project_type)}
"""
    
    def _generate_language_stats(self, files: List) -> str:
        """Generate language statistics"""
        from collections import Counter
        if not files:
            return "No files analyzed"
        
        language_counts = Counter(f.language for f in files if hasattr(f, 'language'))
        total = sum(language_counts.values())
        
        if total == 0:
            return "No language information available"
        
        stats = []
        for lang, count in language_counts.most_common():
            percentage = (count / total) * 100
            stats.append(f"- **{lang}**: {count} files ({percentage:.1f}%)")
        
        return chr(10).join(stats)
    
    def _analyze_internal_dependencies(self, groups: Dict) -> str:
        """Analyze internal dependencies between groups"""
        return "Internal dependency analysis will be implemented based on imports and references."
    
    def _analyze_external_dependencies(self, files: List) -> str:
        """Analyze external dependencies"""
        return "External dependency analysis will be implemented based on package files and imports."
    
    def _analyze_group_characteristics(self, group_name: str, files: List[str], project_type) -> str:
        """Analyze characteristics of a specific group"""
        return f"This group contains {len(files)} files that are classified as {group_name.lower()}."
    
    def _sanitize_filename(self, name: str) -> str:
        """Convert name to valid filename"""
        import re
        sanitized = re.sub(r'[^\w\s-]', '', name)
        sanitized = re.sub(r'[-\s]+', '-', sanitized)
        return sanitized.lower().strip('-')
