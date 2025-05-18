#!/usr/bin/env python3
"""
Punto de entrada para project-prompt

Este script proporciona un punto de entrada unificado para todas las funcionalidades
disponibles en project-prompt, incluyendo análisis de proyectos e inicialización.
"""

import os
import sys
import argparse
import subprocess

def main():
    """Punto de entrada principal del script"""
    parser = argparse.ArgumentParser(description='ProjectPrompt: Herramientas para proyectos')
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando analyze
    analyze_parser = subparsers.add_parser('analyze', help='Analizar un proyecto existente')
    analyze_parser.add_argument('path', nargs='?', default='.', help='Ruta del proyecto a analizar')
    analyze_parser.add_argument('-o', '--output', help='Archivo de salida para el análisis (formato JSON)')
    
    # Comando init
    init_parser = subparsers.add_parser('init', help='Inicializar un nuevo proyecto')
    init_parser.add_argument('name', help='Nombre del nuevo proyecto')
    init_parser.add_argument('--path', default='.', help='Ruta donde crear el proyecto')
    
    # Comando help
    help_parser = subparsers.add_parser('help', help='Mostrar ayuda')
    
    # Procesar argumentos
    args = parser.parse_args()
    
    # Obtener directorio donde están instalados los scripts
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    if not args.command or args.command == 'help':
        parser.print_help()
        return 0
    
    # Ejecutar comando solicitado
    if args.command == 'analyze':
        script_path = os.path.join(script_dir, 'quick_analyze.py')
        if not os.path.exists(script_path):
            script_path = '/mnt/h/Projects/project-prompt/quick_analyze.py'
            
        cmd = [sys.executable, script_path, args.path]
        if args.output:
            cmd.append(args.output)
        
        print(f"Ejecutando: {' '.join(cmd)}")
        result = subprocess.call(cmd)
        return result
    
    elif args.command == 'init':
        script_path = os.path.join(script_dir, 'quick_init.py')
        if not os.path.exists(script_path):
            script_path = '/mnt/h/Projects/project-prompt/quick_init.py'
            
        cmd = [sys.executable, script_path, args.name]
        if args.path:
            cmd.extend(['--path', args.path])
        
        print(f"Ejecutando: {' '.join(cmd)}")
        result = subprocess.call(cmd)
        return result
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
