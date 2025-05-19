#!/usr/bin/env python3
"""
Script para optimización de rendimiento de ProjectPrompt.
Este script identifica cuellos de botella y ofrece sugerencias de mejora.
"""

import os
import sys
import time
import cProfile
import pstats
import io
import argparse
import re
import tracemalloc
from pathlib import Path
import multiprocessing
import subprocess

# Asegurar que el módulo principal está en el path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# Importaciones de ProjectPrompt
try:
    from src.analyzers.project_analyzer import ProjectAnalyzer
    from src.generators.prompt_generator import PromptGenerator
    from src.generators.markdown_generator import MarkdownGenerator
    from src.generators.contextual_prompt_generator import ContextualPromptGenerator
except ImportError as e:
    print(f"Error importando módulos de ProjectPrompt: {e}")
    sys.exit(1)


def profile_function(func, *args, **kwargs):
    """
    Perfilar una función y devolver estadísticas.
    
    Args:
        func: Función a perfilar
        *args, **kwargs: Argumentos para la función
        
    Returns:
        resultado, estadísticas
    """
    profiler = cProfile.Profile()
    profiler.enable()
    
    result = func(*args, **kwargs)
    
    profiler.disable()
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # Mostrar las 20 funciones más relevantes
    
    return result, s.getvalue()


def trace_memory_usage(func, *args, **kwargs):
    """
    Rastrear el uso de memoria de una función.
    
    Args:
        func: Función a rastrear
        *args, **kwargs: Argumentos para la función
        
    Returns:
        resultado, uso_de_memoria
    """
    tracemalloc.start()
    
    result = func(*args, **kwargs)
    
    snapshot = tracemalloc.take_snapshot()
    tracemalloc.stop()
    
    top_stats = snapshot.statistics('lineno')
    memory_report = []
    for stat in top_stats[:10]:  # Mostrar las 10 asignaciones principales
        memory_report.append(f"{stat.size / 1024:.1f} KB - {stat.traceback.format()}")
    
    return result, memory_report


def benchmark_function(func, *args, repeat=5, **kwargs):
    """
    Medir el tiempo de ejecución de una función.
    
    Args:
        func: Función a medir
        *args, **kwargs: Argumentos para la función
        repeat: Número de repeticiones
        
    Returns:
        tiempos_de_ejecución
    """
    times = []
    for i in range(repeat):
        start_time = time.time()
        func(*args, **kwargs)
        elapsed = time.time() - start_time
        times.append(elapsed)
        
    return times


def analyze_project_performance(project_path):
    """
    Analizar el rendimiento del analizador de proyectos.
    
    Args:
        project_path: Ruta al proyecto a analizar
        
    Returns:
        dict: Resultados del análisis
    """
    print(f"Analizando rendimiento para el proyecto: {project_path}")
    
    # Crear analizador
    analyzer = ProjectAnalyzer(project_path)
    
    # Perfilar análisis de proyecto
    print("Perfilando análisis de proyecto...")
    analysis_result, profile_stats = profile_function(analyzer.analyze_project)
    
    # Medir uso de memoria
    print("Midiendo uso de memoria...")
    _, memory_stats = trace_memory_usage(analyzer.analyze_project)
    
    # Benchmark de tiempo
    print("Ejecutando benchmark de tiempo...")
    analysis_times = benchmark_function(analyzer.analyze_project, repeat=3)
    avg_time = sum(analysis_times) / len(analysis_times)
    
    print(f"Tiempo promedio de análisis: {avg_time:.2f} segundos")
    
    return {
        "profile_stats": profile_stats,
        "memory_stats": memory_stats,
        "avg_time": avg_time,
        "analysis_result": analysis_result
    }


def analyze_prompt_generation_performance(project_path, analysis_result=None):
    """
    Analizar el rendimiento del generador de prompts.
    
    Args:
        project_path: Ruta al proyecto
        analysis_result: Resultado del análisis (opcional)
        
    Returns:
        dict: Resultados del análisis
    """
    print("Analizando rendimiento de generación de prompts...")
    
    if analysis_result is None:
        analyzer = ProjectAnalyzer(project_path)
        analysis_result = analyzer.analyze_project()
    
    # Crear generador de prompts
    generator = PromptGenerator()
    
    context = {
        "project_name": os.path.basename(project_path),
        "project_structure": analysis_result.get("structure", {}),
        "project_functionality": analysis_result.get("functionality", {})
    }
    
    # Perfilar generación de prompts
    _, profile_stats = profile_function(generator.generate_prompt, "default", context)
    
    # Medir uso de memoria
    _, memory_stats = trace_memory_usage(generator.generate_prompt, "default", context)
    
    # Benchmark de tiempo
    generation_times = benchmark_function(generator.generate_prompt, "default", context, repeat=5)
    avg_time = sum(generation_times) / len(generation_times)
    
    print(f"Tiempo promedio de generación de prompts: {avg_time:.2f} segundos")
    
    return {
        "profile_stats": profile_stats,
        "memory_stats": memory_stats,
        "avg_time": avg_time
    }


def analyze_contextual_generation_performance(project_path):
    """
    Analizar el rendimiento del generador contextual de prompts.
    
    Args:
        project_path: Ruta al proyecto
        
    Returns:
        dict: Resultados del análisis
    """
    print("Analizando rendimiento de generación contextual...")
    
    # Buscar un archivo Python para la prueba
    py_files = list(Path(project_path).rglob("*.py"))
    if not py_files:
        print("No se encontraron archivos Python para probar la generación contextual")
        return None
    
    test_file = str(py_files[0])
    
    # Crear generador contextual
    generator = ContextualPromptGenerator(project_path)
    
    context = {
        "focus_file": test_file,
        "query": "Explica este archivo"
    }
    
    # Perfilar generación contextual
    _, profile_stats = profile_function(generator.generate_contextual_prompt, context)
    
    # Medir uso de memoria
    _, memory_stats = trace_memory_usage(generator.generate_contextual_prompt, context)
    
    # Benchmark de tiempo
    generation_times = benchmark_function(generator.generate_contextual_prompt, context, repeat=3)
    avg_time = sum(generation_times) / len(generation_times)
    
    print(f"Tiempo promedio de generación contextual: {avg_time:.2f} segundos")
    
    return {
        "profile_stats": profile_stats,
        "memory_stats": memory_stats,
        "avg_time": avg_time
    }


def analyze_documentation_generation(project_path, analysis_result=None):
    """
    Analizar el rendimiento del generador de documentación.
    
    Args:
        project_path: Ruta al proyecto
        analysis_result: Resultado del análisis (opcional)
        
    Returns:
        dict: Resultados del análisis
    """
    print("Analizando rendimiento de generación de documentación...")
    
    if analysis_result is None:
        analyzer = ProjectAnalyzer(project_path)
        analysis_result = analyzer.analyze_project()
    
    # Crear generador de markdown
    generator = MarkdownGenerator()
    
    # Perfilar generación de documentación
    _, profile_stats = profile_function(
        generator.generate_project_documentation, 
        project_path, 
        analysis_result
    )
    
    # Medir uso de memoria
    _, memory_stats = trace_memory_usage(
        generator.generate_project_documentation, 
        project_path, 
        analysis_result
    )
    
    # Benchmark de tiempo
    generation_times = benchmark_function(
        generator.generate_project_documentation, 
        project_path, 
        analysis_result,
        repeat=2
    )
    avg_time = sum(generation_times) / len(generation_times)
    
    print(f"Tiempo promedio de generación de documentación: {avg_time:.2f} segundos")
    
    return {
        "profile_stats": profile_stats,
        "memory_stats": memory_stats,
        "avg_time": avg_time
    }


def identify_bottlenecks(stats):
    """
    Identificar cuellos de botella a partir de las estadísticas.
    
    Args:
        stats: Estadísticas de perfilado
        
    Returns:
        list: Cuellos de botella identificados
    """
    bottlenecks = []
    
    lines = stats.split('\n')
    for line in lines[5:15]:  # Ignorar las primeras líneas de encabezado
        if not line.strip():
            continue
        match = re.search(r'\d+\.\d+ +\d+\.\d+ +\d+\.\d+ +\d+\.\d+ +\d+ +(.+)', line)
        if match:
            function_name = match.group(1).strip()
            bottlenecks.append(function_name)
    
    return bottlenecks


def suggest_improvements(bottlenecks, memory_stats):
    """
    Sugerir mejoras basadas en cuellos de botella identificados.
    
    Args:
        bottlenecks: Lista de cuellos de botella
        memory_stats: Estadísticas de memoria
        
    Returns:
        list: Sugerencias de mejora
    """
    suggestions = []
    
    # Detectar patrones comunes en los cuellos de botella
    has_file_io = any(('open' in b or 'read' in b or 'write' in b) for b in bottlenecks)
    has_json = any('json' in b.lower() for b in bottlenecks)
    has_regex = any(('re.' in b or 'regex' in b.lower() or 'match' in b.lower()) for b in bottlenecks)
    has_string_ops = any(('split' in b or 'join' in b or 'format' in b) for b in bottlenecks)
    
    # Sugerir mejoras para cada tipo de cuello de botella
    if has_file_io:
        suggestions.append("Optimización de E/S: Considere utilizar operaciones de archivo asíncronas o "
                         "almacenar en caché los resultados de las operaciones de lectura frecuentes.")
    
    if has_json:
        suggestions.append("Optimización de JSON: Considere utilizar 'ujson' o 'rapidjson' en lugar del "
                         "módulo 'json' estándar para un mejor rendimiento.")
    
    if has_regex:
        suggestions.append("Optimización de expresiones regulares: Precompile las expresiones regulares "
                         "utilizadas frecuentemente y evite expresiones complejas cuando sea posible.")
    
    if has_string_ops:
        suggestions.append("Optimización de operaciones de cadena: Reduzca la concatenación repetida "
                         "de cadenas y considere usar 'join' en lugar de '+' para concatenaciones múltiples.")
    
    # Sugerencias basadas en uso de memoria
    large_allocations = [s for s in memory_stats if " KB" in s and float(s.split(" KB")[0]) > 100]
    if large_allocations:
        suggestions.append("Optimización de memoria: Se detectaron grandes asignaciones de memoria. "
                         "Considere procesar datos en lotes o implementar transmisión para "
                         "conjuntos de datos grandes.")
    
    # Sugerencias generales
    suggestions.append("Paralelismo: Considere utilizar multiprocesamiento para tareas independientes "
                     "como el análisis de archivos separados.")
    
    suggestions.append("Caché: Implemente un sistema de caché para resultados de análisis y evitar "
                     "recálculos innecesarios en ejecuciones consecutivas.")
    
    return suggestions


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description='Optimizador de rendimiento para ProjectPrompt')
    
    parser.add_argument('--project', type=str, default=None,
                      help='Ruta al proyecto para analizar (por defecto: directorio actual)')
    parser.add_argument('--output', type=str, default='performance_report.txt',
                      help='Archivo para guardar el reporte de rendimiento')
    parser.add_argument('--quick', action='store_true',
                      help='Ejecutar un análisis rápido (menos precisión)')
    
    args = parser.parse_args()
    
    # Determinar el directorio a analizar
    project_path = args.project or os.getcwd()
    if not os.path.isdir(project_path):
        print(f"Error: La ruta {project_path} no es un directorio válido")
        return 1
    
    print(f"=== Análisis de rendimiento de ProjectPrompt ===")
    print(f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Proyecto: {project_path}")
    print(f"Número de CPUs: {multiprocessing.cpu_count()}")
    print("=" * 50)
    
    # Ejecutar análisis de rendimiento
    try:
        # Análisis de proyecto
        project_perf = analyze_project_performance(project_path)
        
        # Análisis de generación de prompts
        prompt_perf = analyze_prompt_generation_performance(project_path, project_perf['analysis_result'])
        
        # Análisis de generación contextual
        contextual_perf = analyze_contextual_generation_performance(project_path)
        
        # Análisis de generación de documentación (si no está en modo rápido)
        if not args.quick:
            docs_perf = analyze_documentation_generation(project_path, project_perf['analysis_result'])
        else:
            docs_perf = None
        
        # Identificar cuellos de botella
        print("\nIdentificando cuellos de botella...")
        bottlenecks = identify_bottlenecks(project_perf['profile_stats'])
        bottlenecks += identify_bottlenecks(prompt_perf['profile_stats'])
        if contextual_perf:
            bottlenecks += identify_bottlenecks(contextual_perf['profile_stats'])
        
        # Sugerir mejoras
        print("\nGenerando sugerencias de optimización...")
        suggestions = suggest_improvements(
            bottlenecks, 
            project_perf['memory_stats'] + prompt_perf['memory_stats']
        )
        
        # Generar informe
        print("\nGenerando informe de rendimiento...")
        with open(args.output, 'w') as f:
            f.write("=== INFORME DE RENDIMIENTO DE PROJECTPROMPT ===\n")
            f.write(f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Proyecto analizado: {project_path}\n\n")
            
            f.write("== TIEMPOS DE EJECUCIÓN ==\n")
            f.write(f"Análisis de proyecto: {project_perf['avg_time']:.2f} segundos\n")
            f.write(f"Generación de prompts: {prompt_perf['avg_time']:.2f} segundos\n")
            if contextual_perf:
                f.write(f"Generación contextual: {contextual_perf['avg_time']:.2f} segundos\n")
            if docs_perf:
                f.write(f"Generación de documentación: {docs_perf['avg_time']:.2f} segundos\n")
            f.write("\n")
            
            f.write("== CUELLOS DE BOTELLA IDENTIFICADOS ==\n")
            for i, bottleneck in enumerate(bottlenecks[:10], 1):
                f.write(f"{i}. {bottleneck}\n")
            f.write("\n")
            
            f.write("== USO DE MEMORIA ==\n")
            for i, stat in enumerate(project_perf['memory_stats'][:5], 1):
                f.write(f"{i}. {stat}\n")
            f.write("\n")
            
            f.write("== SUGERENCIAS DE OPTIMIZACIÓN ==\n")
            for i, suggestion in enumerate(suggestions, 1):
                f.write(f"{i}. {suggestion}\n")
        
        print(f"Informe de rendimiento guardado en: {args.output}")
        print("\n=== Sugerencias de optimización ===")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
        
    except Exception as e:
        print(f"Error durante el análisis de rendimiento: {e}")
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
