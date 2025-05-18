#!/usr/bin/env python3
"""
Asistente para la creación y configuración de proyectos.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.ui.wizards.base_wizard import BaseWizard
from src.ui.cli import cli
from src.analyzers.project_scanner import ProjectScanner
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ProjectWizard(BaseWizard[Dict[str, Any]]):
    """
    Asistente interactivo para crear y configurar proyectos.
    Guía al usuario a través del proceso de creación o importación de proyectos.
    """
    
    def __init__(self):
        """Inicializa el asistente de proyectos."""
        super().__init__(
            title="Configuración de Proyecto", 
            description="Este asistente le guiará en la creación o importación de un proyecto."
        )
        
        # Añadir pasos del asistente
        self.add_step(self._step_project_type)
        self.add_step(self._step_project_details)
        self.add_step(self._step_project_location)
        self.add_step(self._step_configuration_options)
        self.add_step(self._step_confirmation)
    
    def _step_project_type(self) -> bool:
        """Paso 1: Seleccionar tipo de proyecto (nuevo o existente)."""
        cli.print_header("Paso 1: Tipo de Proyecto")
        
        options = [
            "Crear nuevo proyecto",
            "Importar proyecto existente",
            "Analizar proyecto existente"
        ]
        
        choice = self.ask_choice(
            "¿Qué tipo de operación desea realizar?", 
            options
        )
        
        self.data["project_type"] = {
            "Crear nuevo proyecto": "new",
            "Importar proyecto existente": "import",
            "Analizar proyecto existente": "analyze"
        }[choice]
        
        return True
    
    def _step_project_details(self) -> bool:
        """Paso 2: Recoger detalles del proyecto."""
        cli.print_header("Paso 2: Detalles del Proyecto")
        
        if self.data["project_type"] == "new":
            self.data["project_name"] = self.ask_input("Nombre del proyecto", "mi_proyecto")
            
            # Seleccionar plantilla
            templates = ["Python básico", "Django", "Flask", "FastAPI", "React", "Node.js", "Vue.js"]
            self.data["template"] = self.ask_choice("Seleccione una plantilla", templates)
            
        elif self.data["project_type"] in ["import", "analyze"]:
            if "project_path" not in self.data:
                self.data["project_path"] = self.ask_input(
                    "Ruta al proyecto existente", 
                    str(Path.cwd())
                )
                
            # Verificar que la ruta existe
            if not os.path.isdir(self.data["project_path"]):
                self.console.print(f"[red]La ruta {self.data['project_path']} no existe o no es un directorio.[/red]")
                del self.data["project_path"]
                return False
                
            # Detectar nombre del proyecto de la ruta
            self.data["project_name"] = os.path.basename(os.path.abspath(self.data["project_path"]))
            self.console.print(f"Nombre del proyecto detectado: [cyan]{self.data['project_name']}[/cyan]")
            
            # Si estamos analizando, realizar un escaneo rápido
            if self.data["project_type"] == "analyze":
                self.console.print("\nRealizando análisis preliminar...")
                scanner = ProjectScanner(self.data["project_path"])
                
                def scan():
                    return scanner.scan(max_files=100)
                
                scan_result = self.show_spinner("Analizando estructura del proyecto...", scan)
                
                # Mostrar resumen del análisis
                self.console.print(f"\nArchivos detectados: [cyan]{scan_result['file_count']}[/cyan]")
                if scan_result["languages"]:
                    self.console.print("Lenguajes detectados:")
                    for lang, count in scan_result["languages"].items():
                        self.console.print(f"  - {lang}: {count} archivos")
        
        return self.ask_confirm("¿Continuar al siguiente paso?")
    
    def _step_project_location(self) -> bool:
        """Paso 3: Configurar ubicación del proyecto."""
        cli.print_header("Paso 3: Ubicación del Proyecto")
        
        if self.data["project_type"] == "new":
            default_path = os.path.join(os.getcwd(), self.data["project_name"])
            self.data["project_path"] = self.ask_input(
                "Ubicación para el nuevo proyecto", 
                default_path
            )
            
            # Verificar si el directorio ya existe
            if os.path.exists(self.data["project_path"]):
                overwrite = self.ask_confirm(
                    f"La carpeta {self.data['project_path']} ya existe. ¿Desea sobrescribirla?",
                    False
                )
                if not overwrite:
                    return False
        
        return True
    
    def _step_configuration_options(self) -> bool:
        """Paso 4: Configurar opciones adicionales."""
        cli.print_header("Paso 4: Opciones Adicionales")
        
        # Opciones comunes para todos los tipos de proyecto
        self.data["git_init"] = self.ask_confirm("¿Inicializar repositorio Git?", True)
        
        if self.data["project_type"] == "new":
            self.data["create_readme"] = self.ask_confirm("¿Crear README.md?", True)
            self.data["create_gitignore"] = self.ask_confirm("¿Crear .gitignore?", True)
            
            if "Python" in self.data["template"]:
                self.data["create_venv"] = self.ask_confirm("¿Crear entorno virtual?", True)
                self.data["install_deps"] = self.ask_confirm("¿Instalar dependencias?", True)
        
        elif self.data["project_type"] == "import":
            self.data["analyze_deps"] = self.ask_confirm("¿Analizar dependencias?", True)
            self.data["create_config"] = self.ask_confirm("¿Crear configuración de ProjectPrompt?", True)
        
        return True
    
    def _step_confirmation(self) -> bool:
        """Paso 5: Confirmar configuración."""
        cli.print_header("Paso 5: Confirmación")
        
        self.console.print("\n[bold]Resumen de la configuración:[/bold]")
        
        if self.data["project_type"] == "new":
            self.console.print(f"Creando nuevo proyecto: [cyan]{self.data['project_name']}[/cyan]")
            self.console.print(f"Ubicación: [cyan]{self.data['project_path']}[/cyan]")
            self.console.print(f"Plantilla: [cyan]{self.data['template']}[/cyan]")
            
            options = []
            if self.data.get("git_init"):
                options.append("Inicializar Git")
            if self.data.get("create_readme"):
                options.append("Crear README.md")
            if self.data.get("create_gitignore"):
                options.append("Crear .gitignore")
            if self.data.get("create_venv"):
                options.append("Crear entorno virtual")
            if self.data.get("install_deps"):
                options.append("Instalar dependencias")
                
            if options:
                self.console.print("\nOpciones adicionales:")
                for option in options:
                    self.console.print(f"  - {option}")
        
        elif self.data["project_type"] == "import":
            self.console.print(f"Importando proyecto existente: [cyan]{self.data['project_name']}[/cyan]")
            self.console.print(f"Ubicación: [cyan]{self.data['project_path']}[/cyan]")
            
            options = []
            if self.data.get("git_init"):
                options.append("Inicializar Git (si no existe)")
            if self.data.get("analyze_deps"):
                options.append("Analizar dependencias")
            if self.data.get("create_config"):
                options.append("Crear configuración de ProjectPrompt")
                
            if options:
                self.console.print("\nOpciones adicionales:")
                for option in options:
                    self.console.print(f"  - {option}")
        
        elif self.data["project_type"] == "analyze":
            self.console.print(f"Analizando proyecto existente: [cyan]{self.data['project_name']}[/cyan]")
            self.console.print(f"Ubicación: [cyan]{self.data['project_path']}[/cyan]")
        
        # Confirmar para proceder
        return self.ask_confirm("\n¿Confirmar y proceder?", True)
    
    def _process_result(self) -> Dict[str, Any]:
        """
        Procesa los datos recopilados y devuelve la configuración del proyecto.
        
        Returns:
            Diccionario con la configuración del proyecto
        """
        self.console.print("\n[green]¡Configuración completada![/green]")
        
        # Implementación real - aquí podría iniciarse la creación/importación/análisis
        
        return self.data
