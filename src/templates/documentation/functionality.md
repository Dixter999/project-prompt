# Análisis de Funcionalidad: {{ functionality_name | title }}

## Información General

- **Funcionalidad**: {{ functionality_name | title }}
- **Proyecto**: {{ project_name }}
- **Confianza de detección**: {{ confidence }}%
- **Fecha de análisis**: {{ timestamp }}

## Detalles de la Funcionalidad

### Archivos Principales

{% if main_files %}
{% for file in main_files %}
- `{{ file }}`
{% endfor %}
{% else %}
No se identificaron archivos principales para esta funcionalidad.
{% endif %}

### Patrones Detectados

{% if patterns %}
{% for pattern_type, pattern_list in patterns.items() %}
#### {{ pattern_type | title }}

{% for pattern in pattern_list %}
- {{ pattern }}
{% endfor %}

{% endfor %}
{% else %}
No se identificaron patrones específicos.
{% endif %}

## Implementación

{% if implementation_summary %}
{{ implementation_summary }}
{% else %}
Esta funcionalidad fue detectada en base a patrones comunes en el código. Para un análisis más detallado,
revise los archivos principales listados anteriormente.
{% endif %}

{% if code_samples %}
### Ejemplos de Código

{% for sample in code_samples %}
```{{ sample.language }}
{{ sample.code }}
```
**Archivo**: `{{ sample.file }}` (línea {{ sample.line }})

{% endfor %}
{% endif %}

## Dependencias Relacionadas

{% if related_dependencies %}
{% for dependency in related_dependencies %}
- {{ dependency }}
{% endfor %}
{% else %}
No se identificaron dependencias específicamente relacionadas con esta funcionalidad.
{% endif %}

## Recomendaciones

{% if recommendations %}
{{ recommendations }}
{% else %}
Para obtener recomendaciones específicas sobre cómo mejorar esta funcionalidad, use los prompts
contextuales en el directorio `prompts/functionality/`.
{% endif %}

---

> Este documento se actualiza automáticamente con cada análisis.
