"""
Analyze command implementation
"""
import os
import logging
import json

logger = logging.getLogger(__name__)

def analyze_project(path, format_type):
    """
    Analyze a project directory
    
    Args:
        path: Path to the project directory
        format_type: Output format type
    
    Returns:
        dict: Analysis results
    """
    logger.debug(f"Analyzing project at: {path}")
    
    # Initialize results
    results = {
        "project_path": path,
        "file_count": 0,
        "dir_count": 0,
        "languages": {},
        "stats": {}
    }
    
    # Track file extensions
    extensions = {}
    
    # Walk through the project directory
    for root, dirs, files in os.walk(path):
        # Count directories
        results["dir_count"] += len(dirs)
        
        # Process files
        for file in files:
            results["file_count"] += 1
            
            # Count file extensions
            _, ext = os.path.splitext(file)
            if ext:
                ext = ext[1:]  # Remove the dot
                extensions[ext] = extensions.get(ext, 0) + 1
    
    # Map extensions to languages
    for ext, count in extensions.items():
        language = map_extension_to_language(ext)
        if language:
            if language not in results["languages"]:
                results["languages"][language] = {"files": 0}
            results["languages"][language]["files"] += count
    
    # Add stats
    results["stats"] = {
        "total_files": results["file_count"],
        "total_dirs": results["dir_count"],
        "extensions": extensions
    }
    
    logger.debug(f"Analysis completed. Found {results['file_count']} files in {results['dir_count']} directories")
    return results

def map_extension_to_language(ext):
    """
    Map file extension to programming language
    
    Args:
        ext: File extension without the dot
        
    Returns:
        str: Language name or None if unknown
    """
    mapping = {
        "py": "Python",
        "js": "JavaScript",
        "ts": "TypeScript",
        "html": "HTML",
        "css": "CSS",
        "md": "Markdown",
        "json": "JSON",
        "yaml": "YAML",
        "yml": "YAML",
        "java": "Java",
        "c": "C",
        "cpp": "C++",
        "h": "C/C++ Header",
        "rb": "Ruby",
        "go": "Go",
        "rs": "Rust",
        "php": "PHP",
        "sh": "Shell",
        "bat": "Batch",
        "ps1": "PowerShell"
    }
    
    return mapping.get(ext.lower())

def format_output(results, format_type):
    """
    Format analysis results based on format type
    
    Args:
        results: Analysis results
        format_type: Output format type
        
    Returns:
        str: Formatted output
    """
    if format_type == "json":
        return json.dumps(results, indent=2)
    
    elif format_type == "markdown":
        md = f"# Project Analysis: {os.path.basename(results['project_path'])}\n\n"
        md += "## Statistics\n\n"
        md += f"- Total files: {results['file_count']}\n"
        md += f"- Total directories: {results['dir_count']}\n"
        
        md += "\n## Languages\n\n"
        md += "| Language | Files |\n"
        md += "|---------|-------|\n"
        
        for lang, data in results["languages"].items():
            md += f"| {lang} | {data['files']} |\n"
            
        return md
    
    else:  # text format
        text = f"Project Analysis: {os.path.basename(results['project_path'])}\n"
        text += "=" * 50 + "\n"
        text += f"Total files: {results['file_count']}\n"
        text += f"Total directories: {results['dir_count']}\n\n"
        
        text += "Languages:\n"
        for lang, data in results["languages"].items():
            text += f"  {lang}: {data['files']} files\n"
            
        return text

def execute(args, config=None):
    """
    Execute analyze command
    
    Args:
        args: Command arguments
        config: Optional configuration
    """
    logger.info(f"Executing analyze command on: {args.target}")
    
    # Validate target path
    if not os.path.exists(args.target):
        raise FileNotFoundError(f"Target path does not exist: {args.target}")
    
    # Analyze the target
    if os.path.isdir(args.target):
        results = analyze_project(args.target, args.format)
    else:
        raise NotImplementedError("File analysis not implemented yet")
    
    # Format the output
    output = format_output(results, args.format)
    
    # Write or print the output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        logger.info(f"Analysis saved to: {args.output}")
    else:
        print(output)
        
    logger.info("Analysis completed successfully")
