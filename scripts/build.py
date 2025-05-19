#!/usr/bin/env python3
"""
Script de construcción para ProjectPrompt.
Este script facilita la generación de paquetes y ejecutables para distribución.
"""

import os
import sys
import shutil
import subprocess
import platform
import argparse
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path(__file__).parent.parent.absolute()
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
VSCODE_EXT_DIR = PROJECT_ROOT / "vscode-extension"
PACKAGE_NAME = "project-prompt"


def setup_environment():
    """Preparar el entorno para la construcción."""
    print("Configurando entorno de construcción...")
    
    # Crear directorios si no existen
    os.makedirs(BUILD_DIR, exist_ok=True)
    os.makedirs(DIST_DIR, exist_ok=True)
    
    # Limpieza de compilados previos
    print("Limpiando compilados previos...")
    for pattern in ["*.pyc", "*.pyo", "*.pyd", "*.so", "*.dll"]:
        clean_pattern(pattern)
    
    # Verificar dependencias
    print("Verificando dependencias...")
    if not shutil.which("poetry"):
        print("ADVERTENCIA: Poetry no encontrado. Se recomienda para gestionar dependencias.")
    
    if not shutil.which("pyinstaller"):
        print("ADVERTENCIA: PyInstaller no encontrado. Requerido para crear ejecutables.")


def clean_pattern(pattern):
    """Eliminar archivos que coincidan con el patrón."""
    import glob
    for item in glob.glob(str(PROJECT_ROOT / "**" / pattern), recursive=True):
        try:
            os.remove(item)
            print(f"Eliminado: {item}")
        except Exception as e:
            print(f"Error al eliminar {item}: {e}")


def build_package():
    """Construir paquete Python usando Poetry."""
    print("\n=== Construyendo paquete Python ===")
    
    try:
        # Construir usando Poetry si está disponible
        if shutil.which("poetry"):
            print("Construyendo con Poetry...")
            subprocess.run(["poetry", "build"], cwd=PROJECT_ROOT, check=True)
        # Fallback a setuptools
        else:
            print("Construyendo con setuptools...")
            subprocess.run([sys.executable, "setup.py", "sdist", "bdist_wheel"], 
                          cwd=PROJECT_ROOT, check=True)
        
        print("Paquete Python construido exitosamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al construir paquete Python: {e}")
        return False
    
    return True


def build_executable():
    """Construir ejecutables con PyInstaller."""
    print("\n=== Construyendo ejecutables ===")
    
    if not shutil.which("pyinstaller"):
        print("PyInstaller no encontrado. Instalando...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        except subprocess.CalledProcessError:
            print("Error al instalar PyInstaller. Abortando construcción de ejecutables.")
            return False
    
    # Obtener información del sistema
    system = platform.system().lower()
    architecture = platform.architecture()[0]
    
    print(f"Construyendo para: {system} {architecture}")
    
    # Definir nombre del ejecutable según plataforma
    exe_extension = ".exe" if system == "windows" else ""
    output_name = f"{PACKAGE_NAME}-{system}-{architecture}{exe_extension}"
    
    try:
        # Configurar argumentos de PyInstaller
        pyinstaller_args = [
            "pyinstaller",
            "--onefile",
            "--name", output_name,
            "--icon", str(PROJECT_ROOT / "assets" / "icon.ico") if os.path.exists(
                str(PROJECT_ROOT / "assets" / "icon.ico")) else "",
            "--add-data", f"{PROJECT_ROOT / 'templates'}:templates",
            "--noconfirm",
            "--clean",
            str(PROJECT_ROOT / "src" / "main.py")
        ]
        
        # Filtrar argumentos vacíos
        pyinstaller_args = [arg for arg in pyinstaller_args if arg]
        
        # Ejecutar PyInstaller
        subprocess.run(pyinstaller_args, cwd=PROJECT_ROOT, check=True)
        
        # Mover ejecutable a directorio de distribución
        for file in os.listdir(DIST_DIR):
            if file.startswith(PACKAGE_NAME):
                src_path = os.path.join(DIST_DIR, file)
                dst_path = os.path.join(DIST_DIR, f"{output_name}")
                if src_path != dst_path:
                    shutil.move(src_path, dst_path)
                    print(f"Ejecutable renombrado: {dst_path}")
        
        print(f"Ejecutable construido exitosamente: {output_name}")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"Error al construir ejecutable: {e}")
        return False


def build_vscode_extension():
    """Construir extensión de VS Code."""
    print("\n=== Construyendo extensión VS Code ===")
    
    if not os.path.exists(VSCODE_EXT_DIR):
        print("Directorio de extensión VS Code no encontrado. Omitiendo.")
        return False
    
    # Verificar si vsce está instalado
    if not shutil.which("vsce"):
        print("vsce no encontrado. Intentando instalar...")
        try:
            subprocess.run(["npm", "install", "-g", "vsce"], check=True)
        except subprocess.CalledProcessError:
            print("Error al instalar vsce. Abortando construcción de extensión.")
            return False
    
    try:
        # Instalar dependencias
        subprocess.run(["npm", "install"], cwd=VSCODE_EXT_DIR, check=True)
        
        # Construir la extensión
        subprocess.run(["vsce", "package"], cwd=VSCODE_EXT_DIR, check=True)
        
        # Mover el archivo .vsix al directorio dist
        for file in os.listdir(VSCODE_EXT_DIR):
            if file.endswith(".vsix"):
                src_path = os.path.join(VSCODE_EXT_DIR, file)
                dst_path = os.path.join(DIST_DIR, file)
                shutil.move(src_path, dst_path)
                print(f"Extensión VS Code construida: {dst_path}")
        
        print("Extensión VS Code construida exitosamente.")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"Error al construir extensión VS Code: {e}")
        return False


def create_release_notes():
    """Crear notas de lanzamiento."""
    print("\n=== Generando notas de lanzamiento ===")
    
    try:
        from src import __version__
        version = __version__
    except ImportError:
        version = "desconocida"
    
    release_notes_path = DIST_DIR / "RELEASE_NOTES.md"
    
    with open(release_notes_path, "w") as f:
        f.write(f"# ProjectPrompt {version} - Notas de lanzamiento\n\n")
        f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}\n\n")
        f.write("## Novedades\n\n")
        f.write("- Versión inicial estable\n")
        f.write("- Sistema completo de análisis y documentación de proyectos\n")
        f.write("- Integración con múltiples modelos de IA\n")
        f.write("- Extensión para Visual Studio Code\n\n")
        f.write("## Instrucciones de instalación\n\n")
        f.write("### Instalación desde PyPI\n\n")
        f.write("```\npip install project-prompt\n```\n\n")
        f.write("### Instalación desde ejecutable\n\n")
        f.write("Descarga el ejecutable adecuado para tu sistema operativo y ejecútalo directamente.\n\n")
    
    print(f"Notas de lanzamiento generadas: {release_notes_path}")
    return True


def main():
    """Función principal del script de construcción."""
    parser = argparse.ArgumentParser(description='Script de construcción para ProjectPrompt')
    parser.add_argument('--package-only', action='store_true', help='Construir solo el paquete Python')
    parser.add_argument('--exe-only', action='store_true', help='Construir solo el ejecutable')
    parser.add_argument('--vscode-only', action='store_true', help='Construir solo la extensión de VS Code')
    parser.add_argument('--all', action='store_true', help='Construir todo (por defecto)')
    
    args = parser.parse_args()
    
    # Si no se especifica ninguna opción, construir todo
    build_all = not (args.package_only or args.exe_only or args.vscode_only) or args.all
    
    try:
        setup_environment()
        
        if build_all or args.package_only:
            build_package()
        
        if build_all or args.exe_only:
            build_executable()
        
        if build_all or args.vscode_only:
            build_vscode_extension()
        
        if build_all:
            create_release_notes()
            
        print("\n=== Proceso de construcción completado ===")
        print(f"Los archivos de distribución se encuentran en: {DIST_DIR}")
        
    except Exception as e:
        print(f"Error durante el proceso de construcción: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
