# Ejemplos de uso de la API de ProjectPrompt

Este documento contiene ejemplos prácticos de uso de la API de ProjectPrompt para diferentes escenarios.

## 1. Análisis básico de proyecto

```python
from project_prompt import ProjectAnalyzer

# Inicializar el analizador
analyzer = ProjectAnalyzer(
    project_path="/ruta/a/tu/proyecto",
    exclude_patterns=["node_modules", "venv", "__pycache__"]
)

# Analizar el proyecto
analysis = analyzer.analyze()

# Mostrar estadísticas básicas
print(f"Archivos encontrados: {analysis.file_count}")
print(f"Lenguajes detectados: {', '.join(analysis.language_stats.keys())}")
print(f"Tecnologías detectadas: {', '.join(analysis.detected_technologies)}")

# Mostrar estructura del proyecto
analyzer.print_structure(max_depth=3)
```

## 2. Generación de prompts contextuales

```python
from project_prompt import ProjectAnalyzer, PromptGenerator

# Analizar el proyecto
analyzer = ProjectAnalyzer("/ruta/a/tu/proyecto")
project_data = analyzer.analyze()

# Configurar el generador
generator = PromptGenerator(
    default_model="gpt-4",
    context_level="medium"
)

# Generar un prompt para una tarea específica
prompt = generator.generate(
    project_data=project_data,
    task="Implementar un sistema de autenticación con JWT",
    additional_context="Estamos usando Express.js en el backend."
)

# Imprimir el prompt generado
print(prompt)

# Obtener la versión optimizada para un modelo específico
optimized_prompt = generator.optimize_for_model(
    prompt=prompt,
    model="claude-v1"
)

print("\nPrompt optimizado para Claude:")
print(optimized_prompt)
```

## 3. Uso del gestor de plantillas

```python
from project_prompt import TemplateManager, ProjectAnalyzer

# Analizar el proyecto
analyzer = ProjectAnalyzer("/ruta/a/tu/proyecto")
project_data = analyzer.analyze()

# Inicializar el gestor de plantillas
template_manager = TemplateManager()

# Listar plantillas disponibles
available_templates = template_manager.list_templates()
print("Plantillas disponibles:")
for template in available_templates:
    print(f"- {template.name}: {template.description}")

# Usar una plantilla existente
rendered = template_manager.render_template(
    template_name="project_overview",
    context={
        "project": project_data,
        "user_name": "Developer"
    }
)

print("\nResultado:")
print(rendered)

# Crear una plantilla personalizada
template_manager.create_template(
    name="custom_prompt",
    content="""
    # Análisis de proyecto: {{project.name}}
    
    ## Estructura
    {{project.structure_summary}}
    
    ## Tarea
    {{task}}
    
    ## Contexto adicional
    {{additional_context}}
    """,
    description="Plantilla personalizada para análisis de proyecto"
)

# Usar la plantilla personalizada
custom_rendered = template_manager.render_template(
    template_name="custom_prompt",
    context={
        "project": project_data,
        "task": "Implementar sistema de notificaciones",
        "additional_context": "El sistema debe ser en tiempo real."
    }
)

print("\nPlantilla personalizada:")
print(custom_rendered)
```

## 4. Integración con modelos de IA

```python
from project_prompt import ProjectAnalyzer, PromptGenerator, AIModelIntegrator

# Analizar proyecto
analyzer = ProjectAnalyzer("/ruta/a/tu/proyecto")
project_data = analyzer.analyze()

# Generar prompt
generator = PromptGenerator()
prompt = generator.generate(
    project_data=project_data,
    task="Crear endpoints REST para usuarios"
)

# Conectar con un modelo de IA
model = AIModelIntegrator.create(
    provider="openai",
    model_name="gpt-4",
    api_key="tu-api-key-aquí"  # Mejor usar variables de entorno en producción
)

# Obtener respuesta
response = model.complete(
    prompt=prompt,
    max_tokens=1000,
    temperature=0.7
)

print("Respuesta del modelo:")
print(response.content)

# Estimar costo
cost = model.estimate_cost(prompt, response.usage.total_tokens)
print(f"\nCosto estimado: ${cost:.4f}")
```

## 5. Generación de documentación

```python
from project_prompt import DocumentationGenerator

# Inicializar el generador de documentación
doc_generator = DocumentationGenerator(
    project_path="/ruta/a/tu/proyecto",
    output_format="markdown"
)

# Generar documentación para todo el proyecto
docs = doc_generator.generate_documentation()

# Guardar la documentación
doc_generator.save_documentation(
    docs,
    output_dir="/ruta/a/documentacion"
)

print("Documentación generada en /ruta/a/documentacion")

# Generar solo un README
readme = doc_generator.generate_readme()
with open("/ruta/a/tu/proyecto/README.md", "w") as f:
    f.write(readme)

print("README generado")
```

## 6. Uso avanzado con flujos completos

```python
from project_prompt import ProjectPrompt

# Crear instancia de la aplicación
app = ProjectPrompt()

# Flujo completo: analizar proyecto, generar prompt, obtener respuesta y procesar
result = app.process_task(
    project_path="/ruta/a/tu/proyecto",
    task="Refactorizar la clase DatabaseManager para seguir principios SOLID",
    model="gpt-4",
    output_format="markdown",
    save_result=True,
    output_file="refactoring_proposal.md"
)

print(f"Resultado guardado en {result.output_path}")

# Ejecutar una sesión interactiva
app.start_interactive_session(
    project_path="/ruta/a/tu/proyecto",
    context_level="high"
)
```
