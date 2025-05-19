# Guía de contribución

¡Gracias por tu interés en contribuir a ProjectPrompt! Esta guía te ayudará a configurar tu entorno de desarrollo y a entender nuestro proceso de contribución.

## Código de conducta

Este proyecto y todos los participantes están bajo un [Código de conducta](./CODE_OF_CONDUCT.md). Por favor, léelo y respétalo al participar en este proyecto.

## Configuración del entorno de desarrollo

### Requisitos previos

- Python 3.8 o superior
- Git
- Cuenta de GitHub
- Conocimientos básicos de Python y programación orientada a objetos

### Pasos para configurar el entorno

1. **Haz un fork del repositorio**

   Visita la [página del proyecto en GitHub](https://github.com/usuario/project-prompt) y haz click en "Fork".

2. **Clona tu fork localmente**

   ```bash
   git clone https://github.com/TU-USUARIO/project-prompt.git
   cd project-prompt
   ```

3. **Configura el repositorio upstream**

   ```bash
   git remote add upstream https://github.com/usuario/project-prompt.git
   ```

4. **Crea un entorno virtual**

   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\\Scripts\\activate
   ```

5. **Instala las dependencias de desarrollo**

   ```bash
   pip install -e ".[dev]"
   ```

6. **Configura los hooks de pre-commit**

   ```bash
   pre-commit install
   ```

## Flujo de trabajo de desarrollo

### 1. Sincroniza tu fork

Antes de empezar a trabajar en una nueva funcionalidad, asegúrate de que tu fork está actualizado:

```bash
git fetch upstream
git checkout main
git merge upstream/main
```

### 2. Crea una rama para tu funcionalidad

```bash
git checkout -b feature/nombre-descriptivo
```

Utiliza prefijos según el tipo de cambio:
- `feature/` para nuevas funcionalidades
- `fix/` para correcciones de bugs
- `docs/` para cambios en documentación
- `refactor/` para refactorizaciones
- `test/` para añadir o mejorar pruebas

### 3. Desarrolla tu cambio

- Escribe código claro y mantenible
- Sigue las convenciones de estilo (ver más abajo)
- Añade pruebas unitarias para tus cambios
- Actualiza la documentación si es necesario

### 4. Ejecuta las pruebas localmente

```bash
pytest
```

### 5. Haz commit de tus cambios

```bash
git add .
git commit -m "Descripción clara del cambio"
```

### 6. Envía un Pull Request

1. Sube tus cambios a tu fork:

   ```bash
   git push origin feature/nombre-descriptivo
   ```

2. Ve a GitHub y crea un nuevo Pull Request
3. Describe detalladamente los cambios realizados
4. Vincula cualquier issue relacionado

## Convenciones de código

### Estilo y formato

Seguimos [PEP 8](https://www.python.org/dev/peps/pep-0008/) y utilizamos herramientas para asegurar la consistencia:

- **Black** para formato automático de código
- **isort** para ordenar imports
- **flake8** para linting
- **mypy** para comprobación de tipos

### Documentación

- Usa docstrings en formato Google para todas las clases, métodos y funciones
- Mantén actualizada la documentación cuando cambies funcionalidades
- Escribe comentarios claros para código complejo

### Pruebas

- Escribe pruebas unitarias para cada nueva funcionalidad
- Mantén una cobertura de pruebas alta
- Las pruebas deberían ser rápidas y no depender de servicios externos

## Proceso de revisión

1. Los mantenedores revisarán tu PR cuando esté disponible
2. Pueden sugerir cambios o mejoras
3. Una vez aprobado, tu código será fusionado en la rama principal

## Problemas comunes y soluciones

### Las pruebas no pasan

- Asegúrate de que estás usando la versión correcta de Python
- Verifica que has instalado todas las dependencias
- Ejecuta `pytest -v` para ver detalles específicos

### Conflictos en el merge

- Actualiza tu rama con los últimos cambios de main
- Resuelve los conflictos localmente antes de subir los cambios

## Recursos adicionales

- [Documentación de la API](../api/reference/README.md)
- [Guía de estilo PEP 8](https://www.python.org/dev/peps/pep-0008/)
- [Guía de docstrings en formato Google](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)
