#!/usr/bin/env python3
"""
Script para analizar un proyecto, generar un informe en Markdown y proponer mejoras
utilizando la API de Anthropic.

Uso:
    python analyze_with_anthropic_simple.py /ruta/al/proyecto

Este script utiliza las funcionalidades avanzadas de ProjectPrompt y la API de Anthropic
para proporcionar un análisis completo y sugerencias de mejora.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
import argparse
import tempfile

# Asegurarse de que podemos importar desde el directorio actual
sys.path.insert(0, str(Path(__file__).parent))

# Función para cargar dinámicamente la API de Anthropic para evitar importación circular
def get_anthropic_client():
    try:
        from src.integrations.anthropic import get_anthropic_client
        return get_anthropic_client()
    except ImportError as e:
        print(f"Error al importar módulos: {e}")
        print("Asegúrate de que todas las dependencias están instaladas.")
        sys.exit(1)

def run_project_analyzer(project_path, output_file):
    """Ejecuta el analizador de proyectos y devuelve los resultados como JSON."""
    try:
        # Usar subprocess para ejecutar project_prompt_cli.py
        cmd = ["python", "project_prompt_cli.py", "analyze", project_path, "--output", output_file]
        print(f"Ejecutando: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
        # Leer el archivo JSON generado
        with open(output_file, 'r') as f:
            return json.load(f)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el analizador: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error al decodificar el JSON: {e}")
        sys.exit(1)

def generate_markdown_from_analysis(project_data):
    """Genera un informe en Markdown a partir de los datos de análisis."""
    project_path = project_data.get('project_path', '')
    project_name = os.path.basename(project_path)
    stats = project_data.get('stats', {})
    languages = project_data.get('languages', {})
    important_files = project_data.get('important_files', {})
    
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
    
    for lang, data in languages.items():
        files = data.get('files', 0)
        file_percent = (files / stats.get('total_files', 1)) * 100
        lines = data.get('lines', 0)
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
        anthropic_client = get_anthropic_client()
        
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
        return "Error al generar sugerencias con Anthropic API. Verifica tu configuración y clave API."

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
    
    # Archivo temporal para el análisis JSON
    temp_file = os.path.join(tempfile.gettempdir(), "project_analysis.json")
    
    # Analizar el proyecto
    print(f"Analizando proyecto: {args.project_path}")
    project_data = run_project_analyzer(args.project_path, temp_file)
    
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
