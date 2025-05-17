#!/usr/bin/env python3
"""
Plantilla para tests de módulos en ProjectPrompt.
"""
import pytest
from datetime import datetime

# {{module_path}}


def test_{{module_name}}_exists():
    """Verificar que el módulo existe y puede ser importado."""
    try:
        import {{module_name}}
        assert True
    except ImportError:
        assert False, "El módulo {{module_name}} no puede ser importado"


# Casos de prueba generados automáticamente
{{test_cases}}


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
