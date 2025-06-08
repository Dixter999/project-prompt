#!/usr/bin/env python3
"""Simple CLI test to debug hanging issue"""

import subprocess
import tempfile
import os
from pathlib import Path

def test_simple_cli():
    """Simple test of CLI functionality"""
    print("Testing CLI help...")
    result = subprocess.run(
        ["projectprompt", "--help"], 
        capture_output=True, 
        text=True,
        timeout=10
    )
    print(f"Help command return code: {result.returncode}")
    print(f"Help contains 'analyze': {'analyze' in result.stdout}")
    
    print("\nTesting CLI version...")
    result = subprocess.run(
        ["projectprompt", "--version"], 
        capture_output=True, 
        text=True,
        timeout=10
    )
    print(f"Version command return code: {result.returncode}")
    print(f"Version contains '2.0': {'2.0' in result.stdout}")
    
    # Test analyze command
    print("\nTesting analyze command...")
    with tempfile.TemporaryDirectory() as temp_dir:
        test_project = Path(temp_dir) / "test_project"
        test_project.mkdir()
        
        # Create test files
        (test_project / "main.py").write_text("print('hello')")
        (test_project / "utils.py").write_text("def helper(): pass")
        
        # Remove API keys from environment
        env = os.environ.copy()
        env.pop("ANTHROPIC_API_KEY", None)
        env.pop("OPENAI_API_KEY", None)
        
        print(f"Running analyze on: {test_project}")
        result = subprocess.run(
            ["projectprompt", "analyze", "."], 
            cwd=str(test_project),
            capture_output=True, 
            text=True,
            env=env,
            timeout=30
        )
        
        print(f"Analyze command return code: {result.returncode}")
        print(f"Analyze stderr: {result.stderr[:200]}")
        print(f"Analyze stdout: {result.stdout[:200]}")
        
        # Check if analysis.json was created
        analysis_file = test_project / "analysis.json"
        print(f"Analysis file exists: {analysis_file.exists()}")
        
        if analysis_file.exists():
            import json
            with open(analysis_file) as f:
                analysis = json.load(f)
            print(f"Analysis contains files: {'files' in analysis}")
            print(f"Number of files: {len(analysis.get('files', []))}")

if __name__ == "__main__":
    test_simple_cli()
