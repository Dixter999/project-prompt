"""
Project Analyzer Module.

This module provides the main ProjectAnalyzer class that coordinates
various analysis components to provide comprehensive project insights.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .project_scanner import get_project_scanner
from .functionality_detector import get_functionality_detector
from .project_structure_analyzer import get_project_structure_analyzer
from .code_quality_analyzer import get_code_quality_analyzer

logger = logging.getLogger(__name__)


class ProjectAnalyzer:
    """Main project analyzer that coordinates different analysis components."""
    
    def __init__(self, 
                 max_file_size_mb: float = 5.0,
                 max_files: int = 10000,
                 include_quality_analysis: bool = True):
        """
        Initialize the project analyzer.
        
        Args:
            max_file_size_mb: Maximum file size to analyze in MB
            max_files: Maximum number of files to analyze
            include_quality_analysis: Whether to include code quality analysis
        """
        self.max_file_size_mb = max_file_size_mb
        self.max_files = max_files
        self.include_quality_analysis = include_quality_analysis
        
        # Initialize component analyzers
        self.scanner = get_project_scanner(
            max_file_size_mb=max_file_size_mb,
            max_files=max_files
        )
        self.functionality_detector = get_functionality_detector(scanner=self.scanner)
        self.structure_analyzer = get_project_structure_analyzer()
        
        if include_quality_analysis:
            self.quality_analyzer = get_code_quality_analyzer()
        else:
            self.quality_analyzer = None
    
    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """
        Perform comprehensive project analysis.
        
        Args:
            project_path: Path to the project root
            
        Returns:
            Dict containing comprehensive analysis results
        """
        project_path = Path(project_path).resolve()
        
        if not project_path.exists():
            raise FileNotFoundError(f"Project path does not exist: {project_path}")
        
        if not project_path.is_dir():
            raise ValueError(f"Project path is not a directory: {project_path}")
        
        logger.info(f"Starting comprehensive analysis of {project_path}")
        
        analysis_result = {
            'project_path': str(project_path),
            'analysis_timestamp': datetime.now().isoformat(),
            'basic_structure': {},
            'detailed_structure': {},
            'functionalities': {},
            'quality_metrics': {},
            'summary': {},
            'recommendations': []
        }
        
        try:
            # 1. Basic project scanning
            logger.info("Performing basic project scan...")
            analysis_result['basic_structure'] = self.scanner.scan_project(str(project_path))
            
            # 2. Detailed structure analysis
            logger.info("Performing detailed structure analysis...")
            analysis_result['detailed_structure'] = self.structure_analyzer.analyze_structure(str(project_path))
            
            # 3. Functionality detection
            logger.info("Detecting project functionalities...")
            analysis_result['functionalities'] = self.functionality_detector.detect_functionalities(str(project_path))
            
            # 4. Code quality analysis (if enabled)
            if self.quality_analyzer:
                logger.info("Performing code quality analysis...")
                try:
                    analysis_result['quality_metrics'] = self.quality_analyzer.analyze_code_quality(str(project_path))
                except Exception as e:
                    logger.warning(f"Code quality analysis failed: {e}")
                    analysis_result['quality_metrics'] = {'error': str(e)}
            
            # 5. Generate summary and recommendations
            analysis_result['summary'] = self._generate_summary(analysis_result)
            analysis_result['recommendations'] = self._generate_recommendations(analysis_result)
            
            logger.info("Project analysis completed successfully")
            
        except Exception as e:
            logger.error(f"Error during project analysis: {e}")
            analysis_result['error'] = str(e)
            raise
        
        return analysis_result
    
    def analyze_specific_component(self, project_path: str, component_type: str) -> Dict[str, Any]:
        """
        Analyze a specific component of the project.
        
        Args:
            project_path: Path to the project root
            component_type: Type of analysis ('structure', 'functionality', 'quality')
            
        Returns:
            Dict containing specific analysis results
        """
        project_path = Path(project_path).resolve()
        
        if component_type == 'structure':
            return self.structure_analyzer.analyze_structure(str(project_path))
        elif component_type == 'functionality':
            return self.functionality_detector.detect_functionalities(str(project_path))
        elif component_type == 'quality' and self.quality_analyzer:
            return self.quality_analyzer.analyze_code_quality(str(project_path))
        elif component_type == 'basic':
            return self.scanner.scan_project(str(project_path))
        else:
            raise ValueError(f"Unknown component type: {component_type}")
    
    def _generate_summary(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the analysis results."""
        summary = {}
        
        # Basic statistics
        basic_stats = analysis_result.get('basic_structure', {}).get('stats', {})
        summary['file_count'] = basic_stats.get('total_files', 0)
        summary['directory_count'] = basic_stats.get('total_dirs', 0)
        summary['total_size_kb'] = basic_stats.get('total_size_kb', 0)
        
        # Languages
        languages = analysis_result.get('basic_structure', {}).get('languages', {})
        if languages and isinstance(languages, dict):
            # Filter out any non-dict values and safely get primary language
            valid_languages = {k: v for k, v in languages.items() if isinstance(v, dict) and 'files' in v}
            if valid_languages:
                summary['primary_language'] = max(valid_languages.items(), key=lambda x: x[1]['files'])[0]
                summary['language_count'] = len(valid_languages)
            else:
                summary['primary_language'] = 'unknown'
                summary['language_count'] = 0
        else:
            summary['primary_language'] = 'unknown'
            summary['language_count'] = 0
        
        # Project patterns
        patterns = analysis_result.get('detailed_structure', {}).get('patterns', {})
        summary['project_type'] = patterns.get('project_type', 'unknown')
        summary['has_tests'] = patterns.get('has_tests', False)
        summary['has_docs'] = patterns.get('has_docs', False)
        
        # Functionality count
        functionalities = analysis_result.get('functionalities', {})
        summary['functionality_count'] = len(functionalities.get('functionalities', []))
        
        # Quality metrics summary
        quality = analysis_result.get('quality_metrics', {})
        if quality and 'error' not in quality:
            summary['quality_score'] = quality.get('overall_score', 'N/A')
        
        return summary
    
    def _generate_recommendations(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis results."""
        recommendations = []
        
        # Collect recommendations from different analyzers
        structure_recs = analysis_result.get('detailed_structure', {}).get('recommendations', [])
        recommendations.extend(structure_recs)
        
        # Add general recommendations based on summary
        summary = analysis_result.get('summary', {})
        
        if summary.get('file_count', 0) > 1000:
            recommendations.append("Large codebase detected - consider implementing automated documentation")
        
        if not summary.get('has_tests'):
            recommendations.append("No test directory found - implement unit testing for better code quality")
        
        if not summary.get('has_docs'):
            recommendations.append("No documentation directory found - consider adding project documentation")
        
        if summary.get('functionality_count', 0) > 20:
            recommendations.append("Many functionalities detected - consider creating architectural documentation")
        
        return list(set(recommendations))  # Remove duplicates
    
    def export_analysis(self, analysis_result: Dict[str, Any], output_path: str, format: str = 'json') -> str:
        """
        Export analysis results to file.
        
        Args:
            analysis_result: Analysis results to export
            output_path: Path where to save the results
            format: Export format ('json', 'yaml')
            
        Returns:
            Path to the exported file
        """
        output_path = Path(output_path)
        
        if format.lower() == 'json':
            if not output_path.suffix:
                output_path = output_path.with_suffix('.json')
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, indent=2, ensure_ascii=False)
                
        elif format.lower() == 'yaml':
            import yaml
            if not output_path.suffix:
                output_path = output_path.with_suffix('.yaml')
            
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(analysis_result, f, default_flow_style=False, allow_unicode=True)
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        return str(output_path)


def get_project_analyzer(max_file_size_mb: float = 5.0,
                        max_files: int = 10000,
                        include_quality_analysis: bool = True) -> ProjectAnalyzer:
    """
    Get a configured project analyzer instance.
    
    Args:
        max_file_size_mb: Maximum file size to analyze in MB
        max_files: Maximum number of files to analyze
        include_quality_analysis: Whether to include code quality analysis
        
    Returns:
        ProjectAnalyzer instance
    """
    return ProjectAnalyzer(
        max_file_size_mb=max_file_size_mb,
        max_files=max_files,
        include_quality_analysis=include_quality_analysis
    )
