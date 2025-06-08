#!/usr/bin/env python3
"""
Fase 5 - Validación Manual y Directa
Ejecuta validaciones críticas sin dependencias complejas
"""

import subprocess
import sys
import time
import json
from pathlib import Path
import os
import tempfile
import shutil

def validate_cli_basic():
    """Validar funcionamiento básico del CLI"""
    print("🔧 Validando CLI básico...")
    
    results = {}
    
    # Test help
    try:
        result = subprocess.run(["projectprompt", "--help"], capture_output=True, text=True, timeout=10)
        results["help"] = result.returncode == 0
        if results["help"]:
            print("✅ CLI help funciona")
        else:
            print(f"❌ CLI help falla: {result.stderr}")
    except Exception as e:
        results["help"] = False
        print(f"❌ CLI help excepción: {e}")
    
    # Test version
    try:
        result = subprocess.run(["projectprompt", "--version"], capture_output=True, text=True, timeout=10)
        results["version"] = result.returncode == 0
        if results["version"]:
            print(f"✅ CLI version funciona: {result.stdout.strip()}")
            results["version_output"] = result.stdout.strip()
        else:
            print(f"❌ CLI version falla: {result.stderr}")
    except Exception as e:
        results["version"] = False
        print(f"❌ CLI version excepción: {e}")
    
    return results

def validate_analyze_command():
    """Validar comando analyze"""
    print("\n🔍 Validando comando analyze...")
    
    test_dir = tempfile.mkdtemp()
    test_project = Path(test_dir) / "test_analyze"
    
    try:
        test_project.mkdir(parents=True)
        
        # Crear archivos de prueba
        (test_project / "main.py").write_text("import utils\nprint('hello')")
        (test_project / "utils.py").write_text("def helper(): return 'help'")
        (test_project / "config.py").write_text("DEBUG = True")
        
        # Ejecutar analyze
        result = subprocess.run(
            ["projectprompt", "analyze", "."],
            cwd=str(test_project),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        success = result.returncode == 0
        
        if success:
            print("✅ Comando analyze funciona")
            
            # Verificar que se creó analysis.json
            analysis_file = test_project / "analysis.json"
            if analysis_file.exists():
                print("✅ Se creó analysis.json")
                
                # Verificar contenido
                try:
                    with open(analysis_file) as f:
                        analysis = json.load(f)
                    
                    # Validar estructura básica
                    if "files" in analysis:
                        print(f"✅ Analizó {len(analysis['files'])} archivos")
                    
                    if "functional_groups" in analysis:
                        groups = analysis["functional_groups"]
                        print(f"✅ Creó {len(groups)} grupos funcionales")
                        
                        # Verificar que no hay grupos vacíos
                        empty_groups = []
                        for group_name, group_data in groups.items():
                            if isinstance(group_data, dict) and "files" in group_data:
                                files = group_data["files"]
                            elif isinstance(group_data, list):
                                files = group_data
                            else:
                                continue
                            
                            if len(files) == 0:
                                empty_groups.append(group_name)
                        
                        if empty_groups:
                            print(f"❌ CRÍTICO: Grupos vacíos encontrados: {empty_groups}")
                            return False
                        else:
                            print("✅ No hay grupos vacíos")
                    
                    return True
                    
                except json.JSONDecodeError:
                    print("❌ analysis.json no es JSON válido")
                    return False
            else:
                print("❌ No se creó analysis.json")
                return False
        else:
            print(f"❌ Comando analyze falla: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción en analyze: {e}")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

def validate_suggest_without_api():
    """Validar que suggest requiere API keys"""
    print("\n🤖 Validando validación de API keys...")
    
    test_dir = tempfile.mkdtemp()
    test_project = Path(test_dir) / "test_suggest"
    
    try:
        test_project.mkdir(parents=True)
        (test_project / "main.py").write_text("print('test')")
        
        # Primero hacer analyze
        result_analyze = subprocess.run(
            ["projectprompt", "analyze", "."],
            cwd=str(test_project),
            capture_output=True,
            text=True,
            env={k: v for k, v in os.environ.items() if not k.endswith("_API_KEY")}
        )
        
        if result_analyze.returncode == 0:
            print("✅ Analyze funciona sin API keys")
        else:
            print("❌ Analyze falla sin API keys (no debería)")
            return False
        
        # Luego probar suggest sin API keys
        result_suggest = subprocess.run(
            ["projectprompt", "suggest", "test_group"],
            cwd=str(test_project),
            capture_output=True,
            text=True,
            env={k: v for k, v in os.environ.items() if not k.endswith("_API_KEY")}
        )
        
        if result_suggest.returncode != 0:
            if "api key" in result_suggest.stderr.lower():
                print("✅ Suggest requiere API key correctamente")
                return True
            else:
                print(f"❌ Suggest falla por otra razón: {result_suggest.stderr}")
                return False
        else:
            print("❌ Suggest no requiere API key (debería requerirla)")
            return False
            
    except Exception as e:
        print(f"❌ Excepción en suggest validation: {e}")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

def measure_codebase_reduction():
    """Medir reducción del codebase"""
    print("\n📊 Midiendo reducción del codebase...")
    
    project_root = Path(__file__).parent
    
    def count_python_lines(directory):
        if not directory.exists():
            return 0
        
        total_lines = 0
        for py_file in directory.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Contar solo líneas no vacías y no comentarios
                    code_lines = [
                        line for line in lines 
                        if line.strip() and not line.strip().startswith('#')
                    ]
                    total_lines += len(code_lines)
            except Exception:
                continue
        
        return total_lines
    
    # Contar líneas
    src_new_lines = count_python_lines(project_root / "src_new")
    src_old_lines = count_python_lines(project_root / "src")
    
    print(f"📝 Código anterior (src/): {src_old_lines} líneas")
    print(f"📝 Código nuevo (src_new/): {src_new_lines} líneas")
    
    if src_old_lines > 0:
        reduction = ((src_old_lines - src_new_lines) / src_old_lines) * 100
        print(f"📉 Reducción: {reduction:.1f}%")
        
        if reduction >= 50:
            print("✅ Objetivo de reducción 50% alcanzado")
            return True
        else:
            print("❌ Objetivo de reducción 50% NO alcanzado")
            return False
    else:
        print(f"🆕 Nuevo codebase: {src_new_lines} líneas")
        if src_new_lines < 5000:
            print("✅ Codebase compacto")
            return True
        else:
            print("❌ Codebase demasiado grande")
            return False

def validate_performance_basic():
    """Validación básica de rendimiento"""
    print("\n⚡ Validando rendimiento básico...")
    
    test_dir = tempfile.mkdtemp()
    test_project = Path(test_dir) / "perf_test"
    
    try:
        test_project.mkdir(parents=True)
        
        # Crear proyecto de tamaño mediano
        for i in range(20):
            (test_project / f"file_{i}.py").write_text(f"# File {i}\nclass Class{i}:\n    pass")
        
        # Medir tiempo
        start_time = time.time()
        
        result = subprocess.run(
            ["projectprompt", "analyze", "."],
            cwd=str(test_project),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        analysis_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ Análisis completado en {analysis_time:.2f}s")
            
            if analysis_time < 30:
                print("✅ Rendimiento aceptable (<30s)")
                return True
            else:
                print("❌ Rendimiento lento (>30s)")
                return False
        else:
            print(f"❌ Análisis falló: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Análisis tomó demasiado tiempo (>30s)")
        return False
    except Exception as e:
        print(f"❌ Excepción en performance test: {e}")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

def main():
    """Función principal de validación"""
    print("🚀 VALIDACIÓN FASE 5 - TESTING Y OPTIMIZACIÓN")
    print("🎯 Objetivo: Validar calidad y rendimiento para release v2.0")
    print("=" * 70)
    
    start_time = time.time()
    results = {}
    
    # 1. CLI básico
    cli_results = validate_cli_basic()
    results.update(cli_results)
    
    # 2. Comando analyze
    results["analyze_works"] = validate_analyze_command()
    
    # 3. Validación API keys
    results["api_validation"] = validate_suggest_without_api()
    
    # 4. Reducción codebase
    results["codebase_reduction"] = measure_codebase_reduction()
    
    # 5. Rendimiento básico
    results["performance"] = validate_performance_basic()
    
    # Resumen final
    total_time = time.time() - start_time
    
    print("\n" + "=" * 70)
    print("📋 RESUMEN FINAL DE VALIDACIÓN")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v is True)
    total = len(results)
    
    print(f"\n✅ Tests pasados: {passed}/{total}")
    print("-" * 40)
    
    for key, value in results.items():
        status = "✅" if value else "❌"
        print(f"{status} {key}: {'PASS' if value else 'FAIL'}")
    
    print(f"\n⏱️  Tiempo total: {total_time:.1f}s")
    
    if passed == total:
        print("\n🎉 FASE 5 COMPLETADA EXITOSAMENTE")
        print("✅ Sistema listo para release v2.0")
        return 0
    else:
        print(f"\n⚠️  FASE 5 REQUIERE ATENCIÓN")
        print(f"❌ {total - passed} validaciones fallaron")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
