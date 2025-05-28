#!/usr/bin/env python3

# Minimal test for the markdown dashboard fix
import sys
import os

print("Starting test...")

# Add project root to path
sys.path.insert(0, '/mnt/h/Projects/project-prompt')

print("Path added, testing import...")

def test_features_section_fix():
    """Test that _generate_features_section can handle dict format data"""
    print("Testing features section with dict format...")
    
    try:
        print("Importing MarkdownDashboardGenerator...")
        from src.ui.markdown_dashboard import MarkdownDashboardGenerator
        print("Import successful!")
        
        # Create generator instance
        print("Creating generator instance...")
        gen = MarkdownDashboardGenerator('/mnt/h/Projects/project-prompt')
        print("Generator created!")
        
        # Test data in dict format (what get_feature_progress actually returns)
        test_data = {
            'features': {
                'authentication': {
                    'name': 'Authentication System',
                    'completion_estimate': 75,
                    'status': 'In Progress',
                    'files': ['auth.py', 'login.py', 'session.py']
                },
                'dashboard': {
                    'name': 'Dashboard UI',
                    'completion_estimate': 90,
                    'status': 'Nearly Complete',
                    'files': ['dashboard.py', 'templates/dashboard.html']
                }
            }
        }
        
        print("Calling _generate_features_section...")
        # This should not crash anymore
        result = gen._generate_features_section(test_data)
        
        print("✅ SUCCESS: No crash with dict format!")
        print("Generated table:")
        print(result)
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running main test...")
    success = test_features_section_fix()
    print(f"Test result: {'PASS' if success else 'FAIL'}")
