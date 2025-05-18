#!/usr/bin/env python3
"""
Script de prueba para verificar la configuración de paquete.
Este script intenta construir un paquete de prueba para verificar
que la configuración de empaquetado está correcta.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path


def check_build_dependencies():
    """Verificar que las dependencias necesarias están instaladas."""
    print("Verificando dependencias para construcción...")
    
    try:
        import build
        print("✓ Módulo 'build' encontrado.")
    except ImportError:
        print("✗ Módulo 'build' no encontrado, instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "build"], check=True)

    try:
        import wheel
        print("✓ Módulo 'wheel' encontrado.")
    except ImportError:
        print("✗ Módulo 'wheel' no encontrado, instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "wheel"], check=True)


def build_test_package():
    """Construir un paquete de prueba."""
    print("\nConstruyendo paquete de prueba...")
    
    # Crear un directorio temporal para la construcción
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        try:
            # Construir el paquete
            subprocess.run(
                [
                    sys.executable, 
                    "-m", 
                    "build", 
                    "--outdir", 
                    str(temp_path),
                    "."
                ], 
                check=True
            )
            
            # Verificar que se crearon los archivos
            wheel_files = list(temp_path.glob("*.whl"))
            sdist_files = list(temp_path.glob("*.tar.gz"))
            
            if wheel_files:
                print(f"✓ Wheel creado: {wheel_files[0].name}")
            else:
                print("✗ No se pudo crear el wheel.")
                
            if sdist_files:
                print(f"✓ Sdist creado: {sdist_files[0].name}")
            else:
                print("✗ No se pudo crear el sdist.")
                
            # Copiar los archivos al directorio dist si existen
            dist_dir = Path("dist")
            dist_dir.mkdir(exist_ok=True)
            
            for file in wheel_files + sdist_files:
                dest_file = dist_dir / file.name
                print(f"Copiando {file.name} a {dest_file}")
                shutil.copy(file, dest_file)
                
            return bool(wheel_files or sdist_files)
                
        except subprocess.CalledProcessError as e:
            print(f"Error al construir el paquete: {e}")
            return False


def validate_package_metadata():
    """Validar los metadatos del paquete."""
    print("\nValidando metadatos del paquete...")
    
    try:
        # Instalar twine si no está disponible
        try:
            import twine
        except ImportError:
            print("Instalando twine...")
            subprocess.run([sys.executable, "-m", "pip", "install", "twine"], check=True)
        
        # Verificar si existen archivos en dist/
        dist_dir = Path("dist")
        if not dist_dir.exists() or not any(dist_dir.iterdir()):
            print("No hay archivos en dist/ para validar.")
            return False
            
        # Validar con twine
        result = subprocess.run(
            [sys.executable, "-m", "twine", "check", "dist/*"],
            check=False,  # No abortar si hay errores
            capture_output=True,
            text=True
        )
        
        # Mostrar salida de twine
        print(result.stdout)
        
        if result.returncode != 0:
            print(f"Errores en la validación: {result.stderr}")
            return False
            
        return True
    
    except Exception as e:
        print(f"Error al validar el paquete: {e}")
        return False


def main():
    """Función principal."""
    try:
        # Verificar dependencias
        check_build_dependencies()
        
        # Construir paquete de prueba
        if build_test_package():
            print("\n✓ Paquete construido correctamente.")
        else:
            print("\n✗ Error al construir el paquete.")
            return 1
            
        # Validar metadatos
        if validate_package_metadata():
            print("\n✓ Metadatos del paquete validados correctamente.")
        else:
            print("\n✗ Errores en los metadatos del paquete.")
            return 1
            
        print("\n✓ ¡Configuración de empaquetado lista para distribución!")
        return 0
        
    except Exception as e:
        print(f"\nError inesperado: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
