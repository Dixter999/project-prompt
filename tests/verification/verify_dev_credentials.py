#!/usr/bin/env python3
"""
Script simple para verificar las credenciales de desarrollador.
"""

import os
import json
import yaml
from datetime import datetime

# Configuración
CONFIG_DIR = os.path.expanduser("~/.config/project-prompt")
DEV_CREDENTIALS_FILE = os.path.join(CONFIG_DIR, "developer_credentials.json")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.yaml")

def main():
    """Función principal"""
    print("=== Verificador Simple de Credenciales de Desarrollador ===\n")
    
    # Verificar directorio de configuración
    if not os.path.exists(CONFIG_DIR):
        print(f"❌ El directorio de configuración no existe: {CONFIG_DIR}")
        return
    
    print(f"✅ Directorio de configuración: {CONFIG_DIR}")
    
    # Verificar archivo de credenciales de desarrollador
    if os.path.exists(DEV_CREDENTIALS_FILE):
        print(f"✅ Archivo de credenciales encontrado: {DEV_CREDENTIALS_FILE}")
        
        try:
            with open(DEV_CREDENTIALS_FILE, 'r') as f:
                credentials = json.load(f)
            
            print("\nCredenciales de desarrollador:")
            print(f"  Nombre: {credentials.get('name', 'No especificado')}")
            print(f"  Email: {credentials.get('email', 'No especificado')}")
            print(f"  Tipo: {credentials.get('subscription_type', 'No especificado')}")
            print(f"  Licencia: {credentials.get('license_key', 'No especificada')}")
            print(f"  Expira: {credentials.get('expiration_date', 'No especificado')}")
            
            # Verificar si la licencia ha expirado
            if credentials.get('expiration_date'):
                try:
                    expiration_date = datetime.strptime(credentials['expiration_date'], "%Y-%m-%d")
                    now = datetime.now()
                    if expiration_date > now:
                        print(f"  Estado: Válida (expira en {(expiration_date - now).days} días)")
                    else:
                        print(f"  Estado: EXPIRADA")
                except ValueError:
                    print(f"  Estado: Formato de fecha inválido")
        except Exception as e:
            print(f"❌ Error al leer credenciales: {e}")
    else:
        print(f"❌ No se encontró archivo de credenciales: {DEV_CREDENTIALS_FILE}")
    
    # Verificar archivo de configuración
    if os.path.exists(CONFIG_FILE):
        print(f"\n✅ Archivo de configuración encontrado: {CONFIG_FILE}")
        
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = yaml.safe_load(f) or {}
            
            # Verificar sección de suscripción
            if 'subscription' in config and 'license_key' in config['subscription']:
                license_key = config['subscription']['license_key']
                print(f"\nConfiguración de licencia:")
                print(f"  Clave: {license_key}")
            else:
                print("\n❌ No se encontró configuración de licencia en config.yaml")
        except Exception as e:
            print(f"❌ Error al leer configuración: {e}")
    else:
        print(f"\n❌ No se encontró archivo de configuración: {CONFIG_FILE}")
    
    # Mostrar pasos para regenerar credenciales
    print("\nSi necesitas regenerar las credenciales, ejecuta:")
    print("  python generate_developer_credentials.py --force")


if __name__ == "__main__":
    main()
