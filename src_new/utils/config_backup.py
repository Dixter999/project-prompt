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
        """Load configuration from environment variables and config file.
        
        Args:
            project_path: Path to project being analyzed (for project-specific config)
            
        Returns:
            Loaded configuration
        """
        # Start with defaults
        config_dict = self._get_default_config()
        
        # Load from global config file
        config_dict.update(self._load_from_file())
        
        # Load from project-specific config file
        if project_path:
            project_config = self._load_project_config(project_path)
            config_dict.update(project_config)
        
        # Override with environment variables
        config_dict.update(self._load_from_env())
        
        # Create config object
        self._config = self._create_config_object(config_dict)
        
        # Validate configuration
        self._validate_config()
        
        return self._config
    
    def get_config(self) -> ProjectPromptConfig:
        """Get current configuration."""
        if self._config is None:
            self._config = self.load_config()
        return self._config
    
    def save_config(self, config: ProjectPromptConfig, file_path: Optional[str] = None) -> None:
        """Save configuration to file.
        
        Args:
            config: Configuration to save
            file_path: Path to save config file (optional)
        """
        if file_path is None:
            file_path = self.config_file or self.DEFAULT_CONFIG_FILE
        
        config_dict = asdict(config)
        
        # Remove None values and nested objects for cleaner JSON
        cleaned_dict = self._clean_config_dict(config_dict)
        
        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_dict, f, indent=2)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            "ai_provider": "auto",
            "anthropic_model": "claude-3-sonnet-20240229",
            "openai_model": "gpt-4",
            "debug": False,
            "verbose": False,
            "output_dir": "./output",
            "temp_dir": "./tmp",
            
            # Scan config (defaults matching ScanConfig)
            "scan_max_files": 1000,
            "scan_max_file_size": 5 * 1024 * 1024,  # 5MB in bytes
            
            # Analysis config (defaults matching AnalysisConfig)
            "analysis_include_ai_context": False,
            "analysis_max_context_files": 50,
            "analysis_functionality_threshold": 0.5,
            "analysis_detect_patterns": True,
            "analysis_include_file_content": False,
            
            # Export config (defaults matching ExportConfig)
            "export_format": "json",
            "export_include_metadata": True,
            "export_compress_output": False,
            "export_output_directory": "./output"
        }
    
    def _load_from_file(self) -> Dict[str, Any]:
        """Load configuration from file."""
        config_dict = {}
        
        # Try specified config file first
        if self.config_file and Path(self.config_file).exists():
            config_dict.update(self._read_config_file(self.config_file))
        
        # Try default config file
        elif Path(self.DEFAULT_CONFIG_FILE).exists():
            config_dict.update(self._read_config_file(self.DEFAULT_CONFIG_FILE))
        
        return config_dict
    
    def _load_project_config(self, project_path: str) -> Dict[str, Any]:
        """Load project-specific configuration."""
        project_config_file = Path(project_path) / self.DEFAULT_CONFIG_FILE
        
        if project_config_file.exists():
            return self._read_config_file(str(project_config_file))
        
        return {}
    
    def _read_config_file(self, file_path: str) -> Dict[str, Any]:
        """Read configuration from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
            print(f"Warning: Could not load config file {file_path}: {e}")
            return {}
    
    def _load_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config_dict = {}
        
        # AI configuration
        if os.getenv('ANTHROPIC_API_KEY'):
            config_dict['anthropic_api_key'] = os.getenv('ANTHROPIC_API_KEY')
        if os.getenv('OPENAI_API_KEY'):
            config_dict['openai_api_key'] = os.getenv('OPENAI_API_KEY')
        
        # Environment variables with prefix
        for key, value in os.environ.items():
            if key.startswith(self.ENV_PREFIX):
                config_key = key[len(self.ENV_PREFIX):].lower()
                
                # Convert boolean strings
                if value.lower() in ('true', '1', 'yes', 'on'):
                    config_dict[config_key] = True
                elif value.lower() in ('false', '0', 'no', 'off'):
                    config_dict[config_key] = False
                # Convert numeric strings
                elif value.isdigit():
                    config_dict[config_key] = int(value)
                # Keep as string
                else:
                    config_dict[config_key] = value
        
        return config_dict
    
    def _create_config_object(self, config_dict: Dict[str, Any]) -> ProjectPromptConfig:
        """Create configuration object from dictionary."""
        # Extract nested config values - use proper parameter names that match the dataclasses
        scan_config_params = {
            'max_files': config_dict.get('scan_max_files', 1000),
            'max_file_size_mb': config_dict.get('scan_max_file_size', 5 * 1024 * 1024) / (1024 * 1024),  # Convert bytes to MB
        }
        # Only set ignore_dirs/ignore_files if they are provided, otherwise use defaults
        if 'scan_ignore_dirs' in config_dict and config_dict['scan_ignore_dirs'] is not None:
            scan_config_params['ignore_dirs'] = config_dict['scan_ignore_dirs']
        if 'scan_ignore_files' in config_dict and config_dict['scan_ignore_files'] is not None:
            scan_config_params['ignore_files'] = config_dict['scan_ignore_files']
        
        scan_config = ScanConfig(**scan_config_params)
        
        analysis_config = AnalysisConfig(
            include_ai_context=config_dict.get('analysis_include_ai_context', False),
            max_context_files=config_dict.get('analysis_max_context_files', 50),
            functionality_threshold=config_dict.get('analysis_functionality_threshold', 0.5),
            detect_patterns=config_dict.get('analysis_detect_patterns', True),
            include_file_content=config_dict.get('analysis_include_file_content', False)
        )
        
        export_config = ExportConfig(
            format=config_dict.get('export_format', 'json'),
            include_metadata=config_dict.get('export_include_metadata', True),
            compress_output=config_dict.get('export_compress_output', False),
            output_directory=config_dict.get('export_output_directory', './output')
        )
        
        return ProjectPromptConfig(
            ai_provider=config_dict.get('ai_provider', 'auto'),
            anthropic_api_key=config_dict.get('anthropic_api_key'),
            openai_api_key=config_dict.get('openai_api_key'),
            anthropic_model=config_dict.get('anthropic_model', 'claude-3-sonnet-20240229'),
            openai_model=config_dict.get('openai_model', 'gpt-4'),
            debug=config_dict.get('debug', False),
            verbose=config_dict.get('verbose', False),
            output_dir=config_dict.get('output_dir', './output'),
            temp_dir=config_dict.get('temp_dir', './tmp'),
            scan=scan_config,
            analysis=analysis_config,
            export=export_config
        )
    
    def _validate_config(self) -> None:
        """Validate configuration values."""
        if not self._config:
            return
        
        # Validate AI provider
        if self._config.ai_provider not in ['auto', 'anthropic', 'openai']:
            raise ValueError(f"Invalid AI provider: {self._config.ai_provider}")
        
        # Validate API keys if specific provider is set
        if self._config.ai_provider == 'anthropic' and not self._config.anthropic_api_key:
            raise ValueError("Anthropic API key is required when ai_provider is 'anthropic'")
        
        if self._config.ai_provider == 'openai' and not self._config.openai_api_key:
            raise ValueError("OpenAI API key is required when ai_provider is 'openai'")
        
        # Validate directories
        for dir_path in [self._config.output_dir, self._config.temp_dir]:
            try:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
            except PermissionError:
                raise ValueError(f"Cannot create directory: {dir_path}")
        
        # Validate numeric values
        if self._config.scan.max_file_size_mb <= 0:
            raise ValueError("scan_max_file_size_mb must be positive")
        
        if self._config.scan.max_files <= 0:
            raise ValueError("scan_max_files must be positive")
        
        if not 0 <= self._config.analysis.functionality_threshold <= 1:
            raise ValueError("functionality_threshold must be between 0 and 1")
    
    def _clean_config_dict(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Clean configuration dictionary for JSON serialization."""
        cleaned = {}
        
        for key, value in config_dict.items():
            if value is None:
                continue
            
            if isinstance(value, dict):
                cleaned_nested = self._clean_config_dict(value)
                if cleaned_nested:  # Only include non-empty dicts
                    cleaned[key] = cleaned_nested
            else:
                cleaned[key] = value
        
        return cleaned


# Global configuration instance
_config_manager = ConfigManager()


def get_config(config_file: Optional[str] = None, project_path: Optional[str] = None) -> ProjectPromptConfig:
    """Get application configuration.
    
    Args:
        config_file: Path to configuration file
        project_path: Path to project being analyzed
        
    Returns:
        Configuration object
    """
    global _config_manager
    
    if config_file:
        _config_manager = ConfigManager(config_file)
    
    return _config_manager.load_config(project_path)


def save_config(config: ProjectPromptConfig, file_path: Optional[str] = None) -> None:
    """Save configuration to file.
    
    Args:
        config: Configuration to save
        file_path: Path to save config file
    """
    global _config_manager
    _config_manager.save_config(config, file_path)


def reset_config() -> None:
    """Reset configuration manager."""
    global _config_manager
    _config_manager = ConfigManager()
