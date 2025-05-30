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
from src.utils.token_counter import AnthropicTokenCounter

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
        self.token_counter = AnthropicTokenCounter()
        
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
    
    def _analyze_group_files(self, project_path: str, group: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analizar todos los archivos de un grupo.
        
        Args:
            project_path: Ruta al proyecto
            group: Grupo a analizar
            
        Returns:
            Lista con análisis de cada archivo
        """
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
        
        files = group.get('files', [])
        analysis_results = []
        
        # Filtrar archivos válidos para análisis
        valid_files = self._filter_analyzable_files(project_path, files)
        
        if not valid_files:
            logger.warning("No hay archivos válidos para analizar en el grupo")
            return []
        
        total_files = len(valid_files)
        
        # Crear progreso con Rich
        from rich.console import Console
        console = Console()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            # Task para progreso general
            main_task = progress.add_task(f"📊 Analizando {total_files} archivos", total=total_files)
            
            # Task para lotes
            total_batches = (len(valid_files) + self.batch_size - 1) // self.batch_size
            batch_task = progress.add_task("🔄 Procesando lotes", total=total_batches)
            
            # Procesar archivos en lotes
            for i in range(0, len(valid_files), self.batch_size):
                batch = valid_files[i:i + self.batch_size]
                batch_num = (i // self.batch_size) + 1
                
                progress.update(batch_task, description=f"🔄 Lote {batch_num}/{total_batches} ({len(batch)} archivos)")
                
                # Analizar archivos del lote
                for file_info in batch:
                    try:
                        # Actualizar descripción con archivo actual
                        file_path = file_info.get('path', 'unknown')
                        progress.update(main_task, description=f"📄 Analizando: {os.path.basename(file_path)}")
                        
                        file_analysis = self._analyze_single_file(project_path, file_info)
                        if file_analysis:
                            analysis_results.append(file_analysis)
                        
                        # Actualizar progreso
                        progress.update(main_task, advance=1)
                        
                    except Exception as e:
                        logger.error(f"Error al analizar archivo {file_info.get('path', '')}: {e}")
                        progress.update(main_task, advance=1)
                        continue
                
                # Actualizar progreso de lotes
                progress.update(batch_task, advance=1)
                
                # Delay entre lotes para evitar rate limiting
                if i + self.batch_size < len(valid_files):
                    delay_task = progress.add_task(f"⏳ Esperando {self.analysis_delay}s", total=self.analysis_delay)
                    for _ in range(self.analysis_delay):
                        time.sleep(1)
                        progress.update(delay_task, advance=1)
                    progress.remove_task(delay_task)
        
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
            
            # Debug: log para verificar que se está llamando a la API
            logger.info(f"Analizando archivo {file_path} con IA (tamaño: {len(content)} chars)")
            
            # Solicitar análisis a Claude usando el método explain_code con prompt personalizado
            # Combine the analysis prompt with the code content for a comprehensive analysis
            combined_prompt = f"""Analiza este archivo {language} que forma parte de un grupo funcional:

Archivo: {file_path}

Por favor proporciona un análisis estructurado que incluya:

1. **Funcionalidad Principal**: ¿Qué hace este archivo?
2. **Responsabilidades**: Principales responsabilidades y propósito  
3. **Dependencias**: Qué librerías, módulos o archivos importa/usa
4. **Calidad del Código**: Evaluación de la calidad (1-10) con justificación
5. **Complejidad**: Nivel de complejidad (Baja/Media/Alta) y por qué
6. **Mantenibilidad**: Qué tan fácil es mantener este código
7. **Posibles Mejoras**: Sugerencias específicas para mejorar

Mantén el análisis conciso pero informativo.

CÓDIGO A ANALIZAR:
{content}"""
            
            result = self.ai_client.explain_code(combined_prompt, language, "standard", {
                "purpose": "file_analysis",
                "file_path": file_path
            })
            
            # Debug: log de la respuesta
            logger.info(f"Respuesta IA para {file_path}: success={result.get('success', False)}")
            
            if not result.get('success', False):
                logger.error(f"Error en análisis IA para {file_path}: {result.get('error', 'Unknown error')}")
                return None
            
            # Procesar y estructurar respuesta
            ai_content = result.get('explanation', result.get('content', result.get('message', '')))
            logger.info(f"Contenido AI recibido para {file_path}: {len(ai_content)} chars")
            
            analysis_data = self._parse_ai_analysis(file_path, ai_content, content)
            
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

Por favor proporciona un análisis estructurado que incluya EXACTAMENTE estos campos:

1. **Funcionalidad Específica**: Describe en UNA línea concisa qué hace específicamente este archivo (máximo 60 caracteres)
2. **Dependencias Internas**: Lista SOLO los archivos internos del proyecto que este archivo importa o usa (separa con comas)
3. **Dependencias Externas**: Lista SOLO las librerías externas que importa (separa con comas, máximo 3)
4. **Complejidad**: Clasifica como "Baja", "Media" o "Alta" basándote en:
   - Número de funciones/clases
   - Lógica de negocio
   - Manejo de errores
   - Interacciones con otros sistemas
5. **Responsabilidades Principales**: Enumera las 3 responsabilidades principales
6. **Mejoras Recomendadas**: Sugiere mejoras específicas para este archivo

Ejemplo de formato de respuesta:
**Funcionalidad Específica**: Gestiona autenticación de usuarios y tokens JWT
**Dependencias Internas**: auth_utils.py, models/user.py
**Dependencias Externas**: jwt, bcrypt, hashlib
**Complejidad**: Alta
**Responsabilidades Principales**: 
- Validar credenciales de usuario
- Generar y validar tokens JWT
- Gestionar sesiones de usuario
**Mejoras Recomendadas**:
- Separar lógica de tokens en clase independiente
- Agregar tests unitarios para cada función
- Mejorar manejo de errores específicos

Mantén cada sección concisa y específica."""
    
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
        
        # Extraer información específica usando el nuevo formato
        functionality = self._extract_section(ai_response, "Funcionalidad Específica")
        internal_deps = self._extract_section(ai_response, "Dependencias Internas")
        external_deps = self._extract_section(ai_response, "Dependencias Externas")
        complexity = self._extract_section(ai_response, "Complejidad")
        responsibilities = self._extract_section(ai_response, "Responsabilidades Principales")
        improvements = self._extract_section(ai_response, "Mejoras Recomendadas")
        
        # Procesar dependencias
        internal_dependencies = self._parse_dependencies_list(internal_deps)
        external_dependencies = self._parse_dependencies_list(external_deps)
        
        return {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'analysis': {
                'functionality': functionality,
                'internal_dependencies': internal_dependencies,
                'external_dependencies': external_dependencies,
                'complexity': complexity,
                'responsibilities': responsibilities,
                'improvements': improvements
            },
            'metrics': {
                'lines_of_code': lines_count,
                'character_count': char_count,
                'file_size_kb': round(char_count / 1024, 2)
            },
            'analysis_timestamp': datetime.now().isoformat(),
            'full_ai_response': ai_response
        }
    
    def _parse_dependencies_list(self, deps_text: str) -> List[str]:
        """
        Parsear lista de dependencias desde texto.
        
        Args:
            deps_text: Texto con dependencias separadas por comas
            
        Returns:
            Lista de dependencias limpias
        """
        if not deps_text or deps_text.strip() == "-" or "no" in deps_text.lower():
            return []
        
        # Limpiar y separar dependencias
        deps = [dep.strip() for dep in deps_text.split(',')]
        return [dep for dep in deps if dep and len(dep) > 1]
    
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
        output_dir = os.path.join(project_path, "project-output", "analyses", "functionality_groups")
        os.makedirs(output_dir, exist_ok=True)
        
        # Crear nombre de archivo seguro (sin timestamp para seguir el formato exacto requerido)
        safe_group_name = "".join(c for c in group['name'] if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_group_name = safe_group_name.replace(' ', '_')
        
        report_filename = f"{safe_group_name}.md"
        report_path = os.path.join(output_dir, report_filename)
        
        # Generar contenido del reporte con formato específico requerido
        content = self._create_structured_report_content(group, analysis_results, project_path)
        
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
        
        # Agregar tabla resumen simplificada
        if analysis_results:
            content.extend([
                "## 📋 Resumen de Análisis",
                "",
                "| Archivo | Funcionalidad | Mejoras Sugeridas |",
                "|---------|---------------|-------------------|"
            ])
            
            for result in analysis_results:
                file_name = result['file_name']
                functionality = self._truncate_text(result['analysis']['functionality'], 60)
                improvements = self._truncate_text(result['analysis']['suggested_improvements'], 60)
                
                content.append(
                    f"| `{file_name}` | {functionality} | {improvements} |"
                )
            
            content.extend(["", "---", ""])
        
        # Análisis detallado por archivo - Solo información útil
        content.extend([
            "## 🔍 Análisis Detallado por Archivo",
            ""
        ])
        
        for i, result in enumerate(analysis_results, 1):
            analysis = result['analysis']
            
            content.extend([
                f"### {i}. 📄 `{result['file_path']}`",
                "",
                f"**🎯 Funcionalidad Principal:**",
                f"{analysis['functionality']}",
                "",
                f"**🔗 Dependencias:**",
                f"{analysis['dependencies']}",
                "",
                f"**💡 Sugerencias de Mejora:**",
                f"{analysis['suggested_improvements']}",
                "",
                "---",
                ""
            ])
        
        # Footer
        content.extend([
            "",
            f"*Reporte generado por Project Prompt - Análisis IA con Anthropic Claude*",
            f"*Timestamp: {timestamp}*"
        ])
        
        return "\n".join(content)
    
    def _create_structured_report_content(self, group: Dict[str, Any], analysis_results: List[Dict[str, Any]], project_path: str) -> str:
        """
        Crear el contenido markdown del reporte con formato estructurado específico.
        
        Args:
            group: Información del grupo
            analysis_results: Resultados del análisis
            project_path: Ruta al proyecto
            
        Returns:
            Contenido markdown del reporte con formato específico
        """
        from datetime import datetime
        import os
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = [
            f"# Análisis del Grupo: {group['name']}",
            f"Fecha: {timestamp}",
            f"Archivos analizados: {len(analysis_results)}",
            "",
            "## Resumen del Grupo",
            "",
            self._generate_group_summary(group, analysis_results),
            "",
            "## Análisis Detallado por Archivo",
            "",
            "| Archivo | Funcionalidad Específica | Dependencias Internas | Dependencias Externas | Complejidad |",
            "|---------|--------------------------|----------------------|----------------------|-------------|"
        ]
        
        # Generar tabla con formato específico requerido
        for result in analysis_results:
            file_name = result['file_name']
            functionality = self._extract_specific_functionality(result['analysis'])
            internal_deps = self._extract_internal_dependencies(result['analysis'])
            external_deps = self._extract_external_dependencies(result['analysis'])
            complexity = self._extract_complexity_level(result['analysis'])
            
            content.append(
                f"| {file_name} | {functionality} | {internal_deps} | {external_deps} | {complexity} |"
            )
        
        content.extend([
            "",
            "## Conexiones y Dependencias",
            "",
            self._generate_dependency_diagram(analysis_results),
            "",
            "## Recomendaciones",
            "",
            self._generate_group_recommendations(analysis_results)
        ])
        
        return "\n".join(content)
    
    def _generate_group_summary(self, group: Dict[str, Any], analysis_results: List[Dict[str, Any]]) -> str:
        """Generar resumen general del grupo."""
        functionalities = []
        for result in analysis_results:
            functionality = self._extract_specific_functionality(result['analysis'])
            if functionality and functionality != "Sin especificar":
                functionalities.append(functionality)
        
        if functionalities:
            main_purpose = f"Este grupo se encarga principalmente de: {', '.join(functionalities[:3])}."
        else:
            main_purpose = f"Grupo funcional '{group['name']}' que contiene {len(analysis_results)} archivos."
        
        return main_purpose
    
    def _extract_specific_functionality(self, analysis: Dict[str, Any]) -> str:
        """Extraer funcionalidad específica del análisis."""
        if isinstance(analysis, dict):
            functionality = analysis.get('functionality', '')
            if isinstance(functionality, str) and len(functionality) > 50:
                # Truncar funcionalidad si es muy larga
                return functionality[:47] + "..."
            return functionality or "Sin especificar"
        return "Sin especificar"
    
    def _extract_internal_dependencies(self, analysis: Dict[str, Any]) -> str:
        """Extraer dependencias internas del análisis."""
        if isinstance(analysis, dict):
            deps = analysis.get('internal_dependencies', [])
            if isinstance(deps, list) and deps:
                return ", ".join(deps[:3])  # Máximo 3 dependencias
            elif isinstance(deps, str):
                return deps
        return "-"
    
    def _extract_external_dependencies(self, analysis: Dict[str, Any]) -> str:
        """Extraer dependencias externas del análisis."""
        if isinstance(analysis, dict):
            deps = analysis.get('external_dependencies', [])
            if isinstance(deps, list) and deps:
                return ", ".join(deps[:3])  # Máximo 3 dependencias
            elif isinstance(deps, str):
                return deps
        return "-"
    
    def _extract_complexity_level(self, analysis: Dict[str, Any]) -> str:
        """Extraer nivel de complejidad del análisis."""
        if isinstance(analysis, dict):
            complexity = analysis.get('complexity', '')
            if complexity:
                return complexity
            # Intentar inferir complejidad por palabras clave
            text = str(analysis)
            if 'alta' in text.lower() or 'complex' in text.lower():
                return "Alta"
            elif 'media' in text.lower() or 'medium' in text.lower():
                return "Media"
            elif 'baja' in text.lower() or 'low' in text.lower():
                return "Baja"
        return "Media"
    
    def _generate_dependency_diagram(self, analysis_results: List[Dict[str, Any]]) -> str:
        """Generar diagrama textual de dependencias."""
        lines = []
        for result in analysis_results:
            file_name = result['file_name']
            internal_deps = self._extract_internal_dependencies(result['analysis'])
            if internal_deps and internal_deps != "-":
                lines.append(f"- `{file_name}` → {internal_deps}")
        
        if lines:
            return "\n".join(lines)
        else:
            return "No se detectaron dependencias internas complejas entre los archivos del grupo."
    
    def _generate_group_recommendations(self, analysis_results: List[Dict[str, Any]]) -> str:
        """Generar recomendaciones basadas en el análisis."""
        recommendations = []
        
        # Analizar patrones comunes
        high_complexity_files = []
        files_with_many_deps = []
        
        for result in analysis_results:
            complexity = self._extract_complexity_level(result['analysis'])
            if complexity == "Alta":
                high_complexity_files.append(result['file_name'])
                
            internal_deps = self._extract_internal_dependencies(result['analysis'])
            if internal_deps and len(internal_deps.split(',')) > 2:
                files_with_many_deps.append(result['file_name'])
        
        if high_complexity_files:
            recommendations.append(f"- **Refactorización de complejidad**: Los archivos {', '.join(high_complexity_files)} presentan alta complejidad y podrían beneficiarse de modularización.")
        
        if files_with_many_deps:
            recommendations.append(f"- **Reducción de dependencias**: Considerar simplificar las dependencias en {', '.join(files_with_many_deps)} para mejorar la mantenibilidad.")
        
        if len(analysis_results) > 5:
            recommendations.append("- **Organización**: El grupo contiene muchos archivos. Considerar subdividir en grupos más pequeños para mejor organización.")
        
        recommendations.append("- **Documentación**: Agregar documentación específica sobre las responsabilidades y interfaces de cada archivo.")
        recommendations.append("- **Testing**: Implementar tests unitarios específicos para cada funcionalidad identificada.")
        
        return "\n".join(recommendations)
                for dep in deps:
                    content.append(f"- {dep}")
            else:
                content.append("- Ninguna dependencia crítica identificada")
            
            content.extend([
                "",
                f"**Puntos de Mejora:**",
            ])
            
            # Extraer mejoras sugeridas
            improvements = self._parse_improvements_from_analysis(analysis)
            if improvements:
                for improvement in improvements:
                    content.append(f"- {improvement}")
            else:
                content.append("- No se identificaron mejoras específicas")
            
            content.extend([
                "",
                f"**Nivel de Complejidad:** {self._assess_complexity(analysis)}",
                f"**Prioridad de Refactoring:** {self._assess_refactoring_priority(analysis)}",
                "",
                "---",
                ""
            ])
        
        # Sección de dependencias del grupo
        content.extend([
            "## Dependencias del Grupo",
            "",
            "### Dependencias Internas",
        ])
        
        internal_deps = self._identify_internal_dependencies(analysis_results)
        if internal_deps:
            for dep in internal_deps:
                content.append(f"- {dep}")
        else:
            content.append("- No se identificaron dependencias internas críticas")
        
        content.extend([
            "",
            "### Dependencias Externas",
        ])
        
        external_deps = self._identify_external_dependencies(analysis_results)
        if external_deps:
            for dep in external_deps:
                content.append(f"- {dep}")
        else:
            content.append("- No se identificaron dependencias externas críticas")
        
        # Recomendaciones finales
        content.extend([
            "",
            "## Recomendaciones Generales",
            "",
            "### Mejoras de Arquitectura",
        ])
        
        arch_recommendations = self._generate_architecture_recommendations(group, analysis_results)
        for rec in arch_recommendations:
            content.append(f"- {rec}")
        
        content.extend([
            "",
            "### Mejoras de Código",
        ])
        
        code_recommendations = self._generate_code_recommendations(analysis_results)
        for rec in code_recommendations:
            content.append(f"- {rec}")
        
        content.extend([
            "",
            "### Próximos Pasos Sugeridos",
            "",
            "1. **Fase 1:** Implementar mejoras de calidad de código identificadas",
            "2. **Fase 2:** Refactorizar componentes con alta complejidad",
            "3. **Fase 3:** Optimizar dependencias y arquitectura",
            "4. **Fase 4:** Implementar patrones de diseño recomendados",
            "",
            "---",
            "",
            f"*Reporte generado el {timestamp} por ProjectPrompt AI Analyzer*"
        ])
        
        return "\n".join(content)
    
    def _extract_main_functionality(self, analysis: dict) -> str:
        """Extraer la funcionalidad principal de un análisis."""
        functionality = analysis.get('functionality', '')
        if len(functionality) > 60:
            return functionality[:57] + "..."
        return functionality or "No especificada"
    
    def _extract_dependencies(self, analysis: dict) -> str:
        """Extraer dependencias clave del análisis."""
        # Buscar menciones de imports, requires, etc.
        text = str(analysis.get('technical_details', '')) + str(analysis.get('functionality', ''))
        deps = []
        
        # Patrones comunes de dependencias
        import_patterns = ['import ', 'from ', 'require(', 'include ', '#include']
        for pattern in import_patterns:
            if pattern in text.lower():
                deps.append("Múltiples")
                break
        
        if not deps:
            deps.append("Mínimas")
            
        return ", ".join(deps[:3])  # Máximo 3 dependencias mostradas
    
    def _extract_quality_score(self, analysis: dict) -> str:
        """Extraer puntuación de calidad del análisis."""
        # Buscar puntuaciones numéricas en el análisis
        text = str(analysis)
        scores = []
        
        # Buscar patrones de puntuación
        import re
        score_patterns = [
            r'(\d+)/10',
            r'score[:\s]*(\d+)',
            r'quality[:\s]*(\d+)',
            r'rating[:\s]*(\d+)'
        ]
        
        for pattern in score_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                scores.extend([int(m) for m in matches if m.isdigit()])
        
        if scores:
            avg_score = sum(scores) / len(scores)
            if avg_score >= 8:
                return f"Alta ({avg_score:.1f}/10)"
            elif avg_score >= 6:
                return f"Media ({avg_score:.1f}/10)"
            else:
                return f"Baja ({avg_score:.1f}/10)"
        
        # Análisis heurístico basado en palabras clave
        text_lower = text.lower()
        if any(word in text_lower for word in ['excellent', 'good', 'well', 'clean']):
            return "Alta"
        elif any(word in text_lower for word in ['improve', 'refactor', 'fix', 'issue']):
            return "Media"
        else:
            return "Por evaluar"
    
    def _extract_key_recommendations(self, analysis: dict) -> str:
        """Extraer recomendaciones clave del análisis."""
        improvements = analysis.get('suggested_improvements', '')
        if len(improvements) > 50:
            return improvements[:47] + "..."
        return improvements or "Ninguna"
    
    def _parse_dependencies_from_analysis(self, analysis: dict) -> List[str]:
        """Extraer lista de dependencias del análisis."""
        deps = []
        text = str(analysis.get('technical_details', '')) + str(analysis.get('functionality', ''))
        
        # Buscar menciones específicas de librerías/módulos
        common_deps = [
            'os', 'sys', 'json', 'datetime', 'pathlib', 'typing',
            'requests', 'numpy', 'pandas', 'flask', 'django',
            'fastapi', 'sqlalchemy', 'pytest', 'logging'
        ]
        
        for dep in common_deps:
            if dep in text.lower():
                deps.append(f"Módulo {dep}")
        
        # Si no se encontraron dependencias específicas, agregar genéricas
        if not deps:
            if 'import' in text.lower():
                deps.append("Dependencias estándar de Python")
            else:
                deps.append("Sin dependencias externas identificadas")
        
        return deps[:5]  # Máximo 5 dependencias
    
    def _parse_improvements_from_analysis(self, analysis: dict) -> List[str]:
        """Extraer lista de mejoras del análisis."""
        improvements_text = analysis.get('suggested_improvements', '')
        if not improvements_text:
            return []
        
        # Dividir por puntos o líneas
        improvements = []
        
        # Intentar dividir por números o bullets
        import re
        lines = re.split(r'[.\n]|\d+\.', improvements_text)
        
        for line in lines:
            line = line.strip()
            if len(line) > 10:  # Filtrar líneas muy cortas
                improvements.append(line[:80] + ("..." if len(line) > 80 else ""))
        
        return improvements[:4]  # Máximo 4 mejoras
    
    def _assess_complexity(self, analysis: dict) -> str:
        """Evaluar el nivel de complejidad basado en el análisis."""
        text = str(analysis).lower()
        
        # Indicadores de alta complejidad
        high_complexity_indicators = [
            'complex', 'complicated', 'intricate', 'nested',
            'multiple inheritance', 'deep hierarchy', 'coupling'
        ]
        
        # Indicadores de baja complejidad
        low_complexity_indicators = [
            'simple', 'straightforward', 'basic', 'minimal',
            'clean', 'clear', 'direct'
        ]
        
        high_score = sum(1 for indicator in high_complexity_indicators if indicator in text)
        low_score = sum(1 for indicator in low_complexity_indicators if indicator in text)
        
        if high_score > low_score:
            return "Alta"
        elif low_score > high_score:
            return "Baja"
        else:
            return "Media"
    
    def _assess_refactoring_priority(self, analysis: dict) -> str:
        """Evaluar la prioridad de refactoring."""
        improvements = analysis.get('suggested_improvements', '').lower()
        
        # Indicadores de alta prioridad
        high_priority_words = [
            'critical', 'urgent', 'important', 'must', 'should',
            'refactor', 'rewrite', 'fix', 'issue', 'problem'
        ]
        
        priority_score = sum(1 for word in high_priority_words if word in improvements)
        
        if priority_score >= 3:
            return "Alta"
        elif priority_score >= 1:
            return "Media"
        else:
            return "Baja"
    
    def _identify_internal_dependencies(self, analysis_results: List[Dict[str, Any]]) -> List[str]:
        """Identificar dependencias internas entre archivos del grupo."""
        deps = []
        file_names = [result['file_name'] for result in analysis_results]
        
        for result in analysis_results:
            text = str(result['analysis'])
            for other_file in file_names:
                if other_file != result['file_name'] and other_file.replace('.py', '') in text:
                    deps.append(f"{result['file_name']} → {other_file}")
        
        return list(set(deps))[:8]  # Eliminar duplicados y limitar
    
    def _identify_external_dependencies(self, analysis_results: List[Dict[str, Any]]) -> List[str]:
        """Identificar dependencias externas del grupo."""
        deps = set()
        
        for result in analysis_results:
            text = str(result['analysis']).lower()
            
            # Librerías comunes
            external_libs = [
                'requests', 'numpy', 'pandas', 'flask', 'django',
                'fastapi', 'sqlalchemy', 'pytest', 'click', 'typer',
                'rich', 'anthropic', 'openai'
            ]
            
            for lib in external_libs:
                if lib in text:
                    deps.add(f"Librería {lib}")
        
        return list(deps)[:10]
    
    def _generate_architecture_recommendations(self, group: Dict[str, Any], analysis_results: List[Dict[str, Any]]) -> List[str]:
        """Generar recomendaciones de arquitectura."""
        recommendations = []
        
        # Basado en el número de archivos
        if len(analysis_results) > 10:
            recommendations.append("Considerar dividir el grupo en subgrupos más pequeños")
        
        # Basado en dependencias
        internal_deps = self._identify_internal_dependencies(analysis_results)
        if len(internal_deps) > 5:
            recommendations.append("Reducir el acoplamiento entre módulos")
        
        # Recomendaciones generales
        recommendations.extend([
            "Implementar patrones de diseño apropiados para el dominio",
            "Evaluar la separación de responsabilidades",
            "Considerar la aplicación de principios SOLID"
        ])
        
        return recommendations[:5]
    
    def _generate_code_recommendations(self, analysis_results: List[Dict[str, Any]]) -> List[str]:
        """Generar recomendaciones de código."""
        recommendations = []
        
        # Analizar patrones comunes en las mejoras sugeridas
        all_improvements = []
        for result in analysis_results:
            improvements = result['analysis'].get('suggested_improvements', '')
            all_improvements.append(improvements.lower())
        
        combined_text = ' '.join(all_improvements)
        
        # Recomendaciones basadas en patrones
        if 'documentation' in combined_text or 'comment' in combined_text:
            recommendations.append("Mejorar documentación y comentarios")
        
        if 'test' in combined_text:
            recommendations.append("Incrementar cobertura de pruebas")
        
        if 'error' in combined_text or 'exception' in combined_text:
            recommendations.append("Mejorar manejo de errores")
        
        if 'performance' in combined_text or 'optimization' in combined_text:
            recommendations.append("Optimizar rendimiento")
        
        # Recomendaciones generales
        recommendations.extend([
            "Aplicar estándares de codificación consistentes",
            "Implementar logging adecuado",
            "Validar entradas y salidas"
        ])
        
        return recommendations[:6]

    # ...existing code...


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
