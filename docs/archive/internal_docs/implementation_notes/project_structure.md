# Estructura de archivos ProjectPrompt

Este documento describe la estructura de archivos utilizada por ProjectPrompt para almacenar análisis y prompts contextuales.

## Estructura básica

La estructura de archivos se crea en la carpeta `.project-prompt/` en la raíz del proyecto analizado:

```
.project-prompt/
├── project-analysis.md           # Análisis general
├── functionalities/              # Análisis por funcionalidad
│   ├── auth.md
│   ├── database.md
│   └── ...
├── prompts/                      # Prompts contextuales
│   ├── general.md
│   └── functionality/
│       ├── auth.md
│       └── ...
└── config.yaml                   # Configuración
```

## Archivos principales

### project-analysis.md

Contiene el análisis general del proyecto, incluyendo:
- Estructura de directorios
- Lenguajes detectados
- Tecnologías y frameworks
- Conexiones entre componentes

### functionalities/*.md

Cada archivo en el directorio `functionalities/` contiene un análisis específico de una funcionalidad detectada en el proyecto. Incluye:
- Descripción de la funcionalidad
- Archivos relacionados
- Dependencias
- Notas y observaciones

### prompts/general.md

Contiene el prompt contextual general para el proyecto, que puede ser utilizado con asistentes IA para obtener respuestas más relevantes sobre el proyecto.

### prompts/functionality/*.md

Cada archivo en este directorio contiene un prompt contextual específico para una funcionalidad del proyecto, optimizado para obtener respuestas relevantes sobre esa parte específica.

### config.yaml

Contiene la configuración de ProjectPrompt para este proyecto:
- Nombre del proyecto
- Versión
- Idioma preferido
- Configuración de estructura

## Metadata

Todos los archivos `.md` contienen metadata en formato frontmatter YAML, incluyendo:
- title: Título del archivo
- date: Fecha de creación/actualización
- version: Versión del contenido
- type: Tipo de documento (análisis, prompt)
- functionality: Nombre de la funcionalidad (si aplica)

## Comandos CLI disponibles

Para gestionar esta estructura:

```bash
# Inicializar estructura
python -m src.main project-structure --init

# Mostrar información sobre la estructura
python -m src.main project-structure --info

# Eliminar estructura
python -m src.main project-structure --clean

# Crear archivos para una funcionalidad
python -m src.main functionality-files nombre_funcionalidad --description "Descripción"

# Generar prompts contextuales y guardarlos en la estructura
python -m src.main generate-prompts --store
```
