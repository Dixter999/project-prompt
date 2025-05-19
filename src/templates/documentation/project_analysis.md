# Análisis del Proyecto: {{ project_name }}

## Información General

- **Nombre**: {{ project_name }}
- **Ubicación**: {{ project_path }}
- **Fecha de análisis**: {{ timestamp }}
- **Herramienta**: ProjectPrompt v{{ version }}

## Estructura del Proyecto

### Estadísticas Generales

- **Archivos totales**: {{ stats.total_files }}
- **Directorios**: {{ stats.total_dirs }}
- **Tamaño total**: {{ stats.total_size_kb }} KB
- **Archivos binarios**: {{ stats.binary_files }}
{% if stats.avg_file_size %}
- **Tamaño promedio por archivo**: {{ stats.avg_file_size }} KB
{% endif %}

### Lenguajes Detectados

{% if languages._main %}
**Lenguajes principales**:
{% for language in languages._main %}
- {{ language }}
{% endfor %}
{% endif %}

{% if languages._all %}
**Todos los lenguajes**:
{% for language, count in languages._all.items() %}
- {{ language }}: {{ count }} archivos
{% endfor %}
{% endif %}

### Archivos Importantes

{% if important_files %}
{% for category, files in important_files.items() %}
{% if not category.startswith('_') and files %}
#### {{ category | title }}

{% for file in files %}
- `{{ file }}`
{% endfor %}

{% endif %}
{% endfor %}
{% else %}
No se detectaron archivos importantes.
{% endif %}

## Funcionalidades Identificadas

{% if functionalities %}
{% for functionality, data in functionalities.items() %}
### {{ functionality | title }} (Confianza: {{ data.confidence }}%)

{% if data.main_files %}
**Archivos principales**:
{% for file in data.main_files %}
- `{{ file }}`
{% endfor %}
{% endif %}

{% endfor %}
{% else %}
No se detectaron funcionalidades específicas.
{% endif %}

## Dependencias

{% if dependencies._main %}
### Dependencias Principales

{% for dep in dependencies._main %}
- {{ dep }}
{% endfor %}
{% endif %}

{% if dependencies._all %}
### Todas las Dependencias

{% for dep in dependencies._all %}
- {{ dep }}
{% endfor %}
{% endif %}

## Observaciones

{% if observations %}
{{ observations }}
{% else %}
Este análisis fue generado automáticamente por ProjectPrompt.

Para obtener análisis más detallados sobre funcionalidades específicas, consulte los documentos en el directorio `functionalities/`.
{% endif %}

---

> Este documento se actualiza automáticamente con cada análisis.
