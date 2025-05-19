#!/usr/bin/env python3
"""
Análisis simplificado de proyecto
"""
import os
import sys
import time
from collections import Counter

def analyze_project(path):
    """Analizar un proyecto de forma simple"""
    print(f"Analizando proyecto: {path}", flush=True)
    
    # Contar directorios y archivos
    total_dirs = 0
    total_files = 0
    languages = Counter()
    
    # Extensiones comunes para lenguajes de programación
    lang_exts = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.html': 'HTML',
        '.css': 'CSS',
        '.md': 'Markdown',
        '.json': 'JSON',
        '.txt': 'Text',
    }
    
    start = time.time()
    
    # Recorrer directorios
    print("Escaneando estructura de proyecto...", flush=True)
    for root, dirs, files in os.walk(path):
        # Ignorar directorios ocultos
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        total_dirs += len(dirs)
        
        # Imprimir progreso frecuentemente
        if total_dirs % 5 == 0 and total_dirs > 0:
            print(f"Progreso: {total_dirs} directorios, {total_files} archivos encontrados", end="\r", flush=True)
        
        # Contar archivos y clasificar por lenguaje
        for file in files:
            if file.startswith('.'):
                continue
                
            total_files += 1
            _, ext = os.path.splitext(file)
            lang = lang_exts.get(ext.lower(), 'Other')
            languages[lang] += 1
    
    print("", flush=True)  # Limpiar línea de progreso
    
    elapsed = time.time() - start
    
    # Mostrar resultados
    print("\n" + "=" * 50)
    print("RESULTADOS DEL ANÁLISIS")
    print("=" * 50)
    print(f"Directorios: {total_dirs}")
    print(f"Archivos:    {total_files}")
    print(f"Tiempo:      {elapsed:.2f} segundos")
    
    print("\nDistribución de lenguajes:")
    for lang, count in languages.most_common():
        pct = count / total_files * 100 if total_files > 0 else 0
        print(f"- {lang:<10}: {count:>4} archivos ({pct:>5.1f}%)")
    
    print("\nAnálisis completado")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = os.path.abspath(".")
        
    analyze_project(project_path)
