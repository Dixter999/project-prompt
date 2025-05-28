#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para generar dashboard markdown directamente.
"""

from src.ui.markdown_dashboard import MarkdownDashboardGenerator
import sys
import traceback

def main():
    """Ejecutar dashboard markdown directamente."""
    try:
        project_path = "."
        output_path = "project_dashboard_direct.md"
        
        print(f"Generando dashboard para {project_path}...")
        generator = MarkdownDashboardGenerator(project_path)
        result = generator.generate_dashboard(output_path)
        print(f"Dashboard generado en: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
