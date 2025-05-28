#!/usr/bin/env python3

from src.ui.markdown_dashboard import MarkdownDashboardGenerator

# Test the fix
gen = MarkdownDashboardGenerator('/mnt/h/Projects/project-prompt')

# Test with dict format data (what actually gets returned)
test_data = {
    'features': {
        'auth': {
            'name': 'Authentication', 
            'completion_estimate': 80, 
            'files': ['auth.py', 'login.py']
        },
        'ui': {
            'name': 'User Interface',
            'completion_estimate': 60,
            'files': ['dashboard.py', 'markdown_dashboard.py']
        }
    }
}

try:
    result = gen._generate_features_section(test_data)
    print('SUCCESS: No error with dict format!')
    print('Generated output:')
    print(result)
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
