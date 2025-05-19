#!/usr/bin/env python3
"""
Script to verify Anthropic's markdown generation capabilities.
This script checks if the output from Anthropic for project analysis is properly formatted
and contains all the expected sections.
"""

import os
import sys
import argparse
import json
import re
import subprocess
from pathlib import Path

# Set the output directory for all generated files
OUTPUT_DIR = "/mnt/h/Projects/project-prompt/test-projects"

def check_anthropic_env():
    """Check if Anthropic API key is configured."""
    api_key = os.getenv("anthropic_API")
    if not api_key:
        # Try to read from .env file
        try:
            env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('anthropic_API'):
                            api_key = line.split('=')[1].strip().strip('"\'')
                            break
        except Exception as e:
            print(f"Error reading .env file: {e}")
    
    if not api_key:
        print("❌ Anthropic API key not found")
        print("Please set the 'anthropic_API' environment variable or add it to a .env file")
        return False
    
    print(f"✅ Found Anthropic API key: {api_key[:4]}...{api_key[-4:]}")
    return True

def analyze_project(project_path, output_file):
    """Run the project analysis and generate markdown with Anthropic."""
    # Make sure the project path exists
    if not os.path.isdir(project_path):
        print(f"❌ Project path does not exist: {project_path}")
        return False
    
    # Run the analyzer with Anthropic integration
    cmd = [
        "python", 
        "analyze_with_anthropic_direct.py", 
        project_path, 
        "--output", 
        output_file
    ]
    
    print(f"📊 Running analysis: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        
        if not os.path.exists(output_file):
            print(f"❌ Output file was not created: {output_file}")
            return False
            
        print(f"✅ Analysis completed and saved to: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running analysis: {e}")
        return False

def verify_markdown_output(output_file):
    """Verify that the markdown output has the expected structure and content."""
    if not os.path.exists(output_file):
        print(f"❌ Output file not found: {output_file}")
        return False
    
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if it's valid markdown content
        if not content or len(content) < 100:
            print(f"❌ Output file is empty or too short: {len(content)} chars")
            return False
        
        # Check for expected sections
        expected_sections = [
            # Basic analysis sections
            r"# Análisis del Proyecto",
            r"## Estadísticas Generales",
            r"## Distribución de Lenguajes",
            
            # Anthropic generated sections (may vary)
            r"## (Resumen|Propósito|Estructura)",
            r"## (Fortalezas|Puntos Fuertes)",
            r"## (Debilidades|Áreas de Mejora)",
            r"## (Recomendaciones|Sugerencias)"
        ]
        
        missing_sections = []
        for pattern in expected_sections:
            if not re.search(pattern, content, re.IGNORECASE):
                missing_sections.append(pattern)
        
        if missing_sections:
            print(f"❌ Missing expected sections in the markdown output:")
            for section in missing_sections:
                print(f"  - {section}")
            return False
        
        # Check if Anthropic added its content
        if "Sugerencias de Mejora (Generado por Anthropic Claude)" not in content:
            print("❌ Anthropic generated content not found")
            return False
        
        print("✅ Markdown output has all expected sections")
        
        # Count headings to estimate structure quality
        heading_count = len(re.findall(r'^#+\s+.+$', content, re.MULTILINE))
        print(f"📝 Document has {heading_count} headings")
        
        # Count code blocks to check for code examples
        code_block_count = len(re.findall(r'```[\w]*\n[\s\S]*?\n```', content))
        print(f"💻 Document has {code_block_count} code blocks")
        
        return True
    
    except Exception as e:
        print(f"❌ Error verifying markdown output: {e}")
        return False

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Verify Anthropic\'s markdown generation')
    parser.add_argument('project_path', nargs='?', default='.',
                        help='Path to the project to analyze (default: current directory)')
    parser.add_argument('-o', '--output', default='anthropic_analysis_output.md',
                        help='Output file for the analysis (default: anthropic_analysis_output.md)')
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Make sure output file is in the proper directory
    if not os.path.isabs(args.output):
        args.output = os.path.join(OUTPUT_DIR, args.output)
    
    print("=" * 70)
    print("ANTHROPIC MARKDOWN GENERATION VERIFICATION")
    print("=" * 70)
    
    # Step 1: Check if Anthropic API key is configured
    if not check_anthropic_env():
        sys.exit(1)
    
    # Step 2: Run project analysis with Anthropic
    if not analyze_project(args.project_path, args.output):
        sys.exit(1)
    
    # Step 3: Verify markdown output
    if not verify_markdown_output(args.output):
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("✅ VERIFICATION SUCCESSFUL")
    print("=" * 70)
    print(f"Anthropic markdown generation is working correctly")
    print(f"Output saved to: {os.path.abspath(args.output)}")
    print("=" * 70)

if __name__ == "__main__":
    main()
