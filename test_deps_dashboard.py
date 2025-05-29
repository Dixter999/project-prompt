#!/usr/bin/env python3
"""
Test script specifically for dependency analysis in dashboard.
"""

from src.ui.markdown_dashboard import MarkdownDashboardGenerator
from src.utils.config import ConfigManager
from src.analyzers.dependency_graph import DependencyGraph

def test_dependency_section():
    """Test the dependency analysis section of the dashboard."""
    print("🔍 Testing dependency analysis in dashboard...")
    
    config = ConfigManager()
    config.set_premium(False)  # Test with free tier
    
    dashboard_gen = MarkdownDashboardGenerator("/mnt/h/Projects/project-prompt", config)
    
    # Test dependency analysis directly
    print("\n📊 Testing direct dependency analysis...")
    dep_analyzer = DependencyGraph()
    result = dep_analyzer.build_dependency_graph("/mnt/h/Projects/project-prompt", max_files=1000)
    
    print(f"✅ Nodes: {len(result.get('nodes', []))}")
    print(f"✅ Edges: {len(result.get('edges', []))}")
    print(f"✅ Metrics: {result.get('metrics', {})}")
    
    # Test dashboard generation with dependency section
    print("\n🎯 Testing dashboard dependency section...")
    
    # Generate only dependency section
    dependency_section = dashboard_gen._generate_dependency_section()
    
    print(f"✅ Dependency section generated!")
    print(f"Length: {len(dependency_section)} characters")
    
    # Show first part of dependency section
    print("\nPreview:")
    print(dependency_section[:500])
    print("...")
    
    # Check if enhanced features are present
    if "dependency matrix" in dependency_section.lower():
        print("✅ Enhanced dependency matrix found!")
    else:
        print("❌ Enhanced dependency matrix NOT found")
        
    if "importance" in dependency_section.lower():
        print("✅ Enhanced text visualization found!")
    else:
        print("❌ Enhanced text visualization NOT found")

if __name__ == "__main__":
    test_dependency_section()
