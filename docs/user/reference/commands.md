# Referencia completa de comandos

Esta página contiene una referencia detallada de todos los comandos disponibles en ProjectPrompt, organizados por categorías.

## Comandos principales

### project-prompt

El comando principal que inicia la aplicación.

```bash
project-prompt [opciones]
```

Opciones globales:
- `--verbose`: Muestra información detallada durante la ejecución
- `--quiet`: Suprime todos los mensajes no esenciales
- `--help`: Muestra la ayuda del comando
- `--version`: Muestra la versión de la aplicación

## Comandos de análisis

### analyze

Analiza un proyecto y muestra su estructura y características.

```bash
project-prompt analyze [opciones]
```

Opciones:
- `--path PATH`: Ruta al proyecto a analizar (por defecto: directorio actual)
- `--depth DEPTH`: Nivel de profundidad máximo para el análisis
- `--exclude PATTERN`: Patrón para excluir archivos o directorios
- `--output FORMAT`: Formato de salida (json, yaml, markdown)
- `--save FILE`: Guarda el resultado en un archivo

### detect

Detecta automáticamente características específicas en el proyecto.

```bash
project-prompt detect [opciones]
```

Opciones:
- `--path PATH`: Ruta al proyecto
- `--feature FEATURE`: Característica específica a detectar (frameworks, lenguajes, dependencias)
- `--output FORMAT`: Formato de salida

## Comandos de generación

### generate

Genera prompts contextuales basados en el proyecto actual.

```bash
project-prompt generate [opciones]
```

Opciones:
- `--path PATH`: Ruta al proyecto
- `--task TASK`: Tarea para la que generar el prompt
- `--model MODEL`: Modelo de IA al que optimizar (gpt4, claude, etc.)
- `--context LEVEL`: Nivel de contexto a incluir (min, medium, max)
- `--output FILE`: Archivo donde guardar el prompt generado

### template

Gestiona plantillas de prompts.

```bash
project-prompt template [acción] [opciones]
```

Acciones:
- `list`: Lista las plantillas disponibles
- `create`: Crea una nueva plantilla
- `edit`: Edita una plantilla existente
- `delete`: Elimina una plantilla

## Comandos de configuración

### config

Gestiona la configuración de la aplicación.

```bash
project-prompt config [acción] [opciones]
```

Acciones:
- `--init`: Inicializa la configuración con un asistente interactivo
- `--show`: Muestra la configuración actual
- `--edit`: Abre el archivo de configuración en el editor predeterminado
- `--api-key PROVIDER`: Configura una clave de API (openai, anthropic, etc.)
- `--reset`: Restablece la configuración a los valores predeterminados

## Comandos de sincronización

### sync

Sincroniza configuraciones y plantillas entre dispositivos o con un repositorio remoto.

```bash
project-prompt sync [opciones]
```

Opciones:
- `--pull`: Descarga la configuración desde el repositorio remoto
- `--push`: Sube la configuración local al repositorio remoto
- `--repo URL`: URL del repositorio de sincronización

## Comandos de actualización

### update

Actualiza ProjectPrompt a la última versión.

```bash
project-prompt update [opciones]
```

Opciones:
- `--check`: Solo comprueba si hay actualizaciones disponibles
- `--force`: Fuerza la actualización incluso si no es necesario

## Comandos de documentación

### docs

Muestra la documentación o genera documentación para el proyecto.

```bash
project-prompt docs [opciones]
```

Opciones:
- `--generate`: Genera documentación para el proyecto actual
- `--format FORMAT`: Formato de la documentación (markdown, html)
- `--output DIR`: Directorio donde guardar la documentación generada
