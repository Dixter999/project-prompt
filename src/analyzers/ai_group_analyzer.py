#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Analizador de grupos funcionales con IA (Anthropic Claude).

Este módulo implementa análisis inteligente de grupos funcionales usando
la API de Anthropic para generar análisis detallados de cada archivo
dentro de los grupos detectados.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import time

from src.utils.logger import get_logger
from src.integrations.anthropic_advanced import AdvancedAnthropicClient
from src.analyzers.project_progress_tracker import ProjectProgressTracker
from src.analyzers.dependency_graph import DependencyGraph
from src.utils.config import ConfigManager
from src.ui.cli import CLI

# Configurar logger
logger = get_logger()


class AIGroupAnalyzer:
    """Analizador de grupos funcionales con IA."""
    
    def __init__(self, config: Optional[ConfigManager] = None):
        """
        Inicializar el analizador de grupos con IA.
        
        Args:
            config: Configuración opcional
        """
        self.config = config or ConfigManager()
        self.ai_client = AdvancedAnthropicClient(config=self.config)
        self.cli = CLI()
        
        # Configuración de análisis
        self.batch_size = self.config.get("ai_analysis.batch_size", 5)
        self.max_file_size = self.config.get("ai_analysis.max_file_size", 50000)  # 50KB max por archivo
        self.analysis_delay = self.config.get("ai_analysis.delay", 2)  # 2 segundos entre requests
        
    def analyze_group(self, project_path: str, group_name: str) -> Dict[str, Any]:
        """
        Analizar un grupo funcional específico con IA.
        
        Args:
            project_path: Ruta al proyecto
            group_name: Nombre del grupo a analizar
            
        Returns:
            Diccionario con los resultados del análisis
        """
        try:
            # Verificar acceso premium
            if not self.ai_client.verify_premium_access():
                return {
                    "success": False,
                    "error": "Esta función requiere suscripción premium",
                    "group_name": group_name
                }
            
            # Obtener grupos funcionales del proyecto
            groups = self._get_functional_groups(project_path)
            
            if not groups:
                return {
                    "success": False,
                    "error": "No se encontraron grupos funcionales en el proyecto",
                    "group_name": group_name
                }
            
            # Buscar el grupo específico
            target_group = None
            for group in groups:
                if group.get('name', '').lower() == group_name.lower():
                    target_group = group
                    break
                # También buscar por coincidencia parcial
                if group_name.lower() in group.get('name', '').lower():
                    target_group = group
                    break
            
            if not target_group:
                available_groups = [g.get('name', 'Sin nombre') for g in groups]
                return {
                    "success": False,
                    "error": f"Grupo '{group_name}' no encontrado. Grupos disponibles: {', '.join(available_groups)}",
                    "group_name": group_name,
                    "available_groups": available_groups
                }
            
            # Mostrar información del grupo
            self.cli.print_info(f"\n🤖 Analizando grupo: {target_group['name']}")
            self.cli.print_info(f"📁 Archivos en el grupo: {target_group['size']}")
            
            # Estimar costo antes de proceder
            cost_estimate = self._estimate_analysis_cost(target_group)
            self.cli.print_info(f"💰 Costo estimado: ~${cost_estimate:.4f} USD")
            
            # Confirmar continuación
            if not self.cli.confirm("¿Desea continuar con el análisis?"):
                return {
                    "success": False,
                    "error": "Análisis cancelado por el usuario",
                    "group_name": group_name
                }
            
            # Analizar archivos del grupo
            analysis_results = self._analyze_group_files(project_path, target_group)
            
            # Generar reporte de análisis
            report_path = self._generate_analysis_report(project_path, target_group, analysis_results)
            
            return {
                "success": True,
                "group_name": target_group['name'],
                "files_analyzed": len(analysis_results),
                "report_path": report_path,
                "analysis_results": analysis_results
            }
            
        except Exception as e:
            logger.error(f"Error al analizar grupo '{group_name}': {e}")
            return {
                "success": False,
                "error": f"Error durante el análisis: {str(e)}",
                "group_name": group_name
            }
    
    def _get_functional_groups(self, project_path: str) -> List[Dict[str, Any]]:
        """
        Obtener grupos funcionales del proyecto.
        
        Args:
            project_path: Ruta al proyecto
            
        Returns:
            Lista de grupos funcionales
        """
        try:
            # Intentar usar análisis de dependencias primero
            from src.analyzers.dependency_graph import get_dependency_graph
            dep_analyzer = get_dependency_graph()
            dep_result = dep_analyzer.build_dependency_graph(project_path)
            
            # Usar los grupos del dependency analyzer si están disponibles
            if dep_result.get('functionality_groups') and len(dep_result['functionality_groups']) > 0:
                return dep_result['functionality_groups']
            
            # Fallback: crear grupos basados en estructura de directorios del proyecto
            return self._create_directory_based_groups(project_path)
            
        except Exception as e:
            logger.error(f"Error al obtener grupos funcionales: {e}")
            return []
    
    def _create_directory_based_groups(self, project_path: str) -> List[Dict[str, Any]]:
        """
        Crear grupos funcionales basados en la estructura de directorios del proyecto.
        
        Args:
            project_path: Ruta al proyecto
            
        Returns:
            Lista de grupos funcionales basados en directorios
        """
        import os
        from pathlib import Path
        
        groups = []
        project_root = Path(project_path).resolve()
        
        # Definir directorios importantes y sus descripciones
        important_dirs = {
            'src/analyzers': '🔍 Analizadores',
            'src/commands': '⚡ Comandos CLI',
            'src/core': '🎯 Núcleo del Sistema',
            'src/generators': '🏗️ Generadores',
            'src/integrations': '🔗 Integraciones',
            'src/ui': '🎨 Interfaz de Usuario',
            'src/utils': '🛠️ Utilidades',
            'tests': '🧪 Tests',
            'docs': '📚 Documentación',
            'vscode-extension': '🔌 Extensión VSCode'
        }
        
        for dir_path, display_name in important_dirs.items():
            full_dir_path = project_root / dir_path
            if full_dir_path.exists() and full_dir_path.is_dir():
                # Recopilar archivos de código en el directorio
                files = []
                for ext in ['.py', '.js', '.ts', '.md', '.json']:
                    pattern = f"**/*{ext}"
                    for file_path in full_dir_path.glob(pattern):
                        if file_path.is_file() and not any(ignore in str(file_path) for ignore in ['__pycache__', '.pyc', 'node_modules']):
                            rel_path = file_path.relative_to(project_root)
                            files.append({'path': str(rel_path)})
                
                if files:  # Solo incluir directorios con archivos
                    groups.append({
                        'name': display_name,
                        'type': 'directory',
                        'size': len(files),
                        'files': files,
                        'total_importance': len(files) * 3,
                        'directory_path': dir_path
                    })
        
        # Si no se encontraron grupos, crear uno genérico con archivos principales
        if not groups:
            main_files = []
            for ext in ['.py', '.js', '.ts']:
                pattern = f"src/**/*{ext}"
                for file_path in project_root.glob(pattern):
                    if file_path.is_file() and not any(ignore in str(file_path) for ignore in ['__pycache__', '.pyc']):
                        rel_path = file_path.relative_to(project_root)
                        main_files.append({'path': str(rel_path)})
            
            if main_files:
                groups.append({
                    'name': '📁 Código Fuente',
                    'type': 'directory',
                    'size': len(main_files),
                    'files': main_files,
                    'total_importance': len(main_files) * 2,
                    'directory_path': 'src'
                })
        
        return groups
    
    def _estimate_analysis_cost(self, group: Dict[str, Any]) -> float:
        """
        Estimar el costo del análisis basado en el número de archivos.
        
        Args:
            group: Grupo a analizar
            
        Returns:
            Costo estimado en USD
        """
        # Estimación basada en tokens promedio por archivo
        files_count = group.get('size', 0)
        avg_tokens_per_file = 1000  # Estimación conservadora
        tokens_for_analysis = 500   # Tokens adicionales para análisis
        
        total_tokens = files_count * (avg_tokens_per_file + tokens_for_analysis)
        
        # Precio estimado de Claude-3 Sonnet (modelo de análisis)
        price_per_1k_tokens = 0.003  # $0.003 por 1K tokens (aprox)
        
        return (total_tokens / 1000) * price_per_1k_tokens
    
    def _analyze_group_files(self, project_path: str, group: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analizar todos los archivos de un grupo.
        
        Args:
            project_path: Ruta al proyecto
            group: Grupo a analizar
            
        Returns:
            Lista con análisis de cada archivo
        """
        files = group.get('files', [])
        analysis_results = []
        
        # Filtrar archivos válidos para análisis
        valid_files = self._filter_analyzable_files(project_path, files)
        
        if not valid_files:
            logger.warning("No hay archivos válidos para analizar en el grupo")
            return []
        
        # Mostrar progreso
        total_files = len(valid_files)
        self.cli.print_info(f"📊 Analizando {total_files} archivos...")
        
        # Procesar archivos en lotes
        for i in range(0, len(valid_files), self.batch_size):
            batch = valid_files[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (len(valid_files) + self.batch_size - 1) // self.batch_size
            
            self.cli.print_info(f"🔄 Procesando lote {batch_num}/{total_batches} ({len(batch)} archivos)")
            
            # Analizar archivos del lote
            for file_info in batch:
                try:
                    file_analysis = self._analyze_single_file(project_path, file_info)
                    if file_analysis:
                        analysis_results.append(file_analysis)
                    
                    # Progreso individual
                    progress = len(analysis_results)
                    percentage = (progress / total_files) * 100
                    self.cli.print_info(f"📊 Archivos analizados: {progress}/{total_files} ({percentage:.1f}%)")
                    
                except Exception as e:
                    logger.error(f"Error al analizar archivo {file_info.get('path', '')}: {e}")
                    continue
            
            # Delay entre lotes para evitar rate limiting
            if i + self.batch_size < len(valid_files):
                self.cli.print_info(f"⏳ Esperando {self.analysis_delay}s antes del siguiente lote...")
                time.sleep(self.analysis_delay)
        
        self.cli.print_success(f"✅ Análisis completado: {len(analysis_results)} archivos procesados")
        return analysis_results
    
    def _filter_analyzable_files(self, project_path: str, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filtrar archivos que pueden ser analizados.
        
        Args:
            project_path: Ruta al proyecto
            files: Lista de archivos
            
        Returns:
            Lista de archivos válidos para análisis
        """
        valid_files = []
        
        for file_info in files:
            file_path = file_info.get('path', '')
            
            if not file_path:
                continue
            
            full_path = os.path.join(project_path, file_path)
            
            # Verificar que el archivo existe
            if not os.path.exists(full_path):
                continue
            
            # Verificar que no es un directorio
            if os.path.isdir(full_path):
                continue
            
            # Verificar tamaño del archivo
            try:
                file_size = os.path.getsize(full_path)
                if file_size > self.max_file_size:
                    logger.debug(f"Archivo {file_path} muy grande ({file_size} bytes), omitiendo")
                    continue
                
                if file_size == 0:
                    logger.debug(f"Archivo {file_path} vacío, omitiendo")
                    continue
            except OSError:
                continue
            
            # Verificar que es un archivo de texto
            if self._is_text_file(full_path):
                valid_files.append(file_info)
        
        return valid_files
    
    def _is_text_file(self, file_path: str) -> bool:
        """
        Verificar si un archivo es de texto y puede ser analizado.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si es un archivo de texto válido
        """
        # Extensiones de archivos de código comunes
        text_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.clj',
            '.html', '.css', '.scss', '.sass', '.less', '.xml', '.json', '.yaml',
            '.yml', '.toml', '.ini', '.cfg', '.conf', '.md', '.txt', '.sql',
            '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd'
        }
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in text_extensions:
            return True
        
        # Verificar si es archivo de texto por contenido (primera muestra)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                sample = f.read(1024)  # Leer primeros 1KB
                # Si contiene principalmente caracteres imprimibles, considerarlo texto
                printable_chars = sum(1 for c in sample if c.isprintable() or c.isspace())
                return (printable_chars / len(sample)) > 0.7 if sample else False
        except:
            return False
    
    def _analyze_single_file(self, project_path: str, file_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analizar un archivo individual con IA.
        
        Args:
            project_path: Ruta al proyecto
            file_info: Información del archivo
            
        Returns:
            Análisis del archivo o None si falla
        """
        file_path = file_info.get('path', '')
        full_path = os.path.join(project_path, file_path)
        
        try:
            # Leer contenido del archivo
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                return None
            
            # Determinar lenguaje del archivo
            language = self._detect_file_language(file_path)
            
            # Crear prompt para análisis
            analysis_prompt = self._create_analysis_prompt(file_path, content, language)
            
            # Solicitar análisis a Claude
            result = self.ai_client.explain_code(
                code=content,
                language=language,
                detail_level="advanced",
                context={
                    "file_path": file_path,
                    "analysis_type": "functional_group_analysis"
                }
            )
            
            if not result.get('success', False):
                logger.error(f"Error en análisis IA para {file_path}: {result.get('error', 'Unknown error')}")
                return None
            
            # Procesar y estructurar respuesta
            analysis_data = self._parse_ai_analysis(file_path, result['explanation'], content)
            
            return analysis_data
            
        except Exception as e:
            logger.error(f"Error al analizar archivo {file_path}: {e}")
            return None
    
    def _detect_file_language(self, file_path: str) -> str:
        """
        Detectar el lenguaje de programación de un archivo.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lenguaje detectado
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript', 
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.xml': 'xml',
            '.sql': 'sql',
            '.sh': 'bash',
            '.bash': 'bash',
            '.md': 'markdown'
        }
        
        return language_map.get(ext, 'text')
    
    def _create_analysis_prompt(self, file_path: str, content: str, language: str) -> str:
        """
        Crear prompt específico para análisis de grupo funcional.
        
        Args:
            file_path: Ruta al archivo
            content: Contenido del archivo
            language: Lenguaje del archivo
            
        Returns:
            Prompt optimizado para el análisis
        """
        return f"""Analiza este archivo {language} que forma parte de un grupo funcional:

Archivo: {file_path}

Por favor proporciona un análisis estructurado que incluya:

1. **Funcionalidad Principal**: ¿Qué hace este archivo?
2. **Responsabilidades**: Principales responsabilidades y propósito
3. **Dependencias**: Qué librerías, módulos o archivos importa/usa
4. **Calidad del Código**: Evaluación de la calidad (1-10) con justificación
5. **Complejidad**: Nivel de complejidad (Baja/Media/Alta) y por qué
6. **Mantenibilidad**: Qué tan fácil es mantener este código
7. **Posibles Mejoras**: Sugerencias específicas para mejorar

Mantén el análisis conciso pero informativo."""
    
    def _parse_ai_analysis(self, file_path: str, ai_response: str, original_content: str) -> Dict[str, Any]:
        """
        Parsear y estructurar la respuesta de IA.
        
        Args:
            file_path: Ruta al archivo
            ai_response: Respuesta de Claude
            original_content: Contenido original del archivo
            
        Returns:
            Análisis estructurado
        """
        # Calcular métricas básicas del archivo
        lines_count = len(original_content.splitlines())
        char_count = len(original_content)
        
        # Intentar extraer información estructurada de la respuesta
        functionality = self._extract_section(ai_response, "Funcionalidad Principal", "Funcionalidad")
        responsibilities = self._extract_section(ai_response, "Responsabilidades")
        dependencies = self._extract_section(ai_response, "Dependencias")
        quality_info = self._extract_section(ai_response, "Calidad del Código", "Calidad")
        complexity = self._extract_section(ai_response, "Complejidad")
        maintainability = self._extract_section(ai_response, "Mantenibilidad")
        improvements = self._extract_section(ai_response, "Posibles Mejoras", "Mejoras")
        
        # Extraer score de calidad si está presente
        quality_score = self._extract_quality_score(quality_info)
        
        return {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'analysis': {
                'functionality': functionality,
                'responsibilities': responsibilities,
                'dependencies': dependencies,
                'quality_assessment': quality_info,
                'complexity': complexity,
                'maintainability': maintainability,
                'suggested_improvements': improvements,
                'quality_score': quality_score
            },
            'metrics': {
                'lines_of_code': lines_count,
                'character_count': char_count,
                'file_size_kb': round(char_count / 1024, 2)
            },
            'analysis_timestamp': datetime.now().isoformat(),
            'full_ai_response': ai_response
        }
    
    def _extract_section(self, text: str, *section_names: str) -> str:
        """
        Extraer una sección específica del análisis de IA.
        
        Args:
            text: Texto completo
            section_names: Nombres posibles de la sección
            
        Returns:
            Contenido de la sección
        """
        import re
        
        for section_name in section_names:
            # Buscar patrones como "**Sección:**" o "1. **Sección**:"
            patterns = [
                rf'\*\*{re.escape(section_name)}[^*]*\*\*[:\s]*([^*\n]*(?:\n(?!\d+\.|[*#]).*)*)',
                rf'\d+\.\s*\*\*{re.escape(section_name)}[^*]*\*\*[:\s]*([^*\n]*(?:\n(?!\d+\.|[*#]).*)*)',
                rf'{re.escape(section_name)}[:\s]*([^\n]*(?:\n(?!\d+\.|[*#]).*)*)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    content = match.group(1).strip()
                    if content:
                        return content
        
        return "No especificado"
    
    def _extract_quality_score(self, quality_text: str) -> Optional[int]:
        """
        Extraer puntuación numérica de calidad del texto.
        
        Args:
            quality_text: Texto con información de calidad
            
        Returns:
            Puntuación de 1-10 o None
        """
        import re
        
        # Buscar patrones como "8/10", "7 de 10", "puntuación: 6"
        patterns = [
            r'(\d+)/10',
            r'(\d+)\s*de\s*10',
            r'puntuación[:\s]*(\d+)',
            r'score[:\s]*(\d+)',
            r'rating[:\s]*(\d+)',
            r'calidad[:\s]*(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, quality_text, re.IGNORECASE)
            if match:
                score = int(match.group(1))
                if 1 <= score <= 10:
                    return score
        
        return None
    
    def _generate_analysis_report(self, project_path: str, group: Dict[str, Any], analysis_results: List[Dict[str, Any]]) -> str:
        """
        Generar reporte markdown del análisis del grupo.
        
        Args:
            project_path: Ruta al proyecto
            group: Información del grupo
            analysis_results: Resultados del análisis
            
        Returns:
            Ruta al archivo de reporte generado
        """
        # Crear directorio de salida
        output_dir = os.path.join(project_path, "project-output", "analyses", "groups")
        os.makedirs(output_dir, exist_ok=True)
        
        # Crear nombre de archivo seguro
        safe_group_name = "".join(c for c in group['name'] if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_group_name = safe_group_name.replace(' ', '_')
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"{safe_group_name}_{timestamp}.md"
        report_path = os.path.join(output_dir, report_filename)
        
        # Generar contenido del reporte
        content = self._create_report_content(group, analysis_results, project_path)
        
        # Escribir reporte
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.cli.print_success(f"📄 Reporte generado: {report_path}")
        return report_path
    
    def _create_report_content(self, group: Dict[str, Any], analysis_results: List[Dict[str, Any]], project_path: str) -> str:
        """
        Crear el contenido markdown del reporte.
        
        Args:
            group: Información del grupo
            analysis_results: Resultados del análisis
            project_path: Ruta al proyecto
            
        Returns:
            Contenido markdown del reporte
        """
        project_name = os.path.basename(project_path)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = [
            f"# 🤖 Análisis IA de Grupo Funcional: {group['name']}",
            "",
            f"**Proyecto:** {project_name}  ",
            f"**Fecha de Análisis:** {timestamp}  ",
            f"**Tipo de Grupo:** {group.get('type', 'Unknown')}  ",
            f"**Archivos Analizados:** {len(analysis_results)}  ",
            "",
            "---",
            "",
            "## 📊 Resumen del Grupo",
            "",
            f"- **Nombre del Grupo:** {group['name']}",
            f"- **Tipo:** {group.get('type', 'Unknown')}",
            f"- **Total de Archivos:** {group.get('size', 0)}",
            f"- **Archivos Procesados:** {len(analysis_results)}",
            f"- **Importancia Total:** {group.get('total_importance', 0):.1f}",
            "",
        ]
        
        # Agregar tabla resumen
        if analysis_results:
            content.extend([
                "## 📋 Tabla de Análisis por Archivo",
                "",
                "| Archivo | Funcionalidad | Dependencias | Calidad | Complejidad |",
                "|---------|---------------|--------------|---------|-------------|"
            ])
            
            for result in analysis_results:
                file_name = result['file_name']
                functionality = self._truncate_text(result['analysis']['functionality'], 50)
                dependencies = self._truncate_text(result['analysis']['dependencies'], 40)
                quality_score = result['analysis']['quality_score'] or "N/A"
                complexity = result['analysis']['complexity']
                
                content.append(
                    f"| `{file_name}` | {functionality} | {dependencies} | {quality_score} | {complexity} |"
                )
            
            content.extend(["", "---", ""])
        
        # Análisis detallado por archivo
        content.extend([
            "## 🔍 Análisis Detallado por Archivo",
            ""
        ])
        
        for i, result in enumerate(analysis_results, 1):
            analysis = result['analysis']
            metrics = result['metrics']
            
            content.extend([
                f"### {i}. 📄 `{result['file_path']}`",
                "",
                f"**Métricas:**",
                f"- Líneas de código: {metrics['lines_of_code']}",
                f"- Tamaño: {metrics['file_size_kb']} KB",
                "",
                f"**🎯 Funcionalidad Principal:**",
                f"{analysis['functionality']}",
                "",
                f"**📋 Responsabilidades:**",
                f"{analysis['responsibilities']}",
                "",
                f"**🔗 Dependencias:**",
                f"{analysis['dependencies']}",
                "",
                f"**⭐ Calidad del Código:**",
                f"{analysis['quality_assessment']}",
                ""
            ])
            
            if analysis['quality_score']:
                content.append(f"**Puntuación de Calidad:** {analysis['quality_score']}/10")
                content.append("")
            
            content.extend([
                f"**🔧 Complejidad:**",
                f"{analysis['complexity']}",
                "",
                f"**🛠️ Mantenibilidad:**",
                f"{analysis['maintainability']}",
                "",
                f"**💡 Sugerencias de Mejora:**",
                f"{analysis['suggested_improvements']}",
                "",
                "---",
                ""
            ])
        
        # Agregar estadísticas finales
        if analysis_results:
            avg_quality = self._calculate_average_quality(analysis_results)
            complexity_dist = self._calculate_complexity_distribution(analysis_results)
            
            content.extend([
                "## 📈 Estadísticas del Grupo",
                "",
                f"- **Calidad Promedio:** {avg_quality:.1f}/10",
                f"- **Distribución de Complejidad:**"
            ])
            
            for complexity, count in complexity_dist.items():
                percentage = (count / len(analysis_results)) * 100
                content.append(f"  - {complexity}: {count} archivos ({percentage:.1f}%)")
            
            content.extend(["", "---", ""])
        
        # Footer
        content.extend([
            "",
            f"*Reporte generado por Project Prompt - Análisis IA con Anthropic Claude*",
            f"*Timestamp: {timestamp}*"
        ])
        
        return "\n".join(content)
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncar texto a longitud máxima."""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def _calculate_average_quality(self, analysis_results: List[Dict[str, Any]]) -> float:
        """Calcular calidad promedio."""
        scores = [r['analysis']['quality_score'] for r in analysis_results if r['analysis']['quality_score']]
        return sum(scores) / len(scores) if scores else 0.0
    
    def _calculate_complexity_distribution(self, analysis_results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calcular distribución de complejidad."""
        distribution = {}
        for result in analysis_results:
            complexity = result['analysis']['complexity']
            distribution[complexity] = distribution.get(complexity, 0) + 1
        return distribution


def get_ai_group_analyzer(config: Optional[ConfigManager] = None) -> AIGroupAnalyzer:
    """
    Obtener instancia singleton del analizador de grupos con IA.
    
    Args:
        config: Configuración opcional
        
    Returns:
        Instancia del analizador
    """
    if not hasattr(get_ai_group_analyzer, '_instance'):
        get_ai_group_analyzer._instance = AIGroupAnalyzer(config)
    return get_ai_group_analyzer._instance
