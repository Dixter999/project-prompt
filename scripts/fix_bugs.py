#!/usr/bin/env python3
"""
Script para identificar y corregir errores comunes en ProjectPrompt.
Este script implementa revisiones automatizadas y correcciones para problemas
frecuentes encontrados durante las pruebas.
"""

import os
import sys
import re
import argparse
import logging
from pathlib import Path
import importlib.util
import subprocess
import json
from typing import List, Dict, Any, Optional, Tuple

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("bugfix")

# Ruta raíz del proyecto
PROJECT_ROOT = Path(__file__).parent.parent.absolute()


class BugFixRunner:
    """Clase para ejecutar verificaciones y correcciones automáticas."""
    
    def __init__(self, project_path: Path, auto_fix: bool = False):
        """
        Inicializa el corrector de errores.
        
        Args:
            project_path: Ruta al proyecto
            auto_fix: Si es True, corregirá automáticamente los problemas
        """
        self.project_path = project_path
        self.auto_fix = auto_fix
        self.issues_found = []
        self.fixes_applied = []
        
    def run_all_checks(self) -> None:
        """Ejecutar todas las verificaciones disponibles."""
        logger.info("Ejecutando todas las verificaciones...")
        
        self.check_import_errors()
        self.check_missing_init_files()
        self.check_circular_imports()
        self.check_inconsistent_versions()
        self.check_config_compatibility()
        self.check_api_key_handling()
        
        # Resumen final
        if self.issues_found:
            logger.warning(f"Se encontraron {len(self.issues_found)} problemas.")
            for i, issue in enumerate(self.issues_found, 1):
                logger.warning(f"{i}. {issue}")
                
            if self.fixes_applied:
                logger.info(f"Se aplicaron {len(self.fixes_applied)} correcciones.")
                for i, fix in enumerate(self.fixes_applied, 1):
                    logger.info(f"{i}. {fix}")
            elif self.auto_fix:
                logger.info("No se pudieron aplicar correcciones automáticas.")
        else:
            logger.info("No se encontraron problemas. ¡El código parece estar en buen estado!")
        
    def check_import_errors(self) -> None:
        """Verificar errores de importación en los módulos."""
        logger.info("Verificando errores de importación...")
        
        # Buscar todos los archivos Python en el proyecto
        python_files = list(self.project_path.glob("**/*.py"))
        
        for py_file in python_files:
            # Ignorar la carpeta de pruebas y de caché
            if "__pycache__" in str(py_file) or "/venv/" in str(py_file):
                continue
                
            # Verificar importaciones
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(py_file)],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    error_msg = f"Error de importación en {py_file.relative_to(self.project_path)}: {result.stderr}"
                    self.issues_found.append(error_msg)
                    
                    # Intentar corregir problemas comunes
                    if self.auto_fix:
                        fixed = self._fix_import_error(py_file, result.stderr)
                        if fixed:
                            self.fixes_applied.append(f"Corregido error de importación en {py_file.relative_to(self.project_path)}")
                    
            except Exception as e:
                logger.error(f"Error al verificar {py_file}: {e}")
    
    def check_missing_init_files(self) -> None:
        """Verificar archivos __init__.py faltantes en paquetes Python."""
        logger.info("Verificando archivos __init__.py faltantes...")
        
        # Buscar todos los directorios que contienen archivos .py
        py_dirs = set()
        for py_file in self.project_path.glob("**/*.py"):
            if "__pycache__" in str(py_file) or "/venv/" in str(py_file):
                continue
            py_dirs.add(py_file.parent)
        
        # Verificar que cada directorio tenga un __init__.py
        for py_dir in py_dirs:
            init_file = py_dir / "__init__.py"
            if not init_file.exists() and py_dir.name != "scripts":
                rel_dir = py_dir.relative_to(self.project_path)
                self.issues_found.append(f"Falta archivo __init__.py en {rel_dir}")
                
                # Crear archivo __init__.py si se solicita corrección automática
                if self.auto_fix:
                    with open(init_file, 'w') as f:
                        module_name = py_dir.name
                        f.write(f'"""Paquete {module_name} para ProjectPrompt."""\n')
                    self.fixes_applied.append(f"Creado archivo __init__.py en {rel_dir}")
    
    def check_circular_imports(self) -> None:
        """Verificar importaciones circulares en el código."""
        logger.info("Verificando importaciones circulares...")
        
        # Utilizamos pylint para detectar importaciones circulares
        try:
            result = subprocess.run(
                ["pylint", "--disable=all", "--enable=cyclic-import", str(self.project_path / "src")],
                capture_output=True,
                text=True
            )
            
            if "cyclic-import" in result.stdout:
                # Extraer información de importaciones circulares
                for line in result.stdout.split('\n'):
                    if "cyclic-import" in line:
                        self.issues_found.append(f"Importación circular: {line}")
        except FileNotFoundError:
            logger.warning("pylint no está instalado. No se pudieron verificar importaciones circulares.")
    
    def check_inconsistent_versions(self) -> None:
        """Verificar inconsistencias de versión entre diferentes archivos."""
        logger.info("Verificando consistencia de versiones...")
        
        version_map = {}
        
        # Leer versión de src/__init__.py
        init_path = self.project_path / "src" / "__init__.py"
        if init_path.exists():
            with open(init_path, 'r') as f:
                content = f.read()
                version_match = re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', content)
                if version_match:
                    version_map["src/__init__.py"] = version_match.group(1)
        
        # Leer versión de pyproject.toml
        pyproject_path = self.project_path / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, 'r') as f:
                content = f.read()
                version_match = re.search(r'version\s*=\s*[\'"]([^\'"]+)[\'"]', content)
                if version_match:
                    version_map["pyproject.toml"] = version_match.group(1)
        
        # Leer versión de setup.py si existe
        setup_path = self.project_path / "setup.py"
        if setup_path.exists():
            with open(setup_path, 'r') as f:
                content = f.read()
                version_match = re.search(r'version\s*=\s*[\'"]?([^\'"]+)[\'"]?,', content)
                if version_match:
                    version_map["setup.py"] = version_match.group(1)
        
        # Comprobar inconsistencias
        if len(version_map) >= 2:  # Solo si tenemos al menos dos versiones para comparar
            versions = list(version_map.values())
            reference_version = versions[0]
            
            for file, version in version_map.items():
                if version != reference_version:
                    self.issues_found.append(
                        f"Inconsistencia de versión: {file} tiene {version}, "
                        f"pero la versión de referencia es {reference_version}"
                    )
                    
                    # Corregir automáticamente si se solicita
                    if self.auto_fix:
                        self._fix_version(file, version, reference_version)
    
    def check_config_compatibility(self) -> None:
        """Verificar problemas de compatibilidad en la configuración."""
        logger.info("Verificando compatibilidad de configuración...")
        
        config_example_path = self.project_path / "config.yaml.example"
        if not config_example_path.exists():
            return
            
        try:
            import yaml
            with open(config_example_path, 'r') as f:
                config_example = yaml.safe_load(f)
            
            # Verificar que la configuración de ejemplo tenga las secciones necesarias
            required_sections = ["api_keys", "prompt_templates", "default_ai_service"]
            for section in required_sections:
                if section not in config_example:
                    self.issues_found.append(
                        f"La configuración de ejemplo no contiene la sección '{section}'"
                    )
        except ImportError:
            logger.warning("PyYAML no está instalado. No se pudo verificar la configuración.")
        except Exception as e:
            self.issues_found.append(f"Error al analizar la configuración de ejemplo: {e}")
    
    def check_api_key_handling(self) -> None:
        """Verificar el manejo seguro de claves API."""
        logger.info("Verificando manejo de claves API...")
        
        # Buscar patrones de claves API hardcodeadas
        api_key_patterns = [
            r'api_key\s*=\s*[\'"]([^\'"]{10,})[\'"]',
            r'API_KEY\s*=\s*[\'"]([^\'"]{10,})[\'"]',
            r'sk-[a-zA-Z0-9]{20,}'  # Patrón para claves de OpenAI
        ]
        
        for py_file in self.project_path.glob("**/*.py"):
            if "__pycache__" in str(py_file) or "/venv/" in str(py_file) or "/tests/" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    
                    for pattern in api_key_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            self.issues_found.append(
                                f"Posible clave API hardcodeada en {py_file.relative_to(self.project_path)}"
                            )
                            
                            # No corregir automáticamente esta clase de problemas ya que requiere
                            # una revisión manual cuidadosa
                            break
            except Exception as e:
                logger.error(f"Error al verificar {py_file}: {e}")
    
    def _fix_import_error(self, file_path: Path, error_message: str) -> bool:
        """
        Intentar corregir un error de importación.
        
        Args:
            file_path: Ruta al archivo con error
            error_message: Mensaje de error de importación
            
        Returns:
            True si se aplicó una corrección, False en caso contrario
        """
        try:
            with open(file_path, 'r') as f:
                content = f.readlines()
                
            # Buscar problemas comunes y aplicar correcciones
            
            # Problema 1: Import relativo incorrecto
            module_missing_match = re.search(r'No module named \'([^\']+)\'', error_message)
            if module_missing_match:
                missing_module = module_missing_match.group(1)
                
                # Determinar si es un módulo interno o una dependencia externa
                is_internal = missing_module.startswith('src')
                
                modified = False
                for i, line in enumerate(content):
                    # Corregir importaciones relativas
                    if f"import {missing_module}" in line or f"from {missing_module}" in line:
                        if is_internal and not line.startswith("from src"):
                            # Añadir prefijo 'src.' si es un módulo interno
                            content[i] = line.replace(
                                f"from {missing_module}", 
                                f"from src.{missing_module.split('.', 1)[-1]}"
                            ).replace(
                                f"import {missing_module}",
                                f"import src.{missing_module.split('.', 1)[-1]}"
                            )
                            modified = True
                
                if modified:
                    with open(file_path, 'w') as f:
                        f.writelines(content)
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error al intentar corregir {file_path}: {e}")
            return False
    
    def _fix_version(self, file_path: str, current_version: str, target_version: str) -> bool:
        """
        Corregir la versión en un archivo.
        
        Args:
            file_path: Ruta al archivo (relativa al proyecto)
            current_version: Versión actual
            target_version: Versión deseada
            
        Returns:
            True si se aplicó una corrección, False en caso contrario
        """
        try:
            full_path = self.project_path / file_path
            with open(full_path, 'r') as f:
                content = f.read()
            
            if file_path == "src/__init__.py":
                updated = content.replace(
                    f'__version__ = "{current_version}"',
                    f'__version__ = "{target_version}"'
                )
            elif file_path == "pyproject.toml":
                updated = content.replace(
                    f'version = "{current_version}"',
                    f'version = "{target_version}"'
                )
            elif file_path == "setup.py":
                updated = re.sub(
                    r'version\s*=\s*[\'"]?' + re.escape(current_version) + r'[\'"]?,',
                    f'version="{target_version}",',
                    content
                )
            else:
                return False
            
            with open(full_path, 'w') as f:
                f.write(updated)
                
            self.fixes_applied.append(f"Actualizada versión en {file_path} de {current_version} a {target_version}")
            return True
            
        except Exception as e:
            logger.error(f"Error al intentar corregir versión en {file_path}: {e}")
            return False


def parse_args() -> argparse.Namespace:
    """Analizar los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(description="Corrector automático de errores para ProjectPrompt")
    
    parser.add_argument("--fix", action="store_true", help="Aplicar correcciones automáticas")
    parser.add_argument("--project", type=str, default=None,
                      help="Ruta al proyecto (por defecto: directorio actual)")
    
    return parser.parse_args()


def main() -> int:
    """Función principal."""
    args = parse_args()
    
    project_path = Path(args.project) if args.project else PROJECT_ROOT
    
    logger.info(f"Analizando proyecto en: {project_path}")
    logger.info(f"Modo de corrección automática: {'Activado' if args.fix else 'Desactivado'}")
    
    bugfix = BugFixRunner(project_path, args.fix)
    bugfix.run_all_checks()
    
    # Devolver 1 si se encontraron problemas, 0 si todo está bien
    return 1 if bugfix.issues_found else 0


if __name__ == "__main__":
    sys.exit(main())
