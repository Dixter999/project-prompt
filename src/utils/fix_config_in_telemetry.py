#!/usr/bin/env python3
"""
Script para corregir el uso de get_config() en el módulo de telemetría.
"""

import re

def replace_config_get():
    with open('src/utils/telemetry.py', 'r') as file:
        content = file.read()
    
    # Reemplazar la importación
    content = content.replace(
        'from src.utils.config import get_config, save_config',
        'from src.utils.config import config_manager, save_config'
    )
    
    # Reemplazar todas las ocurrencias de get_config()
    content = content.replace('config = get_config()', 'config = config_manager.config')
    
    # Reemplazar save_config(config) con config_manager.save_config()
    content = content.replace('save_config(config)', 'config_manager.save_config()')
    
    # Guardar los cambios
    with open('src/utils/telemetry.py', 'w') as file:
        file.write(content)
    
    print("Archivo src/utils/telemetry.py actualizado correctamente.")

if __name__ == '__main__':
    replace_config_get()
