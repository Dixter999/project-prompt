#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para visualizar el dashboard de progreso del proyecto.

Este módulo implementa una interfaz de usuario para mostrar un dashboard 
con el progreso del proyecto, métricas y recomendaciones.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import webbrowser
import tempfile
import argparse

# Ensure local imports take precedence over system-installed packages
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.analyzers.project_progress_tracker import ProjectProgressTracker, get_project_progress_tracker
from src.utils.logger import get_logger
from src.utils.config import ConfigManager
# Premium features now available for all users

# Configuración del logger
logger = get_logger()


class DashboardGenerator:
    """
    Generador de dashboard para visualizar progreso de proyecto.
    
    Esta clase genera una representación visual del progreso del proyecto
    utilizando HTML/CSS para mostrar métricas, gráficos y recomendaciones.
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
        # Premium features now available for all users
        self.tracker = get_project_progress_tracker(project_path, config)
        
        # Premium features now available for all users
        self.premium_access = True
        
        # Recursos para el dashboard
        self._css_template = self._get_css_template()
        self._js_template = self._get_js_template()
    
    def generate_dashboard(self, output_path: Optional[str] = None, open_browser: bool = True) -> str:
        """
        Generar el dashboard y guardarlo como HTML.
        
        Args:
            output_path: Ruta donde guardar el HTML (opcional)
            open_browser: Si es True, abre el dashboard en el navegador
            
        Returns:
            Ruta al archivo HTML generado
        """
        # Si no tiene acceso premium, generar versión reducida
        if not self.premium_access:
            return self._generate_free_dashboard(output_path, open_browser)
        
        # Recopilar todos los datos necesarios
        project_data = {
            "overview": self.tracker.get_project_overview(),
            "progress": self.tracker.get_progress_metrics(),
            "branches": self.tracker.get_branch_status(),
            "features": self.tracker.get_feature_progress(),
            "recommendations": self.tracker.get_recommendations(),
            "premium": True,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Generar HTML
        html = self._generate_html(project_data)
        
        # Determinar ruta de salida
        if not output_path:
            project_name = os.path.basename(self.project_path).replace(" ", "_")
            # Crear el directorio de análisis si no existe
            analyses_dir = os.path.join(self.project_path, "project-output", "analyses")
            os.makedirs(analyses_dir, exist_ok=True)
            output_path = os.path.join(analyses_dir, f"project_prompt_dashboard_{project_name}.html")
        
        # Guardar el archivo
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"Dashboard generado en: {output_path}")
            
            # Abrir en el navegador si se solicitó
            if open_browser:
                webbrowser.open(f"file://{os.path.abspath(output_path)}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error al guardar el dashboard: {str(e)}")
            raise
    
    def _generate_free_dashboard(self, output_path: Optional[str] = None, open_browser: bool = True) -> str:
        """
        Generar versión limitada del dashboard para usuarios free.
        
        Args:
            output_path: Ruta donde guardar el HTML (opcional)
            open_browser: Si es True, abre el dashboard en el navegador
            
        Returns:
            Ruta al archivo HTML generado
        """
        # Datos limitados
        project_data = {
            "overview": self.tracker.get_project_overview(),
            "progress": {
                "code_quality": self.tracker.get_progress_metrics().get("code_quality", {}),
                "testing": self.tracker.get_progress_metrics().get("testing", {})
            },
            "premium": False,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Generar HTML para versión free
        html = self._generate_html(project_data, is_free=True)
        
        # Determinar ruta de salida
        if not output_path:
            project_name = os.path.basename(self.project_path).replace(" ", "_")
            # Crear el directorio de análisis si no existe
            analyses_dir = os.path.join(self.project_path, "project-output", "analyses")
            os.makedirs(analyses_dir, exist_ok=True)
            output_path = os.path.join(analyses_dir, f"project_prompt_dashboard_{project_name}_free.html")
        
        # Guardar el archivo
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"Dashboard (versión free) generado en: {output_path}")
            
            # Abrir en el navegador si se solicitó
            if open_browser:
                webbrowser.open(f"file://{os.path.abspath(output_path)}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error al guardar el dashboard: {str(e)}")
            raise
    
    def _generate_html(self, data: Dict[str, Any], is_free: bool = False) -> str:
        """
        Generar HTML para el dashboard.
        
        Args:
            data: Datos a mostrar en el dashboard
            is_free: Si es la versión free o premium
            
        Returns:
            Código HTML del dashboard
        """
        # Template básico
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Prompt Dashboard - {data['overview']['name']}</title>
    <style>
        {self._css_template}
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <h1>Project Prompt Dashboard</h1>
            <div class="project-name">{data['overview']['name']}</div>
            <div class="version-tag">{'Premium' if data.get('premium', False) else 'Free Version'}</div>
        </div>
    </header>
    
    <main>
        {self._generate_overview_section(data['overview'])}
        {self._generate_metrics_section(data.get('progress', {}))}
        {self._generate_branches_section(data.get('branches', {})) if not is_free else ''}
        {self._generate_features_section(data.get('features', {})) if not is_free else ''}
        {self._generate_recommendations_section(data.get('recommendations', [])) if not is_free else self._generate_upgrade_section()}
    </main>
    
    <footer>
        <p>Generado por ProjectPrompt el {data.get('generated_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}</p>
    </footer>
    
    <script>
        {self._js_template}
    </script>
</body>
</html>"""
        
        return html_template
    
    def _generate_overview_section(self, overview: Dict[str, Any]) -> str:
        """
        Generar la sección de visión general del proyecto.
        
        Args:
            overview: Datos de visión general
            
        Returns:
            HTML para la sección de visión general
        """
        # Gráfico de distribución de archivos por extensión
        extensions_data = overview.get('files', {}).get('by_extension', {})
        extensions_html = ""
        for ext, count in extensions_data.items():
            extensions_html += f'<div class="ext-item"><span class="ext-name">{ext}</span><span class="ext-count">{count}</span></div>'
        
        # Calcular porcentajes para el gráfico de código vs. comentarios
        code_metrics = overview.get('code_metrics', {})
        total_lines = code_metrics.get('total_lines', 0)
        code_lines = code_metrics.get('code_lines', 0)
        comment_lines = code_metrics.get('comment_lines', 0)
        
        code_percent = (code_lines / total_lines * 100) if total_lines > 0 else 0
        comment_percent = (comment_lines / total_lines * 100) if total_lines > 0 else 0
        other_percent = 100 - code_percent - comment_percent
        
        return f"""
        <section class="card overview">
            <h2>Visión General</h2>
            <div class="overview-stats">
                <div class="stat-item">
                    <div class="stat-value">{overview.get('files', {}).get('total', 0)}</div>
                    <div class="stat-label">Archivos</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{code_metrics.get('total_lines', 0):,}</div>
                    <div class="stat-label">Líneas totales</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{overview.get('structure', {}).get('directories', 0)}</div>
                    <div class="stat-label">Directorios</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{code_metrics.get('files', 0)}</div>
                    <div class="stat-label">Archivos de código</div>
                </div>
            </div>
            
            <div class="overview-details">
                <div class="detail-column">
                    <h3>Distribución de archivos por extensión</h3>
                    <div class="extensions-list">
                        {extensions_html}
                    </div>
                </div>
                <div class="detail-column">
                    <h3>Distribución de líneas</h3>
                    <div class="code-distribution">
                        <div class="progress-bar">
                            <div class="progress-segment code" style="width: {code_percent}%" title="Código: {code_lines:,} líneas ({code_percent:.1f}%)"></div>
                            <div class="progress-segment comments" style="width: {comment_percent}%" title="Comentarios: {comment_lines:,} líneas ({comment_percent:.1f}%)"></div>
                            <div class="progress-segment other" style="width: {other_percent}%" title="Otros: {total_lines - code_lines - comment_lines:,} líneas ({other_percent:.1f}%)"></div>
                        </div>
                        <div class="distribution-legend">
                            <div class="legend-item">
                                <span class="color-box code"></span>
                                <span>Código ({code_percent:.1f}%)</span>
                            </div>
                            <div class="legend-item">
                                <span class="color-box comments"></span>
                                <span>Comentarios ({comment_percent:.1f}%)</span>
                            </div>
                            <div class="legend-item">
                                <span class="color-box other"></span>
                                <span>Otros ({other_percent:.1f}%)</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="last-updated">
                <p>Última actualización: {overview.get('last_updated', 'Desconocido')}</p>
            </div>
        </section>
        """
    
    def _generate_metrics_section(self, progress: Dict[str, Any]) -> str:
        """
        Generar la sección de métricas de progreso.
        
        Args:
            progress: Datos de métricas de progreso
            
        Returns:
            HTML para la sección de métricas
        """
        # Métricas de completitud
        completeness = progress.get('completeness', {})
        completeness_score = completeness.get('score', 0)
        completeness_color = self._get_score_color(completeness_score)
        
        # Métricas de calidad
        code_quality = progress.get('code_quality', {})
        doc_percentage = code_quality.get('documentation_percentage', 0)
        doc_color = self._get_score_color(doc_percentage)
        
        # Métricas de testing
        testing = progress.get('testing', {})
        test_coverage = testing.get('coverage', 0)
        test_color = self._get_score_color(test_coverage)
        test_ratio = testing.get('ratio', 0)
        
        # Lista de archivos complejos
        complex_files = code_quality.get('complex_files', [])
        complex_files_html = ""
        for i, file in enumerate(complex_files[:5]):  # Mostrar máximo 5
            complex_files_html += f"""
            <tr>
                <td>{os.path.basename(file.get('file', ''))}</td>
                <td>{file.get('lines', 0)}</td>
                <td>{file.get('functions', 0)}</td>
                <td>{file.get('nested_depth', 0)}</td>
            </tr>
            """
        
        # Métricas avanzadas (solo premium)
        advanced_html = ""
        if 'advanced' in progress:
            advanced = progress['advanced']
            modularity_score = advanced.get('modularity_score', 0)
            modularity_color = self._get_score_color(modularity_score)
            
            architecture = advanced.get('architecture_pattern', 'Indeterminado')
            
            # Módulos centrales
            central_modules = advanced.get('central_modules', [])
            modules_html = ""
            for module in central_modules[:3]:  # Mostrar máximo 3
                modules_html += f"""
                <div class="module-item">
                    <span class="module-name">{os.path.basename(module.get('file', ''))}</span>
                    <span class="module-deps">{module.get('dependents', 0)} dependientes</span>
                </div>
                """
            
            advanced_html = f"""
            <div class="metrics-row">
                <div class="metric-card">
                    <h3>Modularidad</h3>
                    <div class="circular-progress" style="--progress: {modularity_score}%; --color: {modularity_color};">
                        <div class="inner">
                            <span class="number">{modularity_score}%</span>
                        </div>
                    </div>
                    <p class="description">Medida de independencia entre componentes</p>
                </div>
                
                <div class="metric-card">
                    <h3>Patrón arquitectónico</h3>
                    <div class="architecture-pattern">
                        <span class="pattern-name">{architecture}</span>
                    </div>
                    <p class="description">Patrón detectado en la estructura del proyecto</p>
                </div>
                
                <div class="metric-card">
                    <h3>Módulos centrales</h3>
                    <div class="central-modules">
                        {modules_html}
                    </div>
                    <p class="description">Componentes con mayor número de dependientes</p>
                </div>
            </div>
            """
        
        return f"""
        <section class="card metrics">
            <h2>Métricas de Progreso</h2>
            
            <div class="metrics-row">
                <div class="metric-card">
                    <h3>Completitud</h3>
                    <div class="circular-progress" style="--progress: {completeness_score}%; --color: {completeness_color};">
                        <div class="inner">
                            <span class="number">{completeness_score}%</span>
                        </div>
                    </div>
                    <p class="description">Componentes implementados vs. planificados</p>
                </div>
                
                <div class="metric-card">
                    <h3>Documentación</h3>
                    <div class="circular-progress" style="--progress: {doc_percentage}%; --color: {doc_color};">
                        <div class="inner">
                            <span class="number">{doc_percentage:.1f}%</span>
                        </div>
                    </div>
                    <p class="description">Porcentaje de código documentado</p>
                </div>
                
                <div class="metric-card">
                    <h3>Cobertura de tests</h3>
                    <div class="circular-progress" style="--progress: {test_coverage}%; --color: {test_color};">
                        <div class="inner">
                            <span class="number">{test_coverage:.1f}%</span>
                        </div>
                    </div>
                    <p class="description">Funciones con tests / total funciones</p>
                </div>
            </div>
            
            {advanced_html}
            
            <div class="complex-files">
                <h3>Archivos con alta complejidad</h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Archivo</th>
                            <th>Líneas</th>
                            <th>Funciones</th>
                            <th>Profundidad</th>
                        </tr>
                    </thead>
                    <tbody>
                        {complex_files_html}
                    </tbody>
                </table>
            </div>
        </section>
        """
    
    def _generate_branches_section(self, branches_data: Dict[str, Any]) -> str:
        """
        Generar la sección del estado de branches.
        
        Args:
            branches_data: Datos de branches
            
        Returns:
            HTML para la sección de branches
        """
        if not branches_data or branches_data.get("error"):
            return f"""
            <section class="card branches">
                <h2>Estado de Branches</h2>
                <div class="error-message">
                    <p>{branches_data.get("error", "No se encontró información de branches.")}</p>
                </div>
            </section>
            """
        
        # Categorías de branches
        categories = branches_data.get("categories", {})
        categories_html = ""
        
        # Procesar cada categoría
        for category, branches in categories.items():
            if not branches:
                continue
                
            branches_list = ""
            for branch in branches:
                is_current = branch.get("current", False)
                name = branch.get("name", "")
                date = branch.get("last_commit_date", "")
                msg = branch.get("last_commit_msg", "")
                
                # Verificar si es antigua
                is_old = False
                try:
                    if date != "N/A":
                        date_format = "%Y-%m-%d %H:%M:%S %z"
                        if ' +' not in date and ' -' not in date:
                            date_format = "%Y-%m-%d %H:%M:%S"
                        commit_date = datetime.strptime(date, date_format)
                        delta = datetime.now() - commit_date.replace(tzinfo=None)
                        is_old = delta.days > 30
                except:
                    pass
                
                # Clase para branches actuales y antiguas
                class_names = []
                if is_current:
                    class_names.append("current")
                if is_old:
                    class_names.append("old")
                
                class_attr = f' class="{" ".join(class_names)}"' if class_names else ''
                
                branches_list += f"""
                <li{class_attr}>
                    <div class="branch-name">{name}</div>
                    <div class="branch-details">
                        <span class="commit-date">{date}</span>
                        <span class="commit-msg">{msg}</span>
                    </div>
                </li>
                """
            
            # Solo mostrar categorías con branches
            if branches_list:
                category_display = category.capitalize()
                categories_html += f"""
                <div class="branch-category">
                    <h3>{category_display} ({len(branches)})</h3>
                    <ul class="branch-list">
                        {branches_list}
                    </ul>
                </div>
                """
        
        return f"""
        <section class="card branches">
            <h2>Estado de Branches</h2>
            <div class="branches-container">
                {categories_html}
            </div>
        </section>
        """
    
    def _generate_features_section(self, features_data: Dict[str, Any]) -> str:
        """
        Generar la sección de progreso por características.
        
        Args:
            features_data: Datos de características
            
        Returns:
            HTML para la sección de características
        """
        if not features_data or features_data.get("error"):
            return f"""
            <section class="card features">
                <h2>Progreso por Características</h2>
                <div class="error-message">
                    <p>{features_data.get('error', 'No se encontraron características identificables.')}</p>
                </div>
            </section>
            """

        # Lista de características
        features = features_data.get("features", {})
        features_html = ""

        # Handle both dict and list types for features
        if isinstance(features, dict):
            items = features.items()
        elif isinstance(features, list):
            # If it's a list, convert to (name, data) pairs
            items = []
            for i, data in enumerate(features):
                name = data.get('name', f'Feature {i+1}') if isinstance(data, dict) else f'Feature {i+1}'
                items.append((name, data))
        else:
            items = []

        for name, data in items:
            # Defensive: if data is not a dict, skip
            if not isinstance(data, dict):
                continue
            completion = data.get("completion_estimate", 0)
            color = self._get_score_color(completion)
            files = data.get("files", 0)
            has_tests = "✓" if data.get("has_tests", False) else "✗"
            features_html += f"""
            <tr>
                <td>{name}</td>
                <td>
                    <div class="progress-bar small">
                        <div class="progress-fill" style="width: {completion}%; background-color: {color};" title="{completion}%"></div>
                    </div>
                </td>
                <td>{completion}%</td>
                <td>{files}</td>
                <td>{has_tests}</td>
            </tr>
            """

        return f"""
        <section class="card features">
            <h2>Progreso por Características</h2>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Característica</th>
                        <th>Progreso</th>
                        <th>Completitud</th>
                        <th>Archivos</th>
                        <th>Tests</th>
                    </tr>
                </thead>
                <tbody>
                    {features_html}
                </tbody>
            </table>
        </section>
        """
    
    def _generate_recommendations_section(self, recommendations: List[Dict[str, Any]]) -> str:
        """
        Generar la sección de recomendaciones.
        
        Args:
            recommendations: Lista de recomendaciones
            
        Returns:
            HTML para la sección de recomendaciones
        """
        if not recommendations:
            return """
            <section class="card recommendations">
                <h2>Recomendaciones</h2>
                <p class="no-recommendations">No hay recomendaciones en este momento.</p>
            </section>
            """
        
        recommendations_html = ""
        for rec in recommendations:
            priority = rec.get("priority", "medium")
            priority_class = f"priority-{priority}"
            
            recommendations_html += f"""
            <div class="recommendation-item {priority_class}">
                <div class="rec-header">
                    <span class="rec-type">{rec.get("type", "").capitalize()}</span>
                    <span class="rec-priority">{priority.capitalize()}</span>
                </div>
                <div class="rec-message">{rec.get("message", "")}</div>
                <div class="rec-action">{rec.get("action", "")}</div>
            </div>
            """
        
        return f"""
        <section class="card recommendations">
            <h2>Recomendaciones</h2>
            <div class="recommendations-container">
                {recommendations_html}
            </div>
        </section>
        """
    
    def _generate_upgrade_section(self) -> str:
        """
        Generar sección para actualizar a premium.
        
        Returns:
            HTML para la sección de actualización
        """
        return """
        <section class="card upgrade">
            <h2>Actualiza a Premium</h2>
            <div class="upgrade-content">
                <div class="upgrade-message">
                    <h3>Desbloquea todas las funcionalidades:</h3>
                    <ul>
                        <li>Estado detallado de branches y control de versiones</li>
                        <li>Progreso por características y componentes</li>
                        <li>Recomendaciones proactivas personalizadas</li>
                        <li>Métricas avanzadas de arquitectura y modularidad</li>
                        <li>Identificación de riesgos y áreas de mejora</li>
                    </ul>
                </div>
                <div class="upgrade-action">
                    <button class="upgrade-button" onclick="alert('Para actualizar a premium, ejecuta: project-prompt subscription plans')">Ver Planes Premium</button>
                </div>
            </div>
        </section>
        """
    
    def _get_score_color(self, score: float) -> str:
        """
        Obtener color según puntuación.
        
        Args:
            score: Puntuación (0-100)
            
        Returns:
            Color en formato hexadecimal
        """
        if score < 30:
            return "#e74c3c"  # Rojo
        elif score < 60:
            return "#f1c40f"  # Amarillo
        else:
            return "#2ecc71"  # Verde
    
    def _get_css_template(self) -> str:
        """
        Obtener plantilla CSS para el dashboard.
        
        Returns:
            Código CSS
        """
        return """
        :root {
            --primary: #3498db;
            --secondary: #2c3e50;
            --background: #f5f5f5;
            --card-bg: #ffffff;
            --text: #333333;
            --text-light: #7f8c8d;
            --border: #e0e0e0;
            --success: #2ecc71;
            --warning: #f1c40f;
            --danger: #e74c3c;
            --radius: 8px;
            --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--background);
            color: var(--text);
            line-height: 1.6;
        }
        
        header {
            background-color: var(--primary);
            color: white;
            padding: 20px;
            box-shadow: var(--shadow);
        }
        
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        h1 {
            font-size: 28px;
            margin-bottom: 5px;
        }
        
        .project-name {
            font-size: 18px;
            opacity: 0.9;
            margin-bottom: 5px;
        }
        
        .version-tag {
            background-color: rgba(255, 255, 255, 0.2);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 14px;
            margin-top: 5px;
        }
        
        main {
            max-width: 1200px;
            margin: 20px auto;
            padding: 0 20px;
            display: grid;
            gap: 20px;
        }
        
        .card {
            background-color: var(--card-bg);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 20px;
            margin-bottom: 20px;
        }
        
        h2 {
            color: var(--secondary);
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border);
        }
        
        h3 {
            color: var(--secondary);
            margin-bottom: 15px;
            font-size: 18px;
        }
        
        /* Overview section */
        .overview-stats {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-item {
            text-align: center;
            padding: 15px;
            border-radius: var(--radius);
            border: 1px solid var(--border);
        }
        
        .stat-value {
            font-size: 30px;
            font-weight: bold;
            color: var(--primary);
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 15px;
            color: var(--text-light);
        }
        
        .overview-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 20px;
        }
        
        @media (max-width: 768px) {
            .overview-details {
                grid-template-columns: 1fr;
            }
        }
        
        .extensions-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 10px;
        }
        
        .ext-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 12px;
            background-color: #f8f9fa;
            border-radius: 4px;
            font-size: 14px;
        }
        
        .ext-name {
            color: var(--secondary);
        }
        
        .ext-count {
            color: var(--primary);
            font-weight: bold;
        }
        
        .code-distribution {
            margin-top: 15px;
        }
        
        .progress-bar {
            height: 24px;
            background-color: #f0f0f0;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 15px;
            display: flex;
        }
        
        .progress-bar.small {
            height: 10px;
        }
        
        .progress-segment {
            height: 100%;
        }
        
        .progress-segment.code {
            background-color: #3498db;
        }
        
        .progress-segment.comments {
            background-color: #2ecc71;
        }
        
        .progress-segment.other {
            background-color: #e0e0e0;
        }
        
        .progress-fill {
            height: 100%;
        }
        
        .distribution-legend {
            display: flex;
            justify-content: space-between;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            font-size: 13px;
        }
        
        .color-box {
            width: 12px;
            height: 12px;
            border-radius: 2px;
            margin-right: 5px;
        }
        
        .color-box.code {
            background-color: #3498db;
        }
        
        .color-box.comments {
            background-color: #2ecc71;
        }
        
        .color-box.other {
            background-color: #e0e0e0;
        }
        
        .last-updated {
            text-align: right;
            font-size: 13px;
            color: var(--text-light);
            margin-top: 20px;
        }
        
        /* Metrics section */
        .metrics-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            text-align: center;
            padding: 20px;
            border-radius: var(--radius);
            border: 1px solid var(--border);
        }
        
        .circular-progress {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: conic-gradient(
                var(--color) calc(var(--progress) * 1%),
                #e0e0e0 0
            );
            margin: 0 auto 15px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .circular-progress .inner {
            width: 80%;
            height: 80%;
            background-color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .circular-progress .number {
            font-size: 22px;
            font-weight: bold;
            color: var(--secondary);
        }
        
        .description {
            font-size: 14px;
            color: var(--text-light);
            margin-top: 10px;
        }
        
        .architecture-pattern {
            height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 15px;
        }
        
        .pattern-name {
            font-size: 20px;
            color: var(--secondary);
            font-weight: bold;
        }
        
        .central-modules {
            height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            margin-bottom: 15px;
        }
        
        .module-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            padding: 5px 10px;
            background-color: #f8f9fa;
            border-radius: 4px;
        }
        
        .module-name {
            font-weight: bold;
            color: var(--secondary);
        }
        
        .module-deps {
            color: var(--primary);
        }
        
        /* Data tables */
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        
        .data-table th, .data-table td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }
        
        .data-table th {
            background-color: #f8f9fa;
            font-weight: 600;
        }
        
        .data-table tr:hover {
            background-color: #f8f9fa;
        }
        
        /* Branches section */
        .branches-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .branch-list {
            list-style-type: none;
            margin-bottom: 20px;
        }
        
        .branch-list li {
            padding: 12px;
            border: 1px solid var(--border);
            border-radius: var(--radius);
            margin-bottom: 10px;
            background-color: #f8f9fa;
        }
        
        .branch-list li.current {
            border-left: 5px solid var(--primary);
        }
        
        .branch-list li.old {
            border-left: 5px solid var(--warning);
        }
        
        .branch-name {
            font-weight: bold;
            color: var(--secondary);
            margin-bottom: 5px;
        }
        
        .branch-details {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            color: var(--text-light);
        }
        
        /* Recommendations section */
        .recommendation-item {
            padding: 15px;
            border-left: 5px solid var(--primary);
            background-color: #f8f9fa;
            border-radius: var(--radius);
            margin-bottom: 15px;
        }
        
        .recommendation-item.priority-high {
            border-left-color: var(--danger);
        }
        
        .recommendation-item.priority-medium {
            border-left-color: var(--warning);
        }
        
        .recommendation-item.priority-low {
            border-left-color: var(--success);
        }
        
        .rec-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        
        .rec-type {
            font-weight: bold;
            color: var(--secondary);
        }
        
        .rec-priority {
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 12px;
            background-color: #e0e0e0;
        }
        
        .priority-high .rec-priority {
            background-color: #fadbd8;
            color: #c0392b;
        }
        
        .priority-medium .rec-priority {
            background-color: #fef9e7;
            color: #b7950b;
        }
        
        .priority-low .rec-priority {
            background-color: #d5f5e3;
            color: #27ae60;
        }
        
        .rec-message {
            margin-bottom: 10px;
            font-size: 15px;
        }
        
        .rec-action {
            font-size: 14px;
            color: var(--primary);
            font-style: italic;
        }
        
        /* Upgrade section */
        .upgrade-content {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            align-items: center;
        }
        
        @media (max-width: 768px) {
            .upgrade-content {
                grid-template-columns: 1fr;
            }
        }
        
        .upgrade-message h3 {
            margin-bottom: 10px;
        }
        
        .upgrade-message ul {
            padding-left: 20px;
        }
        
        .upgrade-message li {
            margin-bottom: 8px;
        }
        
        .upgrade-action {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .upgrade-button {
            background-color: var(--primary);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: var(--radius);
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        .upgrade-button:hover {
            background-color: #2980b9;
        }
        
        /* Utility classes */
        .error-message {
            padding: 15px;
            background-color: #fadbd8;
            border-radius: var(--radius);
            color: #c0392b;
        }
        
        .no-recommendations {
            color: var(--text-light);
            font-style: italic;
            text-align: center;
            padding: 20px;
        }
        
        /* Footer */
        footer {
            background-color: var(--secondary);
            color: white;
            text-align: center;
            padding: 15px;
            margin-top: 30px;
            font-size: 14px;
        }
        """
    
    def _get_js_template(self) -> str:
        """
        Obtener plantilla JavaScript para el dashboard.
        
        Returns:
            Código JavaScript
        """
        return """
        // Dashboard interactivity
        document.addEventListener('DOMContentLoaded', function() {
            // Highlight current branch
            const currentBranch = document.querySelector('.branch-list li.current');
            if (currentBranch) {
                currentBranch.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            
            // Make tables sortable
            const tables = document.querySelectorAll('.data-table');
            
            tables.forEach(table => {
                const headers = table.querySelectorAll('th');
                
                headers.forEach((header, index) => {
                    header.addEventListener('click', () => {
                        sortTable(table, index);
                    });
                    
                    // Add sort indicator
                    header.style.cursor = 'pointer';
                    header.setAttribute('title', 'Click to sort');
                });
            });
        });
        
        // Function to sort tables
        function sortTable(table, columnIndex) {
            let switching = true;
            let shouldSwitch, rows, i;
            let switchCount = 0;
            let direction = "asc";
            
            while (switching) {
                switching = false;
                rows = table.rows;
                
                for (i = 1; i < (rows.length - 1); i++) {
                    shouldSwitch = false;
                    
                    const x = rows[i].getElementsByTagName("td")[columnIndex];
                    const y = rows[i + 1].getElementsByTagName("td")[columnIndex];
                    
                    const xContent = x.textContent.toLowerCase();
                    const yContent = y.textContent.toLowerCase();
                    
                    // Convert to numbers if possible
                    const xValue = isNaN(Number(xContent)) ? xContent : Number(xContent);
                    const yValue = isNaN(Number(yContent)) ? yContent : Number(yContent);
                    
                    if (direction === "asc") {
                        if (xValue > yValue) {
                            shouldSwitch = true;
                            break;
                        }
                    } else {
                        if (xValue < yValue) {
                            shouldSwitch = true;
                            break;
                        }
                    }
                }
                
                if (shouldSwitch) {
                    rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                    switching = true;
                    switchCount++;
                } else {
                    if (switchCount === 0 && direction === "asc") {
                        direction = "desc";
                        switching = true;
                    }
                }
            }
            
            // Update sort indicators
            const headers = table.querySelectorAll('th');
            headers.forEach(h => h.classList.remove('sorted-asc', 'sorted-desc'));
            
            headers[columnIndex].classList.add(direction === 'asc' ? 'sorted-desc' : 'sorted-asc');
        }
        """


class DashboardCLI:
    """Interfaz de línea de comandos para el dashboard."""
    
    def __init__(self):
        from src.utils.config import config_manager
        # Premium features now available for all users
        
        self.config = config_manager
        # Premium features now available for all users
    
    def run(self, args=None):
        """
        Ejecutar el CLI del dashboard.
        
        Args:
            args: Lista de argumentos de línea de comandos
            
        Returns:
            int: Código de salida (0 = éxito, 1 = error)
        """
        # Configurar argumentos
        parser = argparse.ArgumentParser(description="Generar dashboard del proyecto")
        parser.add_argument("--project", "-p", default=".", help="Ruta del proyecto")
        parser.add_argument("--output", "-o", help="Ruta donde guardar el dashboard")
        parser.add_argument("--format", "-f", choices=["html", "markdown", "md"], 
                          default="markdown", help="Formato de salida")
        parser.add_argument("--no-browser", action="store_true", 
                          help="No abrir automáticamente en el navegador")
        parser.add_argument("--premium", action="store_true", 
                          help="Modo premium con características avanzadas")
        parser.add_argument("--detailed", action="store_true",
                          help="Incluir análisis detallado de dependencias")
        
        # Procesar argumentos
        parsed_args = parser.parse_args(args or [])
        
        # Configurar banderas
        parsed_args.browser = not parsed_args.no_browser
        
        # Determinar ruta del proyecto
        project_path = parsed_args.project or os.getcwd()
        
        # Normalizar formato
        format_type = "markdown" if parsed_args.format in ["markdown", "md"] else "html"
        
        try:
            # Verificar acceso premium
            has_premium = self.subscription.is_premium_feature_available('project_dashboard')
            is_premium_mode = parsed_args.premium and has_premium
            
            if parsed_args.premium and not has_premium:
                print("⚠️  Las características premium requieren una suscripción activa.")
                print("    Ejecuta 'project-prompt subscription plans' para más información.\n")
                return 1
            
            if not is_premium_mode:
                print("⚠️  Dashboard simplificado (versión gratuita)")
                print("    El dashboard premium incluye:")
                print("    • Análisis detallado de dependencias y arquitectura")
                print("    • Seguimiento completo de branches con filtros inteligentes")
                print("    • Grupos funcionales con archivos específicos")
                print("    • Recomendaciones proactivas personalizadas")
                print("    Ejecuta 'project-prompt premium dashboard' para acceso completo.\n")
            else:
                print("✨ Dashboard Premium con análisis avanzado")
            
            print(f"📊 Generando dashboard {format_type.upper()} para el proyecto en {project_path}")
            
            # Generar dashboard según el formato
            if format_type == "markdown":
                # Importar y usar el generador de markdown
                from src.ui.markdown_dashboard import MarkdownDashboardGenerator
                
                markdown_generator = MarkdownDashboardGenerator(project_path, self.config)
                output_file = markdown_generator.generate_markdown_dashboard(
                    output_path=parsed_args.output,
                    premium_mode=is_premium_mode,
                    detailed=parsed_args.detailed
                )
                
                print(f"✅ Dashboard markdown generado correctamente en: {output_file}")
                
            else:
                # Usar el generador HTML existente
                dashboard = DashboardGenerator(project_path, self.config)
                output_file = dashboard.generate_dashboard(
                    output_path=parsed_args.output,
                    open_browser=parsed_args.browser,
                    premium_mode=is_premium_mode,
                    detailed=parsed_args.detailed
                )
                
                print(f"✅ Dashboard HTML generado correctamente en: {output_file}")
                
                if parsed_args.browser:
                    print("📱 Abriendo dashboard en el navegador...")
            
        except Exception as e:
            print(f"❌ Error al generar dashboard: {str(e)}")
            return 1
        
        return 0


def main():
    """Punto de entrada cuando se ejecuta como script."""
    cli = DashboardCLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
