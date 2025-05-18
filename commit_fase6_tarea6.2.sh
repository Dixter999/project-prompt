#!/bin/bash
# Script para hacer commit de la implementación del Sistema de actualización y sincronización (Tarea 6.2)

# Mensaje de commit
COMMIT_MSG="Implementa sistema de actualización y sincronización (Fase 6 - Tarea 6.2)

- Añade sistema de verificación de nuevas versiones en src/utils/updater.py
- Implementa mecanismo de actualización automática del sistema
- Añade actualización automática de plantillas
- Implementa sincronización de configuraciones entre instalaciones en src/utils/sync_manager.py
- Añade migración de datos entre versiones
- Implementa sistema de respaldo y restauración
- Añade comandos CLI para todas las funcionalidades en src/main.py
- Incluye tests para los nuevos módulos

Esta implementación completa la Tarea 6.2 del proyecto."

# Guardar mensaje en archivo temporal
echo "$COMMIT_MSG" > commit_message.txt

# Añadir archivos modificados
git add src/utils/updater.py
git add src/utils/sync_manager.py
git add src/main.py
git add tests/test_updater.py
git add tests/test_sync_manager.py
git add fases/fase6_progress.md
git add commit_message.txt

# Realizar commit
git commit -F commit_message.txt

# Mostrar confirmación
echo "✅ Commit realizado exitosamente"
echo "📝 Puedes hacer push con: git push origin feature/update-system"
