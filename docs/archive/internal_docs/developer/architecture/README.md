# Arquitectura de ProjectPrompt

Este documento describe la arquitectura general de ProjectPrompt, explicando sus componentes principales y cómo interactúan entre sí.

## Visión general

ProjectPrompt está diseñado siguiendo una arquitectura modular con componentes claramente separados, lo que facilita las pruebas, el mantenimiento y la extensión del sistema.

```
                   ┌────────────────────┐
                   │                    │
                   │      CLI/GUI       │
                   │                    │
                   └─────────┬──────────┘
                             │
                   ┌─────────▼──────────┐
                   │                    │
┌──────────────────►  Core Controller   ◄────────────────┐
│                  │                    │                │
│                  └─────────┬──────────┘                │
│                            │                           │
│                  ┌─────────▼──────────┐                │
│                  │                    │                │
│                  │  Service Manager   │                │
│                  │                    │                │
│                  └──┬──────┬──────┬───┘                │
│                     │      │      │                    │
│        ┌────────────┘      │      └────────┐           │
│        │                   │               │           │
│  ┌─────▼─────┐      ┌──────▼────┐    ┌─────▼─────┐     │
│  │           │      │           │    │           │     │
│  │ Analyzers │      │Generators │    │Integrators│     │
│  │           │      │           │    │           │     │
│  └─────┬─────┘      └─────┬─────┘    └─────┬─────┘     │
│        │                  │                │           │
│        │                  │                │           │
│        │                  │                │           │
│  ┌─────▼──────────────────▼────────────────▼─────┐     │
│  │                                              │     │
└──┤               Data Manager                   │     │
   │                                              │     │
   └──────────────────────┬───────────────────────┘     │
                          │                             │
                    ┌─────▼────┐                        │
                    │          │                        │
                    │ Storage  ├────────────────────────┘
                    │          │
                    └──────────┘
```

## Componentes principales

### 1. Interfaces de usuario (UI)

- **CLI** (`src/ui/cli.py`): Interfaz de línea de comandos
- **Wizards** (`src/ui/wizards/`): Asistentes interactivos para tareas complejas
- **Extensión VSCode** (`vscode-extension/`): Integración con Visual Studio Code

### 2. Controlador principal (Core)

- **Main Controller** (`src/main.py`): Punto de entrada y control central
- **Command Processor** (`src/utils/command_processor.py`): Procesa y dirige los comandos

### 3. Analizadores (Analyzers)

- **Project Structure Analyzer** (`src/analyzers/project_structure.py`): Analiza la estructura de proyectos
- **Dependency Graph** (`src/analyzers/dependency_graph.py`): Analiza dependencias entre componentes
- **Code Quality Analyzer** (`src/analyzers/code_quality_analyzer.py`): Evalúa la calidad del código
- **Functionality Detector** (`src/analyzers/advanced_functionality_detector.py`): Detecta frameworks y funcionalidades

### 4. Generadores (Generators)

- **Prompt Generator** (`src/generators/prompt_generator.py`): Crea prompts contextuales
- **Template Engine** (`src/generators/template_engine.py`): Motor de plantillas
- **Documentation Generator** (`src/generators/documentation_generator.py`): Genera documentación

### 5. Integraciones (Integrations)

- **AI Models** (`src/integrations/ai_models/`): Conectores para OpenAI, Anthropic, etc.
- **Version Control** (`src/integrations/vcs/`): Integración con sistemas de control de versiones
- **External APIs** (`src/integrations/apis/`): Conexiones con APIs externas

### 6. Gestor de datos (Data Manager)

- **Config Manager** (`src/utils/config_manager.py`): Gestión de configuraciones
- **Cache** (`src/utils/cache_manager.py`): Sistema de caché para operaciones costosas
- **Storage** (`src/utils/storage.py`): Persistencia de datos

### 7. Utilidades (Utilities)

- **Logger** (`src/utils/logger.py`): Sistema de registro
- **Updater** (`src/utils/updater.py`): Sistema de actualización
- **Sync Manager** (`src/utils/sync_manager.py`): Sincronización entre dispositivos

## Flujo de datos

1. El usuario interactúa con el sistema a través de la CLI, wizards o la extensión VSCode
2. El controlador principal recibe la solicitud y determina qué servicios necesita
3. Los analizadores procesan el proyecto y extraen información relevante
4. Los generadores utilizan esta información para crear prompts o documentación
5. Las integraciones conectan con servicios externos cuando es necesario
6. El gestor de datos maneja la persistencia y configuración

## Extensibilidad

La arquitectura está diseñada para ser fácilmente extensible:

- Nuevos analizadores pueden añadirse en `src/analyzers/`
- Nuevas plantillas pueden añadirse en `src/templates/`
- Nuevas integraciones con modelos de IA pueden añadirse en `src/integrations/ai_models/`

Para añadir una nueva funcionalidad, generalmente solo es necesario implementar la interfaz adecuada y registrarla en el sistema correspondiente.
