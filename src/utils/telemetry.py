#!/usr/bin/env python3
"""
Sistema de telemetría anónima para ProjectPrompt.
Este módulo proporciona funcionalidades para recolectar datos anónimos de uso
que ayudan a mejorar la herramienta, siempre con el consentimiento del usuario.
"""

import os
import json
import uuid
import time
import platform
import hashlib
import threading
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import requests

from src.utils.config import config_manager
from src.utils import logger

# Configurar logger específico para telemetría
telemetry_logger = logging.getLogger("project_prompt.telemetry")

# URL del endpoint de telemetría (sería reemplazado por un endpoint real en producción)
TELEMETRY_ENDPOINT = "https://telemetry.project-prompt.example/collect"

# Intervalo de envío de telemetría (en segundos)
TELEMETRY_INTERVAL = 24 * 60 * 60  # 24 horas


class TelemetryData:
    """Clase para encapsular los datos de telemetría."""
    
    def __init__(self):
        """Inicializa un nuevo objeto de datos de telemetría."""
        self.session_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat()
        self.data = {}
        
    def add_event(self, category: str, action: str, value: Optional[Any] = None) -> None:
        """
        Añade un evento de telemetría.
        
        Args:
            category: Categoría del evento (ej. 'command', 'ui', 'error')
            action: Acción específica (ej. 'analyze_project', 'generate_prompt')
            value: Valor adicional opcional (ej. duración, tamaño, etc.)
        """
        if category not in self.data:
            self.data[category] = []
            
        event_data = {
            "action": action,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if value is not None:
            event_data["value"] = value
            
        self.data[category].append(event_data)
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte los datos de telemetría a un diccionario.
        
        Returns:
            Diccionario con los datos de telemetría
        """
        # Generamos un ID de instalación anónimo basado en hardware y ruta de instalación
        system_info = _get_anonymous_system_info()
        
        return {
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "installation_id": _get_installation_id(),
            "system_info": system_info,
            "version": _get_version(),
            "events": self.data
        }


class TelemetryManager:
    """Gestor principal de telemetría."""
    
    def __init__(self):
        """Inicializa el gestor de telemetría."""
        self._enabled = self._is_telemetry_enabled()
        self._current_data = TelemetryData()
        self._lock = threading.Lock()
        self._send_thread = None
        self._queue = []
        self._initialized = False
        
    def initialize(self) -> None:
        """Inicializa el sistema de telemetría."""
        if self._initialized:
            return
            
        self._initialized = True
        self._load_queued_data()
        
        if self._enabled:
            self.add_event("system", "startup")
            # Iniciar hilo para envío periódico
            self._schedule_periodic_send()
            
    def shutdown(self) -> None:
        """Cierra el sistema de telemetría, guardando datos pendientes."""
        if self._enabled:
            self.add_event("system", "shutdown")
            self._save_queued_data()
            
    def add_event(self, category: str, action: str, value: Optional[Any] = None) -> None:
        """
        Añade un evento al registro de telemetría actual.
        
        Args:
            category: Categoría del evento
            action: Acción específica
            value: Valor adicional opcional
        """
        if not self._enabled:
            return
            
        with self._lock:
            self._current_data.add_event(category, action, value)
            
    def record_command(self, command: str, duration_ms: Optional[int] = None) -> None:
        """
        Registra un comando ejecutado por el usuario.
        
        Args:
            command: Nombre del comando
            duration_ms: Duración en milisegundos (opcional)
        """
        if duration_ms is not None:
            self.add_event("command", command, {"duration_ms": duration_ms})
        else:
            self.add_event("command", command)
            
    def record_error(self, error_type: str, message: str, 
                     file: Optional[str] = None, line: Optional[int] = None) -> None:
        """
        Registra un error ocurrido en la aplicación.
        
        Args:
            error_type: Tipo de error (ej. 'ValueError', 'ConnectionError')
            message: Mensaje de error (sin información personal)
            file: Nombre del archivo donde ocurrió el error (opcional)
            line: Línea de código donde ocurrió el error (opcional)
        """
        error_data = {
            "type": error_type,
            "message": _sanitize_error_message(message)
        }
        
        if file:
            # Solo incluimos el nombre de archivo, no la ruta completa
            error_data["file"] = os.path.basename(file)
            
        if line:
            error_data["line"] = line
            
        self.add_event("error", "exception", error_data)
        
    def record_feature_usage(self, feature: str) -> None:
        """
        Registra el uso de una característica específica.
        
        Args:
            feature: Nombre de la característica
        """
        self.add_event("feature", feature)
        
    def toggle_telemetry(self, enabled: bool) -> bool:
        """
        Activa o desactiva la telemetría.
        
        Args:
            enabled: True para activar, False para desactivar
            
        Returns:
            True si el cambio fue exitoso, False en caso contrario
        """
        try:
            config_manager.set("telemetry", {"enabled": enabled})
            config_manager.save_config()
            
            self._enabled = enabled
            
            # Registrar evento de cambio de consentimiento
            if enabled:
                self.add_event("system", "telemetry_opted_in")
            else:
                # Un último evento antes de desactivar
                self.add_event("system", "telemetry_opted_out")
                # Eliminar datos pendientes
                with self._lock:
                    self._queue = []
                    self._current_data = TelemetryData()
                self._save_queued_data()
                
            return True
        except Exception as e:
            telemetry_logger.error(f"Error al cambiar configuración de telemetría: {e}")
            return False
            
    def is_enabled(self) -> bool:
        """
        Verifica si la telemetría está habilitada.
        
        Returns:
            True si está habilitada, False en caso contrario
        """
        return self._enabled
        
    def get_collected_data_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen de los datos recolectados.
        Para mostrar transparencia al usuario sobre qué se envía.
        
        Returns:
            Resumen de datos de telemetría
        """
        result = {
            "enabled": self._enabled,
            "installation_id": _get_installation_id(),
            "data_collected": {},
            "queued_events": len(self._queue),
            "current_session": {}
        }
        
        # Información actual
        with self._lock:
            for category, events in self._current_data.data.items():
                result["current_session"][category] = len(events)
                
            # Mostrar ejemplos de algunos datos (sin información personal)
            if self._queue:
                sample = self._queue[0]
                for category, events in sample.get("events", {}).items():
                    if events:
                        # Solo mostrar las acciones registradas, no valores específicos
                        actions = list(set(e["action"] for e in events))
                        result["data_collected"][category] = actions
                        
        return result
        
    def send_telemetry_now(self) -> bool:
        """
        Fuerza el envío inmediato de los datos de telemetría acumulados.
        
        Returns:
            True si el envío fue exitoso, False en caso contrario
        """
        if not self._enabled:
            return False
            
        return self._send_data()
        
    def _is_telemetry_enabled(self) -> bool:
        """
        Comprueba si la telemetría está habilitada en la configuración.
        
        Returns:
            True si está habilitada, False en caso contrario
        """
        try:
            return config_manager.get("telemetry", {}).get("enabled", False)
        except Exception as e:
            telemetry_logger.error(f"Error al comprobar configuración de telemetría: {e}")
            return False
            
    def _schedule_periodic_send(self) -> None:
        """Programa el envío periódico de datos de telemetría."""
        if not self._enabled:
            return
            
        def send_and_reschedule():
            try:
                self._send_data()
            except Exception as e:
                telemetry_logger.error(f"Error al enviar telemetría periódica: {e}")
            finally:
                # Reprogramar para la siguiente ejecución
                if self._enabled:
                    self._send_thread = threading.Timer(TELEMETRY_INTERVAL, send_and_reschedule)
                    self._send_thread.daemon = True
                    self._send_thread.start()
                    
        # Primera ejecución
        self._send_thread = threading.Timer(TELEMETRY_INTERVAL, send_and_reschedule)
        self._send_thread.daemon = True
        self._send_thread.start()
        
    def _send_data(self) -> bool:
        """
        Envía los datos de telemetría acumulados.
        
        Returns:
            True si el envío fue exitoso, False en caso contrario
        """
        if not self._enabled:
            return False
            
        with self._lock:
            # Añadir datos actuales a la cola
            if self._current_data.data:
                self._queue.append(self._current_data.to_dict())
                self._current_data = TelemetryData()
                
            if not self._queue:
                return True  # No hay datos para enviar
                
            queue_to_send = self._queue.copy()
            
        # Intentar enviar los datos
        success = self._send_to_server(queue_to_send)
        
        if success:
            with self._lock:
                # Eliminar de la cola solo los elementos que se enviaron
                self._queue = self._queue[len(queue_to_send):]
            self._save_queued_data()
            
        return success
        
    def _send_to_server(self, data: List[Dict[str, Any]]) -> bool:
        """
        Envía los datos al servidor de telemetría.
        
        Args:
            data: Lista de datos de telemetría para enviar
            
        Returns:
            True si el envío fue exitoso, False en caso contrario
        """
        if not data:
            return True
            
        try:
            payload = {"batch": data}
            response = requests.post(
                TELEMETRY_ENDPOINT,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                telemetry_logger.debug(f"Telemetría enviada correctamente: {len(data)} registros")
                return True
            else:
                telemetry_logger.warning(
                    f"Error al enviar telemetría: {response.status_code} - {response.text}"
                )
                return False
        except requests.RequestException as e:
            telemetry_logger.warning(f"Error de conexión al enviar telemetría: {e}")
            return False
        except Exception as e:
            telemetry_logger.error(f"Error inesperado al enviar telemetría: {e}")
            return False
            
    def _save_queued_data(self) -> None:
        """Guarda los datos pendientes en el almacenamiento local."""
        if not self._enabled:
            return
            
        try:
            config = config_manager.config
            telemetry_dir = os.path.join(
                os.path.dirname(os.path.abspath(config.get("config_path", ""))),
                "telemetry"
            )
            
            os.makedirs(telemetry_dir, exist_ok=True)
            
            with self._lock:
                if not self._queue:
                    return
                    
                queue_file = os.path.join(telemetry_dir, "queue.json")
                with open(queue_file, "w") as f:
                    json.dump(self._queue, f)
        except Exception as e:
            telemetry_logger.error(f"Error al guardar datos de telemetría: {e}")
            
    def _load_queued_data(self) -> None:
        """Carga datos pendientes desde el almacenamiento local."""
        try:
            config = config_manager.config
            telemetry_dir = os.path.join(
                os.path.dirname(os.path.abspath(config.get("config_path", ""))),
                "telemetry"
            )
            
            queue_file = os.path.join(telemetry_dir, "queue.json")
            
            if not os.path.exists(queue_file):
                return
                
            with open(queue_file, "r") as f:
                queue_data = json.load(f)
                
            with self._lock:
                self._queue = queue_data
                
            telemetry_logger.debug(f"Cargados {len(self._queue)} registros de telemetría pendientes")
        except Exception as e:
            telemetry_logger.error(f"Error al cargar datos de telemetría: {e}")


# Utilitarios privados

def _get_installation_id() -> str:
    """
    Genera un ID de instalación anónimo basado en una huella hardware.
    Completamente anónimo y no puede rastrearse al usuario específico.
    
    Returns:
        ID de instalación anónimo
    """
    try:
        config = config_manager.config
        
        # Comprobar si ya tenemos un ID guardado
        installation_id = config.get("telemetry", {}).get("installation_id")
        if installation_id:
            return installation_id
            
        # Generar un nuevo ID basado en características del sistema
        # No incluimos información que pueda identificar al usuario
        system_info = [
            platform.system(),
            platform.machine(),
            str(os.cpu_count()),
            platform.python_implementation()
        ]
        
        # Añadir un salt aleatorio para mayor privacidad
        salt = str(uuid.uuid4())
        system_info.append(salt)
        
        # Generar hash del sistema
        hasher = hashlib.sha256()
        hasher.update("|".join(system_info).encode("utf-8"))
        installation_id = hasher.hexdigest()
        
        # Guardar para uso futuro
        if "telemetry" not in config:
            config["telemetry"] = {}
            
        config["telemetry"]["installation_id"] = installation_id
        config_manager.save_config()
        
        return installation_id
    except Exception as e:
        telemetry_logger.error(f"Error al generar ID de instalación: {e}")
        # Fallback a un ID aleatorio
        return str(uuid.uuid4())


def _get_anonymous_system_info() -> Dict[str, str]:
    """
    Obtiene información anónima sobre el sistema.
    No incluye información que pueda identificar al usuario.
    
    Returns:
        Diccionario con información del sistema
    """
    return {
        "os": platform.system(),
        "os_version": _anonymize_os_version(platform.version()),
        "python_version": platform.python_version(),
        "cpu_arch": platform.machine(),
        "cpu_count": str(os.cpu_count() or 0),
        "locale": _get_system_locale()
    }


def _get_version() -> str:
    """
    Obtiene la versión actual de ProjectPrompt.
    
    Returns:
        Versión de ProjectPrompt
    """
    try:
        from src import __version__
        return __version__
    except ImportError:
        return "unknown"


def _anonymize_os_version(version: str) -> str:
    """
    Anonimiza la versión del sistema operativo para eliminar identificadores únicos.
    
    Args:
        version: Versión completa del sistema operativo
        
    Returns:
        Versión anonimizada
    """
    # Solo mantener la información general, eliminar detalles específicos
    try:
        # Para Windows, mantener solo el número de versión principal
        if platform.system() == "Windows":
            import re
            match = re.search(r"(\d+\.\d+)", version)
            if match:
                return match.group(1)
                
        # Para Linux, solo mantener el nombre de la distribución si está disponible
        elif platform.system() == "Linux":
            import re
            # Intentar extraer solo el nombre de la distribución
            match = re.search(r"^([a-zA-Z]+)", version)
            if match:
                return match.group(1)
    except Exception:
        pass
        
    # En caso de error o para otros sistemas, devolver solo los primeros caracteres
    if len(version) > 5:
        return version[:5] + "..."
    return version


def _get_system_locale() -> str:
    """
    Obtiene la configuración regional del sistema.
    
    Returns:
        Código de localización (ej. 'en_US')
    """
    try:
        import locale
        return locale.getdefaultlocale()[0] or "unknown"
    except Exception:
        return "unknown"


def _sanitize_error_message(message: str) -> str:
    """
    Elimina posible información personal de mensajes de error.
    
    Args:
        message: Mensaje de error original
        
    Returns:
        Mensaje de error sanitizado
    """
    # Eliminar rutas de archivo absolutas
    import re
    
    # Reemplazar rutas absolutas con <PATH>
    sanitized = re.sub(r"[a-zA-Z]:\\[^\s:*?\"<>|]+", "<PATH>", message)
    sanitized = re.sub(r"(/[^\s/]+)+/?", "<PATH>", sanitized)
    
    # Eliminar posibles correos electrónicos
    sanitized = re.sub(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "<EMAIL>", sanitized)
    
    # Eliminar posibles tokens API u otras cadenas que parezcan tokens
    sanitized = re.sub(r"[a-zA-Z0-9_\-]{30,}", "<TOKEN>", sanitized)
    
    return sanitized


# Instancia global del gestor de telemetría
_telemetry_manager = TelemetryManager()


def get_telemetry_manager() -> TelemetryManager:
    """
    Obtiene la instancia global del gestor de telemetría.
    
    Returns:
        Instancia del gestor de telemetría
    """
    return _telemetry_manager


def initialize_telemetry() -> None:
    """
    Inicializa el sistema de telemetría.
    Debe ser llamado durante el inicio de la aplicación.
    """
    _telemetry_manager.initialize()


def shutdown_telemetry() -> None:
    """
    Cierra el sistema de telemetría.
    Debe ser llamado durante el cierre de la aplicación.
    """
    _telemetry_manager.shutdown()


# Funciones de conveniencia para registrar eventos comunes

def record_command(command: str, duration_ms: Optional[int] = None) -> None:
    """Registra un comando ejecutado."""
    _telemetry_manager.record_command(command, duration_ms)


def record_error(error_type: str, message: str, 
                file: Optional[str] = None, line: Optional[int] = None) -> None:
    """Registra un error ocurrido."""
    _telemetry_manager.record_error(error_type, message, file, line)


def record_feature_usage(feature: str) -> None:
    """Registra el uso de una característica."""
    _telemetry_manager.record_feature_usage(feature)
