#!/usr/bin/env python3
"""
Test script for ProjectPrompt v2.0 migration validation.
Tests core functionality without requiring AI API keys.
"""

import sys
import os
from pathlib import Path

# Add src_new to path for testing
project_root = Path(__file__).parent
src_new_path = str(project_root / 'src_new')
sys.path.insert(0, src_new_path)

def test_imports():
    """Test that all core modules can be imported."""
    print("Testing imports...")
    
    try:
        # Core modules
        from core.scanner import ProjectScanner
        from core.detector import FunctionalityDetector  
        from core.analyzer import ProjectAnalyzer
        print("✓ Core modules imported successfully")
        
        # AI modules (without requiring API keys)
        from ai.client import BaseAIClient
        print("✓ AI modules imported successfully")
        
        # Models
        from models.project import ProjectAnalysis, ProjectType, AnalysisStatus, ScanConfig, AnalysisConfig
        print("✓ Models imported successfully")
        
        # Utils
        from utils.config import ConfigManager, ProjectPromptConfig
        print("✓ Utils imported successfully")
        
        # Generators
        from generators.suggestions import SuggestionsGenerator
        print("✓ Generators imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_scanner():
    """Test ProjectScanner functionality."""
    print("\nTesting ProjectScanner...")
    
    try:
        from core.scanner import ProjectScanner
        from models.project import ScanConfig
        
        # Use a smaller config to avoid hanging on large directories
        config = ScanConfig(max_files=50)
        scanner = ProjectScanner(config)
        
        # Test on src_new directory (smaller than full project)
        test_dir = Path(__file__).parent / "src_new"
        if not test_dir.exists():
            test_dir = Path(__file__).parent  # Fallback to current directory
        
        structure = scanner.scan_project(str(test_dir))
        
        print(f"✓ Scanned project with {len(structure.files)} files and {len(structure.directories)} directories")
        print(f"✓ Main language detected: {structure.main_language}")
        
        return True
        
    except Exception as e:
        print(f"✗ Scanner test failed: {e}")
        return False


def test_detector():
    """Test FunctionalityDetector functionality."""
    print("\nTesting FunctionalityDetector...")
    
    try:
        from core.detector import FunctionalityDetector
        
        detector = FunctionalityDetector()
        
        # Test with some sample files
        test_files = [
            "setup.py",
            "requirements.txt", 
            "src_new/cli.py",
            "src_new/ai/client.py"
        ]
        
        existing_files = [f for f in test_files if Path(f).exists()]
        
        if existing_files:
            functionalities = detector.detect_functionalities(existing_files)
            print(f"✓ Detected {len(functionalities)} functionalities: {functionalities}")
        else:
            print("✓ Detector initialized successfully (no test files found)")
        
        return True
        
    except Exception as e:
        print(f"✗ Detector test failed: {e}")
        return False


def test_analyzer():
    """Test ProjectAnalyzer functionality."""
    print("\nTesting ProjectAnalyzer...")
    
    try:
        from core.analyzer import ProjectAnalyzer
        from models.project import ScanConfig, AnalysisConfig
        import tempfile
        import os
        
        # Create a simple test project
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_py = os.path.join(temp_dir, 'main.py')
            with open(test_py, 'w') as f:
                f.write('def main():\n    print("Hello World")\n\nif __name__ == "__main__":\n    main()')
            
            test_req = os.path.join(temp_dir, 'requirements.txt')
            with open(test_req, 'w') as f:
                f.write('requests==2.28.0\n')
            
            # Configure analyzer for small test
            scan_config = ScanConfig(max_files=10)
            analysis_config = AnalysisConfig()
            
            analyzer = ProjectAnalyzer(scan_config, analysis_config)
            
            # Test analysis without AI (to avoid API key requirements)
            analysis = analyzer.analyze_project(temp_dir, use_ai=False)
            
            print(f"✓ Analysis completed for project: {analysis.project_name}")
            print(f"✓ Detected type: {analysis.project_type}")
            print(f"✓ Files: {analysis.file_count}, Directories: {analysis.directory_count}")
            
            return True
        
    except Exception as e:
        print(f"✗ Analyzer test failed: {e}")
        return False


def test_config():
    """Test configuration system."""
    print("\nTesting Configuration...")
    
    try:
        from utils.config import ConfigManager, ProjectPromptConfig
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        print(f"✓ Configuration loaded successfully")
        print(f"✓ AI Provider: {config.ai_provider}")
        print(f"✓ Scan max files: {config.scan.max_files}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def test_models():
    """Test data models."""
    print("\nTesting Data Models...")
    
    try:
        from models.project import (
            ProjectAnalysis, ProjectType, AnalysisStatus,
            Suggestion, SuggestionReport, 
            determine_project_type, calculate_suggestion_priority
        )
        
        # Test ProjectAnalysis creation
        analysis = ProjectAnalysis(
            project_name="test_project",
            project_path="/test/path",
            project_type=ProjectType.CLI_TOOL,
            main_language="python",
            file_count=10,
            directory_count=3,
            status=AnalysisStatus.COMPLETED
        )
        
        print(f"✓ ProjectAnalysis created: {analysis.project_name}")
        
        # Test Suggestion creation
        suggestion = Suggestion(
            id="test-1",
            category="Testing",
            title="Test suggestion",
            description="A test suggestion",
            impact="Medium",
            effort="Low",
            priority=5
        )
        
        print(f"✓ Suggestion created: {suggestion.title}")
        
        # Test utility functions
        project_type = determine_project_type(["cli", "python"], "python")
        print(f"✓ Project type determination: {project_type}")
        
        priority = calculate_suggestion_priority("High", "Low", "Security")
        print(f"✓ Priority calculation: {priority}")
        
        return True
        
    except Exception as e:
        print(f"✗ Models test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("ProjectPrompt v2.0 Migration Validation")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_models,
        test_scanner,
        test_detector,
        test_analyzer
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Migration validation successful.")
        return 0
    else:
        print("❌ Some tests failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
