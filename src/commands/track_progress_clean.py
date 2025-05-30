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
            
            self.cli.print_success(f"📋 Resumen de progreso ({len(suggestion_dirs)} grupos)")
            self.cli.print_separator()
            
            total_phases = 0
            total_completed = 0
            
            for suggestion_dir in sorted(suggestion_dirs):
                group_name = suggestion_dir.name.replace('suggestions_', '')
                progress_file = suggestion_dir / "progress.json"
                
                if not progress_file.exists():
                    continue
                
                with open(progress_file, 'r', encoding='utf-8') as f:
                    progress_data = json.load(f)
                
                # Calcular estadísticas
                phases = progress_data.get('phases', {})
                completed_phases = sum(1 for phase in phases.values() 
                                     if phase.get('status') == 'completed')
                total_phases_group = len(phases)
                
                total_phases += total_phases_group
                total_completed += completed_phases
                
                # Calcular porcentaje
                if total_phases_group > 0:
                    percentage = (completed_phases / total_phases_group) * 100
                else:
                    percentage = 0
                
                # Mostrar progreso del grupo
                progress_bar = self._create_progress_bar(percentage)
                status_emoji = "✅" if percentage == 100 else "🔄" if percentage > 0 else "⏳"
                
                self.cli.print_info(f"{status_emoji} **{group_name}**")
                self.cli.print_info(f"   {progress_bar} {percentage:.1f}% ({completed_phases}/{total_phases_group} fases)")
                
                # Mostrar última actualización
                last_updated = progress_data.get('last_updated', 'Nunca')
                self.cli.print_info(f"   📅 Última actualización: {last_updated}")
                self.cli.print_info("")
            
            # Mostrar estadísticas totales
            if total_phases > 0:
                overall_percentage = (total_completed / total_phases) * 100
                overall_progress_bar = self._create_progress_bar(overall_percentage)
                
                self.cli.print_separator()
                self.cli.print_success("📊 **Progreso General del Proyecto**")
                self.cli.print_info(f"   {overall_progress_bar} {overall_percentage:.1f}%")
                self.cli.print_info(f"   📈 {total_completed}/{total_phases} fases completadas")
            
            return True
            
        except Exception as e:
            logger.error(f"Error al mostrar resumen: {e}")
            self.cli.print_error(f"❌ Error al mostrar resumen de progreso: {str(e)}")
            return False
    
    def _find_group_suggestions_dir(self, group_name: str) -> Optional[Path]:
        """
        Buscar directorio de sugerencias para un grupo.
        
        Args:
            group_name: Nombre del grupo funcional
            
        Returns:
            Path al directorio de sugerencias o None si no existe
        """
        if not self.suggestions_dir.exists():
            return None
        
        # Buscar directorio que coincida con el nombre del grupo
        possible_names = [
            f"suggestions_{group_name}",
            f"suggestions_{group_name.replace(' ', '_')}",
            f"suggestions_{group_name.replace(':', '_')}"
        ]
        
        for name in possible_names:
            candidate_dir = self.suggestions_dir / name
            if candidate_dir.exists() and candidate_dir.is_dir():
                return candidate_dir
        
        return None
    
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
            return self._interactive_phase_progress_update(group_name, phase_number, phase_progress_file, phase_content)
            
        except Exception as e:
            logger.error(f"Error al rastrear fase {phase_number} del grupo {group_name}: {e}")
            self.cli.print_error(f"❌ Error al rastrear progreso de la fase: {str(e)}")
            return False
    
    def _display_phase_details(self, group_name: str, phase_number: int, phase_content: str) -> None:
        """
        Mostrar detalles de una fase específica.
        
        Args:
            group_name: Nombre del grupo funcional
            phase_number: Número de la fase
            phase_content: Contenido de la fase (markdown)
        """
        self.cli.print_success(f"📄 Detalles de la Fase {phase_number} - {group_name}")
        self.cli.print_separator()
        
        # Extraer título de la fase
        lines = phase_content.split('\n')
        title = "Sin título"
        for line in lines:
            if line.startswith('# '):
                title = line.replace('# ', '').strip()
                break
        
        self.cli.print_info(f"📋 **Título:** {title}")
        
        # Extraer y mostrar tareas
        tasks = []
        in_task_section = False
        for line in lines:
            if "## Tareas" in line or "## Tasks" in line:
                in_task_section = True
                continue
            elif line.startswith('## ') and in_task_section:
                break
            elif in_task_section and line.strip().startswith('- '):
                task = line.strip().replace('- ', '')
                tasks.append(task)
        
        if tasks:
            self.cli.print_info(f"📝 **Tareas ({len(tasks)} encontradas):**")
            for i, task in enumerate(tasks, 1):
                self.cli.print_info(f"   {i}. {task}")
        else:
            self.cli.print_info("📝 **Tareas:** No se encontraron tareas específicas")
        
        # Extraer Implementation Prompt si existe
        if "## Implementation Prompt" in phase_content:
            self.cli.print_info("🚀 **Implementation Prompt:** Disponible en el archivo")
        
        self.cli.print_info("")
    
    def _create_phase_progress_file(self, progress_file: Path, phase_number: int, 
                                   phase_content: str, group_name: str) -> None:
        """
        Crear archivo de progreso para una fase específica.
        
        Args:
            progress_file: Ruta al archivo de progreso
            phase_number: Número de la fase
            phase_content: Contenido de la fase (markdown)
            group_name: Nombre del grupo funcional
        """
        try:
            # Extraer información de la fase
            lines = phase_content.split('\n')
            phase_title = "Sin título"
            tasks = []
            
            # Extraer título
            for line in lines:
                if line.startswith('# '):
                    phase_title = line.replace('# ', '').strip()
                    break
            
            # Extraer tareas
            in_task_section = False
            for line in lines:
                if "## Tareas" in line or "## Tasks" in line:
                    in_task_section = True
                    continue
                elif line.startswith('## ') and in_task_section:
                    break
                elif in_task_section and line.strip().startswith('- '):
                    task = line.strip().replace('- ', '')
                    tasks.append(task)
            
            # Crear contenido markdown del progreso
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            progress_content = f"""# Progreso de Fase {phase_number} - {group_name}

## Información General
- **Fase:** {phase_number}
- **Título:** {phase_title}
- **Grupo:** {group_name}
- **Estado:** ⏳ Pendiente
- **Creado:** {current_time}
- **Última actualización:** {current_time}

## Tareas de la Fase

| Tarea | Estado | Fecha Completada | Notas |
|-------|--------|------------------|-------|
"""
            
            # Añadir tareas extraídas
            if tasks:
                for i, task in enumerate(tasks, 1):
                    progress_content += f"| {i}. {task} | ⏳ Pendiente | - | - |\n"
            else:
                progress_content += "| Sin tareas específicas identificadas | ⏳ Pendiente | - | - |\n"
            
            progress_content += f"""
## Historial de Cambios

### {current_time}
- ✅ Archivo de progreso creado
- 📋 {len(tasks) if tasks else 0} tareas identificadas

## Notas

*No hay notas adicionales*

## Comandos Útiles

Para actualizar este progreso:
```bash
pp track-progress "{group_name}" --phase {phase_number}
```

Para ver todas las fases:
```bash
pp track-progress "{group_name}"
```
"""
            
            # Guardar archivo de progreso
            with open(progress_file, 'w', encoding='utf-8') as f:
                f.write(progress_content)
            
            self.cli.print_success(f"✅ Archivo de progreso creado para la Fase {phase_number}")
        
        except Exception as e:
            logger.error(f"Error al crear archivo de progreso para fase {phase_number}: {e}")
            self.cli.print_error(f"❌ Error al crear archivo de progreso: {str(e)}")
    
    def _interactive_phase_progress_update(self, group_name: str, phase_number: int, 
                                         progress_file: Path, phase_content: str) -> bool:
        """
        Actualización interactiva del progreso de una fase.
        
        Args:
            group_name: Nombre del grupo funcional
            phase_number: Número de la fase
            progress_file: Archivo de progreso de la fase
            phase_content: Contenido de la fase (markdown)
            
        Returns:
            True si se actualizó exitosamente
        """
        try:
            # Leer progreso actual
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress_content = f.read()
            
            self.cli.print_info("💡 Opciones disponibles:")
            self.cli.print_info("   1. Marcar fase como completada")
            self.cli.print_info("   2. Cambiar estado de fase")
            self.cli.print_info("   3. Marcar tarea como completada")
            self.cli.print_info("   4. Añadir nota")
            self.cli.print_info("   5. Ver progreso actual")
            self.cli.print_info("   6. Salir")
            
            choice = input("\n🔢 Seleccione una opción (1-6): ").strip()
            
            if choice == "1":
                return self._mark_phase_completed_markdown(progress_file, phase_number)
            elif choice == "2":
                return self._change_phase_status_markdown(progress_file, phase_number)
            elif choice == "3":
                return self._mark_task_completed_markdown(progress_file, phase_number)
            elif choice == "4":
                return self._add_note_markdown(progress_file, phase_number)
            elif choice == "5":
                self._show_current_progress_markdown(progress_content)
                return True
            elif choice == "6":
                self.cli.print_info("👋 Saliendo del seguimiento")
                return True
            else:
                self.cli.print_warning("⚠️  Opción no válida")
                return False
                
        except Exception as e:
            logger.error(f"Error en actualización interactiva de fase: {e}")
            self.cli.print_error(f"❌ Error en actualización de fase: {str(e)}")
            return False
    
    def _create_progress_bar(self, percentage: float, width: int = 20) -> str:
        """
        Crear barra de progreso visual.
        
        Args:
            percentage: Porcentaje de progreso (0-100)
            width: Ancho de la barra
            
        Returns:
            String con barra de progreso
        """
        filled = int((percentage / 100) * width)
        bar = "▓" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    def _display_detailed_progress_markdown(self, group_name: str, progress_content: str, 
                                          suggestions_dir: Path) -> None:
        """
        Mostrar progreso detallado desde archivo markdown.
        
        Args:
            group_name: Nombre del grupo funcional
            progress_content: Contenido del archivo progress.md
            suggestions_dir: Directorio de sugerencias
        """
        self.cli.print_success(f"📊 Progreso detallado: {group_name}")
        self.cli.print_separator()
        
        # Buscar archivos de fases disponibles
        phase_files = sorted([f for f in suggestions_dir.glob("phase*.md") 
                             if f.name.startswith('phase') and f.name.endswith('.md')])
        
        if not phase_files:
            self.cli.print_warning("⚠️  No se encontraron archivos de fases")
            return
        
        total_phases = len(phase_files)
        completed_phases = 0
        
        for phase_file in phase_files:
            # Extraer número de fase del nombre del archivo
            phase_number = phase_file.stem.replace('phase', '')
            phase_progress_file = suggestions_dir / f"phase_{phase_number}_progress.md"
            
            # Leer título de la fase
            with open(phase_file, 'r', encoding='utf-8') as f:
                phase_content = f.read()
            
            phase_title = "Sin título"
            for line in phase_content.split('\n'):
                if line.startswith('# '):
                    phase_title = line.replace('# ', '').strip()
                    break
            
            # Determinar estado de la fase
            status = "⏳ Pendiente"
            if phase_progress_file.exists():
                with open(phase_progress_file, 'r', encoding='utf-8') as f:
                    progress_content_phase = f.read()
                
                if "✅ Completada" in progress_content_phase:
                    status = "✅ Completada"
                    completed_phases += 1
                elif "🔄 En Progreso" in progress_content_phase:
                    status = "🔄 En Progreso"
            
            self.cli.print_info(f"{status.split()[0]} **Fase {phase_number}: {phase_title}** ({status.split()[1]})")
            
            # Mostrar progreso de tareas si existe archivo de progreso
            if phase_progress_file.exists():
                with open(phase_progress_file, 'r', encoding='utf-8') as f:
                    progress_content_phase = f.read()
                
                # Contar tareas completadas en la tabla
                task_lines = []
                in_table = False
                for line in progress_content_phase.split('\n'):
                    if '|-------|' in line:
                        in_table = True
                        continue
                    elif in_table and line.strip().startswith('|') and '|' in line[1:]:
                        task_lines.append(line)
                    elif in_table and not line.strip().startswith('|'):
                        break
                
                completed_tasks = sum(1 for line in task_lines if '✅' in line)
                total_tasks = len(task_lines)
                
                if total_tasks > 0:
                    self.cli.print_info(f"   📋 Tareas: {completed_tasks}/{total_tasks} completadas")
            
            self.cli.print_info("")
        
        # Mostrar resumen general
        if total_phases > 0:
            overall_percentage = (completed_phases / total_phases) * 100
            progress_bar = self._create_progress_bar(overall_percentage)
            self.cli.print_separator()
            self.cli.print_success("📈 **Progreso General**")
            self.cli.print_info(f"   {progress_bar} {overall_percentage:.1f}%")
            self.cli.print_info(f"   🎯 {completed_phases}/{total_phases} fases completadas")
    
    def _interactive_progress_update_markdown(self, group_name: str, suggestions_dir: Path) -> bool:
        """
        Actualización interactiva de progreso basada en markdown.
        
        Args:
            group_name: Nombre del grupo funcional
            suggestions_dir: Directorio de sugerencias
            
        Returns:
            True si se actualizó exitosamente
        """
        try:
            self.cli.print_info("💡 Opciones disponibles:")
            self.cli.print_info("   1. Seleccionar fase específica para actualizar")
            self.cli.print_info("   2. Ver resumen de todas las fases")
            self.cli.print_info("   3. Salir")
            
            choice = input("\n🔢 Seleccione una opción (1-3): ").strip()
            
            if choice == "1":
                return self._select_phase_for_update(group_name, suggestions_dir)
            elif choice == "2":
                # Ya se mostró el resumen, solo confirmar
                self.cli.print_info("📊 Resumen mostrado arriba")
                return True
            elif choice == "3":
                self.cli.print_info("👋 Saliendo del seguimiento")
                return True
            else:
                self.cli.print_warning("⚠️  Opción no válida")
                return False
                
        except Exception as e:
            logger.error(f"Error en actualización interactiva markdown: {e}")
            self.cli.print_error(f"❌ Error en actualización: {str(e)}")
            return False
    
    def _select_phase_for_update(self, group_name: str, suggestions_dir: Path) -> bool:
        """
        Seleccionar una fase específica para actualizar.
        
        Args:
            group_name: Nombre del grupo funcional
            suggestions_dir: Directorio de sugerencias
            
        Returns:
            True si se actualizó exitosamente
        """
        try:
            # Buscar archivos de fases disponibles
            phase_files = sorted([f for f in suggestions_dir.glob("phase*.md") 
                                 if f.name.startswith('phase') and f.name.endswith('.md')])
            
            if not phase_files:
                self.cli.print_warning("⚠️  No se encontraron archivos de fases")
                return False
            
            self.cli.print_info("📋 Fases disponibles:")
            for phase_file in phase_files:
                phase_number = phase_file.stem.replace('phase', '')
                
                # Leer título de la fase
                with open(phase_file, 'r', encoding='utf-8') as f:
                    phase_content = f.read()
                
                phase_title = "Sin título"
                for line in phase_content.split('\n'):
                    if line.startswith('# '):
                        phase_title = line.replace('# ', '').strip()
                        break
                
                self.cli.print_info(f"   {phase_number}. {phase_title}")
            
            phase_choice = input("\n🎯 Seleccione número de fase: ").strip()
            
            # Validar que la fase existe
            phase_file = suggestions_dir / f"phase{phase_choice}.md"
            if not phase_file.exists():
                self.cli.print_warning("⚠️  Fase no válida")
                return False
            
            # Leer contenido de la fase
            with open(phase_file, 'r', encoding='utf-8') as f:
                phase_content = f.read()
            
            # Crear o actualizar archivo de progreso de fase
            phase_progress_file = suggestions_dir / f"phase_{phase_choice}_progress.md"
            if not phase_progress_file.exists():
                self._create_phase_progress_file(phase_progress_file, int(phase_choice), 
                                               phase_content, group_name)
            
            # Actualizar progreso de la fase seleccionada
            return self._interactive_phase_progress_update(group_name, int(phase_choice), 
                                                         phase_progress_file, phase_content)
            
        except Exception as e:
            logger.error(f"Error al seleccionar fase: {e}")
            self.cli.print_error(f"❌ Error al seleccionar fase: {str(e)}")
            return False
    
    def _mark_phase_completed_markdown(self, progress_file: Path, phase_number: int) -> bool:
        """
        Marcar una fase como completada en archivo markdown.
        
        Args:
            progress_file: Archivo de progreso de la fase
            phase_number: Número de la fase
            
        Returns:
            True si se marcó como completada exitosamente
        """
        try:
            # Leer contenido actual
            with open(progress_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Actualizar estado a completada
            content = content.replace("**Estado:** ⏳ Pendiente", "**Estado:** ✅ Completada")
            content = content.replace("**Estado:** 🔄 En Progreso", "**Estado:** ✅ Completada")
            
            # Actualizar última actualización
            import re
            content = re.sub(r'\*\*Última actualización:\*\* .*', 
                           f"**Última actualización:** {current_time}", content)
            
            # Añadir entrada al historial
            history_section = f"""
### {current_time}
- ✅ Fase marcada como completada
- 🎉 Todos los objetivos de la fase han sido alcanzados

## Notas"""
            
            content = content.replace("## Notas", history_section)
            
            # Guardar cambios
            with open(progress_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.cli.print_success(f"✅ Fase {phase_number} marcada como completada")
            return True
            
        except Exception as e:
            logger.error(f"Error al marcar fase como completada: {e}")
            self.cli.print_error(f"❌ Error al marcar fase como completada: {str(e)}")
            return False
    
    def _change_phase_status_markdown(self, progress_file: Path, phase_number: int) -> bool:
        """
        Cambiar estado de una fase en archivo markdown.
        
        Args:
            progress_file: Archivo de progreso de la fase
            phase_number: Número de la fase
            
        Returns:
            True si se cambió el estado exitosamente
        """
        try:
            statuses = {
                '1': ('⏳ Pendiente', 'Fase marcada como pendiente'),
                '2': ('🔄 En Progreso', 'Fase marcada como en progreso'),
                '3': ('✅ Completada', 'Fase marcada como completada'),
                '4': ('🚫 Bloqueada', 'Fase marcada como bloqueada')
            }
            
            self.cli.print_info("📊 Estados disponibles:")
            for key, (status, _) in statuses.items():
                self.cli.print_info(f"   {key}. {status}")
            
            status_choice = input("\n🔄 Seleccione nuevo estado (1-4): ").strip()
            
            if status_choice not in statuses:
                self.cli.print_warning("⚠️  Estado no válido")
                return False
            
            new_status, action_text = statuses[status_choice]
            
            # Leer contenido actual
            with open(progress_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Actualizar estado
            import re
            content = re.sub(r'\*\*Estado:\*\* [^|]*', f"**Estado:** {new_status}", content)
            
            # Actualizar última actualización
            content = re.sub(r'\*\*Última actualización:\*\* .*', 
                           f"**Última actualización:** {current_time}", content)
            
            # Añadir entrada al historial
            history_section = f"""
### {current_time}
- 🔄 {action_text}

## Notas"""
            
            content = content.replace("## Notas", history_section)
            
            # Guardar cambios
            with open(progress_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.cli.print_success(f"✅ Estado de la Fase {phase_number} cambiado a: {new_status}")
            return True
            
        except Exception as e:
            logger.error(f"Error al cambiar estado de fase: {e}")
            self.cli.print_error(f"❌ Error al cambiar estado de fase: {str(e)}")
            return False
    
    def _mark_task_completed_markdown(self, progress_file: Path, phase_number: int) -> bool:
        """
        Marcar una tarea como completada en archivo markdown.
        
        Args:
            progress_file: Archivo de progreso de la fase
            phase_number: Número de la fase
            
        Returns:
            True si se marcó la tarea como completada exitosamente
        """
        try:
            # Leer contenido actual
            with open(progress_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extraer tareas de la tabla
            lines = content.split('\n')
            task_lines = []
            task_indices = []
            
            in_table = False
            for i, line in enumerate(lines):
                if '|-------|' in line:
                    in_table = True
                    continue
                elif in_table and line.strip().startswith('|') and '|' in line[1:]:
                    task_lines.append(line)
                    task_indices.append(i)
                elif in_table and not line.strip().startswith('|'):
                    break
            
            if not task_lines:
                self.cli.print_warning("⚠️  No se encontraron tareas en esta fase")
                return False
            
            # Mostrar tareas pendientes
            pending_tasks = []
            for j, line in enumerate(task_lines):
                if '⏳ Pendiente' in line:
                    # Extraer nombre de la tarea
                    parts = line.split('|')
                    if len(parts) >= 2:
                        task_name = parts[1].strip()
                        pending_tasks.append((j, task_name))
            
            if not pending_tasks:
                self.cli.print_success("🎉 ¡Todas las tareas ya están completadas!")
                return True
            
            self.cli.print_info("📋 Tareas pendientes:")
            for j, (_, task_name) in enumerate(pending_tasks, 1):
                self.cli.print_info(f"   {j}. {task_name}")
            
            task_choice = input("\n🎯 Seleccione tarea a completar (número): ").strip()
            
            try:
                task_idx = int(task_choice) - 1
                if task_idx < 0 or task_idx >= len(pending_tasks):
                    self.cli.print_warning("⚠️  Tarea no válida")
                    return False
                
                # Obtener índice real de la tarea en el archivo
                real_task_idx, task_name = pending_tasks[task_idx]
                line_idx = task_indices[real_task_idx]
                
                # Actualizar línea de la tarea
                current_time = datetime.now().strftime("%Y-%m-%d")
                old_line = lines[line_idx]
                new_line = old_line.replace('⏳ Pendiente', '✅ Completada').replace('| - |', f'| {current_time} |')
                lines[line_idx] = new_line
                
                # Actualizar última actualización
                current_time_full = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for i, line in enumerate(lines):
                    if "**Última actualización:**" in line:
                        lines[i] = f"- **Última actualización:** {current_time_full}"
                        break
                
                # Añadir entrada al historial
                history_section = f"""
### {current_time_full}
- ✅ Tarea completada: {task_name}

## Notas"""
                
                content = '\n'.join(lines)
                content = content.replace("## Notas", history_section)
                
                # Guardar cambios
                with open(progress_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.cli.print_success(f"✅ Tarea '{task_name}' marcada como completada")
                return True
                
            except ValueError:
                self.cli.print_warning("⚠️  Número de tarea no válido")
                return False
            
        except Exception as e:
            logger.error(f"Error al marcar tarea como completada: {e}")
            self.cli.print_error(f"❌ Error al marcar tarea como completada: {str(e)}")
            return False
    
    def _add_note_markdown(self, progress_file: Path, phase_number: int) -> bool:
        """
        Añadir nota al progreso en archivo markdown.
        
        Args:
            progress_file: Archivo de progreso de la fase
            phase_number: Número de la fase
            
        Returns:
            True si se añadió la nota exitosamente
        """
        try:
            note = input("\n📝 Ingrese nota: ").strip()
            
            if not note:
                self.cli.print_warning("⚠️  Nota vacía, cancelando")
                return False
            
            # Leer contenido actual
            with open(progress_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Actualizar última actualización
            import re
            content = re.sub(r'\*\*Última actualización:\*\* .*', 
                           f"**Última actualización:** {current_time}", content)
            
            # Añadir nota al final
            note_section = f"""
### {current_time}
- 📝 Nota añadida: {note}

## Notas

*{note}*

## Comandos Útiles"""
            
            content = content.replace("## Comandos Útiles", note_section)
            
            # Guardar cambios
            with open(progress_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.cli.print_success("✅ Nota añadida exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error al añadir nota: {e}")
            self.cli.print_error(f"❌ Error al añadir nota: {str(e)}")
            return False
    
    def _show_current_progress_markdown(self, progress_content: str) -> None:
        """
        Mostrar progreso actual desde contenido markdown.
        
        Args:
            progress_content: Contenido del archivo de progreso
        """
        self.cli.print_success("📊 Progreso Actual")
        self.cli.print_separator()
        
        # Mostrar contenido formateado
        lines = progress_content.split('\n')
        for line in lines:
            if line.startswith('# '):
                self.cli.print_success(line.replace('# ', ''))
            elif line.startswith('## '):
                self.cli.print_info(line.replace('## ', '📋 '))
            elif line.startswith('- **'):
                self.cli.print_info(f"   {line}")
            elif '|' in line and ('✅' in line or '⏳' in line):
                self.cli.print_info(f"   {line}")
        
        self.cli.print_info("")


def get_track_progress_command() -> TrackProgressCommand:
    """
    Factory function para obtener instancia del comando.
    
    Returns:
        Instancia de TrackProgressCommand
    """
    return TrackProgressCommand()
