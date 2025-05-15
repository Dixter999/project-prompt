# Fase 2: Análisis Básico de Proyectos (Nivel Gratuito)

## Descripción
Esta fase implementa la funcionalidad básica de análisis de proyectos, disponible en la versión gratuita. Permitirá escanear un proyecto VSCode, identificar su estructura y crear una representación en markdown.

## Tareas

### 2.1 Detección de estructura de proyectos
- **Branch**: `feature/project-structure-detector`
- **Descripción**: Crear un sistema para detectar la estructura de un proyecto VSCode.
- **Archivos a crear**:
  - `src/analyzers/project_scanner.py` - Escaneo de estructura
  - `src/analyzers/file_analyzer.py` - Análisis básico de archivos
  - `src/analyzers/__init__.py` - Inicializador
- **Funcionalidades**:
  - Detección recursiva de archivos y directorios
  - Identificación de archivos importantes (main, index, etc.)
  - Reconocimiento de lenguajes de programación
  - Mapa de dependencias básico

### 2.2 Generación de reportes en Markdown
- **Branch**: `feature/markdown-reports`
- **Descripción**: Implementar generación de reportes en formato Markdown.
- **Archivos a crear**:
  - `src/generators/markdown_generator.py` - Generador de MD
  - `src/generators/templates/project_report.md` - Plantilla de reporte
  - `src/generators/__init__.py` - Inicializador
- **Funcionalidades**:
  - Creación de documentos MD con estructura del proyecto
  - Visualización de archivos clave
  - Inclusión de estadísticas básicas
  - Almacenamiento en directorio `.project-prompt` del proyecto

### 2.3 Identificación básica de funcionalidades
- **Branch**: `feature/basic-functionality-detector`
- **Descripción**: Detectar funcionalidades básicas en el proyecto.
- **Archivos a crear**:
  - `src/analyzers/functionality_detector.py` - Detector de funcionalidades
  - `src/templates/common_functionalities.py` - Funcionalidades comunes
  - `src/templates/__init__.py` - Inicializador
- **Funcionalidades a detectar**:
  - Autenticación/Login
  - Base de datos
  - APIs
  - Frontend/UI
  - Tests

### 2.4 Integración en CLI y comando de análisis
- **Branch**: `feature/analyze-command`
- **Descripción**: Integrar el análisis en la interfaz de comandos.
- **Archivos a modificar**:
  - `src/ui/cli.py` - Añadir comando de análisis
  - `src/main.py` - Actualizar punto de entrada
- **Archivos a crear**:
  - `src/ui/analysis_view.py` - Vista de resultados de análisis
- **Comandos a implementar**:
  - `project-prompt analyze` - Análisis completo
  - `project-prompt list` - Listar funcionalidades detectadas

### 2.5 Creación de prompts contextuales básicos
- **Branch**: `feature/basic-prompts`
- **Descripción**: Generar prompts básicos basados en el análisis.
- **Archivos a crear**:
  - `src/generators/prompt_generator.py` - Generador de prompts
  - `src/templates/prompt_templates.py` - Plantillas de prompts
- **Tipos de prompts**:
  - Descripción general del proyecto
  - Sugerencias de mejora básicas
  - Identificación de posibles problemas
- **Limitaciones freemium**:
  - Máximo 3 prompts por análisis
  - Sin prompts específicos para funcionalidades