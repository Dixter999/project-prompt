"""
Sistema Multi-Agente - FASE 1: Analizador de Contexto de Archivos
Componente especializado para análisis contextual de archivos y metadatos del proyecto.
"""

import os
import mimetypes
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import re


class ProjectType(Enum):
    """Tipos de proyecto detectados"""
    WEB_FRONTEND = "web_frontend"
    WEB_BACKEND = "web_backend"
    FULL_STACK = "full_stack"
    MOBILE_APP = "mobile_app"
    DESKTOP_APP = "desktop_app"
    DATA_SCIENCE = "data_science"
    MACHINE_LEARNING = "machine_learning"
    API_SERVICE = "api_service"
    LIBRARY = "library"
    CLI_TOOL = "cli_tool"
    GAME = "game"
    EMBEDDED = "embedded"
    UNKNOWN = "unknown"


class TechnologyStack(Enum):
    """Stacks tecnológicos principales"""
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    NODE_JS = "nodejs"
    PYTHON = "python"
    JAVA = "java"
    DOTNET = "dotnet"
    PHP = "php"
    RUBY = "ruby"
    GO = "go"
    RUST = "rust"
    CPP = "cpp"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    FLUTTER = "flutter"
    REACT_NATIVE = "react_native"
    UNITY = "unity"
    UNKNOWN = "unknown"


@dataclass
class FileMetadata:
    """Metadatos de un archivo"""
    path: str
    size: int
    extension: str
    mime_type: str
    language: str
    is_config: bool
    is_test: bool
    is_documentation: bool
    is_source_code: bool
    complexity_estimate: int
    last_modified: float


@dataclass
class ProjectStructure:
    """Estructura del proyecto analizada"""
    root_path: str
    total_files: int
    source_files: int
    test_files: int
    config_files: int
    documentation_files: int
    languages_detected: Dict[str, int]
    frameworks_detected: Set[str]
    build_tools_detected: Set[str]
    package_managers_detected: Set[str]


@dataclass
class FileContextAnalysisResult:
    """Resultado del análisis de contexto de archivos"""
    project_type: ProjectType
    technology_stack: List[TechnologyStack]
    project_structure: ProjectStructure
    target_files: List[FileMetadata]
    related_files: List[FileMetadata]
    complexity_factors: Dict[str, float]
    recommendations: List[str]
    context_score: float


class FileContextAnalyzer:
    """
    Analizador de contexto de archivos para clasificación inteligente de tasks.
    Analiza estructura del proyecto, tecnologías y archivos relevantes.
    """
    
    def __init__(self):
        self._initialize_technology_patterns()
        self._initialize_file_mappings()
        
    def _initialize_technology_patterns(self):
        """Inicializa patrones para detección de tecnologías"""
        
        self.framework_patterns = {
            'react': [
                r'import.*react', r'from\s+["\']react["\']', r'React\.', r'jsx?$',
                r'package\.json.*"react"', r'\.jsx$'
            ],
            'vue': [
                r'import.*vue', r'from\s+["\']vue["\']', r'Vue\.', r'\.vue$',
                r'package\.json.*"vue"'
            ],
            'angular': [
                r'import.*@angular', r'@Component', r'@Injectable', r'angular\.json',
                r'package\.json.*"@angular"'
            ],
            'node.js': [
                r'package\.json', r'node_modules', r'require\(', r'module\.exports',
                r'process\.env', r'__dirname'
            ],
            'express': [
                r'express\(\)', r'app\.listen', r'app\.get', r'app\.post',
                r'package\.json.*"express"'
            ],
            'django': [
                r'from django', r'import django', r'settings\.py', r'urls\.py',
                r'models\.py', r'views\.py', r'requirements\.txt.*django'
            ],
            'flask': [
                r'from flask', r'Flask\(__name__\)', r'app\.route',
                r'requirements\.txt.*flask'
            ],
            'fastapi': [
                r'from fastapi', r'FastAPI\(\)', r'@app\.',
                r'requirements\.txt.*fastapi'
            ],
            'spring': [
                r'@SpringBootApplication', r'@RestController', r'@Service',
                r'pom\.xml.*spring', r'application\.properties'
            ],
            'flutter': [
                r'import.*flutter', r'pubspec\.yaml', r'\.dart$',
                r'StatelessWidget', r'StatefulWidget'
            ],
            'react_native': [
                r'react-native', r'import.*react-native', r'App\.js',
                r'package\.json.*"react-native"'
            ]
        }
        
        self.language_patterns = {
            'javascript': [r'\.js$', r'\.mjs$', r'package\.json'],
            'typescript': [r'\.ts$', r'\.tsx$', r'tsconfig\.json'],
            'python': [r'\.py$', r'requirements\.txt', r'setup\.py', r'pyproject\.toml'],
            'java': [r'\.java$', r'pom\.xml', r'build\.gradle'],
            'csharp': [r'\.cs$', r'\.csproj$', r'\.sln$'],
            'php': [r'\.php$', r'composer\.json'],
            'ruby': [r'\.rb$', r'Gemfile', r'\.gemspec$'],
            'go': [r'\.go$', r'go\.mod', r'go\.sum'],
            'rust': [r'\.rs$', r'Cargo\.toml', r'Cargo\.lock'],
            'cpp': [r'\.cpp$', r'\.hpp$', r'\.cc$', r'\.h$', r'CMakeLists\.txt'],
            'swift': [r'\.swift$', r'Package\.swift'],
            'kotlin': [r'\.kt$', r'\.kts$'],
            'dart': [r'\.dart$', r'pubspec\.yaml'],
            'sql': [r'\.sql$', r'\.ddl$'],
            'html': [r'\.html$', r'\.htm$'],
            'css': [r'\.css$', r'\.scss$', r'\.sass$', r'\.less$'],
            'json': [r'\.json$'],
            'yaml': [r'\.yaml$', r'\.yml$'],
            'xml': [r'\.xml$'],
            'markdown': [r'\.md$', r'\.markdown$']
        }
        
        self.build_tools = {
            'npm': ['package\.json', 'package-lock\.json', 'node_modules'],
            'yarn': ['yarn\.lock', '\.yarnrc'],
            'pnpm': ['pnpm-lock\.yaml'],
            'pip': ['requirements\.txt', 'pyproject\.toml', 'setup\.py'],
            'poetry': ['pyproject\.toml', 'poetry\.lock'],
            'conda': ['environment\.yml', 'conda\.yaml'],
            'maven': ['pom\.xml'],
            'gradle': ['build\.gradle', 'gradle\.properties'],
            'cargo': ['Cargo\.toml', 'Cargo\.lock'],
            'composer': ['composer\.json', 'composer\.lock'],
            'bundler': ['Gemfile', 'Gemfile\.lock'],
            'go_modules': ['go\.mod', 'go\.sum'],
            'cmake': ['CMakeLists\.txt'],
            'make': ['Makefile', 'makefile']
        }
    
    def _initialize_file_mappings(self):
        """Inicializa mapeos de tipos de archivos"""
        
        self.config_files = {
            r'\.json$', r'\.yaml$', r'\.yml$', r'\.toml$', r'\.ini$', r'\.conf$',
            r'\.config$', r'\.env$', r'\.properties$', r'tsconfig\.json',
            r'package\.json', r'composer\.json', r'pom\.xml', r'build\.gradle',
            r'Cargo\.toml', r'pyproject\.toml', r'setup\.py', r'requirements\.txt'
        }
        
        self.test_files = {
            r'test_.*\.py$', r'.*_test\.py$', r'.*\.test\.js$', r'.*\.spec\.js$',
            r'.*\.test\.ts$', r'.*\.spec\.ts$', r'.*Test\.java$', r'.*Tests\.cs$',
            r'test.*\.rb$', r'.*_test\.rb$', r'.*_test\.go$', r'.*\.test\.php$'
        }
        
        self.documentation_files = {
            r'README.*', r'CHANGELOG.*', r'LICENSE.*', r'CONTRIBUTING.*',
            r'\.md$', r'\.rst$', r'\.txt$', r'docs/', r'documentation/'
        }
        
        self.source_code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cs', '.php', '.rb',
            '.go', '.rs', '.cpp', '.hpp', '.cc', '.h', '.swift', '.kt', '.dart',
            '.vue', '.svelte', '.html', '.css', '.scss', '.sass', '.less'
        }
    
    def analyze_context(self, file_paths: Optional[List[str]] = None, 
                       project_context: Optional[Dict] = None) -> FileContextAnalysisResult:
        """
        Analiza el contexto de archivos y proyecto.
        
        Args:
            file_paths: Lista de rutas de archivos específicos a analizar
            project_context: Contexto adicional del proyecto
            
        Returns:
            FileContextAnalysisResult con análisis completo del contexto
        """
        
        # Determinar directorio raíz del proyecto
        if file_paths and file_paths[0]:
            root_path = self._find_project_root(file_paths[0])
        elif project_context and 'root_path' in project_context:
            root_path = project_context['root_path']
        else:
            root_path = os.getcwd()
        
        # Analizar estructura del proyecto
        project_structure = self._analyze_project_structure(root_path)
        
        # Detectar tipo de proyecto
        project_type = self._detect_project_type(project_structure)
        
        # Detectar stack tecnológico
        technology_stack = self._detect_technology_stack(project_structure, root_path)
        
        # Analizar archivos específicos
        target_files = []
        if file_paths:
            target_files = [self._analyze_file(fp) for fp in file_paths if os.path.exists(fp)]
        
        # Encontrar archivos relacionados
        related_files = self._find_related_files(target_files, root_path)
        
        # Calcular factores de complejidad
        complexity_factors = self._calculate_complexity_factors(
            project_structure, target_files, related_files
        )
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations(
            project_type, technology_stack, complexity_factors
        )
        
        # Calcular score de contexto
        context_score = self._calculate_context_score(
            project_structure, complexity_factors, len(target_files)
        )
        
        return FileContextAnalysisResult(
            project_type=project_type,
            technology_stack=technology_stack,
            project_structure=project_structure,
            target_files=target_files,
            related_files=related_files,
            complexity_factors=complexity_factors,
            recommendations=recommendations,
            context_score=context_score
        )
    
    def _find_project_root(self, file_path: str) -> str:
        """Encuentra la raíz del proyecto basándose en archivos indicadores"""
        
        indicators = [
            'package.json', 'pyproject.toml', 'setup.py', 'requirements.txt',
            'pom.xml', 'build.gradle', 'Cargo.toml', 'go.mod', 'composer.json',
            '.git', '.gitignore', 'README.md', 'LICENSE'
        ]
        
        current_path = Path(file_path).parent if os.path.isfile(file_path) else Path(file_path)
        
        while current_path != current_path.parent:
            for indicator in indicators:
                if (current_path / indicator).exists():
                    return str(current_path)
            current_path = current_path.parent
            
        return str(Path(file_path).parent)
    
    def _analyze_project_structure(self, root_path: str) -> ProjectStructure:
        """Analiza la estructura del proyecto"""
        
        if not os.path.exists(root_path):
            return self._empty_project_structure(root_path)
        
        total_files = 0
        source_files = 0
        test_files = 0
        config_files = 0
        documentation_files = 0
        languages_detected = {}
        frameworks_detected = set()
        build_tools_detected = set()
        package_managers_detected = set()
        
        for root, dirs, files in os.walk(root_path):
            # Ignorar directorios comunes que no son relevantes
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in 
                      ['node_modules', '__pycache__', 'target', 'build', 'dist']]
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, root_path)
                
                total_files += 1
                
                # Categorizar archivo
                if self._is_source_file(file):
                    source_files += 1
                elif self._is_test_file(rel_path):
                    test_files += 1
                elif self._is_config_file(file):
                    config_files += 1
                elif self._is_documentation_file(file):
                    documentation_files += 1
                
                # Detectar lenguaje
                language = self._detect_file_language(file)
                if language:
                    languages_detected[language] = languages_detected.get(language, 0) + 1
                
                # Detectar frameworks y herramientas
                self._detect_frameworks_in_file(file_path, frameworks_detected)
                self._detect_build_tools_in_file(file, build_tools_detected, package_managers_detected)
        
        return ProjectStructure(
            root_path=root_path,
            total_files=total_files,
            source_files=source_files,
            test_files=test_files,
            config_files=config_files,
            documentation_files=documentation_files,
            languages_detected=languages_detected,
            frameworks_detected=frameworks_detected,
            build_tools_detected=build_tools_detected,
            package_managers_detected=package_managers_detected
        )
    
    def _analyze_file(self, file_path: str) -> FileMetadata:
        """Analiza metadatos de un archivo específico"""
        
        if not os.path.exists(file_path):
            return self._empty_file_metadata(file_path)
        
        stat = os.stat(file_path)
        path_obj = Path(file_path)
        
        return FileMetadata(
            path=file_path,
            size=stat.st_size,
            extension=path_obj.suffix,
            mime_type=mimetypes.guess_type(file_path)[0] or 'unknown',
            language=self._detect_file_language(path_obj.name) or 'unknown',
            is_config=self._is_config_file(path_obj.name),
            is_test=self._is_test_file(file_path),
            is_documentation=self._is_documentation_file(path_obj.name),
            is_source_code=self._is_source_file(path_obj.name),
            complexity_estimate=self._estimate_file_complexity(file_path),
            last_modified=stat.st_mtime
        )
    
    def _detect_project_type(self, structure: ProjectStructure) -> ProjectType:
        """Detecta el tipo de proyecto basándose en la estructura"""
        
        frameworks = structure.frameworks_detected
        languages = structure.languages_detected
        
        # Web Frontend
        if any(fw in frameworks for fw in ['react', 'vue', 'angular']):
            return ProjectType.WEB_FRONTEND
        
        # Web Backend
        if any(fw in frameworks for fw in ['express', 'django', 'flask', 'fastapi', 'spring']):
            return ProjectType.WEB_BACKEND
        
        # Mobile
        if any(fw in frameworks for fw in ['flutter', 'react_native']):
            return ProjectType.MOBILE_APP
        
        # Data Science / ML
        if 'python' in languages and any(
            keyword in str(structure.frameworks_detected).lower() 
            for keyword in ['pandas', 'numpy', 'scikit', 'tensorflow', 'pytorch']
        ):
            return ProjectType.DATA_SCIENCE
        
        # API Service
        if any(fw in frameworks for fw in ['fastapi', 'express', 'spring']):
            return ProjectType.API_SERVICE
        
        # CLI Tool
        if structure.source_files < 20 and 'python' in languages:
            return ProjectType.CLI_TOOL
        
        return ProjectType.UNKNOWN
    
    def _detect_technology_stack(self, structure: ProjectStructure, root_path: str) -> List[TechnologyStack]:
        """Detecta el stack tecnológico del proyecto"""
        
        stacks = []
        frameworks = structure.frameworks_detected
        languages = structure.languages_detected
        
        # JavaScript/TypeScript
        if 'javascript' in languages or 'typescript' in languages:
            stacks.append(TechnologyStack.JAVASCRIPT)
            if 'typescript' in languages:
                stacks.append(TechnologyStack.TYPESCRIPT)
        
        # Python
        if 'python' in languages:
            stacks.append(TechnologyStack.PYTHON)
        
        # Frameworks específicos
        if 'react' in frameworks:
            stacks.append(TechnologyStack.REACT)
        if 'vue' in frameworks:
            stacks.append(TechnologyStack.VUE)
        if 'angular' in frameworks:
            stacks.append(TechnologyStack.ANGULAR)
        if 'node.js' in frameworks or 'express' in frameworks:
            stacks.append(TechnologyStack.NODE_JS)
        if 'flutter' in frameworks:
            stacks.append(TechnologyStack.FLUTTER)
        if 'react_native' in frameworks:
            stacks.append(TechnologyStack.REACT_NATIVE)
        
        # Otros lenguajes
        if 'java' in languages:
            stacks.append(TechnologyStack.JAVA)
        if 'csharp' in languages:
            stacks.append(TechnologyStack.DOTNET)
        if 'php' in languages:
            stacks.append(TechnologyStack.PHP)
        if 'ruby' in languages:
            stacks.append(TechnologyStack.RUBY)
        if 'go' in languages:
            stacks.append(TechnologyStack.GO)
        if 'rust' in languages:
            stacks.append(TechnologyStack.RUST)
        if 'cpp' in languages:
            stacks.append(TechnologyStack.CPP)
        
        return stacks if stacks else [TechnologyStack.UNKNOWN]
    
    def _find_related_files(self, target_files: List[FileMetadata], root_path: str) -> List[FileMetadata]:
        """Encuentra archivos relacionados con los archivos objetivo"""
        
        if not target_files:
            return []
        
        related = []
        
        for target in target_files:
            # Archivos en el mismo directorio
            target_dir = os.path.dirname(target.path)
            if os.path.exists(target_dir):
                for file in os.listdir(target_dir):
                    file_path = os.path.join(target_dir, file)
                    if os.path.isfile(file_path) and file_path != target.path:
                        if self._is_related_file(target, file_path):
                            related.append(self._analyze_file(file_path))
        
        # Limitar número de archivos relacionados
        return related[:10]
    
    def _is_related_file(self, target: FileMetadata, candidate_path: str) -> bool:
        """Determina si un archivo está relacionado con el archivo objetivo"""
        
        target_name = Path(target.path).stem
        candidate_name = Path(candidate_path).stem
        candidate_ext = Path(candidate_path).suffix
        
        # Mismo nombre base
        if target_name == candidate_name:
            return True
        
        # Archivos de test relacionados
        if target.is_source_code and self._is_test_file(candidate_path):
            if target_name in candidate_name:
                return True
        
        # Archivos de configuración relacionados
        if candidate_ext in ['.json', '.yaml', '.yml', '.toml'] and target.is_source_code:
            return True
        
        return False
    
    def _calculate_complexity_factors(self, structure: ProjectStructure, 
                                    target_files: List[FileMetadata],
                                    related_files: List[FileMetadata]) -> Dict[str, float]:
        """Calcula factores de complejidad del contexto"""
        
        factors = {}
        
        # Complejidad por tamaño del proyecto
        factors['project_size'] = min(structure.total_files / 1000.0, 1.0)
        
        # Complejidad por diversidad de lenguajes
        factors['language_diversity'] = min(len(structure.languages_detected) / 5.0, 1.0)
        
        # Complejidad por frameworks
        factors['framework_complexity'] = min(len(structure.frameworks_detected) / 3.0, 1.0)
        
        # Complejidad por archivos objetivo
        if target_files:
            avg_file_complexity = sum(f.complexity_estimate for f in target_files) / len(target_files)
            factors['target_file_complexity'] = min(avg_file_complexity / 100.0, 1.0)
        else:
            factors['target_file_complexity'] = 0.0
        
        # Complejidad por herramientas de build
        factors['build_tool_complexity'] = min(len(structure.build_tools_detected) / 3.0, 1.0)
        
        return factors
    
    def _generate_recommendations(self, project_type: ProjectType, 
                                technology_stack: List[TechnologyStack],
                                complexity_factors: Dict[str, float]) -> List[str]:
        """Genera recomendaciones basadas en el análisis"""
        
        recommendations = []
        
        # Recomendaciones por tipo de proyecto
        if project_type == ProjectType.WEB_FRONTEND:
            recommendations.append("Consider using specialized frontend analysis tools")
            recommendations.append("Focus on component-level analysis")
        elif project_type == ProjectType.WEB_BACKEND:
            recommendations.append("Emphasize API design and database interactions")
            recommendations.append("Consider security and performance implications")
        elif project_type == ProjectType.DATA_SCIENCE:
            recommendations.append("Focus on data flow and algorithm efficiency")
            recommendations.append("Consider model validation and testing")
        
        # Recomendaciones por complejidad
        avg_complexity = sum(complexity_factors.values()) / len(complexity_factors)
        if avg_complexity > 0.7:
            recommendations.append("High complexity project - consider breaking into smaller tasks")
            recommendations.append("Multiple agent collaboration may be beneficial")
        elif avg_complexity < 0.3:
            recommendations.append("Simple project structure - single agent should suffice")
        
        # Recomendaciones por stack tecnológico
        if TechnologyStack.TYPESCRIPT in technology_stack:
            recommendations.append("TypeScript detected - focus on type safety")
        if TechnologyStack.PYTHON in technology_stack:
            recommendations.append("Python project - consider PEP compliance")
        
        return recommendations
    
    def _calculate_context_score(self, structure: ProjectStructure, 
                                complexity_factors: Dict[str, float],
                                target_file_count: int) -> float:
        """Calcula score general del análisis de contexto"""
        
        # Factores de score
        structure_score = min(structure.source_files / 100.0, 1.0) * 0.3
        complexity_score = sum(complexity_factors.values()) / len(complexity_factors) * 0.4
        target_score = min(target_file_count / 10.0, 1.0) * 0.3
        
        return min(structure_score + complexity_score + target_score, 1.0)
    
    # Métodos auxiliares para detección de tipos de archivos
    
    def _is_source_file(self, filename: str) -> bool:
        """Determina si un archivo es código fuente"""
        return Path(filename).suffix in self.source_code_extensions
    
    def _is_test_file(self, filepath: str) -> bool:
        """Determina si un archivo es de pruebas"""
        return any(re.search(pattern, filepath) for pattern in self.test_files)
    
    def _is_config_file(self, filename: str) -> bool:
        """Determina si un archivo es de configuración"""
        return any(re.search(pattern, filename) for pattern in self.config_files)
    
    def _is_documentation_file(self, filename: str) -> bool:
        """Determina si un archivo es de documentación"""
        return any(re.search(pattern, filename) for pattern in self.documentation_files)
    
    def _detect_file_language(self, filename: str) -> Optional[str]:
        """Detecta el lenguaje de un archivo por su extensión"""
        for language, patterns in self.language_patterns.items():
            if any(re.search(pattern, filename) for pattern in patterns):
                return language
        return None
    
    def _detect_frameworks_in_file(self, file_path: str, frameworks_set: Set[str]):
        """Detecta frameworks leyendo el contenido del archivo"""
        try:
            if os.path.getsize(file_path) > 1024 * 1024:  # Skip files > 1MB
                return
                
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(10000)  # Read first 10KB
                
                for framework, patterns in self.framework_patterns.items():
                    if any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns):
                        frameworks_set.add(framework)
        except (OSError, UnicodeDecodeError):
            pass
    
    def _detect_build_tools_in_file(self, filename: str, build_tools_set: Set[str], 
                                   package_managers_set: Set[str]):
        """Detecta herramientas de build por nombre de archivo"""
        for tool, patterns in self.build_tools.items():
            if any(re.search(pattern, filename) for pattern in patterns):
                build_tools_set.add(tool)
                
                # Mapear herramientas a package managers
                package_manager_map = {
                    'npm': 'npm', 'yarn': 'yarn', 'pnpm': 'pnpm',
                    'pip': 'pip', 'poetry': 'poetry', 'conda': 'conda',
                    'maven': 'maven', 'gradle': 'gradle', 'cargo': 'cargo',
                    'composer': 'composer', 'bundler': 'bundler', 'go_modules': 'go'
                }
                
                if tool in package_manager_map:
                    package_managers_set.add(package_manager_map[tool])
    
    def _estimate_file_complexity(self, file_path: str) -> int:
        """Estima la complejidad de un archivo (líneas de código efectivas)"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            effective_lines = 0
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith('#') and not stripped.startswith('//'):
                    effective_lines += 1
                    
            return effective_lines
        except (OSError, UnicodeDecodeError):
            return 0
    
    def _empty_project_structure(self, root_path: str) -> ProjectStructure:
        """Retorna estructura de proyecto vacía"""
        return ProjectStructure(
            root_path=root_path,
            total_files=0,
            source_files=0,
            test_files=0,
            config_files=0,
            documentation_files=0,
            languages_detected={},
            frameworks_detected=set(),
            build_tools_detected=set(),
            package_managers_detected=set()
        )
    
    def _empty_file_metadata(self, file_path: str) -> FileMetadata:
        """Retorna metadatos de archivo vacíos"""
        return FileMetadata(
            path=file_path,
            size=0,
            extension='',
            mime_type='unknown',
            language='unknown',
            is_config=False,
            is_test=False,
            is_documentation=False,
            is_source_code=False,
            complexity_estimate=0,
            last_modified=0.0
        )
