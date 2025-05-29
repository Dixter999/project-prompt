#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Debug script to investigate dependency analysis issues.
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.analyzers.connection_analyzer import ConnectionAnalyzer
from src.analyzers.dependency_graph import DependencyGraph
from src.utils.logger import get_logger

logger = get_logger()

def debug_connection_analysis():
    """Debug the connection analysis process."""
    project_path = str(project_root)
    
    print(f"🔍 Debugging dependency analysis for: {project_path}")
    print("=" * 80)
    
    # Initialize analyzers
    connection_analyzer = ConnectionAnalyzer()
    
    print("1. Testing ConnectionAnalyzer...")
    print("-" * 40)
    
    # Analyze connections with detailed logging
    connections_result = connection_analyzer.analyze_connections(project_path, max_files=1000)
    
    print(f"✅ Files analyzed: {connections_result.get('files_analyzed', 0)}")
    print(f"✅ Language stats: {connections_result.get('language_stats', {})}")
    
    file_imports = connections_result.get('file_imports', {})
    print(f"✅ Files with imports: {len(file_imports)}")
    
    # Sample file imports for debugging
    print("\n📄 Sample file imports (first 5):")
    for i, (file_path, imports_data) in enumerate(list(file_imports.items())[:5]):
        language = imports_data.get('language', 'unknown')
        imports = imports_data.get('imports', [])
        print(f"  {i+1}. {file_path}")
        print(f"     Language: {language}")
        print(f"     Imports ({len(imports)}): {imports[:3]}{'...' if len(imports) > 3 else ''}")
        print()
    
    file_connections = connections_result.get('file_connections', {})
    print(f"✅ Files with connections: {len(file_connections)}")
    
    # Count total connections
    total_connections = sum(len(targets) for targets in file_connections.values())
    print(f"✅ Total connections: {total_connections}")
    
    # Show sample connections
    print("\n🔗 Sample connections (first 5 files with connections):")
    connection_count = 0
    for file_path, targets in file_connections.items():
        if connection_count >= 5:
            break
        if targets:  # Only show files with actual connections
            print(f"  {file_path} → {targets}")
            connection_count += 1
    
    print("\n" + "=" * 80)
    
    # Test DependencyGraph
    print("2. Testing DependencyGraph...")
    print("-" * 40)
    
    dependency_graph = DependencyGraph()
    graph_result = dependency_graph.build_dependency_graph(
        project_path, 
        max_files=1000, 
        use_madge=False  # Use traditional analysis to debug
    )
    
    print(f"✅ Nodes: {len(graph_result.get('nodes', []))}")
    print(f"✅ Edges: {len(graph_result.get('edges', []))}")
    print(f"✅ Metrics: {graph_result.get('metrics', {})}")
    
    # Show sample edges
    edges = graph_result.get('edges', [])
    print(f"\n🔗 Sample edges (first 10):")
    for i, edge in enumerate(edges[:10]):
        source = edge.get('source', 'unknown')
        target = edge.get('target', 'unknown')
        print(f"  {i+1}. {source} → {target}")
    
    print("\n" + "=" * 80)
    
    # Debug import resolution
    print("3. Debugging import resolution...")
    print("-" * 40)
    
    # Find Python files and test import extraction
    python_files = []
    for file_path, imports_data in file_imports.items():
        if imports_data.get('language') == 'python':
            python_files.append(file_path)
    
    print(f"✅ Python files found: {len(python_files)}")
    
    # Test a few Python files for import resolution
    sample_python_files = python_files[:3]
    for file_path in sample_python_files:
        print(f"\n📄 Testing: {file_path}")
        
        # Get imports for this file
        imports_data = file_imports.get(file_path, {})
        imports = imports_data.get('imports', [])
        print(f"   Raw imports: {imports}")
        
        # Test resolution manually
        connections = file_connections.get(file_path, [])
        print(f"   Resolved connections: {connections}")
        
        # Manual resolution test
        module_map = connection_analyzer._build_module_map(file_imports, project_path)
        print(f"   Module map sample: {dict(list(module_map.items())[:5])}")
        
        for imp in imports[:3]:  # Test first 3 imports
            resolved = connection_analyzer._resolve_import(
                imp, file_path, 'python', module_map, project_path
            )
            print(f"   '{imp}' → {resolved}")
    
    print("\n" + "=" * 80)
    print("🎯 Debug complete!")
    
    # Summary
    total_imports = sum(len(data.get('imports', [])) for data in file_imports.values())
    print(f"\n📊 Summary:")
    print(f"   - Files analyzed: {len(file_imports)}")
    print(f"   - Total raw imports found: {total_imports}")
    print(f"   - Files with resolved connections: {len(file_connections)}")
    print(f"   - Total resolved connections: {total_connections}")
    print(f"   - Resolution rate: {(total_connections/total_imports*100):.1f}%" if total_imports > 0 else "   - No imports found")

if __name__ == "__main__":
    debug_connection_analysis()
