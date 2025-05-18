# Módulo de Generadores (Generators)

El módulo `generators` contiene componentes responsables de generar prompts, documentación y otros contenidos basados en el análisis de proyectos.

## Clases principales

### PromptGenerator

Genera prompts contextuales optimizados para diferentes modelos de IA.

```python
from project_prompt.generators import PromptGenerator
from project_prompt.analyzers import ProjectStructureAnalyzer

# Analizar proyecto
analyzer = ProjectStructureAnalyzer("/ruta/al/proyecto")
project_data = analyzer.analyze()

# Generar prompt
generator = PromptGenerator()
prompt = generator.generate(
    project_data=project_data,
    task="Implementar autenticación de usuarios",
    model="gpt-4",
    context_level="medium"
)
```

#### Métodos

| Método | Descripción | Parámetros | Retorno |
|--------|-------------|------------|---------|
| `generate()` | Genera un prompt contextual | `project_data`, `task`, `model`, `context_level` | `str` |
| `optimize_for_model()` | Optimiza un prompt para un modelo específico | `prompt`, `model` | `str` |
| `estimate_tokens()` | Estima tokens en un prompt | `prompt` | `int` |

### TemplateEngine

Motor de plantillas para generar distintos tipos de contenido.

```python
from project_prompt.generators import TemplateEngine

engine = TemplateEngine()
result = engine.render_template(
    template_name="project_summary",
    context={"project_data": project_data}
)
```

#### Métodos

| Método | Descripción | Parámetros | Retorno |
|--------|-------------|------------|---------|
| `render_template()` | Renderiza una plantilla | `template_name`, `context` | `str` |
| `register_template()` | Registra una nueva plantilla | `name`, `content` | `None` |
| `get_template()` | Obtiene una plantilla | `name` | `Template` |

### DocumentationGenerator

Genera documentación para proyectos.

```python
from project_prompt.generators import DocumentationGenerator

generator = DocumentationGenerator(project_path="/ruta/al/proyecto")
docs = generator.generate_documentation(output_format="markdown")
```

#### Métodos

| Método | Descripción | Parámetros | Retorno |
|--------|-------------|------------|---------|
| `generate_documentation()` | Genera documentación | `output_format` | `dict` |
| `generate_readme()` | Genera un README | - | `str` |
| `generate_api_docs()` | Genera documentación de API | - | `dict` |

### ContextExtractor

Extrae y filtra información contextual relevante de un proyecto.

```python
from project_prompt.generators import ContextExtractor

extractor = ContextExtractor(project_data=project_data)
context = extractor.extract_context_for_task("Implementar autenticación")
```

#### Métodos

| Método | Descripción | Parámetros | Retorno |
|--------|-------------|------------|---------|
| `extract_context_for_task()` | Extrae contexto para una tarea | `task`, `max_tokens` | `dict` |
| `filter_relevant_files()` | Filtra archivos relevantes | `task`, `limit` | `list` |
| `prioritize_components()` | Prioriza componentes | `task` | `list` |

## Clases de datos

### Template

Representa una plantilla para generación de contenido.

#### Atributos

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `name` | `str` | Nombre de la plantilla |
| `content` | `str` | Contenido de la plantilla |
| `variables` | `list` | Variables disponibles en la plantilla |
| `description` | `str` | Descripción de la plantilla |

### GeneratedContent

Representa contenido generado por alguno de los generadores.

#### Atributos

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `content` | `str` | Contenido generado |
| `metadata` | `dict` | Metadatos sobre la generación |
| `format` | `str` | Formato del contenido |
