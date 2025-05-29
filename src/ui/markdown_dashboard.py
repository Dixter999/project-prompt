#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para generar dashboard de progreso del proyecto en formato Markdown.

Este módulo implementa un generador de dashboard que produce un reporte
completo en formato Markdown con todas las métricas y análisis del proyecto.
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from src.analyzers.project_progress_tracker import ProjectProgressTracker, get_project_progress_tracker
from src.utils.logger import get_logger
from src.utils.config import ConfigManager
from src.utils.subscription_manager import get_subscription_manager

# Configuración del logger
logger = get_logger()


class MarkdownDashboardGenerator:
    """
    Generador de dashboard en formato Markdown.
    
    Esta clase genera un dashboard completo en formato Markdown con métricas
    de progreso, análisis de código, estado de branches y recomendaciones.
    """
    
    def __init__(self, project_path: str, config: Optional[ConfigManager] = None):
        """
        Inicializar el generador del dashboard.
        
        Args:
            project_path: Ruta al directorio del proyecto
            config: Configuración opcional
        """
        self.project_path = os.path.abspath(project_path)
        self.config = config or ConfigManager()
        self.subscription = get_subscription_manager()
        self.tracker = get_project_progress_tracker(project_path, config)
        
        # Verificar acceso premium
        self.premium_access = self.subscription.is_premium_feature_available('project_dashboard')
    
    def generate_markdown_dashboard(self, output_path: Optional[str] = None, premium_mode: bool = False, detailed: bool = False) -> str:
        """
        Generar el dashboard completo y guardarlo como Markdown.
        
        Args:
            output_path: Ruta donde guardar el Markdown (opcional)
            premium_mode: Si está en modo premium (opcional)
            detailed: Si incluir análisis detallado (opcional)
            
        Returns:
            Ruta al archivo Markdown generado
        """
        # Determinar si usar características premium
        is_premium = self.premium_access and premium_mode
        
        # Si no tiene acceso premium o no está en modo premium, generar versión reducida
        if not is_premium:
            return self._generate_free_markdown_dashboard(output_path)
        
        # Obtener todos los datos
        project_data = {
            "overview": self.tracker.get_project_overview(),
            "progress": self.tracker.get_progress_metrics(),
            "branches": self.tracker.get_branch_status(),
            "features": self.tracker.get_feature_progress(),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "detailed": detailed
        }
        
        # Solo incluir análisis pesados si está en modo detallado
        if detailed:
            project_data["dependencies"] = self._get_dependency_analysis()
            project_data["recommendations"] = self.tracker.get_recommendations()
        
        # Generar contenido Markdown
        markdown = self._generate_markdown(project_data)
        
        # Determinar ruta de salida
        if not output_path:
            project_name = os.path.basename(self.project_path).replace(" ", "_")
            # Crear el directorio de análisis si no existe
            analyses_dir = os.path.join(self.project_path, "project-output", "analyses")
            os.makedirs(analyses_dir, exist_ok=True)
            output_path = os.path.join(
                analyses_dir,
                f"project_dashboard_{project_name}.md"
            )
        
        # Guardar el archivo
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            logger.info(f"Dashboard Markdown generado en: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error al guardar el dashboard: {str(e)}")
            raise
    
    def generate_dashboard(self, output_path: Optional[str] = None, premium_mode: bool = False, detailed: bool = False) -> str:
        """
        Alias para generate_markdown_dashboard para compatibilidad.
        
        Args:
            output_path: Ruta donde guardar el Markdown (opcional)
            premium_mode: Si está en modo premium (opcional)
            detailed: Si incluir análisis detallado (opcional)
            
        Returns:
            Ruta al archivo Markdown generado
        """
        return self.generate_markdown_dashboard(output_path, premium_mode, detailed)
    
    def _generate_free_markdown_dashboard(self, output_path: Optional[str] = None) -> str:
        """
        Generar versión limitada del dashboard para usuarios free.
        
        Args:
            output_path: Ruta donde guardar el Markdown (opcional)
            
        Returns:
            Ruta al archivo Markdown generado
        """
        # Datos limitados
        project_data = {
            "overview": self.tracker.get_project_overview(),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Generar contenido Markdown simplificado
        markdown = self._generate_free_markdown(project_data)
        
        # Determinar ruta de salida
        if not output_path:
            project_name = os.path.basename(self.project_path).replace(" ", "_")
            # Crear el directorio de análisis si no existe
            analyses_dir = os.path.join(self.project_path, "project-output", "analyses")
            os.makedirs(analyses_dir, exist_ok=True)
            output_path = os.path.join(
                analyses_dir,
                f"project_dashboard_{project_name}_free.md"
            )
        
        # Guardar el archivo
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            logger.info(f"Dashboard (versión free) generado en: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error al guardar el dashboard: {str(e)}")
            raise
    
    def _generate_markdown(self, data: Dict[str, Any]) -> str:
        """
        Generar el contenido Markdown completo del dashboard.
        
        Args:
            data: Datos del proyecto
            
        Returns:
            Contenido Markdown del dashboard
        """
        project_name = os.path.basename(self.project_path)
        is_detailed = data.get('detailed', False)
        
        try:
            overview_section = self._generate_overview_section(data['overview'])
        except Exception as e:
            logger.error(f"Error generando sección overview: {str(e)}")
            overview_section = "## 📋 Visión General del Proyecto\n\nError al generar sección de overview."
        
        try:
            metrics_section = self._generate_metrics_section(data.get('progress', {}))
        except Exception as e:
            logger.error(f"Error generando sección metrics: {str(e)}")
            metrics_section = "## 📈 Métricas de Progreso\n\nError al generar métricas de progreso."
        
        try:
            branches_section = self._generate_simplified_branches_section(data.get('branches', {}))
        except Exception as e:
            logger.error(f"Error generando sección branches: {str(e)}")
            branches_section = "## 🌿 Estado de Branches\n\nError al generar estado de branches."
        
        try:
            features_section = self._generate_features_section(data.get('features', {}))
        except Exception as e:
            logger.error(f"Error generando sección features: {str(e)}")
            logger.error(f"Features data type: {type(data.get('features', {}))}")
            logger.error(f"Features data content: {data.get('features', {})}")
            features_section = "## 🎯 Grupos Funcionales\n\nError al generar grupos funcionales."
        
        # Solo incluir secciones detalladas si está habilitado
        dependencies_section = ""
        recommendations_section = ""
        
        if is_detailed:
            try:
                dependencies_section = self._generate_dependencies_section(data.get('dependencies', {}))
            except Exception as e:
                logger.error(f"Error generando sección dependencies: {str(e)}")
                dependencies_section = "## 🔗 Análisis de Dependencias\n\nError al generar análisis de dependencias."
            
            try:
                recommendations_section = self._generate_recommendations_section(data.get('recommendations', []))
            except Exception as e:
                logger.error(f"Error generando sección recommendations: {str(e)}")
                recommendations_section = "## 💡 Recomendaciones\n\nError al generar recomendaciones."
        
        # Construir el markdown con secciones opcionales
        sections = [
            f"# 📊 Dashboard del Proyecto: {project_name}",
            f"*Generado por ProjectPrompt Premium el {data.get('generated_at')}*",
            "---",
            overview_section,
            metrics_section,
            branches_section,
            features_section
        ]
        
        if is_detailed and dependencies_section:
            sections.append(dependencies_section)
            
        if is_detailed and recommendations_section:
            sections.append(recommendations_section)
        
        sections.extend([
            "---",
            "*Dashboard generado con ProjectPrompt Premium - Para más información visite: https://github.com/Dixter999/project-prompt"
        ])
        
        return "\n\n".join(sections)
    
    def _generate_free_markdown(self, data: Dict[str, Any]) -> str:
        """
        Generar el contenido Markdown limitado para usuarios free.
        
        Args:
            data: Datos del proyecto
            
        Returns:
            Contenido Markdown del dashboard
        """
        project_name = os.path.basename(self.project_path)
        
        # Generate basic functional groups for free users
        basic_features_section = self._generate_free_features_section()
        
        markdown = f"""# 📊 Dashboard del Proyecto: {project_name}

*Generado por ProjectPrompt (versión gratuita) el {data.get('generated_at')}*

---

{self._generate_overview_section(data['overview'])}

{basic_features_section}

## 🚀 Mejora a Premium

Para acceder a métricas avanzadas, análisis de branches, seguimiento de características y recomendaciones personalizadas, actualiza a ProjectPrompt Premium:

### Características Premium disponibles:
- ✨ **Métricas de progreso avanzadas**: Completitud, calidad del código, cobertura de tests
- 🔀 **Análisis de branches**: Estado de ramas, commits recientes, progreso por rama
- 🎯 **Listado detallado de archivos**: Archivos específicos en cada grupo funcional
- 🤖 **Análisis con IA**: Recomendaciones inteligentes y detección de patrones
- 📈 **Métricas de modularidad**: Análisis de arquitectura y dependencias
- 🔍 **Detección de áreas de riesgo**: Identificación de componentes problemáticos

Para más información, ejecuta: `project-prompt subscription plans`

---

*Dashboard generado con ProjectPrompt - Para más información visite: https://github.com/Dixter999/project-prompt
"""
        
        return markdown
    
    def _generate_overview_section(self, overview: Dict[str, Any]) -> str:
        """Generar sección de visión general."""
        stats = overview.get('stats', {})
        files = overview.get('files', {})
        code_metrics = overview.get('code_metrics', {})
        
        # Distribución de líneas
        total_lines = code_metrics.get('total_lines', 0)
        code_lines = code_metrics.get('code_lines', 0)
        comment_lines = code_metrics.get('comment_lines', 0)
        
        code_percent = (code_lines / total_lines * 100) if total_lines > 0 else 0
        comment_percent = (comment_lines / total_lines * 100) if total_lines > 0 else 0
        other_percent = 100 - code_percent - comment_percent
        
        return f"""## 📋 Visión General del Proyecto

### Estadísticas Generales
- **Total de archivos**: {files.get('total', 0):,}
- **Total de líneas**: {total_lines:,}
- **Directorios**: {overview.get('structure', {}).get('directories', 0)}
- **Archivos de código**: {code_metrics.get('files', 0)}

### Distribución de Líneas
- **Código**: {code_lines:,} líneas ({code_percent:.1f}%)
- **Comentarios**: {comment_lines:,} líneas ({comment_percent:.1f}%)
- **Otros**: {total_lines - code_lines - comment_lines:,} líneas ({other_percent:.1f}%)
"""
    
    def _generate_metrics_section(self, progress: Dict[str, Any]) -> str:
        """Generar sección de métricas de progreso."""
        if not progress:
            return ""
            
        completeness = progress.get('completeness', {})
        code_quality = progress.get('code_quality', {})
        testing = progress.get('testing', {})
        
        # Puntuaciones principales
        completeness_score = completeness.get('overall_score', 0)
        doc_percentage = code_quality.get('documentation_percentage', 0)
        test_coverage = testing.get('coverage_estimate', 0)
        
        # Archivos complejos
        complex_files = code_quality.get('complex_files', [])
        complex_files_table = ""
        if complex_files:
            complex_files_table = "| Archivo | Líneas | Funciones | Profundidad |\n|---------|--------|-----------|-------------|\n"
            for file_info in complex_files[:5]:  # Top 5
                file_name = os.path.basename(file_info.get('file', ''))
                lines = file_info.get('lines', 0)
                functions = file_info.get('functions', 0)
                depth = file_info.get('nested_depth', 0)
                complex_files_table += f"| {file_name} | {lines} | {functions} | {depth} |\n"
        
        # Métricas avanzadas (solo premium)
        advanced_section = ""
        if 'advanced' in progress:
            advanced = progress['advanced']
            modularity_score = advanced.get('modularity_score', 0)
            architecture = advanced.get('architecture_pattern', 'Indeterminado')
            
            # Módulos centrales
            central_modules = advanced.get('central_modules', [])
            modules_list = ""
            for module in central_modules[:3]:  # Top 3
                module_name = os.path.basename(module.get('file', ''))
                dependents = module.get('dependents', 0)
                modules_list += f"- **{module_name}**: {dependents} dependientes\n"
            
            advanced_section = f"""
### Métricas Avanzadas
- **Modularidad**: {modularity_score}% (independencia entre componentes)
- **Patrón arquitectónico detectado**: {architecture}

#### Módulos Centrales
{modules_list if modules_list else "No se detectaron módulos centrales."}
"""
        
        return f"""## 📈 Métricas de Progreso

### Métricas Principales
- **Completitud**: {completeness_score}% (componentes implementados vs. planificados)
- **Documentación**: {doc_percentage:.1f}% (porcentaje de código documentado)
- **Cobertura de tests**: {test_coverage:.1f}% (funciones con tests / total funciones)

{advanced_section}

### Archivos con Alta Complejidad
{complex_files_table if complex_files_table else "No se detectaron archivos con alta complejidad."}
"""
    
    def _generate_branches_section(self, branches_data: Dict[str, Any]) -> str:
        """Generar sección de estado de branches."""
        try:
            if not branches_data:
                return "## 🌿 Estado de Branches\n\nNo se detectó información de control de versiones Git."
            
            # Comprobar si tenemos una lista de branches o una estructura de datos con categorías
            if 'branches' in branches_data:
                if isinstance(branches_data['branches'], list):
                    # Formato con lista plana de branches
                    branches_list = branches_data['branches']
                    current_branch = next((b['name'] for b in branches_list if b.get('current', False)), 'N/A')
                    
                    branches_content = "\n### Todas las Branches\n\n"
                    
                    for branch in branches_list:
                        name = branch.get('name', '')
                        date = branch.get('last_commit_date', 'N/A')
                        msg = branch.get('last_commit_msg', 'N/A')
                        
                        current_indicator = " 🌟 (actual)" if branch.get('current', False) else ""
                        branches_content += f"- **{name}**{current_indicator}\n"
                        branches_content += f"  - Último commit: {date}\n"
                        branches_content += f"  - Mensaje: {msg}\n\n"
                    
                elif isinstance(branches_data['branches'], dict):
                    # Formato alternativo con branches como diccionario
                    branches_content = ""
                    current_branch = branches_data.get('current_branch', 'N/A')
                    
                    for branch_name, branch_info in branches_data['branches'].items():
                        branches_content += f"- **{branch_name}**\n"
                        if isinstance(branch_info, dict):
                            for key, value in branch_info.items():
                                branches_content += f"  - {key}: {value}\n"
                        branches_content += "\n"
                else:
                    branches_content = "\nFormato de branches desconocido.\n"
                    current_branch = "N/A"
            
            # Si hay categorías, mostrarlas
            if 'categories' in branches_data and isinstance(branches_data['categories'], dict):
                categories = branches_data['categories']
                current_branch = branches_data.get('current_branch', 'N/A')
                branches_content = ""
                
                for category, branch_list in categories.items():
                    if branch_list:
                        branches_content += f"\n### {category.capitalize()} ({len(branch_list)})\n\n"
                        
                        for branch in branch_list:
                            name = branch.get('name', '')
                            date = branch.get('last_commit_date', 'N/A')
                            msg = branch.get('last_commit_msg', 'N/A')
                            
                            current_indicator = " 🌟 (actual)" if branch.get('current', False) else ""
                            branches_content += f"- **{name}**{current_indicator}\n"
                            branches_content += f"  - Último commit: {date}\n"
                            branches_content += f"  - Mensaje: {msg}\n\n"
            
            return f"""## 🌿 Estado de Branches

**Branch actual**: {current_branch}

{branches_content}"""
        except Exception as e:
            return f"## 🌿 Estado de Branches\n\nError al analizar branches: {str(e)}"
        
        return f"""## 🌿 Estado de Branches

**Branch actual**: {current_branch}

{branches_content}
"""
    
    def _generate_simplified_branches_section(self, branches_data: Dict[str, Any]) -> str:
        """Generar sección simplificada de estado de branches."""
        try:
            if not branches_data:
                return "## 🌿 Estado de Branches\n\nNo se detectó información de control de versiones Git."
            
            current_branch = branches_data.get('current_branch', 'N/A')
            categories = branches_data.get('categories', {})
            
            if not categories:
                return "## 🌿 Estado de Branches\n\nNo se encontraron branches para mostrar."
            
            # Contar branches únicos por categoría
            total_unique_branches = 0
            category_summary = []
            
            for category, branch_list in categories.items():
                if not branch_list:
                    continue
                
                # Remover duplicados basado en el nombre del branch
                seen_names = set()
                unique_branches = []
                for branch in branch_list:
                    name = branch.get('name', '')
                    if name and name not in seen_names:
                        seen_names.add(name)
                        unique_branches.append(branch)
                
                if unique_branches:
                    total_unique_branches += len(unique_branches)
                    category_summary.append((category, len(unique_branches), unique_branches[:5]))  # Solo mostrar top 5
            
            # Generar contenido
            content = f"## 🌿 Estado de Branches\n\n**Branch actual**: {current_branch}\n\n"
            content += f"**Total de branches únicos**: {total_unique_branches}\n\n"
            
            for category, count, sample_branches in category_summary:
                content += f"### {category.capitalize()} ({count})\n\n"
                
                for branch in sample_branches:
                    name = branch.get('name', '')
                    date = branch.get('last_commit_date', 'N/A')
                    msg = branch.get('last_commit_msg', 'N/A')
                    
                    # Truncar mensaje si es muy largo
                    if len(msg) > 80:
                        msg = msg[:77] + "..."
                    
                    current_indicator = " 🌟 (actual)" if branch.get('current', False) else ""
                    content += f"- **{name}**{current_indicator}\n"
                    content += f"  - {date} - {msg}\n\n"
                
                if count > 5:
                    content += f"*... y {count - 5} branches más de tipo {category}*\n\n"
            
            return content
            
        except Exception as e:
            logger.error(f"Error al generar sección simplificada de branches: {str(e)}")
            return f"## 🌿 Estado de Branches\n\nError al analizar branches: {str(e)}"

    def _generate_features_section(self, features_data: Dict[str, Any]) -> str:
        """Generar sección de grupos funcionales."""
        if not features_data or not features_data.get('features'):
            return "## 🎯 Grupos Funcionales\n\nNo se detectaron grupos funcionales específicos para seguimiento."
        
        features = features_data.get('features', {})
        
        # Handle different data structures for features
        items = []
        
        if isinstance(features, dict):
            # If features is a dict, iterate over its items
            items = list(features.items())
        elif isinstance(features, list):
            # If it's a list, convert to (name, data) pairs
            for i, data in enumerate(features):
                if isinstance(data, dict):
                    name = data.get('name', f'Grupo {i+1}')
                    items.append((name, data))
                else:
                    # Handle non-dict items in the list
                    items.append((f'Grupo {i+1}', {'name': str(data), 'type': 'unknown', 'completion_estimate': 0, 'files': 0}))
        else:
            # Handle unexpected data types
            logger.warning(f"Unexpected features data type: {type(features)}")
            return "## 🎯 Grupos Funcionales\n\nError al procesar datos de grupos funcionales."

        if not items:
            return "## 🎯 Grupos Funcionales\n\nNo se encontraron grupos funcionales para mostrar."

        # Sort items by importance if available
        items.sort(key=lambda x: x[1].get('importance', 0) if isinstance(x[1], dict) else 0, reverse=True)

        functional_groups_content = ""
        
        for name, group_data in items:
            # Defensive: ensure group_data is a dict
            if not isinstance(group_data, dict):
                logger.warning(f"Skipping non-dict group data for {name}: {type(group_data)}")
                continue
            
            # Extract group information with fallbacks
            group_name = group_data.get('name', name)
            group_type = group_data.get('type', 'unknown')
            description = group_data.get('description', f"Grupo funcional: {group_name}")
            completion = group_data.get('completion_estimate', 0)
            files_count = group_data.get('files', 0)
            importance = group_data.get('importance', 0)
            file_list = group_data.get('file_list', [])
            
            # Skip groups with zero files
            if not file_list or files_count == 0:
                continue
            
            # Ensure completion is numeric
            if not isinstance(completion, (int, float)):
                completion = 0
            
            # Create progress bar
            progress_bar = "▓" * int(completion / 10) + "░" * (10 - int(completion / 10))
            
            # Determine group icon based on type and name
            icon = "📁"
            if "test" in group_name.lower() or group_type == "test":
                icon = "🧪"
            elif "doc" in group_name.lower() or group_type == "documentation":
                icon = "📖"
            elif "core" in group_name.lower() or "main" in group_name.lower():
                icon = "⚙️"
            elif "ui" in group_name.lower() or "frontend" in group_name.lower():
                icon = "🎨"
            elif "api" in group_name.lower() or group_type == "api":
                icon = "🔗"
            elif "config" in group_name.lower() or group_type == "configuration":
                icon = "⚙️"
            elif group_type == "functionality":
                icon = "🔧"
            elif group_type == "directory":
                icon = "📁"

            # Show up to 10 files, then summarize
            files_md = ""
            if file_list:
                files_md += "**Archivos principales:**\n"
                for f in file_list[:10]:
                    files_md += f"- `{f}`\n"
                if len(file_list) > 10:
                    files_md += f"- ...y {len(file_list) - 10} archivos más\n"

            functional_groups_content += f"""### {icon} {group_name}\n\n**Tipo**: {group_type.capitalize()}  \n**Descripción**: {description}  \n**Completitud**: {completion}% {progress_bar}  \n**Archivos**: {files_count}  \n**Importancia**: {importance:.1f}\n\n{files_md}\n"""

        if not functional_groups_content:
            return "## 🎯 Grupos Funcionales\n\nNo se encontraron grupos funcionales para mostrar."

        return f"""## 🎯 Grupos Funcionales\n\nLos siguientes grupos funcionales han sido identificados en el proyecto:\n\n{functional_groups_content}\n*Los grupos funcionales representan áreas lógicas del código organizadas por funcionalidad, no por estructura de directorios.*\n"""
    
    def _generate_free_features_section(self) -> str:
        """
        Generar una sección simplificada de grupos funcionales para usuarios gratuitos.
        
        Esta versión muestra los grupos funcionales básicos sin los listados detallados
        de archivos, manteniendo la diferenciación con la versión premium.
        
        Returns:
            Contenido Markdown de la sección de características gratuitas
        """
        try:
            # Create a temporary tracker instance for basic functionality detection
            from src.analyzers.project_progress_tracker import ProjectProgressTracker
            
            # Use a basic tracker without premium features
            temp_tracker = ProjectProgressTracker(self.project_path, self.config)
            # Force free access to ensure functional groups are generated for free users
            temp_tracker.premium_access = False
            
            # Get basic functional groups using directory-based approach
            basic_features = temp_tracker._create_directory_based_groups()
            
            # Also try to get basic functionality groups if available
            try:
                func_features = temp_tracker._create_basic_functional_groups()
                # Merge both approaches, prioritizing functionality-based groups
                basic_features.update(func_features)
            except Exception:
                # Fallback to directory-based only
                pass
            
        except Exception as e:
            logger.warning(f"Error al crear grupos funcionales básicos: {e}")
            return self._generate_fallback_features_section()
        
        if not basic_features:
            return self._generate_fallback_features_section()
        
        # Sort by importance and file count
        sorted_features = sorted(basic_features.items(), 
                                key=lambda x: (x[1].get('importance', 0), x[1].get('files', 0)), 
                                reverse=True)
        
        functional_groups_content = ""
        
        for group_name, group_data in sorted_features[:8]:  # Limit to top 8 groups for free users
            # Extract group information with fallbacks
            completion = group_data.get('completion_estimate', 0)
            files_count = group_data.get('files', 0)
            group_type = group_data.get('type', 'unknown')
            description = group_data.get('description', f"Grupo funcional: {group_name}")
            
            # Skip groups with zero files
            if files_count == 0:
                continue
            
            # Ensure completion is numeric
            if not isinstance(completion, (int, float)):
                completion = 0
            
            # Create progress bar
            progress_bar = "▓" * int(completion / 10) + "░" * (10 - int(completion / 10))
            
            # Determine group icon (clean up if emoji already exists)
            clean_name = group_name
            icon = "📁"
            
            if group_name.startswith('🔐'):
                icon = "🔐"
                clean_name = group_name[2:].strip()
            elif group_name.startswith('🗄️'):
                icon = "🗄️"
                clean_name = group_name[3:].strip()
            elif group_name.startswith('🔗'):
                icon = "🔗"
                clean_name = group_name[2:].strip()
            elif group_name.startswith('🎨'):
                icon = "🎨"
                clean_name = group_name[2:].strip()
            elif group_name.startswith('🧪'):
                icon = "🧪"
                clean_name = group_name[2:].strip()
            elif group_name.startswith('⚙️'):
                icon = "⚙️"
                clean_name = group_name[3:].strip()
            elif group_name.startswith('📚'):
                icon = "📚"
                clean_name = group_name[2:].strip()
            elif group_name.startswith('🛡️'):
                icon = "🛡️"
                clean_name = group_name[3:].strip()
            elif group_name.startswith('📋'):
                icon = "📋"
                clean_name = group_name[2:].strip()
            elif group_name.startswith('🚀'):
                icon = "🚀"
                clean_name = group_name[2:].strip()
            elif group_name.startswith('📊'):
                icon = "📊"
                clean_name = group_name[2:].strip()
            elif group_name.startswith('🔧'):
                icon = "🔧"
                clean_name = group_name[2:].strip()
            elif "test" in group_name.lower():
                icon = "🧪"
            elif "doc" in group_name.lower():
                icon = "📖"
            elif "core" in group_name.lower() or "main" in group_name.lower():
                icon = "⚙️"
            elif "ui" in group_name.lower() or "frontend" in group_name.lower():
                icon = "🎨"
            elif "api" in group_name.lower():
                icon = "🔗"
            elif "config" in group_name.lower():
                icon = "⚙️"
            
            functional_groups_content += f"""### {icon} {clean_name}

**Tipo**: {group_type.capitalize()}  
**Descripción**: {description}  
**Completitud**: {completion}% {progress_bar}  
**Archivos**: {files_count}

"""

        if not functional_groups_content:
            return self._generate_fallback_features_section()

        return f"""## 🎯 Grupos Funcionales

Los siguientes grupos funcionales han sido identificados en el proyecto:

{functional_groups_content}
💡 **Versión gratuita**: Se muestran hasta 8 grupos principales sin listado detallado de archivos.  
🚀 **Actualiza a Premium** para ver todos los grupos con archivos específicos y análisis con IA.

"""

    def _generate_fallback_features_section(self) -> str:
        """
        Generar una sección de fallback cuando no se pueden detectar grupos funcionales.
        """
        return """## 🎯 Grupos Funcionales

⚠️ **Análisis básico no disponible**: No se pudieron detectar grupos funcionales en este momento.

### 🚀 ¿Qué obtienes con Premium?
- **Detección inteligente**: Grupos funcionales detectados automáticamente
- **Análisis detallado**: Lista completa de archivos en cada grupo
- **Métricas avanzadas**: Completitud y progreso por funcionalidad
- **Recomendaciones con IA**: Sugerencias específicas de mejora

Para más información, ejecuta: `project-prompt subscription plans`

"""
    
    def _generate_recommendations_section(self, recommendations: List[Dict[str, Any]]) -> str:
        """Generar sección de recomendaciones."""
        if not recommendations:
            return "## 💡 Recomendaciones\n\nNo hay recomendaciones disponibles en este momento."
        
        recommendations_content = ""
        
        # Agrupar por prioridad
        high_priority = [r for r in recommendations if r.get('priority') == 'high']
        medium_priority = [r for r in recommendations if r.get('priority') == 'medium']
        low_priority = [r for r in recommendations if r.get('priority') == 'low']
        
        def format_recommendations(recs, title, icon):
            if not recs:
                return ""
            
            content = f"\n### {icon} {title}\n\n"
            for rec in recs:
                rec_type = rec.get('type', 'General')
                message = rec.get('message', 'Sin descripción')
                action = rec.get('action', '')
                
                content += f"#### {rec_type}\n"
                content += f"{message}\n"
                if action:
                    content += f"**Acción recomendada**: {action}\n"
                content += "\n"
            
            return content
        
        recommendations_content += format_recommendations(
            high_priority, "Prioridad Alta", "🔴"
        )
        recommendations_content += format_recommendations(
            medium_priority, "Prioridad Media", "🟡"
        )
        recommendations_content += format_recommendations(
            low_priority, "Prioridad Baja", "🟢"
        )
        
        return f"""## 💡 Recomendaciones

{recommendations_content}
"""
    
    def _get_dependency_analysis(self) -> Dict[str, Any]:
        """
        Obtener análisis de dependencias del proyecto.
        
        Returns:
            Dict con información sobre dependencias
        """
        try:
            # Intentar usar análisis en caché para evitar análisis duplicados
            from src.analyzers.analysis_cache import get_analysis_cache
            cache = get_analysis_cache()
            
            # Usar cache primero si está disponible
            cached_result = cache.get(self.project_path, 'dependencies')
            if cached_result:
                logger.info(f"✅ Usando análisis de dependencias en caché para {self.project_path}")
                analysis_result = cached_result
            else:
                # Sin caché, ejecutar análisis
                from src.analyzers.dependency_graph import DependencyGraph
                
                dep_analyzer = DependencyGraph()
                analysis_result = dep_analyzer.build_dependency_graph(self.project_path, max_files=1000)
                
                # Guardar en caché para futuras llamadas
                cache.set(self.project_path, 'dependencies', analysis_result)
            
            logger.info("✅ Análisis de dependencias completado")
            
            # Extraer datos relevantes
            metrics = analysis_result.get('metrics', {})
            if 'edges' in metrics and 'nodes' in metrics and 'nodes' > 0:
                # Calcular dependencias promedio si no están ya calculadas
                metrics['average_dependencies_per_file'] = metrics.get(
                    'average_dependencies_per_file', 
                    metrics.get('edges', 0) / max(metrics.get('nodes', 1), 1)
                )
                metrics['total_dependencies'] = metrics.get('total_dependencies', metrics.get('edges', 0))
                metrics['total_files'] = metrics.get('total_files', metrics.get('nodes', 0))
            
            return {
                "graph_data": analysis_result,
                "functionality_groups": analysis_result.get('functionality_groups', []),
                "central_files": analysis_result.get('central_files', []),
                "metrics": metrics,
                "files_excluded": analysis_result.get('files_excluded', {})
            }
            
        except Exception as e:
            logger.error(f"Error al analizar dependencias: {e}")
            return {
                "error": str(e),
                "graph_data": {},
                "functionality_groups": [],
                "central_files": [],
                "metrics": {},
                "files_excluded": {}
            }
    
    def _generate_dependencies_section(self, dependencies_data: Dict[str, Any]) -> str:
        """Generar sección de análisis de dependencias con representación textual del grafo."""
        if not dependencies_data or dependencies_data.get('error'):
            error_msg = dependencies_data.get('error', 'Error desconocido')
            return f"## 🔗 Análisis de Dependencias\n\nError al analizar dependencias: {error_msg}"
        
        graph_data = dependencies_data.get('graph_data', {})
        functionality_groups = dependencies_data.get('functionality_groups', [])
        central_files = dependencies_data.get('central_files', [])
        metrics = dependencies_data.get('metrics', {})
        files_excluded = dependencies_data.get('files_excluded', {})
        
        section_content = "## 🔗 Análisis de Dependencias\n\n"
        
        # Métricas generales
        if metrics:
            total_files = metrics.get('total_files', 0)
            total_dependencies = metrics.get('total_dependencies', 0)
            avg_dependencies = metrics.get('average_dependencies_per_file', 0)
            
            section_content += f"""### 📊 Métricas del Grafo de Dependencias

- **Total de archivos analizados**: {total_files}
- **Total de dependencias**: {total_dependencies}  
- **Promedio de dependencias por archivo**: {avg_dependencies:.1f}

"""

        # Archivos centrales/críticos
        if central_files:
            section_content += "### 🎯 Archivos Centrales\n\n"
            section_content += "Archivos con alto número de dependencias (críticos para el proyecto):\n\n"
            
            for file_info in central_files[:10]:  # Mostrar top 10
                if isinstance(file_info, dict):
                    file_path = file_info.get('file', 'archivo desconocido')
                    dep_count = file_info.get('dependencies', 0)
                    reverse_dep_count = file_info.get('reverse_dependencies', 0)
                else:
                    file_path = str(file_info)
                    dep_count = 0
                    reverse_dep_count = 0
                
                # Extraer solo el nombre del archivo y directorio inmediato
                file_display = "/".join(file_path.split("/")[-2:]) if "/" in file_path else file_path
                
                section_content += f"- **{file_display}**: {dep_count} dependencias, {reverse_dep_count} dependencias inversas\n"
            
            section_content += "\n"

        # Representación textual del grafo por grupos funcionales
        if functionality_groups:
            section_content += "### 🗂️ Estructura de Dependencias por Grupos Funcionales\n\n"
            
            for group in functionality_groups:
                if not isinstance(group, dict):
                    continue
                    
                group_name = group.get('name', 'Grupo sin nombre')
                group_files = group.get('files', [])
                group_type = group.get('type', 'unknown')
                
                if not group_files:
                    continue
                
                # Determinar icono del grupo
                icon = "📁"
                if "test" in group_name.lower():
                    icon = "🧪"
                elif "doc" in group_name.lower():
                    icon = "📖"
                elif "core" in group_name.lower() or "main" in group_name.lower():
                    icon = "⚙️"
                elif "ui" in group_name.lower():
                    icon = "🎨"
                elif "api" in group_name.lower():
                    icon = "🔗"
                
                section_content += f"#### {icon} {group_name} ({len(group_files)} archivos)\n\n"
                
                # Crear representación textual de las conexiones dentro del grupo
                connections_found = False
                dependencies_graph = graph_data.get('dependencies', {})
                
                for file_item in group_files[:8]:  # Limitar a 8 archivos por grupo
                    # Comprobar si es un diccionario o una cadena
                    if isinstance(file_item, dict):
                        file_path = file_item.get('path', file_item.get('file', ''))
                    else:
                        file_path = str(file_item)
                        
                    file_display = file_path.split("/")[-1] if "/" in file_path else file_path
                    file_deps = dependencies_graph.get(file_path, [])
                    
                    # Obtener rutas normalizadas para comparar
                    group_file_paths = []
                    for gf in group_files:
                        if isinstance(gf, dict):
                            gf_path = gf.get('path', gf.get('file', ''))
                            if gf_path:
                                group_file_paths.append(gf_path)
                        else:
                            group_file_paths.append(str(gf))
                    
                    # Filtrar dependencias que estén en el mismo grupo
                    internal_deps = [dep for dep in file_deps if dep in group_file_paths]
                    external_deps = [dep for dep in file_deps if dep not in group_file_paths]
                    
                    if internal_deps or external_deps:
                        connections_found = True
                        section_content += f"```\n{file_display}\n"
                        
                        # Dependencias internas del grupo
                        for dep in internal_deps[:3]:  # Máximo 3 por claridad
                            dep_display = dep.split("/")[-1] if "/" in dep else dep
                            section_content += f"├── 🔗 {dep_display}\n"
                        
                        # Dependencias externas
                        if external_deps:
                            section_content += f"└── 🌐 {len(external_deps)} deps externas\n"
                        
                        section_content += "```\n\n"
                
                if not connections_found:
                    section_content += "*No se detectaron dependencias internas significativas en este grupo.*\n\n"

        # Archivos excluidos
        if files_excluded:
            section_content += "### 🚫 Manejo de .gitignore\n\n"
            total_excluded = sum(files_excluded.values()) if isinstance(files_excluded, dict) else 0
            
            if total_excluded > 0:
                section_content += f"**Total de archivos excluidos**: {total_excluded}\n\n"
                
                if isinstance(files_excluded, dict):
                    for pattern, count in files_excluded.items():
                        if count > 0:
                            section_content += f"- `{pattern}`: {count} archivos excluidos\n"
                    section_content += "\n"
            else:
                section_content += "✅ No se encontraron archivos excluidos por .gitignore que afecten el análisis.\n\n"

        # Agregar representación textual del grafo
        graph_data_for_textual = dependencies_data.get('graph_data', {})
        
        if graph_data_for_textual:
            section_content += "### 📊 Representación Textual del Grafo de Dependencias\n\n"
            try:
                from src.analyzers.dependency_graph import DependencyGraph
                dep_analyzer = DependencyGraph()
                textual_representation = dep_analyzer._generate_text_visualization(graph_data_for_textual, max_nodes=15)
                
                if textual_representation and textual_representation.strip():
                    section_content += "```\n"
                    section_content += textual_representation
                    section_content += "\n```\n\n"
                    
                    # Agregar matriz de dependencias si hay conexiones
                    try:
                        dependency_matrix = dep_analyzer.generate_dependency_matrix(graph_data_for_textual, max_files=8)
                        section_content += dependency_matrix
                    except Exception as e:
                        logger.warning(f"Error al generar matriz de dependencias: {e}")
                else:
                    section_content += "*No se pudieron encontrar conexiones significativas para la representación textual.*\n\n"
                    
            except Exception as e:
                section_content += f"*Error al generar representación textual: {str(e)}*\n\n"

        # Nota explicativa
        section_content += """*Este análisis muestra la estructura de dependencias del proyecto, ayudando a identificar:*
- *Archivos centrales críticos para el funcionamiento*
- *Organización lógica del código por funcionalidad*  
- *Posibles puntos de refactorización o mejora arquitectural*
"""
        
        return section_content

    # ...existing code...
def main():
    """Punto de entrada cuando se ejecuta como script."""
    if len(sys.argv) < 2:
        print("Uso: python markdown_dashboard.py <ruta_proyecto> [ruta_salida]")
        sys.exit(1)
    
    project_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        generator = MarkdownDashboardGenerator(project_path)
        result_path = generator.generate_dashboard(output_path)
        print(f"Dashboard generado exitosamente: {result_path}")
    except Exception as e:
        print(f"Error al generar dashboard: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
