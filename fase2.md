# Fase 2: Reestructuración Core
**Branch**: `phase2/core-restructure`  
**Duración**: 2 semanas  
**Objetivo**: Crear nueva arquitectura simplificada y migrar build system

## 🎯 Objetivos de la Fase
- Crear nueva estructura de directorios limpia
- Migrar funcionalidad core a arquitectura simplificada
- Eliminar Poetry y crear setup.py simple
- Consolidar integraciones de IA
- Reducir dependencias de 15+ a 6-8

## 📁 Nueva Estructura de Directorios

### Semana 1: Crear Estructura Nueva
```bash
mkdir -p src_new/{core,ai,generators,models,utils}
touch src_new/{core,ai,generators,models,utils}/__init__.py
```

**Estructura objetivo**:
```
src_new/
├── core/
│   ├── __init__.py
│   ├── analyzer.py      # Analizador unificado
│   ├── scanner.py       # ProjectScanner migrado
│   └── detector.py      # FunctionalityDetector migrado
├── ai/
│   ├── __init__.py
│   ├── client.py        # Cliente IA unificado
│   ├── anthropic.py     # Integración Anthropic
│   └── openai.py        # Integración OpenAI
├── generators/
│   ├── __init__.py
│   └── suggestions.py   # Generador de sugerencias
├── models/
│   ├── __init__.py
│   └── project.py       # Modelos de datos consolidados
├── utils/
│   ├── __init__.py
│   ├── files.py         # Utilidades de archivos
│   └── config.py        # Configuración simple
└── cli.py              # CLI simplificado
```

## 🔄 Migración de Funcionalidad Core

### 1. Migrar ProjectScanner
**Archivo**: `src_new/core/scanner.py`

```python
# Migrar desde: src/analyzers/project_scanner.py
# Cambios necesarios:
# - Eliminar dependencias de UI/Dashboard
# - Simplificar configuración
# - Mantener solo lógica de escaneo esencial
```

**Funcionalidades a mantener**:
- Escaneo recursivo de directorios
- Filtrado de archivos por extensión
- Detección de archivos de configuración
- Exclusión de directorios innecesarios

**Funcionalidades a eliminar**:
- Generación de estadísticas para UI
- Exportación a múltiples formatos
- Integración con sistema de progreso

### 2. Migrar FunctionalityDetector
**Archivo**: `src_new/core/detector.py`

```python
# Migrar desde: src/analyzers/functionality_detector.py
# Simplificar configuraciones complejas
# Mantener solo patrones de detección esenciales
```

**Funcionalidades a mantener**:
- Detección de patrones de código
- Clasificación de archivos por funcionalidad
- Identificación de módulos principales

### 3. Crear Analizador Unificado
**Archivo**: `src_new/core/analyzer.py`

```python
class ProjectAnalyzer:
    """Analizador principal que coordina todo el análisis"""
    
    def __init__(self):
        self.scanner = ProjectScanner()
        self.detector = FunctionalityDetector()
        # dependency_analyzer se creará en Fase 3
    
    def analyze(self, path: str, max_files: int = 1000) -> ProjectAnalysis:
        """
        Análisis completo del proyecto:
        1. Escanear archivos
        2. Detectar funcionalidades
        3. Crear grupos lógicos
        4. Generar contexto para IA
        """
        # Implementación unificada
```

### 4. Consolidar Cliente IA
**Archivo**: `src_new/ai/client.py`

```python
class AIClient:
    """Cliente unificado para APIs de IA"""
    
    def __init__(self, provider: str = "anthropic"):
        if provider == "anthropic":
            from .anthropic import AnthropicClient
            self.client = AnthropicClient()
        elif provider == "openai":
            from .openai import OpenAIClient  
            self.client = OpenAIClient()
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def generate_suggestions(self, context: str, group_info: dict) -> str:
        """Genera sugerencias usando el provider configurado"""
        return self.client.complete(context, group_info)
```

## 🔧 Migración de Build System

### Eliminar Poetry
```bash
rm pyproject.toml
rm poetry.lock
rm -rf .venv  # Si existe
```

### Crear setup.py Simple
**Archivo**: `setup.py`

```python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="projectprompt",
    version="2.0.0",
    author="ProjectPrompt Team",
    description="Simple project analysis and AI-powered suggestions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/projectprompt",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "anthropic>=0.8.0",
        "openai>=1.0.0", 
        "click>=8.0.0",
        "pydantic>=2.0.0",
        "networkx>=3.0",
        "python-dotenv>=1.0.0"
    ],
    entry_points={
        'console_scripts': [
            'projectprompt=src.cli:main',
            'pp=src.cli:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
```

### Crear requirements.txt Mínimo
**Archivo**: `requirements.txt`

```txt
# Core dependencies
anthropic>=0.8.0
openai>=1.0.0
click>=8.0.0
pydantic>=2.0.0
networkx>=3.0
python-dotenv>=1.0.0

# Development dependencies (optional)
pytest>=7.0.0
black>=22.0.0
flake8>=5.0.0
```

### Crear requirements-dev.txt
**Archivo**: `requirements-dev.txt`

```txt
-r requirements.txt

# Testing
pytest>=7.0.0
pytest-cov>=4.0.0

# Code quality
black>=22.0.0
flake8>=5.0.0
mypy>=1.0.0

# Documentation
mkdocs>=1.4.0
mkdocs-material>=8.0.0
```

## 🔗 Consolidación de Integraciones

### Migrar Integración Anthropic
**Archivo**: `src_new/ai/anthropic.py`

```python
# Migrar desde: src/integrations/anthropic.py
# Simplificar y limpiar
# Mantener solo funcionalidad esencial
```

### Migrar Integración OpenAI
**Archivo**: `src_new/ai/openai.py`

```python
# Migrar desde: src/integrations/openai.py
# Simplificar y limpiar
# Asegurar compatibilidad con nueva arquitectura
```

## 📋 Modelos de Datos Consolidados

### Archivo: `src_new/models/project.py`

```python
from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path

@dataclass
class FileInfo:
    """Información de un archivo individual"""
    path: str
    size: int
    extension: str
    functionality_type: str
    
@dataclass 
class GroupInfo:
    """Información de un grupo funcional"""
    name: str
    files: List[str]
    group_type: str
    importance: float
    
@dataclass
class ProjectAnalysis:
    """Resultado completo del análisis de proyecto"""
    project_path: str
    files: List[FileInfo]
    groups: Dict[str, GroupInfo]
    analysis_timestamp: str
    
    def save_to_directory(self, output_dir: Path):
        """Guarda análisis en directorio especificado"""
        # Implementación de guardado
```

## 🛠️ Configuración Simplificada

### Archivo: `src_new/utils/config.py`

```python
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

class Config:
    """Configuración simple basada en .env"""
    
    def __init__(self, env_file: Optional[Path] = None):
        if env_file is None:
            env_file = Path.cwd() / '.env'
        
        if env_file.exists():
            load_dotenv(env_file)
    
    @property
    def anthropic_api_key(self) -> str:
        key = os.getenv('ANTHROPIC_API_KEY', '')
        if not key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        return key
    
    @property 
    def openai_api_key(self) -> str:
        key = os.getenv('OPENAI_API_KEY', '')
        if not key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        return key
    
    @property
    def default_output_dir(self) -> str:
        return os.getenv('DEFAULT_OUTPUT_DIR', './project-output')
    
    @property
    def max_files_to_analyze(self) -> int:
        return int(os.getenv('MAX_FILES_TO_ANALYZE', '1000'))
    
    @property
    def default_api_provider(self) -> str:
        return os.getenv('DEFAULT_API_PROVIDER', 'anthropic')
```

### Archivo: `.env.example`

```bash
# ProjectPrompt Configuration
# Copy this file to .env and fill in your API keys

# AI API Keys (at least one required)
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here

# Optional Configuration
DEFAULT_OUTPUT_DIR=./project-output
MAX_FILES_TO_ANALYZE=1000
DEFAULT_API_PROVIDER=anthropic
```

## 🧪 Testing de Migración

### Tests para Nueva Estructura
```bash
# Test básico de imports
python -c "from src_new.core.analyzer import ProjectAnalyzer; print('✅ New structure imports OK')"

# Test de configuración
python -c "from src_new.utils.config import Config; print('✅ Config system OK')"

# Test de AI client
python -c "from src_new.ai.client import AIClient; print('✅ AI client OK')"
```

### Validación de Build
```bash
# Test de instalación
pip install -e .

# Test de entry points
projectprompt --help
pp --help
```

## 📊 Métricas Esperadas

### Reducción de Dependencias
- **Antes**: 15+ dependencias (Poetry + extras)
- **Después**: 6 dependencias core + 3 dev

### Simplificación de Estructura
- **Antes**: 8 directorios principales con overlap
- **Después**: 5 directorios claros y específicos

### Instalación
- **Antes**: Poetry install (complejo)
- **Después**: pip install -e . (simple)

## ⚠️ Riesgos y Mitigaciones

### Riesgo: Pérdida de funcionalidad durante migración
**Mitigación**: Migrar incrementalmente, mantener estructura antigua hasta validación

### Riesgo: Problemas de compatibilidad de dependencias
**Mitigación**: Testing exhaustivo en entorno limpio

### Riesgo: Configuración rota
**Mitigación**: Validar config system con múltiples escenarios

## 🚀 Comandos Git para Fase 2

```bash
# Iniciar fase
git checkout develop
git checkout -b phase2/core-restructure

# Durante la fase (commits granulares)
git add src_new/ && git commit -m "Create new directory structure"
git add setup.py requirements.txt && git commit -m "Migrate from Poetry to setup.py"
git add src_new/core/ && git commit -m "Migrate core analyzers"
git add src_new/ai/ && git commit -m "Consolidate AI integrations"
git add .env.example && git commit -m "Simplify configuration system"

# Finalizar fase
git checkout develop
git merge phase2/core-restructure
```

## ✅ Criterios de Éxito

Al final de Fase 2:
1. ✅ Nueva estructura de directorios creada y poblada
2. ✅ Build system migrado de Poetry a setup.py
3. ✅ Dependencias reducidas a <8 core
4. ✅ Funcionalidad core migrada y funcionando
5. ✅ Sistema de configuración .env funcionando
6. ✅ Entry points funcionando (projectprompt, pp)

**Resultado**: Arquitectura limpia y simplificada, instalación simple, configuración simple, lista para resolver problemas técnicos en Fase 3.