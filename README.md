# ProjectPrompt: Generación de prompts contextuales (Básico y Mejorado)

Asistente inteligente para análisis y documentación de proyectos que utiliza IA para generar prompts contextuales y guiar el desarrollo.

## Características

- Análisis de estructura de proyectos
- Detección de funcionalidades
- Generación de prompts contextuales
- Documentación progresiva
- Integración con IDEs

## Requisitos Previos

* Python 3.8 o superior
* Git (para clonar el repositorio)
* pip (gestor de paquetes Python)
* Acceso a Internet (para instalar dependencias)

## Guía Detallada de Instalación y Configuración

### Instalación Automatizada (Recomendada)

#### Para Linux/macOS
```bash
# Clonar el repositorio
git clone https://github.com/projectprompt/project-prompt.git
cd project-prompt

# Ejecutar script de configuración
chmod +x setup_environment.sh
./setup_environment.sh
```

#### Para Windows
```powershell
# Clonar el repositorio
git clone https://github.com/projectprompt/project-prompt.git
cd project-prompt

# Ejecutar script de configuración
.\setup_environment.bat
```

El script de configuración hará lo siguiente automáticamente:
1. Verificar la instalación de Python
2. Crear un entorno virtual
3. Instalar todas las dependencias
4. Configurar el acceso al comando
5. Establecer permisos necesarios

### Instalación Manual

#### Para Sistemas Linux/macOS

1. **Instalar Python**:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-venv

   # Fedora
   sudo dnf install python3 python3-pip

   # macOS (con Homebrew)
   brew install python3
   ```

2. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/projectprompt/project-prompt.git
   cd project-prompt
   ```

3. **Crear y activar entorno virtual**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configurar acceso al comando**:
   ```bash
   # Crear enlace simbólico (recomendado)
   mkdir -p $HOME/bin
   ln -sf $(pwd)/project_prompt.py $HOME/bin/project-prompt
   chmod +x $HOME/bin/project-prompt

   # Asegurar que $HOME/bin está en PATH
   echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc  # Para bash
   # O para zsh:
   echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
   
   # Aplicar cambios
   source ~/.bashrc  # O source ~/.zshrc para zsh
   ```

#### Para Windows

1. **Instalar Python**:
   - Descargar e instalar Python desde [python.org](https://www.python.org/downloads/)
   - Durante la instalación, marcar "Add Python to PATH"

2. **Clonar el repositorio**:
   ```powershell
   git clone https://github.com/projectprompt/project-prompt.git
   cd project-prompt
   ```

3. **Crear y activar entorno virtual**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

4. **Instalar dependencias**:
   ```powershell
   pip install -r requirements.txt
   ```

5. **Crear script de acceso**:
   ```powershell
   # Crear un batch file para fácil acceso
   echo @echo off > project-prompt.bat
   echo python "%~dp0project_prompt.py" %* >> project-prompt.bat
   
   # Opcional: Mover el batch file a una ubicación en el PATH
   # Por ejemplo, puedes copiarlo a C:\Windows
   ```

### Instalación en Entornos Especiales

#### Instalación en Docker

```bash
# Construir imagen Docker
docker build -t project-prompt .

# Ejecutar en un contenedor Docker
docker run -it --rm -v $(pwd):/workspace project-prompt analyze /workspace
```

#### Instalación en WSL (Windows Subsystem for Linux)

1. **Instalar WSL** según las [instrucciones oficiales de Microsoft](https://docs.microsoft.com/es-es/windows/wsl/install)
2. **Abrir terminal WSL** y seguir los pasos de instalación para Linux:
   ```bash
   git clone https://github.com/projectprompt/project-prompt.git
   cd project-prompt
   chmod +x setup_environment.sh
   ./setup_environment.sh
   ```

#### Entornos Virtuales Alternativos

**Con Conda/Miniconda**:
```bash
# Crear entorno conda
conda create -n projectprompt python=3.10
conda activate projectprompt

# Instalar desde el repositorio
git clone https://github.com/projectprompt/project-prompt.git
cd project-prompt
pip install -r requirements.txt
python setup.py develop
```

**Con pipenv**:
```bash
# Instalar pipenv si no está instalado
pip install pipenv

# Instalar desde el repositorio
git clone https://github.com/projectprompt/project-prompt.git
cd project-prompt
pipenv install
pipenv run python project_prompt.py --help
```

### Instalación Alternativa con pip (próximamente)

```bash
# Con pip
pip install project-prompt

# Con Poetry
poetry add project-prompt
```

## Verificación de la instalación

Para verificar que la instalación funcionó correctamente:

```bash
# Si usaste el enlace simbólico o pip
project-prompt --version

# Alternativamente, ejecutar directamente el script
python project_prompt.py --version

# Verificar funcionalidades básicas
project-prompt analyze --test
```

### Verificación Avanzada

```bash
# Verificar componentes del sistema
project-prompt system-check

# Probar análisis básico con proyecto de ejemplo
project-prompt analyze test-projects/weather-api
```

## Guía Detallada de Uso

### Comandos Básicos

```bash
# Ver ayuda general
project-prompt --help

# Ver ayuda específica para un comando
project-prompt analyze --help
```

### Análisis de Proyectos

```bash
# Analizar el directorio actual
project-prompt analyze

# Analizar un proyecto específico
project-prompt analyze /ruta/a/mi/proyecto

# Guardar análisis en un archivo JSON
project-prompt analyze --output analisis_proyecto.json

# Limitar número de archivos analizados
project-prompt analyze --max-files 500

# Limitar tamaño de archivos analizados (en MB)
project-prompt analyze --max-size 2.5

# Mostrar estructura del proyecto
project-prompt analyze --structure
```

### Inicialización de Proyectos

```bash
# Crear un nuevo proyecto en la ubicación actual
project-prompt init mi-proyecto

# Crear un proyecto en una ubicación específica
project-prompt init mi-proyecto --path /ruta/destino
```

### Generación de Prompts

```bash
# Generar prompts básicos
project-prompt generate-prompts

# Generar prompts mejorados
project-prompt generate-prompts --enhanced

# Generar prompts para un proyecto específico
project-prompt generate-prompts /ruta/a/mi/proyecto

# Guardar prompts en un archivo
project-prompt generate-prompts --output mis_prompts.md
```

### Configuración de APIs para Funciones Premium

```bash
# Configurar API key de Anthropic
project-prompt set-api anthropic TU_API_KEY

# Verificar sistema freemium
python verify_freemium_system.py
```

### Herramientas de Análisis Independientes

```bash
# Análisis rápido
python quick_analyze.py /ruta/a/mi/proyecto

# Análisis detallado con salida JSON
python project_analyzer.py /ruta/a/mi/proyecto salida.json
```

### Pruebas y Verificación

```bash
# Ejecutar pruebas básicas
./test_projectprompt.sh

# Ejecutar pruebas avanzadas
./enhanced_test_projectprompt.sh

# Ejecutar pruebas completas con informe
./run_complete_test.sh
```

## Solución de Problemas Comunes

### Error de importación de módulos

Si ve errores como "No module named 'src'", ejecute el script desde el directorio raíz:

```bash
cd /ruta/a/project-prompt
python -m src.main
```

O instale el paquete en modo desarrollo:
```bash
cd /ruta/a/project-prompt
pip install -e .
```

### Permisos denegados en scripts

Si encuentra errores de permiso en los scripts:

```bash
chmod +x *.sh
chmod +x project_prompt.py
```

### API Key no reconocida

Asegúrese de exportar la variable de entorno:

```bash
export ANTHROPIC_API_KEY="your_key_here"
```

Para Windows:
```powershell
$env:ANTHROPIC_API_KEY="your_key_here"
```

O usar el archivo de configuración:
```bash
cp config.yaml.example config.yaml
# Editar config.yaml con tu editor favorito
# y añadir tu API key
```

### Errores de dependencias

Si encuentra errores relacionados con dependencias:

```bash
# Reinstalar las dependencias
pip install --force-reinstall -r requirements.txt

# Verificar la versión de Python
python --version  # Debe ser 3.8+

# Activar el entorno virtual correcto
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows
```

### Problemas con entornos virtuales

Si el entorno virtual no está funcionando correctamente:

```bash
# Eliminar y recrear el entorno virtual
rm -rf venv           # Linux/macOS
rmdir /s /q venv      # Windows

# Crear nuevo entorno
python3 -m venv venv  # Linux/macOS
python -m venv venv   # Windows

# Activar y reinstalar
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### Errores circulares de importación

Si encuentra errores circulares de importación:

```bash
# Solución temporal
python fix_config_in_telemetry.py
```

### Problemas de conexión con APIs externas

```bash
# Verificar conectividad
python test_anthropic_integration.py --test-connection

# Verificar credenciales
python verify_freemium_system.py --credentials-only
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

## Documentación Completa

ProjectPrompt cuenta con una documentación unificada y detallada que explica todas sus funciones y características:

- [Documentación Completa](docs/complete_documentation.md) - Manual completo con todas las funciones
  - También disponible [en Español](docs/documentacion_completa_es.md)
- [Guía del Usuario](docs/user_guide.md) - Manual paso a paso para usuarios
- [Referencia de Scripts](docs/script_reference.md) - Información detallada de cada script
- [Sistema Freemium](docs/developer/freemium_system.md) - Documentación sobre las características freemium

## Estructura de Directorios

```
project-prompt/
├── project_prompt.py         # Punto de entrada principal
├── quick_analyze.py          # Analizador de proyectos independiente
├── project_analyzer.py       # Analizador detallado
├── quick_init.py             # Inicializador de proyectos
├── requirements.txt          # Dependencias
├── docs/                     # Documentación completa
├── src/                      # Código fuente
│   ├── analyzers/            # Módulos de análisis
│   ├── generators/           # Generadores de prompts
│   ├── utils/                # Utilidades
│   └── templates/            # Plantillas
├── tests/                    # Pruebas unitarias
└── test-projects/            # Proyectos de ejemplo para pruebas
```

## Mantenimiento y Desarrollo

### Actualización del Proyecto

```bash
# Actualizar desde el repositorio
git pull origin main

# Reinstalar dependencias (si han cambiado)
pip install -r requirements.txt
```

### Limpieza de Archivos Temporales

```bash
# Ejecutar script de limpieza (modo prueba)
./cleanup_project.sh

# Ejecutar limpieza real
./cleanup_project.sh --execute
```

### Contribuciones

Si deseas contribuir al proyecto, por favor revisa [CONTRIBUTING.md](CONTRIBUTING.md) para las pautas detalladas.

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

Para más detalles sobre el sistema freemium, consultar la [guía de verificación](docs/freemium_system_verification_guide.md) o la [documentación completa](docs/complete_documentation.md#freemium-system).

## Entornos de Desarrollo Integrados (IDE) Compatibles

ProjectPrompt está diseñado para funcionar con múltiples IDEs y editores:

### VS Code
- Instale las extensiones recomendadas:
  ```bash
  code --install-extension ms-python.python
  code --install-extension ms-python.vscode-pylance
  ```
- Configure el entorno virtual:
  ```bash
  # Desde el directorio del proyecto
  python -m venv venv
  code .
  # Seleccionar el intérprete Python del entorno virtual desde VS Code
  ```

### PyCharm
- Abrir el proyecto y configurar el intérprete Python para usar el entorno virtual
- Marcar los directorios `src` y `tests` como Sources Root
- Configurar Run/Debug configurations para `project_prompt.py`

### Jupyter Notebook/Lab
- Configurar kernel:
  ```bash
  # Instalar ipykernel
  pip install ipykernel
  
  # Registrar kernel
  python -m ipykernel install --user --name=projectprompt
  
  # Iniciar Jupyter
  jupyter lab
  ```

## Opciones Avanzadas de Configuración

### Configuración de Límites

Ajustar límites para análisis de proyectos grandes:

```bash
# En Linux/macOS
export PROJECT_PROMPT_MAX_FILES=2000
export PROJECT_PROMPT_MAX_SIZE_MB=10

# En Windows PowerShell
$env:PROJECT_PROMPT_MAX_FILES=2000
$env:PROJECT_PROMPT_MAX_SIZE_MB=10
```

### Configuración Persistente

Crear archivo de configuración personalizado:

```bash
cp config.yaml.example config.yaml
```

Editar `config.yaml`:
```yaml
# Ejemplo de configuración
analysis:
  max_files: 2000
  max_size_mb: 10
  ignore_patterns: ["node_modules", ".git", "venv"]
  
apis:
  anthropic:
    api_key: "tu_clave_api_aquí"
    model: "claude-3-sonnet-20240229"
  
output:
  format: "markdown"
  verbose: true
```

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

## Requisitos del Sistema y Compatibilidad

### Requisitos Mínimos
- Python 3.8 o superior
- 512 MB RAM
- 100 MB espacio en disco
- Conexión a Internet (para instalación de dependencias y funciones premium)

### Sistemas Operativos Compatibles
- Linux (Ubuntu, Debian, Fedora, CentOS, etc.)
- macOS 10.14+
- Windows 10/11

### Entornos de Ejecución Compatibles
- Entornos virtuales Python (venv, conda)
- Contenedores Docker
- WSL (Windows Subsystem for Linux)
- Servidores Linux remotos

### Dependencias Principales
- typer: Para la interfaz de línea de comandos
- rich: Para visualización enriquecida
- anthropic/openai: Para integración con modelos de IA (solo características premium)
- pyyaml: Para procesamiento de configuración
- jinja2: Para generación de plantillas
- tabulate: Para formateo de tablas
- requests: Para comunicación con APIs

## Licencia

MIT
