#!/usr/bin/env python3
"""
Inicializador de proyecto básico para project-prompt
"""
import os
import sys
import shutil
import argparse

def init_project(name, path="."):
    """Inicializar un proyecto básico"""
    # Crear estructura de directorios
    project_path = os.path.join(path, name)
    
    if os.path.exists(project_path):
        print(f"Error: El directorio {project_path} ya existe.")
        return False
    
    try:
        print(f"Creando estructura básica para '{name}'...")
        os.makedirs(project_path, exist_ok=True)
        
        # Crear directorios básicos
        dirs = ["src", "tests", "docs"]
        for d in dirs:
            os.makedirs(os.path.join(project_path, d), exist_ok=True)
            print(f"Creado directorio: {d}/")
        
        # Crear archivos básicos
        create_readme(project_path, name)
        create_setup_py(project_path, name)
        create_gitignore(project_path)
        create_basic_src(project_path, name)
        create_basic_test(project_path, name)
        
        print("\nEstructura de proyecto creada exitosamente.")
        print(f"\nPara comenzar a trabajar con tu proyecto:")
        print(f"  cd {name}")
        print(f"  python -m src.main")
        
        return True
        
    except Exception as e:
        print(f"Error al inicializar proyecto: {e}")
        return False

def create_readme(project_path, name):
    """Crear un archivo README.md básico"""
    content = f"""# {name}

Proyecto generado con project-prompt.

## Instalación

```bash
# Con pip
pip install -e .

# Con Poetry
poetry install
```

## Uso

```bash
# Ejecutar aplicación
python -m src.main
```
"""
    with open(os.path.join(project_path, "README.md"), "w") as f:
        f.write(content)
    print("Creado archivo: README.md")

def create_setup_py(project_path, name):
    """Crear un archivo setup.py básico"""
    snake_case_name = name.replace('-', '_').replace(' ', '_').lower()
    
    content = f"""#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="{name}",
    version="0.1.0",
    description="Proyecto generado con project-prompt",
    author="Su Nombre",
    author_email="su.email@example.com",
    packages=find_packages(),
    install_requires=[
        "typer",
        "rich",
    ],
    entry_points={{
        "console_scripts": [
            "{snake_case_name}=src.main:app",
        ],
    }},
)
"""
    with open(os.path.join(project_path, "setup.py"), "w") as f:
        f.write(content)
    print("Creado archivo: setup.py")

def create_gitignore(project_path):
    """Crear un archivo .gitignore básico"""
    content = """# Archivos generados
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Entornos virtuales
env/
venv/
ENV/
env.bak/
venv.bak/

# Archivos de configuración
.idea/
.vscode/
*.swp
*.swo
.DS_Store
"""
    with open(os.path.join(project_path, ".gitignore"), "w") as f:
        f.write(content)
    print("Creado archivo: .gitignore")

def create_basic_src(project_path, name):
    """Crear archivos básicos en src"""
    # Crear __init__.py
    init_content = f"""\"\"\"Proyecto {name}\"\"\"

__version__ = "0.1.0"
"""
    src_dir = os.path.join(project_path, "src")
    with open(os.path.join(src_dir, "__init__.py"), "w") as f:
        f.write(init_content)
    print("Creado archivo: src/__init__.py")
    
    # Crear main.py
    snake_case_name = name.replace('-', '_').replace(' ', '_').lower()
    main_content = f"""#!/usr/bin/env python
# -*- coding: utf-8 -*-
\"\"\"
Punto de entrada principal para {name}.
\"\"\"

import typer
from rich.console import Console

app = typer.Typer(help="{name}: Descripción de la aplicación")
console = Console()

@app.command()
def hello(name: str = "World"):
    \"\"\"Saludar al usuario.\"\"\"
    console.print(f"[bold green]¡Hola {{name}}![/bold green]")

@app.command()
def version():
    \"\"\"Mostrar la versión de la aplicación.\"\"\"
    from src import __version__
    console.print(f"[bold]{name}[/bold] versión: {{__version__}}")

if __name__ == "__main__":
    app()
"""
    with open(os.path.join(src_dir, "main.py"), "w") as f:
        f.write(main_content)
    print("Creado archivo: src/main.py")

def create_basic_test(project_path, name):
    """Crear archivos básicos de prueba"""
    test_dir = os.path.join(project_path, "tests")
    
    # Crear __init__.py
    with open(os.path.join(test_dir, "__init__.py"), "w") as f:
        f.write("")
    print("Creado archivo: tests/__init__.py")
    
    # Crear test_basic.py
    test_content = """#!/usr/bin/env python
# -*- coding: utf-8 -*-
\"\"\"
Pruebas básicas para la aplicación.
\"\"\"

def test_version():
    \"\"\"Probar que la versión existe.\"\"\"
    from src import __version__
    assert __version__ is not None
"""
    with open(os.path.join(test_dir, "test_basic.py"), "w") as f:
        f.write(test_content)
    print("Creado archivo: tests/test_basic.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inicializar un proyecto básico")
    parser.add_argument("name", help="Nombre del proyecto")
    parser.add_argument("--path", default=".", help="Ruta donde crear el proyecto")
    
    args = parser.parse_args()
    init_project(args.name, args.path)
