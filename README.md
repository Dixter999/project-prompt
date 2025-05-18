# ProjectPrompt: Generación de prompts contextuales (Básico y Mejorado)

Asistente inteligente para análisis y documentación de proyectos que utiliza IA para generar prompts contextuales y guiar el desarrollo.

## Características

- Análisis de estructura de proyectos
- Detección de funcionalidades
- Generación de prompts contextuales
- Documentación progresiva
- Integración con IDEs

## Instalación

### Opción 1: Instalación rápida desde el repositorio

```bash
# Descargar el repositorio
git clone https://github.com/projectprompt/project-prompt.git
cd project-prompt

# Crear enlaces simbólicos a los scripts
mkdir -p $HOME/bin
ln -sf $(pwd)/project_prompt.py $HOME/bin/project-prompt
chmod +x $HOME/bin/project-prompt

# Asegurar que $HOME/bin está en PATH
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc  # o ~/.zshrc para zsh
source ~/.bashrc  # o source ~/.zshrc
```

### Opción 2: Instalación con pip (próximamente)

```bash
# Con pip
pip install project-prompt

# Con Poetry
poetry add project-prompt
```

## Uso básico

```bash
# Inicializar un nuevo proyecto
project-prompt init mi-proyecto

# Analizar un proyecto existente
project-prompt analyze

# Analizar un proyecto específico
project-prompt analyze /ruta/a/mi/proyecto
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

En desarrollo activo. Versión actual: 1.0.0

### Componentes Funcionales

- **Analizador Rápido**: Análisis de estructura de proyectos, detectando lenguajes y archivos importantes.
- **Inicializador de Proyectos**: Creación de nuevos proyectos con estructura básica y configuración.
- **Herramientas de Línea de Comandos**: Interfaz unificada para acceder a todas las funcionalidades.

## Guía de Ejecución

### Configuración Inicial

```bash
# Clonar el repositorio
git clone https://github.com/projectprompt/project-prompt.git
cd project-prompt

# Instalar dependencias (opcional)
pip install -r requirements.txt

# Configurar comando directo (recomendado)
mkdir -p $HOME/bin
ln -sf $(pwd)/project_prompt.py $HOME/bin/project-prompt
chmod +x $HOME/bin/project-prompt

# Asegurar que $HOME/bin está en PATH
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc  # o ~/.bashrc para bash
source ~/.zshrc  # o source ~/.bashrc
```

### Ejecución Básica

```bash
# Analizar el proyecto actual
project-prompt analyze .

# Guardar análisis en archivo JSON
project-prompt analyze . resultados.json

# Inicializar un nuevo proyecto
project-prompt init mi-proyecto

# Ver opciones disponibles
project-prompt --help
```

### Ejecución Manual

```bash
# Usar scripts directamente
python quick_analyze.py /ruta/a/tu/proyecto
python quick_init.py nuevo-proyecto

# Usar script integrado
python project_prompt.py analyze /ruta/a/tu/proyecto
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

Para más detalles sobre el sistema freemium, consultar la [guía de verificación](docs/developer/freemium_system.md) o la [documentación completa](docs/complete_documentation.md#freemium-system).

## Documentación Completa

ProjectPrompt cuenta con una documentación unificada y detallada que explica todas sus funciones y características:

- [Documentación Completa](docs/complete_documentation.md) - Manual completo con todas las funciones
  - También disponible [en Español](docs/documentacion_completa_es.md)
- [Guía del Usuario](docs/user_guide.md) - Manual paso a paso para usuarios
- [Referencia de Scripts](docs/script_reference.md) - Información detallada de cada script
- [Sistema Freemium](docs/developer/freemium_system.md) - Documentación sobre las características freemium

## Testing

ProjectPrompt incluye un completo framework de pruebas para verificar todas sus funcionalidades:

```bash
# Ejecutar todas las pruebas
./test_projectprompt.sh

# Ejecutar pruebas avanzadas
./enhanced_test_projectprompt.sh
```

Para información detallada sobre cómo probar ProjectPrompt, consulte la [Guía de Testing](docs/testing_guide.md) y la [Guía de Testing Comprehensiva](docs/comprehensive_testing_guide.md).

### Proyecto de prueba

Un proyecto de muestra (Weather API) está incluido en `test-projects/weather-api` para facilitar las pruebas y demostraciones. Este proyecto contiene una estructura típica de una aplicación Python que puede ser analizada por ProjectPrompt.

## Licencia

MIT
