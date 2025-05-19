#!/usr/bin/env python3
"""
CLI wrapper para project-prompt

Este script proporciona una interfaz de línea de comandos para ProjectPrompt
"""

import os
import sys
import argparse
import subprocess

def main():
    """Punto de entrada principal para la CLI"""
    parser = argparse.ArgumentParser(description='ProjectPrompt: Análisis de proyectos')
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando analyze
    analyze_parser = subparsers.add_parser('analyze', help='Analizar un proyecto')
    analyze_parser.add_argument('path', nargs='?', default='.', help='Ruta al proyecto (por defecto: directorio actual)')
    analyze_parser.add_argument('-o', '--output', help='Archivo de salida para el análisis (formato JSON)')
    
    # Comando init
    init_parser = subparsers.add_parser('init', help='Inicializar un nuevo proyecto')
    
    # Procesar argumentos
    args = parser.parse_args()
    
    # Obtener directorio del script actual
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'analyze':
        analyzer_path = os.path.join(script_dir, 'project_analyzer.py')
        cmd = [sys.executable, analyzer_path, args.path]
        if args.output:
            cmd.append(args.output)
        subprocess.run(cmd)
    
    elif args.command == 'init':
        print("Inicializando nuevo proyecto...")
        print("Esta función está pendiente de implementación.")

if __name__ == "__main__":
    main()
