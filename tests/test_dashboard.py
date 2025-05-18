#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests para el módulo de dashboard y tracker de progreso.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import json
import tempfile
from datetime import datetime

from src.analyzers.project_progress_tracker import ProjectProgressTracker
from src.ui.dashboard import DashboardGenerator
from src.utils.config import ConfigManager


class TestProjectProgressTracker(unittest.TestCase):
    """Pruebas para el rastreador de progreso del proyecto."""
    
    def setUp(self):
        """Inicializar para cada test."""
        self.test_dir = tempfile.mkdtemp()
        self.config = MagicMock(spec=ConfigManager)
        
        # Simular suscripción premium
        subscription_patcher = patch('src.analyzers.project_progress_tracker.get_subscription_manager')
        self.mock_subscription = subscription_patcher.start()
        self.mock_subscription_instance = MagicMock()
        self.mock_subscription_instance.is_premium_feature_available.return_value = True
        self.mock_subscription.return_value = self.mock_subscription_instance
        
        # Simular ProjectScanner
        scanner_patcher = patch('src.analyzers.project_progress_tracker.ProjectScanner')
        self.mock_scanner = scanner_patcher.start()
        self.mock_scanner_instance = MagicMock()
        self.mock_scanner_instance.files = [
            os.path.join(self.test_dir, 'file1.py'),
            os.path.join(self.test_dir, 'file2.py'),
            os.path.join(self.test_dir, 'test_file.py'),
            os.path.join(self.test_dir, 'README.md')
        ]
        self.mock_scanner.return_value = self.mock_scanner_instance
        
        # Simular DependencyGraph
        graph_patcher = patch('src.analyzers.project_progress_tracker.DependencyGraph')
        self.mock_graph = graph_patcher.start()
        self.mock_graph_instance = MagicMock()
        self.mock_graph_instance.graph = {}
        self.mock_graph.return_value = self.mock_graph_instance
        
        # Simular CompletenessVerifier
        completeness_patcher = patch('src.analyzers.project_progress_tracker.CompletenessVerifier')
        self.mock_completeness = completeness_patcher.start()
        self.mock_completeness_instance = MagicMock()
        self.mock_completeness_instance.verify_project_completeness.return_value = {
            "score": 75,
            "implemented_components": ["comp1", "comp2", "comp3"],
            "missing_components": ["comp4"],
            "suggestions": ["Implement comp4"]
        }
        self.mock_completeness.return_value = self.mock_completeness_instance
        
        # Simular FileAnalyzer
        file_analyzer_patcher = patch('src.analyzers.project_progress_tracker.FileAnalyzer')
        self.mock_file_analyzer = file_analyzer_patcher.start()
        self.mock_file_analyzer_instance = MagicMock()
        self.mock_file_analyzer.return_value = self.mock_file_analyzer_instance
        
        # Simular subprocess.check_output para las llamadas a Git
        subprocess_patcher = patch('src.analyzers.project_progress_tracker.subprocess.check_output')
        self.mock_subprocess = subprocess_patcher.start()
        self.mock_subprocess.side_effect = self._mock_git_output
        
        self.addCleanup(subscription_patcher.stop)
        self.addCleanup(scanner_patcher.stop)
        self.addCleanup(graph_patcher.stop)
        self.addCleanup(completeness_patcher.stop)
        self.addCleanup(file_analyzer_patcher.stop)
        self.addCleanup(subprocess_patcher.stop)
        
        # Crear instancia para pruebas
        self.tracker = ProjectProgressTracker(self.test_dir, self.config)
    
    def _mock_git_output(self, cmd, **kwargs):
        """Simular salida de comandos git."""
        if 'branch' in cmd:
            return "* main\n  feature/test\n  feature/other".encode()
        elif 'log' in cmd and '--format=%ad' in cmd:
            return "2023-05-01 12:00:00 +0000".encode()
        elif 'log' in cmd and '--format=%s' in cmd:
            return "Test commit message".encode()
        elif 'rev-list' in cmd:
            return "42".encode()
        elif 'shortlog' in cmd:
            return "    30\tUser One\n    12\tUser Two".encode()
        else:
            return "".encode()
    
    def test_get_project_overview(self):
        """Probar obtención de visión general del proyecto."""
        # Simular lectura de archivos
        with patch('builtins.open', mock_open(read_data="def test():\n    # Comment\n    return True")):
            overview = self.tracker.get_project_overview()
        
        self.assertIsInstance(overview, dict)
        self.assertEqual(overview["name"], os.path.basename(self.test_dir))
        self.assertIn("files", overview)
        self.assertIn("code_metrics", overview)
        self.assertIn("timestamp", overview)
    
    def test_get_progress_metrics(self):
        """Probar obtención de métricas de progreso."""
        # Simular lectura de archivos
        with patch('builtins.open', mock_open(read_data="def test():\n    # Comment\n    return True")):
            metrics = self.tracker.get_progress_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn("completeness", metrics)
        self.assertIn("code_quality", metrics)
        self.assertIn("testing", metrics)
        self.assertEqual(metrics["completeness"]["score"], 75)
    
    def test_get_branch_status(self):
        """Probar obtención de estado de branches."""
        branches = self.tracker.get_branch_status()
        
        self.assertIsInstance(branches, dict)
        
        # Si es un repositorio Git, verificar estructura completa
        if "error" not in branches:
            self.assertIn("branches", branches)
            self.assertIn("categories", branches)
            self.assertTrue(any(b["current"] for b in branches["branches"]))
        else:
            # En caso contrario, verificar que el error sea el esperado
            self.assertEqual(branches["error"], "No es un repositorio Git")
    
    def test_get_feature_progress(self):
        """Probar obtención de progreso por características."""
        # Crear un directorio para simular una característica
        feature_dir = os.path.join(self.test_dir, "feature1")
        os.makedirs(feature_dir, exist_ok=True)
        
        # Simular listdir
        with patch('os.listdir', return_value=["feature1"]):
            with patch('os.path.isdir', return_value=True):
                with patch.object(self.tracker, '_get_files_in_dir', return_value=[
                    os.path.join(feature_dir, "module.py"),
                    os.path.join(feature_dir, "test_module.py")
                ]):
                    with patch.object(self.tracker, '_count_code_lines', return_value=50):
                        with patch.object(self.tracker, '_count_test_lines', return_value=20):
                            features = self.tracker.get_feature_progress()
        
        self.assertIsInstance(features, dict)
        self.assertIn("features", features)
        self.assertIn("feature1", features["features"])
        self.assertTrue(features["features"]["feature1"]["has_tests"])
    
    def test_get_recommendations(self):
        """Probar obtención de recomendaciones."""
        # Simular métricas para generar recomendaciones
        with patch.object(self.tracker, 'get_progress_metrics', return_value={
            "code_quality": {"documentation_percentage": 20},
            "testing": {"coverage": 30}
        }):
            with patch.object(self.tracker, 'get_branch_status', return_value={
                "branches": []
            }):
                recommendations = self.tracker.get_recommendations()
        
        self.assertIsInstance(recommendations, list)
        self.assertTrue(len(recommendations) > 0)
        self.assertIn("message", recommendations[0])
        self.assertIn("action", recommendations[0])
    
    def test_is_code_file(self):
        """Probar detección de archivos de código."""
        self.assertTrue(self.tracker._is_code_file("test.py"))
        self.assertTrue(self.tracker._is_code_file("file.js"))
        self.assertFalse(self.tracker._is_code_file("image.png"))
        self.assertFalse(self.tracker._is_code_file("document.pdf"))


class TestDashboardGenerator(unittest.TestCase):
    """Pruebas para el generador de dashboard."""
    
    def setUp(self):
        """Inicializar para cada test."""
        self.test_dir = tempfile.mkdtemp()
        self.config = MagicMock(spec=ConfigManager)
        
        # Simular suscripción premium
        subscription_patcher = patch('src.ui.dashboard.get_subscription_manager')
        self.mock_subscription = subscription_patcher.start()
        self.mock_subscription_instance = MagicMock()
        self.mock_subscription_instance.is_premium_feature_available.return_value = True
        self.mock_subscription.return_value = self.mock_subscription_instance
        
        # Simular ProjectProgressTracker
        tracker_patcher = patch('src.ui.dashboard.get_project_progress_tracker')
        self.mock_tracker = tracker_patcher.start()
        self.mock_tracker_instance = MagicMock()
        self.mock_tracker_instance.get_project_overview.return_value = {
            "name": "test-project",
            "path": self.test_dir,
            "last_updated": "2023-05-01 12:00:00",
            "files": {
                "total": 10,
                "by_extension": {".py": 5, ".md": 2, ".json": 3}
            },
            "code_metrics": {
                "total_lines": 500,
                "code_lines": 350,
                "comment_lines": 100,
                "files": 5
            },
            "structure": {
                "directories": 3,
                "max_depth": 2,
                "dir_structure": {"": 5, "src": 3, "tests": 2}
            }
        }
        self.mock_tracker_instance.get_progress_metrics.return_value = {
            "completeness": {
                "score": 75,
                "implemented_components": ["comp1", "comp2", "comp3"],
                "missing_components": ["comp4"],
                "suggestions": ["Implement comp4"]
            },
            "code_quality": {
                "documentation_percentage": 65.5,
                "complex_files": [
                    {"file": "src/complex.py", "lines": 600, "functions": 25, "nested_depth": 6}
                ],
                "duplication_estimate": {"percentage": 15}
            },
            "testing": {
                "test_files": 3,
                "code_files": 7,
                "ratio": 0.43,
                "coverage": 60
            },
            "advanced": {
                "modularity_score": 80,
                "architecture_pattern": "MVC (Model-View-Controller)",
                "central_modules": [
                    {"file": "src/core.py", "dependents": 12}
                ]
            }
        }
        self.mock_tracker_instance.get_branch_status.return_value = {
            "branches": [
                {"name": "main", "current": True, "last_commit_date": "2023-05-01 12:00:00", "last_commit_msg": "Initial commit"},
                {"name": "feature/test", "current": False, "last_commit_date": "2023-04-15 10:00:00", "last_commit_msg": "Test feature"}
            ],
            "categories": {
                "main": [{"name": "main", "current": True, "last_commit_date": "2023-05-01 12:00:00", "last_commit_msg": "Initial commit"}],
                "feature": [{"name": "feature/test", "current": False, "last_commit_date": "2023-04-15 10:00:00", "last_commit_msg": "Test feature"}],
                "bugfix": [],
                "release": [],
                "develop": [],
                "other": []
            },
            "count": 2
        }
        self.mock_tracker_instance.get_feature_progress.return_value = {
            "features": {
                "feature1": {
                    "files": 5,
                    "code_lines": 300,
                    "test_lines": 100,
                    "has_tests": True,
                    "completion_estimate": 85
                },
                "feature2": {
                    "files": 3,
                    "code_lines": 150,
                    "test_lines": 0,
                    "has_tests": False,
                    "completion_estimate": 40
                }
            },
            "count": 2
        }
        self.mock_tracker_instance.get_recommendations.return_value = [
            {
                "type": "testing",
                "priority": "medium",
                "message": "Baja cobertura en el módulo X",
                "action": "Añade tests para las funciones principales"
            },
            {
                "type": "code_quality",
                "priority": "high",
                "message": "Alta complejidad en src/complex.py",
                "action": "Refactoriza dividiéndolo en módulos más pequeños"
            }
        ]
        self.mock_tracker.return_value = self.mock_tracker_instance
        
        # Simular webbrowser.open
        webbrowser_patcher = patch('src.ui.dashboard.webbrowser.open')
        self.mock_webbrowser = webbrowser_patcher.start()
        
        self.addCleanup(subscription_patcher.stop)
        self.addCleanup(tracker_patcher.stop)
        self.addCleanup(webbrowser_patcher.stop)
        
        # Crear instancia para pruebas
        self.dashboard = DashboardGenerator(self.test_dir, self.config)
    
    def test_generate_dashboard_premium(self):
        """Probar generación de dashboard premium."""
        with patch('builtins.open', mock_open()) as mock_file:
            output_path = self.dashboard.generate_dashboard(open_browser=False)
        
        self.assertTrue(mock_file.called)
        self.assertTrue(os.path.dirname(output_path))
        self.assertTrue(output_path.endswith('.html'))
    
    def test_generate_dashboard_free(self):
        """Probar generación de dashboard free."""
        # Cambiar a modo free
        self.mock_subscription_instance.is_premium_feature_available.return_value = False
        self.dashboard.premium_access = False
        
        with patch('builtins.open', mock_open()) as mock_file:
            output_path = self.dashboard.generate_dashboard(open_browser=False)
        
        self.assertTrue(mock_file.called)
        self.assertTrue(output_path.endswith('_free.html'))
    
    def test_generate_html_includes_all_sections_in_premium(self):
        """Verificar que el HTML premium incluye todas las secciones."""
        html = self.dashboard._generate_html({
            "overview": self.mock_tracker_instance.get_project_overview(),
            "progress": self.mock_tracker_instance.get_progress_metrics(),
            "branches": self.mock_tracker_instance.get_branch_status(),
            "features": self.mock_tracker_instance.get_feature_progress(),
            "recommendations": self.mock_tracker_instance.get_recommendations(),
            "premium": True,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        self.assertIn("Visión General", html)
        self.assertIn("Métricas de Progreso", html)
        self.assertIn("Estado de Branches", html)
        self.assertIn("Progreso por Características", html)
        self.assertIn("Recomendaciones", html)
        self.assertIn("Premium", html)
    
    def test_generate_html_limited_sections_in_free(self):
        """Verificar que el HTML free incluye solo las secciones permitidas."""
        html = self.dashboard._generate_html({
            "overview": self.mock_tracker_instance.get_project_overview(),
            "progress": {
                "code_quality": self.mock_tracker_instance.get_progress_metrics().get("code_quality", {}),
                "testing": self.mock_tracker_instance.get_progress_metrics().get("testing", {})
            },
            "premium": False,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, is_free=True)
        
        self.assertIn("Visión General", html)
        self.assertIn("Métricas de Progreso", html)
        self.assertIn("Free Version", html)
        self.assertNotIn("Estado de Branches", html)
        self.assertNotIn("Progreso por Características", html)
        self.assertIn("Actualiza a Premium", html)


if __name__ == '__main__':
    unittest.main()
