#!/usr/bin/env python3
"""
Script para enviar un análisis de proyecto existente a Anthropic para obtener sugerencias.

Uso:
    python send_analysis_to_anthropic.py analysis_file.json -o output.md
"""

import os
import sys
import json
import argparse
import requests

def read_analysis_file(file_path):
    """Lee el archivo de análisis y lo convierte a formato JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error al leer el archivo de análisis: {e}")
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

def get_anthropic_api_key():
    """Obtiene la clave API de Anthropic desde varias fuentes posibles."""
    # Intentar desde variable de entorno
    api_key = os.getenv("anthropic_API")
    if api_key:
        return api_key
        
    # Intentar desde archivo .env
    try:
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('anthropic_API'):
                        api_key = line.split('=')[1].strip().strip('"\'')
                        if api_key:
                            return api_key
    except Exception as e:
        print(f"Error al leer .env: {e}")
        
    # Intentar desde config.yaml
    try:
        config_dir = os.path.expanduser("~/.config/project-prompt")
        config_file = os.path.join(config_dir, "config.yaml")
        if os.path.exists(config_file):
            import yaml
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                if config and 'api' in config and 'anthropic' in config['api']:
                    api_key = config['api']['anthropic'].get('key')
                    if api_key:
                        return api_key
    except Exception as e:
        print(f"Error al leer config.yaml: {e}")
        
    return None

def generate_improvements_with_anthropic(markdown_content, project_path):
    """Utiliza la API de Anthropic para generar sugerencias de mejora."""
    print("\nGenerando sugerencias de mejora con Anthropic API...")
    
    # Verificar que tengamos una clave API de Anthropic
    api_key = get_anthropic_api_key()
    if not api_key:
        print("Error: No se encontró la API key de Anthropic")
        print("Asegúrate de definir 'anthropic_API' en el archivo .env")
        return None
    
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
        return None

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
    parser = argparse.ArgumentParser(description='Envía un análisis de proyecto a Anthropic para obtener sugerencias')
    parser.add_argument('analysis_file', type=str, help='Archivo JSON con el análisis del proyecto')
    parser.add_argument('-o', '--output', type=str, help='Archivo de salida para el informe con sugerencias')
    args = parser.parse_args()
    
    # Verificar que el archivo de análisis existe
    if not os.path.isfile(args.analysis_file):
        print(f"Error: El archivo {args.analysis_file} no existe.")
        sys.exit(1)
    
    # Leer el archivo de análisis
    project_data = read_analysis_file(args.analysis_file)
    project_path = project_data.get('project_path', '')
    
    # Generar el informe en Markdown
    print("Generando informe en Markdown...")
    markdown_content = generate_markdown_from_analysis(project_data)
    
    # Generar sugerencias con Anthropic
    suggestions = generate_improvements_with_anthropic(markdown_content, project_path)
    
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
