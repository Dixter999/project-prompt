"""
Gestor de sincronización para ProjectPrompt.

Este módulo proporciona funcionalidades para sincronizar configuraciones
entre diferentes entornos y migrar datos entre versiones.
"""

import os
import sys
import json
import shutil
import logging
import subprocess
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

from ..utils.config import ConfigManager, config_manager, get_config
from ..utils.logger import get_logger

logger = get_logger()

DEFAULT_SYNC_DIRECTORIES = [
    "templates",
    "prompts",
    "configurations",
    "plugins",
]


class SyncManager:
    """Gestor para sincronizar configuraciones y datos entre diferentes instalaciones."""

    def __init__(self, config=None):
        """
        Inicializa el gestor de sincronización.
        
        Args:
            config: Configuración del sistema
        """
        self.config = config or get_config()
        self.sync_enabled = self.config.get('sync_enabled', False)
        self.sync_provider = self.config.get('sync_provider', 'local')
        self.last_sync = self._get_last_sync_time()
        
        # Directorio central para sincronización local
        self.sync_dir = Path(self.config.get('sync_directory', ''))
        if not self.sync_dir:
            self.sync_dir = Path.home() / ".projectprompt" / "sync"
            
        # Directorios a sincronizar (configurable)
        self.sync_directories = self.config.get('sync_directories', DEFAULT_SYNC_DIRECTORIES)
        
        # Directorio de datos de ProjectPrompt
        self.data_dir = self._get_data_dir()
        
        # Inicializar sistema de sincronización si está habilitado
        if self.sync_enabled:
            self._initialize_sync_directory()
    
    def _get_data_dir(self) -> Path:
        """Obtiene el directorio de datos de ProjectPrompt."""
        data_dir = self.config.get('data_directory', '')
        if data_dir:
            return Path(data_dir)
        
        # Directorio por defecto según plataforma
        if platform.system() == "Windows":
            return Path(os.environ.get('APPDATA', '')) / "ProjectPrompt"
        else:  # Linux, MacOS, etc.
            return Path.home() / ".projectprompt"
    
    def _initialize_sync_directory(self) -> None:
        """Inicializa el directorio de sincronización si no existe."""
        try:
            # Crear directorios necesarios
            self.sync_dir.mkdir(exist_ok=True, parents=True)
            
            # Crear archivo de metadatos si no existe
            metadata_file = self.sync_dir / "sync_metadata.json"
            if not metadata_file.exists():
                # Import version from main module
                from src import __version__
                metadata = {
                    "created": datetime.now().isoformat(),
                    "last_sync": None,
                    "sync_version": __version__,
                    "installations": []
                }
                
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
            
            # Registrar esta instalación
            self._register_installation()
                
        except Exception as e:
            logger.error(f"Error al inicializar directorio de sincronización: {e}")
            self.sync_enabled = False
    
    def _register_installation(self) -> None:
        """Registra esta instalación en los metadatos de sincronización."""
        try:
            metadata_file = self.sync_dir / "sync_metadata.json"
            if not metadata_file.exists():
                return
                
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Identificar esta instalación
            install_id = self._get_installation_id()
            install_info = {
                "id": install_id,
                "name": platform.node() or "Unknown",
                "platform": platform.system(),
                "last_sync": None,
            }
            
            # Verificar si ya está registrada
            installations = metadata.get("installations", [])
            exists = False
            
            for idx, installation in enumerate(installations):
                if installation.get("id") == install_id:
                    installations[idx] = install_info
                    exists = True
                    break
            
            if not exists:
                installations.append(install_info)
                
            metadata["installations"] = installations
            
            # Guardar metadatos actualizados
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Error al registrar instalación: {e}")
    
    def _get_installation_id(self) -> str:
        """
        Genera un ID único para esta instalación basado en factores del sistema.
        """
        # Usar características únicas de la instalación para generar un ID
        try:
            import uuid
            import hashlib
            
            system_info = [
                platform.node(),
                platform.system(),
                platform.platform(),
                str(self.data_dir),
                str(Path.home())
            ]
            
            # Si hay UUID de máquina disponible, usarlo
            try:
                if platform.system() == "Windows":
                    # ID del producto Windows
                    import subprocess
                    result = subprocess.run(
                        ["wmic", "os", "get", "serialnumber"], 
                        capture_output=True, text=True, check=True
                    )
                    if result.stdout:
                        product_id = result.stdout.strip().splitlines()[-1]
                        system_info.append(product_id)
                elif platform.system() == "Darwin":  # macOS
                    # Hardware UUID
                    result = subprocess.run(
                        ["system_profiler", "SPHardwareDataType"], 
                        capture_output=True, text=True, check=True
                    )
                    if result.stdout:
                        system_info.append(result.stdout)
                else:  # Linux y otros
                    # Intentar UUID de máquina
                    try:
                        with open("/etc/machine-id", 'r') as f:
                            machine_id = f.read().strip()
                            system_info.append(machine_id)
                    except:
                        pass
            except:
                pass
                
            # Generar un hash de la información del sistema
            hasher = hashlib.md5()
            hasher.update("".join(system_info).encode())
            return hasher.hexdigest()
        except:
            # Si falla, usar un UUID v4 aleatorio
            return str(uuid.uuid4())
    
    def _get_last_sync_time(self) -> Optional[datetime]:
        """Obtiene la fecha y hora de la última sincronización."""
        try:
            sync_file = Path.home() / ".projectprompt" / "last_sync.json"
            
            if not sync_file.exists():
                return None
                
            with open(sync_file, 'r') as f:
                data = json.load(f)
                last_sync = data.get('last_sync')
                
                if last_sync:
                    return datetime.fromisoformat(last_sync)
                return None
                
        except Exception as e:
            logger.warning(f"Error al leer última fecha de sincronización: {e}")
            return None
    
    def _update_last_sync_time(self) -> None:
        """Actualiza el registro de la última sincronización."""
        try:
            sync_file = Path.home() / ".projectprompt" / "last_sync.json"
            sync_file.parent.mkdir(exist_ok=True, parents=True)
            
            now = datetime.now().isoformat()
            
            data = {"last_sync": now}
            with open(sync_file, 'w') as f:
                json.dump(data, f)
                
            self.last_sync = datetime.now()
            
            # Actualizar también en los metadatos de sincronización
            metadata_file = self.sync_dir / "sync_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                install_id = self._get_installation_id()
                for installation in metadata.get('installations', []):
                    if installation.get('id') == install_id:
                        installation['last_sync'] = now
                        break
                
                metadata['last_sync'] = now
                
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Error al actualizar fecha de sincronización: {e}")
    
    def sync_configurations(self) -> Tuple[bool, Dict[str, int]]:
        """
        Sincroniza configuraciones entre instalaciones.
        
        Returns:
            Tupla (éxito, estadísticas de sincronización)
        """
        if not self.sync_enabled:
            return False, {"error": "La sincronización no está habilitada"}
            
        logger.info(f"Iniciando sincronización usando proveedor: {self.sync_provider}")
        stats = {"uploaded": 0, "downloaded": 0, "skipped": 0, "conflicts": 0, "errors": 0}
        
        try:
            if self.sync_provider == "local":
                success, sync_stats = self._local_sync()
                stats.update(sync_stats)
            elif self.sync_provider == "cloud":
                success, sync_stats = self._cloud_sync()
                stats.update(sync_stats)
            else:
                logger.error(f"Proveedor de sincronización no soportado: {self.sync_provider}")
                return False, {"error": f"Proveedor no soportado: {self.sync_provider}"}
            
            if success:
                self._save_last_sync_time()
                logger.info("Sincronización completada con éxito")
            else:
                logger.warning("Sincronización completada con errores")
                
            return success, stats
            
        except Exception as e:
            error_msg = f"Error durante la sincronización: {str(e)}"
            logger.error(error_msg)
            stats["errors"] += 1
            return False, stats
    
    def _local_sync(self) -> Tuple[bool, Dict[str, int]]:
        """
        Realiza sincronización utilizando un directorio local.
        
        Returns:
            Tupla (éxito, estadísticas)
        """
        stats = {"uploaded": 0, "downloaded": 0, "skipped": 0, "conflicts": 0, "errors": 0}
        success = True
        
        try:
            # Verificar directorios
            for sync_dir_name in self.sync_directories:
                local_dir = self.data_dir / sync_dir_name
                sync_target_dir = self.sync_dir / sync_dir_name
                
                # Sincronización bidireccional
                if local_dir.exists() and sync_target_dir.exists():
                    # Decidir qué archivos sincronizar en cada dirección
                    local_files = self._get_file_list_with_times(local_dir)
                    sync_files = self._get_file_list_with_times(sync_target_dir)
                    
                    # Archivos para subir (local -> sync)
                    for rel_path, local_info in local_files.items():
                        sync_info = sync_files.get(rel_path)
                        
                        if not sync_info:
                            # El archivo no existe en el directorio de sincronización
                            self._copy_file(
                                local_dir / rel_path,
                                sync_target_dir / rel_path
                            )
                            stats["uploaded"] += 1
                        elif local_info["mtime"] > sync_info["mtime"]:
                            # El archivo local es más reciente
                            self._copy_file(
                                local_dir / rel_path,
                                sync_target_dir / rel_path
                            )
                            stats["uploaded"] += 1
                        else:
                            stats["skipped"] += 1
                    
                    # Archivos para descargar (sync -> local)
                    for rel_path, sync_info in sync_files.items():
                        local_info = local_files.get(rel_path)
                        
                        if not local_info:
                            # El archivo no existe localmente
                            self._copy_file(
                                sync_target_dir / rel_path,
                                local_dir / rel_path
                            )
                            stats["downloaded"] += 1
                        elif sync_info["mtime"] > local_info["mtime"]:
                            # El archivo en el directorio de sincronización es más reciente
                            self._copy_file(
                                sync_target_dir / rel_path,
                                local_dir / rel_path
                            )
                            stats["downloaded"] += 1
                
                # Si el directorio local existe pero el de sincronización no
                elif local_dir.exists() and not sync_target_dir.exists():
                    # Crear el directorio de sincronización y copiar todos los archivos
                    sync_target_dir.mkdir(exist_ok=True, parents=True)
                    copied = self._copy_directory_contents(local_dir, sync_target_dir)
                    stats["uploaded"] += copied
                
                # Si el directorio de sincronización existe pero el local no
                elif not local_dir.exists() and sync_target_dir.exists():
                    # Crear el directorio local y copiar todos los archivos
                    local_dir.mkdir(exist_ok=True, parents=True)
                    copied = self._copy_directory_contents(sync_target_dir, local_dir)
                    stats["downloaded"] += copied
            
            return success, stats
            
        except Exception as e:
            logger.error(f"Error en sincronización local: {e}")
            stats["errors"] += 1
            return False, stats
    
    def _cloud_sync(self) -> Tuple[bool, Dict[str, int]]:
        """
        Realiza sincronización utilizando un servicio en la nube.
        
        Returns:
            Tupla (éxito, estadísticas)
        """
        # Implementación básica para demostrar la estructura
        # En una implementación real, aquí se conectaría con servicios como
        # Dropbox, Google Drive, GitHub, etc.
        
        logger.warning("Sincronización en la nube no implementada completamente")
        
        # Por ahora, simplemente delegamos a la sincronización local
        return self._local_sync()
    
    def _get_file_list_with_times(self, directory: Path) -> Dict[str, Dict[str, float]]:
        """
        Obtiene lista de archivos con sus tiempos de modificación.
        
        Args:
            directory: Directorio a escanear
            
        Returns:
            Diccionario con rutas relativas y metadatos de cada archivo
        """
        result = {}
        
        if not directory.exists():
            return result
            
        for file_path in directory.glob('**/*'):
            if file_path.is_file():
                rel_path = str(file_path.relative_to(directory))
                result[rel_path] = {
                    "mtime": file_path.stat().st_mtime,
                    "size": file_path.stat().st_size
                }
                
        return result
    
    def _copy_file(self, src: Path, dst: Path) -> bool:
        """
        Copia un archivo manteniendo metadatos.
        
        Args:
            src: Ruta al archivo original
            dst: Ruta al archivo destino
            
        Returns:
            True si la copia fue exitosa
        """
        try:
            # Crear directorio de destino si no existe
            dst.parent.mkdir(exist_ok=True, parents=True)
            
            # Copiar archivo con metadatos
            shutil.copy2(src, dst)
            logger.debug(f"Archivo copiado: {src} -> {dst}")
            return True
        except Exception as e:
            logger.error(f"Error al copiar archivo {src} -> {dst}: {e}")
            return False
    
    def _copy_directory_contents(self, src_dir: Path, dst_dir: Path) -> int:
        """
        Copia el contenido de un directorio a otro.
        
        Args:
            src_dir: Directorio origen
            dst_dir: Directorio destino
            
        Returns:
            Número de archivos copiados
        """
        copied = 0
        
        try:
            # Crear directorio destino si no existe
            dst_dir.mkdir(exist_ok=True, parents=True)
            
            # Copiar archivos manteniendo estructura
            for src_file in src_dir.glob('**/*'):
                if src_file.is_file():
                    # Calcular ruta relativa y destino
                    rel_path = src_file.relative_to(src_dir)
                    dst_file = dst_dir / rel_path
                    
                    # Crear directorio necesario
                    dst_file.parent.mkdir(exist_ok=True, parents=True)
                    
                    # Copiar archivo
                    shutil.copy2(src_file, dst_file)
                    copied += 1
            
            return copied
        except Exception as e:
            logger.error(f"Error al copiar directorio {src_dir} -> {dst_dir}: {e}")
            return copied
    
    def migrate_data(self, from_version: str, to_version: str) -> Tuple[bool, str]:
        """
        Migra datos entre diferentes versiones de ProjectPrompt.
        
        Args:
            from_version: Versión desde la que se migra
            to_version: Versión hacia la que se migra
            
        Returns:
            Tupla (éxito, mensaje)
        """
        logger.info(f"Migrando datos de v{from_version} a v{to_version}")
        
        try:
            # Realizar respaldo antes de migrar
            backup_success = self.create_backup()
            if not backup_success:
                logger.warning("No se pudo crear respaldo antes de migrar. Continuando sin respaldo...")
            
            # Aplicar migraciones necesarias según version
            if self._apply_migrations(from_version, to_version):
                msg = f"Migración completada correctamente de v{from_version} a v{to_version}"
                logger.info(msg)
                return True, msg
            else:
                msg = "No se requieren migraciones específicas"
                logger.info(msg)
                return True, msg
                
        except Exception as e:
            error_msg = f"Error durante la migración: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def _apply_migrations(self, from_version: str, to_version: str) -> bool:
        """
        Aplica las migraciones necesarias entre versiones.
        
        Args:
            from_version: Versión desde la que se migra
            to_version: Versión hacia la que se migra
            
        Returns:
            True si se aplicó alguna migración
        """
        import pkg_resources
        from_v = pkg_resources.parse_version(from_version)
        to_v = pkg_resources.parse_version(to_version)
        
        # Lista de migraciones disponibles
        migrations = [
            (pkg_resources.parse_version("0.1.0"), self._migrate_0_1_0),
            (pkg_resources.parse_version("0.2.0"), self._migrate_0_2_0),
            # Agregar más migraciones según sea necesario
        ]
        
        # Aplicar migraciones en orden
        applied = False
        for version, migration_func in sorted(migrations):
            if from_v < version <= to_v:
                logger.info(f"Aplicando migración para versión {version}")
                migration_func()
                applied = True
        
        return applied
    
    def _migrate_0_1_0(self) -> None:
        """Migración para la versión 0.1.0."""
        # Cambios en estructura de archivos config
        config_path = self.data_dir / "config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                
                # Actualizar formato de configuración
                if 'api_key' in config_data and isinstance(config_data['api_key'], str):
                    config_data['api_keys'] = {
                        'default': config_data.pop('api_key')
                    }
                
                # Guardar configuración actualizada
                with open(config_path, 'w') as f:
                    json.dump(config_data, f, indent=2)
                    
                logger.info("Configuración migrada a formato v0.1.0")
            except Exception as e:
                logger.error(f"Error durante migración 0.1.0 (config): {e}")
    
    def _migrate_0_2_0(self) -> None:
        """Migración para la versión 0.2.0."""
        # Migrar plantillas al nuevo formato
        templates_dir = self.data_dir / "templates"
        if templates_dir.exists():
            try:
                for template_file in templates_dir.glob("*.json"):
                    try:
                        with open(template_file, 'r') as f:
                            template_data = json.load(f)
                        
                        # Actualizar formato de plantilla
                        if 'content' in template_data and 'metadata' not in template_data:
                            template_data = {
                                'metadata': {
                                    'name': template_file.stem,
                                    'version': '0.2.0',
                                    'created': datetime.now().isoformat()
                                },
                                'content': template_data.pop('content')
                            }
                            
                            # Guardar plantilla actualizada
                            with open(template_file, 'w') as f:
                                json.dump(template_data, f, indent=2)
                                
                    except Exception as e:
                        logger.error(f"Error migrando plantilla {template_file}: {e}")
                        
                logger.info("Plantillas migradas a formato v0.2.0")
            except Exception as e:
                logger.error(f"Error durante migración 0.2.0 (templates): {e}")
    
    def create_backup(self) -> bool:
        """
        Crea una copia de seguridad de los datos del usuario.
        
        Returns:
            True si la copia fue exitosa
        """
        try:
            backup_dir = self.data_dir / "backups"
            backup_dir.mkdir(exist_ok=True, parents=True)
            
            # Crear nombre para el backup con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"projectprompt_backup_{timestamp}.zip"
            
            # Archivos y directorios a incluir en el backup
            to_backup = []
            for sync_dir_name in self.sync_directories:
                dir_path = self.data_dir / sync_dir_name
                if dir_path.exists():
                    to_backup.append(dir_path)
                    
            # Incluir el archivo de configuración si existe
            config_file = self.data_dir / "config.json"
            if config_file.exists():
                to_backup.append(config_file)
            
            if not to_backup:
                logger.warning("No hay archivos para respaldar")
                return False
                
            # Crear el archivo ZIP
            import zipfile
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Agregar archivos y directorios
                for item in to_backup:
                    if item.is_file():
                        zipf.write(item, item.name)
                    elif item.is_dir():
                        for file_path in item.glob('**/*'):
                            if file_path.is_file():
                                rel_path = file_path.relative_to(self.data_dir)
                                zipf.write(file_path, str(rel_path))
            
            logger.info(f"Backup creado en: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error al crear backup: {e}")
            return False
    
    def restore_backup(self, backup_file: Union[str, Path]) -> Tuple[bool, str]:
        """
        Restaura una copia de seguridad.
        
        Args:
            backup_file: Ruta al archivo de backup
            
        Returns:
            Tupla (éxito, mensaje)
        """
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                return False, f"El archivo de backup {backup_file} no existe"
                
            if backup_path.suffix != '.zip':
                return False, f"El archivo {backup_file} no es un backup válido (debe ser ZIP)"
                
            # Crear backup del estado actual antes de restaurar
            self.create_backup()
                
            import zipfile
            # Extraer archivos
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(self.data_dir)
            
            logger.info(f"Backup {backup_file} restaurado correctamente")
            return True, f"Backup restaurado correctamente desde {backup_file}"
            
        except Exception as e:
            error_msg = f"Error al restaurar backup: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        Lista los backups disponibles.
        
        Returns:
            Lista de diccionarios con información de cada backup
        """
        backups = []
        backup_dir = self.data_dir / "backups"
        
        if backup_dir.exists():
            for backup_file in backup_dir.glob("*.zip"):
                try:
                    # Obtener información del archivo
                    stat = backup_file.stat()
                    backups.append({
                        "filename": backup_file.name,
                        "path": str(backup_file),
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    })
                except Exception:
                    pass
                    
        return sorted(backups, key=lambda x: x["created"], reverse=True)


def get_sync_manager() -> SyncManager:
    """
    Obtiene una instancia del gestor de sincronización.
    
    Returns:
        Instancia de SyncManager
    """
    return SyncManager()


if __name__ == "__main__":
    # Prueba básica de funcionalidad
    sm = get_sync_manager()
    status = sm.get_status()
    print(f"Estado de sincronización: {'Activada' if status['enabled'] else 'Desactivada'}")
    print(f"Última sincronización: {status['last_sync']}")
    print(f"Instalaciones registradas: {status['installations']}")
