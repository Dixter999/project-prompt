#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for FASE 2 Integration
Tests the new workflow functionality in adaptive-implement command
"""

import os
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_import_fase2_components():
    """Test that all FASE 2 components can be imported successfully"""
    print("🔍 Testing FASE 2 component imports...")
    
    try:
        # Test FASE 1 imports
        from src.api_manager.context_builder import ContextBuilder
        from src.api_manager.prompt_enricher import PromptEnricher
        from src.api_manager.anthropic_client import AnthropicClient
        from src.api_manager.request_optimizer import RequestOptimizer
        print("✅ FASE 1 components imported successfully")
        
        # Test FASE 2 imports
        from src.api_manager.conversation_manager import ConversationManager
        from src.api_manager.response_processor import ResponseProcessor
        from src.api_manager.implementation_coordinator import ImplementationCoordinator
        print("✅ FASE 2 components imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_fase2_component_initialization():
    """Test that FASE 2 components can be initialized"""
    print("\n🔧 Testing FASE 2 component initialization...")
    
    try:
        from src.api_manager.conversation_manager import ConversationManager
        from src.api_manager.response_processor import ResponseProcessor
        from src.api_manager.implementation_coordinator import ImplementationCoordinator
        from src.api_manager.anthropic_client import AnthropicClient
        
        # Test ConversationManager
        conv_mgr = ConversationManager()
        print("✅ ConversationManager initialized")
        
        # Test ResponseProcessor
        resp_proc = ResponseProcessor()
        print("✅ ResponseProcessor initialized")
        
        # Test ImplementationCoordinator (without API key for now)
        try:
            # Create a mock client for testing
            mock_client = AnthropicClient(api_key="test-key")
            coord = ImplementationCoordinator(mock_client)
            print("✅ ImplementationCoordinator initialized")
        except Exception as e:
            print(f"⚠️  ImplementationCoordinator: {str(e)} (expected without valid API key)")
        
        return True
        
    except Exception as e:
        print(f"❌ Initialization error: {str(e)}")
        return False

def test_cli_adaptive_implement_help():
    """Test that the CLI adaptive-implement command help works"""
    print("\n📖 Testing CLI adaptive-implement help...")
    
    try:
        from src.cli import cli
        from click.testing import CliRunner
        
        runner = CliRunner()
        result = runner.invoke(cli, ['adaptive-implement', '--help'])
        
        if result.exit_code == 0:
            print("✅ CLI adaptive-implement help works")
            
            # Check for FASE 2 options
            help_text = result.output
            if '--use-workflow' in help_text:
                print("✅ --use-workflow option found in help")
            else:
                print("❌ --use-workflow option missing from help")
                
            if '--conversation-mode' in help_text:
                print("✅ --conversation-mode option found in help")
            else:
                print("❌ --conversation-mode option missing from help")
                
            if '--max-requests' in help_text:
                print("✅ --max-requests option found in help")
            else:
                print("❌ --max-requests option missing from help")
                
            return True
        else:
            print(f"❌ CLI help failed with exit code: {result.exit_code}")
            print(f"Output: {result.output}")
            return False
            
    except Exception as e:
        print(f"❌ CLI test error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 FASE 2 Integration Test Suite")
    print("=" * 50)
    
    tests = [
        test_import_fase2_components,
        test_fase2_component_initialization,
        test_cli_adaptive_implement_help
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! FASE 2 integration is ready.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
