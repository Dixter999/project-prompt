#!/usr/bin/env python3
"""
Script para reorganizar la estructura del proyecto ProjectPrompt
según las recomendaciones del análisis
"""

import os
import sys
import shutil
from pathlib import Path

# Colores para mensajes en terminal
class Colors:
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    RED = '\033[0;31m'
    YELLOW = '\033[0;33m'
    NC = '\033[0m'  # Sin Color

# Verificar que estamos en el directorio correcto
if not os.path.isfile("project_prompt.py") or not os.path.isdir("src"):
    print(f"{Colors.RED}Este script debe ejecutarse desde el directorio raíz del proyecto ProjectPrompt.{Colors.NC}")
    sys.exit(1)

print(f"{Colors.BLUE}=== Reorganización de Estructura del Proyecto ==={Colors.NC}")
print(f"{Colors.BLUE}================================================={Colors.NC}\n")

# Determinar si es un ensayo o ejecución real
DRY_RUN = True
if len(sys.argv) > 1 and sys.argv[1] == "--execute":
    DRY_RUN = False
    print(f"{Colors.YELLOW}EJECUCIÓN REAL: Los cambios se aplicarán al proyecto.{Colors.NC}")
else:
    print(f"{Colors.GREEN}ENSAYO: No se realizarán cambios. Use --execute para aplicar cambios.{Colors.NC}")

def create_dir(path):
    """Crear un directorio si no existe."""
    if DRY_RUN:
        print(f"  {Colors.BLUE}Crearía directorio: {path}{Colors.NC}")
    else:
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"  {Colors.GREEN}Creado directorio: {path}{Colors.NC}")
        else:
            print(f"  {Colors.YELLOW}El directorio ya existe: {path}{Colors.NC}")

def move_file(source, dest):
    """Mover un archivo de una ubicación a otra."""
    if DRY_RUN:
        print(f"  {Colors.BLUE}Movería: {source} -> {dest}{Colors.NC}")
    else:
        if os.path.isfile(source):
            # Crear el directorio destino si no existe
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            
            # Mover el archivo
            shutil.move(source, dest)
            print(f"  {Colors.GREEN}Movido: {source} -> {dest}{Colors.NC}")
        else:
            print(f"  {Colors.RED}No se encontró el archivo: {source}{Colors.NC}")

def create_symlink(target, link_name):
    """Crear un enlace simbólico."""
    if DRY_RUN:
        print(f"  {Colors.BLUE}Crearía enlace simbólico: {link_name} -> {target}{Colors.NC}")
    else:
        try:
            # Si ya existe, eliminarlo primero
            if os.path.exists(link_name):
                os.remove(link_name)
                
            os.symlink(target, link_name)
            print(f"  {Colors.GREEN}Creado enlace simbólico: {link_name} -> {target}{Colors.NC}")
        except Exception as e:
            print(f"  {Colors.RED}Error al crear enlace simbólico: {str(e)}{Colors.NC}")

# 1. Crear estructura de directorios mejorada
print(f"\n{Colors.YELLOW}1. Creando estructura de directorios mejorada...{Colors.NC}")
directories = [
    "tools/scripts",
    "tools/ci",
    "tools/utils",
    "docs/development",
    "docs/api",
    "docs/user",
    "bin"
]

for directory in directories:
    create_dir(directory)

# 2. Reorganizar scripts de shell
print(f"\n{Colors.YELLOW}2. Reorganizando scripts de shell...{Colors.NC}")
shell_scripts = [f for f in os.listdir('.') if f.endswith('.sh') and f != "setup_environment.sh"]

for script in shell_scripts:
    dest_path = os.path.join("tools/scripts", script)
    move_file(script, dest_path)
    
    # Crear un enlace simbólico para mantener la compatibilidad
    if not DRY_RUN:
        create_symlink(dest_path, script)

# 3. Reorganizar scripts de utilidad
print(f"\n{Colors.YELLOW}3. Reorganizando scripts de utilidad...{Colors.NC}")
utility_scripts = [
    "fix_config_in_telemetry.py",
    "set_anthropic_key.py",
    "structure_improvement.py",
    "verify_freemium_system.py"
]

for script in utility_scripts:
    if os.path.isfile(script):
        move_file(script, os.path.join("tools/utils", script))

# 4. Mover archivos de fases a documentación
print(f"\n{Colors.YELLOW}4. Reorganizando documentación...{Colors.NC}")
if os.path.isdir("fases"):
    create_dir("docs/development/fases")
    phase_files = [f for f in os.listdir('fases') if f.endswith('.md')]
    
    for phase_file in phase_files:
        move_file(os.path.join("fases", phase_file), 
                  os.path.join("docs/development/fases", phase_file))
    
    # Eliminar directorio vacío
    if not DRY_RUN and os.path.isdir("fases"):
        if not os.listdir("fases"):
            os.rmdir("fases")
            print(f"  {Colors.GREEN}Eliminado directorio vacío: fases{Colors.NC}")

# 5. Crear enlaces simbólicos en bin
print(f"\n{Colors.YELLOW}5. Creando enlaces simbólicos en bin/ para comandos principales...{Colors.NC}")
main_scripts = {
    "project_prompt.py": "bin/project-prompt",
    "quick_analyze.py": "bin/quick-analyze",
    "simple_analyze.py": "bin/simple-analyze"
}

for source, link in main_scripts.items():
    if os.path.isfile(source):
        create_symlink(f"../{source}", link)
        if not DRY_RUN:
            os.chmod(link, 0o755)  # Hacer ejecutable

# 6. Limpiar archivos .pyc y directorios __pycache__
print(f"\n{Colors.YELLOW}6. Eliminando archivos pyc y directorios __pycache__...{Colors.NC}")
if DRY_RUN:
    print(f"  {Colors.BLUE}Eliminaría archivos .pyc y directorios __pycache__{Colors.NC}")
else:
    # Eliminar archivos .pyc
    pyc_files = []
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                pyc_path = os.path.join(root, file)
                pyc_files.append(pyc_path)
                os.remove(pyc_path)
    
    print(f"  {Colors.GREEN}Eliminados {len(pyc_files)} archivos .pyc{Colors.NC}")
    
    # Eliminar directorios __pycache__
    pycache_dirs = []
    for root, dirs, _ in os.walk('.'):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                pycache_path = os.path.join(root, dir_name)
                pycache_dirs.append(pycache_path)
                shutil.rmtree(pycache_path)
    
    print(f"  {Colors.GREEN}Eliminados {len(pycache_dirs)} directorios __pycache__{Colors.NC}")

print(f"\n{Colors.GREEN}=== Proceso completado ==={Colors.NC}")
if DRY_RUN:
    print(f"{Colors.YELLOW}Este fue un ensayo. Ejecute con --execute para aplicar los cambios.{Colors.NC}")
    print(f"{Colors.YELLOW}Comando: python restructure_project.py --execute{Colors.NC}")
else:
    print(f"{Colors.GREEN}La estructura del proyecto ha sido reorganizada con éxito.{Colors.NC}")
    print(f"{Colors.YELLOW}Nota: Puede ser necesario actualizar rutas en scripts o importaciones.{Colors.NC}")
