#!/usr/bin/env python3
"""
Enhanced Verification Script for Anthropic Markdown Generation

This script performs comprehensive verification of Anthropic's markdown generation
capabilities by checking various quality metrics and structure requirements.
"""

import os
import sys
import argparse
import json
import re
import time
import subprocess
import logging
from pathlib import Path
import tempfile
import random

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Terminal colors
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
NC = "\033[0m"  # No Color
BOLD = "\033[1m"

# Base directory and output directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(BASE_DIR, "project-output")
TEMPLATES_DIR = os.path.join(BASE_DIR, "src", "templates")
ANALYZER_SCRIPT = os.path.join(BASE_DIR, "src", "core", "analyze_with_anthropic_direct.py")

def print_section(title):
    """Print a section title with consistent formatting"""
    print(f"\n{BOLD}{'=' * 60}{NC}")
    print(f"{BOLD}{title}{NC}")
    print(f"{BOLD}{'=' * 60}{NC}\n")

def check_environment():
    """Check if the environment is properly configured"""
    
    # Check for API key
    api_key = os.environ.get("anthropic_API")
    if not api_key:
        # Try to read from .env file
        try:
            env_paths = ['.env', os.path.join(OUTPUT_DIR, '.env')]
            for env_path in env_paths:
                if os.path.exists(env_path):
                    with open(env_path, 'r') as f:
                        for line in f:
                            if line.startswith('anthropic_API'):
                                api_key = line.split('=')[1].strip().strip('"\'')
                                break
        except Exception as e:
            logger.error(f"Error reading .env file: {e}")
    
    if not api_key:
        print(f"{RED}❌ Anthropic API key not found{NC}")
        print(f"Please set the 'anthropic_API' environment variable or create a .env file")
        return False
    
    print(f"{GREEN}✅ Anthropic API key found{NC}")
    
    # Check for analyzer script
    if not os.path.exists(ANALYZER_SCRIPT):
        print(f"{RED}❌ Analyzer script not found: {ANALYZER_SCRIPT}{NC}")
        return False
    
    print(f"{GREEN}✅ Analyzer script found{NC}")
    
    return True

def create_test_project(project_type):
    """Create a test project for analysis"""
    print(f"Creating test project of type: {project_type}")
    
    # Use the create_test_project.py script in the same directory
    creator_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "create_test_project.py")
    if not os.path.exists(creator_script):
        print(f"{RED}❌ Project creator script not found: {creator_script}{NC}")
        return None
    
    # Generate a unique project name
    timestamp = int(time.time())
    project_name = f"anthropic_test_{project_type}_{timestamp}"
    
    try:
        cmd = [sys.executable, creator_script, "--type", project_type, "--name", project_name]
        process = subprocess.run(cmd, check=True, text=True, capture_output=True)
        
        # Extract the project path from the output
        output = process.stdout
        match = re.search(r"Project created successfully at: (.+)$", output, re.MULTILINE)
        if match:
            project_path = match.group(1).strip()
            print(f"{GREEN}✅ Created test project at: {project_path}{NC}")
            return project_path
        else:
            print(f"{RED}❌ Failed to extract project path from output:{NC}")
            print(output)
            return None
    except subprocess.CalledProcessError as e:
        print(f"{RED}❌ Failed to create test project:{NC}")
        print(e.stdout)
        print(e.stderr)
        return None

def run_anthropic_analysis(project_path, model="claude-3-haiku-20240307"):
    """Run Anthropic analysis on the project"""
    print(f"Running Anthropic analysis on project: {project_path}")
    
    # Generate output file name
    project_name = os.path.basename(project_path)
    output_file = os.path.join(OUTPUT_DIR, f"anthropic_analysis_{project_name}.md")
    
    # Run analysis
    analyzer_script = ANALYZER_SCRIPT
    
    try:
        cmd = [sys.executable, analyzer_script, project_path, "--output", output_file]
        print(f"Running: {' '.join(cmd)}")
        
        env = os.environ.copy()
        process = subprocess.run(cmd, env=env, text=True, capture_output=True)
        
        if process.returncode != 0:
            print(f"{RED}❌ Analysis failed with exit code: {process.returncode}{NC}")
            print(f"stdout: {process.stdout}")
            print(f"stderr: {process.stderr}")
            return None
        
        if not os.path.exists(output_file):
            print(f"{RED}❌ Output file was not created: {output_file}{NC}")
            return None
        
        print(f"{GREEN}✅ Analysis completed successfully{NC}")
        return output_file
    
    except Exception as e:
        print(f"{RED}❌ Error running analysis: {e}{NC}")
        return None

def analyze_markdown_quality(markdown_file):
    """Analyze the quality of the generated markdown"""
    print(f"Analyzing markdown quality: {markdown_file}")
    
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check basic content
        if not content or len(content) < 100:
            print(f"{RED}❌ Output file is empty or too short: {len(content)} chars{NC}")
            return {
                "success": False,
                "reason": "Empty or too short content",
                "score": 0
            }
        
        # Check for Anthropic-generated content
        if "Sugerencias de Mejora (Generado por Anthropic Claude)" not in content:
            print(f"{RED}❌ No Anthropic-generated content found{NC}")
            return {
                "success": False,
                "reason": "No Anthropic-generated content found",
                "score": 0
            }
        
        # Count sections
        headings = re.findall(r'^#+\s+.+$', content, re.MULTILINE)
        print(f"Document has {len(headings)} headings:")
        for heading in headings[:5]:  # Show first 5 headings
            print(f"  - {heading}")
        if len(headings) > 5:
            print(f"  - ... and {len(headings) - 5} more")
        
        # Count code blocks
        code_blocks = re.findall(r'```[\w]*\n[\s\S]*?\n```', content)
        print(f"Document has {len(code_blocks)} code blocks")
        
        # Check for lists
        lists = re.findall(r'^\s*[*-]\s+.+$', content, re.MULTILINE)
        print(f"Document has {len(lists)} list items")
        
        # Word count as a quality metric
        words = len(content.split())
        print(f"Document word count: {words}")
        
        # Calculate quality score
        quality_score = 0
        max_score = 10
        
        # Scoring based on content richness
        if len(headings) >= 3: quality_score += 1
        if len(headings) >= 6: quality_score += 1
        if len(code_blocks) >= 1: quality_score += 1
        if len(code_blocks) >= 3: quality_score += 1
        if len(lists) >= 5: quality_score += 1
        if len(lists) >= 10: quality_score += 1
        if words >= 300: quality_score += 1
        if words >= 600: quality_score += 1
        
        # Check if important sections are present
        important_sections = [
            r"(Resumen|Propósito|Estructura)",
            r"(Fortalezas|Puntos Fuertes)",
            r"(Debilidades|Áreas de Mejora)",
            r"(Recomendaciones|Sugerencias)"
        ]
        
        section_score = 0
        for pattern in important_sections:
            if re.search(r'#+\s+' + pattern, content, re.IGNORECASE):
                section_score += 0.5
                
        quality_score += section_score
        
        # Calculate percentage
        quality_percentage = (quality_score / max_score) * 100
        
        print(f"Quality score: {quality_score}/{max_score} ({quality_percentage:.1f}%)")
        
        result = {
            "success": quality_score >= 6,
            "score": quality_score,
            "max_score": max_score,
            "percentage": quality_percentage,
            "metrics": {
                "headings": len(headings),
                "code_blocks": len(code_blocks),
                "list_items": len(lists),
                "word_count": words
            }
        }
        
        if result["success"]:
            print(f"{GREEN}✅ Markdown quality is good{NC}")
        else:
            print(f"{RED}❌ Markdown quality is below threshold{NC}")
        
        return result
    
    except Exception as e:
        print(f"{RED}❌ Error analyzing markdown: {e}{NC}")
        return {
            "success": False,
            "reason": str(e),
            "score": 0
        }

def run_verification(project_types=None):
    """Run verification tests on multiple project types"""
    if not project_types:
        project_types = ["web-project", "backend-api", "mobile-app", "data-science", "game-dev", "mixed"]
    
    print_section("ANTHROPIC MARKDOWN GENERATION VERIFICATION")
    
    # Check environment
    if not check_environment():
        return False
    
    results = {}
    overall_success = True
    
    for project_type in project_types:
        print_section(f"TESTING PROJECT TYPE: {project_type.upper()}")
        
        # Create test project
        project_path = create_test_project(project_type)
        if not project_path:
            results[project_type] = {
                "success": False,
                "reason": "Failed to create test project"
            }
            overall_success = False
            continue
        
        # Run Anthropic analysis
        output_file = run_anthropic_analysis(project_path)
        if not output_file:
            results[project_type] = {
                "success": False,
                "reason": "Failed to run Anthropic analysis"
            }
            overall_success = False
            continue
        
        # Analyze markdown quality
        quality_result = analyze_markdown_quality(output_file)
        results[project_type] = quality_result
        
        if not quality_result["success"]:
            overall_success = False
        
        # Small delay to avoid API rate limits
        time.sleep(2)
    
    # Print summary
    print_section("VERIFICATION SUMMARY")
    
    for project_type, result in results.items():
        status = f"{GREEN}PASSED{NC}" if result.get("success") else f"{RED}FAILED{NC}"
        score = result.get("score", "N/A")
        max_score = result.get("max_score", "N/A")
        percentage = result.get("percentage", "N/A")
        if isinstance(percentage, (int, float)):
            percentage = f"{percentage:.1f}%"
        
        print(f"{project_type.upper()}: {status} (Score: {score}/{max_score} - {percentage})")
    
    if overall_success:
        print(f"\n{GREEN}✅ ALL TESTS PASSED: Anthropic markdown generation is working correctly{NC}")
    else:
        print(f"\n{RED}❌ SOME TESTS FAILED: Check the results above for details{NC}")
    
    # Save results to file
    results_file = os.path.join(OUTPUT_DIR, f"verification_results_{int(time.time())}.json")
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": time.time(),
            "overall_success": overall_success,
            "results": results
        }, f, indent=2)
    
    print(f"Results saved to: {results_file}")
    
    return overall_success

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Verify Anthropic markdown generation')
    parser.add_argument('--project-types', nargs='+', choices=[
        "web-project", "backend-api", "mobile-app", "data-science", 
        "cli-tool", "library", "game-dev", "mixed", "all"
    ], default=["web-project"], help='Project types to test')
    parser.add_argument('--check-environment', action='store_true',
                      help='Only check if the environment is properly configured')
    
    args = parser.parse_args()
    
    # If check-environment flag is passed, only check the environment and exit
    if args.check_environment:
        print_section("ENVIRONMENT CHECK")
        success = check_environment()
        return 0 if success else 1
    
    if "all" in args.project_types:
        project_types = ["web-project", "backend-api", "mobile-app", "data-science", "game-dev", "mixed"]
    else:
        project_types = args.project_types
    
    success = run_verification(project_types)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
