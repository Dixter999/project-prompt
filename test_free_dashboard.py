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
    
    project_path = "/mnt/h/Projects/project-prompt"
    
    # Create config with free subscription
    config = ConfigManager()
    config.set_subscription_type("free")
    
    # Create dashboard generator
    dashboard_gen = MarkdownDashboardGenerator(project_path, config)
    
    # Generate free dashboard
    print("Generating enhanced free dashboard...")
    
    try:
        dashboard_content = dashboard_gen.generate_dashboard()
        
        # Save to output file
        output_file = os.path.join(project_path, "project-output", "analyses", "enhanced_free_dashboard_test.md")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(dashboard_content)
        
        print(f"✅ Enhanced free dashboard generated successfully!")
        print(f"📄 Saved to: {output_file}")
        print(f"📊 Length: {len(dashboard_content)} characters")
        
        # Show first few lines
        lines = dashboard_content.split('\n')
        print(f"📋 First 10 lines:")
        for i, line in enumerate(lines[:10]):
            print(f"  {i+1:2}: {line}")
        
        # Count sections
        sections = [line for line in lines if line.startswith('##')]
        print(f"🎯 Sections found: {len(sections)}")
        for section in sections:
            print(f"  - {section}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_free_dashboard()
    sys.exit(0 if success else 1)
