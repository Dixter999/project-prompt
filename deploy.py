#!/usr/bin/env python3
"""
Deployment script for ProjectPrompt

This script handles the entire deployment process for ProjectPrompt:
1. Runs all tests to verify system functionality
2. Builds packages for distribution
3. Creates documentation
4. Prepares release artifacts

Usage:
    python deploy.py [options]

Options:
    --test-only      Only run tests without packaging
    --build-only     Skip tests and only build packages
    --no-docs        Skip documentation generation
    --release        Create a full release with version tag
"""

import os
import sys
import argparse
import subprocess
import datetime
import shutil
from pathlib import Path

# Configuración
VERSION = "1.0.0"  # Leer de config o incrementar automáticamente
PACKAGES = ["sdist", "bdist_wheel"]
PLATFORMS = ["win32", "linux", "darwin"]

def run_command(cmd, description=None, check=True, capture_output=False):
    """Ejecuta un comando y devuelve su salida"""
    if description:
        print(f"\n[*] {description}")
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, capture_output=capture_output)

def run_tests():
    """Ejecuta todas las pruebas del sistema"""
    print("\n=== Ejecutando pruebas ===")
    
    # Pruebas unitarias básicas
    run_command([sys.executable, "-m", "unittest", "discover", "-s", "tests"], 
               "Ejecutando pruebas unitarias")
    
    # Pruebas de integración
    run_command([sys.executable, "run_complete_test.sh"], 
               "Ejecutando pruebas de integración")
               
    # Pruebas del sistema freemium
    run_command([sys.executable, "test_freemium_system.py"], 
               "Verificando sistema freemium")
               
    # Pruebas de integración con Anthropic
    run_command([sys.executable, "test_anthropic_integration.py"], 
               "Verificando integración con Anthropic")
               
    print("\n✅ Todas las pruebas completadas exitosamente")

def build_packages():
    """Construye los paquetes para distribución"""
    print("\n=== Generando paquetes de distribución ===")
    
    # Limpiar directorio dist
    dist_dir = Path("./dist")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(exist_ok=True)
    
    # Construir paquetes con setuptools
    cmd = [sys.executable, "setup.py"]
    cmd.extend(PACKAGES)
    run_command(cmd, "Construyendo paquetes de distribución")
    
    print(f"\n✅ Paquetes generados en {dist_dir.absolute()}")

def generate_docs():
    """Genera la documentación actualizada"""
    print("\n=== Generando documentación ===")
    
    # Actualizar versión en la documentación
    version_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Lista de archivos de documentación a actualizar
    doc_files = [
        "docs/complete_documentation.md",
        "docs/user_guide.md",
        "README.md"
    ]
    
    for doc_file in doc_files:
        try:
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Actualizar versión y fecha
            content = content.replace("{{VERSION}}", VERSION)
            content = content.replace("{{DATE}}", version_date)
            
            with open(doc_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"✓ Actualizado {doc_file}")
        except Exception as e:
            print(f"⚠ Error actualizando {doc_file}: {e}")
    
    print("\n✅ Documentación actualizada")

def create_release():
    """Crea los artefactos para una release completa"""
    print("\n=== Preparando release ===")
    
    # Crear tag de versión en git
    run_command(["git", "tag", f"v{VERSION}"], 
               f"Creando tag v{VERSION}")
    
    # Crear archivo release con notas de la versión
    release_notes = f"""# ProjectPrompt v{VERSION}

Fecha: {datetime.datetime.now().strftime("%Y-%m-%d")}

## Cambios en esta versión

- Implementación completa del sistema de análisis de proyectos
- Integración con API de Anthropic
- Sistema Freemium para funcionalidades premium
- Mejoras en la generación de prompts contextualizados

## Instrucciones de instalación

```bash
pip install project-prompt=={VERSION}
```

## Documentación

Consulta la documentación completa en https://github.com/usuario/project-prompt/docs
"""
    
    with open(f"release-notes-v{VERSION}.md", "w", encoding="utf-8") as f:
        f.write(release_notes)
    
    print(f"\n✅ Release v{VERSION} preparada")
    print(f"📝 Notas de release generadas en release-notes-v{VERSION}.md")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Despliegue de ProjectPrompt")
    parser.add_argument("--test-only", action="store_true", help="Solo ejecutar pruebas")
    parser.add_argument("--build-only", action="store_true", help="Solo construir paquetes")
    parser.add_argument("--no-docs", action="store_true", help="Omitir generación de documentación")
    parser.add_argument("--release", action="store_true", help="Crear release completa")
    
    args = parser.parse_args()
    
    print(f"=== ProjectPrompt v{VERSION} - Proceso de Despliegue ===")
    print(f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not args.build_only:
        run_tests()
    
    if not args.test_only:
        build_packages()
        
        if not args.no_docs:
            generate_docs()
    
    if args.release:
        create_release()
    
    print("\n✅ Proceso de despliegue completado")

if __name__ == "__main__":
    main()
