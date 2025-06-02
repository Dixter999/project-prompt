"""ProjectPrompt - Asistente inteligente para análisis y documentación de proyectos usando IA."""

def _get_version():
    """Get the version from package metadata."""
    try:
        # Try using importlib.metadata (Python 3.8+)
        from importlib.metadata import version
        return version("projectprompt")
    except ImportError:
        # Fallback to pkg_resources for older Python versions
        try:
            import pkg_resources
            return pkg_resources.get_distribution("projectprompt").version
        except Exception:
            # Last resort: return a fallback version
            return "1.3.2"

__version__ = _get_version()
