#!/usr/bin/env python3
"""
Sistema de temas para la interfaz de línea de comandos.
Este módulo proporciona la funcionalidad para cambiar el aspecto de la CLI.
"""

from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass

from rich.style import Style
from rich.theme import Theme as RichTheme
from rich.console import Console

# We'll use lazy imports to avoid circular dependencies
# The actual imports will happen inside the functions that need them


class ElementType(str, Enum):
    """Tipos de elementos de UI que pueden tener estilos temáticos."""
    HEADER = "header"
    SUBHEADER = "subheader"
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    ACCENT = "accent"
    PROMPT = "prompt"
    HIGHLIGHT = "highlight"
    CODE = "code"
    LINK = "link"
    MENU = "menu"
    TABLE_HEADER = "table_header"
    TABLE_ROW = "table_row"
    DIM = "dim"
    NORMAL = "normal"
    
    
@dataclass
class ColorScheme:
    """Esquema de colores para un tema."""
    primary: str
    secondary: str
    tertiary: str
    success: str
    error: str
    warning: str
    info: str
    accent: str
    background: str
    foreground: str


class Theme:
    """
    Clase que representa un tema visual para la interfaz de línea de comandos.
    Define colores y estilos para diferentes elementos de la interfaz.
    """
    
    def __init__(self, name: str, color_scheme: ColorScheme):
        """
        Inicializa un nuevo tema.
        
        Args:
            name: Nombre del tema
            color_scheme: Esquema de colores para el tema
        """
        self.name = name
        self.colors = color_scheme
        self.styles: Dict[ElementType, Style] = self._create_styles()
    
    def _create_styles(self) -> Dict[ElementType, Style]:
        """
        Crea los estilos para los diferentes elementos basándose en el esquema de colores.
        
        Returns:
            Diccionario con los estilos para cada tipo de elemento
        """
        return {
            ElementType.HEADER: Style(color=self.colors.primary, bold=True),
            ElementType.SUBHEADER: Style(color=self.colors.secondary, bold=True),
            ElementType.SUCCESS: Style(color=self.colors.success, bold=True),
            ElementType.ERROR: Style(color=self.colors.error, bold=True),
            ElementType.WARNING: Style(color=self.colors.warning, bold=True),
            ElementType.INFO: Style(color=self.colors.info),
            ElementType.ACCENT: Style(color=self.colors.accent),
            ElementType.PROMPT: Style(color=self.colors.primary, bold=True),
            ElementType.HIGHLIGHT: Style(color=self.colors.tertiary, bold=True),
            ElementType.CODE: Style(color=self.colors.secondary, bgcolor="black"),
            ElementType.LINK: Style(color=self.colors.accent, underline=True),
            ElementType.MENU: Style(color=self.colors.primary),
            ElementType.TABLE_HEADER: Style(color=self.colors.secondary, bold=True),
            ElementType.TABLE_ROW: Style(color=self.colors.foreground),
            ElementType.DIM: Style(color=self.colors.foreground, dim=True),
            ElementType.NORMAL: Style(color=self.colors.foreground),
        }
    
    def get_rich_theme(self) -> RichTheme:
        """
        Genera un tema Rich basado en este tema.
        
        Returns:
            Tema para la biblioteca Rich
        """
        rich_styles = {}
        
        for element_type, style in self.styles.items():
            rich_styles[element_type.value] = style
            
        # Alias comunes para facilitar su uso
        rich_styles["h1"] = self.styles[ElementType.HEADER]
        rich_styles["h2"] = self.styles[ElementType.SUBHEADER]
        rich_styles["success"] = self.styles[ElementType.SUCCESS]
        rich_styles["error"] = self.styles[ElementType.ERROR]
        rich_styles["warning"] = self.styles[ElementType.WARNING]
        rich_styles["info"] = self.styles[ElementType.INFO]
        rich_styles["code"] = self.styles[ElementType.CODE]
            
        return RichTheme(rich_styles)
    
    def apply_to_console(self, console: Console) -> None:
        """
        Aplica este tema a una consola Rich.
        
        Args:
            console: Consola Rich a la que aplicar el tema
        """
        console.theme = self.get_rich_theme()


# Definición de temas disponibles
THEMES = {
    "default": Theme(
        name="Default",
        color_scheme=ColorScheme(
            primary="blue",
            secondary="cyan",
            tertiary="magenta",
            success="green",
            error="red",
            warning="yellow",
            info="bright_white",
            accent="bright_cyan",
            background="black",
            foreground="white"
        )
    ),
    "dark": Theme(
        name="Dark",
        color_scheme=ColorScheme(
            primary="bright_blue",
            secondary="bright_cyan",
            tertiary="bright_magenta",
            success="bright_green",
            error="bright_red",
            warning="bright_yellow",
            info="white",
            accent="bright_cyan",
            background="black",
            foreground="bright_white"
        )
    ),
    "light": Theme(
        name="Light",
        color_scheme=ColorScheme(
            primary="blue",
            secondary="dark_blue",
            tertiary="purple",
            success="dark_green",
            error="dark_red",
            warning="dark_orange",
            info="black",
            accent="turquoise2",
            background="white",
            foreground="black"
        )
    ),
    "blue": Theme(
        name="Blue",
        color_scheme=ColorScheme(
            primary="bright_blue",
            secondary="cyan",
            tertiary="blue_violet",
            success="green",
            error="red",
            warning="yellow",
            info="white",
            accent="sky_blue2",
            background="navy_blue",
            foreground="white"
        )
    ),
    "green": Theme(
        name="Green",
        color_scheme=ColorScheme(
            primary="bright_green",
            secondary="green",
            tertiary="spring_green3",
            success="bright_green",
            error="red",
            warning="bright_yellow",
            info="white",
            accent="chartreuse1",
            background="dark_green",
            foreground="white"
        )
    )
}


def get_current_theme() -> Theme:
    """
    Obtiene el tema actual basado en la configuración.
    
    Returns:
        Tema actual
    """
    # Lazy import to avoid circular dependencies
    try:
        from src.utils.config import config_manager
        theme_name = config_manager.get("theme", "default")
    except (ImportError, AttributeError):
        # Fall back to default theme if config_manager is not available
        theme_name = "default"
    
    return THEMES.get(theme_name, THEMES["default"])


def apply_theme_to_console(console: Optional[Console] = None) -> Console:
    """
    Aplica el tema actual a una consola Rich.
    
    Args:
        console: Consola Rich a la que aplicar el tema (opcional)
        
    Returns:
        Consola con el tema aplicado
    """
    theme = get_current_theme()
    
    if console is None:
        console = Console()
        
    theme.apply_to_console(console)
    return console


def get_available_theme_names() -> list:
    """
    Obtiene la lista de nombres de temas disponibles.
    
    Returns:
        Lista de nombres de temas
    """
    return list(THEMES.keys())
    

def set_theme(theme_name: str) -> bool:
    """
    Establece el tema actual.
    
    Args:
        theme_name: Nombre del tema a establecer
        
    Returns:
        True si el tema se estableció correctamente, False en caso contrario
    """
    # Lazy imports to avoid circular dependencies
    from src.utils.config import get_config, save_config
    
    if theme_name not in THEMES:
        return False
        
    config = get_config()
    config["theme"] = theme_name
    save_config(config)
    
    return True
