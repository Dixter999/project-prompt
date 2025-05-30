#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comando CLI para seguimiento de progreso de sugerencias de mejora.

Este módulo implementa el comando 'pp track-progress' que permite
hacer seguimiento del progreso de implementación de las sugerencias
generadas para grupos funcionales.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from src.utils.logger import get_logger
from src.utils.config import ConfigManager
from src.ui.cli import CLI

# Configurar logger
logger = get_logger()


class TrackProgressCommand:
    """Comando para seguimiento de progreso de sugerencias."""
    
    def __init__(self, config: Optional[ConfigManager] = None):
        """
        Inicializar comando de seguimiento de progreso.
        
        Args:
            config: Configuración opcional
        """
        self.config = config or ConfigManager()
        self.cli = CLI()
        self.base_output_dir = Path("project-output")
        self.suggestions_dir = self.base_output_dir / "suggestions"
    
    def execute(self, group_name: Optional[str] = None, project_path: Optional[str] = None, phase: Optional[int] = None) -> bool:
        """
        Ejecutar seguimiento de progreso.
        
        Args:
            group_name: Nombre del grupo funcional para rastrear
            project_path: Ruta al proyecto (usa directorio actual si no se especifica)
            phase: Número de fase específica a rastrear (opcional)
            
        Returns:
            True si el seguimiento fue exitoso
        """
        try:
            project_path = project_path or "."
            project_path = os.path.abspath(project_path)
            
            self.cli.print_header("📊 Seguimiento de Progreso de Sugerencias")
            self.cli.print_info(f"📂 Proyecto: {project_path}")
            
            if not os.path.exists(project_path):
                self.cli.print_error(f"❌ El directorio del proyecto no existe: {project_path}")
                return False
            
            # Cambiar al directorio del proyecto
            original_dir = os.getcwd()
            os.chdir(project_path)
            
            try:
                if group_name:
                    # Rastrear progreso de un grupo específico
                    if phase:
                        return self._track_specific_phase(group_name, phase)
                    else:
                        return self._track_specific_group(group_name)
                else:
                    # Mostrar resumen de todos los grupos
                    return self._show_progress_summary()
                    
            finally:
                os.chdir(original_dir)
                
        except KeyboardInterrupt:
            self.cli.print_warning("\n⚠️  Seguimiento interrumpido por el usuario")
            return False
        except Exception as e:
            logger.error(f"Error en comando track-progress: {e}")
            self.cli.print_error(f"❌ Error inesperado: {str(e)}")
            return False
    
    def _track_specific_group(self, group_name: str) -> bool:
        """
        Rastrear progreso de un grupo específico.
        
        Args:
            group_name: Nombre del grupo funcional
            
        Returns:
            True si el seguimiento fue exitoso
        """
        try:
            # Buscar directorio de sugerencias para el grupo
            group_suggestions_dir = self._find_group_suggestions_dir(group_name)
            
            if not group_suggestions_dir:
                self.cli.print_warning(f"⚠️  No se encontraron sugerencias para el grupo: {group_name}")
                self.cli.print_info("💡 Ejecute primero 'pp generate-suggestions' para generar sugerencias")
                return False
            
            # Buscar archivo de progreso general
            progress_file = group_suggestions_dir / "progress.md"
            
            if not progress_file.exists():
                self.cli.print_warning(f"⚠️  No se encontró archivo de progreso para el grupo: {group_name}")
                self.cli.print_info("💡 Ejecute primero 'pp generate-suggestions' para generar sugerencias")
                return False
            
            # Leer progreso actual
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress_content = f.read()
            
            # Mostrar progreso detallado
            self._display_detailed_progress_markdown(group_name, progress_content, group_suggestions_dir)
            
            # Permitir actualización interactiva
            return self._interactive_progress_update_markdown(group_name, group_suggestions_dir)
            
        except Exception as e:
            logger.error(f"Error al rastrear grupo {group_name}: {e}")
            self.cli.print_error(f"❌ Error al rastrear progreso del grupo: {str(e)}")
            return False
    
    def _track_specific_phase(self, group_name: str, phase_number: int) -> bool:
        """
        Rastrear progreso de una fase específica.
        
        Args:
            group_name: Nombre del grupo funcional
            phase_number: Número de la fase a rastrear
            
        Returns:
            True si el seguimiento fue exitoso
        """
        try:
            # Buscar directorio de sugerencias para el grupo
            group_suggestions_dir = self._find_group_suggestions_dir(group_name)
            
            if not group_suggestions_dir:
                self.cli.print_warning(f"⚠️  No se encontraron sugerencias para el grupo: {group_name}")
                self.cli.print_info("💡 Ejecute primero 'pp generate-suggestions' para generar sugerencias")
                return False
            
            # Buscar archivo de fase específica
            phase_file = group_suggestions_dir / f"phase{phase_number}.md"
            
            if not phase_file.exists():
                self.cli.print_warning(f"⚠️  No se encontró la fase {phase_number} para el grupo: {group_name}")
                available_phases = [f.name for f in group_suggestions_dir.glob("phase*.md")]
                if available_phases:
                    self.cli.print_info(f"📋 Fases disponibles: {', '.join(available_phases)}")
                return False
            
            # Leer contenido de la fase
            with open(phase_file, 'r', encoding='utf-8') as f:
                phase_content = f.read()
            
            # Buscar archivo de progreso específico de la fase
            phase_progress_file = group_suggestions_dir / f"phase_{phase_number}_progress.md"
            
            # Mostrar información de la fase
            self._display_phase_details(group_name, phase_number, phase_content)
            
            # Crear o actualizar archivo de progreso de fase si no existe
            if not phase_progress_file.exists():
                self._create_phase_progress_file(phase_progress_file, phase_number, phase_content, group_name)
            
            # Permitir actualización interactiva del progreso de fase
            return self._interactive_phase_progress_update(group_name, phase_number, phase_progress_file)
            
        except Exception as e:
            logger.error(f"Error al rastrear fase {phase_number} del grupo {group_name}: {e}")
            self.cli.print_error(f"❌ Error al rastrear progreso de la fase: {str(e)}")
            return False
    
    def _show_progress_summary(self) -> bool:
        """
        Mostrar resumen de progreso de todos los grupos.
        
        Returns:
            True si se mostró el resumen exitosamente
        """
        try:
            if not self.suggestions_dir.exists():
                self.cli.print_warning("⚠️  No se encontraron sugerencias en este proyecto")
                self.cli.print_info("💡 Ejecute 'pp analyze-group' y 'pp generate-suggestions' primero")
                return False
            
            # Buscar todos los directorios de sugerencias
            suggestion_dirs = [d for d in self.suggestions_dir.iterdir() 
                             if d.is_dir() and d.name.startswith('suggestions_')]
            
            if not suggestion_dirs:
                self.cli.print_warning("⚠️  No se encontraron directorios de sugerencias")
                return False
            
            self.cli.print_info("📊 Resumen de Progreso por Grupos")
            
            total_groups = len(suggestion_dirs)
            groups_with_progress = 0
            total_phases = 0
            completed_phases = 0
            
            for suggestion_dir in suggestion_dirs:
                group_name = suggestion_dir.name.replace('suggestions_', '')
                self.cli.print_info(f"🔍 Grupo: {group_name}")
                
                # Buscar archivo de progreso
                progress_file = suggestion_dir / "progress.md"
                if progress_file.exists():
                    groups_with_progress += 1
                    
                    # Contar fases y progreso
                    phase_files = list(suggestion_dir.glob("phase*.md"))
                    total_phases += len(phase_files)
                    
                    # Leer progreso
                    with open(progress_file, 'r', encoding='utf-8') as f:
                        progress_content = f.read()
                    
                    # Contar fases completadas (buscar ✅ en el contenido)
                    completed_in_group = progress_content.count('✅')
                    completed_phases += completed_in_group
                    
                    self.cli.print_info(f"  📋 Fases: {len(phase_files)}")
                    self.cli.print_info(f"  ✅ Completadas: {completed_in_group}")
                    self.cli.print_info(f"  ⏳ Progreso: {completed_in_group}/{len(phase_files)} ({(completed_in_group/len(phase_files)*100):.1f}%)")
                else:
                    self.cli.print_warning(f"  ⚠️  Sin archivo de progreso")
                
                self.cli.print_info("")
            
            # Mostrar resumen general
            self.cli.print_info("📈 Resumen General del Proyecto")
            self.cli.print_info(f"📁 Grupos funcionales: {total_groups}")
            self.cli.print_info(f"📊 Grupos con progreso: {groups_with_progress}")
            self.cli.print_info(f"📋 Total de fases: {total_phases}")
            self.cli.print_info(f"✅ Fases completadas: {completed_phases}")
            if total_phases > 0:
                overall_progress = (completed_phases / total_phases) * 100
                self.cli.print_info(f"🎯 Progreso general: {overall_progress:.1f}%")
            
            return True
            
        except Exception as e:
            logger.error(f"Error al mostrar resumen de progreso: {e}")
            self.cli.print_error(f"❌ Error al mostrar resumen: {str(e)}")
            return False
    
    def _find_group_suggestions_dir(self, group_name: str) -> Optional[Path]:
        """
        Buscar directorio de sugerencias para un grupo.
        
        Args:
            group_name: Nombre del grupo funcional
            
        Returns:
            Path al directorio de sugerencias o None si no se encuentra
        """
        if not self.suggestions_dir.exists():
            return None
        
        # Buscar directorios que contengan el nombre del grupo
        possible_dirs = [
            self.suggestions_dir / f"suggestions_{group_name}",
            self.suggestions_dir / group_name
        ]
        
        # Buscar también directorios que contengan el grupo en el nombre
        for dir_path in self.suggestions_dir.iterdir():
            if dir_path.is_dir() and group_name.lower() in dir_path.name.lower():
                possible_dirs.append(dir_path)
        
        # Retornar el primer directorio que exista
        for dir_path in possible_dirs:
            if dir_path.exists() and dir_path.is_dir():
                return dir_path
        
        return None
    
    def _display_detailed_progress_markdown(self, group_name: str, progress_content: str, group_dir: Path):
        """
        Mostrar progreso detallado de un grupo basado en markdown.
        
        Args:
            group_name: Nombre del grupo
            progress_content: Contenido del archivo progress.md
            group_dir: Directorio del grupo
        """
        self.cli.print_info(f"📋 Progreso Detallado: {group_name}")
        
        # Mostrar contenido del archivo de progreso
        lines = progress_content.split('\n')
        for line in lines:
            if line.strip():
                if line.startswith('#'):
                    self.cli.print_info(line)
                elif '|' in line and ('✅' in line or '⏳' in line):
                    self.cli.print_info(f"   {line}")
        
        self.cli.print_info("")
    
    def _interactive_progress_update_markdown(self, group_name: str, group_dir: Path) -> bool:
        """
        Permitir actualización interactiva del progreso usando markdown.
        
        Args:
            group_name: Nombre del grupo
            group_dir: Directorio del grupo
            
        Returns:
            True si se actualizó el progreso
        """
        try:
            self.cli.print_info("🔄 ¿Desea actualizar el progreso de alguna fase? (s/N)")
            response = input().strip().lower()
            
            if response not in ['s', 'sí', 'si', 'y', 'yes']:
                return True
            
            # Buscar archivos de fase
            phase_files = sorted(group_dir.glob("phase*.md"))
            if not phase_files:
                self.cli.print_warning("⚠️  No se encontraron archivos de fase")
                return False
            
            # Mostrar fases disponibles
            self.cli.print_info("📋 Fases disponibles:")
            for i, phase_file in enumerate(phase_files, 1):
                phase_name = phase_file.stem
                self.cli.print_info(f"  {i}. {phase_name}")
            
            # Seleccionar fase
            self.cli.print_info("Seleccione el número de fase a actualizar:")
            try:
                selection = int(input().strip())
                if 1 <= selection <= len(phase_files):
                    selected_phase = phase_files[selection - 1]
                    phase_number = int(selected_phase.stem.replace('phase', ''))
                    return self._interactive_phase_progress_update(group_name, phase_number, 
                                                                 group_dir / f"phase_{phase_number}_progress.md")
                else:
                    self.cli.print_warning("⚠️  Selección inválida")
                    return False
            except ValueError:
                self.cli.print_warning("⚠️  Entrada inválida")
                return False
                
        except Exception as e:
            logger.error(f"Error en actualización interactiva: {e}")
            self.cli.print_error(f"❌ Error: {str(e)}")
            return False
    
    def _display_phase_details(self, group_name: str, phase_number: int, phase_content: str):
        """
        Mostrar detalles de una fase específica.
        
        Args:
            group_name: Nombre del grupo
            phase_number: Número de la fase
            phase_content: Contenido del archivo de fase
        """
        self.cli.print_info(f"📋 Fase {phase_number} - {group_name}")
        
        # Extraer título de la fase del contenido
        lines = phase_content.split('\n')
        for line in lines[:10]:  # Buscar en las primeras 10 líneas
            if line.startswith('# '):
                self.cli.print_info(f"📌 {line[2:].strip()}")
                break
        
        # Buscar Implementation Prompts en el contenido
        implementation_prompts = []
        in_implementation_section = False
        
        for line in lines:
            if '## Implementation Prompt' in line:
                in_implementation_section = True
                continue
            elif line.startswith('## ') and in_implementation_section:
                in_implementation_section = False
            elif in_implementation_section and line.strip():
                implementation_prompts.append(line.strip())
        
        if implementation_prompts:
            self.cli.print_info(f"🎯 Implementation Prompts encontrados: {len(implementation_prompts)}")
        
        self.cli.print_info("")
    
    def _create_phase_progress_file(self, progress_file: Path, phase_number: int, phase_content: str, group_name: str):
        """
        Crear archivo de progreso para una fase específica.
        
        Args:
            progress_file: Ruta al archivo de progreso
            phase_number: Número de la fase
            phase_content: Contenido de la fase
            group_name: Nombre del grupo
        """
        try:
            # Extraer Implementation Prompts del contenido de la fase
            lines = phase_content.split('\n')
            implementation_prompts = []
            current_prompt = []
            in_implementation_section = False
            
            for line in lines:
                if '## Implementation Prompt' in line:
                    if current_prompt:
                        implementation_prompts.append('\n'.join(current_prompt))
                        current_prompt = []
                    in_implementation_section = True
                    current_prompt.append(line)
                elif line.startswith('## ') and in_implementation_section:
                    if current_prompt:
                        implementation_prompts.append('\n'.join(current_prompt))
                        current_prompt = []
                    in_implementation_section = False
                elif in_implementation_section:
                    current_prompt.append(line)
            
            # Agregar el último prompt si existe
            if current_prompt:
                implementation_prompts.append('\n'.join(current_prompt))
            
            # Crear contenido del archivo de progreso
            progress_content = f"""# Progreso - Fase {phase_number} - {group_name}

**Fecha de creación:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Estado:** ⏳ En progreso

## Tabla de Progreso

| Task | Estado | Fecha | Notas |
|------|--------|-------|-------|
"""
            
            # Agregar tareas basadas en los Implementation Prompts
            for i, prompt in enumerate(implementation_prompts, 1):
                # Extraer título del prompt
                prompt_lines = prompt.split('\n')
                title = f"Implementation Prompt {i}"
                for line in prompt_lines:
                    if line.startswith('## '):
                        title = line[3:].strip()
                        break
                
                progress_content += f"| {title} | ⏳ Pendiente | - | - |\n"
            
            # Si no hay implementation prompts, agregar tareas genéricas
            if not implementation_prompts:
                progress_content += "| Análisis de requisitos | ⏳ Pendiente | - | - |\n"
                progress_content += "| Implementación | ⏳ Pendiente | - | - |\n"
                progress_content += "| Testing | ⏳ Pendiente | - | - |\n"
                progress_content += "| Documentación | ⏳ Pendiente | - | - |\n"
            
            progress_content += f"""

## Historial de Cambios

**{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:** Archivo de progreso creado para Fase {phase_number}

## Notas

- Use ✅ para marcar tareas completadas
- Use ⏳ para tareas en progreso
- Use ❌ para tareas con problemas
- Agregue fechas y notas según sea necesario
"""
            
            # Escribir archivo
            progress_file.parent.mkdir(parents=True, exist_ok=True)
            with open(progress_file, 'w', encoding='utf-8') as f:
                f.write(progress_content)
            
            self.cli.print_success(f"✅ Archivo de progreso creado: {progress_file.name}")
            
        except Exception as e:
            logger.error(f"Error al crear archivo de progreso: {e}")
            self.cli.print_error(f"❌ Error al crear archivo de progreso: {str(e)}")
    
    def _interactive_phase_progress_update(self, group_name: str, phase_number: int, progress_file: Path) -> bool:
        """
        Actualización interactiva del progreso de una fase específica.
        
        Args:
            group_name: Nombre del grupo
            phase_number: Número de la fase
            progress_file: Archivo de progreso de la fase
            
        Returns:
            True si se actualizó exitosamente
        """
        try:
            # Crear archivo si no existe
            if not progress_file.exists():
                self.cli.print_info(f"📝 Creando archivo de progreso para Fase {phase_number}...")
                # Necesitamos el contenido de la fase para crear el progreso
                phase_file = progress_file.parent / f"phase{phase_number}.md"
                if phase_file.exists():
                    with open(phase_file, 'r', encoding='utf-8') as f:
                        phase_content = f.read()
                    self._create_phase_progress_file(progress_file, phase_number, phase_content, group_name)
                else:
                    self.cli.print_error(f"❌ No se encontró archivo de fase: phase{phase_number}.md")
                    return False
            
            # Leer progreso actual
            with open(progress_file, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            # Mostrar progreso actual
            self.cli.print_subheader(f"📊 Progreso Actual - Fase {phase_number}")
            self._display_progress_table(current_content)
            
            self.cli.print_info(f"\n✅ Progreso de Fase {phase_number} mostrado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error en actualización interactiva de fase: {e}")
            self.cli.print_error(f"❌ Error: {str(e)}")
            return False
    
    def _display_progress_table(self, content: str):
        """
        Mostrar tabla de progreso de manera formateada.
        
        Args:
            content: Contenido del archivo de progreso
        """
        lines = content.split('\n')
        in_table = False
        
        for line in lines:
            if line.startswith('| Task'):
                in_table = True
                self.cli.print_info(line)
            elif line.startswith('|---'):
                self.cli.print_info(line)
            elif in_table and line.startswith('|'):
                self.cli.print_info(line)
            elif in_table and not line.startswith('|'):
                break


def get_track_progress_command() -> TrackProgressCommand:
    """
    Factory function para obtener instancia del comando.
    
    Returns:
        Instancia de TrackProgressCommand
    """
    return TrackProgressCommand()