"""
Tests para el sistema de actualización.
"""

import os
import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.utils.updater import Updater, check_and_notify_updates

class TestUpdater:
    
    @pytest.fixture
    def mock_config(self):
        return {
            "templates_directory": "templates"
        }
    
    @pytest.fixture
    def updater(self, mock_config):
        with patch('src.utils.updater.Config') as MockConfig:
            mock_config_instance = MagicMock()
            mock_config_instance.get.side_effect = lambda key, default=None: mock_config.get(key, default)
            MockConfig.return_value = mock_config_instance
            return Updater(config=mock_config_instance)
    
    def test_get_current_version(self, updater):
        # Comprobar que se obtiene una versión (cualquier formato válido)
        version = updater._version
        assert version is not None
        assert isinstance(version, str)
    
    def test_should_check_for_updates(self, updater):
        # Caso 1: Forzar verificación debe retornar True
        updater.force_check = True
        assert updater.should_check_for_updates() is True
        
        # Caso 2: Sin registro de última verificación, debe retornar True
        updater.force_check = False
        updater._last_check_data = {"last_check": None}
        assert updater.should_check_for_updates() is True
        
        # Caso 3: Verificación reciente, debe retornar False
        now = datetime.now().isoformat()
        updater._last_check_data = {"last_check": now}
        assert updater.should_check_for_updates() is False
        
        # Caso 4: Verificación antigua, debe retornar True
        old_date = (datetime.now() - timedelta(days=2)).isoformat()
        updater._last_check_data = {"last_check": old_date}
        assert updater.should_check_for_updates() is True
    
    @patch('requests.get')
    def test_check_for_updates(self, mock_get, updater):
        # Mockear respuesta de API de GitHub
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'tag_name': 'v1.5.0',
            'body': '- Mejora 1\n- Mejora 2\n',
            'html_url': 'https://github.com/projectprompt/project-prompt/releases/tag/v1.5.0'
        }
        mock_get.return_value = mock_response
        
        # Simular versión actual inferior
        updater._version = '1.0.0'
        
        # Verificar actualización
        result = updater.check_for_updates()
        
        assert result['available'] is True
        assert result['version'] == '1.0.0'
        assert result['latest'] == '1.5.0'
        assert len(result['changes']) == 2
        assert result['changes'] == ['Mejora 1', 'Mejora 2']
    
    def test_skip_version(self, updater):
        version_to_skip = '1.5.0'
        
        # Asegurarse que el método _save_last_check_data está mockeado
        with patch.object(updater, '_save_last_check_data') as mock_save:
            updater.skip_version(version_to_skip)
            
            assert updater._last_check_data['skipped_version'] == version_to_skip
            mock_save.assert_called_once()
    
    @patch('subprocess.run')
    def test_update_system_pip(self, mock_run, updater):
        # Mockear detección de instalación pip
        with patch.object(updater, '_is_pip_installed', return_value=True):
            # Configurar respuesta del subproceso
            mock_run.return_value = MagicMock(returncode=0, stdout="Successfully installed", stderr="")
            
            # Probar actualización
            success, message = updater.update_system()
            
            assert success is True
            assert "completada" in message.lower()
            mock_run.assert_called_once()
    
    @patch('requests.get')
    def test_update_templates(self, mock_get, updater):
        # Mockear respuesta de índice de plantillas
        mock_index_response = MagicMock()
        mock_index_response.status_code = 200
        mock_index_response.json.return_value = {
            'templates': [
                {'path': 'template1.md', 'version': '1.0.0'},
                {'path': 'subdir/template2.md', 'version': '1.1.0'}
            ]
        }
        
        # Mockear respuesta de contenido de plantilla
        mock_template_response = MagicMock()
        mock_template_response.status_code = 200
        mock_template_response.text = '# Template\nversion: 1.0.0\n\nContent'
        
        # Configurar múltiples retornos para mock_get
        mock_get.side_effect = [mock_index_response, mock_template_response, mock_template_response]
        
        # Mockear operaciones de sistema de archivos
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('builtins.open', MagicMock()), \
             patch('shutil.copy2', MagicMock()):
            
            # Configurar que los archivos no existan (se crearán por primera vez)
            mock_exists.return_value = False
            
            # Ejecutar actualización de plantillas
            success, stats = updater.update_templates()
            
            assert success is True
            assert mock_get.call_count >= 3  # Índice + 2 plantillas
            mock_mkdir.assert_called()
    
    @patch('builtins.print')
    @patch('src.utils.updater.Updater')
    def test_check_and_notify_updates(self, MockUpdater, mock_print):
        # Mockear updater
        mock_updater = MagicMock()
        mock_updater.should_check_for_updates.return_value = True
        mock_updater.check_for_updates.return_value = {
            'available': True,
            'version': '1.0.0',
            'latest': '1.5.0',
            'changes': ['Mejora 1', 'Mejora 2']
        }
        MockUpdater.return_value = mock_updater
        
        # Ejecutar función
        check_and_notify_updates()
        
        # Verificar que se imprimió la notificación
        assert mock_print.call_count > 0
        assert any('Actualización disponible' in str(args) for args, _ in mock_print.call_args_list)


if __name__ == '__main__':
    pytest.main(['-xvs', __file__])
