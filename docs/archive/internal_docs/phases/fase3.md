# Fase 3: Sistema de Documentación y Prompts Contextuales

## Descripción
Esta fase implementa el sistema de documentación progresiva y la generación de prompts contextuales más avanzados, creando la estructura de archivos markdown que almacenarán el análisis y las sugerencias.

## Tareas

### 3.1 Sistema de documentación en markdown
- **Branch**: `feature/markdown-documentation-system`
- **Descripción**: Implementar sistema para crear y gestionar documentación markdown.
- **Archivos a crear**:
  - `src/utils/markdown_manager.py` - Gestión de archivos markdown
  - `src/templates/documentation/` - Directorio con plantillas
  - `src/templates/documentation/project_analysis.md` - Análisis general
  - `src/templates/documentation/functionality.md` - Plantilla para funcionalidades
- **Funcionalidades**:
  - Creación de estructura de documentación
  - Sistema de plantillas flexibles
  - Actualización de documentos existentes
  - Historial de cambios

### 3.2 Análisis de conexiones entre archivos
- **Branch**: `feature/file-connections-analyzer`
- **Descripción**: Detectar conexiones entre archivos (imports, dependencias) excluyendo archivos no relevantes.
- **Archivos a crear**:
  - `src/analyzers/connection_analyzer.py` - Análisis de conexiones
  - `src/analyzers/dependency_graph.py` - Generación de grafo de dependencias
- **Funcionalidades**:
  - Detección de imports en Python, JavaScript, etc.
  - Análisis de dependencias entre archivos
  - Visualización de grafo (texto en markdown)
  - Identificación de componentes desconectados
- **Exclusiones importantes**:
  - Imágenes (jpg, png, gif, svg, etc.)
  - Videos (mp4, webm, etc.)
  - Archivos multimedia en general
  - HTML puramente presentacionales (sin lógica)
  - Archivos de recursos y binarios
  - Cualquier otro archivo que no contribuya a la estructura de dependencias del código

### 3.3 Generación de prompts contextuales mejorados
- **Branch**: `feature/enhanced-prompts`
- **Descripción**: Mejorar la generación de prompts con contexto más específico.
- **Archivos a crear**:
  - `src/generators/contextual_prompt_generator.py` - Generador contextual
  - `src/templates/prompts/` - Directorio con plantillas de prompts
  - `src/templates/prompts/functionality_analysis.md` - Plantilla de análisis
- **Mejoras**:
  - Inclusión de contexto específico del proyecto
  - Referencias a archivos concretos
  - Sugerencias basadas en patrones detectados
  - Preguntas guiadas para aclarar funcionalidades poco claras

### 3.4 Implementación de la estructura de archivos del proyecto
- **Branch**: `feature/project-files-structure`
- **Descripción**: Crear estructura de archivos para almacenar análisis y prompts.
- **Estructura a implementar**:
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
- **Funcionalidades**:
  - Creación automática de la estructura
  - Plantillas específicas por tipo de archivo
  - Detección de estructura existente
  - Actualización incremental

### 3.5 Interfaz de usuario para navegación de documentación
- **Branch**: `feature/documentation-navigator`
- **Descripción**: Implementar navegación de la documentación desde CLI.
- **Archivos a crear**:
  - `src/ui/documentation_navigator.py` - Navegador de documentación
  - `src/ui/markdown_viewer.py` - Visor de markdown
- **Comandos a implementar**:
  - `project-prompt docs` - Mostrar documentación
  - `project-prompt docs list` - Listar documentos
  - `project-prompt docs view [path]` - Ver documento específico