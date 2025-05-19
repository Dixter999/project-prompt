#!/usr/bin/env python3
"""
Demo script para mostrar cómo utilizar el generador de prompts contextuales mejorado.
Este script proporciona ejemplos prácticos de uso.

Uso:
    python demo_enhanced_prompts.py

Requiere:
    - ProjectPrompt instalado
    - Un proyecto para analizar
"""

import os
import sys
from pathlib import Path

# Asegurarse de que podemos importar desde el directorio padre
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generators.contextual_prompt_generator import ContextualPromptGenerator

# Ejemplo básico de cómo usar el generador mejorado
def main():
    print("Demostración del Generador de Prompts Contextuales Mejorados")
    print("---------------------------------------------------------")
    
    # Obtener la ruta del proyecto (por defecto, el directorio actual)
    project_path = os.getcwd()
    
    # Configuración básica
    config = {
        "project_name": Path(project_path).name,
        "output_dir": os.path.join(project_path, "output"),
        "model_type": "gpt-4"
    }
    
    # Crear el generador
    generator = ContextualPromptGenerator(project_path, config)
    
    # Ejemplos de diferentes tipos de prompts
    print("\n1. Generando prompt para arquitectura del proyecto:")
    architecture_prompt = generator.generate_architecture_prompt()
    print(f"\n{architecture_prompt[:300]}...\n")
    
    print("\n2. Generando prompt para una funcionalidad específica:")
    functionality_name = "generación de prompts"  # Esto podría venir de un detector de funcionalidades
    functionality_prompt = generator.generate_functionality_prompt(functionality_name)
    print(f"\n{functionality_prompt[:300]}...\n")
    
    print("\n3. Generando prompt para completar código:")
    file_path = "ejemplo.py"
    code_context = """def generar_prompt_contextual(proyecto, archivos):
    # Esta función necesita implementación
    pass"""
    completion_prompt = generator.generate_completion_prompt(file_path, code_context)
    print(f"\n{completion_prompt[:300]}...\n")
    
    print("\n4. Generando preguntas de clarificación:")
    description = "Sistema de análisis de dependencias entre archivos"
    questions = generator.generate_clarification_questions(description)
    print("\nPreguntas generadas:")
    for i, question in enumerate(questions, 1):
        print(f"  {i}. {question}")
    
    print("\n---------------------------------------------------------")
    print("Fin de la demostración")


if __name__ == "__main__":
    main()
