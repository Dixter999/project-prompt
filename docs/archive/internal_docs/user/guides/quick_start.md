# Guía de inicio rápido

Esta guía te ayudará a comenzar a utilizar ProjectPrompt en pocos minutos.

## Instalación

### Requisitos previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Acceso a una terminal o línea de comandos

### Instalación desde PyPI

```bash
pip install project-prompt
```

### Instalación desde el código fuente

```bash
git clone https://github.com/usuario/project-prompt.git
cd project-prompt
pip install -e .
```

## Configuración inicial

Después de instalar ProjectPrompt, ejecuta el siguiente comando para configurar la herramienta:

```bash
project-prompt config --init
```

Esto iniciará un asistente interactivo que te guiará a través del proceso de configuración.

### Configuración de API Keys

Para utilizar modelos de IA, necesitarás configurar tus claves de API:

```bash
project-prompt config --api-key openai
```

## Comandos básicos

### Analizar un proyecto

```bash
project-prompt analyze --path ./mi-proyecto
```

### Generar un prompt contextual

```bash
project-prompt generate --path ./mi-proyecto --task "implementar autenticación"
```

### Ver ayuda completa

```bash
project-prompt --help
```

## Próximos pasos

- Explora los [tutoriales detallados](../tutorials/README.md) para aprender más funcionalidades
- Consulta la [referencia de comandos](../reference/commands.md) para ver todas las opciones disponibles
- Prueba la [extensión de VSCode](../tutorials/vscode_extension.md) para integrar ProjectPrompt en tu editor
