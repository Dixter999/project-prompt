#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="test-project",
    version="0.1.0",
    description="Proyecto generado con project-prompt",
    author="Su Nombre",
    author_email="su.email@example.com",
    packages=find_packages(),
    install_requires=[
        "typer",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "test_project=src.main:app",
        ],
    },
)
