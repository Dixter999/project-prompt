# Módulo de Integraciones (Integrations)

El módulo `integrations` contiene componentes que permiten a ProjectPrompt interactuar con servicios externos, como modelos de IA y sistemas de control de versiones.

## Clases principales

### AIModelIntegrator

Clase base para integración con modelos de inteligencia artificial.

```python
from project_prompt.integrations import get_ai_model

# Obtener un integrador específico
model = get_ai_model(provider="openai", model_name="gpt-4")

# Enviar un prompt
response = model.complete(prompt="Explica cómo implementar autenticación en Python.")
```

#### Métodos comunes en subclases

| Método | Descripción | Parámetros | Retorno |
|--------|-------------|------------|---------|
| `complete()` | Obtiene una respuesta del modelo | `prompt`, `options` | `str` |
| `is_available()` | Comprueba si el modelo está disponible | - | `bool` |
| `estimate_cost()` | Estima el costo de la solicitud | `prompt` | `float` |

### Integraciones específicas

#### OpenAIIntegrator

Integración específica para modelos de OpenAI.

```python
from project_prompt.integrations.ai_models import OpenAIIntegrator

model = OpenAIIntegrator(
    model_name="gpt-4",
    api_key="tu-api-key"
)
response = model.complete(
    prompt="Explica cómo implementar autenticación en Python.",
    temperature=0.7,
    max_tokens=500
)
```

#### AnthropicIntegrator

Integración específica para modelos de Anthropic (Claude).

```python
from project_prompt.integrations.ai_models import AnthropicIntegrator

model = AnthropicIntegrator(
    model_name="claude-v1",
    api_key="tu-api-key"
)
response = model.complete(prompt="Explica cómo implementar autenticación en Python.")
```

### VersionControlIntegrator

Clase base para integración con sistemas de control de versiones.

```python
from project_prompt.integrations import get_vcs

# Obtener un integrador específico
vcs = get_vcs(system="git", repo_path="/ruta/al/proyecto")

# Obtener cambios recientes
changes = vcs.get_recent_changes(limit=10)
```

#### Métodos comunes en subclases

| Método | Descripción | Parámetros | Retorno |
|--------|-------------|------------|---------|
| `get_recent_changes()` | Obtiene cambios recientes | `limit` | `list` |
| `get_file_history()` | Obtiene historial de un archivo | `file_path` | `list` |
| `get_contributors()` | Obtiene lista de contribuidores | - | `list` |

### GitIntegrator

Integración específica para repositorios Git.

```python
from project_prompt.integrations.vcs import GitIntegrator

git = GitIntegrator(repo_path="/ruta/al/proyecto")
branches = git.get_branches()
changes = git.get_recent_changes(branch="main", limit=5)
```

#### Métodos específicos

| Método | Descripción | Parámetros | Retorno |
|--------|-------------|------------|---------|
| `get_branches()` | Obtiene ramas del repositorio | - | `list` |
| `get_commits()` | Obtiene commits | `branch`, `limit` | `list` |
| `get_diff()` | Obtiene diferencias | `commit_a`, `commit_b` | `str` |

## Clases de datos

### AIModelResponse

Representa una respuesta de un modelo de IA.

#### Atributos

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `content` | `str` | Contenido de la respuesta |
| `model` | `str` | Modelo que generó la respuesta |
| `usage` | `dict` | Información de uso (tokens, etc.) |
| `metadata` | `dict` | Metadatos adicionales |

### VCSChange

Representa un cambio en un sistema de control de versiones.

#### Atributos

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `id` | `str` | Identificador del cambio (hash, etc.) |
| `author` | `str` | Autor del cambio |
| `date` | `datetime` | Fecha y hora del cambio |
| `message` | `str` | Mensaje asociado al cambio |
| `files` | `list` | Archivos modificados |
