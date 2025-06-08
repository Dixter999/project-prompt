#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test simple de los componentes de Fase 3.
Ejecuta tests básicos sin problemas de importación.
"""

import sys
import os
from pathlib import Path

# Agregar paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Test de importaciones y funcionalidad básica
def test_group_manager():
    """Test básico de GroupManager"""
    try:
        from src_new.core.group_manager import GroupManager
        manager = GroupManager()
        
        # Test filtro de grupos vacíos
        groups = {
            'valid': ['file1.py'],
            'empty': [],
            'nonexistent': ['nonexistent.py']
        }
        
        # Mock file exists check
        original_exists = Path.exists
        def mock_exists(self):
            return 'file1.py' in str(self)
        Path.exists = mock_exists
        
        try:
            filtered = manager.filter_empty_groups(groups)
            assert 'empty' not in filtered
            assert 'valid' in filtered
            print("✅ GroupManager: Empty groups filtered correctly")
        finally:
            Path.exists = original_exists
            
        return True
    except Exception as e:
        print(f"❌ GroupManager test failed: {e}")
        return False


def test_dependency_analyzer():
    """Test básico de UnifiedDependencyAnalyzer"""
    try:
        from src_new.core.dependency_analyzer import UnifiedDependencyAnalyzer
        analyzer = UnifiedDependencyAnalyzer()
        
        # Test análisis básico con archivos vacíos
        result = analyzer.analyze_dependencies([])
        assert 'graph' in result
        assert 'total_connections' in result
        assert result['total_connections'] == 0  # Sin archivos, sin conexiones
        
        print("✅ UnifiedDependencyAnalyzer: Basic analysis works")
        return True
    except Exception as e:
        print(f"❌ UnifiedDependencyAnalyzer test failed: {e}")
        return False


def test_priority_system():
    """Test básico de GroupPrioritySystem"""
    try:
        from src_new.core.group_priority_system import GroupPrioritySystem
        priority_system = GroupPrioritySystem()
        
        # Test eliminación de duplicados
        groups_with_duplicates = {
            'core_modules': ['file1.py', 'file2.py'],
            'utility_modules': ['file1.py', 'utils.py']  # file1.py duplicado
        }
        
        clean_groups = priority_system.assign_files_to_groups(groups_with_duplicates)
        
        # Verificar que no hay duplicados
        all_files = [f for files in clean_groups.values() for f in files]
        unique_files = set(all_files)
        assert len(all_files) == len(unique_files)
        
        # Verificar que core tiene prioridad
        assert 'file1.py' in clean_groups['core_modules']
        assert 'file1.py' not in clean_groups.get('utility_modules', [])
        
        print("✅ GroupPrioritySystem: Duplicates removed, priority respected")
        return True
    except Exception as e:
        print(f"❌ GroupPrioritySystem test failed: {e}")
        return False


def test_file_group_mapping():
    """Test básico de GroupMappingManager"""
    try:
        from src_new.core.file_group_mapping import GroupMappingManager
        mapping_manager = GroupMappingManager()
        
        # Test creación de mapeos
        groups = {
            'core': ['file1.py', 'file2.py'],
            'utils': ['utils.py']
        }
        
        mappings = mapping_manager.create_mappings(groups)
        
        # Verificar mapeos bidireccionales
        assert len(mappings) == 3  # 3 archivos total
        
        # Test búsqueda
        mapping = mapping_manager.get_file_group('file1.py')
        assert mapping is not None
        assert mapping.group_name == 'core'
        
        # Test búsqueda inversa
        core_files = mapping_manager.get_group_files('core')
        assert 'file1.py' in core_files
        assert 'file2.py' in core_files
        
        print("✅ GroupMappingManager: Bidirectional mapping works")
        return True
    except Exception as e:
        print(f"❌ GroupMappingManager test failed: {e}")
        return False


def test_integration():
    """Test de integración básica"""
    try:
        from src_new.core.group_manager import GroupManager
        from src_new.core.dependency_analyzer import UnifiedDependencyAnalyzer
        from src_new.core.group_priority_system import GroupPrioritySystem
        from src_new.core.file_group_mapping import GroupMappingManager
        from src_new.models.project import FileInfo
        
        # Simular flujo completo usando archivos reales de test
        files = [
            FileInfo(path="test_main.py", name="test_main.py", extension=".py", size=1024, language="python"),
            FileInfo(path="test_utils.py", name="test_utils.py", extension=".py", size=512, language="python")
        ]
        
        # 1. Crear grupos
        group_manager = GroupManager()
        groups = group_manager.create_groups(files)
        
        # 2. Eliminar duplicados
        priority_system = GroupPrioritySystem()
        clean_groups = priority_system.assign_files_to_groups(groups)
        
        # 3. Crear mapeos
        mapping_manager = GroupMappingManager()
        mappings = mapping_manager.create_mappings(clean_groups)
        
        # 4. Analizar dependencias (usando archivos de test reales)
        dependency_analyzer = UnifiedDependencyAnalyzer()
        dep_result = dependency_analyzer.analyze_dependencies(['test_main.py', 'test_utils.py'])
        
        # Validaciones
        assert len(clean_groups) > 0
        assert all(len(files) > 0 for files in clean_groups.values())
        assert len(mappings) > 0
        assert 'graph' in dep_result
        
        print("✅ Integration test: Complete workflow successful")
        return True
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


def main():
    """Ejecutar todos los tests"""
    print("🧪 Running Phase 3 Critical Fixes Tests")
    print("=" * 50)
    
    tests = [
        test_group_manager,
        test_dependency_analyzer,
        test_priority_system,
        test_file_group_mapping,
        test_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL PHASE 3 CRITICAL FIXES VALIDATED!")
        print("✅ Zero empty groups")
        print("✅ Unified dependency analyzer")
        print("✅ Zero file duplicates")
        print("✅ Complete bidirectional mapping")
    else:
        print("⚠️  Some tests failed. Check implementations.")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
