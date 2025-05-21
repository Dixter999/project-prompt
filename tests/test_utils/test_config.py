"""Tests for the ConfigManager class in src/utils/config.py"""
import os
import tempfile
import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

# Import the class we're testing
from src.utils.config import ConfigManager, DEFAULT_CONFIG

class TestConfigManager:
    """Test cases for the ConfigManager class"""
    
    def test_config_manager_initialization(self):
        """Test that ConfigManager initializes with default values"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'config.yaml')
            config = ConfigManager(config_path=config_path)
            
            # Check that default config is loaded
            assert config.get('log_level') == 'info'
            assert config.get('api.anthropic.enabled') is False
            assert config.get('api.openai.enabled') is False
    
    def test_load_config(self):
        """Test loading configuration from a YAML file"""
        test_config = {
            'log_level': 'debug',
            'api': {
                'anthropic': {
                    'enabled': True,
                    'key_name': 'TEST_ANTHROPIC_KEY'
                },
                'openai': {
                    'enabled': True,
                    'key_name': 'TEST_OPENAI_KEY'
                }
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'config.yaml')
            with open(config_path, 'w') as f:
                yaml.dump(test_config, f)
            
            config = ConfigManager(config_path=config_path)
            
            # Verify loaded values
            assert config.get('log_level') == 'debug'
            assert config.get('api.anthropic.enabled') is True
            assert config.get('api.openai.key_name') == 'TEST_OPENAI_KEY'
    
    def test_save_config(self):
        """Test saving configuration to a file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'config.yaml')
            config = ConfigManager(config_path=config_path)
            
            # Update some values
            config.set('log_level', 'debug')
            config.set('api.anthropic.enabled', True)
            config.set('api.anthropic.key_name', 'TEST_KEY_123')
            
            # Save and reload
            config.save()
            
            # Verify file was created
            assert os.path.exists(config_path)
            
            # Load the saved config
            with open(config_path, 'r') as f:
                saved_config = yaml.safe_load(f)
            
            # Verify saved values
            assert saved_config['log_level'] == 'debug'
            assert saved_config['api']['anthropic']['enabled'] is True
            assert saved_config['api']['anthropic']['key_name'] == 'TEST_KEY_123'
    
    def test_get_nested_value(self):
        """Test getting nested configuration values"""
        config = ConfigManager()
        
        # Test getting existing nested value
        assert config.get('api.anthropic.enabled') is False
        
        # Test getting non-existent value with default
        assert config.get('non.existent.key', 'default') == 'default'
    
    @patch('src.utils.config.keyring')
    def test_api_key_management(self, mock_keyring):
        """Test API key storage and retrieval"""
        # Setup mock keyring
        mock_keyring.get_password.return_value = None
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'config.yaml')
            config = ConfigManager(config_path=config_path)
            
            # Test setting an API key
            config.set_api_key('TEST_SERVICE', 'test_key')
            
            # Verify key was stored in keyring
            mock_keyring.set_password.assert_called_once_with(
                'project-prompt', 'TEST_SERVICE', 'test_key'
            )
            
            # Test getting the API key
            mock_keyring.get_password.return_value = 'test_key'
            assert config.get_api_key('TEST_SERVICE') == 'test_key'
            mock_keyring.get_password.assert_called_with('project-prompt', 'TEST_SERVICE')
            
            # Test deleting the API key
            config.delete_api_key('TEST_SERVICE')
            mock_keyring.delete_password.assert_called_once_with('project-prompt', 'TEST_SERVICE')
