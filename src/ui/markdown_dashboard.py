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
    
    def generate_markdown_dashboard(self, output_path: Optional[str] = None) -> str:
        """
        Generar el dashboard completo y guardarlo como Markdown.
        
        Args:
            output_path: Ruta donde guardar el Markdown (opcional)
            
        Returns:
            Ruta al archivo Markdown generado
        """
        # Si no tiene acceso premium, generar versión reducida
        if not self.premium_access:
            return self._generate_free_markdown_dashboard(output_path)
        
        # Obtener todos los datos
        project_data = {
            "overview": self.tracker.get_project_overview(),
            "progress": self.tracker.get_progress_metrics(),
            "branches": self.tracker.get_branch_status(),
            "features": self.tracker.get_feature_progress(),
            "recommendations": self.tracker.get_recommendations(),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Generar contenido Markdown
        markdown = self._generate_markdown(project_data)
        
        # Determinar ruta de salida
        if not output_path:
            project_name = os.path.basename(self.project_path).replace(" ", "_")
            output_path = os.path.join(
                self.project_path, 
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
            output_path = os.path.join(
                self.project_path,
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
        
        markdown = f"""# 📊 Dashboard del Proyecto: {project_name}

*Generado por ProjectPrompt Premium el {data.get('generated_at')}*

---

{self._generate_overview_section(data['overview'])}

{self._generate_metrics_section(data.get('progress', {}))}

{self._generate_branches_section(data.get('branches', {}))}

{self._generate_features_section(data.get('features', {}))}

{self._generate_recommendations_section(data.get('recommendations', []))}

---

*Dashboard generado con ProjectPrompt Premium - Para más información visite: https://projectprompt.dev*
"""
        
        return markdown
    
    def _generate_free_markdown(self, data: Dict[str, Any]) -> str:
        """
        Generar el contenido Markdown limitado para usuarios free.
        
        Args:
            data: Datos del proyecto
            
        Returns:
            Contenido Markdown del dashboard
        """
        project_name = os.path.basename(self.project_path)
        
        markdown = f"""# 📊 Dashboard del Proyecto: {project_name}

*Generado por ProjectPrompt (versión gratuita) el {data.get('generated_at')}*

---

{self._generate_overview_section(data['overview'])}

## 🚀 Mejora a Premium

Para acceder a métricas avanzadas, análisis de branches, seguimiento de características y recomendaciones personalizadas, actualiza a ProjectPrompt Premium:

### Características Premium disponibles:
- ✨ **Métricas de progreso avanzadas**: Completitud, calidad del código, cobertura de tests
- 🔀 **Análisis de branches**: Estado de ramas, commits recientes, progreso por rama
- 🎯 **Seguimiento de características**: Progreso detallado por funcionalidad
- 🎯 **Recomendaciones proactivas**: Sugerencias específicas para mejorar el proyecto
- 📈 **Métricas de modularidad**: Análisis de arquitectura y dependencias
- 🔍 **Detección de áreas de riesgo**: Identificación de componentes problemáticos

Para más información, ejecuta: `project-prompt subscription plans`

---

*Dashboard generado con ProjectPrompt - Para más información visite: https://projectprompt.dev*
"""
        
        return markdown
    
    def _generate_overview_section(self, overview: Dict[str, Any]) -> str:
        """Generar sección de visión general."""
        stats = overview.get('stats', {})
        files = overview.get('files', {})
        code_metrics = overview.get('code_metrics', {})
        
        # Preparar estadísticas de extensiones
        extensions_list = ""
        file_extensions = files.get('by_extension', {})
        if file_extensions:
            sorted_extensions = sorted(
                file_extensions.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]  # Top 10
            
            for ext, count in sorted_extensions:
                percentage = (count / files.get('total', 1)) * 100
                extensions_list += f"- **{ext}**: {count} archivos ({percentage:.1f}%)\n"
        
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

### Top 10 Extensiones de Archivo
{extensions_list if extensions_list else "No hay datos de extensiones disponibles."}
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
        if not branches_data or not branches_data.get('branches'):
            return "## 🌿 Estado de Branches\n\nNo se detectó información de control de versiones Git."
        
        branches = branches_data.get('branches', {})
        current_branch = branches_data.get('current_branch', 'N/A')
        
        branches_content = ""
        
        for category, branch_list in branches.items():
            if branch_list:
                branches_content += f"\n### {category.capitalize()} ({len(branch_list)})\n\n"
                
                for branch in branch_list:
                    name = branch.get('name', '')
                    date = branch.get('last_commit_date', 'N/A')
                    msg = branch.get('last_commit_message', 'N/A')
                    
                    current_indicator = " 🌟 (actual)" if name == current_branch else ""
                    branches_content += f"- **{name}**{current_indicator}\n"
                    branches_content += f"  - Último commit: {date}\n"
                    branches_content += f"  - Mensaje: {msg}\n\n"
        
        return f"""## 🌿 Estado de Branches

**Branch actual**: {current_branch}

{branches_content}
"""
    
    def _generate_features_section(self, features_data: Dict[str, Any]) -> str:
        """Generar sección de progreso por características."""
        if not features_data or not features_data.get('features'):
            return "## 🎯 Progreso por Características\n\nNo se detectaron características específicas para seguimiento."
        
        features = features_data.get('features', [])
        
        features_table = "| Característica | Estado | Progreso | Archivos |\n|----------------|--------|----------|----------|\n"
        
        for feature in features:
            name = feature.get('name', 'N/A')
            status = feature.get('status', 'Unknown')
            progress = feature.get('progress', 0)
            files_count = len(feature.get('files', []))
            
            # Convertir progreso a barra visual
            progress_bar = "▓" * int(progress / 10) + "░" * (10 - int(progress / 10))
            
            features_table += f"| {name} | {status} | {progress}% {progress_bar} | {files_count} |\n"
        
        return f"""## 🎯 Progreso por Características

{features_table}
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
