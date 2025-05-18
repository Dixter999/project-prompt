#!/usr/bin/env python3
"""
Asistente para la configuración del sistema.
"""

from typing import Dict, Any, List, Optional
import os
from pathlib import Path

from src.ui.wizards.base_wizard import BaseWizard
from src.ui.cli import cli
from src.utils.config import ConfigManager, get_config, save_config

class ConfigWizard(BaseWizard[Dict[str, Any]]):
    """
    Asistente interactivo para configurar ProjectPrompt.
    Guía al usuario a través de las diferentes opciones de configuración.
    """
    
    def __init__(self):
        """Inicializa el asistente de configuración."""
        super().__init__(
            title="Configuración de ProjectPrompt", 
            description="Este asistente le guiará en la configuración de las opciones del sistema."
        )
        
        # Cargar configuración actual
        self.config = get_config()
        
        # Añadir pasos del asistente
        self.add_step(self._step_general_config)
        self.add_step(self._step_api_keys)
        self.add_step(self._step_template_config)
        self.add_step(self._step_sync_config)
        self.add_step(self._step_review)
    
    def _step_general_config(self) -> bool:
        """Paso 1: Configuración general."""
        cli.print_header("Paso 1: Configuración General")
        
        # Configuración del nivel de log
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        current_log_level = self.config.get("log_level", "INFO")
        
        self.console.print("Nivel de log actual: " + 
            f"[cyan]{current_log_level}[/cyan]")
        
        change_log = self.ask_confirm("¿Desea cambiar el nivel de log?", False)
        if change_log:
            index = log_levels.index(current_log_level) if current_log_level in log_levels else 1
            log_level = self.ask_choice(
                "Seleccione el nivel de log", 
                log_levels, 
                default=index
            )
            self.data["log_level"] = log_level
        else:
            self.data["log_level"] = current_log_level
        
        # Configuración del directorio de datos
        current_data_dir = self.config.get("data_directory", str(Path.home() / ".projectprompt"))
        self.console.print("\nDirectorio de datos actual: " + 
            f"[cyan]{current_data_dir}[/cyan]")
        
        change_dir = self.ask_confirm("¿Desea cambiar el directorio de datos?", False)
        if change_dir:
            data_dir = self.ask_input(
                "Introduzca la ruta al directorio de datos", 
                current_data_dir
            )
            self.data["data_directory"] = os.path.expanduser(data_dir)
        else:
            self.data["data_directory"] = current_data_dir
        
        # Configuración del tema
        current_theme = self.config.get("theme", "default")
        themes = ["default", "dark", "light", "blue", "green"]
        
        self.console.print("\nTema actual: " + 
            f"[cyan]{current_theme}[/cyan]")
        
        change_theme = self.ask_confirm("¿Desea cambiar el tema?", False)
        if change_theme:
            index = themes.index(current_theme) if current_theme in themes else 0
            theme = self.ask_choice(
                "Seleccione el tema", 
                themes, 
                default=index
            )
            self.data["theme"] = theme
        else:
            self.data["theme"] = current_theme
        
        return True
    
    def _step_api_keys(self) -> bool:
        """Paso 2: Configuración de claves de API."""
        cli.print_header("Paso 2: Claves de API")
        
        # API de Anthropic
        current_anthropic = "********" if self.config.get("anthropic_api_key") else "No configurada"
        self.console.print("API Key de Anthropic: " + 
            f"[cyan]{current_anthropic}[/cyan]")
        
        config_anthropic = self.ask_confirm("¿Desea configurar la API de Anthropic?", 
            not bool(self.config.get("anthropic_api_key")))
        
        if config_anthropic:
            key = self.ask_input("Introduzca la API Key de Anthropic", password=True)
            if key:
                self.data["anthropic_api_key"] = key
        
        # API de GitHub
        current_github = "********" if self.config.get("github_token") else "No configurada"
        self.console.print("\nToken de GitHub: " + 
            f"[cyan]{current_github}[/cyan]")
        
        config_github = self.ask_confirm("¿Desea configurar el token de GitHub?", 
            not bool(self.config.get("github_token")))
        
        if config_github:
            token = self.ask_input("Introduzca el token de GitHub", password=True)
            if token:
                self.data["github_token"] = token
        
        # API de OpenAI
        current_openai = "********" if self.config.get("openai_api_key") else "No configurada"
        self.console.print("\nAPI Key de OpenAI: " + 
            f"[cyan]{current_openai}[/cyan]")
        
        config_openai = self.ask_confirm("¿Desea configurar la API de OpenAI?", 
            not bool(self.config.get("openai_api_key")))
        
        if config_openai:
            key = self.ask_input("Introduzca la API Key de OpenAI", password=True)
            if key:
                self.data["openai_api_key"] = key
                
        return True
    
    def _step_template_config(self) -> bool:
        """Paso 3: Configuración de plantillas."""
        cli.print_header("Paso 3: Configuración de Plantillas")
        
        # Directorio de plantillas
        current_dir = self.config.get("templates_directory", "templates")
        self.console.print("Directorio de plantillas actual: " + 
            f"[cyan]{current_dir}[/cyan]")
        
        change_dir = self.ask_confirm("¿Desea cambiar el directorio de plantillas?", False)
        if change_dir:
            templates_dir = self.ask_input(
                "Introduzca la ruta al directorio de plantillas", 
                current_dir
            )
            self.data["templates_directory"] = templates_dir
        else:
            self.data["templates_directory"] = current_dir
        
        # Actualización automática de plantillas
        current_auto = self.config.get("auto_update_templates", True)
        self.console.print("\nActualización automática de plantillas: " + 
            f"[cyan]{'Activada' if current_auto else 'Desactivada'}[/cyan]")
        
        self.data["auto_update_templates"] = self.ask_confirm(
            "¿Activar actualización automática de plantillas?", 
            current_auto
        )
        
        return True
    
    def _step_sync_config(self) -> bool:
        """Paso 4: Configuración de sincronización."""
        cli.print_header("Paso 4: Configuración de Sincronización")
        
        # Activar sincronización
        current_enabled = self.config.get("sync_enabled", False)
        self.console.print("Sincronización: " + 
            f"[cyan]{'Activada' if current_enabled else 'Desactivada'}[/cyan]")
        
        enabled = self.ask_confirm("¿Activar sincronización?", current_enabled)
        self.data["sync_enabled"] = enabled
        
        if enabled:
            # Proveedor de sincronización
            providers = ["local", "dropbox", "google_drive", "onedrive"]
            current_provider = self.config.get("sync_provider", "local")
            
            self.console.print("\nProveedor de sincronización actual: " + 
                f"[cyan]{current_provider}[/cyan]")
            
            index = providers.index(current_provider) if current_provider in providers else 0
            provider = self.ask_choice(
                "Seleccione el proveedor de sincronización", 
                providers, 
                default=index
            )
            self.data["sync_provider"] = provider
            
            # Directorio de sincronización para proveedor local
            if provider == "local":
                current_dir = self.config.get("sync_directory", str(Path.home() / ".projectprompt" / "sync"))
                self.console.print("\nDirectorio de sincronización actual: " + 
                    f"[cyan]{current_dir}[/cyan]")
                
                sync_dir = self.ask_input(
                    "Introduzca la ruta al directorio de sincronización", 
                    current_dir
                )
                self.data["sync_directory"] = os.path.expanduser(sync_dir)
        
        return True
    
    def _step_review(self) -> bool:
        """Paso 5: Revisión y confirmación."""
        cli.print_header("Paso 5: Revisión y Confirmación")
        
        self.console.print("[bold]Resumen de la configuración:[/bold]\n")
        
        # Mostrar configuración general
        self.console.print("[bold]Configuración General:[/bold]")
        self.console.print(f"  Nivel de log: [cyan]{self.data['log_level']}[/cyan]")
        self.console.print(f"  Directorio de datos: [cyan]{self.data['data_directory']}[/cyan]")
        self.console.print(f"  Tema: [cyan]{self.data['theme']}[/cyan]\n")
        
        # Mostrar configuración de APIs
        self.console.print("[bold]Claves de API:[/bold]")
        
        # Anthropic API
        if "anthropic_api_key" in self.data:
            self.console.print("  API Anthropic: [green]Configurada[/green]")
        elif self.config.get("anthropic_api_key"):
            self.console.print("  API Anthropic: [cyan]No modificada[/cyan]")
        else:
            self.console.print("  API Anthropic: [yellow]No configurada[/yellow]")
        
        # GitHub API
        if "github_token" in self.data:
            self.console.print("  Token GitHub: [green]Configurado[/green]")
        elif self.config.get("github_token"):
            self.console.print("  Token GitHub: [cyan]No modificado[/cyan]")
        else:
            self.console.print("  Token GitHub: [yellow]No configurado[/yellow]")
        
        # OpenAI API
        if "openai_api_key" in self.data:
            self.console.print("  API OpenAI: [green]Configurada[/green]")
        elif self.config.get("openai_api_key"):
            self.console.print("  API OpenAI: [cyan]No modificada[/cyan]")
        else:
            self.console.print("  API OpenAI: [yellow]No configurada[/yellow]\n")
        
        # Mostrar configuración de plantillas
        self.console.print("[bold]Configuración de Plantillas:[/bold]")
        self.console.print(f"  Directorio: [cyan]{self.data['templates_directory']}[/cyan]")
        auto_update = "Activada" if self.data["auto_update_templates"] else "Desactivada"
        self.console.print(f"  Actualización automática: [cyan]{auto_update}[/cyan]\n")
        
        # Mostrar configuración de sincronización
        self.console.print("[bold]Configuración de Sincronización:[/bold]")
        sync_status = "Activada" if self.data["sync_enabled"] else "Desactivada"
        self.console.print(f"  Sincronización: [cyan]{sync_status}[/cyan]")
        
        if self.data["sync_enabled"]:
            self.console.print(f"  Proveedor: [cyan]{self.data['sync_provider']}[/cyan]")
            if self.data["sync_provider"] == "local" and "sync_directory" in self.data:
                self.console.print(f"  Directorio: [cyan]{self.data['sync_directory']}[/cyan]")
        
        # Confirmar para guardar
        return self.ask_confirm("\n¿Guardar esta configuración?", True)
    
    def _process_result(self) -> Dict[str, Any]:
        """
        Guarda la configuración y devuelve los datos actualizados.
        
        Returns:
            Diccionario con la configuración actualizada
        """
        # Actualizar la configuración
        updated_config = self.config.copy()
        updated_config.update(self.data)
        
        # Guardar configuración
        self.show_spinner("Guardando configuración...", lambda: save_config(updated_config))
        
        self.console.print("\n[green]¡Configuración guardada correctamente![/green]")
        
        return updated_config
