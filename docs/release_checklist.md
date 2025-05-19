# ProjectPrompt - Release Checklist

Este documento define la lista de verificación para preparar una versión de ProjectPrompt para su publicación. Siga esta guía para asegurar que la versión cumple con los estándares de calidad y está lista para ser utilizada por los usuarios.

## Pre-Release Checklist

### Documentación

- [ ] Toda la documentación está actualizada con las nuevas funcionalidades
- [ ] El número de versión está actualizado en todos los archivos relevantes
- [ ] La guía de usuario refleja el comportamiento actual del software
- [ ] Las instrucciones de instalación están verificadas
- [ ] El archivo README.md contiene información actualizada
- [ ] Se han documentado los cambios en el archivo CHANGELOG.md

### Código

- [ ] Se han fusionado todos los pull requests relacionados con la versión
- [ ] Todos los conflictos están resueltos
- [ ] Se ha ejecutado el linter sobre todo el código fuente
- [ ] Se han realizado revisiones de código para cambios importantes
- [ ] Se ha verificado la compatibilidad con versiones anteriores
- [ ] Los TODOs críticos han sido resueltos o documentados

### Testing

- [ ] Se han ejecutado todas las pruebas unitarias
- [ ] Las pruebas de integración completan correctamente
- [ ] Se ha verificado la funcionalidad en los principales sistemas operativos:
  - [ ] Windows 10/11
  - [ ] macOS
  - [ ] Linux (Ubuntu/Debian)
- [ ] Se han realizado pruebas manuales de escenarios críticos
- [ ] Se ha verificado el sistema freemium
- [ ] Se ha probado la integración con Anthropic

### Paquetes y Distribución

- [ ] Se ha incrementado el número de versión según SemVer
- [ ] Se han generado los paquetes de distribución (sdist, wheel)
- [ ] Se han instalado y verificado los paquetes en un entorno limpio
- [ ] Se han actualizado las dependencias si es necesario
- [ ] Se han minimizado las dependencias externas

## Release Procedure

1. **Preparación Final**
   - Ejecutar `./verify_and_deploy.sh` para verificación completa
   - Revisar la salida y resolver cualquier problema identificado

2. **Generación de Versión**
   - Actualizar la versión en `setup.py`, `__init__.py` y otros archivos relevantes
   - Crear un commit con el mensaje "Release vX.Y.Z"
   - Crear un tag: `git tag -a vX.Y.Z -m "Version X.Y.Z"`

3. **Publicación**
   - Subir el tag a Github: `git push origin vX.Y.Z`
   - Generar los paquetes finales: `python setup.py sdist bdist_wheel`
   - Subir a PyPI: `twine upload dist/*`

4. **Verificación Post-Release**
   - Verificar la instalación desde PyPI: `pip install project-prompt`
   - Comprobar que la documentación online está actualizada
   - Verificar que las funcionalidades principales funcionan correctamente

5. **Anuncio**
   - Publicar anuncio en canales oficiales
   - Actualizar el sitio web con la nueva versión
   - Notificar a usuarios importantes o colaboradores

## Post-Release Tasks

- [ ] Comenzar planificación para próxima versión
- [ ] Revisar y categorizar feedback de usuarios
- [ ] Abrir issues para problemas encontrados
- [ ] Actualizar la hoja de ruta del proyecto
- [ ] Analizar métricas de adopción e instalación

## Emergency Hotfix Procedure

En caso de detectar un error crítico después de la publicación:

1. Crear rama desde el tag de la versión: `git checkout -b hotfix-vX.Y.Z vX.Y.Z`
2. Implementar solución y pruebas correspondientes
3. Actualizar la versión a vX.Y.(Z+1)
4. Seguir el procedimiento de release para la nueva versión
5. Documentar el problema y la solución en CHANGELOG.md
