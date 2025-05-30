#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comando CLI para generar sugerencias de mejora basadas en análisis de grupos.

Este módulo implementa el comando 'pp generate-suggestions' que genera
sugerencias estructuradas por fases según el análisis previo de grupos funcionales.
"""

import os
import sys
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

from src.analyzers.ai_group_analyzer import get_ai_group_analyzer
from src.utils.logger import get_logger
from src.utils.config import ConfigManager
from src.ui.cli import CLI
from src.integrations.anthropic_advanced import AdvancedAnthropicClient

# Configurar logger
logger = get_logger()


class GenerateSuggestionsCommand:
    """Comando para generar sugerencias de mejora por fases."""
    
    def __init__(self, config: Optional[ConfigManager] = None):
        """
        Inicializar comando de generación de sugerencias.
        
        Args:
            config: Configuración opcional
        """
        self.config = config or ConfigManager()
        self.cli = CLI()
        self.ai_client = AdvancedAnthropicClient(config=self.config)
        self.analyzer = get_ai_group_analyzer(self.config)
    
    def execute(self, group_name: str, project_path: Optional[str] = None, api: str = "anthropic") -> bool:
        """
        Ejecutar generación de sugerencias.
        
        Args:
            group_name: Nombre del grupo a analizar
            project_path: Ruta al proyecto
            api: API a usar (anthropic)
            
        Returns:
            True si fue exitoso
        """
        try:
            # Determinar ruta del proyecto
            if not project_path:
                project_path = os.getcwd()
            
            if not os.path.exists(project_path):
                self.cli.print_error(f"❌ Directorio no encontrado: {project_path}")
                return False
            
            # Verificar API
            if api != "anthropic":
                self.cli.print_error("❌ Solo se soporta Anthropic API por ahora")
                return False
            
            if not self.ai_client.is_configured:
                self.cli.print_error("❌ Anthropic API no está configurada")
                self.cli.print_info("💡 Configure con: project-prompt config anthropic-key")
                return False
            
            # Mostrar información inicial
            self.cli.print_header("🤖 Generación de Sugerencias de Mejora")
            self.cli.print_info(f"📁 Proyecto: {os.path.basename(project_path)}")
            self.cli.print_info(f"🎯 Grupo: {group_name}")
            self.cli.print_info(f"🔗 API: {api}")
            
            # Verificar si existe análisis previo
            analysis_file = self._find_analysis_file(project_path, group_name)
            
            if not analysis_file:
                self.cli.print_error(f"❌ No se encontró análisis previo para el grupo '{group_name}'")
                self.cli.print_info("💡 Ejecute primero: project-prompt analyze-group \"{}\"".format(group_name))
                return False
            
            # Leer análisis previo
            analysis_data = self._read_analysis_file(analysis_file)
            if not analysis_data:
                self.cli.print_error("❌ Error al leer el análisis previo")
                return False
            
            # Generar sugerencias usando IA
            self.cli.print_info("🔄 Generando sugerencias con IA...")
            suggestions = self._generate_suggestions_with_ai(analysis_data, group_name)
            
            if not suggestions:
                self.cli.print_error("❌ Error al generar sugerencias")
                return False
            
            # Crear estructura de archivos de sugerencias
            output_dir = self._create_suggestions_structure(project_path, group_name, suggestions)
            
            if output_dir:
                self.cli.print_success("✅ Sugerencias generadas exitosamente!")
                self.cli.print_info(f"📁 Archivos generados en: {output_dir}")
                self._list_generated_files(output_dir)
                return True
            else:
                self.cli.print_error("❌ Error al crear archivos de sugerencias")
                return False
        
        except KeyboardInterrupt:
            self.cli.print_warning("\n⚠️  Generación cancelada por el usuario")
            return False
        except Exception as e:
            logger.error(f"Error en generate-suggestions: {e}")
            self.cli.print_error(f"❌ Error inesperado: {str(e)}")
            return False
    
    def _find_analysis_file(self, project_path: str, group_name: str) -> Optional[str]:
        """
        Buscar archivo de análisis previo.
        
        Args:
            project_path: Ruta del proyecto
            group_name: Nombre del grupo
            
        Returns:
            Ruta al archivo de análisis o None
        """
        # Normalizar nombre del grupo para nombre de archivo (como hace el analyzer)
        safe_group_name = "".join(c for c in group_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_group_name = safe_group_name.replace(' ', '_')
        
        # Buscar en project-output/analyses/groups/
        groups_dir = os.path.join(project_path, "project-output", "analyses", "groups")
        if os.path.exists(groups_dir):
            for file in os.listdir(groups_dir):
                if file.startswith(safe_group_name) and file.endswith(".md"):
                    return os.path.join(groups_dir, file)
        
        # Buscar también en project-output/analyses/functionality_groups/
        func_groups_dir = os.path.join(project_path, "project-output", "analyses", "functionality_groups")
        if os.path.exists(func_groups_dir):
            # Buscar archivo exacto
            potential_file = os.path.join(func_groups_dir, f"{safe_group_name}.md")
            if os.path.exists(potential_file):
                return potential_file
            
            # Buscar por coincidencia parcial (para manejar casos de nombres generados automaticamente)
            for file in os.listdir(func_groups_dir):
                if safe_group_name.lower() in file.lower() and file.endswith(".md"):
                    return os.path.join(func_groups_dir, file)
        
        return None
    
    def _read_analysis_file(self, file_path: str) -> Optional[str]:
        """
        Leer contenido del archivo de análisis.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Contenido del archivo o None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error al leer análisis: {e}")
            return None
    
    def _generate_suggestions_with_ai(self, analysis_content: str, group_name: str) -> Optional[Dict[str, Any]]:
        """
        Generar sugerencias usando IA.
        
        Args:
            analysis_content: Contenido del análisis previo
            group_name: Nombre del grupo
            
        Returns:
            Diccionario con sugerencias estructuradas
        """
        prompt = f"""Basándote en el siguiente análisis detallado de un grupo funcional, genera un plan de mejoras estructurado por fases.

ANÁLISIS DEL GRUPO FUNCIONAL:
{analysis_content}

INSTRUCCIONES:
1. Analiza cada archivo y sus sugerencias de mejora específicas del análisis real
2. Agrupa las mejoras en 3 fases lógicas de implementación
3. Cada fase debe tener 1-3 tareas específicas con el formato exacto requerido

FORMATO DE SALIDA (JSON):
{{
  "phases": [
    {{
      "phase_number": 1,
      "title": "Título de la Fase",
      "description": "Descripción detallada de qué implementa esta fase",
      "tasks": [
        {{
          "task_number": "1.1",
          "task_name": "Nombre de la Funcionalidad",
          "branch": "feature/nombre-especifico-del-branch",
          "description": "Descripción detallada de qué implementa esta tarea",
          "files_to_create": [
            {{
              "path": "src/path/to/file.py",
              "purpose": "Propósito del archivo y funcionalidad principal"
            }}
          ],
          "functionalities": [
            "Descripción de funcionalidad 1",
            "Descripción de funcionalidad 2"
          ]
        }}
      ]
    }}
  ],
  "group_name": "{group_name}",
  "total_phases": 3
}}

REGLAS CRÍTICAS:
- Basa las sugerencias ÚNICAMENTE en las mejoras específicas mencionadas en el análisis
- NO generes sugerencias genéricas
- Cada task debe tener un branch único y descriptivo
- Los nombres de archivos deben ser realistas y específicos
- Las funcionalidades deben ser medibles y específicas
- Incluye siempre tests unitarios en files_to_create

Asegúrate de que cada fase sea independiente pero construya sobre las anteriores. Las mejoras deben ser específicas y basadas en el análisis real de los archivos."""

        try:
            # Use the base client's generate_text method 
            response = self.ai_client.base_client.generate_text(
                prompt=prompt,
                max_tokens=4000,
                temperature=0.3
            )
            
            if response and 'content' in response:
                content = response.get('content', '')
                # Extraer JSON del contenido
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    import json
                    suggestions_json = content[json_start:json_end]
                    return json.loads(suggestions_json)
            
            return None
        except Exception as e:
            logger.error(f"Error al generar sugerencias con IA: {e}")
            return None
    
    def _create_suggestions_structure(self, project_path: str, group_name: str, suggestions: Dict[str, Any]) -> Optional[str]:
        """
        Crear estructura de archivos de sugerencias.
        
        Args:
            project_path: Ruta del proyecto
            group_name: Nombre del grupo
            suggestions: Datos de sugerencias
            
        Returns:
            Ruta al directorio creado o None
        """
        try:
            # Crear directorio de sugerencias
            safe_group_name = group_name.replace(":", "_").replace("/", "_").replace(" ", "_")
            suggestions_dir = os.path.join(
                project_path, 
                "project-output", 
                "suggestions", 
                f"suggestions_{safe_group_name}"
            )
            os.makedirs(suggestions_dir, exist_ok=True)
            
            phases = suggestions.get('phases', [])
            
            # Crear archivo para cada fase
            for phase in phases:
                phase_file = os.path.join(suggestions_dir, f"phase{phase['phase_number']}.md")
                self._create_phase_file(phase_file, phase, group_name)
            
            # Crear archivo de progreso inicial
            progress_file = os.path.join(suggestions_dir, "progress.md")
            self._create_progress_file(progress_file, phases, group_name)
            
            return suggestions_dir
        except Exception as e:
            logger.error(f"Error al crear estructura de sugerencias: {e}")
            return None
    
    def _create_phase_file(self, file_path: str, phase: Dict[str, Any], group_name: str):
        """
        Crear archivo de fase individual.
        
        Args:
            file_path: Ruta del archivo a crear
            phase: Datos de la fase
            group_name: Nombre del grupo
        """
        content = f"# Phase {phase['phase_number']}: {phase['title']}\n\n"
        
        # Obtener tareas de la fase
        tasks = phase.get('tasks', [])
        
        if not tasks:
            # Fallback para estructura anterior
            content += f"""## {phase['phase_number']}.1 {phase['title']}

**Branch:** {phase.get('branch', 'feature/phase-' + str(phase['phase_number']))}
**Description:** {phase.get('description', 'Descripción no disponible')}

**Files to create:**
"""
            for file_info in phase.get('files_to_create', []):
                content += f"- `{file_info['path']}` - {file_info['purpose']}\n"
            
            content += "\n**Functionalities:**\n"
            for func in phase.get('functionalities', []):
                content += f"- {func}\n"
            
            # Generar Implementation Prompt específico
            group_name_sanitized = group_name.replace(":", "__").replace("/", "_").replace(" ", "_")
            implementation_prompt = self._generate_implementation_prompt(
                phase['phase_number'], 
                f"{phase['phase_number']}.1", 
                phase['title'], 
                group_name_sanitized,
                "main"
            )
            
            content += f"""
## Implementation Prompt

```
{implementation_prompt}
```
"""
        else:
            # Nueva estructura con tareas múltiples
            for task in tasks:
                task_number = task.get('task_number', f"{phase['phase_number']}.1")
                task_name = task.get('task_name', 'Sin nombre')
                branch = task.get('branch', f"feature/phase-{phase['phase_number']}-task")
                description = task.get('description', 'Descripción no disponible')
                
                content += f"""## {task_number} {task_name}

**Branch:** {branch}
**Description:** {description}

**Files to create:**
"""
                
                for file_info in task.get('files_to_create', []):
                    content += f"- `{file_info['path']}` - {file_info['purpose']}\n"
                
                content += "\n**Functionalities:**\n"
                for func in task.get('functionalities', []):
                    content += f"- {func}\n"
                
                # Generar Implementation Prompt específico para cada tarea
                group_name_sanitized = group_name.replace(":", "__").replace("/", "_").replace(" ", "_")
                
                # Determinar branch anterior (para el primer task es main, para otros es el anterior)
                if task == tasks[0]:
                    previous_branch = "main"
                else:
                    prev_task_index = tasks.index(task) - 1
                    previous_branch = tasks[prev_task_index].get('branch', 'main')
                
                implementation_prompt = self._generate_implementation_prompt(
                    phase['phase_number'], 
                    task_number, 
                    task_name, 
                    group_name_sanitized,
                    previous_branch
                )
                
                content += f"""
## Implementation Prompt

```
{implementation_prompt}
```

"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_implementation_prompt(self, phase_number: int, task_number: str, task_name: str, group_name_sanitized: str, previous_branch: str) -> str:
        """
        Generar el Implementation Prompt exacto según especificaciones.
        
        Args:
            phase_number: Número de la fase
            task_number: Número de la tarea (ej: "1.1")
            task_name: Nombre de la tarea
            group_name_sanitized: Nombre del grupo sanitizado para rutas
            previous_branch: Branch de la tarea anterior
            
        Returns:
            Implementation Prompt formateado
        """
        return f"""I am developing ProjectPrompt, an intelligent project assistant that analyzes codebases and provides contextual suggestions.

I am in **Phase {phase_number}**, task **{task_number} {task_name}** and need to implement the functionality described in `project-output/suggestions/suggestions_{group_name_sanitized}/phase{phase_number}.md`.

Please help me to:
1. Create the appropriate branch according to the instructions
2. Develop the necessary code for this specific task
3. Prepare the commit commands when the task is complete
4. Update the corresponding markdown file

The previous task was completed in branch `{previous_branch}`.

Please don't repeat the markdown instructions in your response. Focus exclusively on implementing the current task following the technical specifications from the markdown file. Mark the task as "Done" only when it's completely implemented with passing tests."""
    
    def _create_progress_file(self, file_path: str, phases: List[Dict[str, Any]], group_name: str):
        """
        Crear archivo de seguimiento de progreso.
        
        Args:
            file_path: Ruta del archivo
            phases: Lista de fases
            group_name: Nombre del grupo
        """
        content = f"""# Progress Report: {group_name}

## Task Status

"""
        
        for phase in phases:
            tasks = phase.get('tasks', [])
            
            if not tasks:
                # Estructura anterior con una sola tarea por fase
                content += f"""### {phase['phase_number']}.1 {phase['title']} ⏳
**Branch:** {phase.get('branch', 'feature/phase-' + str(phase['phase_number']))}
**Status:** Pending
**Implemented functionalities:**
"""
                for func in phase.get('functionalities', []):
                    content += f"- ⏳ {func}\n"
                content += "**Tests:** Pending implementation\n\n"
            else:
                # Nueva estructura con múltiples tareas por fase
                for task in tasks:
                    task_number = task.get('task_number', f"{phase['phase_number']}.1")
                    task_name = task.get('task_name', 'Sin nombre')
                    branch = task.get('branch', f"feature/phase-{phase['phase_number']}-task")
                    
                    content += f"""### {task_number} {task_name} ⏳
**Branch:** {branch}
**Status:** Pending
**Implemented functionalities:**
"""
                    for func in task.get('functionalities', []):
                        content += f"- ⏳ {func}\n"
                    content += "**Tests:** Pending implementation\n\n"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _list_generated_files(self, output_dir: str):
        """
        Listar archivos generados.
        
        Args:
            output_dir: Directorio de salida
        """
        try:
            files = sorted(os.listdir(output_dir))
            for file in files:
                if file.endswith('.md'):
                    self.cli.print_info(f"   📄 {file}")
        except Exception as e:
            logger.warning(f"Error al listar archivos: {e}")


def main():
    """Función principal para ejecutar desde línea de comandos."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generar sugerencias de mejora basadas en análisis de grupos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  pp generate-suggestions --group "src/analyzers" --api anthropic
  pp generate-suggestions --group "Directory: src/ui" --api anthropic
        """
    )
    
    parser.add_argument(
        '--group',
        required=True,
        help='Nombre del grupo funcional para generar sugerencias'
    )
    
    parser.add_argument(
        '--api',
        default='anthropic',
        choices=['anthropic'],
        help='API a usar para generar sugerencias'
    )
    
    parser.add_argument(
        '--project-path', '-p',
        help='Ruta al proyecto (usa directorio actual por defecto)'
    )
    
    args = parser.parse_args()
    
    # Ejecutar comando
    command = GenerateSuggestionsCommand()
    success = command.execute(args.group, args.project_path, args.api)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
