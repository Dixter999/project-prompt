# Project-Prompt Architecture

This document provides an overview of the Project-Prompt architecture and component design.

## High-Level Architecture

Project-Prompt follows a modular architecture with well-defined components:

```
                   ┌────────────┐
                   │    CLI     │
                   └─────┬──────┘
                         │
                         ▼
┌──────────┐       ┌────────────┐       ┌──────────────┐
│  Config  │◄─────►│    Core    │◄─────►│  Analyzers   │
└──────────┘       └─────┬──────┘       └──────────────┘
                         │
                         ▼
┌──────────┐       ┌────────────┐       ┌──────────────┐
│ Templates │◄─────►│ Generators │◄─────►│ AI Services  │
└──────────┘       └─────┬──────┘       └──────────────┘
                         │
                         ▼
                   ┌────────────┐
                   │   Output   │
                   └────────────┘
```

## Core Components

### 1. CLI Interface (`src/ui/cli.py`)

Provides the command-line interface for interacting with Project-Prompt, including:
- Command parsing and execution
- Interactive menus
- Output formatting

### 2. Core Engine (`src/core/`)

The central component that orchestrates the analysis, generation, and output processes:
- Project scanning
- Analysis coordination
- Output management

### 3. Project Analyzers (`src/analyzers/`)

Responsible for analyzing projects and extracting relevant information:
- Language detection
- Dependency analysis
- Structure analysis
- Functionality detection

### 4. Prompt Generators (`src/generators/`)

Generate contextual prompts based on project analysis:
- Context distillation
- Template application
- Format conversion

### 5. AI Service Integrations (`src/integrations/`)

Integrate with various AI models:
- Anthropic Claude
- OpenAI (future)
- Other AI providers (future)

### 6. Configuration System (`src/utils/config.py`)

Manages user configuration and preferences:
- User settings
- API keys
- Feature toggles

### 7. Template System (`src/templates/`)

Provides templates for various project types and functionalities:
- Project templates
- Prompt templates
- Output templates

## Data Flow

1. User invokes CLI with command and options
2. Core engine initializes and loads configuration
3. Project is scanned and analyzed
4. Analysis results are processed and relevant context extracted
5. Templates are applied to generate prompts
6. (Optional) AI services are called for advanced functionality
7. Results are formatted and output generated
8. Output is presented to user or saved to files

## Extension Points

Project-Prompt is designed for extensibility:

1. **Custom Analyzers**:
   - Implement the Analyzer interface
   - Register in the analyzer registry

2. **Custom Templates**:
   - Add new template files
   - Register in the template registry

3. **New AI Integrations**:
   - Implement the AIService interface
   - Register in the service registry

## File Organization

The project follows a modular structure:

```
src/
├── __init__.py            # Package initialization
├── main.py                # Main entry point
├── analyzers/             # Project analysis modules
├── api/                   # API endpoints
├── core/                  # Core functionality
├── generators/            # Prompt generators
├── integrations/          # AI service integrations
├── templates/             # Templates
├── ui/                    # User interfaces
└── utils/                 # Utility functions
```

## Key Design Principles

1. **Modularity**: Components are loosely coupled and can be replaced or extended
2. **Extensibility**: Key components have extension points
3. **Configurability**: Behavior can be configured without code changes
4. **Testability**: Components are designed to be testable in isolation

## Future Architecture Considerations

1. **Plugin System**: Formalize plugin architecture for third-party extensions
2. **API Server**: Provide REST API for integrating with other tools
3. **UI Applications**: Web and desktop interfaces
4. **Distributed Processing**: Handle larger projects via distributed analysis
