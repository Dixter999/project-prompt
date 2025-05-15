# Análisis de Proyecto: {{project_name}}

*Generado por [ProjectPrompt](https://github.com/Dixter999/project-prompt) v{{version}} en {{date}}*

## 📊 Resumen del Proyecto

**Ruta:** {{project_path}}  
**Archivos totales:** {{stats.total_files}}  
**Directorios totales:** {{stats.total_dirs}}  
**Tamaño total:** {{stats.total_size_kb}} KB

## 🔍 Lenguajes Detectados

{% if languages._main %}
**Lenguajes principales:**  
{% for lang in languages._main %}
- {{lang}} ({{languages[lang].percentage}}%)
{% endfor %}
{% endif %}

{% if languages._secondary %}
**Lenguajes secundarios:**  
{% for lang in languages._secondary %}
- {{lang}} ({{languages[lang].percentage}}%)
{% endfor %}
{% endif %}

### Distribución de Lenguajes

| Lenguaje | Archivos | % del proyecto | Tamaño (KB) |
|----------|----------|--------------|------------|
{% for name, data in languages.items() %}{% if not name.startswith('_') %}
| {{name}} | {{data.files}} | {{data.percentage}}% | {{data.size_kb}} |
{% endif %}{% endfor %}

## 📁 Estructura del Proyecto

```
{{directory_tree}}
```

## 📌 Archivos Importantes

{% for category, files in important_files.items() %}{% if not category.startswith('_') and files %}
### {{category|capitalize}}
{% for file in files %}
- `{{file}}`
{% endfor %}

{% endif %}{% endfor %}

{% if dependencies._main %}
## 📦 Dependencias Principales

{% for dep in dependencies._main %}
- {{dep}}
{% endfor %}
{% endif %}

{% if dependency_graph %}
## 🔄 Grafo de Dependencias

```mermaid
graph LR
{% for source, targets in dependency_graph.items() %}
  {{source|file_to_id}}[{{source|filename}}]
  {% for target in targets %}
  {{source|file_to_id}} --> {{target|file_to_id}}[{{target|filename}}]
  {% endfor %}
{% endfor %}
```
{% endif %}

## 🛠️ Recomendaciones

- **Repositorio**: Asegúrate de tener un archivo README.md completo y actualizado.
- **Documentación**: Considera documentar las partes principales del código.
{% if 'tests' not in important_files and stats.total_files > 10 %}
- **Tests**: Este proyecto parece no tener tests automatizados. Considera añadirlos para mejorar la calidad.
{% endif %}
{% if stats.binary_files > 5 %}
- **Archivos binarios**: El proyecto contiene {{stats.binary_files}} archivos binarios. Considera usar Git LFS si son parte del control de versiones.
{% endif %}

---

*Este reporte fue generado automáticamente. Los análisis y recomendaciones son orientativos.*
