"""
Tests para el gestor de sincronización.
"""

import os
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock, mock_open

from src.utils.sync_manager import SyncManager, get_sync_manager

class TestSyncManager:
    
    @pytest.fixture
    def mock_config(self):
        return {
            "sync_enabled": True,
            "sync_provider": "local",
            "sync_directories": ["templates", "prompts"]
        }
    
    @pytest.fixture
    def sync_manager(self, mock_config):
        with patch('src.utils.sync_manager.Config') as MockConfig:
            mock_config_instance = MagicMock()
            mock_config_instance.get.side_effect = lambda key, default=None: mock_config.get(key, default)
            MockConfig.return_value = mock_config_instance
            
            # Parchar métodos de inicialización
            with patch.object(SyncManager, '_initialize_sync_directory'), \
                 patch.object(SyncManager, '_register_installation'), \
                 patch.object(SyncManager, '_get_last_sync_time', return_value=None):
                
                sm = SyncManager(config=mock_config_instance)
                # Establecer directorios para pruebas
                sm.data_dir = Path("/mock/data/dir")
                sm.sync_dir = Path("/mock/sync/dir")
                return sm
    
    def test_get_data_dir(self, sync_manager):
        # Test con directorio configurado
        with patch.object(sync_manager.config, 'get', return_value='/configured/data/dir'):
            data_dir = sync_manager._get_data_dir()
            assert data_dir == Path('/configured/data/dir')
        
        # Test con directorio por defecto
        with patch.object(sync_manager.config, 'get', return_value=''), \
             patch('platform.system', return_value='Linux'):
            data_dir = sync_manager._get_data_dir()
            assert data_dir == Path.home() / ".projectprompt"
    
    def test_get_installation_id(self, sync_manager):
        # Verificar que genera un ID consistente para la misma instalación
        id1 = sync_manager._get_installation_id()
        id2 = sync_manager._get_installation_id()
        
        assert id1 == id2
        assert isinstance(id1, str)
        assert len(id1) > 0
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"last_sync": "2023-01-01T12:00:00"}')
    def test_get_last_sync_time(self, mock_file, mock_exists, sync_manager):
        # Archivo existe
        mock_exists.return_value = True
        
        result = sync_manager._get_last_sync_time()
        assert result == datetime(2023, 1, 1, 12, 0, 0)
        
        # Archivo no existe
        mock_exists.return_value = False
        result = sync_manager._get_last_sync_time()
        assert result is None
    
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', new_callable=mock_open)
    def test_update_last_sync_time(self, mock_file, mock_mkdir, sync_manager):
        # Mockear llamadas a Path.exists() para metadata_file
        with patch('pathlib.Path.exists', return_value=False):
            sync_manager._update_last_sync_time()
            
            # Verificar que se intentó crear el directorio
            mock_mkdir.assert_called()
            # Verificar que se intentó escribir el archivo
            mock_file.assert_called()
    
    def test_sync_directory(self, sync_manager):
        # Crear directorios temporales para pruebas
        with tempfile.TemporaryDirectory() as source_dir, \
             tempfile.TemporaryDirectory() as target_dir:
             
            source = Path(source_dir)
            target = Path(target_dir)
            
            # Crear algunos archivos de prueba
            test_file1 = source / "test1.txt"
            test_file1.write_text("Test content 1")
            
            subdir = source / "subdir"
            subdir.mkdir()
            test_file2 = subdir / "test2.txt"
            test_file2.write_text("Test content 2")
            
            # Ejecutar sincronización
            stats = {"uploaded": 0, "skipped": 0, "failed": 0}
            with patch('shutil.copy2') as mock_copy:
                sync_manager._sync_directory(source, target, stats)
                
                # Verificar que se intentaron copiar los archivos
                assert mock_copy.call_count == 2
                assert stats["uploaded"] == 2
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.mkdir')
    @patch('src.utils.sync_manager.SyncManager._sync_directory')
    @patch('src.utils.sync_manager.SyncManager._update_last_sync_time')
    def test_upload_data(self, mock_update_time, mock_sync_dir, mock_mkdir, mock_exists, sync_manager):
        # Configurar que los directorios existen
        mock_exists.return_value = True
        
        # Ejecutar upload
        result, stats = sync_manager.upload_data()
        
        # Verificar resultados
        assert result is True
        assert mock_sync_dir.call_count == len(sync_manager.sync_directories)
        mock_update_time.assert_called_once()
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.mkdir')
    @patch('src.utils.sync_manager.SyncManager._sync_directory')
    @patch('src.utils.sync_manager.SyncManager._update_last_sync_time')
    def test_download_data(self, mock_update_time, mock_sync_dir, mock_mkdir, mock_exists, sync_manager):
        # Configurar que los directorios existen
        mock_exists.return_value = True
        
        # Ejecutar download
        result, stats = sync_manager.download_data()
        
        # Verificar resultados
        assert result is True
        assert mock_sync_dir.call_count == len(sync_manager.sync_directories)
        mock_update_time.assert_called_once()
    
    def test_get_status(self, sync_manager):
        # Configurar propiedades básicas
        sync_manager.sync_provider = "local"
        sync_manager.sync_enabled = True
        sync_manager.last_sync = datetime(2023, 1, 1, 12, 0, 0)
        
        # Mockear lectura de archivo de metadatos
        metadata = {
            "installations": [
                {
                    "name": "TestPC",
                    "platform": "Linux",
                    "last_sync": "2023-01-01T12:00:00"
                }
            ]
        }
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(metadata))):
            
            status = sync_manager.get_status()
            
            assert status["provider"] == "local"
            assert status["enabled"] is True
            assert status["last_sync"] == "2023-01-01 12:00:00"
            assert status["installations"] == 1
            assert len(status["installation_list"]) == 1
            assert status["installation_list"][0]["name"] == "TestPC"
    
    @patch('zipfile.ZipFile')
    @patch('tempfile.TemporaryDirectory')
    @patch('os.walk')
    @patch('os.path.join')
    @patch('os.path.relpath')
    @patch('pathlib.Path.exists')
    @patch('shutil.copytree')
    @patch('shutil.copy2')
    def test_create_backup(self, mock_copy, mock_copytree, mock_exists, mock_relpath, 
                          mock_join, mock_walk, mock_temp_dir, mock_zipfile, sync_manager):
        # Configurar mocks
        mock_exists.return_value = True
        mock_temp_dir.return_value.__enter__.return_value = "/temp/dir"
        mock_walk.return_value = [("/temp/dir", [], ["file1.txt", "file2.txt"])]
        mock_join.side_effect = lambda *args: "/".join(args)
        mock_relpath.return_value = "file1.txt"
        
        # Ejecutar
        success, message = sync_manager.create_backup("/path/to/backup.zip")
        
        # Verificar
        assert success is True
        assert "Respaldo creado" in message
        assert mock_zipfile.called
    
    @patch('zipfile.ZipFile')
    @patch('tempfile.TemporaryDirectory')
    @patch('os.path.exists')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.with_name')
    @patch('shutil.move')
    @patch('shutil.copytree')
    @patch('shutil.copy2')
    def test_restore_backup(self, mock_copy2, mock_copytree, mock_move, mock_with_name,
                           mock_path_exists, mock_os_exists, mock_temp_dir, mock_zipfile, sync_manager):
        # Configurar mocks
        mock_os_exists.return_value = True
        mock_path_exists.return_value = True
        mock_temp_dir.return_value.__enter__.return_value = "/temp/dir"
        mock_with_name.return_value = Path("/mock/backup_path")
        
        # Ejecutar
        success, message = sync_manager.restore_backup("/path/to/backup.zip")
        
        # Verificar
        assert success is True
        assert "restaurado correctamente" in message
        assert mock_zipfile.called
        assert mock_move.called
    
    def test_get_sync_manager(self):
        with patch('src.utils.sync_manager.SyncManager') as MockSyncManager:
            mock_instance = MagicMock()
            MockSyncManager.return_value = mock_instance
            
            result = get_sync_manager()
            assert result == mock_instance
            MockSyncManager.assert_called_once()


if __name__ == '__main__':
    pytest.main(['-xvs', __file__])
