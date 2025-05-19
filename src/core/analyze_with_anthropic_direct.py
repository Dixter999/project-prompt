#!/usr/bin/env python3
"""
Script para analizar un proyecto, generar un informe en Markdown y proponer mejoras
utilizando la API de Anthropic.

Uso:
    python analyze_with_anthropic_direct.py /ruta/al/proyecto

Este script utiliza las funcionalidades avanzadas de ProjectPrompt y la API de Anthropic
para proporcionar un análisis completo y sugerencias de mejora.
"""

import os
import sys
import json
import subprocess
import tempfile
import argparse
import requests
import time
from pathlib import Path

def run_project_analyzer(project_path, output_file):
    """Ejecuta el analizador de proyectos y devuelve los resultados como JSON."""
    try:
        # Usar subprocess para ejecutar project_prompt_cli.py desde el directorio correcto
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  "core", "project_prompt_cli.py")
        cmd = ["python", script_path, "analyze", project_path, "--output", output_file]
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
    
    # Verificar que tengamos una clave API de Anthropic
    api_key = os.getenv("anthropic_API")
    if not api_key:
        # Intentar leerla desde .env
        try:
            env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('anthropic_API'):
                            api_key = line.split('=')[1].strip().strip('"\'')
        except Exception as e:
            print(f"Error al leer .env: {e}")
    
    if not api_key:
        print("Error: No se encontró la API key de Anthropic")
        print("Asegúrate de definir 'anthropic_API' en el archivo .env")
        return "Error: API de Anthropic no configurada"
    
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

    # Llamar directamente a la API de Anthropic
    try:
        response = anthropic_api_call(api_key, prompt)
        print("\n✅ Sugerencias generadas correctamente!")
        return response
    except Exception as e:
        print(f"\nError al generar sugerencias con Anthropic API: {e}")
        return "Error al generar sugerencias con Anthropic API. Verifica tu configuración y clave API."

def anthropic_api_call(api_key, prompt):
    """Realiza una llamada directa a la API de Anthropic Claude."""
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 4000,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        raise Exception(f"Error en API Anthropic: {response.status_code} - {response.text}")
        
    # Procesar respuesta
    result = response.json()
    content = result.get("content", [])
    
    # Extraer el texto del contenido
    text_parts = []
    for item in content:
        if item.get("type") == "text":
            text_parts.append(item.get("text", ""))
            
    return "".join(text_parts).strip()

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
    if suggestions and not suggestions.startswith("Error"):
        full_report = f"{markdown_content}\n\n## Sugerencias de Mejora (Generado por Anthropic Claude)\n\n{suggestions}"
    else:
        full_report = markdown_content
    
    # Determinar el nombre del archivo de salida
    project_name = os.path.basename(os.path.abspath(args.project_path))
    if args.output:
        output_path = args.output
    else:
        # Usar la carpeta project-output para guardar los resultados
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_dir = os.path.join(base_dir, "project-output", "analyses")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"analysis_{project_name}_{int(time.time())}.md")
    
    # Guardar el resultado
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_report)
    print(f"\nInforme completo guardado en: {output_path}")
    
    # Mostrar resumen en consola
    print("\n" + "=" * 50)
    print("RESUMEN DEL ANÁLISIS")
    print("=" * 50)
    print(f"Proyecto: {project_name}")
    print(f"Archivo de salida: {output_path}")
    print("=" * 50)

if __name__ == "__main__":
    main()
