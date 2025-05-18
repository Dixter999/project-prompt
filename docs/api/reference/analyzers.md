# Módulo de Analizadores (Analyzers)

El módulo `analyzers` contiene componentes responsables de analizar proyectos y extraer información relevante para la generación de prompts.

## Clases principales

### ProjectStructureAnalyzer

Analiza la estructura de archivos y directorios de un proyecto.

```python
from project_prompt.analyzers import ProjectStructureAnalyzer

analyzer = ProjectStructureAnalyzer(
    project_path="/ruta/al/proyecto",
    exclude_patterns=["node_modules", "*.pyc", "__pycache__"]
)
structure = analyzer.analyze()
```

#### Métodos

| Método | Descripción | Parámetros | Retorno |
|--------|-------------|------------|---------|
| `analyze()` | Analiza la estructura del proyecto | - | `ProjectStructure` |
| `get_file_tree()` | Obtiene el árbol de archivos | `max_depth` (int, opcional) | `dict` |
| `get_summary()` | Genera un resumen del proyecto | - | `dict` |

### DependencyAnalyzer

Analiza las dependencias entre archivos y componentes del proyecto.

```python
from project_prompt.analyzers import DependencyAnalyzer

analyzer = DependencyAnalyzer(project_path="/ruta/al/proyecto")
dependencies = analyzer.analyze_dependencies()
```

#### Métodos

| Método | Descripción | Parámetros | Retorno |
|--------|-------------|------------|---------|
| `analyze_dependencies()` | Analiza las dependencias | - | `DependencyGraph` |
| `get_dependency_graph()` | Obtiene el grafo de dependencias | - | `dict` |
| `find_central_components()` | Identifica componentes centrales | - | `list` |

### FunctionalityDetector

Detecta frameworks, bibliotecas y patrones utilizados en el proyecto.

```python
from project_prompt.analyzers import FunctionalityDetector

detector = FunctionalityDetector(project_path="/ruta/al/proyecto")
technologies = detector.detect_technologies()
frameworks = detector.detect_frameworks()
```

#### Métodos

| Método | Descripción | Parámetros | Retorno |
|--------|-------------|------------|---------|
| `detect_technologies()` | Detecta tecnologías | - | `dict` |
| `detect_frameworks()` | Detecta frameworks | - | `dict` |
| `detect_patterns()` | Detecta patrones de diseño | - | `list` |

### CodeQualityAnalyzer

Evalúa la calidad del código en el proyecto.

```python
from project_prompt.analyzers import CodeQualityAnalyzer

analyzer = CodeQualityAnalyzer(project_path="/ruta/al/proyecto")
metrics = analyzer.calculate_metrics()
```

#### Métodos

| Método | Descripción | Parámetros | Retorno |
|--------|-------------|------------|---------|
| `calculate_metrics()` | Calcula métricas de calidad | - | `dict` |
| `analyze_complexity()` | Analiza la complejidad ciclomática | - | `dict` |
| `find_code_smells()` | Identifica posibles problemas | - | `list` |

## Clases de datos

### ProjectStructure

Representa la estructura de un proyecto analizado.

#### Atributos

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `root_path` | `str` | Ruta al directorio raíz del proyecto |
| `files` | `list` | Lista de archivos en el proyecto |
| `directories` | `list` | Lista de directorios en el proyecto |
| `file_count` | `int` | Número total de archivos |
| `language_stats` | `dict` | Estadísticas de lenguajes utilizados |

### DependencyGraph

Representa el grafo de dependencias entre componentes.

#### Atributos

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `nodes` | `list` | Nodos del grafo (archivos/componentes) |
| `edges` | `list` | Conexiones entre nodos (dependencias) |
| `entry_points` | `list` | Puntos de entrada al proyecto |
