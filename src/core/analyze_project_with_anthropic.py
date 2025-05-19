#!/usr/bin/env python3
"""
Script para analizar un proyecto, generar un informe en Markdown y proponer mejoras
utilizando la API de Anthropic.

Uso:
    python analyze_project_with_anthropic.py /ruta/al/proyecto

Este script utiliza las funcionalidades avanzadas de ProjectPrompt y la API de Anthropic
para proporcionar un análisis completo y sugerencias de mejora.
"""

import os
import sys
import json
from pathlib import Path
import argparse
import tempfile

# Asegurarse de que podemos importar desde el directorio actual
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.analyzers.project_scanner import ProjectScanner
    from src.integrations.anthropic import AnthropicAPI
except ImportError as e:
    print(f"Error al importar módulos: {e}")
    print("Asegúrate de que todas las dependencias están instaladas.")
    sys.exit(1)

def analyze_project(project_path):
    """Analiza un proyecto utilizando ProjectScanner."""
    print(f"Analizando proyecto: {project_path}")
    
    try:
        scanner = ProjectScanner()
        return scanner.scan_project(project_path)
    except Exception as e:
        print(f"Error durante el análisis del proyecto: {e}")
        sys.exit(1)

def generate_markdown_from_analysis(project_data):
    """Genera un informe en Markdown a partir de los datos de análisis."""
    project_path = project_data.get('project_path', '')
    project_name = os.path.basename(project_path)
    stats = project_data.get('stats', {})
    languages = project_data.get('languages', {})
    important_files = project_data.get('important_files', {})
    
    # Debugging
    print(f"Estructura del proyecto_data: {type(project_data)}")
    print(f"Estructura del languages: {type(languages)}")
    
    markdown = f"""# Análisis del Proyecto: {project_name}

## Estadísticas Generales

- **Total de archivos:** {stats.get('total_files', 0)}
- **Total de directorios:** {stats.get('total_dirs', 0)}
- **Archivos analizados:** {stats.get('analyzed_files', 0)}
- **Archivos binarios:** {stats.get('binary_files', 0)}
- **Tamaño total:** {stats.get('total_size_kb', 0):.2f} KB
- **Tiempo de análisis:** {project_data.get('scan_time', 0):.2f} segundos

## Distribución de Lenguajes

| Lenguaje | Archivos | % del Proyecto | Líneas |
|----------|----------|----------------|--------|
"""
    
    for lang in languages:
        if isinstance(languages[lang], dict):
            files = languages[lang].get('files', 0)
            lines = languages[lang].get('lines', 0)
        elif isinstance(languages[lang], list):
            files = languages[lang][0] if len(languages[lang]) > 0 else 0
            lines = languages[lang][1] if len(languages[lang]) > 1 else 0
        else:
            files = 0
            lines = 0
        
        # Asegurarse de que files sea un número para poder dividirlo
        if isinstance(files, str):
            try:
                files = int(files)
            except ValueError:
                files = 0
                
        file_percent = files / stats.get('total_files', 1) * 100
        markdown += f"| {lang} | {files} | {file_percent:.1f}% | {lines} |\n"
    
    markdown += "\n## Archivos Importantes\n\n"
    
    for category, files in important_files.items():
        if files:
            markdown += f"### {category.capitalize()}\n\n"
            for file in files:
                markdown += f"- `{file}`\n"
            markdown += "\n"
    
    return markdown

def generate_improvements_with_anthropic(markdown_content, project_path):
    """Utiliza la API de Anthropic para generar sugerencias de mejora."""
    print("\nGenerando sugerencias de mejora con Anthropic API...")
    
    try:
        # Obtener el cliente de Anthropic
        anthropic_client = AnthropicAPI()
        
        # Si no está configurado, salir
        if not anthropic_client.is_configured:
            print("Error: La API de Anthropic no está configurada.")
            print("Configúrala con 'python set_anthropic_key.py' y vuelve a intentarlo.")
            sys.exit(1)
        
        # Crear un prompt para Claude
        prompt = f"""Basándote en el siguiente análisis de un proyecto de software, proporciona:
1. Un resumen de la estructura y propósito del proyecto
2. Fortalezas identificadas en la organización del código
3. Debilidades o áreas de mejora
4. Recomendaciones específicas para mejorar la estructura, organización y calidad del código
5. Sugerencias para la documentación

Por favor, presenta tu análisis en formato Markdown con secciones bien definidas.

ANÁLISIS DEL PROYECTO:
{markdown_content}

INFORMACIÓN ADICIONAL:
- Ruta del proyecto: {project_path}

Proporciona un análisis útil y constructivo que pueda ayudar a mejorar este proyecto.
"""

        # Llamar a la API de Anthropic
        response = anthropic_client.simple_completion(prompt)
        
        print("\n✅ Sugerencias generadas correctamente!")
        
        return response
        
    except Exception as e:
        print(f"\nError al generar sugerencias con Anthropic API: {e}")
        return None

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description='Analiza un proyecto y genera un informe con sugerencias de mejora usando Anthropic API')
    parser.add_argument('project_path', type=str, help='Ruta al proyecto a analizar')
    parser.add_argument('-o', '--output', type=str, help='Archivo de salida para el análisis')
    args = parser.parse_args()
    
    # Validar la ruta del proyecto
    if not os.path.isdir(args.project_path):
        print(f"Error: La ruta {args.project_path} no es un directorio válido.")
        sys.exit(1)
    
    # Analizar el proyecto
    project_data = analyze_project(args.project_path)
    
    # Generar el informe en Markdown
    print("\nGenerando informe en Markdown...")
    markdown_content = generate_markdown_from_analysis(project_data)
    
    # Generar sugerencias con Anthropic
    suggestions = generate_improvements_with_anthropic(markdown_content, args.project_path)
    
    # Combinar el informe y las sugerencias
    if suggestions:
        full_report = f"{markdown_content}\n\n## Sugerencias de Mejora (Generado por Anthropic Claude)\n\n{suggestions}"
    else:
        full_report = markdown_content
    
    # Guardar o mostrar el resultado
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(full_report)
        print(f"\nInforme completo guardado en: {args.output}")
    else:
        print("\n" + "=" * 50)
        print("INFORME DEL PROYECTO")
        print("=" * 50)
        print(full_report)

if __name__ == "__main__":
    main()
