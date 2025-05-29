#!/usr/bin/env python3
"""
Test script for the enhanced free dashboard functionality.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.markdown_dashboard import MarkdownDashboardGenerator
from src.utils.config import ConfigManager

def test_free_dashboard():
    """Test the enhanced free dashboard generation."""
    print("🧪 Testing Enhanced Free Dashboard Generation")
    print("=" * 50)
    
    project_path = "/mnt/h/Projects/project-prompt"
    
    try:
        print(f"📁 Project path: {project_path}")
        
        # Create config  
        config = ConfigManager()
        
        # Create dashboard generator
        dashboard_gen = MarkdownDashboardGenerator(project_path, config)
        
        # Force non-premium mode by setting premium_access to False
        dashboard_gen.premium_access = False
        
        print("🔄 Generating free dashboard...")
        
        # Generate free dashboard
        output_path = dashboard_gen._generate_free_markdown_dashboard()
        
        print(f"✅ Free dashboard generated: {output_path}")
        
        # Read and analyze the generated content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📊 Dashboard length: {len(content)} characters")
        print(f"📏 Dashboard lines: {len(content.split('\n'))} lines")
        
        # Check for functional groups section
        if "## 🎯 Grupos Funcionales" in content:
            print("✅ Functional groups section found!")
            
            # Count groups mentioned
            groups_count = content.count("###")
            print(f"📦 Number of functional groups found: {groups_count}")
            
            # Look for progress bars
            progress_bars = content.count("▓")
            print(f"📊 Progress bars found: {progress_bars}")
            
        else:
            print("❌ Functional groups section not found!")
            return False
        
        # Verify it's marked as free version
        if "versión gratuita" in content.lower():
            print("✅ Correctly marked as free version")
        else:
            print("⚠️  Free version marking not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_free_dashboard()
    sys.exit(0 if success else 1)
