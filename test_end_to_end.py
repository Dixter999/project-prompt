#!/usr/bin/env python3
"""
End-to-end test for ProjectPrompt v2.0
"""

import sys
import os
from pathlib import Path

# Add src_new to path
sys.path.insert(0, str(Path(__file__).parent / "src_new"))

from core.analyzer import ProjectAnalyzer
from models.project import ScanConfig, AnalysisConfig
import tempfile

def test_end_to_end():
    """Test complete workflow"""
    print('Testing end-to-end project analysis...')

    # Create a sample project
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some files
        main_py = os.path.join(temp_dir, 'main.py')
        with open(main_py, 'w') as f:
            f.write('#!/usr/bin/env python\nimport sys\n\ndef main():\n    print("Hello World")\n\nif __name__ == "__main__":\n    main()')
        
        req_txt = os.path.join(temp_dir, 'requirements.txt')
        with open(req_txt, 'w') as f:
            f.write('requests==2.28.0\nnumpy==1.21.0\n')
        
        readme_md = os.path.join(temp_dir, 'README.md')
        with open(readme_md, 'w') as f:
            f.write('# Test Project\n\nA simple test project for validation.')
        
        # Create subdirectory
        src_dir = os.path.join(temp_dir, 'src')
        os.makedirs(src_dir)
        
        utils_py = os.path.join(src_dir, 'utils.py')
        with open(utils_py, 'w') as f:
            f.write('def helper_function():\n    return "utility"')
        
        # Run analysis
        scan_config = ScanConfig(max_files=100)
        analysis_config = AnalysisConfig()
        
        analyzer = ProjectAnalyzer(scan_config, analysis_config)
        analysis = analyzer.analyze_project(temp_dir, use_ai=False)
        
        print(f'✓ Project: {analysis.project_name}')
        print(f'✓ Type: {analysis.project_type}')
        print(f'✓ Language: {analysis.main_language}')
        print(f'✓ Files: {analysis.file_count}')
        print(f'✓ Directories: {analysis.directory_count}')
        print(f'✓ Functionalities: {analysis.detected_functionalities}')
        print(f'✓ Status: {analysis.status}')
        
    print('✅ End-to-end test completed successfully!')

if __name__ == "__main__":
    test_end_to_end()
