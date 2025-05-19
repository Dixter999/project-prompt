# Documentación para Desarrolladores

Bienvenido a la documentación para desarrolladores de ProjectPrompt. Esta sección está diseñada para aquellos que desean contribuir al proyecto o entender su funcionamiento interno.

## Contenido

- [Arquitectura](./architecture/README.md) - Visión general de la arquitectura del sistema
- [Guía de contribución](./contributing/README.md) - Cómo contribuir al proyecto
- [Diseño y decisiones](./design/README.md) - Decisiones de diseño y fundamentos técnicos

## Empezar a contribuir

Si estás interesado en contribuir a ProjectPrompt, te recomendamos comenzar por:

1. Leer la [guía de contribución](./contributing/README.md)
2. Familiarizarte con la [arquitectura](./architecture/README.md) del proyecto
3. Revisar los [issues abiertos](https://github.com/usuario/project-prompt/issues) para ver en qué puedes ayudar

## Estructura del proyecto

```
src/
├── analyzers/        # Componentes de análisis de proyectos
├── generators/       # Generadores de prompts y contenido
├── integrations/     # Integraciones con APIs externas
├── templates/        # Plantillas para generación de prompts
├── ui/               # Interfaces de usuario (CLI, GUI)
└── utils/            # Utilidades generales
```

## Flujo de desarrollo

ProjectPrompt sigue un flujo de desarrollo basado en características (feature branches). Para contribuir:

1. Haz fork del repositorio
2. Crea una nueva rama para tu característica (`git checkout -b feature/tu-caracteristica`)
3. Realiza tus cambios siguiendo las convenciones de código
4. Añade pruebas para tus cambios
5. Envía un pull request con una descripción detallada

## Recursos adicionales

- [Documentación de la API](../api/reference/README.md)
- [Ejemplos de código](../api/examples/README.md)
- [Historial de cambios](./design/changelog.md)
