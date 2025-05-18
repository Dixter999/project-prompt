#!/usr/bin/env python3
"""
Script para ejecutar pruebas completas en diferentes sistemas operativos.
Este script está diseñado para ser utilizado en CI/CD o manualmente para verificar
la compatibilidad de ProjectPrompt con diferentes plataformas.
"""

import os
import sys
import argparse
import subprocess
import platform
import time
import logging
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"test-run-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log")
    ]
)

logger = logging.getLogger("test-runner")

# Determinar la ruta al proyecto
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
TEST_DIRS = [
    PROJECT_ROOT / "tests",
    PROJECT_ROOT / "tests" / "integration",
    PROJECT_ROOT / "tests" / "e2e"
]


def detect_platform():
    """Detectar el sistema operativo y versión."""
    system = platform.system()
    version = platform.version()
    python_version = platform.python_version()
    
    logger.info(f"Sistema operativo: {system} {version}")
    logger.info(f"Versión de Python: {python_version}")
    
    return system, version, python_version


def check_dependencies():
    """Verificar las dependencias necesarias para ejecutar las pruebas."""
    logger.info("Verificando dependencias...")
    
    try:
        import pytest
        logger.info(f"pytest encontrado: {pytest.__version__}")
    except ImportError:
        logger.error("pytest no está instalado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-cov"])
    
    # Verificar dependencias del proyecto
    try:
        requirements_file = PROJECT_ROOT / "requirements.txt"
        if requirements_file.exists():
            logger.info("Instalando dependencias del proyecto...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
    except Exception as e:
        logger.error(f"Error al instalar dependencias: {e}")


def run_unit_tests(verbosity=1, coverage=False):
    """Ejecutar pruebas unitarias."""
    logger.info("Ejecutando pruebas unitarias...")
    
    cmd = [sys.executable, "-m", "pytest", str(PROJECT_ROOT / "tests")]
    
    # Configurar nivel de verbosidad
    if verbosity > 0:
        cmd.append(f"-{'v' * verbosity}")
    
    # Configurar cobertura
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=term", "--cov-report=html"])
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        
        if result.stdout:
            logger.info("=== Salida de pruebas unitarias ===")
            logger.info(result.stdout)
            
        if result.stderr:
            logger.warning("=== Errores de pruebas unitarias ===")
            logger.warning(result.stderr)
            
        if result.returncode != 0:
            logger.error(f"Las pruebas unitarias fallaron con código {result.returncode}")
            return False
        else:
            logger.info("Pruebas unitarias completadas exitosamente")
            return True
            
    except Exception as e:
        logger.error(f"Error al ejecutar pruebas unitarias: {e}")
        return False
    finally:
        elapsed_time = time.time() - start_time
        logger.info(f"Tiempo de ejecución de pruebas unitarias: {elapsed_time:.2f} segundos")


def run_integration_tests(verbosity=1):
    """Ejecutar pruebas de integración."""
    logger.info("Ejecutando pruebas de integración...")
    
    cmd = [sys.executable, "-m", "pytest", str(PROJECT_ROOT / "tests" / "integration")]
    
    # Configurar nivel de verbosidad
    if verbosity > 0:
        cmd.append(f"-{'v' * verbosity}")
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        
        if result.stdout:
            logger.info("=== Salida de pruebas de integración ===")
            logger.info(result.stdout)
            
        if result.stderr:
            logger.warning("=== Errores de pruebas de integración ===")
            logger.warning(result.stderr)
            
        if result.returncode != 0:
            logger.error(f"Las pruebas de integración fallaron con código {result.returncode}")
            return False
        else:
            logger.info("Pruebas de integración completadas exitosamente")
            return True
            
    except Exception as e:
        logger.error(f"Error al ejecutar pruebas de integración: {e}")
        return False
    finally:
        elapsed_time = time.time() - start_time
        logger.info(f"Tiempo de ejecución de pruebas de integración: {elapsed_time:.2f} segundos")


def run_e2e_tests(verbosity=1):
    """Ejecutar pruebas end-to-end."""
    logger.info("Ejecutando pruebas end-to-end...")
    
    cmd = [sys.executable, "-m", "pytest", str(PROJECT_ROOT / "tests" / "e2e")]
    
    # Configurar nivel de verbosidad
    if verbosity > 0:
        cmd.append(f"-{'v' * verbosity}")
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        
        if result.stdout:
            logger.info("=== Salida de pruebas end-to-end ===")
            logger.info(result.stdout)
            
        if result.stderr:
            logger.warning("=== Errores de pruebas end-to-end ===")
            logger.warning(result.stderr)
            
        if result.returncode != 0:
            logger.error(f"Las pruebas end-to-end fallaron con código {result.returncode}")
            return False
        else:
            logger.info("Pruebas end-to-end completadas exitosamente")
            return True
            
    except Exception as e:
        logger.error(f"Error al ejecutar pruebas end-to-end: {e}")
        return False
    finally:
        elapsed_time = time.time() - start_time
        logger.info(f"Tiempo de ejecución de pruebas end-to-end: {elapsed_time:.2f} segundos")


def run_specific_test(test_path, verbosity=1):
    """Ejecutar una prueba específica."""
    logger.info(f"Ejecutando prueba específica: {test_path}")
    
    cmd = [sys.executable, "-m", "pytest", test_path]
    
    # Configurar nivel de verbosidad
    if verbosity > 0:
        cmd.append(f"-{'v' * verbosity}")
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Error al ejecutar prueba específica: {e}")
        return False


def run_performance_tests(verbosity=1, repeat=3):
    """Ejecutar pruebas de rendimiento."""
    logger.info(f"Ejecutando pruebas de rendimiento (repeticiones: {repeat})...")
    
    # Identificar pruebas de rendimiento (si existen)
    perf_test_dir = PROJECT_ROOT / "tests" / "performance"
    if not perf_test_dir.exists():
        logger.warning("No se encontró el directorio de pruebas de rendimiento")
        return True
    
    cmd = [sys.executable, "-m", "pytest", str(perf_test_dir)]
    
    # Configurar nivel de verbosidad
    if verbosity > 0:
        cmd.append(f"-{'v' * verbosity}")
    
    # Repetir las pruebas para obtener tiempos promedio
    success = True
    times = []
    
    for i in range(repeat):
        logger.info(f"Ejecución de rendimiento {i+1}/{repeat}")
        start_time = time.time()
        try:
            result = subprocess.run(cmd, check=False, capture_output=True)
            elapsed = time.time() - start_time
            times.append(elapsed)
            
            if result.returncode != 0:
                success = False
                logger.error(f"Fallo en ejecución {i+1}")
        except Exception as e:
            logger.error(f"Error en ejecución {i+1}: {e}")
            success = False
    
    # Calcular estadísticas
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        logger.info(f"Rendimiento: Promedio={avg_time:.2f}s, Min={min_time:.2f}s, Max={max_time:.2f}s")
    
    return success


def run_all_tests(verbosity=1, coverage=False):
    """Ejecutar todos los tipos de pruebas."""
    logger.info("Iniciando ejecución de todas las pruebas...")
    start_time = time.time()
    
    # Ejecutar cada tipo de prueba
    unit_success = run_unit_tests(verbosity, coverage)
    integration_success = run_integration_tests(verbosity)
    e2e_success = run_e2e_tests(verbosity)
    
    # Calcular resultado global
    all_success = unit_success and integration_success and e2e_success
    
    elapsed_time = time.time() - start_time
    logger.info(f"Tiempo total de ejecución: {elapsed_time:.2f} segundos")
    
    # Generar resumen
    logger.info("=== RESUMEN DE PRUEBAS ===")
    logger.info(f"Pruebas unitarias: {'EXITOSAS' if unit_success else 'FALLIDAS'}")
    logger.info(f"Pruebas de integración: {'EXITOSAS' if integration_success else 'FALLIDAS'}")
    logger.info(f"Pruebas end-to-end: {'EXITOSAS' if e2e_success else 'FALLIDAS'}")
    logger.info(f"Resultado global: {'EXITOSO' if all_success else 'FALLIDO'}")
    
    return all_success


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Ejecutor de pruebas para ProjectPrompt")
    
    # Opciones generales
    parser.add_argument("-v", "--verbose", action="count", default=0, 
                      help="Aumentar nivel de verbosidad (-v, -vv, etc.)")
    parser.add_argument("--coverage", action="store_true", 
                      help="Generar informe de cobertura de código")
    
    # Tipos de prueba
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true", 
                     help="Ejecutar todas las pruebas (por defecto)")
    group.add_argument("--unit", action="store_true", 
                     help="Ejecutar solo pruebas unitarias")
    group.add_argument("--integration", action="store_true", 
                     help="Ejecutar solo pruebas de integración")
    group.add_argument("--e2e", action="store_true", 
                     help="Ejecutar solo pruebas end-to-end")
    group.add_argument("--performance", action="store_true", 
                     help="Ejecutar pruebas de rendimiento")
    group.add_argument("--specific", type=str, 
                     help="Ejecutar una prueba específica (ruta al archivo)")
    
    args = parser.parse_args()
    
    # Detectar plataforma
    detect_platform()
    
    # Verificar dependencias
    check_dependencies()
    
    # Ejecutar las pruebas según los argumentos
    if args.unit:
        success = run_unit_tests(args.verbose, args.coverage)
    elif args.integration:
        success = run_integration_tests(args.verbose)
    elif args.e2e:
        success = run_e2e_tests(args.verbose)
    elif args.performance:
        success = run_performance_tests(args.verbose)
    elif args.specific:
        success = run_specific_test(args.specific, args.verbose)
    else:  # Por defecto, ejecutar todas
        success = run_all_tests(args.verbose, args.coverage)
    
    # Salir con el código apropiado
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
