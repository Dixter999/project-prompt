"""
Rules Manager for ProjectPrompt

This module handles loading, parsing, and caching of project-specific rules defined 
in markdown files. It supports structured rule parsing and validation for different categories.
"""

import os
import re
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
import time
from functools import lru_cache
from dataclasses import dataclass

# Configure logger
logger = logging.getLogger(__name__)

@dataclass
class RuleItem:
    """Represents a single rule item with its content and metadata"""
    content: str
    priority: Optional[str] = None  # mandatory, recommended, optional
    category: Optional[str] = None
    line_number: int = 0

@dataclass
class RuleGroup:
    """Represents a group of rules under the same category and priority"""
    rules: List[RuleItem]
    priority: Optional[str] = None

@dataclass
class RuleCategory:
    """Represents a category of rules with different priority groups"""
    name: str
    groups: Dict[str, RuleGroup]  # Priority -> RuleGroup mapping
    description: Optional[str] = None

class RulesManager:
    """
    Manages loading, parsing, and accessing project-specific rules.
    
    This class handles:
    - Searching for rules files in project directories
    - Parsing markdown rules into structured format
    - Caching rules for performance
    - Providing access to rules by category
    - Validating rules syntax and structure
    """
    
    # Default rule file name
    DEFAULT_RULES_FILENAME = "project-prompt-rules.md"
    
    # Cache expiration time (in seconds)
    CACHE_EXPIRATION = 300  # 5 minutes
    
    # Known rule categories
    KNOWN_CATEGORIES = {
        "project overview", 
        "technology constraints", 
        "architecture rules", 
        "code style requirements", 
        "testing requirements", 
        "ai analysis preferences", 
        "documentation standards", 
        "custom analysis rules", 
        "file organization", 
        "naming conventions"
    }
    
    # Known rule priorities
    KNOWN_PRIORITIES = {"mandatory", "recommended", "optional"}
    
    def __init__(self, project_root: str = None):
        """
        Initialize the RulesManager
        
        Args:
            project_root: The root directory of the project. If not provided,
                         the current working directory is used.
        """
        self.project_root = project_root or os.getcwd()
        self.rules_file_path = None
        self.last_loaded = 0
        self.rules: Dict[str, RuleCategory] = {}
        self.validation_errors: List[str] = []
        
        # Try to load rules automatically at initialization
        self._load_rules()
    
    def _find_rules_file(self) -> Optional[str]:
        """
        Search for rules file in project directories
        
        Returns:
            The path to the rules file if found, None otherwise
        """
        # Possible locations for the rules file, in order of priority
        possible_locations = [
            # Project root
            os.path.join(self.project_root, self.DEFAULT_RULES_FILENAME),
            
            # project-output directory
            os.path.join(self.project_root, "project-output", self.DEFAULT_RULES_FILENAME),
            
            # .projectprompt directory (if exists)
            os.path.join(self.project_root, ".projectprompt", self.DEFAULT_RULES_FILENAME)
        ]
        
        # Return the first file that exists
        for location in possible_locations:
            if os.path.isfile(location):
                logger.info(f"Found rules file at: {location}")
                return location
        
        logger.info("No rules file found in the project")
        return None
    
    def _load_rules(self, force_reload: bool = False) -> bool:
        """
        Load rules from file if it exists and has been modified since last load
        
        Args:
            force_reload: Force reload even if cache hasn't expired
            
        Returns:
            True if rules were loaded, False otherwise
        """
        # Find rules file if we don't have one already
        if not self.rules_file_path:
            self.rules_file_path = self._find_rules_file()
            if not self.rules_file_path:
                return False
        
        # Check if we need to reload based on cache expiration or file modification
        current_time = time.time()
        file_mtime = os.path.getmtime(self.rules_file_path) if self.rules_file_path else 0
        
        if (not force_reload and 
            self.last_loaded > 0 and
            current_time - self.last_loaded < self.CACHE_EXPIRATION and
            file_mtime < self.last_loaded):
            # Cache is still valid, no need to reload
            return True
        
        # Load and parse the rules file
        try:
            with open(self.rules_file_path, "r", encoding="utf-8") as file:
                content = file.read()
            
            # Parse the rules and update cache timestamp
            self.rules = {}
            self.validation_errors = []
            self._parse_rules(content)
            self.last_loaded = current_time
            
            # Validate rules after parsing
            self.validate_rules()
            
            return True
        except Exception as e:
            logger.error(f"Error loading rules file: {e}")
            return False
    
    def _parse_rules(self, content: str) -> None:
        """
        Parse markdown rules content into structured format
        
        Args:
            content: The markdown content to parse
        """
        if not content.strip():
            return
        
        # Split content into lines for processing
        lines = content.split('\n')
        
        current_category = None
        current_priority = None
        current_section = None
        
        # Line by line parsing
        for line_num, line in enumerate(lines, 1):
            # Skip empty lines
            if not line.strip():
                continue
            
            # Handle headers to determine category and priority
            if line.startswith('#'):
                # Count the number of # to determine the header level
                header_level = len(line) - len(line.lstrip('#'))
                header_text = line.lstrip('#').strip().lower()
                
                if header_level == 1:
                    # Main title, skip
                    continue
                elif header_level == 2:
                    # Category level
                    current_category = header_text
                    current_priority = None
                    self.rules[current_category] = RuleCategory(
                        name=current_category,
                        groups={}
                    )
                elif header_level == 3:
                    # This could be a subcategory or priority
                    if header_text.lower() in self.KNOWN_PRIORITIES:
                        current_priority = header_text.lower()
                        if current_category and current_category in self.rules:
                            if current_priority not in self.rules[current_category].groups:
                                self.rules[current_category].groups[current_priority] = RuleGroup(
                                    rules=[],
                                    priority=current_priority
                                )
                    else:
                        # This is a subcategory within the current category
                        # For now we treat it as part of the same category
                        current_section = header_text
            
            # Handle rule items (bullet points)
            elif line.strip().startswith('-') or line.strip().startswith('*'):
                rule_text = line.strip()[1:].strip()
                if current_category and current_category in self.rules:
                    # Determine where to add the rule
                    if current_priority and current_priority in self.rules[current_category].groups:
                        # Add to specific priority group
                        self.rules[current_category].groups[current_priority].rules.append(
                            RuleItem(
                                content=rule_text,
                                priority=current_priority,
                                category=current_category,
                                line_number=line_num
                            )
                        )
                    else:
                        # Add to default group if no priority specified
                        if "default" not in self.rules[current_category].groups:
                            self.rules[current_category].groups["default"] = RuleGroup(
                                rules=[],
                                priority=None
                            )
                        self.rules[current_category].groups["default"].rules.append(
                            RuleItem(
                                content=rule_text,
                                priority=None,
                                category=current_category,
                                line_number=line_num
                            )
                        )
    
    def validate_rules(self) -> List[str]:
        """
        Validate rules syntax and structure
        
        Returns:
            List of validation error messages
        """
        self.validation_errors = []
        
        # Check if we have any rules
        if not self.rules:
            self.validation_errors.append("No rules found or parsed")
            return self.validation_errors
        
        # Check for required categories
        essential_categories = {"project overview", "technology constraints"}
        missing_categories = [cat for cat in essential_categories if cat not in self.rules]
        if missing_categories:
            self.validation_errors.append(
                f"Missing essential categories: {', '.join(missing_categories)}"
            )
        
        # Check rules within each category
        for category_name, category in self.rules.items():
            # Check if this category has any rules
            if not category.groups:
                self.validation_errors.append(f"Category '{category_name}' has no rules")
                continue
            
            # Check rules within groups
            for priority, group in category.groups.items():
                if not group.rules:
                    self.validation_errors.append(
                        f"Category '{category_name}', priority '{priority}' has no rules"
                    )
        
        return self.validation_errors
    
    def get_rules_by_category(self, category: str) -> Optional[RuleCategory]:
        """
        Get rules for a specific category
        
        Args:
            category: The category name (case-insensitive)
            
        Returns:
            RuleCategory object if found, None otherwise
        """
        # Force reload if cache expired
        self._load_rules()
        
        # Normalize category name to lowercase for case-insensitive matching
        category_lower = category.lower()
        
        # Direct match
        if category_lower in self.rules:
            return self.rules[category_lower]
        
        # Fuzzy match (allow partial category name)
        for cat_name, cat_data in self.rules.items():
            if category_lower in cat_name:
                return cat_data
        
        return None
    
    def get_rules_by_priority(self, priority: str) -> Dict[str, List[RuleItem]]:
        """
        Get all rules with a specific priority across categories
        
        Args:
            priority: The priority level (mandatory, recommended, optional)
            
        Returns:
            Dictionary mapping category names to lists of rules
        """
        # Force reload if cache expired
        self._load_rules()
        
        result = {}
        priority = priority.lower()
        
        for category_name, category in self.rules.items():
            matching_rules = []
            if priority in category.groups:
                matching_rules.extend(category.groups[priority].rules)
            
            if matching_rules:
                result[category_name] = matching_rules
        
        return result
    
    def get_all_rules(self) -> Dict[str, RuleCategory]:
        """
        Get all rules organized by category
        
        Returns:
            Dictionary of all rule categories and their rules
        """
        # Force reload if cache expired
        self._load_rules()
        return self.rules
    
    def get_rules_as_context_string(self) -> str:
        """
        Get all rules formatted as a context string for AI prompts
        
        Returns:
            Rules formatted as a string for inclusion in AI context
        """
        # Force reload if cache expired
        self._load_rules()
        
        if not self.rules:
            return "No project-specific rules defined."
        
        lines = ["# Project Rules and Context"]
        
        for category_name, category in self.rules.items():
            # Add the category header
            lines.append(f"\n## {category_name.title()}")
            
            # Add each priority group
            for priority_name, group in category.groups.items():
                # Only add the priority header if it's a known priority
                if priority_name.lower() in self.KNOWN_PRIORITIES:
                    lines.append(f"\n### {priority_name.title()}")
                
                # Add each rule in this group
                for rule in group.rules:
                    lines.append(f"- {rule.content}")
        
        return "\n".join(lines)
    
    def has_rules(self) -> bool:
        """
        Check if any rules are defined
        
        Returns:
            True if rules are defined, False otherwise
        """
        # Force reload if cache expired
        self._load_rules()
        return bool(self.rules)
    
    def create_default_rules_file(self, target_path: str = None) -> bool:
        """
        Create a default rules template file
        
        Args:
            target_path: Path where the template should be saved.
                       If None, uses the project root.
                       
        Returns:
            True if file was created, False otherwise
        """
        if not target_path:
            target_path = os.path.join(self.project_root, self.DEFAULT_RULES_FILENAME)
        
        # Check if file already exists
        if os.path.exists(target_path):
            logger.warning(f"Rules file already exists at {target_path}")
            return False
        
        try:
            # Get template content from the template file
            template_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "templates",
                "project-prompt-rules-template.md"
            )
            
            # If template file exists, use it, otherwise use the default template
            if os.path.exists(template_path):
                with open(template_path, "r", encoding="utf-8") as f:
                    template_content = f.read()
            else:
                # Fallback to hardcoded template
                template_content = self._get_default_template()
            
            # Write the template to the target path
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(template_content)
            
            logger.info(f"Created default rules file at {target_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating default rules file: {e}")
            return False
    
    def _get_default_template(self) -> str:
        """
        Get the default rules template as a string
        
        Returns:
            Default template content
        """
        return """# Project Rules and Context

## Project Overview
This is a brief description of your project and its main objectives.

## Technology Constraints

### Mandatory Technologies
- **UI Framework**: Specify your UI framework requirements
- **Backend**: Specify your backend technology requirements
- **Database**: Specify your database requirements
- **Testing**: Specify your testing requirements

### Prohibited Technologies
- List technologies that should not be used
- Specify alternatives if applicable

## Architecture Rules

### Service Structure
- Describe your service architecture requirements
- Specify inheritance or design patterns to follow

### File Organization
```
src/
  ├── models/       # What goes here
  ├── services/     # What goes here
  ├── api/          # What goes here
  └── utils/        # What goes here
```

### Naming Conventions
- Classes: Specify naming convention
- Functions: Specify naming convention
- Variables: Specify naming convention
- Files: Specify naming convention

## Code Style Requirements

### Language Specific
- Specify language-specific coding standards
- Mention linting rules if applicable

### Error Handling
- Describe your error handling strategy
- Specify logging requirements

## Testing Requirements

### Unit Tests
- Specify unit testing requirements
- Mention coverage expectations

### Integration Tests
- Describe integration testing approach
- Specify tooling requirements

## AI Analysis Preferences

### Focus Areas
1. List primary focus areas for AI analysis
2. Specify what's most important for your project

### Suggestion Priorities
1. Rank what types of suggestions are most valuable
2. Specify what should be prioritized in analysis

## Documentation Standards

### Code Documentation
- Specify documentation requirements for code
- Mention tools or formats to use

### Project Documentation
- Describe requirements for project documentation
- Specify how documentation should be maintained

## Custom Analysis Rules

### When analyzing this project:
1. Specific instructions for analysis
2. What to look for or focus on

### When suggesting improvements:
1. Types of improvements that are most valuable
2. Guidance on suggesting changes
"""


# For testing only - not executed when imported as a module
if __name__ == "__main__":
    # Test with current directory
    rules_manager = RulesManager()
    
    # Print all rules
    if rules_manager.has_rules():
        print(rules_manager.get_rules_as_context_string())
    else:
        print("No rules found, creating template...")
        rules_manager.create_default_rules_file()
