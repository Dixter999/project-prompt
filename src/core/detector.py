#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simplified FunctionalityDetector for the new architecture.

Detects common project functionalities without complex configurations.
"""

import os
import re
from typing import Dict, List, Optional, Any

try:
    from models.project import FunctionalityDetection
except ImportError:
    # Fallback for direct execution
    from ..models.project import FunctionalityDetection

# Simplified patterns for functionality detection
SIMPLE_PATTERNS = {
    'authentication': {
        'files': ['auth', 'login', 'user', 'jwt', 'oauth', 'security'],
        'keywords': ['authenticate', 'login', 'jwt', 'auth', 'password', 'token']
    },
    'database': {
        'files': ['db', 'model', 'schema', 'migration', 'orm'],
        'keywords': ['database', 'model', 'query', 'schema', 'table', 'collection']
    },
    'api': {
        'files': ['api', 'controller', 'route', 'endpoint', 'service'],
        'keywords': ['api', 'endpoint', 'controller', 'route', 'rest', 'graphql']
    },
    'frontend': {
        'files': ['component', 'view', 'page', 'ui', 'react', 'vue'],
        'keywords': ['component', 'render', 'template', 'view', 'state', 'props']
    },
    'testing': {
        'files': ['test', 'spec', '__tests__', 'cypress', 'jest'],
        'keywords': ['test', 'spec', 'assert', 'expect', 'describe', 'it']
    },
    'configuration': {
        'files': ['config', 'settings', '.env', 'docker', 'compose'],
        'keywords': ['config', 'environment', 'settings', 'docker', 'deploy']
    }
}

# Minimum confidence threshold
CONFIDENCE_THRESHOLD = 2


class FunctionalityDetector:
    """Simplified detector for common functionalities."""
    
    def __init__(self):
        """Initialize detector."""
        self.results = {}
    
    def detect_functionalities(self, file_paths: List[str]) -> List[FunctionalityDetection]:
        """
        Detect functionalities in the project.
        
        Args:
            file_paths: List of file paths to analyze
            
        Returns:
            List of detected functionalities
        """
        scores = {}
        evidence = {}
        patterns_matched = {}
        
        # Initialize scores
        for functionality in SIMPLE_PATTERNS:
            scores[functionality] = 0
            evidence[functionality] = []
            patterns_matched[functionality] = []
        
        # Analyze file paths and names
        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            
            # Check file names and paths
            for func_name, patterns in SIMPLE_PATTERNS.items():
                for pattern in patterns['files']:
                    if pattern.lower() in file_path.lower() or pattern.lower() in file_name.lower():
                        scores[func_name] += 1
                        if file_path not in evidence[func_name]:
                            evidence[func_name].append(file_path)
                        if pattern not in patterns_matched[func_name]:
                            patterns_matched[func_name].append(f"file:{pattern}")
            
            # Analyze file content for important files
            if self._is_analyzable_file(file_path):
                self._analyze_file_content(file_path, scores, evidence, patterns_matched)
        
        # Convert to FunctionalityDetection objects
        detected_functionalities = []
        for functionality, score in scores.items():
            if score >= CONFIDENCE_THRESHOLD:
                confidence = min(1.0, score / (CONFIDENCE_THRESHOLD * 2))
                
                detection = FunctionalityDetection(
                    name=functionality,
                    confidence=confidence,
                    description=self._get_functionality_description(functionality),
                    evidence_files=evidence[functionality][:5],  # Limit to top 5
                    patterns_matched=patterns_matched[functionality]
                )
                detected_functionalities.append(detection)
        
        return detected_functionalities
    
    def _is_analyzable_file(self, file_path: str) -> bool:
        """Check if file should be analyzed for content."""
        # Only analyze text files, avoid binary and large files
        analyzable_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.cs',
            '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            '.html', '.css', '.scss', '.json', '.yaml', '.yml', '.toml',
            '.md', '.txt', '.rst', '.sql', '.sh', '.bash'
        }
        
        ext = os.path.splitext(file_path)[1].lower()
        return ext in analyzable_extensions
    
    def _analyze_file_content(self, file_path: str, scores: dict, evidence: dict, patterns_matched: dict):
        """Analyze file content for keywords."""
        try:
            if not os.path.exists(file_path):
                return
                
            # Check file size to avoid processing huge files
            if os.path.getsize(file_path) > 1024 * 1024:  # 1MB limit
                return
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check keywords in content
            for func_name, patterns in SIMPLE_PATTERNS.items():
                for keyword in patterns['keywords']:
                    if re.search(r'\b' + re.escape(keyword) + r'\b', content, re.IGNORECASE):
                        scores[func_name] += 0.5
                        if file_path not in evidence[func_name]:
                            evidence[func_name].append(file_path)
                        pattern_key = f"keyword:{keyword}"
                        if pattern_key not in patterns_matched[func_name]:
                            patterns_matched[func_name].append(pattern_key)
        except:
            # Ignore read errors
            pass
    
    def _get_functionality_description(self, functionality: str) -> str:
        """Get description for functionality."""
        descriptions = {
            'authentication': 'User authentication and authorization features',
            'database': 'Database operations and data modeling',
            'api': 'API endpoints and web service functionality',
            'frontend': 'User interface and frontend components',
            'testing': 'Test suites and testing infrastructure',
            'configuration': 'Configuration management and deployment setup'
        }
        return descriptions.get(functionality, f'{functionality.title()} functionality')
    
    def get_functionality_summary(self) -> str:
        """Generate summary of detected functionalities."""
        if not self.results:
            return "No functionality analysis has been performed."
        
        main_funcs = self.results.get('main_functionalities', [])
        if not main_funcs:
            return "No main functionalities detected."
        
        summary = f"Detected functionalities ({len(main_funcs)}):\n"
        for func in main_funcs:
            data = self.results['detected'][func]
            summary += f"- {func.title()}: {data['confidence']}% confidence\n"
        
        return summary
