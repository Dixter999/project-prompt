#!/usr/bin/env python3
"""
Vista de gestión de subscripción para ProjectPrompt.
Este módulo proporciona las interfaces de usuario necesarias para gestionar
la suscripción del usuario, activar licencias y ver estadísticas de uso.
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime

import typer
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console

from src.utils import logger
from src.ui.cli import CLI
from src.utils.subscription_manager import get_subscription_manager, SUBSCRIPTION_LIMITS
from src.utils.license_validator import LicenseStatus

console = Console()
cli = CLI()


class SubscriptionView:
    """Vista para gestionar la subscripción del usuario."""
    
    def __init__(self):
        """Inicializa la vista de suscripción."""
        self.subscription_manager = get_subscription_manager()
    
    def show_subscription_info(self) -> None:
        """Muestra información sobre la suscripción actual del usuario."""
        cli.print_header("Información de Suscripción")
        
        stats = self.subscription_manager.get_usage_statistics()
        sub_type = stats["subscription_type"].upper()
        
        # Determinar el color según tipo de suscripción
        color = {
            "FREE": "white",
            "BASIC": "cyan",
            "PRO": "magenta",
            "TEAM": "gold3"
        }.get(sub_type, "white")
        
        # Crear panel con información básica
        panel_content = (
            f"[bold]{sub_type}[/bold]\n\n"
            f"Estado: [{'green' if stats['is_premium'] else 'yellow'}]"
            f"{'PREMIUM' if stats['is_premium'] else 'GRATUITO'}[/]\n"
        )
        
        # Añadir información de expiración si es premium
        if stats["is_premium"]:
            license_key = typer.get_app_dir("project-prompt")
            license_key = ""  # No mostrar la clave completa por seguridad
            panel_content += f"Licencia: •••••••••••••\n"
        
        console.print(Panel.fit(
            panel_content,
            title="[b]Suscripción Actual[/b]",
            border_style=color
        ))
        
        # Tabla de uso
        table = Table(title="Uso de Recursos", border_style="bright_black")
        table.add_column("Recurso", style="cyan")
        table.add_column("Usado", style="green")
        table.add_column("Límite", style="yellow")
        table.add_column("Estado", style="magenta")
        
        # Función para calcular estado y porcentaje
        def get_usage_state(used, limit):
            if limit == "∞":
                return "[green]Ilimitado[/green]", 0
            
            percent = (used / int(limit)) * 100 if int(limit) > 0 else 0
            if percent < 50:
                return f"[green]{percent:.1f}%[/green]", percent
            elif percent < 80:
                return f"[yellow]{percent:.1f}%[/yellow]", percent
            else:
                return f"[red]{percent:.1f}%[/red]", percent
        
        # Prompts diarios
        state, _ = get_usage_state(stats["daily_prompts_used"], stats["daily_prompts_limit"])
        table.add_row(
            "Prompts diarios", 
            str(stats["daily_prompts_used"]), 
            str(stats["daily_prompts_limit"]),
            state
        )
        
        # Llamadas API diarias
        state, _ = get_usage_state(stats["daily_api_calls_used"], stats["daily_api_calls_limit"])
        table.add_row(
            "Llamadas API", 
            str(stats["daily_api_calls_used"]), 
            str(stats["daily_api_calls_limit"]),
            state
        )
        
        console.print(table)
        
        # Tabla de características disponibles
        features_table = Table(title="Características Disponibles", border_style="bright_black")
        features_table.add_column("Característica", style="cyan")
        features_table.add_column("Disponible", style="green")
        
        # Mapeo de características a nombres amigables
        feature_names = {
            "basic_analysis": "Análisis básico de código",
            "documentation": "Navegación de documentación",
            "implementation_prompts": "Guías de implementación",
            "test_generation": "Generación de tests unitarios",
            "completeness_verification": "Verificación de completitud",
            "project_dashboard": "Dashboard de proyecto"
        }
        
        # Mostrar estado de características
        all_features = list(feature_names.keys())
        available = stats["available_features"]
        
        for feature in all_features:
            name = feature_names.get(feature, feature)
            is_available = feature in available
            status = "[green]✓[/green]" if is_available else "[red]✗[/red]"
            features_table.add_row(name, status)
            
        console.print(features_table)
    
    def activate_license(self, license_key: str) -> None:
        """
        Activa una licencia para la suscripción premium.
        
        Args:
            license_key: Clave de licencia a activar
        """
        cli.print_header("Activación de Licencia")
        
        console.print(f"Verificando licencia: [dim]{license_key}[/dim]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("Verificando licencia...", total=None)
            success, message = self.subscription_manager.activate_license(license_key)
            progress.remove_task(task)
        
        if success:
            cli.print_success(message)
            self.show_subscription_info()
        else:
            cli.print_error(message)
    
    def deactivate_license(self) -> None:
        """Desactiva la licencia actual y revierte a la versión gratuita."""
        cli.print_header("Desactivación de Licencia")
        
        # Confirmar acción
        if not typer.confirm("¿Estás seguro de que deseas desactivar tu licencia premium?"):
            cli.print_warning("Operación cancelada.")
            return
        
        success, message = self.subscription_manager.deactivate_license()
        
        if success:
            cli.print_success(message)
        else:
            cli.print_error(message)
    
    def show_subscription_plans(self) -> None:
        """Muestra información sobre los planes de suscripción disponibles."""
        cli.print_header("Planes de Suscripción")
        
        table = Table(title="Planes Disponibles", border_style="bright_black", highlight=True)
        table.add_column("Plan", style="bold")
        table.add_column("Precio", style="green")
        table.add_column("Prompts/día", justify="right")
        table.add_column("API/día", justify="right")
        table.add_column("Características", justify="left")
        
        # Definir los planes
        plans = [
            {
                "name": "FREE",
                "price": "Gratis",
                "color": "white",
                "prompts": SUBSCRIPTION_LIMITS["free"]["daily_prompts"],
                "api_calls": SUBSCRIPTION_LIMITS["free"]["api_calls_per_day"],
                "features": SUBSCRIPTION_LIMITS["free"]["features"]
            },
            {
                "name": "BASIC",
                "price": "$9.99/mes",
                "color": "cyan",
                "prompts": SUBSCRIPTION_LIMITS["basic"]["daily_prompts"],
                "api_calls": SUBSCRIPTION_LIMITS["basic"]["api_calls_per_day"],
                "features": SUBSCRIPTION_LIMITS["basic"]["features"]
            },
            {
                "name": "PRO",
                "price": "$19.99/mes",
                "color": "magenta",
                "prompts": SUBSCRIPTION_LIMITS["pro"]["daily_prompts"],
                "api_calls": SUBSCRIPTION_LIMITS["pro"]["api_calls_per_day"],
                "features": SUBSCRIPTION_LIMITS["pro"]["features"]
            },
            {
                "name": "TEAM",
                "price": "$49.99/mes",
                "color": "gold3",
                "prompts": SUBSCRIPTION_LIMITS["team"]["daily_prompts"],
                "api_calls": SUBSCRIPTION_LIMITS["team"]["api_calls_per_day"],
                "features": SUBSCRIPTION_LIMITS["team"]["features"]
            }
        ]
        
        # Función para mostrar límites
        def format_limit(limit):
            return "∞" if limit == -1 else str(limit)
        
        # Función para mostrar características disponibles
        def format_features(features: List[str]) -> str:
            feature_names = {
                "basic_analysis": "Análisis básico",
                "documentation": "Documentación",
                "implementation_prompts": "Guías de implementación",
                "test_generation": "Generación de tests",
                "completeness_verification": "Verificación de completitud",
                "project_dashboard": "Dashboard de proyecto"
            }
            
            formatted = []
            for feat in features:
                name = feature_names.get(feat, feat)
                formatted.append(f"✓ {name}")
            
            return "\n".join(formatted)
        
        # Añadir filas con los planes
        for plan in plans:
            table.add_row(
                f"[{plan['color']}]{plan['name']}[/{plan['color']}]",
                plan["price"],
                format_limit(plan["prompts"]),
                format_limit(plan["api_calls"]),
                format_features(plan["features"])
            )
            
        console.print(table)
        
        # Información de compra
        console.print(Panel(
            "Para adquirir una suscripción premium, visita:\n"
            "[link=https://www.projectprompt.dev/pricing]https://www.projectprompt.dev/pricing[/link]",
            title="Comprar Suscripción",
            border_style="green"
        ))


# Instancia global para fácil acceso
subscription_view = SubscriptionView()

# Funciones de conveniencia
show_subscription = subscription_view.show_subscription_info
activate_license = subscription_view.activate_license
deactivate_license = subscription_view.deactivate_license
show_plans = subscription_view.show_subscription_plans
