#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration system for ProjectPrompt v2.0
Simple .env-based configuration

Fase 4: Configuración simplificada
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional


class Config:
    """Configuración simple basada exclusivamente en .env"""
    
    def __init__(self, env_file: Optional[Path] = None):
        # Buscar .env en múltiples ubicaciones
        env_paths = [
            env_file,
            Path.cwd() / '.env',
            Path.home() / '.projectprompt' / '.env',
            Path(__file__).parent.parent.parent / '.env'
        ]
        
        for env_path in env_paths:
            if env_path and env_path.exists():
                load_dotenv(env_path)
                self.env_file_used = env_path
                break
        else:
            self.env_file_used = None
    
    @property
    def anthropic_api_key(self) -> str:
        """API key para Anthropic Claude"""
        key = os.getenv('ANTHROPIC_API_KEY', '').strip()
        if not key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. "
                "Please set it in your .env file or environment variables."
            )
        return key
    
    @property 
    def openai_api_key(self) -> str:
        """API key para OpenAI GPT"""
        key = os.getenv('OPENAI_API_KEY', '').strip()
        if not key:
            raise ValueError(
                "OPENAI_API_KEY not found. "
                "Please set it in your .env file or environment variables."
            )
        return key
    
    @property
    def default_output_dir(self) -> str:
        """Directorio por defecto para outputs"""
        return os.getenv('DEFAULT_OUTPUT_DIR', './project-output')
    
    @property
    def max_files_to_analyze(self) -> int:
        """Máximo número de archivos a analizar"""
        try:
            return int(os.getenv('MAX_FILES_TO_ANALYZE', '1000'))
        except ValueError:
            return 1000
    
    @property
    def default_api_provider(self) -> str:
        """Proveedor de API por defecto"""
        provider = os.getenv('DEFAULT_API_PROVIDER', 'anthropic').lower()
        if provider not in ['anthropic', 'openai']:
            return 'anthropic'
        return provider
    
    @property
    def exclude_patterns(self) -> list:
        """Patrones de archivos/directorios a excluir"""
        patterns = os.getenv('EXCLUDE_PATTERNS', '')
        if patterns:
            return [p.strip() for p in patterns.split(',') if p.strip()]
        return [
            '*.pyc', '*.pyo', '*.pyd', '__pycache__',
            '.git', '.svn', '.hg', '.pytest_cache',
            'node_modules', '.venv', 'venv', '.env'
        ]
    
    def validate(self) -> tuple[bool, list]:
        """Valida configuración completa"""
        errors = []
        
        # Verificar que al menos una API key existe
        has_anthropic = False
        has_openai = False
        
        try:
            self.anthropic_api_key
            has_anthropic = True
        except ValueError:
            pass
        
        try:
            self.openai_api_key
            has_openai = True
        except ValueError:
            pass
        
        if not has_anthropic and not has_openai:
            errors.append("No API keys found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY.")
        
        # Verificar directorio de output
        output_dir = Path(self.default_output_dir)
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create output directory: {e}")
        
        return len(errors) == 0, errors


# Simple factory function for backward compatibility
def get_config() -> Config:
    """Get a Config instance."""
    return Config()
