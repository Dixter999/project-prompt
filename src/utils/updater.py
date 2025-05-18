"""
Sistema de actualización para ProjectPrompt.

Este módulo proporciona funcionalidades para verificar nuevas versiones,
actualizar automáticamente el sistema y sus plantillas.
"""

import os
import sys
import json
import platform
import tempfile
import shutil
import logging
import subprocess
import pkg_resources
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

from ..utils.config import ConfigManager, config_manager, get_config
from ..utils.logger import get_logger


logger = get_logger()

# Constantes
GITHUB_API_URL = "https://api.github.com/repos/projectprompt/project-prompt/"
TEMPLATE_REPO_URL = "https://raw.githubusercontent.com/projectprompt/templates/main/"
UPDATE_CHECK_INTERVAL_DAYS = 1  # Verificar actualizaciones cada día por defecto


class Updater:
    """Clase para gestionar actualizaciones del sistema ProjectPrompt."""
    
    def __init__(self, config=None, force: bool = False):
        """
        Inicializa el gestor de actualizaciones.
        
        Args:
            config: Configuración del sistema
            force: Forzar la verificación incluso si se hizo recientemente
        """
        self.config = config or get_config()
        self.force_check = force
        self._version = self._get_current_version()
        self._last_check_data = self._load_last_check_data()
        
    def _get_current_version(self) -> str:
        """Obtiene la versión actual de ProjectPrompt."""
        try:
            return pkg_resources.get_distribution("project-prompt").version
        except pkg_resources.DistributionNotFound:
            # Si ejecutamos desde código fuente, intentamos obtener la versión de otra manera
            try:
                from .. import __version__
                return __version__
            except ImportError:
                return "0.0.0"
    
    def _load_last_check_data(self) -> Dict:
        """Carga los datos de la última verificación de actualizaciones."""
        check_file = Path.home() / ".projectprompt" / "update_check.json"
        
        if not check_file.exists():
            return {"last_check": None, "skipped_version": None}
        
        try:
            with open(check_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"last_check": None, "skipped_version": None}
    
    def _save_last_check_data(self) -> None:
        """Guarda los datos de la última verificación."""
        check_dir = Path.home() / ".projectprompt"
        check_file = check_dir / "update_check.json"
        
        try:
            check_dir.mkdir(exist_ok=True, parents=True)
            with open(check_file, 'w') as f:
                json.dump(self._last_check_data, f)
        except IOError as e:
            logger.warning(f"No se pudo guardar la información de verificación: {e}")
    
    def should_check_for_updates(self) -> bool:
        """Determina si se debe verificar actualizaciones basado en la última verificación."""
        if self.force_check:
            return True
            
        last_check = self._last_check_data.get("last_check")
        if not last_check:
            return True
            
        try:
            last_date = datetime.fromisoformat(last_check)
            days_since_check = (datetime.now() - last_date).days
            return days_since_check >= UPDATE_CHECK_INTERVAL_DAYS
        except (ValueError, TypeError):
            return True
    
    def check_for_updates(self) -> Dict[str, Any]:
        """
        Verifica si hay nuevas versiones disponibles.
        
        Returns:
            Dict con información de la actualización {'available': bool, 'version': str, 'changes': list}
        """
        if not self.should_check_for_updates():
            logger.debug("Saltando verificación de actualizaciones por configuración.")
            return {"available": False, "version": self._version}
        
        try:
            logger.info("Verificando actualizaciones...")
            response = requests.get(f"{GITHUB_API_URL}releases/latest", timeout=5)
            response.raise_for_status()
            
            release_data = response.json()
            latest_version = release_data['tag_name'].lstrip('v')
            changes = self._parse_changes(release_data.get('body', ''))
            
            self._last_check_data["last_check"] = datetime.now().isoformat()
            self._save_last_check_data()
            
            if pkg_resources.parse_version(latest_version) > pkg_resources.parse_version(self._version):
                skipped = self._last_check_data.get("skipped_version")
                if skipped and skipped == latest_version:
                    return {"available": False, "version": self._version, "latest": latest_version}
                
                return {
                    "available": True,
                    "version": self._version,
                    "latest": latest_version,
                    "changes": changes,
                    "url": release_data.get('html_url')
                }
            
            return {"available": False, "version": self._version, "latest": latest_version}
            
        except (requests.RequestException, json.JSONDecodeError) as e:
            logger.warning(f"Error al verificar actualizaciones: {e}")
            return {"available": False, "version": self._version, "error": str(e)}
    
    def _parse_changes(self, changes_text: str) -> List[str]:
        """Extrae los cambios importantes del texto de la release."""
        if not changes_text:
            return []
        
        lines = changes_text.split('\n')
        changes = []
        
        for line in lines:
            line = line.strip()
            if line.startswith(('- ', '* ', '• ')):
                changes.append(line[2:])
        
        return changes
    
    def skip_version(self, version: str) -> None:
        """
        Marca una versión específica para ser ignorada.
        
        Args:
            version: Versión a ignorar
        """
        self._last_check_data["skipped_version"] = version
        self._save_last_check_data()
        logger.info(f"Versión {version} marcada para ser ignorada.")
    
    def update_system(self) -> Tuple[bool, str]:
        """
        Actualiza el sistema ProjectPrompt a la última versión.
        
        Returns:
            Tupla (éxito, mensaje)
        """
        try:
            logger.info("Iniciando actualización del sistema...")
            
            # Determinar método de instalación y actualizar
            if self._is_pip_installed():
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--upgrade", "project-prompt"],
                    check=True,
                    capture_output=True,
                    text=True
                )
                logger.info("Actualización mediante pip completada.")
                return True, "Actualización completada exitosamente."
            else:
                logger.info("Usando método de actualización desde repositorio...")
                return self._update_from_repo()
                
        except subprocess.CalledProcessError as e:
            error_msg = f"Error al actualizar: {e.stderr}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error inesperado durante la actualización: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def _is_pip_installed(self) -> bool:
        """Verifica si ProjectPrompt fue instalado con pip."""
        try:
            dist = pkg_resources.get_distribution("project-prompt")
            return dist is not None
        except pkg_resources.DistributionNotFound:
            return False
    
    def _update_from_repo(self) -> Tuple[bool, str]:
        """Actualización mediante clonado del repositorio."""
        temp_dir = tempfile.mkdtemp()
        try:
            subprocess.run(
                ["git", "clone", "https://github.com/projectprompt/project-prompt.git", temp_dir],
                check=True,
                capture_output=True
            )
            
            # Instalar desde el repositorio clonado
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-e", temp_dir],
                check=True,
                capture_output=True
            )
            
            return True, "Actualización desde repositorio completada."
            
        except subprocess.CalledProcessError as e:
            return False, f"Error al actualizar desde repositorio: {e.stderr}"
        finally:
            # Limpiar directorio temporal
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass
    
    def update_templates(self) -> Tuple[bool, Dict[str, int]]:
        """
        Actualiza las plantillas a la última versión.
        
        Returns:
            Tupla (éxito, estadísticas)
        """
        logger.info("Actualizando plantillas...")
        stats = {"updated": 0, "added": 0, "skipped": 0, "failed": 0}
        
        try:
            # Obtener índice de plantillas
            response = requests.get(f"{TEMPLATE_REPO_URL}index.json", timeout=5)
            response.raise_for_status()
            templates_index = response.json()
            
            # Directorio de plantillas local
            templates_dir = Path(self.config.get('templates_directory', ''))
            if not templates_dir.is_absolute():
                # Si es relativa, buscar desde el directorio de instalación
                import pkg_resources
                base_dir = Path(pkg_resources.resource_filename('project_prompt', ''))
                templates_dir = base_dir.parent / templates_dir
            
            templates_dir.mkdir(exist_ok=True, parents=True)
            
            # Procesar cada plantilla
            for template in templates_index.get('templates', []):
                template_path = template.get('path')
                template_version = template.get('version')
                
                if not template_path:
                    continue
                
                # Verificar si necesita actualización
                local_path = templates_dir / template_path
                needs_update = not local_path.exists()
                
                if local_path.exists() and template_version:
                    # Verificar versión si existe localmente
                    try:
                        with open(local_path, 'r') as f:
                            content = f.read()
                            current_version = self._extract_version_from_template(content)
                            if not current_version or pkg_resources.parse_version(template_version) > pkg_resources.parse_version(current_version):
                                needs_update = True
                    except IOError:
                        needs_update = True
                
                # Actualizar si es necesario
                if needs_update:
                    try:
                        response = requests.get(f"{TEMPLATE_REPO_URL}{template_path}", timeout=5)
                        response.raise_for_status()
                        
                        # Crear directorios necesarios
                        local_path.parent.mkdir(exist_ok=True, parents=True)
                        
                        with open(local_path, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        
                        if local_path.exists():
                            if template.get('executable', False):
                                local_path.chmod(0o755)  # Hacer ejecutable
                            
                            if local_path.exists():
                                stats['updated' if local_path.exists() else 'added'] += 1
                                logger.info(f"Plantilla actualizada: {template_path}")
                    except Exception as e:
                        stats['failed'] += 1
                        logger.error(f"Error al actualizar plantilla {template_path}: {e}")
                else:
                    stats['skipped'] += 1
            
            return True, stats
        except (requests.RequestException, json.JSONDecodeError) as e:
            logger.error(f"Error al actualizar plantillas: {e}")
            return False, stats
    
    def _extract_version_from_template(self, content: str) -> Optional[str]:
        """Extrae la versión de una plantilla si está presente."""
        for line in content.split('\n')[:10]:  # Buscar en primeras líneas
            if 'version:' in line.lower():
                parts = line.split(':', 1)
                if len(parts) > 1:
                    version = parts[1].strip().strip('"\'')
                    return version
        return None


def check_and_notify_updates():
    """
    Verifica si hay actualizaciones disponibles y muestra una notificación.
    Esta función puede ser llamada al inicio del programa.
    """
    try:
        updater = Updater()
        if updater.should_check_for_updates():
            update_info = updater.check_for_updates()
            
            if update_info.get('available'):
                version = update_info.get('latest')
                print(f"\n⭐ Actualización disponible: v{version} ⭐")
                print("Ejecute 'project-prompt update' para actualizar.")
                if update_info.get('changes'):
                    print("\nMejoras destacadas:")
                    for change in update_info.get('changes')[:3]:  # Mostrar top 3 cambios
                        print(f"• {change}")
                print()  # Línea en blanco al final
    except Exception as e:
        # Fallar silenciosamente, la verificación de actualizaciones no debería interrumpir
        logger.debug(f"Error durante verificación de actualizaciones: {e}")


if __name__ == "__main__":
    # Prueba simple del sistema de actualizaciones
    check_and_notify_updates()
