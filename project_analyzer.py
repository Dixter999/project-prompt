#!/usr/bin/env python3
"""
Script para analizar un proyecto Python.
Una versión simplificada y sin dependencias internas del analizador de project-prompt.
"""

import os
import sys
import json
import time
from collections import Counter
from pathlib import Path
import fnmatch

# Configuración
MAX_FILE_SIZE_MB = 5.0  # Tamaño máximo de archivo a analizar (MB)
MAX_FILES = 10000  # Número máximo de archivos a analizar
IGNORE_DIRS = [
    '.git', '.svn', '.hg', '.vscode', '__pycache__', 'venv', 'env', 
    'node_modules', 'build', 'dist', 'target', '.idea', '.gradle'
]
IGNORE_FILES = ['*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.exe', '*.bin', '*.dat']

def is_binary_file(file_path: str) -> bool:
    """Determinar si un archivo es binario o texto."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)  # Leer primeros 1024 bytes
        return False
    except UnicodeDecodeError:
        return True
    except Exception:
        return True

def get_file_language(file_path: str) -> str:
    """Detectar el lenguaje de programación de un archivo basado en su extensión."""
    ext = os.path.splitext(file_path)[1].lower()
    
    # Mapeo de extensiones a lenguajes
    language_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.html': 'HTML',
        '.css': 'CSS',
        '.java': 'Java',
        '.c': 'C',
        '.cpp': 'C++',
        '.h': 'C/C++ Header',
        '.hpp': 'C++ Header',
        '.cs': 'C#',
        '.php': 'PHP',
        '.rb': 'Ruby',
        '.go': 'Go',
        '.rs': 'Rust',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.sh': 'Shell',
        '.md': 'Markdown',
        '.json': 'JSON',
        '.yml': 'YAML',
        '.yaml': 'YAML',
        '.xml': 'XML',
        '.sql': 'SQL',
        '.r': 'R',
        '.dart': 'Dart',
        '.lua': 'Lua',
    }
    
    return language_map.get(ext, 'Other')

def count_lines(file_path: str) -> int:
    """Contar el número de líneas de código en un archivo."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0

def should_ignore(path: str, ignore_dirs=None, ignore_files=None) -> bool:
    """Verificar si un archivo o directorio debe ser ignorado."""
    if ignore_dirs is None:
        ignore_dirs = IGNORE_DIRS
    if ignore_files is None:
        ignore_files = IGNORE_FILES
    
    # Comprobar si el directorio debe ser ignorado
    for ignore_dir in ignore_dirs:
        if ignore_dir in Path(path).parts:
            return True
    
    # Comprobar si el archivo debe ser ignorado
    if os.path.isfile(path):
        for pattern in ignore_files:
            if fnmatch.fnmatch(os.path.basename(path), pattern):
                return True
    
    return False

def analyze_project(project_path: str) -> dict:
    """
    Analizar la estructura y características de un proyecto.
    
    Args:
        project_path: Ruta al directorio del proyecto
    
    Returns:
        dict: Datos del análisis del proyecto
    """
    start_time = time.time()
    project_path = os.path.abspath(project_path)
    
    # Validar que el directorio existe
    if not os.path.isdir(project_path):
        print(f"Error: El directorio {project_path} no existe")
        return {}
    
    print(f"Iniciando análisis del proyecto: {project_path}")
    print("Escaneando archivos y directorios...")
    
    # Inicializar contadores y colecciones
    total_files = 0
    total_dirs = 0
    analyzed_files = 0
    binary_files = 0
    total_size_kb = 0
    languages = {}
    important_files = {
        "configuration": [],
        "documentation": [],
        "build": [],
        "main_code": [],
        "tests": [],
    }
    
    # Mapeo de patrones para archivos importantes
    important_patterns = {
        "configuration": ["*.json", "*.yaml", "*.yml", "*.toml", "*.ini", "*.cfg", "*.config", "*.conf", "*rc"],
        "documentation": ["*.md", "*.rst", "*.txt", "LICENSE*", "README*", "CHANGELOG*", "CONTRIBUTING*"],
        "build": ["setup.py", "pyproject.toml", "package.json", "requirements.txt", "Makefile", "CMakeLists.txt", "build.gradle", "pom.xml"],
        "main_code": ["main.py", "app.py", "index.js", "server.js", "src/*.py", "src/*/*.py"],
        "tests": ["test_*.py", "*_test.py", "tests/*.py", "test/*.py", "spec/*.js", "*_spec.js"]
    }

    # Recorrer el directorio del proyecto
    print("Escaneando directorios y archivos...")
    for root, dirs, files in os.walk(project_path):
        # Filtrar directorios a ignorar
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d))]
        total_dirs += len(dirs)
        
        # Imprimir progreso cada cierto número de directorios
        if total_dirs % 10 == 0 and total_dirs > 0:
            print(f"Progreso: {total_dirs} directorios, {total_files} archivos encontrados", end="\r")
            sys.stdout.flush()
        
        # Procesar archivos
        for file in files:
            file_path = os.path.join(root, file)
            
            # Verificar si se debe ignorar
            if should_ignore(file_path):
                continue
            
            total_files += 1
            
            # Aplicar límite de archivos
            if total_files > MAX_FILES:
                continue
                
            # Obtener tamaño y verificar límite
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            total_size_kb += file_size_mb * 1024
            
            if file_size_mb > MAX_FILE_SIZE_MB:
                continue
            
            # Comprobar si es archivo binario
            if is_binary_file(file_path):
                binary_files += 1
                continue
                
            analyzed_files += 1
            
            # Identificar lenguaje
            rel_path = os.path.relpath(file_path, project_path)
            language = get_file_language(file_path)
            
            # Actualizar estadísticas de lenguaje
            if language not in languages:
                languages[language] = {"files": 0, "lines": 0}
            languages[language]["files"] += 1
            languages[language]["lines"] += count_lines(file_path)
            
            # Categorizar archivos importantes
            for category, patterns in important_patterns.items():
                for pattern in patterns:
                    if fnmatch.fnmatch(file, pattern) or fnmatch.fnmatch(rel_path, pattern):
                        important_files[category].append(rel_path)
                        break
    
    # Ordenar lenguajes por número de archivos
    languages = {k: v for k, v in sorted(
        languages.items(), 
        key=lambda item: item[1]["files"], 
        reverse=True
    )}
    
    # Compilar resultados
    analysis_time = time.time() - start_time
    result = {
        "project_path": project_path,
        "scan_time": round(analysis_time, 2),
        "stats": {
            "total_files": total_files,
            "total_dirs": total_dirs,
            "analyzed_files": analyzed_files,
            "binary_files": binary_files,
            "total_size_kb": round(total_size_kb, 2)
        },
        "languages": languages,
        "important_files": important_files,
    }
    
    return result

def print_analysis_report(analysis: dict):
    """Imprimir un informe del análisis en la consola."""
    if not analysis:
        print("No hay datos de análisis disponibles.")
        return
    
    print("\n" + "="*60)
    print(f"ANÁLISIS DE PROYECTO: {os.path.basename(analysis['project_path'])}")
    print("="*60)
    
    stats = analysis["stats"]
    print("\nESTADÍSTICAS:")
    print(f"Total de archivos:     {stats['total_files']}")
    print(f"Total de directorios:  {stats['total_dirs']}")
    print(f"Archivos analizados:   {stats['analyzed_files']}")
    print(f"Archivos binarios:     {stats['binary_files']}")
    print(f"Tamaño total:          {stats['total_size_kb']:,.2f} KB")
    print(f"Tiempo de análisis:    {analysis['scan_time']:.2f} segundos")
    
    print("\nDISTRIBUCIÓN DE LENGUAJES:")
    for lang, info in analysis["languages"].items():
        pct = info["files"] / stats["analyzed_files"] * 100 if stats["analyzed_files"] > 0 else 0
        print(f"{lang:<12}: {info['files']:>5} archivos ({pct:>5.1f}%), {info['lines']:>8,} líneas")
    
    # Añadir una pausa para que se vea la salida
    sys.stdout.flush()
    
    print("\nARCHIVOS IMPORTANTES:")
    for category, files in analysis["important_files"].items():
        if files:
            print(f"\n{category.upper()}:")
            for file in files[:10]:  # Mostrar solo los primeros 10
                print(f"- {file}")
            if len(files) > 10:
                print(f"  ... y {len(files) - 10} archivos más")

def save_analysis_to_json(analysis: dict, output_path: str):
    """Guardar el análisis en un archivo JSON."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2)
    print(f"\nAnálisis guardado en: {output_path}")

if __name__ == "__main__":
    # Procesar argumentos
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Analizando proyecto: {project_path}")
    analysis = analyze_project(project_path)
    print_analysis_report(analysis)
    
    # Opcionalmente guardar resultados
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
        save_analysis_to_json(analysis, output_path)
