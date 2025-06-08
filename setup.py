"""
Setup configuration for ProjectPrompt - Phase 2 Refactored Version.
Simplified setup with minimal dependencies.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "ProjectPrompt - AI-powered project analysis and suggestions tool"

# Read version from __init__.py
def get_version():
    try:
        with open('src_new/__init__.py', 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"\'')
    except FileNotFoundError:
        pass
    return "0.2.0"

# Core dependencies - minimal set
CORE_DEPENDENCIES = [
    "anthropic>=0.7.0",       # Anthropic AI client
    "openai>=1.0.0",          # OpenAI client
    "click>=8.0.0",           # CLI framework
    "python-dotenv>=0.19.0",  # Environment variable loading
    "pathspec>=0.10.0",       # Gitignore-style pattern matching
    "typing-extensions>=4.0.0"  # Type hints for older Python
]

# Development dependencies
DEV_DEPENDENCIES = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=1.0.0",
    "pre-commit>=2.20.0"
]

# Optional dependencies for enhanced features
OPTIONAL_DEPENDENCIES = {
    "yaml": ["PyYAML>=6.0"],
    "markdown": ["markdown>=3.4.0"],
    "dev": DEV_DEPENDENCIES
}

setup(
    name="project-prompt",
    version=get_version(),
    description="AI-powered project analysis and improvement suggestions",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="ProjectPrompt Team",
    author_email="contact@projectprompt.dev",
    url="https://github.com/project-prompt/project-prompt",
    packages=find_packages(where="src_new"),
    package_dir={"": "src_new"},
    python_requires=">=3.8",
    install_requires=CORE_DEPENDENCIES,
    extras_require=OPTIONAL_DEPENDENCIES,
    entry_points={
        "console_scripts": [
            "project-prompt=cli:main",
            "pp=cli:main",  # Short alias
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Utilities",
    ],
    keywords="ai, code-analysis, project-analysis, suggestions, anthropic, openai",
    include_package_data=True,
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://github.com/project-prompt/project-prompt/issues",
        "Source": "https://github.com/project-prompt/project-prompt",
        "Documentation": "https://project-prompt.readthedocs.io/",
    },
)
