# Projec# Generación de prompts contextuales (Básico y Mejorado)Prompt

Asistente inteligente para análisis y documentación de proyectos que utiliza IA para generar prompts contextuales y guiar el desarrollo.

## Características

- Análisis de estructura de proyectos
- Detección de funcionalidades
- Generación de prompts contextuales
- Documentación progresiva
- Integración con IDEs

## Instalación

```bash
# Con pip
pip install project-prompt

# Con Poetry
poetry add project-prompt
```

## Uso básico

```bash
# Inicializar un proyecto
project-prompt init

# Analizar un proyecto
project-prompt analyze

# Generar prompts básicos
project-prompt generate_prompts

# Generar prompts contextuales mejorados
project-prompt generate_prompts --enhanced

# Ver ayuda
project-prompt --help
```

## Modelos de IA compatibles

- OpenAI GPT (API key requerida)
- Anthropic Claude (API key requerida)
- Funcionalidad básica sin API keys

## Generador de Prompts Contextuales Mejorados

El generador de prompts contextuales mejorado (`--enhanced`) ofrece capacidades avanzadas:

- Inclusión automática de contexto específico del proyecto en los prompts
- Referencias directas a archivos relevantes para cada funcionalidad
- Sugerencias basadas en patrones detectados en el código
- Sistema de preguntas guiadas para clarificar aspectos poco claros
- Análisis de arquitectura basado en grafos de dependencias
- Generación de prompts específicos para completado de código

## Modelo Freemium

- **Gratuito**: Análisis de estructura básico, detección de funcionalidades estándar
- **Premium**: Análisis profundo, generación avanzada de prompts, documentación detallada

## Licencia

MIT

## Estado del proyecto

En desarrollo activo. Versión actual: 0.1.0
