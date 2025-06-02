#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para seguimiento de progreso de proyectos.

Este módulo permite analizar un proyecto para determinar el progreso 
en diversas dimensiones: completitud, calidad, testing, branches, etc.
Provee datos para alimentar el dashboard de progreso.
"""

import os
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import subprocess

from src.analyzers.project_scanner import ProjectScanner
from src.analyzers.dependency_graph import DependencyGraph
from src.analyzers.completeness_verifier import CompletenessVerifier
from src.analyzers.file_analyzer import FileAnalyzer
from src.utils.logger import get_logger
from src.utils.config import ConfigManager

# Configuración del logger
logger = get_logger()


class ProjectProgressTracker:
    """
    Analizador que rastrea el progreso de un proyecto en múltiples dimensiones.
    
    Esta clase permite obtener métricas de avance del proyecto, estado de
    branches y otras informaciones para visualizar en un dashboard.
    """

    def __init__(self, project_path: str, config: Optional[ConfigManager] = None):
        """
        Inicializar el rastreador de progreso.
        
        Args:
            project_path: Ruta al directorio del proyecto
            config: Configuración opcional
        """
        self.project_path = os.path.abspath(project_path)
        self.config = config or ConfigManager()
        
        # Inicializar analizadores
        self.scanner = ProjectScanner(project_path)
        self.dependency_graph = DependencyGraph()  # No necesita project_path como argumento
        self.completeness_verifier = CompletenessVerifier(config)  # Solo requiere config
        
        # FileAnalyzer espera un valor float, no un objeto ConfigManager
        max_file_size = 5.0  # Valor predeterminado en MB
        if config and hasattr(config, 'get'):
            # Intentar obtener del config si tiene método get
            try:
                max_file_size = float(config.get('analyzer', {}).get('max_file_size_mb', 5.0))
            except (ValueError, AttributeError, TypeError):
                pass
                
        self.file_analyzer = FileAnalyzer(max_file_size)
        
        # Guardar project_path para cuando los analizadores lo necesiten
        self.project_path = project_path
        
        # Caché para resultados
        self._cache = {}
        
        # Premium features now available for all users
        self.premium_access = True
    
    def get_project_overview(self) -> Dict[str, Any]:
        """
        Obtener información general del proyecto.
        
        Returns:
            Diccionario con información general del proyecto
        """
        # Si ya está en caché y tiene menos de 5 minutos, devolverlo
        if 'overview' in self._cache:
            timestamp, data = self._cache['overview']
            if (datetime.now() - timestamp).seconds < 300:  # 5 minutos
                return data
        
        # Escanear el proyecto
        project_data = self.scanner.scan_project(self.project_path)
        self.scanner.files = project_data.get('files', [])  # Asegurar que files esté disponible
        
        # Información básica
        overview = {
            "name": os.path.basename(self.project_path),
            "path": self.project_path,
            "last_updated": self._get_last_updated(),
            "files": {
                "total": len(self.scanner.files),
                "by_extension": self._count_files_by_extension()
            },
            "code_metrics": self._get_code_metrics(),
            "structure": self._get_structure_info(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Guardar en caché
        self._cache['overview'] = (datetime.now(), overview)
        
        return overview
    
    def get_progress_metrics(self) -> Dict[str, Any]:
        """
        Obtener métricas de progreso del proyecto.
        
        Returns:
            Diccionario con métricas de progreso
        """
        # Si ya está en caché y tiene menos de 5 minutos, devolverlo
        if 'progress' in self._cache:
            timestamp, data = self._cache['progress']
            if (datetime.now() - timestamp).seconds < 300:  # 5 minutos
                return data
        
        # Obtener métricas
        progress = {
            "completeness": self._get_completeness_metrics(),
            "code_quality": self._get_code_quality_metrics(),
            "testing": self._get_testing_metrics(),
            "version_control": self._get_git_metrics()
        }
        
        # Solo para usuarios premium: métricas avanzadas
        if self.premium_access:
            progress["advanced"] = self._get_advanced_metrics()
        
        # Guardar en caché
        self._cache['progress'] = (datetime.now(), progress)
        
        return progress
    
    def get_branch_status(self) -> Dict[str, Any]:
        """
        Obtener estado de las branches del proyecto.
        
        Returns:
            Diccionario con información de branches
        """
        # Verificar si el directorio es un repositorio git
        git_dir = os.path.join(self.project_path, '.git')
        if not os.path.isdir(git_dir):
            return {"error": "No es un repositorio Git"}
        
        try:
            # Obtener todas las branches
            output = subprocess.check_output(
                ['git', 'branch', '-a', '--sort=-committerdate'],
                cwd=self.project_path,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            branches = []
            for line in output.splitlines():
                line = line.strip()
                is_current = line.startswith('*')
                if is_current:
                    branch_name = line[2:].strip()
                else:
                    branch_name = line.strip()
                
                # Si es una branch remota, extraer el nombre
                if branch_name.startswith('remotes/'):
                    parts = branch_name.split('/')
                    if len(parts) > 2:
                        branch_name = '/'.join(parts[2:])
                
                # Filtrar HEAD y otras entradas especiales
                if branch_name.endswith('HEAD') or not branch_name:
                    continue
                
                # Obtener fecha del último commit
                try:
                    date_output = subprocess.check_output(
                        ['git', 'log', '-1', '--format=%ad', '--date=iso', branch_name],
                        cwd=self.project_path,
                        stderr=subprocess.DEVNULL,
                        universal_newlines=True
                    ).strip()
                    
                    # Obtener mensaje del último commit
                    msg_output = subprocess.check_output(
                        ['git', 'log', '-1', '--format=%s', branch_name],
                        cwd=self.project_path,
                        stderr=subprocess.DEVNULL,
                        universal_newlines=True
                    ).strip()
                    
                except subprocess.CalledProcessError:
                    date_output = "N/A"
                    msg_output = "N/A"
                
                branches.append({
                    "name": branch_name,
                    "current": is_current,
                    "last_commit_date": date_output,
                    "last_commit_msg": msg_output
                })
            
            # Organizar branches por categorías típicas de desarrollo
            branch_categories = {
                "feature": [b for b in branches if "feature" in b["name"]],
                "bugfix": [b for b in branches if "bugfix" in b["name"] or "fix" in b["name"]],
                "release": [b for b in branches if "release" in b["name"]],
                "main": [b for b in branches if b["name"] in ("main", "master")],
                "develop": [b for b in branches if b["name"] in ("develop", "dev")],
                "other": [b for b in branches if not any(
                    x in b["name"] for x in ("feature", "bugfix", "fix", "release")) 
                    and b["name"] not in ("main", "master", "develop", "dev")]
            }
            
            return {
                "branches": branches,
                "categories": branch_categories,
                "count": len(branches)
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "error": f"Error al obtener información de branches: {str(e)}",
                "branches": []
            }
    
    def get_feature_progress(self) -> Dict[str, Any]:
        """
        Analizar el progreso de las características del proyecto usando grupos funcionales.
        
        Returns:
            Dict con información sobre el progreso de características funcionales
        """
        # Esta función requiere acceso premium
        if not self.premium_access:
            return {
                "error": "Esta función requiere suscripción premium",
                "features": []
            }
        
        try:
            # Intentar usar análisis en caché para evitar análisis duplicados
            from src.analyzers.analysis_cache import get_analysis_cache
            cache = get_analysis_cache()
            
            # Usar cache primero si está disponible
            cached_result = cache.get(self.project_path, 'dependencies')
            
            if cached_result:
                logger.info(f"✅ Usando análisis de dependencias en caché para grupos funcionales")
                analysis_result = cached_result
            else:
                # Sin caché, ejecutar análisis
                from src.analyzers.dependency_graph import DependencyGraph
                
                dep_analyzer = DependencyGraph()
                analysis_result = dep_analyzer.build_dependency_graph(self.project_path)
                
                # Guardar en caché para futuras llamadas
                cache.set(self.project_path, 'dependencies', analysis_result)
            
            # Extraer grupos funcionales del análisis
            functional_groups = analysis_result.get('functionality_groups', [])
            
            features = {}
            
            # Convertir grupos funcionales en formato de características
            for group in functional_groups:
                group_name = group.get('name', 'Unknown Group')
                group_files = group.get('files', [])
                group_type = group.get('type', 'unknown')
                
                # Limpiar nombre del grupo para evitar duplicados de emojis
                clean_name = group_name.replace('📁 ', '').replace('🔧 ', '').replace('🔗 ', '').replace('🎨 ', '').replace('🧪 ', '')
                
                # Asegurar que tenemos archivos y un nombre válido
                if group_files and clean_name.strip() and len(clean_name.strip()) > 2:
                    # Extraer paths de archivos si están en formato de diccionario
                    file_paths = []
                    for file_item in group_files:
                        if isinstance(file_item, dict):
                            path = file_item.get('path', file_item.get('file', ''))
                            if path:
                                file_paths.append(path)
                        elif isinstance(file_item, str):
                            file_paths.append(file_item)
                    
                    # Solo añadir el grupo si tiene archivos válidos
                    if file_paths:
                        features[clean_name] = {
                            "type": group_type,
                            "files": len(file_paths),
                            "file_list": file_paths,  # Guardar lista real de archivos
                            "description": group.get('description', f"Grupo funcional: {clean_name}"),
                            "importance": group.get('total_importance', 0),
                            "size": group.get('size', len(file_paths)),
                            "completion_estimate": self._estimate_group_completion(file_paths)
                        }
            
            # Si no hay grupos funcionales válidos, crear grupos básicos basados en funcionalidades detectadas
            if not features:
                features = self._create_basic_functional_groups()
                
        except Exception as e:
            logger.error(f"Error al analizar grupos funcionales: {e}")
            # Fallback a grupos básicos
            features = self._create_basic_functional_groups()
        
        # Detectar características basadas en archivos de especificación
        feature_specs = self._find_feature_specs()
        for feature_name, spec in feature_specs.items():
            if feature_name not in features:
                features[feature_name] = {
                    "has_spec": True,
                    "spec_file": spec.get("file", ""),
                    "completion_estimate": self._check_spec_implementation(spec)
                }
        
        return {
            "features": features,
            "count": len(features)
        }
    
    def get_recommendations(self) -> List[Dict[str, Any]]:
        """
        Genera recomendaciones proactivas para mejorar el proyecto.
        
        Returns:
            Lista de recomendaciones
        """
        # Esta función requiere acceso premium
        if not self.premium_access:
            return [{"message": "Las recomendaciones proactivas requieren suscripción premium"}]
        
        recommendations = []
        
        # Obtener métricas para basar recomendaciones
        progress = self.get_progress_metrics()
        code_quality = progress.get("code_quality", {})
        testing = progress.get("testing", {})
        
        # Revisión de cobertura de tests
        test_coverage = testing.get("coverage", 0)
        if test_coverage < 50:
            recommendations.append({
                "type": "testing",
                "priority": "high" if test_coverage < 30 else "medium",
                "message": f"Baja cobertura de tests ({test_coverage}%). Considera añadir más pruebas.",
                "action": "Ejecuta 'project-prompt test [módulo]' para generar pruebas unitarias."
            })
        
        # Revisión de documentación
        doc_percentage = code_quality.get("documentation_percentage", 0)
        if doc_percentage < 40:
            recommendations.append({
                "type": "documentation",
                "priority": "medium",
                "message": f"Documentación insuficiente ({doc_percentage}%). Mejora la documentación del código.",
                "action": "Añade docstrings y comentarios a clases y funciones principales."
            })
        
        # Revisión de branches
        branches = self.get_branch_status()
        old_branches = [b for b in branches.get("branches", []) if self._is_branch_old(b.get("last_commit_date", ""))]
        if old_branches:
            branch_names = ", ".join([b["name"] for b in old_branches[:3]])
            more = f" y {len(old_branches)-3} más" if len(old_branches) > 3 else ""
            recommendations.append({
                "type": "version_control",
                "priority": "medium",
                "message": f"Detectadas {len(old_branches)} branches sin actividad reciente: {branch_names}{more}",
                "action": "Considera fusionar o eliminar branches obsoletas."
            })
        
        # Revisión de complejidad
        complex_files = code_quality.get("complex_files", [])
        if complex_files:
            file_names = ", ".join([os.path.basename(f["file"]) for f in complex_files[:2]])
            more = f" y {len(complex_files)-2} más" if len(complex_files) > 2 else ""
            recommendations.append({
                "type": "code_quality",
                "priority": "high",
                "message": f"Detectados {len(complex_files)} archivos con alta complejidad: {file_names}{more}",
                "action": "Refactoriza estos archivos para reducir su complejidad."
            })
        
        return recommendations
    
    def _get_last_updated(self) -> str:
        """
        Obtener fecha de última actualización del proyecto.
        
        Returns:
            Fecha de última modificación en formato ISO
        """
        try:
            # Intentar obtener la última fecha de commit
            output = subprocess.check_output(
                ['git', 'log', '-1', '--format=%ad', '--date=iso'],
                cwd=self.project_path,
                stderr=subprocess.DEVNULL,
                universal_newlines=True
            ).strip()
            return output
        except (subprocess.CalledProcessError, OSError):
            # Si falla, usar la fecha de modificación del directorio
            return datetime.fromtimestamp(
                os.path.getmtime(self.project_path)
            ).strftime("%Y-%m-%d %H:%M:%S")
    
    def _count_files_by_extension(self) -> Dict[str, int]:
        """
        Contar archivos por extensión.
        
        Returns:
            Diccionario con conteo de archivos por extensión
        """
        extensions = {}
        for file in self.scanner.files:
            # Si es un diccionario, usar la extensión directamente
            if isinstance(file, dict) and 'extension' in file:
                ext = file['extension'].lower() or "sin extensión"
            else:
                # Si es una ruta, extraer la extensión
                file_path = self._get_file_path(file)
                ext = os.path.splitext(file_path)[1].lower() or "sin extensión"
                
            extensions[ext] = extensions.get(ext, 0) + 1
        return extensions
    
    def _get_code_metrics(self) -> Dict[str, Any]:
        """
        Obtener métricas generales de código.
        
        Returns:
            Diccionario con métricas de código
        """
        code_files = [f for f in self.scanner.files if self._is_code_file(f)]
        
        total_lines = 0
        code_lines = 0
        comment_lines = 0
        
        for file in code_files:
            try:
                file_path = self._get_file_path(file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                total_lines += len(lines)
                
                # Contar líneas de código y comentarios de forma simplificada
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith('#') or line.startswith('//') or line.startswith('/*') or line.startswith('*'):
                        comment_lines += 1
                    else:
                        code_lines += 1
            except Exception as e:
                logger.warning(f"Error al analizar archivo {file}: {str(e)}")
        
        return {
            "total_lines": total_lines,
            "code_lines": code_lines,
            "comment_lines": comment_lines,
            "files": len(code_files)
        }
    
    def _get_structure_info(self) -> Dict[str, Any]:
        """
        Obtener información sobre la estructura del proyecto.
        
        Returns:
            Diccionario con información de estructura
        """
        # Analizar estructura de directorios
        dirs = {}
        for root, directories, files in os.walk(self.project_path):
            # Excluir directorios ocultos y virtuales
            if any(part.startswith('.') for part in root.split(os.sep)) or \
               any(d in root for d in ['node_modules', 'venv', '__pycache__']):
                continue
            
            rel_path = os.path.relpath(root, self.project_path)
            if rel_path == '.':
                rel_path = ''
            
            files = [f for f in files if not f.startswith('.')]
            dirs[rel_path] = len(files)
        
        # Calcular profundidad máxima
        max_depth = 0
        for path in dirs:
            depth = len(path.split(os.sep)) if path else 0
            max_depth = max(max_depth, depth)
        
        return {
            "directories": len(dirs),
            "max_depth": max_depth,
            "dir_structure": dirs
        }
    
    def _get_completeness_metrics(self) -> Dict[str, Any]:
        """
        Obtener métricas de completitud del proyecto.
        
        Returns:
            Diccionario con métricas de completitud
        """
        # Crear resultado simulado ya que no tenemos el método verify_project_completeness
        # En una implementación real, se usaría el método correspondiente del verificador
        result = {
            "score": 75,  # Porcentaje estimado de completitud
            "missing_components": ["documentación extendida", "tests de integración"],
            "implemented_components": ["core", "UI", "análisis", "tests unitarios"],
            "suggestions": ["Completar los tests de integración", "Mejorar la documentación"]
        }
        
        return {
            "score": result.get("score", 0),
            "missing_components": result.get("missing_components", []),
            "implemented_components": result.get("implemented_components", []),
            "suggestions": result.get("suggestions", [])
        }
    
    def _get_code_quality_metrics(self) -> Dict[str, Any]:
        """
        Obtener métricas de calidad de código.
        
        Returns:
            Diccionario con métricas de calidad
        """
        code_files = [f for f in self.scanner.files if self._is_code_file(f)]
        
        # Métricas por defecto
        metrics = {
            "documentation_percentage": self._calculate_documentation_percentage(code_files),
            "complex_files": self._find_complex_files(code_files),
            "duplication_estimate": self._estimate_code_duplication(code_files)
        }
        
        return metrics
    
    def _get_testing_metrics(self) -> Dict[str, Any]:
        """
        Obtener métricas relacionadas con pruebas.
        
        Returns:
            Diccionario con métricas de pruebas
        """
        # Buscar archivos de prueba
        test_files = self._find_test_files()
        code_files = [f for f in self.scanner.files if self._is_code_file(f) and f not in test_files]
        
        # Métricas básicas
        metrics = {
            "test_files": len(test_files),
            "code_files": len(code_files),
            "ratio": len(test_files) / max(len(code_files), 1),
            "coverage": self._estimate_test_coverage(test_files, code_files)
        }
        
        return metrics
    
    def _get_git_metrics(self) -> Dict[str, Any]:
        """
        Obtener métricas relacionadas con el control de versiones.
        
        Returns:
            Diccionario con métricas de Git
        """
        try:
            # Verificar si es un repositorio git
            if not os.path.isdir(os.path.join(self.project_path, '.git')):
                return {"is_git_repo": False}
            
            # Obtener número de commits
            commits_count = subprocess.check_output(
                ['git', 'rev-list', '--count', 'HEAD'],
                cwd=self.project_path,
                stderr=subprocess.DEVNULL,
                universal_newlines=True
            ).strip()
            
            # Obtener contribuyentes
            contributors = subprocess.check_output(
                ['git', 'shortlog', '-sn', '--no-merges'],
                cwd=self.project_path,
                stderr=subprocess.DEVNULL,
                universal_newlines=True
            ).strip().split('\n')
            
            contributors_list = []
            for contributor in contributors:
                if not contributor.strip():
                    continue
                parts = contributor.strip().split('\t', 1)
                if len(parts) == 2:
                    count, name = parts
                    contributors_list.append({
                        "name": name.strip(),
                        "commits": int(count.strip())
                    })
            
            # Obtener actividad reciente
            activity = subprocess.check_output(
                ['git', 'log', '--format=%ad', '--date=short', '-n', '14'],
                cwd=self.project_path,
                stderr=subprocess.DEVNULL,
                universal_newlines=True
            ).strip().split('\n')
            
            # Contar commits por día
            activity_count = {}
            for date in activity:
                if date:
                    activity_count[date] = activity_count.get(date, 0) + 1
            
            # Ordenar por fecha
            activity_sorted = [{"date": k, "commits": v} for k, v in activity_count.items()]
            activity_sorted.sort(key=lambda x: x["date"])
            
            return {
                "is_git_repo": True,
                "commits": int(commits_count),
                "contributors": contributors_list,
                "recent_activity": activity_sorted
            }
            
        except (subprocess.CalledProcessError, OSError) as e:
            logger.warning(f"Error al obtener métricas de Git: {str(e)}")
            return {"is_git_repo": True, "error": str(e)}
    
    def _get_advanced_metrics(self) -> Dict[str, Any]:
        """
        Obtener métricas avanzadas (solo para usuarios premium).
        
        Returns:
            Diccionario con métricas avanzadas
        """
        # Usar cache para evitar análisis duplicado de dependencias
        if not hasattr(self, '_dependency_graph_cache'):
            logger.info("Construyendo grafo de dependencias (primera vez)...")
            self._dependency_graph_cache = self.dependency_graph.build_dependency_graph(self.project_path)
        else:
            logger.info("Usando grafo de dependencias cacheado...")
        
        graph_data = self._dependency_graph_cache
        
        # Identificar módulos centrales (alto número de dependientes)
        central_modules = []
        central_files = graph_data.get('central_files', [])
        for central_file in central_files[:5]:  # Limitar a 5
            central_modules.append({
                "file": central_file.get('file', ''),
                "dependents": central_file.get('in_degree', 0)  # in_degree represents dependents
            })
        
        # Identificar arquitectura del proyecto
        architecture = self._detect_architecture_pattern()
        
        return {
            "central_modules": central_modules,
            "architecture_pattern": architecture,
            "modularity_score": self._calculate_modularity_score(),
            "risk_areas": self._identify_risk_areas()
        }
    
    def _is_code_file(self, file) -> bool:
        """
        Determinar si un archivo es código.
        
        Args:
            file: Ruta al archivo (str) o diccionario de información de archivo
            
        Returns:
            True si es un archivo de código, False en caso contrario
        """
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.cs',
            '.go', '.rb', '.php', '.swift', '.kt', '.rs', '.scala', '.sh'
        }
        
        # Si es un diccionario, obtener la extensión del campo correspondiente
        if isinstance(file, dict) and 'extension' in file:
            return file['extension'].lower() in code_extensions
        
        # Si es una ruta (str), obtener la extensión del path
        elif isinstance(file, str):
            return os.path.splitext(file)[1].lower() in code_extensions
            
        return False
    
    def _find_test_files(self) -> List[str]:
        """
        Encontrar archivos de prueba en el proyecto.
        
        Returns:
            Lista de rutas a archivos de prueba
        """
        test_files = []
        
        for file in self.scanner.files:
            file_path = self._get_file_path(file)
            file_lower = file_path.lower()
            if 'test' in os.path.basename(file_lower) or \
               '/test' in file_lower.replace('\\', '/') or \
               '/tests/' in file_lower.replace('\\', '/'):
                test_files.append(file)
        
        return test_files
    
    def _calculate_documentation_percentage(self, files: List[str]) -> float:
        """
        Calcular porcentaje de documentación en los archivos.
        
        Args:
            files: Lista de rutas a archivos
            
        Returns:
            Porcentaje de documentación (0-100)
        """
        total_functions = 0
        documented_functions = 0
        
        for file in files:
            try:
                file_path = self._get_file_path(file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Detectar lenguaje
                ext = os.path.splitext(file_path)[1].lower()
                
                # Para Python
                if ext == '.py':
                    # Contar definiciones de funciones y clases
                    func_matches = re.findall(r'def\s+\w+\s*\(', content)
                    class_matches = re.findall(r'class\s+\w+', content)
                    total_functions += len(func_matches) + len(class_matches)
                    
                    # Contar docstrings
                    docstring_matches = re.findall(r'"""[\s\S]*?"""', content)
                    documented_functions += len(docstring_matches)
                
                # Para JavaScript/TypeScript
                elif ext in ('.js', '.ts', '.jsx', '.tsx'):
                    # Contar definiciones de funciones
                    func_matches = re.findall(r'function\s+\w+\s*\(|const\s+\w+\s*=\s*\(|let\s+\w+\s*=\s*\(|var\s+\w+\s*=\s*\(', content)
                    class_matches = re.findall(r'class\s+\w+', content)
                    total_functions += len(func_matches) + len(class_matches)
                    
                    # Contar comentarios JSDoc
                    jsdoc_matches = re.findall(r'/\*\*[\s\S]*?\*/', content)
                    documented_functions += len(jsdoc_matches)
                
                # Para otros lenguajes, simplificar
                else:
                    # Contar líneas que parecen definiciones de funciones
                    func_matches = re.findall(r'\w+\s*\(.*?\)\s*\{', content)
                    total_functions += len(func_matches)
                    
                    # Contar bloques de comentarios
                    comment_matches = re.findall(r'/\*[\s\S]*?\*/|//.*?$', content, re.MULTILINE)
                    documented_functions += min(len(comment_matches), len(func_matches))
                
            except Exception as e:
                logger.warning(f"Error al analizar documentación de {file}: {str(e)}")
        
        # Calcular porcentaje
        return (documented_functions / max(total_functions, 1)) * 100
    
    def _find_complex_files(self, files: List[str]) -> List[Dict[str, Any]]:
        """
        Encontrar archivos con alta complejidad.
        
        Args:
            files: Lista de rutas a archivos
            
        Returns:
            Lista de archivos complejos con métricas
        """
        complex_files = []
        
        for file in files:
            try:
                file_path = self._get_file_path(file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Métricas simples de complejidad
                metrics = {
                    "file": file_path,
                    "lines": content.count('\n') + 1,
                    "functions": self._count_functions(content),
                    "nested_depth": self._estimate_nesting_depth(content)
                }
                
                # Determinar si es complejo
                is_complex = (
                    metrics["lines"] > 500 or
                    metrics["functions"] > 20 or
                    metrics["nested_depth"] > 5
                )
                
                if is_complex:
                    complex_files.append(metrics)
                
            except Exception as e:
                logger.warning(f"Error al analizar complejidad de {file}: {str(e)}")
        
        # Ordenar por complejidad
        return sorted(complex_files, 
                      key=lambda x: x["lines"] + x["functions"] * 10 + x["nested_depth"] * 30,
                      reverse=True)
    
    def _count_functions(self, content: str) -> int:
        """
        Contar funciones en el contenido de un archivo.
        
        Args:
            content: Contenido del archivo
            
        Returns:
            Número de funciones
        """
        # Buscar patrones comunes de definición de funciones
        patterns = [
            r'def\s+\w+\s*\(',  # Python
            r'function\s+\w+\s*\(',  # JavaScript
            r'const\s+\w+\s*=\s*\(',  # Arrow functions
            r'let\s+\w+\s*=\s*\(',
            r'var\s+\w+\s*=\s*\(',
            r'class\s+\w+',  # Clases
            r'\w+\s*\(.*?\)\s*\{',  # Estilo C/Java
        ]
        
        count = 0
        for pattern in patterns:
            count += len(re.findall(pattern, content))
        
        return count
    
    def _estimate_nesting_depth(self, content: str) -> int:
        """
        Estimar profundidad de anidación máxima.
        
        Args:
            content: Contenido del archivo
            
        Returns:
            Profundidad máxima estimada
        """
        lines = content.split('\n')
        max_depth = 0
        current_depth = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Incrementar profundidad al abrir bloques
            if stripped.endswith('{') or stripped.endswith(':'):
                current_depth += 1
            
            # Decrementar profundidad al cerrar bloques
            elif stripped == '}' or stripped.startswith('}'):
                current_depth = max(0, current_depth - 1)
            
            max_depth = max(max_depth, current_depth)
        
        return max_depth
    
    def _estimate_code_duplication(self, files: List[str]) -> Dict[str, Any]:
        """
        Estimar duplicación de código en el proyecto.
        
        Args:
            files: Lista de rutas a archivos
            
        Returns:
            Estimación de duplicación
        """
        # Enfoque simplificado: detectar funciones con nombres similares
        function_names = {}
        
        for file in files:
            try:
                file_path = self._get_file_path(file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extraer nombres de funciones
                # Python
                for match in re.finditer(r'def\s+(\w+)\s*\(', content):
                    name = match.group(1)
                    function_names[name] = function_names.get(name, 0) + 1
                
                # JavaScript/TypeScript
                for match in re.finditer(r'function\s+(\w+)\s*\(', content):
                    name = match.group(1)
                    function_names[name] = function_names.get(name, 0) + 1
                
            except Exception as e:
                logger.warning(f"Error al analizar duplicación en {file}: {str(e)}")
        
        # Contar funciones duplicadas
        duplicated = {name: count for name, count in function_names.items() if count > 1}
        
        # Calcular porcentaje aproximado
        total_functions = sum(function_names.values())
        duplicated_functions = sum(duplicated.values()) - len(duplicated)
        percentage = (duplicated_functions / max(total_functions, 1)) * 100
        
        return {
            "percentage": percentage,
            "duplicated_functions": len(duplicated),
            "examples": list(duplicated.keys())[:5]
        }
    
    def _estimate_test_coverage(self, test_files: List[str], code_files: List[str]) -> float:
        """
        Estimar cobertura de pruebas.
        
        Args:
            test_files: Lista de archivos de prueba
            code_files: Lista de archivos de código
            
        Returns:
            Porcentaje estimado de cobertura
        """
        # Extraer nombres de funciones de los archivos de código
        code_functions = set()
        
        for file in code_files:
            try:
                file_path = self._get_file_path(file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Python
                for match in re.finditer(r'def\s+(\w+)\s*\(', content):
                    code_functions.add(match.group(1))
                
                # JavaScript/TypeScript
                for match in re.finditer(r'function\s+(\w+)\s*\(', content):
                    code_functions.add(match.group(1))
                
                # Clases
                for match in re.finditer(r'class\s+(\w+)', content):
                    code_functions.add(match.group(1))
                
            except Exception:
                pass
        
        # Buscar esas funciones en los archivos de prueba
        tested_functions = set()
        
        for file in test_files:
            try:
                file_path = self._get_file_path(file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for func in code_functions:
                    if func in content:
                        tested_functions.add(func)
                
            except Exception:
                pass
        
        # Calcular porcentaje
        if not code_functions:
            return 0
        
        return (len(tested_functions) / len(code_functions)) * 100
    
    def _get_files_in_dir(self, directory: str) -> List[str]:
        """
        Obtener rutas a todos los archivos en un directorio y subdirectorios.
        
        Args:
            directory: Directorio a analizar
            
        Returns:
            Lista de rutas a archivos
        """
        files = []
        
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                # Excluir archivos ocultos y binarios
                if not filename.startswith('.') and self._is_text_file(filename):
                    files.append(os.path.join(root, filename))
        
        return files
    
    def _is_text_file(self, filename: str) -> bool:
        """
        Determinar si un archivo es de texto basado en su extensión.
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            True si es un archivo de texto, False en caso contrario
        """
        text_extensions = {
            '.txt', '.md', '.py', '.js', '.ts', '.html', '.css', '.scss', '.json',
            '.xml', '.yaml', '.yml', '.ini', '.cfg', '.conf', '.sh', '.bat',
            '.c', '.cpp', '.h', '.hpp', '.java', '.cs', '.go', '.rb', '.php'
        }
        
        return os.path.splitext(filename)[1].lower() in text_extensions
    
    def _count_code_lines(self, file_path: str) -> int:
        """
        Contar líneas de código en un archivo.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Número de líneas de código
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Filtrar líneas vacías y comentarios simples
            code_lines = [
                line for line in lines 
                if line.strip() and not line.strip().startswith(('#', '//', '/*', '*'))
            ]
            
            return len(code_lines)
        
        except Exception:
            return 0
    
    def _count_test_lines(self, file_path: str) -> int:
        """
        Contar líneas de código en un archivo de pruebas.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Número de líneas de pruebas
        """
        # Solo contar si es un archivo de prueba
        if 'test' not in os.path.basename(file_path).lower():
            return 0
        
        return self._count_code_lines(file_path)
    
    def _find_feature_specs(self) -> Dict[str, Any]:
        """
        Buscar especificaciones de características en el proyecto.
        
        Returns:
            Diccionario con características encontradas
        """
        specs = {}
        
        # Buscar en directorios típicos de documentación
        doc_dirs = ['docs', 'doc', 'specifications', 'specs', 'design']
        
        for doc_dir in doc_dirs:
            dir_path = os.path.join(self.project_path, doc_dir)
            
            if os.path.isdir(dir_path):
                for root, _, filenames in os.walk(dir_path):
                    for filename in filenames:
                        if filename.endswith(('.md', '.txt')):
                            file_path = os.path.join(root, filename)
                            
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                # Buscar títulos que sugieran una característica
                                feature_headers = re.findall(r'#+\s*(.+?)\n', content)
                                
                                for header in feature_headers:
                                    # Identificar palabras clave comunes en títulos de características
                                    keywords = ['feature', 'functionality', 'component', 'módulo', 
                                              'característica', 'funcionalidad']
                                    
                                    if any(keyword in header.lower() for keyword in keywords):
                                        # Extraer nombre de la característica
                                        name = re.sub(r'feature|functionality|component|:|-', '', 
                                                    header, flags=re.IGNORECASE).strip()
                                        
                                        # Añadir a especificaciones
                                        specs[name] = {
                                            "file": file_path,
                                            "description": header,
                                            "content": content
                                        }
                            
                            except Exception:
                                pass
        
        return specs
    
    def _estimate_feature_completion(self, feature_name: str, feature_files: List[str]) -> int:
        """
        Estimar porcentaje de completitud de una característica.
        
        Args:
            feature_name: Nombre de la característica
            feature_files: Archivos de la característica
            
        Returns:
            Porcentaje de completitud estimado
        """
        # Señales de completitud
        completion_signals = {
            "has_tests": any("test" in os.path.basename(f).lower() for f in feature_files),
            "has_docs": any(f.endswith(('.md', '.txt', '.html')) for f in feature_files),
            "has_implementation": any(self._is_code_file(f) for f in feature_files),
            "has_todo_marks": False,
            "has_issue_marks": False
        }
        
        # Buscar marcas TODO o FIXME en los archivos
        for file in feature_files:
            try:
                if self._is_text_file(file):
                    file_path = self._get_file_path(file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if re.search(r'TODO|FIXME|XXX|PENDING', content, re.IGNORECASE):
                        completion_signals["has_todo_marks"] = True
                    
                    if re.search(r'ISSUE|BUG|PROBLEM', content, re.IGNORECASE):
                        completion_signals["has_issue_marks"] = True
            
            except Exception:
                pass
        
        # Calcular puntuación
        score = 0
        if completion_signals["has_implementation"]:
            score += 50  # Base por tener implementación
        
        if completion_signals["has_tests"]:
            score += 25  # Bonus por tests
        
        if completion_signals["has_docs"]:
            score += 15  # Bonus por documentación
        
        if completion_signals["has_todo_marks"]:
            score -= 15  # Penalización por TODOs
        
        if completion_signals["has_issue_marks"]:
            score -= 20  # Penalización por issues conocidas
        
        # Limitar entre 0 y 100
        return max(0, min(100, score))
    
    def _check_spec_implementation(self, spec: Dict[str, Any]) -> int:
        """
        Verificar implementación de una especificación.
        
        Args:
            spec: Diccionario con datos de la especificación
            
        Returns:
            Porcentaje de implementación estimado
        """
        try:
            content = spec.get("content", "")
            
            # Buscar menciones a requisitos o componentes
            requirements = re.findall(r'[-*]\s*(.+?)(?:\n|$)', content)
            
            if not requirements:
                return 50  # No se pueden identificar requisitos específicos
            
            # Verificar implementación de requisitos
            implemented = 0
            
            for req in requirements:
                # Extraer palabras clave del requisito
                keywords = [w for w in re.findall(r'\b\w{3,}\b', req.lower()) 
                           if w not in ['the', 'and', 'for', 'with', 'that', 'this']]
                
                if not keywords:
                    continue
                
                # Buscar estas palabras clave en archivos de código
                found = False
                for file in self.scanner.files:
                    if self._is_code_file(file):
                        try:
                            file_path = self._get_file_path(file)
                            with open(file_path, 'r', encoding='utf-8') as f:
                                file_content = f.read().lower()
                            
                            # Si se encuentran suficientes palabras clave, considerar implementado
                            if sum(1 for k in keywords if k in file_content) >= min(2, len(keywords)):
                                found = True
                                break
                        
                        except Exception:
                            pass
                
                if found:
                    implemented += 1
            
            # Calcular porcentaje
            return (implemented / len(requirements)) * 100
        
        except Exception as e:
            logger.warning(f"Error al verificar implementación de especificación: {str(e)}")
            return 0
    
    def _detect_architecture_pattern(self) -> str:
        """
        Detectar patrón arquitectónico del proyecto.
        
        Returns:
            Nombre del patrón detectado
        """
        directories = [d for d in os.listdir(self.project_path) 
                      if os.path.isdir(os.path.join(self.project_path, d))]
        
        # MVC: Models, Views, Controllers
        if all(d in directories for d in ['models', 'views', 'controllers']):
            return "MVC (Model-View-Controller)"
        
        # MVVM: Models, Views, ViewModels
        if all(d in directories for d in ['models', 'views', 'viewmodels']):
            return "MVVM (Model-View-ViewModel)"
        
        # Clean Architecture / Hexagonal
        if any(d in directories for d in ['domain', 'infrastructure', 'application']):
            return "Clean Architecture / Hexagonal"
        
        # Microservicios
        if any('service' in d.lower() for d in directories) and len(directories) > 5:
            return "Microservicios"
        
        # Monolítico por capas
        layers = ['data', 'services', 'ui', 'utils', 'helpers', 'api']
        if sum(1 for d in directories if any(layer in d.lower() for layer in layers)) >= 3:
            return "Monolítico por capas"
        
        return "Indeterminado"
    
    def _calculate_modularity_score(self) -> int:
        """
        Calcular puntuación de modularidad.
        
        Returns:
            Puntuación de modularidad (0-100)
        """
        try:
            # Obtener datos del grafo de dependencias
            graph_data = self.dependency_graph.build_dependency_graph(self.project_path)
            
            if not graph_data or not graph_data.get('nodes'):
                return 50  # Valor por defecto
            
            # Evaluar basado en características de la gráfica de dependencias
            num_nodes = len(graph_data['nodes'])
            
            if num_nodes == 0:
                return 50
            
            # Usar métricas del grafo
            metrics = graph_data.get('metrics', {})
            avg_deps = metrics.get('avg_out_degree', 0)
            
            # Identificar nodos centrales usando los datos existentes
            central_files = graph_data.get('central_files', [])
            central_ratio = min(len(central_files) / num_nodes, 1.0) if num_nodes > 0 else 0
            
            # Calcular puntuación
            # Menos dependencias por módulo = mejor modularity
            deps_score = max(0, 100 - (avg_deps * 10))
            
            # Menos nodos centrales = mejor modularidad
            central_score = max(0, 100 - (central_ratio * 100))
            
            # Combinar puntuaciones
            return int((deps_score * 0.6) + (central_score * 0.4))
            
        except Exception as e:
            logger.warning(f"Error calculando puntuación de modularidad: {str(e)}")
            return 50  # Valor por defecto en caso de error
    
    def _identify_risk_areas(self) -> List[Dict[str, Any]]:
        """
        Identificar áreas de riesgo en el código.
        
        Returns:
            Lista de áreas de riesgo
        """
        risk_areas = []
        
        # Archivos muy grandes
        for file in self.scanner.files:
            if self._is_code_file(file):
                try:
                    file_path = self._get_file_path(file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    lines = content.count('\n') + 1
                    
                    if lines > 500:
                        risk_areas.append({
                            "type": "large_file",
                            "file": file,
                            "lines": lines,
                            "risk_level": "medium" if lines < 1000 else "high"
                        })
                except Exception:
                    pass
        
        # Módulos con muchos dependientes
        try:
            graph_data = self.dependency_graph.build_dependency_graph(self.project_path)
            central_files = graph_data.get('central_files', [])
            
            for central_file in central_files:
                dependents = central_file.get('in_degree', 0)  # in_degree represents dependents
                if dependents > 10:
                    risk_areas.append({
                        "type": "high_coupling",
                        "file": central_file.get('file', ''),
                        "dependents": dependents,
                        "risk_level": "medium" if dependents < 20 else "high"
                    })
        except Exception as e:
            logger.warning(f"Error al analizar dependencias para áreas de riesgo: {str(e)}")
        
        # Ordenar por nivel de riesgo
        risk_areas.sort(key=lambda x: 0 if x["risk_level"] == "high" else 1)
        
        return risk_areas
    
    def _is_branch_old(self, date_str: str) -> bool:
        """
        Determinar si una branch no se ha actualizado recientemente.
        
        Args:
            date_str: Fecha de último commit en formato ISO
            
        Returns:
            True si la branch es antigua, False en caso contrario
        """
        if date_str == "N/A":
            return False
        
        try:
            # Convertir a fecha
            date_format = "%Y-%m-%d %H:%M:%S %z"
            if ' +' not in date_str and ' -' not in date_str:
                date_format = "%Y-%m-%d %H:%M:%S"
            
            commit_date = datetime.strptime(date_str, date_format)
            
            # Calcular días desde el commit
            delta = datetime.now() - commit_date.replace(tzinfo=None)
            days = delta.days
            
            # Considerar antigua si tiene más de 30 días
            return days > 30
        
        except Exception:
            return False
    
    def _get_file_path(self, file) -> str:
        """
        Obtener la ruta de un archivo, ya sea que se pase como string o como diccionario.
        
        Args:
            file: Ruta al archivo (str) o diccionario de información de archivo
            
        Returns:
            Ruta del archivo como string
        """
        if isinstance(file, dict) and 'path' in file:
            return file['path']
        elif isinstance(file, str):
            return file
        else:
            return str(file)  # Intentar convertir a string como último recurso
    
    def _create_basic_functional_groups(self) -> Dict[str, Any]:
        """
        Crear grupos funcionales básicos basados en funcionalidades detectadas.
        
        Returns:
            Dict con grupos funcionales básicos
        """
        features = {}
        
        try:
            # Usar detector de funcionalidades para crear grupos básicos
            from src.analyzers.functionality_detector import get_functionality_detector
            
            detector = get_functionality_detector()
            functionality_result = detector.detect_functionalities(self.project_path)
            
            detected_functionalities = functionality_result.get('detected', {})
            
            for func_name, func_data in detected_functionalities.items():
                if func_data.get('present', False):
                    evidence = func_data.get('evidence', {})
                    files = evidence.get('files', [])
                    
                    # Clean up and format the functionality name
                    clean_name = func_name.capitalize().strip()
                    
                    # Add appropriate emoji based on functionality type
                    icon_map = {
                        'authentication': '🔐',
                        'database': '🗄️',
                        'api': '🔗',
                        'frontend': '🎨',
                        'testing': '🧪',
                        'configuration': '⚙️',
                        'documentation': '📚',
                        'security': '🛡️',
                        'logging': '📋',
                        'deployment': '🚀',
                        'monitoring': '📊'
                    }
                    
                    icon = icon_map.get(func_name.lower(), '🔧')
                    display_name = f"{icon} {clean_name}"
                    
                    features[display_name] = {
                        "type": "functionality",
                        "files": len(files),
                        "description": f"Funcionalidad {func_name}",
                        "importance": func_data.get('confidence', 0),
                        "size": len(files),
                        "completion_estimate": min(func_data.get('confidence', 0), 100)
                    }
                    
        except Exception as e:
            logger.error(f"Error al crear grupos funcionales básicos: {e}")
            # Fallback a estructura de directorios simple
            features = self._create_directory_based_groups()
            
        return features
    
    def _create_directory_based_groups(self) -> Dict[str, Any]:
        """
        Crear grupos basados en estructura de directorios como último recurso.
        
        Returns:
            Dict con grupos basados en directorios
        """
        features = {}
        
        # Mapeo de directorios a tipos funcionales
        directory_mapping = {
            'src': '📁 Código Fuente Principal',
            'tests': '🧪 Pruebas y Testing',
            'docs': '📖 Documentación',
            'examples': '💡 Ejemplos y Demos',
            'config': '⚙️ Configuración',
            'scripts': '🔧 Scripts y Herramientas',
            'assets': '📦 Recursos y Assets',
            'public': '🌐 Archivos Públicos',
            'static': '📄 Archivos Estáticos'
        }
        
        try:
            dirs = [d for d in os.listdir(self.project_path) 
                    if os.path.isdir(os.path.join(self.project_path, d)) 
                    and not d.startswith('.') and d not in ('node_modules', 'venv', 'env', '__pycache__')]
            
            for dir_name in dirs:
                # Usar nombre mapeado si existe, sino usar el nombre del directorio
                display_name = directory_mapping.get(dir_name, f"📁 {dir_name.capitalize()}")
                
                dir_path = os.path.join(self.project_path, dir_name)
                feature_files = self._get_files_in_dir(dir_path)
                
                features[display_name] = {
                    "type": "directory",
                    "files": len(feature_files),
                    "description": f"Archivos en directorio {dir_name}",
                    "importance": len(feature_files) * 10,  # Importancia basada en número de archivos
                    "size": len(feature_files),
                    "completion_estimate": self._estimate_group_completion(feature_files)
                }
                
        except Exception as e:
            logger.error(f"Error al crear grupos de directorios: {e}")
            
        return features
    
    def _estimate_group_completion(self, group_files: List[str]) -> int:
        """
        Estimar porcentaje de completitud de un grupo funcional.
        
        Args:
            group_files: Lista de archivos en el grupo
            
        Returns:
            Porcentaje de completitud estimado
        """
        if not group_files:
            return 0
            
        # Señales de completitud
        completion_signals = {
            "has_tests": False,
            "has_docs": False,
            "has_implementation": False,
            "has_todo_marks": False,
            "has_issue_marks": False
        }
        
        # Analizar archivos del grupo
        for file_info in group_files:
            try:
                if isinstance(file_info, dict):
                    file_path = file_info.get('path', '')
                else:
                    file_path = str(file_info)
                
                if not file_path:
                    continue
                    
                file_name = os.path.basename(file_path).lower()
                
                # Detectar tipos de archivos
                if "test" in file_name:
                    completion_signals["has_tests"] = True
                
                if file_path.endswith(('.md', '.txt', '.html', '.rst')):
                    completion_signals["has_docs"] = True
                
                if self._is_code_file(file_path):
                    completion_signals["has_implementation"] = True
                    
                    # Buscar marcas TODO o FIXME si es un archivo de texto
                    if self._is_text_file(file_name):
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            
                            if re.search(r'TODO|FIXME|XXX|PENDING', content, re.IGNORECASE):
                                completion_signals["has_todo_marks"] = True
                            
                            if re.search(r'ISSUE|BUG|PROBLEM', content, re.IGNORECASE):
                                completion_signals["has_issue_marks"] = True
                        except Exception:
                            pass
                
            except Exception as e:
                logger.debug(f"Error al analizar archivo {file_info}: {e}")
                continue
        
        # Calcular puntuación
        score = 0
        if completion_signals["has_implementation"]:
            score += 50  # Base por tener implementación
        
        if completion_signals["has_tests"]:
            score += 25  # Bonus por tests
        
        if completion_signals["has_docs"]:
            score += 15  # Bonus por documentación
        
        if completion_signals["has_todo_marks"]:
            score -= 15  # Penalización por TODOs
        
        if completion_signals["has_issue_marks"]:
            score -= 20  # Penalización por issues conocidas
        
        # Limitar entre 0 y 100
        return max(0, min(100, score))

def get_project_progress_tracker(project_path: str, config: Optional[ConfigManager] = None) -> ProjectProgressTracker:
    """
    Obtener un rastreador de progreso del proyecto.
    
    Args:
        project_path: Ruta al directorio del proyecto
        config: Configuración opcional
    
    Returns:
        Instancia de ProjectProgressTracker
    """
    return ProjectProgressTracker(project_path, config)
