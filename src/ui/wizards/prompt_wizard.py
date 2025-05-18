#!/usr/bin/env python3
"""
Asistente para la creación de prompts personalizados.
"""

from typing import Dict, Any, List, Optional
import os
from pathlib import Path

from src.ui.wizards.base_wizard import BaseWizard
from src.ui.cli import cli
from src.utils.config import get_config


class PromptWizard(BaseWizard[Dict[str, Any]]):
    """
    Asistente interactivo para crear prompts personalizados.
    Guía al usuario a través del proceso de creación de prompts optimizados.
    """
    
    def __init__(self, project_path: Optional[str] = None):
        """
        Inicializa el asistente de prompts.
        
        Args:
            project_path: Ruta al proyecto para el que se crea el prompt (opcional)
        """
        super().__init__(
            title="Creación de Prompt", 
            description="Este asistente le guiará en la creación de prompts optimizados."
        )
        
        self.project_path = project_path or os.getcwd()
        
        # Añadir pasos del asistente
        self.add_step(self._step_prompt_type)
        self.add_step(self._step_prompt_purpose)
        self.add_step(self._step_context_options)
        self.add_step(self._step_llm_selection)
        self.add_step(self._step_customization)
        self.add_step(self._step_preview)
    
    def _step_prompt_type(self) -> bool:
        """Paso 1: Seleccionar tipo de prompt."""
        cli.print_header("Paso 1: Tipo de Prompt")
        
        prompt_types = [
            "Generación de código",
            "Análisis de código",
            "Documentación",
            "Explicación de código",
            "Personalizado"
        ]
        
        selected = self.ask_choice(
            "Seleccione el tipo de prompt que desea crear:",
            prompt_types
        )
        
        # Mapear selección a tipo interno
        type_map = {
            "Generación de código": "code_generation",
            "Análisis de código": "code_analysis",
            "Documentación": "documentation",
            "Explicación de código": "code_explanation",
            "Personalizado": "custom"
        }
        
        self.data["prompt_type"] = type_map[selected]
        self.data["prompt_type_name"] = selected
        
        return True
    
    def _step_prompt_purpose(self) -> bool:
        """Paso 2: Definir propósito del prompt."""
        cli.print_header("Paso 2: Propósito del Prompt")
        
        # Nombre del prompt
        self.data["prompt_name"] = self.ask_input(
            "Nombre del prompt (para referencia)",
            f"{self.data['prompt_type_name']} Prompt"
        )
        
        # Descripción detallada según el tipo
        if self.data["prompt_type"] == "code_generation":
            purpose_prompt = "Describa qué código desea generar:"
            default_desc = "Generar código para..."
        elif self.data["prompt_type"] == "code_analysis":
            purpose_prompt = "Describa qué aspecto del código desea analizar:"
            default_desc = "Analizar el código para identificar..."
        elif self.data["prompt_type"] == "documentation":
            purpose_prompt = "Describa qué documentación necesita generar:"
            default_desc = "Generar documentación para..."
        elif self.data["prompt_type"] == "code_explanation":
            purpose_prompt = "Describa qué código necesita explicar:"
            default_desc = "Explicar cómo funciona..."
        else:  # custom
            purpose_prompt = "Describa el propósito de este prompt:"
            default_desc = "Este prompt será usado para..."
        
        self.console.print("\n[italic]Sea específico sobre lo que desea lograr con este prompt.[/italic]")
        self.data["prompt_purpose"] = self.ask_input(purpose_prompt, default_desc)
        
        return True
    
    def _step_context_options(self) -> bool:
        """Paso 3: Configurar opciones de contexto."""
        cli.print_header("Paso 3: Opciones de Contexto")
        
        # Verificar si hay un proyecto
        self.console.print(f"Proyecto actual: [cyan]{os.path.basename(self.project_path)}[/cyan]")
        self.console.print(f"Ruta: [dim]{self.project_path}[/dim]")
        
        # Incluir contexto del proyecto
        self.data["include_project_context"] = self.ask_confirm(
            "¿Incluir contexto del proyecto en el prompt?",
            True
        )
        
        if self.data["include_project_context"]:
            # Nivel de detalle del contexto
            detail_levels = ["Básico", "Estándar", "Completo"]
            detail_desc = [
                "Solo estructura y archivos principales",
                "Estructura, dependencias y funciones principales",
                "Análisis completo del código fuente"
            ]
            
            self.console.print("\n[bold]Nivel de detalle del contexto:[/bold]")
            for i, (level, desc) in enumerate(zip(detail_levels, detail_desc)):
                self.console.print(f"  [cyan]{i+1}.[/cyan] {level}: {desc}")
            
            selected = self.ask_choice(
                "Seleccione el nivel de detalle:", 
                detail_levels,
                default=1  # Estándar por defecto
            )
            
            self.data["context_detail"] = {
                "Básico": "basic",
                "Estándar": "standard",
                "Completo": "complete"
            }[selected]
            
            # Opciones de contexto específicas
            self.console.print("\n[bold]Elementos a incluir en el contexto:[/bold]")
            self.data["include_deps"] = self.ask_confirm("¿Incluir dependencias?", True)
            self.data["include_docs"] = self.ask_confirm("¿Incluir documentación existente?", True)
            self.data["include_comments"] = self.ask_confirm("¿Incluir comentarios del código?", True)
            self.data["include_tests"] = self.ask_confirm("¿Incluir tests?", False)
        
        return True
    
    def _step_llm_selection(self) -> bool:
        """Paso 4: Seleccionar modelo de lenguaje."""
        cli.print_header("Paso 4: Modelo de Lenguaje")
        
        # Obtener modelos disponibles según configuración
        config = get_config()
        models = []
        
        if config.get("anthropic_api_key"):
            models.extend(["Claude 3 Opus", "Claude 3 Sonnet", "Claude 3 Haiku"])
        
        if config.get("openai_api_key"):
            models.extend(["GPT-4o", "GPT-4", "GPT-3.5 Turbo"])
        
        # Añadir opción genérica si no hay APIs configuradas
        if not models:
            models = ["Modelo genérico (sin API)"]
            self.console.print("[yellow]No se detectaron claves de API configuradas.[/yellow]")
            self.console.print("[yellow]Se usará una plantilla genérica de prompt.[/yellow]\n")
        
        selected = self.ask_choice(
            "Seleccione el modelo de lenguaje a utilizar:",
            models,
            default=0
        )
        
        self.data["llm_model"] = selected
        
        # Preguntar por temperatura si hay un modelo específico
        if selected != "Modelo genérico (sin API)":
            temperatures = ["0.0 - Determinista", "0.3 - Conservador", "0.7 - Balanceado", "1.0 - Creativo"]
            temp = self.ask_choice(
                "Seleccione el nivel de creatividad/temperatura:",
                temperatures,
                default=2  # Balanceado por defecto
            )
            
            # Extraer valor numérico
            self.data["temperature"] = float(temp.split(" - ")[0])
        
        return True
    
    def _step_customization(self) -> bool:
        """Paso 5: Personalización adicional."""
        cli.print_header("Paso 5: Personalización")
        
        # Instrucciones específicas adicionales
        self.console.print("[bold]Instrucciones adicionales:[/bold]")
        self.console.print("[italic]Incluya cualquier instrucción específica que desee añadir al prompt.[/italic]")
        self.console.print("[italic]Ejemplo: Usa patrones de diseño específicos, sigue convenciones PEP-8, etc.[/italic]\n")
        
        self.data["additional_instructions"] = self.ask_input(
            "Instrucciones adicionales",
            "No se requieren instrucciones adicionales."
        )
        
        # Formato de salida preferido
        output_formats = ["Código con explicaciones", "Solo código", "Markdown explicativo", "Personalizado"]
        selected_format = self.ask_choice(
            "\nSeleccione el formato de salida preferido:",
            output_formats,
            default=0
        )
        
        self.data["output_format"] = selected_format
        
        if selected_format == "Personalizado":
            self.data["custom_format"] = self.ask_input(
                "Describa el formato personalizado que desea",
                "Formato con estructura de..."
            )
        
        # Guardar como plantilla
        self.data["save_as_template"] = self.ask_confirm(
            "\n¿Desea guardar este prompt como plantilla para uso futuro?",
            True
        )
        
        if self.data["save_as_template"]:
            self.data["template_name"] = self.ask_input(
                "Nombre para la plantilla",
                self.data["prompt_name"].replace(" ", "_").lower()
            )
        
        return True
    
    def _step_preview(self) -> bool:
        """Paso 6: Vista previa y confirmación."""
        cli.print_header("Paso 6: Vista Previa")
        
        # Generar vista previa del prompt
        preview = self._generate_prompt_preview()
        
        self.console.print("[bold]Vista previa del prompt:[/bold]\n")
        self.console.print(Panel(preview, expand=False))
        
        # Confirmar finalización
        return self.ask_confirm("\n¿Finalizar y crear el prompt?", True)
    
    def _generate_prompt_preview(self) -> str:
        """
        Genera una vista previa del prompt basada en las opciones seleccionadas.
        
        Returns:
            Texto del prompt
        """
        preview = f"# {self.data['prompt_name']}\n\n"
        preview += f"## Propósito\n{self.data['prompt_purpose']}\n\n"
        
        # Sección de contexto si aplica
        if self.data.get("include_project_context"):
            preview += "## Contexto del Proyecto\n"
            preview += f"Proyecto: {os.path.basename(self.project_path)}\n"
            preview += f"Nivel de detalle: {self.data['context_detail']}\n"
            
            elements = []
            if self.data.get("include_deps"):
                elements.append("dependencias")
            if self.data.get("include_docs"):
                elements.append("documentación")
            if self.data.get("include_comments"):
                elements.append("comentarios")
            if self.data.get("include_tests"):
                elements.append("tests")
                
            if elements:
                preview += f"Incluye: {', '.join(elements)}\n"
            preview += "[Aquí se incluirá el contexto generado automáticamente...]\n\n"
        
        # Modelo y configuración
        preview += f"## Modelo: {self.data['llm_model']}\n"
        if "temperature" in self.data:
            preview += f"Temperatura: {self.data['temperature']}\n\n"
        
        # Instrucciones adicionales
        if self.data["additional_instructions"] != "No se requieren instrucciones adicionales.":
            preview += "## Instrucciones Adicionales\n"
            preview += f"{self.data['additional_instructions']}\n\n"
        
        # Formato de salida
        preview += "## Formato de Salida\n"
        if self.data["output_format"] == "Personalizado":
            preview += f"{self.data['custom_format']}\n"
        else:
            preview += f"{self.data['output_format']}\n"
        
        return preview
    
    def _process_result(self) -> Dict[str, Any]:
        """
        Procesa los datos recopilados y genera el prompt.
        
        Returns:
            Diccionario con la información del prompt
        """
        # Generar el prompt completo
        prompt_text = self._generate_prompt_preview()
        self.data["prompt_text"] = prompt_text
        
        # Guardar como plantilla si se solicitó
        if self.data.get("save_as_template"):
            template_dir = Path(get_config().get('templates_directory', 'templates'))
            
            # Asegurar que el directorio existe
            def save_template():
                try:
                    if not os.path.isabs(template_dir):
                        template_dir_path = Path.cwd() / template_dir
                    else:
                        template_dir_path = template_dir
                        
                    template_dir_path.mkdir(exist_ok=True, parents=True)
                    
                    template_file = template_dir_path / f"{self.data['template_name']}.md"
                    with open(template_file, 'w') as f:
                        f.write(prompt_text)
                        
                    self.data["template_path"] = str(template_file)
                    return True
                except Exception as e:
                    self.console.print(f"[red]Error al guardar la plantilla: {e}[/red]")
                    return False
            
            success = self.show_spinner("Guardando plantilla...", save_template)
            
            if success:
                self.console.print(f"\n[green]Plantilla guardada como '{self.data['template_name']}.md'[/green]")
        
        self.console.print("\n[green]¡Prompt creado exitosamente![/green]")
        
        return self.data
