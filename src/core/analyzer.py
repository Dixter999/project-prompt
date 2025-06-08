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
from ..models.project import ScanConfig


class ProjectAnalysis:
    """Simple analysis result container"""
    
    def __init__(self, project_path: Path, groups: Dict[str, List[str]], 
                 files: List[str], total_files: int):
        self.project_path = project_path
        self.groups = groups
        self.files = files
        self.total_files = total_files
        self.analysis_date = datetime.now()


class ProjectAnalyzer:
    """Simplified project analyzer"""
    
    def __init__(self, scan_config: Optional[ScanConfig] = None):
        """Initialize analyzer with optional scan configuration"""
        self.scan_config = scan_config or ScanConfig()
        self.scanner = ProjectScanner()
        self.detector = FunctionalityDetector()
        self.group_manager = GroupManager()
    
    def analyze_project(self, path: Path) -> ProjectAnalysis:
        """
        Analyze project structure and create functional groups.
        
        Args:
            path: Path to project directory
            
        Returns:
            ProjectAnalysis with groups and file information
        """
        if not os.path.isdir(path):
            raise ValueError(f"Path is not a valid directory: {path}")
        
        # Step 1: Scan project files
        scan_result = self.scanner.scan_project(path, self.scan_config)
        
        # Step 2: Detect functionalities
        functionality_result = self.detector.detect_functionalities(scan_result)
        
        # Step 3: Create functional groups (remove empty ones)
        raw_groups = self.group_manager.create_functional_groups(functionality_result)
        groups = {name: files for name, files in raw_groups.items() if files}
        
        # Create analysis result
        analysis = ProjectAnalysis(
            project_path=path,
            groups=groups,
            files=scan_result.files,
            total_files=len(scan_result.files)
        )
        
        return analysis
