#!/usr/bin/env python3
"""
Script to run the analyze function directly.
"""

import os
import sys

# Add project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def analyze_project(path):
    """Analyze a project's structure and functionalities."""
    print(f"Analyzing project at: {path}")
    
    # Only import what we need to avoid circular imports
    from src.analyzers.project_scanner import ProjectScanner
    
    scanner = ProjectScanner()
    project_data = scanner.scan_project(path)
    
    print("\nProject Statistics:")
    stats = project_data.get('stats', {})
    print(f"Total files: {stats.get('total_files', 0)}")
    print(f"Total directories: {stats.get('total_dirs', 0)}")
    print(f"Analyzed files: {stats.get('analyzed_files', 0)}")
    print(f"Binary files: {stats.get('binary_files', 0)}")
    print(f"Total size: {stats.get('total_size_kb', 0):,} KB")
    
    print("\nLanguage Distribution:")
    languages = project_data.get('languages', {})
    for lang, stats in languages.items():
        print(f"- {lang}: {stats.get('files', 0)} files, {stats.get('lines', 0)} lines")
    
    print("\nImportant Files:")
    important_files = project_data.get('important_files', {})
    for category, files in important_files.items():
        print(f"\n{category.upper()}:")
        for file in files[:5]:  # Show only first 5 files
            print(f"- {file}")
        if len(files) > 5:
            print(f"  ... and {len(files) - 5} more")
    
    return project_data

if __name__ == "__main__":
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = os.path.dirname(os.path.abspath(__file__))
    
    analyze_project(project_path)
