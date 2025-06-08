#!/usr/bin/env python3
"""
Fase 5 - Script de Validación Completa
Ejecuta todos los tests críticos y genera reporte de calidad para release v2.0
"""

import subprocess
import sys
import time
import json
from pathlib import Path
import os

class Phase5Validator:
    """Validador completo para Fase 5"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.results = {
            "start_time": time.time(),
            "tests": {},
            "metrics": {},
            "performance": {},
            "errors": []
        }
    
    def run_test_suite(self, test_file: str, description: str):
        """Ejecuta una suite de tests y registra resultados"""
        print(f"\n🧪 Ejecutando {description}...")
        print("=" * 60)
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", f"tests/{test_file}", "-v", "--tb=short"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            success = result.returncode == 0
            self.results["tests"][test_file] = {
                "success": success,
                "output": result.stdout,
                "errors": result.stderr,
                "description": description
            }
            
            if success:
                print(f"✅ {description}: PASSED")
            else:
                print(f"❌ {description}: FAILED")
                print(f"Error: {result.stderr}")
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {description}: TIMEOUT")
            self.results["tests"][test_file] = {
                "success": False,
                "output": "",
                "errors": "Test suite timed out",
                "description": description
            }
            return False
        except Exception as e:
            print(f"💥 {description}: EXCEPTION - {e}")
            self.results["tests"][test_file] = {
                "success": False,
                "output": "",
                "errors": str(e),
                "description": description
            }
            return False
    
    def validate_cli_functionality(self):
        """Valida funcionalidad básica del CLI"""
        print("\n🔧 Validando funcionalidad CLI básica...")
        
        # Test help command
        try:
            result = subprocess.run(
                ["projectprompt", "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            self.results["metrics"]["cli_help_works"] = result.returncode == 0
        except Exception:
            self.results["metrics"]["cli_help_works"] = False
        
        # Test version command
        try:
            result = subprocess.run(
                ["projectprompt", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            self.results["metrics"]["cli_version_works"] = result.returncode == 0
            if result.returncode == 0:
                self.results["metrics"]["version_output"] = result.stdout.strip()
        except Exception:
            self.results["metrics"]["cli_version_works"] = False
    
    def measure_codebase_metrics(self):
        """Mide métricas del codebase"""
        print("\n📊 Midiendo métricas del codebase...")
        
        # Contar líneas en src_new
        src_new_lines = self._count_python_lines(self.project_root / "src_new")
        self.results["metrics"]["src_new_lines"] = src_new_lines
        
        # Contar líneas en src (si existe)
        src_old_lines = self._count_python_lines(self.project_root / "src")
        self.results["metrics"]["src_old_lines"] = src_old_lines
        
        # Calcular reducción
        if src_old_lines > 0:
            reduction = ((src_old_lines - src_new_lines) / src_old_lines) * 100
            self.results["metrics"]["codebase_reduction_percent"] = reduction
            self.results["metrics"]["target_50_percent_reduction"] = reduction >= 50
        else:
            self.results["metrics"]["codebase_reduction_percent"] = 0
            self.results["metrics"]["target_50_percent_reduction"] = src_new_lines < 5000
        
        print(f"   📝 Código anterior: {src_old_lines} líneas")
        print(f"   📝 Código nuevo: {src_new_lines} líneas")
        if src_old_lines > 0:
            print(f"   📉 Reducción: {self.results['metrics']['codebase_reduction_percent']:.1f}%")
    
    def _count_python_lines(self, directory: Path) -> int:
        """Cuenta líneas de código Python en un directorio"""
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
    
    def validate_dependencies(self):
        """Valida que las dependencias estén instaladas"""
        print("\n📦 Validando dependencias...")
        
        required_packages = ['click', 'anthropic', 'openai', 'python-dotenv', 'psutil']
        
        for package in required_packages:
            try:
                result = subprocess.run(
                    [sys.executable, "-c", f"import {package}"],
                    capture_output=True,
                    text=True
                )
                self.results["metrics"][f"dependency_{package}"] = result.returncode == 0
            except Exception:
                self.results["metrics"][f"dependency_{package}"] = False
    
    def generate_report(self):
        """Genera reporte final de validación"""
        self.results["end_time"] = time.time()
        self.results["total_duration"] = self.results["end_time"] - self.results["start_time"]
        
        print("\n" + "=" * 80)
        print("📋 REPORTE FINAL DE VALIDACIÓN FASE 5")
        print("=" * 80)
        
        # Resumen de tests
        total_tests = len(self.results["tests"])
        passed_tests = sum(1 for test in self.results["tests"].values() if test["success"])
        
        print(f"\n🧪 TESTS EJECUTADOS: {passed_tests}/{total_tests} pasaron")
        print("-" * 40)
        
        for test_file, test_result in self.results["tests"].items():
            status = "✅ PASS" if test_result["success"] else "❌ FAIL"
            print(f"{status} {test_result['description']}")
        
        # Métricas críticas
        print(f"\n📊 MÉTRICAS CRÍTICAS")
        print("-" * 40)
        
        # Reducción del codebase
        reduction = self.results["metrics"].get("codebase_reduction_percent", 0)
        target_met = self.results["metrics"].get("target_50_percent_reduction", False)
        status = "✅" if target_met else "❌"
        print(f"{status} Reducción codebase: {reduction:.1f}% (objetivo: ≥50%)")
        
        # CLI funcional
        cli_help = self.results["metrics"].get("cli_help_works", False)
        cli_version = self.results["metrics"].get("cli_version_works", False)
        cli_status = "✅" if cli_help and cli_version else "❌"
        print(f"{cli_status} CLI funcional: help={cli_help}, version={cli_version}")
        
        # Versión
        version = self.results["metrics"].get("version_output", "unknown")
        version_status = "✅" if "2.0" in version else "❌"
        print(f"{version_status} Versión: {version}")
        
        # Estado general
        print(f"\n🎯 ESTADO GENERAL")
        print("-" * 40)
        
        all_tests_passed = passed_tests == total_tests
        critical_metrics_met = target_met and cli_help and cli_version
        
        if all_tests_passed and critical_metrics_met:
            print("🎉 FASE 5 COMPLETADA EXITOSAMENTE")
            print("✅ Todos los tests pasaron")
            print("✅ Métricas críticas alcanzadas")
            print("✅ Sistema listo para release v2.0")
            exit_code = 0
        else:
            print("⚠️  FASE 5 REQUIERE ATENCIÓN")
            if not all_tests_passed:
                print(f"❌ {total_tests - passed_tests} tests fallaron")
            if not critical_metrics_met:
                print("❌ Métricas críticas no alcanzadas")
            exit_code = 1
        
        print(f"\n⏱️  Duración total: {self.results['total_duration']:.1f} segundos")
        
        # Guardar reporte
        report_file = self.project_root / "phase5_validation_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"📄 Reporte guardado en: {report_file}")
        
        return exit_code
    
    def run_complete_validation(self):
        """Ejecuta validación completa de Fase 5"""
        print("🚀 INICIANDO VALIDACIÓN COMPLETA FASE 5")
        print("🎯 Objetivo: Validar calidad y rendimiento para release v2.0")
        print("=" * 80)
        
        # 1. Validar dependencias
        self.validate_dependencies()
        
        # 2. Validar CLI básico
        self.validate_cli_functionality()
        
        # 3. Medir métricas del codebase
        self.measure_codebase_metrics()
        
        # 4. Ejecutar tests críticos
        self.run_test_suite("test_core_functionality.py", "Tests de funcionalidad crítica")
        self.run_test_suite("test_performance.py", "Tests de rendimiento")
        self.run_test_suite("test_success_metrics.py", "Tests de métricas de éxito")
        
        # 5. Generar reporte final
        return self.generate_report()

def main():
    """Función principal"""
    validator = Phase5Validator()
    exit_code = validator.run_complete_validation()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
