# Grafo de Dependencias del Proyecto

Proyecto: project-prompt
Ruta: /mnt/h/Projects/project-prompt
Total de archivos analizados: 98
Total de archivos excluidos: 11

## 📋 Archivos Excluidos por .gitignore
✅ **11 archivos excluidos** por las reglas de .gitignore
Esto ayuda a mantener el análisis enfocado en el código fuente relevante.

### Desglose de Exclusiones
| Tipo de exclusión | Cantidad |
|---|---|
| Por extensión (multimedia, binarios, etc.) | 0 |
| Por patrón (directorios/archivos no relevantes) | 0 |
| HTML puramente presentacional | 0 |
| **Por .gitignore** | **11** |

## Métricas del Grafo
| Métrica | Valor |
|---|---|
| Total Files | 138 |
| Total Dependencies | 872 |
| Average Dependencies | 6.32 |
| Important Files Count | 98 |
| Important Files Ratio | 0.71 |
| Complexity | high |
| Analysis Method | madge_enhanced |
| Performance Optimized | True |
| Files Analyzed | 98 |
| Groups Detected | 16 |

## Lenguajes Detectados
| Lenguaje | Archivos |
|---|---|
| python | 62 |
| python-ui | 17 |
| python-service | 12 |
| config | 2 |
| python-test | 5 |

## Componentes Conectados
Se detectaron 0 componentes conectados.

## Archivos Centrales
Archivos con mayor número de dependencias (entrada/salida):
- `src/main.py`: 41 conexiones (0 entrantes, 41 salientes)
- `src/ui/cli.py`: 26 conexiones (0 entrantes, 26 salientes)
- `src/generators/implementation_prompt_generator.py`: 17 conexiones (0 entrantes, 17 salientes)
- `src/ui/analysis_view.py`: 15 conexiones (0 entrantes, 15 salientes)
- `src/ui/documentation_navigator.py`: 15 conexiones (0 entrantes, 15 salientes)
- `src/utils/sync_manager.py`: 14 conexiones (0 entrantes, 14 salientes)
- `src/utils/updater.py`: 14 conexiones (0 entrantes, 14 salientes)
- `src/generators/contextual_prompt_generator.py`: 13 conexiones (0 entrantes, 13 salientes)
- `src/templates/backend-api/middleware/auth.py`: 13 conexiones (0 entrantes, 13 salientes)
- `src/templates/premium/premium_templates.py`: 13 conexiones (0 entrantes, 13 salientes)

## 📊 Grupos Funcionales Detectados
Los siguientes grupos funcionales fueron identificados en el proyecto:

### 1. Type: python
**Tipo:** file_type
**Archivos:** 62
**Descripción:** Grupo funcional: Type: python

**Archivos en el grupo:**
- `src/main.py` (importancia: 41.00)
- `src/generators/implementation_prompt_generator.py` (importancia: 17.00)
- `src/utils/sync_manager.py` (importancia: 14.00)
- `src/utils/updater.py` (importancia: 14.00)
- `src/generators/contextual_prompt_generator.py` (importancia: 13.00)
- `src/templates/premium/premium_templates.py` (importancia: 13.00)
- `src/utils/telemetry.py` (importancia: 13.00)
- `src/analyzers/project_progress_tracker.py` (importancia: 12.00)
- ... y 54 archivos más

**Grafo del grupo Type: python:**
```
Grupo: Type: python (62 archivos)
==================================================
  ... y 56 archivos más
```

### 2. Type: python-ui
**Tipo:** file_type
**Archivos:** 17
**Descripción:** Grupo funcional: Type: python-ui

**Archivos en el grupo:**
- `src/ui/cli.py` (importancia: 26.00)
- `src/ui/analysis_view.py` (importancia: 15.00)
- `src/ui/documentation_navigator.py` (importancia: 15.00)
- `src/ui/interview_system.py` (importancia: 13.00)
- `src/ui/markdown_viewer.py` (importancia: 12.00)
- `src/ui/menu.py` (importancia: 12.00)
- `src/ui/subscription_view.py` (importancia: 12.00)
- `src/ui/themes.py` (importancia: 12.00)
- ... y 9 archivos más

**Grafo del grupo Type: python-ui:**
```
Grupo: Type: python-ui (17 archivos)
==================================================
  ... y 11 archivos más
```

### 3. Directory: src/utils
**Tipo:** directory
**Archivos:** 22
**Descripción:** Grupo funcional: Directory: src/utils

**Archivos en el grupo:**
- `src/utils/sync_manager.py` (importancia: 14.00)
- `src/utils/updater.py` (importancia: 14.00)
- `src/utils/telemetry.py` (importancia: 13.00)
- `src/utils/config.py` (importancia: 11.00)
- `src/utils/generate_developer_credentials.py` (importancia: 11.00)
- `src/utils/api_validator.py` (importancia: 10.00)
- `src/utils/documentation_system.py` (importancia: 9.00)
- `src/utils/license_validator.py` (importancia: 9.00)
- ... y 14 archivos más

**Grafo del grupo Directory: src/utils:**
```
Grupo: Directory: src/utils (22 archivos)
==================================================
Estructura de directorio:
  📄 sync_manager.py (importancia: 14.0)
  📄 updater.py (importancia: 14.0)
  📄 telemetry.py (importancia: 13.0)
  📄 config.py (importancia: 11.0)
  📄 generate_developer_credentials.py (importancia: 11.0)
  📄 api_validator.py (importancia: 10.0)
  ... y 16 archivos más
```

### 4. Directory: src/ui
**Tipo:** directory
**Archivos:** 12
**Descripción:** Grupo funcional: Directory: src/ui

**Archivos en el grupo:**
- `src/ui/cli.py` (importancia: 26.00)
- `src/ui/analysis_view.py` (importancia: 15.00)
- `src/ui/documentation_navigator.py` (importancia: 15.00)
- `src/ui/interview_system.py` (importancia: 13.00)
- `src/ui/markdown_viewer.py` (importancia: 12.00)
- `src/ui/menu.py` (importancia: 12.00)
- `src/ui/subscription_view.py` (importancia: 12.00)
- `src/ui/themes.py` (importancia: 12.00)
- ... y 4 archivos más

**Grafo del grupo Directory: src/ui:**
```
Grupo: Directory: src/ui (12 archivos)
==================================================
Estructura de directorio:
  📄 cli.py (importancia: 26.0)
  📄 analysis_view.py (importancia: 15.0)
  📄 documentation_navigator.py (importancia: 15.0)
  📄 interview_system.py (importancia: 13.0)
  📄 markdown_viewer.py (importancia: 12.0)
  📄 menu.py (importancia: 12.0)
  ... y 6 archivos más
```

### 5. Directory: src/analyzers
**Tipo:** directory
**Archivos:** 16
**Descripción:** Grupo funcional: Directory: src/analyzers

**Archivos en el grupo:**
- `src/analyzers/project_progress_tracker.py` (importancia: 12.00)
- `src/analyzers/functionality_analyzer.py` (importancia: 11.00)
- `src/analyzers/dependency_graph.py` (importancia: 10.00)
- `src/analyzers/project_analyzer.py` (importancia: 10.00)
- `src/analyzers/__init__.py` (importancia: 10.00)
- `src/analyzers/advanced_functionality_detector.py` (importancia: 9.00)
- `src/analyzers/code_quality_analyzer.py` (importancia: 9.00)
- `src/analyzers/madge_analyzer.py` (importancia: 9.00)
- ... y 8 archivos más

**Grafo del grupo Directory: src/analyzers:**
```
Grupo: Directory: src/analyzers (16 archivos)
==================================================
Estructura de directorio:
  📄 project_progress_tracker.py (importancia: 12.0)
  📄 functionality_analyzer.py (importancia: 11.0)
  📄 dependency_graph.py (importancia: 10.0)
  📄 project_analyzer.py (importancia: 10.0)
  📄 __init__.py (importancia: 10.0)
  📄 advanced_functionality_detector.py (importancia: 9.0)
  ... y 10 archivos más
```

### 6. Type: python-service
**Tipo:** file_type
**Archivos:** 12
**Descripción:** Grupo funcional: Type: python-service

**Archivos en el grupo:**
- `src/templates/backend-api/middleware/auth.py` (importancia: 13.00)
- `src/templates/backend-api/routes/users.py` (importancia: 11.00)
- `src/templates/backend-api/main.py` (importancia: 10.00)
- `src/templates/backend-api/routes/items.py` (importancia: 10.00)
- `src/utils/api_validator.py` (importancia: 10.00)
- `src/templates/backend-api/routes/auth.py` (importancia: 9.00)
- `src/templates/backend-api/services/user_service.py` (importancia: 9.00)
- `src/templates/backend-api/db/models.py` (importancia: 5.00)
- ... y 4 archivos más

**Grafo del grupo Type: python-service:**
```
Grupo: Type: python-service (12 archivos)
==================================================
  ... y 6 archivos más
```

### 7. Directory: src/generators
**Tipo:** directory
**Archivos:** 8
**Descripción:** Grupo funcional: Directory: src/generators

**Archivos en el grupo:**
- `src/generators/implementation_prompt_generator.py` (importancia: 17.00)
- `src/generators/contextual_prompt_generator.py` (importancia: 13.00)
- `src/generators/markdown_generator.py` (importancia: 10.00)
- `src/generators/prompt_generator.py` (importancia: 10.00)
- `src/generators/test_generator.py` (importancia: 8.00)
- `src/generators/implementation_proposal_generator.py` (importancia: 6.00)
- `src/generators/__init__.py` (importancia: 5.00)
- `src/generators/branch_strategy_generator.py` (importancia: 4.00)

**Grafo del grupo Directory: src/generators:**
```
Grupo: Directory: src/generators (8 archivos)
==================================================
Estructura de directorio:
  📄 implementation_prompt_generator.py (importancia: 17.0)
  📄 contextual_prompt_generator.py (importancia: 13.0)
  📄 markdown_generator.py (importancia: 10.0)
  📄 prompt_generator.py (importancia: 10.0)
  📄 test_generator.py (importancia: 8.0)
  📄 implementation_proposal_generator.py (importancia: 6.0)
  ... y 2 archivos más
```

### 8. Directory: src
**Tipo:** directory
**Archivos:** 2
**Descripción:** Grupo funcional: Directory: src

**Archivos en el grupo:**
- `src/main.py` (importancia: 41.00)
- `src/factory.py` (importancia: 7.00)

**Grafo del grupo Directory: src:**
```
Grupo: Directory: src (2 archivos)
==================================================
Estructura de directorio:
  📄 main.py (importancia: 41.0)
  📄 factory.py (importancia: 7.0)

Conexiones internas:
  main.py → factory.py
  factory.py → main.py
```

### 9. Directory: src/integrations
**Tipo:** directory
**Archivos:** 7
**Descripción:** Grupo funcional: Directory: src/integrations

**Archivos en el grupo:**
- `src/integrations/anthropic_advanced.py` (importancia: 10.00)
- `src/integrations/copilot_advanced.py` (importancia: 8.00)
- `src/integrations/test_anthropic.py` (importancia: 7.00)
- `src/integrations/anthropic.py` (importancia: 6.00)
- `src/integrations/copilot.py` (importancia: 5.00)
- `src/integrations/openai_integration.py` (importancia: 5.00)
- `src/integrations/__init__.py` (importancia: 5.00)

**Grafo del grupo Directory: src/integrations:**
```
Grupo: Directory: src/integrations (7 archivos)
==================================================
Estructura de directorio:
  📄 anthropic_advanced.py (importancia: 10.0)
  📄 copilot_advanced.py (importancia: 8.0)
  📄 test_anthropic.py (importancia: 7.0)
  📄 anthropic.py (importancia: 6.0)
  📄 copilot.py (importancia: 5.0)
  📄 openai_integration.py (importancia: 5.0)
  ... y 1 archivos más
```

### 10. Directory: src/ui/wizards
**Tipo:** directory
**Archivos:** 5
**Descripción:** Grupo funcional: Directory: src/ui/wizards

**Archivos en el grupo:**
- `src/ui/wizards/base_wizard.py` (importancia: 10.00)
- `src/ui/wizards/project_wizard.py` (importancia: 9.00)
- `src/ui/wizards/config_wizard.py` (importancia: 7.00)
- `src/ui/wizards/prompt_wizard.py` (importancia: 7.00)
- `src/ui/wizards/__init__.py` (importancia: 4.00)

**Grafo del grupo Directory: src/ui/wizards:**
```
Grupo: Directory: src/ui/wizards (5 archivos)
==================================================
Estructura de directorio:
  📄 base_wizard.py (importancia: 10.0)
  📄 project_wizard.py (importancia: 9.0)
  📄 config_wizard.py (importancia: 7.0)
  📄 prompt_wizard.py (importancia: 7.0)
  📄 __init__.py (importancia: 4.0)
```

### 11. Directory: src/templates/backend-api/routes
**Tipo:** directory
**Archivos:** 3
**Descripción:** Grupo funcional: Directory: src/templates/backend-api/routes

**Archivos en el grupo:**
- `src/templates/backend-api/routes/users.py` (importancia: 11.00)
- `src/templates/backend-api/routes/items.py` (importancia: 10.00)
- `src/templates/backend-api/routes/auth.py` (importancia: 9.00)

**Grafo del grupo Directory: src/templates/backend-api/routes:**
```
Grupo: Directory: src/templates/backend-api/routes (3 archivos)
==================================================
Estructura de directorio:
  📄 users.py (importancia: 11.0)
  📄 items.py (importancia: 10.0)
  📄 auth.py (importancia: 9.0)

Conexiones internas:
  users.py → items.py, auth.py
  items.py → users.py, auth.py
  auth.py → users.py, items.py
```

### 12. Type: python-test
**Tipo:** file_type
**Archivos:** 5
**Descripción:** Grupo funcional: Type: python-test

**Archivos en el grupo:**
- `src/analyzers/testability_analyzer.py` (importancia: 8.00)
- `src/generators/test_generator.py` (importancia: 8.00)
- `src/integrations/test_anthropic.py` (importancia: 7.00)
- `test_import_trace.py` (importancia: 3.00)
- `src/templates/library/src/testlib/calculator.py` (importancia: 3.00)

**Grafo del grupo Type: python-test:**
```
Grupo: Type: python-test (5 archivos)
==================================================
```

### 13. Directory: src/core
**Tipo:** directory
**Archivos:** 5
**Descripción:** Grupo funcional: Directory: src/core

**Archivos en el grupo:**
- `src/core/analyze_project_with_anthropic.py` (importancia: 6.00)
- `src/core/analyze_with_anthropic_direct.py` (importancia: 6.00)
- `src/core/analyze_with_anthropic_simple.py` (importancia: 6.00)
- `src/core/project_analyzer.py` (importancia: 5.00)
- `src/core/analyze_and_suggest.py` (importancia: 4.00)

**Grafo del grupo Directory: src/core:**
```
Grupo: Directory: src/core (5 archivos)
==================================================
Estructura de directorio:
  📄 analyze_project_with_anthropic.py (importancia: 6.0)
  📄 analyze_with_anthropic_direct.py (importancia: 6.0)
  📄 analyze_with_anthropic_simple.py (importancia: 6.0)
  📄 project_analyzer.py (importancia: 5.0)
  📄 analyze_and_suggest.py (importancia: 4.0)
```

### 14. Directory: src/templates/backend-api/models
**Tipo:** directory
**Archivos:** 3
**Descripción:** Grupo funcional: Directory: src/templates/backend-api/models

**Archivos en el grupo:**
- `src/templates/backend-api/models/item.py` (importancia: 4.00)
- `src/templates/backend-api/models/token.py` (importancia: 4.00)
- `src/templates/backend-api/models/user.py` (importancia: 4.00)

**Grafo del grupo Directory: src/templates/backend-api/models:**
```
Grupo: Directory: src/templates/backend-api/models (3 archivos)
==================================================
Estructura de directorio:
  📄 item.py (importancia: 4.0)
  📄 token.py (importancia: 4.0)
  📄 user.py (importancia: 4.0)

Conexiones internas:
  item.py → token.py, user.py
  token.py → item.py, user.py
  user.py → item.py, token.py
```

### 15. Directory: examples
**Tipo:** directory
**Archivos:** 2
**Descripción:** Grupo funcional: Directory: examples

**Archivos en el grupo:**
- `examples/simple_premium_demo.py` (importancia: 6.00)
- `examples/demo_enhanced_prompts.py` (importancia: 3.00)

**Grafo del grupo Directory: examples:**
```
Grupo: Directory: examples (2 archivos)
==================================================
Estructura de directorio:
  📄 simple_premium_demo.py (importancia: 6.0)
  📄 demo_enhanced_prompts.py (importancia: 3.0)

Conexiones internas:
  simple_premium_demo.py → demo_enhanced_prompts.py
  demo_enhanced_prompts.py → simple_premium_demo.py
```

### 16. Directory: src/templates/backend-api/db
**Tipo:** directory
**Archivos:** 2
**Descripción:** Grupo funcional: Directory: src/templates/backend-api/db

**Archivos en el grupo:**
- `src/templates/backend-api/db/models.py` (importancia: 5.00)
- `src/templates/backend-api/db/database.py` (importancia: 4.00)

**Grafo del grupo Directory: src/templates/backend-api/db:**
```
Grupo: Directory: src/templates/backend-api/db (2 archivos)
==================================================
Estructura de directorio:
  📄 models.py (importancia: 5.0)
  📄 database.py (importancia: 4.0)

Conexiones internas:
  models.py → database.py
  database.py → models.py
```

## Representación Textual del Grafo
```
1. src/main.py
2. src/ui/cli.py
3. src/generators/implementation_prompt_generator.py
4. src/ui/analysis_view.py
5. src/ui/documentation_navigator.py
6. src/utils/sync_manager.py
7. src/utils/updater.py
8. src/generators/contextual_prompt_generator.py
9. src/templates/backend-api/middleware/auth.py
10. src/templates/premium/premium_templates.py

Dependencias:
```