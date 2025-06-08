#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GroupManager to prevent empty groups.

Part of Phase 3: Critical Problem Fixes
Resolves: Problem 1 - Groups with 0 files
"""

from typing import Dict, List, Optional
from pathlib import Path
import logging

try:
    from models.project import FileInfo
except ImportError:
    # Fallback for direct execution
    from ..models.project import FileInfo

logger = logging.getLogger(__name__)


class GroupManager:
    """Group manager that prevents empty groups"""
    
    def __init__(self, check_file_existence: bool = True):
        """Initialize the group manager.
        
        Args:
            check_file_existence: Whether to check if files actually exist on filesystem
        """
        self.logger = logger
        self.check_file_existence = check_file_existence
    
    def filter_empty_groups(self, groups: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Remove groups without files or with non-existent files.
        
        Args:
            groups: Dictionary of groups with file lists
            
        Returns:
            Filtered dictionary without empty groups
        """
        filtered_groups = {}
        
        for group_name, files in groups.items():
            # Filter files that actually exist (if enabled)
            if self.check_file_existence:
                existing_files = [f for f in files if self._file_exists(f)]
            else:
                # In test mode, assume all files exist
                existing_files = files
            
            # Only add group if it has valid files
            if existing_files and len(existing_files) > 0:
                filtered_groups[group_name] = existing_files
                self.logger.info(f"✅ Group '{group_name}' has {len(existing_files)} valid files")
            else:
                self.logger.warning(f"⚠️  Skipping empty group: {group_name}")
        
        return filtered_groups
    
    def _file_exists(self, file_path: str) -> bool:
        """
        Verify that the file actually exists.
        
        Args:
            file_path: Path of the file to verify
            
        Returns:
            True if the file exists
        """
        try:
            return Path(file_path).exists()
        except Exception as e:
            self.logger.error(f"Error checking file existence for {file_path}: {e}")
            return False
    
    def create_groups(self, files: List[FileInfo]) -> Dict[str, List[str]]:
        """
        Create groups ensuring they are not empty.
        
        Args:
            files: List of FileInfo to group
            
        Returns:
            Dictionary of valid groups without empty groups
        """
        raw_groups = self._build_raw_groups(files)
        return self.filter_empty_groups(raw_groups)
    
    def _build_raw_groups(self, files: List[FileInfo]) -> Dict[str, List[str]]:
        """
        Build initial groups based on file patterns.
        
        Args:
            files: List of FileInfo
            
        Returns:
            Initial groups (may be empty)
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
            
            # Grouping logic
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
        Validate that there are no empty groups.
        
        Args:
            groups: Dictionary of groups to validate
            
        Returns:
            True if all groups have files
            
        Raises:
            ValueError: If an empty group is found
        """
        for group_name, files in groups.items():
            if not files or len(files) == 0:
                raise ValueError(f"Empty group detected: {group_name}")
        
        self.logger.info(f"✅ All {len(groups)} groups validated successfully")
        return True
    
    def get_group_statistics(self, groups: Dict[str, List[str]]) -> Dict:
        """
        Generate group statistics.
        
        Args:
            groups: Dictionary of groups
            
        Returns:
            Grouping statistics
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
