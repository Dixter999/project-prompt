#!/usr/bin/env python3
"""
Script for analyzing a project with ProjectPrompt and generating improvement suggestions 
using the Anthropic API.

Usage:
    python analyze_and_suggest.py /path/to/project -o output.md

This script combines the functionality of project_prompt_cli.py for analyzing the project
and uses the Anthropic API to generate improvement suggestions.
"""

import os
import sys
import json
import argparse
import tempfile
import subprocess
import requests

def run_project_analysis(project_path):
    """Run the project analysis using project_prompt_cli.py"""
    print(f"Analyzing project: {project_path}")
    
    # Create a temporary file for the JSON output
    temp_file = os.path.join(tempfile.gettempdir(), "project_analysis.json")
    
    # Run the analysis command
    cmd = ["python", "project_prompt_cli.py", "analyze", project_path, "--output", temp_file]
    subprocess.run(cmd, check=True)
    
    # Read the generated JSON file
    with open(temp_file, 'r') as f:
        analysis_data = json.load(f)
    
    return analysis_data

def format_analysis_as_markdown(analysis):
    """Format the analysis data as Markdown"""
    project_path = analysis.get('project_path', '')
    project_name = os.path.basename(project_path)
    stats = analysis.get('stats', {})
    languages = analysis.get('languages', {})
    important_files = analysis.get('important_files', {})
    
    markdown = f"""# Analysis of Project: {project_name}

## General Statistics

- **Total files:** {stats.get('total_files', 0)}
- **Total directories:** {stats.get('total_dirs', 0)}
- **Analyzed files:** {stats.get('analyzed_files', 0)}
- **Binary files:** {stats.get('binary_files', 0)}
- **Total size:** {stats.get('total_size_kb', 0):.2f} KB
- **Analysis time:** {analysis.get('scan_time', 0):.2f} seconds

## Language Distribution

| Language | Files | % of Project | Lines |
|----------|-------|--------------|-------|
"""
    
    for lang, data in languages.items():
        files = data.get('files', 0)
        file_percent = (files / stats.get('total_files', 1)) * 100
        lines = data.get('lines', 0)
        markdown += f"| {lang} | {files} | {file_percent:.1f}% | {lines} |\n"
    
    markdown += "\n## Important Files\n\n"
    
    for category, files in important_files.items():
        if files:
            markdown += f"### {category.capitalize()}\n\n"
            for file in files:
                markdown += f"- `{file}`\n"
            markdown += "\n"
    
    return markdown

def get_anthropic_api_key():
    """Get the Anthropic API key from the .env file"""
    api_key = None
    
    try:
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('anthropic_API'):
                        parts = line.split('=', 1)
                        if len(parts) >= 2:
                            api_key = parts[1].strip().strip('"\'')
    except Exception as e:
        print(f"Error reading .env file: {e}")
    
    return api_key

def get_improvement_suggestions(analysis_markdown, project_path):
    """Use Anthropic API to get improvement suggestions"""
    print("\nGenerating improvement suggestions with Anthropic API...")
    
    # Get the API key
    api_key = get_anthropic_api_key()
    if not api_key:
        print("Error: Anthropic API key not found in .env file")
        return None
        
    # Create the prompt for Claude
    prompt = f"""Based on the following software project analysis, provide:
1. A summary of the project structure and purpose
2. Strengths identified in the code organization
3. Weaknesses or areas for improvement
4. Specific recommendations to improve structure, organization, and code quality
5. Suggestions for documentation

Please present your analysis in Markdown format with well-defined sections.

PROJECT ANALYSIS:
{analysis_markdown}

ADDITIONAL INFORMATION:
- Project path: {project_path}

Provide a helpful and constructive analysis that can help improve this project.
"""

    # Make the API request
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 4000,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            print(f"Error from Anthropic API: {response.status_code} - {response.text}")
            return None
            
        # Process the response
        result = response.json()
        content = result.get("content", [])
        
        # Extract text from the content
        text_parts = []
        for item in content:
            if item.get("type") == "text":
                text_parts.append(item.get("text", ""))
                
        suggestions = "".join(text_parts).strip()
        print("\n✅ Improvement suggestions generated successfully!")
        return suggestions
        
    except Exception as e:
        print(f"\nError calling Anthropic API: {e}")
        return None

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Analyze a project and generate improvement suggestions using Anthropic API')
    parser.add_argument('project_path', help='Path to the project to analyze')
    parser.add_argument('-o', '--output', help='Output file for the analysis report')
    args = parser.parse_args()
    
    # Validate the project path
    if not os.path.isdir(args.project_path):
        print(f"Error: {args.project_path} is not a valid directory")
        sys.exit(1)
    
    try:
        # Run the project analysis
        analysis = run_project_analysis(args.project_path)
        
        # Format the analysis as Markdown
        markdown = format_analysis_as_markdown(analysis)
        
        # Get improvement suggestions from Anthropic
        suggestions = get_improvement_suggestions(markdown, args.project_path)
        
        # Combine the analysis and suggestions
        if suggestions:
            full_report = f"{markdown}\n\n## Improvement Suggestions (Generated by Anthropic Claude)\n\n{suggestions}"
        else:
            full_report = markdown
        
        # Output the result
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(full_report)
            print(f"\nComplete report saved to: {args.output}")
        else:
            print("\n" + "=" * 50)
            print("PROJECT ANALYSIS REPORT")
            print("=" * 50)
            print(full_report)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
