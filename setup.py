#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from setuptools import setup, find_packages

# Read version from pyproject.toml
with open("pyproject.toml", "r") as f:
    version_match = re.search(r'version = "([^"]+)"', f.read())
    version = version_match.group(1) if version_match else "0.1.0"

# Read README for long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="project-prompt",
    version=version,
    description="Asistente inteligente para análisis y documentación de proyectos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/project-prompt",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.5.0",
        "openai>=1.0.0",
        "anthropic>=0.5.0",
        "pyyaml>=6.0.1",
    ],
    entry_points={
        "console_scripts": [
            "project-prompt=src.main:app",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
