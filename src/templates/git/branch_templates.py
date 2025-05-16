#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Plantillas para generación de estrategias de branches de Git.
"""

# Plantilla predeterminada de workflow
DEFAULT_TEMPLATE = """
Para implementar esta funcionalidad, se recomienda seguir este workflow:

1. Crear el branch principal desde la rama de desarrollo:
   ```
   git checkout develop
   git pull
   git checkout -b {branch}
   ```

2. Realizar los cambios necesarios, haciendo commits atómicos y descriptivos.

3. Probar la implementación exhaustivamente.

4. Crear una Pull Request hacia la rama develop.

5. Solicitar revisión del código.

6. Una vez aprobada, hacer merge a develop:
   ```
   git checkout develop
   git merge --no-ff {branch}
   git push origin develop
   ```
"""

# Plantilla para feature branches
FEATURE_BRANCH_TEMPLATE = """
Para implementar esta nueva funcionalidad, se recomienda seguir este workflow:

1. Crear el branch de feature desde la rama de desarrollo:
   ```
   git checkout develop
   git pull
   git checkout -b {branch}
   ```

2. Realizar los cambios necesarios, haciendo commits frecuentes:
   ```
   git add <archivos>
   git commit -m "feat(<alcance>): descripción del cambio"
   ```

3. Integrar regularmente los cambios de develop:
   ```
   git checkout develop
   git pull
   git checkout {branch}
   git merge develop
   ```

4. Resolver cualquier conflicto que surja.

5. Asegurar que la funcionalidad está completa y pasa todas las pruebas.

6. Crear una Pull Request hacia la rama develop.

7. Tras aprobación, hacer merge a develop:
   ```
   git checkout develop
   git merge --no-ff {branch}
   git push origin develop
   ```
"""

# Plantilla para bugfix branches
BUGFIX_BRANCH_TEMPLATE = """
Para corregir este bug, se recomienda seguir este workflow:

1. Crear un branch de bugfix desde la rama afectada:
   ```
   git checkout develop
   git pull
   git checkout -b {branch}
   ```

2. Implementar la corrección (fix), añadiendo pruebas que demuestren que el bug está resuelto:
   ```
   git add <archivos>
   git commit -m "fix(<alcance>): descripción de la corrección"
   ```

3. Verificar que las pruebas pasan y que no se han introducido nuevas regresiones.

4. Crear una Pull Request hacia la rama afectada.

5. Una vez aprobada, hacer merge al branch correspondiente:
   ```
   git checkout develop
   git merge --no-ff {branch}
   git push origin develop
   ```

6. Si es un bug crítico que necesita ser desplegado urgentemente, considerar también un cherry-pick a la rama de producción:
   ```
   git checkout main
   git cherry-pick <commit-hash>
   git push origin main
   ```
"""

# Plantilla para hotfix branches
HOTFIX_BRANCH_TEMPLATE = """
Para implementar este hotfix urgente, se recomienda seguir este workflow:

1. Crear el branch de hotfix desde la rama de producción:
   ```
   git checkout main
   git pull
   git checkout -b {branch}
   ```

2. Implementar la corrección mínima necesaria para resolver el problema:
   ```
   git add <archivos>
   git commit -m "fix(<alcance>): descripción de la corrección urgente"
   ```

3. Probar exhaustivamente para asegurar que la corrección funciona y no introduce nuevos problemas.

4. Crear una Pull Request hacia la rama main.

5. Tras aprobación rápida, hacer merge a main y crear un tag de versión:
   ```
   git checkout main
   git merge --no-ff {branch}
   git tag -a vX.Y.Z -m "Hotfix: descripción breve"
   git push --tags origin main
   ```

6. Propagar la corrección a develop:
   ```
   git checkout develop
   git merge --no-ff {branch}
   git push origin develop
   ```
"""

# Plantilla para refactor branches
REFACTOR_BRANCH_TEMPLATE = """
Para este refactor, se recomienda seguir este workflow:

1. Crear el branch de refactor desde la rama de desarrollo:
   ```
   git checkout develop
   git pull
   git checkout -b {branch}
   ```

2. Realizar los cambios de refactorización, manteniendo la funcionalidad actual:
   ```
   git add <archivos>
   git commit -m "refactor(<alcance>): descripción de la mejora de código"
   ```

3. Asegurar que todas las pruebas existentes pasan sin modificación.

4. Considerar añadir nuevas pruebas para mejorar la cobertura.

5. Integrar regularmente los cambios de develop:
   ```
   git checkout develop
   git pull
   git checkout {branch}
   git merge develop
   ```

6. Crear una Pull Request hacia develop.

7. Tras revisión exhaustiva de código, hacer merge a develop:
   ```
   git checkout develop
   git merge --no-ff {branch}
   git push origin develop
   ```
"""
