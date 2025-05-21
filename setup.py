#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from setuptools import setup, find_packages

# Read version from pyproject.toml
with open("pyproject.toml", "r") as f:
    version_match = re.search(r'version = "([^"]+)"', f.read())
    version = version_match.group(1) if version_match else "1.0.0"

# Read README for long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="project-prompt",
    version=version,
    description="Asistente inteligente para análisis y documentación de proyectos usando IA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Daniel Lagowski Solé",
    author_email="daniel@lagowski.es",
    url="https://github.com/project-prompt/project-prompt",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.5.0",
        "openai>=1.0.0",
        "anthropic>=0.5.0",
        "pyyaml>=6.0.1",
        "python-frontmatter>=1.0.0",
        "jinja2>=3.0.0",
        "tabulate>=0.9.0",
        "requests>=2.28.0",
        "keyring>=24.0.0",
        "tiktoken>=0.5.0",
    ],
    entry_points={
        "console_scripts": [
            "project-prompt=src.main:app",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    project_urls={
        "Bug Tracker": "https://github.com/project-prompt/project-prompt/issues",
        "Documentation": "https://github.com/Dixter999/project-prompt?tab=readme-ov-file#readme",
        "Source Code": "https://github.com/project-prompt/project-prompt",
    },
)
