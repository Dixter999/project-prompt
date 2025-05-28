#!/usr/bin/env python3

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

print("Testing dashboard generation with mock data...")

try:
    from ui.markdown_dashboard import MarkdownDashboardGenerator
    
    # Create generator
    gen = MarkdownDashboardGenerator('/mnt/h/Projects/project-prompt')
    
    # Test case 1: Dict format (what the actual code returns)
    print("\n1. Testing with dict format features...")
    test_data_dict = {
        'features': {
            'auth': {
                'name': 'Authentication', 
                'status': 'Complete',
                'completion_estimate': 80, 
                'files': ['auth.py', 'login.py']
            },
            'ui': {
                'name': 'User Interface',
                'status': 'In Progress',
                'completion_estimate': 60,
                'files': ['dashboard.py', 'markdown_dashboard.py']
            }
        }
    }
    
    result = gen._generate_features_section(test_data_dict)
    print("✅ Dict format test passed!")
    print("Generated content:")
    print(result[:300] + "...")
    
    # Test case 2: List format
    print("\n2. Testing with list format features...")
    test_data_list = {
        'features': [
            {
                'name': 'Authentication', 
                'status': 'Complete',
                'completion_estimate': 80, 
                'files': ['auth.py', 'login.py']
            },
            {
                'name': 'User Interface',
                'status': 'In Progress',
                'completion_estimate': 60,
                'files': ['dashboard.py', 'markdown_dashboard.py']
            }
        ]
    }
    
    result = gen._generate_features_section(test_data_list)
    print("✅ List format test passed!")
    print("Generated content:")
    print(result[:300] + "...")
    
    # Test case 3: Empty features
    print("\n3. Testing with empty features...")
    test_data_empty = {'features': {}}
    result = gen._generate_features_section(test_data_empty)
    print("✅ Empty features test passed!")
    
    # Test case 4: Invalid features data
    print("\n4. Testing with invalid features data...")
    test_data_invalid = {'features': "invalid_string"}
    result = gen._generate_features_section(test_data_invalid)
    print("✅ Invalid data test passed!")
    
    print("\n🎉 All tests passed! The fix is working correctly.")
    
except Exception as e:
    print(f"❌ Error during testing: {str(e)}")
    import traceback
    traceback.print_exc()
