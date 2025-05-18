#!/usr/bin/env python3
"""
Clase base para todos los asistentes (wizards) de ProjectPrompt.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, TypeVar, Generic, Union

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.ui.cli import cli


T = TypeVar('T')


class BaseWizard(Generic[T], ABC):
    """
    Clase base para todos los asistentes de configuración paso a paso.
    Define la estructura y flujo de control básicos para cualquier asistente.
    """
    
    def __init__(self, title: str, description: str = ""):
        """
        Inicializa un nuevo asistente.
        
        Args:
            title: Título del asistente
            description: Descripción corta del propósito del asistente
        """
        self.title = title
        self.description = description
        self.console = Console()
        self.steps: List[Callable[[], bool]] = []
        self.current_step = 0
        self.data: Dict[str, Any] = {}
        
    def add_step(self, step_function: Callable[[], bool]):
        """
        Añade un paso al asistente.
        
        Args:
            step_function: Función que implementa el paso.
                           Debe devolver True para continuar, False para volver atrás.
        """
        self.steps.append(step_function)
    
    def start(self) -> Optional[T]:
        """
        Inicia el asistente y ejecuta los pasos secuencialmente.
        
        Returns:
            Resultado del asistente o None si fue cancelado
        """
        if not self.steps:
            self.console.print("[bold red]Error:[/bold red] El asistente no tiene pasos definidos.")
            return None
        
        # Mostrar pantalla de bienvenida
        self._show_welcome()
        
        # Procesar pasos
        self.current_step = 0
        while 0 <= self.current_step < len(self.steps):
            try:
                # Ejecutar paso actual
                result = self.steps[self.current_step]()
                
                # Avanzar o retroceder según resultado
                if result:
                    self.current_step += 1
                else:
                    self.current_step -= 1
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Asistente cancelado por el usuario.[/yellow]")
                return None
            
            # Limpiar pantalla entre pasos
            if 0 <= self.current_step < len(self.steps):
                cli.clear_screen()
        
        # Si salimos porque current_step < 0, significa cancelación
        if self.current_step < 0:
            self.console.print("\n[yellow]Asistente cancelado por el usuario.[/yellow]")
            return None
            
        # Procesar y devolver resultado
        return self._process_result()
    
    def _show_welcome(self):
        """Muestra la pantalla de bienvenida del asistente."""
        cli.clear_screen()
        cli.print_header(f"Asistente: {self.title}")
        
        if self.description:
            self.console.print(Panel(self.description, expand=False))
        
        self.console.print("\n[dim]Presione Enter para comenzar o Ctrl+C para cancelar[/dim]")
        input()
        cli.clear_screen()
    
    def _show_progress(self):
        """Muestra el progreso actual del asistente."""
        progress = f"Paso {self.current_step + 1} de {len(self.steps)}"
        self.console.print(f"[dim]{progress}[/dim]")
    
    def ask_input(self, prompt: str, default: str = "", password: bool = False) -> str:
        """
        Solicita una entrada de texto al usuario.
        
        Args:
            prompt: Mensaje a mostrar
            default: Valor por defecto
            password: Si es True, oculta la entrada
            
        Returns:
            Texto ingresado por el usuario
        """
        return Prompt.ask(
            prompt, 
            default=default, 
            password=password,
            console=self.console
        )
    
    def ask_confirm(self, prompt: str, default: bool = True) -> bool:
        """
        Solicita una confirmación al usuario.
        
        Args:
            prompt: Mensaje a mostrar
            default: Valor por defecto
            
        Returns:
            True si el usuario confirma, False en caso contrario
        """
        return Confirm.ask(prompt, default=default, console=self.console)
    
    def ask_choice(self, prompt: str, choices: List[str], default: int = 0) -> str:
        """
        Solicita al usuario que elija una opción de una lista.
        
        Args:
            prompt: Mensaje a mostrar
            choices: Lista de opciones
            default: Índice de la opción por defecto
            
        Returns:
            Opción seleccionada
        """
        if not choices:
            raise ValueError("La lista de opciones no puede estar vacía")
            
        # Mostrar opciones numeradas
        self.console.print(f"\n{prompt}")
        for i, choice in enumerate(choices):
            self.console.print(f"  [cyan]{i+1}.[/cyan] {choice}")
        
        # Solicitar selección
        while True:
            try:
                selected = IntPrompt.ask(
                    "\nSeleccione una opción",
                    default=default + 1,
                    console=self.console
                )
                
                if 1 <= selected <= len(choices):
                    return choices[selected - 1]
                else:
                    self.console.print("[red]Opción inválida. Intente de nuevo.[/red]")
            except ValueError:
                self.console.print("[red]Por favor ingrese un número.[/red]")
    
    def show_spinner(self, text: str, func: Callable[[], T]) -> T:
        """
        Muestra un spinner mientras se ejecuta una función.
        
        Args:
            text: Texto a mostrar junto al spinner
            func: Función a ejecutar
            
        Returns:
            Resultado de la función
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task(text, total=None)
            result = func()
            progress.update(task, completed=True)
            return result
    
    @abstractmethod
    def _process_result(self) -> T:
        """
        Procesa los datos recopilados y devuelve el resultado del asistente.
        Debe ser implementado por las clases derivadas.
        
        Returns:
            Resultado del asistente
        """
        pass
