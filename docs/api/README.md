# Documentación de la API de ProjectPrompt

Esta sección contiene la documentación técnica detallada sobre la API de ProjectPrompt, incluyendo módulos, clases y funciones.

## Estructura

La documentación de la API está organizada por módulos principales:

- [Analizadores](./reference/analyzers.md): Componentes para análisis de proyectos
- [Generadores](./reference/generators.md): Componentes para generación de prompts y contenido
- [Integraciones](./reference/integrations.md): Conectores con servicios externos
- [Utilidades](./reference/utils.md): Funciones y clases de utilidad

## Uso programático

ProjectPrompt está diseñado para ser utilizado no solo como una herramienta independiente, sino también como una biblioteca que puede integrarse en otras aplicaciones Python.

### Instalación como biblioteca

```bash
pip install project-prompt
```

### Uso básico

```python
from project_prompt import ProjectAnalyzer, PromptGenerator

# Analizar un proyecto
analyzer = ProjectAnalyzer(project_path="/ruta/a/tu/proyecto")
project_data = analyzer.analyze()

# Generar un prompt contextual
generator = PromptGenerator()
prompt = generator.generate(
    project_data=project_data,
    task="Implementar autenticación de usuarios",
    model="gpt-4"
)

print(prompt)
```

## Ejemplos

Para ver ejemplos prácticos de uso de la API, consulta la sección de [ejemplos](../examples/).
