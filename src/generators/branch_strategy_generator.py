#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generador de estrategias de branches de Git para implementaciones.
Este módulo permite generar sugerencias de nombres de branches y estructura
para implementar funcionalidades específicas.
"""
import os
import re
from typing import Dict, Any, List, Optional

from src.utils.logger import get_logger
from src.templates.git import branch_templates

logger = get_logger()

class BranchStrategyGenerator:
    """
    Genera sugerencias de branches de Git para implementaciones de funcionalidades.
    """
    def __init__(self):
        """Inicializa el generador de estrategias de branches."""
        # Carga las plantillas de branches
        self.templates = {
            'default': branch_templates.DEFAULT_TEMPLATE,
            'feature': branch_templates.FEATURE_BRANCH_TEMPLATE,
            'bugfix': branch_templates.BUGFIX_BRANCH_TEMPLATE,
            'hotfix': branch_templates.HOTFIX_BRANCH_TEMPLATE,
            'refactor': branch_templates.REFACTOR_BRANCH_TEMPLATE,
        }
        
        # Prefijos válidos para branches según el tipo
        self.branch_prefixes = {
            'feature': 'feature/',
            'bugfix': 'bugfix/',
            'hotfix': 'hotfix/',
            'refactor': 'refactor/',
            'docs': 'docs/',
            'test': 'test/'
        }
    
    def _normalize_name(self, name: str) -> str:
        """
        Normaliza un nombre para usarlo en un branch de git.
        
        Args:
            name: Nombre a normalizar
            
        Returns:
            Nombre normalizado compatible con convenciones de git
        """
        # Convertir a minúsculas
        name = name.lower()
        
        # Reemplazar espacios y caracteres especiales por guiones
        name = re.sub(r'[^a-z0-9]+', '-', name)
        
        # Eliminar guiones al principio y final
        name = name.strip('-')
        
        # Asegurarse de que no haya guiones dobles
        name = re.sub(r'-+', '-', name)
        
        return name
    
    def generate_branch_name(self, functionality: str, branch_type: str = 'feature') -> str:
        """
        Genera un nombre de branch siguiendo convenciones.
        
        Args:
            functionality: Nombre de la funcionalidad
            branch_type: Tipo de branch (feature, bugfix, hotfix, refactor)
            
        Returns:
            Nombre de branch normalizado
        """
        # Verificar tipo de branch y usar prefijo correspondiente
        prefix = self.branch_prefixes.get(branch_type, 'feature/')
        
        # Normalizar nombre de la funcionalidad
        normalized_name = self._normalize_name(functionality)
        
        # Generar nombre completo
        return f"{prefix}{normalized_name}"
    
    def _detect_dependencies(self, proposal_data: Dict[str, Any]) -> List[str]:
        """
        Detecta posibles dependencias entre funcionalidades basado en propuestas.
        
        Args:
            proposal_data: Datos de la propuesta de implementación
            
        Returns:
            Lista de posibles dependencias
        """
        dependencies = []
        
        # Si hay referencias a otras funcionalidades en la propuesta
        description = proposal_data.get('description', '')
        files = proposal_data.get('files_section', '')
        
        # Buscar patrones que indiquen dependencias
        common_dependencies = [
            'auth', 'authentication', 'database', 'db', 'api', 
            'core', 'config', 'settings', 'model', 'user'
        ]
        
        for dep in common_dependencies:
            # Si la dependencia aparece pero no es la funcionalidad principal
            if (dep in description.lower() or dep in files.lower()) and dep not in proposal_data.get('name', '').lower():
                dependencies.append(dep)
        
        return dependencies
    
    def generate_branch_strategy(self, functionality: str, proposal_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Genera una estrategia completa de branches para implementar una funcionalidad.
        
        Args:
            functionality: Nombre de la funcionalidad
            proposal_data: Datos de la propuesta de implementación (opcional)
            
        Returns:
            Diccionario con la estrategia de branches
        """
        # Determinar tipo de branch según contexto
        if proposal_data:
            # Analizar descripción para determinar tipo
            description = proposal_data.get('description', '').lower()
            
            # Detectar si es un fix o corrección
            if 'bug' in description or 'fix' in description or 'issue' in description:
                branch_type = 'bugfix'
            # Detectar si es una mejora de código existente
            elif 'refactor' in description or 'improve' in description or 'optimize' in description:
                branch_type = 'refactor'
            # Por defecto, asumir que es una feature
            else:
                branch_type = 'feature'
        else:
            # Sin contexto, asumir que es una feature
            branch_type = 'feature'
            proposal_data = {
                'name': functionality,
                'description': f"Implementación de {functionality}",
                'files_section': ''
            }
        
        # Generar nombre del branch principal
        main_branch = self.generate_branch_name(functionality, branch_type)
        
        # Detectar dependencias
        dependencies = self._detect_dependencies(proposal_data)
        
        # Preparar estructura modular de cambios
        modular_structure = []
        
        # Dividir la implementación en módulos si hay suficiente información
        files_section = proposal_data.get('files_section', '')
        if isinstance(files_section, str) and '\n' in files_section:
            # Dividir por líneas y agrupar archivos relacionados
            files = [f.strip() for f in files_section.split('\n') if f.strip()]
            
            # Agrupar por tipo/directorio
            file_groups = {}
            for file in files:
                if '/' in file:
                    directory = file.split('/')[0]
                    if directory not in file_groups:
                        file_groups[directory] = []
                    file_groups[directory].append(file)
                else:
                    if 'root' not in file_groups:
                        file_groups['root'] = []
                    file_groups['root'].append(file)
            
            # Crear branches para cada grupo significativo
            for group, group_files in file_groups.items():
                if len(group_files) > 1:  # Solo crear subbranch si hay múltiples archivos
                    sub_branch = self.generate_branch_name(f"{functionality}-{group}", branch_type)
                    modular_structure.append({
                        'branch': sub_branch,
                        'component': group,
                        'files': group_files,
                        'description': f"Componente {group} para {functionality}"
                    })
        
        # Si no se logró crear una estructura modular pero hay dependencias
        # sugerir una estructura basada en dependencias
        if not modular_structure and dependencies:
            modular_structure.append({
                'branch': self.generate_branch_name(f"{functionality}-core", branch_type),
                'component': 'core',
                'description': f"Componentes principales para {functionality}"
            })
            
            for dep in dependencies:
                modular_structure.append({
                    'branch': self.generate_branch_name(f"{functionality}-{dep}-integration", branch_type),
                    'component': f"{dep}-integration",
                    'description': f"Integración con {dep} para {functionality}",
                    'depends_on': [f"{functionality}-core"]
                })
        
        # Seleccionar la plantilla adecuada
        template_type = branch_type if branch_type in self.templates else 'default'
        template = self.templates[template_type]

        # Construir estrategia completa
        strategy = {
            'main_branch': main_branch,
            'type': branch_type,
            'name': functionality,
            'description': proposal_data.get('description', f"Implementación de {functionality}"),
            'dependencies': dependencies,
            'modular_structure': modular_structure,
            'workflow': template,
        }
        
        return strategy
    
    def format_branch_strategy_markdown(self, strategy: Dict[str, Any]) -> str:
        """
        Formatea la estrategia de branches en Markdown para su visualización o documentación.
        
        Args:
            strategy: Estrategia de branches generada
            
        Returns:
            Texto en formato Markdown con la estrategia
        """
        markdown = f"# Estrategia de Branches para {strategy['name']}\n\n"
        
        markdown += f"## Branch Principal\n\n"
        markdown += f"```\n{strategy['main_branch']}\n```\n\n"
        
        markdown += f"## Descripción\n\n"
        markdown += f"{strategy['description']}\n\n"
        
        # Agregar dependencias si existen
        if strategy['dependencies']:
            markdown += f"## Dependencias Identificadas\n\n"
            for dep in strategy['dependencies']:
                markdown += f"- {dep.capitalize()}\n"
            markdown += "\n"
        
        # Agregar estructura modular si existe
        if strategy['modular_structure']:
            markdown += f"## Estructura Modular Sugerida\n\n"
            markdown += "Se recomienda dividir la implementación en los siguientes branches:\n\n"
            
            for module in strategy['modular_structure']:
                markdown += f"### Branch: `{module['branch']}`\n\n"
                markdown += f"**Componente:** {module['component']}\n\n"
                markdown += f"**Descripción:** {module['description']}\n\n"
                
                if 'files' in module and module['files']:
                    markdown += "**Archivos:**\n\n"
                    for file in module['files']:
                        markdown += f"- `{file}`\n"
                    markdown += "\n"
                
                if 'depends_on' in module:
                    markdown += "**Depende de:**\n\n"
                    for dep in module['depends_on']:
                        markdown += f"- `{dep}`\n"
                    markdown += "\n"
        
        # Agregar workflow de Git recomendado
        markdown += f"## Workflow de Trabajo Recomendado\n\n"
        markdown += f"{strategy['workflow']}\n\n"
        
        # Agregar convenciones de commits sugeridas
        markdown += f"## Convenciones de Commits Sugeridas\n\n"
        markdown += "```\n"
        markdown += "<tipo>(<alcance>): <descripción corta>\n\n"
        markdown += "<cuerpo opcional>\n\n"
        markdown += "<pie opcional>\n"
        markdown += "```\n\n"
        markdown += "**Tipos comunes:**\n\n"
        markdown += "- `feat`: Nueva característica\n"
        markdown += "- `fix`: Corrección de errores\n"
        markdown += "- `docs`: Documentación\n"
        markdown += "- `style`: Cambios de formato (no afectan código)\n"
        markdown += "- `refactor`: Refactorización de código\n"
        markdown += "- `test`: Añadir o corregir tests\n"
        markdown += "- `chore`: Tareas de mantenimiento\n"
        
        return markdown


def get_branch_strategy_generator() -> BranchStrategyGenerator:
    """
    Crea y devuelve una instancia del generador de estrategias de branches.
    
    Returns:
        Una instancia de BranchStrategyGenerator
    """
    return BranchStrategyGenerator()
