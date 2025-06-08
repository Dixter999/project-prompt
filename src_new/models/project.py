"""
Consolidated data models for ProjectPrompt.
Contains all core data structures used throughout the application.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from enum import Enum
from pathlib import Path


@dataclass
class ScanConfig:
    """Configuration for project scanning."""
    max_files: int = 1000
    max_file_size_mb: float = 5.0
    ignore_dirs: List[str] = field(default_factory=lambda: [
        '.git', '.svn', '.hg', '.idea', '.vscode', '__pycache__',
        'node_modules', 'venv', '.env', 'env', '.venv', 'ENV',
        'build', 'dist', 'target', 'bin', 'obj',
        '.pytest_cache', '.coverage', 'htmlcov',
        '.next', '.nuxt', '.output',
    ])
    ignore_files: List[str] = field(default_factory=lambda: [
        '.DS_Store', 'Thumbs.db', '*.pyc', '*.pyo', '*.pyd',
        '*.so', '*.dylib', '*.dll', '*.exe', '*.bin',
        '*.cache', '*.log', '*.tmp', '*.temp',
    ])


@dataclass
class AnalysisConfig:
    """Configuration for project analysis."""
    include_ai_context: bool = False
    max_context_files: int = 50
    functionality_threshold: float = 0.5
    detect_patterns: bool = True
    include_file_content: bool = False


@dataclass
class ExportConfig:
    """Configuration for exporting results."""
    format: str = "json"  # json, yaml, markdown
    include_metadata: bool = True
    compress_output: bool = False
    output_directory: str = "./output"


class ProjectType(Enum):
    """Project type enumeration."""
    WEB_APPLICATION = "web_application"
    API = "api"
    CLI_TOOL = "cli_tool"
    LIBRARY = "library"
    DESKTOP_APP = "desktop_app"
    MOBILE_APP = "mobile_app"
    DATA_SCIENCE = "data_science"
    GAME = "game"
    UNKNOWN = "unknown"


class AnalysisStatus(Enum):
    """Analysis status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class FileInfo:
    """Information about a scanned file."""
    path: str
    name: str
    extension: str
    size: int
    language: str
    is_important: bool = False
    functionality_score: float = 0.0
    content_preview: Optional[str] = None


@dataclass
class DirectoryInfo:
    """Information about a scanned directory."""
    path: str
    name: str
    file_count: int
    subdirectory_count: int
    total_size: int
    main_language: Optional[str] = None


@dataclass
class ProjectStructure:
    """Complete project structure information."""
    root_path: str
    files: List[FileInfo] = field(default_factory=list)
    directories: List[DirectoryInfo] = field(default_factory=list)
    total_files: int = 0
    total_directories: int = 0
    total_size: int = 0
    languages: Dict[str, int] = field(default_factory=dict)
    main_language: Optional[str] = None


@dataclass
class FunctionalityDetection:
    """Detected functionality information."""
    name: str
    confidence: float
    description: str
    evidence_files: List[str] = field(default_factory=list)
    patterns_matched: List[str] = field(default_factory=list)


@dataclass
class ProjectAnalysis:
    """Complete project analysis results."""
    # Basic info
    project_name: str
    project_path: str
    project_type: ProjectType = ProjectType.UNKNOWN
    main_language: str = "unknown"
    
    # Structure info
    file_count: int = 0
    directory_count: int = 0
    total_size: int = 0
    
    # Content analysis
    detected_functionalities: List[str] = field(default_factory=list)
    functionality_details: List[FunctionalityDetection] = field(default_factory=list)
    important_files: List[str] = field(default_factory=list)
    
    # Phase 3: File organization
    files: List[FileInfo] = field(default_factory=list)
    groups: Dict[str, List[str]] = field(default_factory=dict)
    file_mappings: List[Any] = field(default_factory=list)  # Will be FileGroupMapping objects
    dependency_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # AI context
    ai_context: Optional[str] = None
    context_files: List[str] = field(default_factory=list)
    
    # Analysis metadata
    analysis_date: Optional[str] = None
    analysis_duration: Optional[float] = None
    status: AnalysisStatus = AnalysisStatus.PENDING


@dataclass
class AIResponse:
    """AI service response."""
    provider: str
    model: str
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    response_time: Optional[float] = None


@dataclass
class Suggestion:
    """Project improvement suggestion."""
    id: str
    category: str
    title: str
    description: str
    impact: str  # High, Medium, Low
    effort: str  # High, Medium, Low
    priority: int  # 1-10
    implementation_steps: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    estimated_time: Optional[str] = None


@dataclass
class SuggestionReport:
    """Complete suggestions report."""
    project_name: str
    project_path: str
    suggestions: List[Suggestion] = field(default_factory=list)
    summary: str = ""
    generated_date: Optional[str] = None
    ai_provider: Optional[str] = None
    
    # Statistics
    total_suggestions: int = 0
    high_priority_count: int = 0
    medium_priority_count: int = 0
    low_priority_count: int = 0
    categories: Set[str] = field(default_factory=set)


@dataclass
class ProjectReport:
    """Complete project analysis and suggestions report."""
    # Project identification
    project_name: str
    project_path: str
    report_id: str
    generated_date: str
    
    # Analysis results
    analysis: ProjectAnalysis
    suggestions: SuggestionReport
    
    # Configuration used
    config: Optional[Dict[str, Any]] = None
    
    # Export metadata
    export_format: Optional[str] = None
    export_path: Optional[str] = None


# Utility functions for working with models

def create_file_info(file_path: Path, language: str = "unknown") -> FileInfo:
    """Create FileInfo from a Path object."""
    try:
        stat = file_path.stat()
        return FileInfo(
            path=str(file_path),
            name=file_path.name,
            extension=file_path.suffix,
            size=stat.st_size,
            language=language
        )
    except (OSError, ValueError):
        return FileInfo(
            path=str(file_path),
            name=file_path.name,
            extension=file_path.suffix,
            size=0,
            language=language
        )


def create_directory_info(dir_path: Path) -> DirectoryInfo:
    """Create DirectoryInfo from a Path object."""
    return DirectoryInfo(
        path=str(dir_path),
        name=dir_path.name,
        file_count=0,
        subdirectory_count=0,
        total_size=0
    )


def determine_project_type(functionalities: List[str], main_language: str) -> ProjectType:
    """Determine project type based on detected functionalities and language."""
    func_set = set(f.lower() for f in functionalities)
    
    # Web application patterns
    if any(f in func_set for f in ['web', 'http', 'server', 'frontend', 'backend']):
        return ProjectType.WEB_APPLICATION
    
    # API patterns
    if any(f in func_set for f in ['api', 'rest', 'graphql', 'endpoint']):
        return ProjectType.API
    
    # CLI tool patterns
    if any(f in func_set for f in ['cli', 'command', 'terminal']):
        return ProjectType.CLI_TOOL
    
    # Data science patterns
    if any(f in func_set for f in ['data', 'ml', 'ai', 'analysis', 'jupyter']):
        return ProjectType.DATA_SCIENCE
    
    # Desktop app patterns
    if any(f in func_set for f in ['gui', 'desktop', 'qt', 'tkinter', 'electron']):
        return ProjectType.DESKTOP_APP
    
    # Mobile app patterns
    if any(f in func_set for f in ['mobile', 'android', 'ios', 'react-native', 'flutter']):
        return ProjectType.MOBILE_APP
    
    # Game patterns
    if any(f in func_set for f in ['game', 'unity', 'godot', 'pygame']):
        return ProjectType.GAME
    
    # Library patterns (fallback for certain languages)
    if main_language.lower() in ['python', 'javascript', 'typescript', 'java', 'c++']:
        if not func_set or len(func_set) == 1:
            return ProjectType.LIBRARY
    
    return ProjectType.UNKNOWN


def calculate_suggestion_priority(impact: str, effort: str, category: str) -> int:
    """Calculate numerical priority based on impact, effort, and category."""
    # Base priority from impact
    impact_scores = {"High": 8, "Medium": 5, "Low": 2}
    base_score = impact_scores.get(impact, 2)
    
    # Adjust for effort (lower effort = higher priority)
    effort_adjustments = {"Low": 2, "Medium": 0, "High": -2}
    effort_adjustment = effort_adjustments.get(effort, 0)
    
    # Adjust for category
    category_bonuses = {
        "Security": 3,
        "Performance": 2,
        "Code Quality": 1,
        "Testing": 1,
        "Documentation": 0,
        "Architecture": 1
    }
    category_bonus = category_bonuses.get(category, 0)
    
    # Calculate final priority (1-10 scale)
    priority = base_score + effort_adjustment + category_bonus
    return max(1, min(10, priority))


def merge_project_analyses(analyses: List[ProjectAnalysis]) -> ProjectAnalysis:
    """Merge multiple project analyses into one."""
    if not analyses:
        raise ValueError("Cannot merge empty list of analyses")
    
    if len(analyses) == 1:
        return analyses[0]
    
    # Use first analysis as base
    merged = analyses[0]
    
    # Merge data from other analyses
    for analysis in analyses[1:]:
        merged.file_count += analysis.file_count
        merged.directory_count += analysis.directory_count
        merged.total_size += analysis.total_size
        
        # Merge functionalities (deduplicate)
        all_funcs = set(merged.detected_functionalities + analysis.detected_functionalities)
        merged.detected_functionalities = list(all_funcs)
        
        # Merge important files (deduplicate)
        all_files = set(merged.important_files + analysis.important_files)
        merged.important_files = list(all_files)
    
    return merged
