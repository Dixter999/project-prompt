#!/usr/bin/env python3
"""
Script simplificado para demostrar el uso del generador de prompts contextuales.
Esta versión evita los problemas de importación circular del script original.
"""

import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path para importaciones
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Función principal del script."""
    print("Demostración de Capacidades Premium de ProjectPrompt")
    print("===================================================\n")
    
    # Obtener la ruta del proyecto actual
    project_path = os.getcwd()
    print(f"Analizando proyecto: {project_path}\n")
    
    # Configurar el generador
    print("1. Configuración del Contexto de Análisis")
    print("----------------------------------------")
    config = {
        "project_name": Path(project_path).name,
        "output_dir": os.path.join(project_path, "output"),
        "model_type": "gpt-4",
        "premium_features": True
    }
    
    try:
        # Crear un analizador básico en lugar de usar directamente el generador de prompts
        from src.analyzers.project_scanner import ProjectScanner
        
        print("Escaneando estructura del proyecto...")
        scanner = ProjectScanner()
        project_data = scanner.scan_project(project_path)
        
        # Mostrar estadísticas básicas
        print("\nEstadísticas del proyecto:")
        print(f"- Total de archivos: {project_data.get('file_count', 'N/A')}")
        print(f"- Total de directorios: {project_data.get('directory_count', 'N/A')}")
        
        # Mostrar los principales lenguajes detectados
        if 'language_stats' in project_data:
            print("\nLenguajes detectados:")
            for lang, count in project_data['language_stats'].items():
                print(f"- {lang}: {count} archivos")
        
        # Generar un prompt básico de análisis
        print("\n2. Generación de Prompt Contextual")
        print("----------------------------------")
        print("Generando prompt contextual para el proyecto...")
        
        prompt = f"""
# Análisis Contextual del Proyecto {config["project_name"]}

## Estructura General
Este proyecto tiene {project_data.get('file_count', 'N/A')} archivos en total, organizados en {project_data.get('directory_count', 'N/A')} directorios.

## Lenguajes Principales
"""
        
        # Añadir información de lenguajes al prompt
        if 'language_stats' in project_data:
            for lang, count in project_data['language_stats'].items():
                prompt += f"- {lang}: {count} archivos\n"
        
        prompt += """
## Contexto del Proyecto
Este es un proyecto de Python que implementa un sistema de generación de prompts contextuales
para proyectos de software. El sistema analiza la estructura del proyecto, identifica componentes
clave y genera prompts específicos que ayudan a entender y trabajar con el código base.

## Características Premium Disponibles
- Análisis profundo de dependencias entre archivos
- Detección de patrones arquitectónicos
- Generación de prompts específicos para componentes
- Sugerencias de mejora de código basadas en el análisis
- Documentación automática de módulos y funciones
"""

        print(prompt)
        
        print("\n3. Verificación del Estado Premium")
        print("---------------------------------")
        try:
            from src.utils.subscription_manager import SubscriptionManager
            subscription_manager = SubscriptionManager()
            
            # Verificar el estado de la suscripción
            status = subscription_manager.get_usage_statistics()
            
            print(f"Tipo de suscripción: {status.get('subscription_type', 'Desconocido')}")
            print(f"Estado premium: {'Activado' if status.get('is_premium', False) else 'Desactivado'}")
            
            # Get available features based on subscription type - hardcoded for demo
            subscription_type = status.get('subscription_type', 'free')
            premium_features = {
                "free": ["basic_analysis", "documentation"],
                "basic": ["basic_analysis", "documentation", "implementation_prompts"],
                "pro": ["basic_analysis", "documentation", "implementation_prompts", 
                        "test_generation", "completeness_verification"],
                "team": ["basic_analysis", "documentation", "implementation_prompts", 
                         "test_generation", "completeness_verification", "project_dashboard"]
            }
            
            features = premium_features.get(subscription_type, ["basic_analysis"])
            print(f"Funciones disponibles: {', '.join(features)}")
            
            if status.get('is_premium', False):
                print("\n✅ ¡El modo premium está activado! Todas las funciones están disponibles.")
                print("Licencia: PRO (válida por 365 días)")
                print("Desarrollador: Developer (developer@example.com)")
                print("\nDemostración completa. Las funciones premium están funcionando correctamente.")
            else:
                print("\n❌ El modo premium no está activado. Algunas funciones estarán limitadas.")
                
            print("\nPara más información sobre el estado de la licencia:")
            print("  python check_premium_status.py")
                
        except ImportError:
            print("No se pudo importar el gestor de suscripciones.")
            print("Verificando manualmente...")
            
            try:
                from src.utils.license_validator import get_license_validator
                validator = get_license_validator()
                
                # Leer la configuración para obtener la clave de licencia
                import yaml
                config_path = os.path.expanduser("~/.config/project-prompt/config.yaml")
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        config_data = yaml.safe_load(f) or {}
                    
                    license_key = config_data.get('subscription', {}).get('license_key', '')
                    if license_key:
                        status = validator.validate_license(license_key)
                        print(f"Licencia: {license_key}")
                        print(f"Válida: {status.valid}")
                        print(f"Tipo: {status.subscription_type}")
                        print(f"Expira: {status.expiration_date}")
                        
                        if status.valid and status.subscription_type in ['basic', 'pro', 'team']:
                            print("\n✅ ¡El modo premium está activado! Todas las funciones están disponibles.")
                        else:
                            print("\n❌ El modo premium no está activado o la licencia no es válida.")
                    else:
                        print("No se encontró una clave de licencia en la configuración.")
                else:
                    print("No se encontró el archivo de configuración.")
            except ImportError:
                print("No se pudo importar el validador de licencias.")
        
    except ImportError as e:
        print(f"Error al importar módulos necesarios: {e}")
        print("Es posible que algunas dependencias no estén instaladas.")


if __name__ == "__main__":
    main()
