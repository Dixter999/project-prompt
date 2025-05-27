#!/usr/bin/env python3
"""
Gestor de consentimiento para telemetría en ProjectPrompt.
Proporciona interfaces para obtener, mostrar y gestionar el consentimiento
del usuario para la recolección de datos anónimos.
"""

import os
import time
from enum import Enum
from typing import Dict, Any, Optional, Callable

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

from src.utils import config_manager
from src.utils.telemetry import get_telemetry_manager
from src.utils import logger


class ConsentStatus(str, Enum):
    """Estados posibles de consentimiento de telemetría."""
    UNKNOWN = "unknown"
    GRANTED = "granted"
    DENIED = "denied"
    DEFERRED = "deferred"


class ConsentManager:
    """
    Gestor de consentimiento para la recolección de datos anónimos.
    Proporciona métodos para verificar, solicitar y gestionar el consentimiento
    del usuario para la telemetría.
    """
    
    def __init__(self, console: Optional[Console] = None):
        """
        Inicializa el gestor de consentimiento.
        
        Args:
            console: Consola Rich para mostrar información (opcional)
        """
        self.console = console if console is not None else Console()
        self.telemetry_manager = get_telemetry_manager()
        self._consent_callback = None
        self._deferred_until = None
        
    def check_consent_status(self) -> ConsentStatus:
        """
        Verifica el estado actual del consentimiento para telemetría.
        
        Returns:
            Estado actual del consentimiento
        """
        config = config_manager.config
        
        # Verificar si hay una decisión explícita
        if "telemetry" in config:
            if "enabled" in config["telemetry"]:
                return ConsentStatus.GRANTED if config["telemetry"]["enabled"] else ConsentStatus.DENIED
                
            # Verificar si se ha pospuesto la decisión
            if "deferred_until" in config["telemetry"]:
                deferred_until = config["telemetry"]["deferred_until"]
                if time.time() < deferred_until:
                    return ConsentStatus.DEFERRED
        
        return ConsentStatus.UNKNOWN
        
    def request_consent(self, force: bool = False) -> ConsentStatus:
        """
        Solicita al usuario su consentimiento para la telemetría.
        
        Args:
            force: Si True, solicita consentimiento incluso si ya se ha decidido
            
        Returns:
            Estado del consentimiento tras la solicitud
        """
        if not force:
            status = self.check_consent_status()
            if status != ConsentStatus.UNKNOWN:
                return status
                
        self._show_consent_prompt()
        choice = self._get_user_choice()
        
        return self._process_choice(choice)
        
    def show_collected_data(self) -> None:
        """
        Muestra al usuario un resumen de los datos que se recolectan.
        Proporciona transparencia sobre la telemetría.
        """
        data_summary = self.telemetry_manager.get_collected_data_summary()
        
        self.console.print("[bold]Resumen de datos recolectados[/bold]\n")
        
        # Estado general
        status = "Activada" if data_summary["enabled"] else "Desactivada"
        status_color = "green" if data_summary["enabled"] else "red"
        self.console.print(f"Estado de la telemetría: [{status_color}]{status}[/{status_color}]")
        
        # ID de instalación (anónimo)
        self.console.print(f"ID de instalación anónimo: {data_summary['installation_id']}")
        self.console.print("Este ID no contiene información personal y no puede vincularse a su identidad.\n")
        
        # Eventos actuales y pendientes
        self.console.print(f"Eventos en sesión actual: {sum(data_summary['current_session'].values())}")
        self.console.print(f"Eventos pendientes de envío: {data_summary['queued_events']}")
        
        # Tipos de datos recolectados
        if not data_summary["data_collected"]:
            self.console.print("\nNo hay datos de ejemplo disponibles.")
        else:
            self.console.print("\n[bold]Categorías y tipos de datos recolectados:[/bold]")
            
            table = Table(show_header=True)
            table.add_column("Categoría")
            table.add_column("Tipos de acciones")
            
            for category, actions in data_summary["data_collected"].items():
                table.add_row(category, ", ".join(actions))
                
            self.console.print(table)
            
        self.console.print("\n[italic]Nota: Todos los datos son anónimos y se utilizan únicamente para mejorar ProjectPrompt.[/italic]")
        
    def set_consent_callback(self, callback: Callable[[bool], None]) -> None:
        """
        Establece una función de callback para cuando cambia el consentimiento.
        
        Args:
            callback: Función a llamar cuando cambie el consentimiento
        """
        self._consent_callback = callback
        
    def enable_telemetry(self) -> bool:
        """
        Activa la telemetría explícitamente.
        
        Returns:
            True si se activó correctamente, False en caso contrario
        """
        success = self.telemetry_manager.toggle_telemetry(True)
        
        if success and self._consent_callback:
            self._consent_callback(True)
            
        return success
        
    def disable_telemetry(self) -> bool:
        """
        Desactiva la telemetría explícitamente.
        
        Returns:
            True si se desactivó correctamente, False en caso contrario
        """
        success = self.telemetry_manager.toggle_telemetry(False)
        
        if success and self._consent_callback:
            self._consent_callback(False)
            
        return success
        
    def _show_consent_prompt(self) -> None:
        """Muestra al usuario la solicitud de consentimiento."""
        self.console.clear()
        
        markdown_text = """
        # Telemetría anónima en ProjectPrompt
        
        ProjectPrompt puede recopilar información de uso **completamente anónima** para ayudarnos a mejorar la herramienta.
        
        ## Qué recopilamos:
        
        - **Comandos utilizados** (sin argumentos personales)
        - **Errores encontrados** (sin información de identificación)
        - **Características más usadas**
        - **Información básica del sistema** (sistema operativo, versión de Python)
        
        ## Lo que NUNCA recopilamos:
        
        - Datos personales o de identificación
        - Contenido de tus proyectos o archivos
        - Nombres de archivos o rutas completas
        - Claves API o credenciales
        
        La telemetría es totalmente opcional y puedes cambiar tu elección en cualquier momento con el comando:
        `project-prompt config --telemetry <on|off>`
        """
        
        md = Markdown(markdown_text)
        panel = Panel(md, title="Telemetría anónima", expand=False)
        self.console.print(panel)
        
    def _get_user_choice(self) -> str:
        """
        Obtiene la elección del usuario sobre la telemetría.
        
        Returns:
            Letra correspondiente a la opción elegida
        """
        valid_choices = ["y", "n", "l", "d"]
        prompt = "\n¿Deseas activar la telemetría anónima? [y]es/[n]o/[l]ater/[d]etails: "
        
        while True:
            self.console.print(prompt, end="")
            choice = input().lower()
            
            if choice == "":
                choice = "y"  # Default
                
            if choice in valid_choices:
                return choice
                
            self.console.print("[red]Opción no válida. Por favor, elija una opción válida.[/red]")
            
    def _process_choice(self, choice: str) -> ConsentStatus:
        """
        Procesa la elección del usuario y actualiza la configuración.
        
        Args:
            choice: Opción elegida por el usuario (y/n/l/d)
            
        Returns:
            Estado final del consentimiento
        """
        if choice == "d":
            # Mostrar detalles adicionales y volver a preguntar
            self.show_collected_data()
            self.console.print()
            choice = self._get_user_choice()
            return self._process_choice(choice)
            
        elif choice == "y":
            # Activar telemetría
            self.telemetry_manager.toggle_telemetry(True)
            self.console.print("[green]Telemetría activada. Gracias por ayudarnos a mejorar ProjectPrompt.[/green]")
            if self._consent_callback:
                self._consent_callback(True)
            return ConsentStatus.GRANTED
            
        elif choice == "n":
            # Desactivar telemetría
            self.telemetry_manager.toggle_telemetry(False)
            self.console.print("[yellow]Telemetría desactivada. Puedes cambiar esto en cualquier momento.[/yellow]")
            if self._consent_callback:
                self._consent_callback(False)
            return ConsentStatus.DENIED
            
        elif choice == "l":
            # Posponer decisión
            config = config_manager.config
            if "telemetry" not in config:
                config["telemetry"] = {}
                
            # Posponer por 7 días
            deferred_until = time.time() + (7 * 24 * 60 * 60)
            config["telemetry"]["deferred_until"] = deferred_until
            config_manager.save_config()
            
            self.console.print("[blue]Decisión pospuesta. Te preguntaremos más adelante.[/blue]")
            return ConsentStatus.DEFERRED
            
        return ConsentStatus.UNKNOWN
