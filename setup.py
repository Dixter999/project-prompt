"""
Setup configuration for ProjectPrompt v2.0
"""

from setuptools import setup, find_packages

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
        with open('src/__init__.py', 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"\'')
    except FileNotFoundError:
        pass
    return "2.0.0"

# Core dependencies
DEPENDENCIES = [
    "anthropic>=0.7.0",
    "openai>=1.0.0", 
    "click>=8.0.0",
    "python-dotenv>=0.19.0",
    "pathspec>=0.10.0",
    "typing-extensions>=4.0.0"
]

setup(
    name="projectprompt",
    version=get_version(),
    description="AI-powered project analysis and improvement suggestions",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="ProjectPrompt",
    url="https://github.com/your-username/projectprompt",
    packages=find_packages(include=["src", "src.*", "."]),
    package_dir={"": "."},
    python_requires=">=3.8",
    install_requires=DEPENDENCIES,
    entry_points={
        "console_scripts": [
            "projectprompt=main:main",
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
    ],
    keywords="ai, code-analysis, project-analysis",
    include_package_data=True,
    zip_safe=False,
)
