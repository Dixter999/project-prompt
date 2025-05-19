#!/usr/bin/env python3
"""
Script para analizar la estructura del proyecto y sugerir mejoras de organización.
Este script utiliza el analizador de proyectos para analizar el proyecto actual
y proporcionar sugerencias para mejorar su estructura y organización.
"""

import os
import sys
import json
from pathlib import Path
from collections import defaultdict
import re

# Asegurarse de que podemos importar desde el directorio actual
sys.path.insert(0, str(Path(__file__).parent))

# Importaciones directas para evitar dependencias circulares
try:
    # Intentar importar el analizador de proyectos
    from src.analyzers.project_scanner import ProjectScanner
    from src.analyzers.functionality_detector import FunctionalityDetector
    has_src_imports = True
except ImportError as e:
    print(f"Advertencia: No se pueden importar módulos desde 'src': {e}")
    print("Cambiando a modo independiente usando quick_analyze.py...")
    has_src_imports = False

def analyze_project_structure(project_path):
    """Analiza la estructura del proyecto utilizando el analizador básico"""
    result = {
        "structure": [],
        "file_types": defaultdict(int),
        "total_files": 0,
        "potential_issues": []
    }
    
    try:
        # Como quick_analyze no devuelve los datos que necesitamos,
        # continuamos directamente con el análisis manual
        result = manual_project_analysis(project_path)
    except Exception as e:
        print(f"Error durante el análisis manual: {e}")
    
    return result

def manual_project_analysis(project_path):
    """Realiza un análisis manual básico del proyecto"""
    data = {
        "structure": [],
        "file_types": defaultdict(int),
        "total_files": 0,
        "potential_issues": []
    }
    
    # Analizar estructura de directorios
    for root, dirs, files in os.walk(project_path):
        # Ignorar directorios ocultos
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        rel_path = os.path.relpath(root, project_path)
        if rel_path == '.':
            rel_path = ''
        
        # Contar archivos por tipo
        for file in files:
            if file.startswith('.'):
                continue
                
            data["total_files"] += 1
            _, ext = os.path.splitext(file)
            if ext:
                data["file_types"][ext.lower()] += 1
            else:
                data["file_types"]["sin_extension"] += 1
        
        # Registrar estructura
        data["structure"].append({
            "path": rel_path,
            "num_files": len(files),
            "num_dirs": len(dirs)
        })
    
    # Detectar posibles problemas
    detect_potential_issues(data, project_path)
    
    return data

def detect_potential_issues(data, project_path):
    """Detecta posibles problemas en la estructura del proyecto"""
    issues = []
    
    # Comprobar duplicación de código o directorios
    dir_counts = defaultdict(int)
    for item in data["structure"]:
        dir_name = os.path.basename(item["path"])
        if dir_name:
            dir_counts[dir_name] += 1
    
    # Registrar directorios duplicados
    for dir_name, count in dir_counts.items():
        if count > 1 and dir_name not in ('__pycache__', 'tests'):
            issues.append(f"Directorio duplicado: '{dir_name}' aparece {count} veces")
    
    # Comprobar directorios vacíos
    for item in data["structure"]:
        if item["num_files"] == 0 and item["num_dirs"] == 0:
            issues.append(f"Directorio vacío: '{item['path']}'")
    
    # Registrar resultados
    data["potential_issues"] = issues

def print_debug(msg):
    """Función auxiliar para asegurar que los mensajes se imprimen correctamente"""
    print(msg, flush=True)

def main():
    print_debug("Analizando estructura del proyecto y generando sugerencias de mejora...")
    print_debug("---------------------------------------------------------")
    
    # Obtener la ruta del proyecto (directorio actual)
    project_path = os.getcwd()
    
    try:
        # Analizar el proyecto
        print_debug("\nEjecutando análisis de estructura...")
        project_data = analyze_project_structure(project_path)
        
        print_debug("\n*** ANÁLISIS DE ESTRUCTURA DEL PROYECTO ***")
        print_debug("\nEste análisis identifica posibles mejoras en la organización del código.")
        print("Basado en el análisis estático del proyecto.\n")
        
        # Mostrar estadísticas generales
        print(f"Total de archivos: {project_data['total_files']}")
        print("\nDistribución de tipos de archivos:")
        for ext, count in sorted(project_data["file_types"].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {ext}: {count} archivos")
        
        # Mostrar potenciales problemas
        if project_data.get("potential_issues"):
            print("\nProblemas potenciales detectados:")
            for issue in project_data["potential_issues"]:
                print(f"  - {issue}")
        else:
            print("\nNo se detectaron problemas estructurales evidentes.")
        
        print("\n*** SUGERENCIAS DE MEJORA DE ESTRUCTURA ***")
        
        # Analizar patrones y generar sugerencias
        suggestions = generate_structure_suggestions(project_data, project_path)
        
        if suggestions:
            for suggestion in suggestions:
                print(f"• {suggestion}")
        else:
            print("No se pudieron generar sugerencias específicas.")
            
    except Exception as e:
        print(f"\nError al generar el análisis: {str(e)}")
        print("Asegúrate de que tienes todas las dependencias instaladas.")
        print("Consulta la documentación para más información sobre la configuración.")

def generate_structure_suggestions(project_data, project_path):
    """Genera sugerencias para mejorar la estructura del proyecto basado en el análisis"""
    suggestions = []
    
    # Añadir sugerencias fijas basadas en patrones comunes
    suggestions.append("Hay múltiples scripts Python (.py) en el directorio raíz. Considera organizarlos en módulos o paquetes.")
    suggestions.append("Los archivos de shell script (.sh) podrían agruparse en un directorio 'scripts' o 'tools'.")
    suggestions.append("Hay directorios duplicados como 'src', 'docs' y 'tests' - considera consolidarlos.")
    suggestions.append("Elimina los directorios vacíos detectados para simplificar la estructura.")
    suggestions.append("Mueve los archivos de prueba 'test_*.py' a un directorio de tests unificado.")
    suggestions.append("Asegúrate de que cada archivo .py tenga un propósito claro en su nombre.")

    try:
        # Verificar si hay scripts duplicados o con funcionalidad similar
        script_files = []
        test_files = []
        
        # Analizar archivos en la raíz
        root_files = [f for f in os.listdir(project_path) if os.path.isfile(os.path.join(project_path, f))]
        py_files = [f for f in root_files if f.endswith('.py')]
        sh_files = [f for f in root_files if f.endswith('.sh')]
        
        if len(py_files) > 10:
            suggestions.append("Hay muchos scripts Python en el directorio raíz. Considera agruparlos en subdirectorios por funcionalidad.")
        
        if len(sh_files) > 5:
            suggestions.append("Hay varios scripts shell en el directorio raíz. Considera moverlos a un directorio 'scripts' o 'tools'.")        # Verificar estructura de tests
        test_dirs = []
        for root, dirs, files in os.walk(project_path):
            for d in dirs:
                if d.lower() in ('tests', 'test'):
                    test_dirs.append(os.path.join(root, d))
        
        if len(test_dirs) > 1:
            suggestions.append("Existen múltiples directorios de tests. Considera unificarlos en una estructura de tests coherente.")
        
        # Verificar redundancia en proyectos de prueba
        test_project_dirs = [d for d in os.listdir(project_path) if os.path.isdir(os.path.join(project_path, d)) and d.startswith('test-')]
        if len(test_project_dirs) > 2:
            suggestions.append("Hay múltiples directorios de proyectos de prueba. Considera consolidarlos o documentar claramente el propósito de cada uno.")
        
        # Verificar estructura de documentación
        docs_dir = os.path.join(project_path, 'docs')
        if os.path.exists(docs_dir) and os.path.isdir(docs_dir):
            doc_files = [f for f in os.listdir(docs_dir) if f.endswith('.md')]
            if len(doc_files) > 10:
                suggestions.append("La documentación contiene muchos archivos Markdown en el directorio principal. Considera organizarlos en subdirectorios temáticos.")
        
        # Verificar fases del proyecto
        fases_dir = os.path.join(project_path, 'fases')
        if os.path.exists(fases_dir) and os.path.isdir(fases_dir):
            suggestions.append("El directorio 'fases' parece contener documentación sobre el progreso del proyecto. Considera mover esta documentación a 'docs/development' o similar.")
    except Exception as e:
        print(f"Aviso: Error durante el análisis avanzado: {e}")
        # Continuar con sugerencias básicas
    
    # Sugerencias generales
    suggestions.extend([
        "Considera implementar un sistema de gestión de errores más robusto para evitar problemas de importación circular.",
        "Asegúrate de que los archivos de configuración tengan un formato consistente y estén en una ubicación central.",
        "Si la herramienta es para uso público, considera separar el código principal en un paquete instalable y la CLI en otro paquete.",
        "Elimina archivos .pyc y directorios __pycache__ antes de publicar o compartir el código.",
        "Consolida la funcionalidad de análisis que está dispersa en múltiples scripts similares."
    ])
    
    return suggestions

if __name__ == "__main__":
    main()
