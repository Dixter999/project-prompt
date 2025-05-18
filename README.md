# ProjectPrompt: Generación de prompts contextuales (Básico y Mejorado)

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

## Estado del proyecto

En desarrollo activo. Versión actual: 0.1.0

## Guía de Ejecución

### Configuración Inicial

```bash
# Clonar el repositorio
git clone https://github.com/projectprompt/project-prompt.git
cd project-prompt

# Instalar dependencias
pip install -r requirements.txt

# Configurar el entorno (opcional)
cp config.yaml.example config.yaml
```

### Ejecución Básica

```bash
# Iniciar el análisis de un proyecto
python -m src.main analyze --path /ruta/a/tu/proyecto

# Generar prompts contextuales
python -m src.main generate --output prompts.json

# Ejecutar en modo avanzado (requiere API key)
python -m src.main generate --enhanced --output prompts_enhanced.json
```

### Configuración de API para IA

```bash
# Configurar API de Anthropic
python set_anthropic_key.py --key TU_CLAVE_API
```

### Sistema Freemium

El proyecto implementa un sistema de verificación freemium:

```bash
# Verificar estado del sistema freemium
./run_freemium_tests.sh

# Verificar en modo simulación (sin API keys)
./run_freemium_tests.sh --simulate

# Verificar componentes individuales
python test_freemium_system.py --test license
python test_freemium_system.py --test subscription
python test_freemium_system.py --test anthropic
```

### Actualizaciones

```bash
# Verificar actualizaciones disponibles
python -m src.utils.updater

# Actualizar el sistema
python -m src.main update
```

Para más detalles sobre el sistema freemium, consultar la [guía de verificación](docs/freemium_system_verification_guide.md).

## Licencia

MIT
