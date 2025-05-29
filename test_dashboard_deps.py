#!/usr/bin/env python3
"""
Test the enhanced dependency analysis specifically in dashboard.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, '/mnt/h/Projects/project-prompt')

from src.ui.markdown_dashboard import MarkdownDashboardGenerator
from src.utils.config import ConfigManager

def test_enhanced_dependency_dashboard():
    """Test enhanced dependency analysis in dashboard."""
    print("🔍 Testing enhanced dependency analysis in dashboard...")
    
    # Create configuration
    config = ConfigManager()
    config.set_premium(False)  # Test with free tier first
    
    # Create dashboard generator
    dashboard_gen = MarkdownDashboardGenerator("/mnt/h/Projects/project-prompt", config)
    
    print("\n📊 Testing dependency analysis retrieval...")
    
    # Test the dependency analysis method directly
    try:
        deps_data = dashboard_gen._get_dependency_analysis()
        print(f"✅ Dependency analysis completed!")
        print(f"   - Graph data available: {'graph_data' in deps_data}")
        print(f"   - Metrics available: {'metrics' in deps_data}")
        print(f"   - Functionality groups: {len(deps_data.get('functionality_groups', []))}")
        print(f"   - Central files: {len(deps_data.get('central_files', []))}")
        
        metrics = deps_data.get('metrics', {})
        if metrics:
            print(f"   - Total files: {metrics.get('total_files', 0)}")
            print(f"   - Total dependencies: {metrics.get('total_dependencies', 0)}")
            print(f"   - Average deps per file: {metrics.get('average_dependencies_per_file', 0):.1f}")
    
    except Exception as e:
        print(f"❌ Error in dependency analysis: {e}")
        return False
    
    print("\n🎯 Testing dependency section generation...")
    
    # Test the dependency section generation
    try:
        deps_section = dashboard_gen._generate_dependencies_section(deps_data)
        print(f"✅ Dependency section generated!")
        print(f"   - Section length: {len(deps_section)} characters")
        
        # Check for enhanced features
        section_lower = deps_section.lower()
        
        # Check for dependency matrix
        if "matriz" in section_lower or "matrix" in section_lower or "│" in deps_section:
            print("✅ Enhanced dependency matrix found!")
        else:
            print("❌ Dependency matrix NOT found")
            
        # Check for text visualization  
        if "representación textual" in section_lower:
            print("✅ Text visualization found!")
        else:
            print("❌ Text visualization NOT found")
            
        # Check for functionality groups
        if "grupos funcionales" in section_lower:
            print("✅ Functionality groups found!")
        else:
            print("❌ Functionality groups NOT found")
            
        # Show preview
        print("\n📋 Preview of dependency section:")
        print("=" * 60)
        print(deps_section[:800])
        print("..." if len(deps_section) > 800 else "")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating dependency section: {e}")
        return False

if __name__ == "__main__":
    success = test_enhanced_dependency_dashboard()
    if success:
        print("\n🎉 Enhanced dependency analysis test PASSED!")
    else:
        print("\n💥 Enhanced dependency analysis test FAILED!")
