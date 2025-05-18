#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pruebas básicas para la aplicación.
"""

def test_version():
    """Probar que la versión existe."""
    from src import __version__
    assert __version__ is not None
