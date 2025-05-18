# Módulo de Utilidades (Utils)

El módulo `utils` contiene funciones y clases de utilidad que dan soporte a las demás partes de ProjectPrompt.

## Clases principales

### ConfigManager

Gestiona la configuración de la aplicación.

```python
from project_prompt.utils import config_manager

# Obtener configuración
config = config_manager.get_config()
api_key = config.get("api_keys", {}).get("openai")

# Modificar configuración
config_manager.set_config("api_keys.openai", "nueva-api-key")
config_manager.save_config()
```

#### Métodos

| Método | Descripción | Parámetros | Retorno |
|--------|-------------|------------|---------|
| `get_config()` | Obtiene la configuración actual | - | `dict` |
| `set_config()` | Establece un valor de configuración | `key`, `value` | `None` |
| `save_config()` | Guarda la configuración | - | `bool` |
| `reset_config()` | Restablece la configuración | - | `None` |

### Logger

Sistema de registro para la aplicación.

```python
from project_prompt.utils import logger

# Registrar mensajes
logger.debug("Información detallada")
logger.info("Información general")
logger.warning("Advertencia")
logger.error("Error")
```

#### Métodos

| Método | Descripción | Parámetros | Retorno |
|--------|-------------|------------|---------|
| `debug()` | Registra mensaje de depuración | `message` | `None` |
| `info()` | Registra mensaje informativo | `message` | `None` |
| `warning()` | Registra advertencia | `message` | `None` |
| `error()` | Registra error | `message` | `None` |
| `set_level()` | Establece nivel de registro | `level` | `None` |

### Updater

Gestiona actualizaciones de la aplicación.

```python
from project_prompt.utils import Updater

updater = Updater()
has_updates = updater.check_for_updates()
if has_updates:
    updater.update()
```

#### Métodos

| Método | Descripción | Parámetros | Retorno |
|--------|-------------|------------|---------|
| `check_for_updates()` | Comprueba actualizaciones | - | `bool` |
| `get_latest_version()` | Obtiene última versión | - | `str` |
| `update()` | Actualiza la aplicación | - | `bool` |
| `backup()` | Crea copia de seguridad | - | `str` |

### SyncManager

Gestiona la sincronización entre dispositivos.

```python
from project_prompt.utils import SyncManager

sync = SyncManager()
sync.pull()  # Descargar cambios
sync.push()  # Subir cambios
```

#### Métodos

| Método | Descripción | Parámetros | Retorno |
|--------|-------------|------------|---------|
| `pull()` | Descarga configuración remota | - | `bool` |
| `push()` | Sube configuración local | - | `bool` |
| `sync()` | Sincroniza en ambas direcciones | - | `bool` |
| `get_status()` | Obtiene estado de sincronización | - | `dict` |

### CacheManager

Gestiona el sistema de caché para operaciones costosas.

```python
from project_prompt.utils import cache_manager

# Usar cache
@cache_manager.cached(timeout=3600)
def operacion_costosa(parametro):
    # ...realizar operación...
    return resultado
```

#### Métodos

| Método | Descripción | Parámetros | Retorno |
|--------|-------------|------------|---------|
| `cached()` | Decorador para cachear funciones | `timeout`, `key_prefix` | `function` |
| `get()` | Obtiene valor de caché | `key` | `Any` |
| `set()` | Establece valor en caché | `key`, `value`, `timeout` | `None` |
| `clear()` | Limpia la caché | `key_pattern` | `int` |

## Funciones de utilidad

### Funciones de sistema de archivos

```python
from project_prompt.utils.fs import (
    list_files,
    read_file,
    get_file_type,
    get_file_size
)

# Listar archivos con filtro
files = list_files("/ruta", extensions=[".py", ".md"])

# Leer contenido
content = read_file("/ruta/archivo.py")

# Obtener tipo
file_type = get_file_type("/ruta/archivo.py")  # "python"

# Obtener tamaño
size = get_file_size("/ruta/archivo.py")  # en bytes
```

### Funciones de texto

```python
from project_prompt.utils.text import (
    tokenize,
    count_tokens,
    truncate_to_token_limit,
    extract_keywords
)

# Contar tokens
num_tokens = count_tokens("Texto de ejemplo")

# Truncar texto
truncated = truncate_to_token_limit(
    "Texto muy largo...", 
    max_tokens=100
)

# Extraer palabras clave
keywords = extract_keywords("Texto con palabras clave importantes")
```

## Constantes y enumeraciones

### LogLevel

Niveles de registro disponibles.

```python
from project_prompt.utils import LogLevel

# Valores disponibles
LogLevel.DEBUG    # Información de depuración detallada
LogLevel.INFO     # Información general
LogLevel.WARNING  # Advertencias
LogLevel.ERROR    # Errores
LogLevel.CRITICAL # Errores críticos
```

### FileType

Tipos de archivo reconocidos.

```python
from project_prompt.utils import FileType

# Ejemplos
FileType.PYTHON   # Archivos Python (.py)
FileType.MARKDOWN # Archivos Markdown (.md)
FileType.JSON     # Archivos JSON (.json)
FileType.UNKNOWN  # Tipo desconocido
```
