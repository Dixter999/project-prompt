#!/usr/bin/env python3
"""
Plantilla para tests de clases en ProjectPrompt.
"""
import pytest
from datetime import datetime

# {{module_path}}


def test_{{class_name}}_class_exists():
    """Verificar que la clase {{class_name}} existe y puede ser importada."""
    try:
        from {{module_name}} import {{class_name}}
        assert True
    except ImportError:
        assert False, "La clase {{class_name}} no puede ser importada"


def test_{{class_name}}_can_be_instantiated():
    """Verificar que la clase {{class_name}} puede ser instanciada."""
    try:
        from {{module_name}} import {{class_name}}
        instance = {{class_name}}()
        assert isinstance(instance, {{class_name}})
    except Exception as e:
        assert False, f"La clase {{class_name}} no puede ser instanciada: {str(e)}"


# Casos de prueba generados automáticamente
{{test_cases}}


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
