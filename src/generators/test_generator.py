#!/usr/bin/env python3
"""
Generador de tests unitarios para ProjectPrompt.
Crea tests unitarios para las funcionalidades del proyecto detectadas.
"""
import os
import json
from typing import Dict, List, Any, Optional, Union, TYPE_CHECKING
from pathlib import Path

from src.utils import logger, config_manager

# Evitar importaciones circulares


class TestGenerator:
    """Generador de tests unitarios para funcionalidades del proyecto."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializar generador de tests.
        
        Args:
            config: Configuración adicional para el generador
        """
        self.config = config or {}
        self.output_dir = self.config.get("output_dir", "tests")
        self.test_framework = self.config.get("test_framework", "pytest")
        
        # Importar aquí para evitar importaciones circulares
        from src.analyzers.project_scanner import get_project_scanner
        from src.analyzers.functionality_detector import get_functionality_detector
        from src.analyzers.testability_analyzer import get_testability_analyzer
        
        # Obtener analizadores
        self.scanner = get_project_scanner()
        self.functionality_detector = get_functionality_detector()
        self.testability_analyzer = get_testability_analyzer()
        
        # Estructura de templates
        self.templates_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "templates", "tests"
        )
        
    def _get_template(self, template_name: str) -> str:
        """
        Obtener contenido de una plantilla de test.
        
        Args:
            template_name: Nombre de la plantilla
            
        Returns:
            Contenido de la plantilla
        """
        template_path = os.path.join(self.templates_dir, f"{template_name}.py")
        if not os.path.exists(template_path):
            template_path = os.path.join(self.templates_dir, "default.py")
        
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    
    def _generate_test_content(self, module_name: str, test_data: Dict[str, Any]) -> str:
        """
        Generar contenido para un archivo de test.
        
        Args:
            module_name: Nombre del módulo a testear
            test_data: Datos de test para el módulo
        
        Returns:
            Contenido del archivo de test
        """
        # Seleccionar plantilla según el tipo
        if "class" in test_data and test_data["class"]:
            template = self._get_template("class_test")
        else:
            template = self._get_template("module_test")
        
        # Reemplazar marcadores en la plantilla
        replacements = {
            "{{module_name}}": module_name,
            "{{module_path}}": test_data.get("module_path", ""),
            "{{class_name}}": test_data.get("class", ""),
            "{{functions}}": ", ".join(f'"{f}"' for f in test_data.get("functions", [])),
            "{{date}}": test_data.get("date", ""),
            "{{test_cases}}": self._generate_test_cases(test_data),
        }
        
        for marker, value in replacements.items():
            template = template.replace(marker, value)
        
        return template
    
    def _generate_test_cases(self, test_data: Dict[str, Any]) -> str:
        """
        Generar casos de prueba basados en las funciones detectadas.
        
        Args:
            test_data: Datos de prueba para el módulo
            
        Returns:
            Código de los casos de prueba
        """
        cases = []
        
        for function in test_data.get("functions", []):
            function_data = test_data.get("function_details", {}).get(function, {})
            
            # Determinar si es método de clase o función
            if test_data.get("class"):
                test_fn = f"test_{function}"
                test_code = self._generate_class_method_test(
                    test_data.get("class"), 
                    function, 
                    function_data
                )
            else:
                test_fn = f"test_{function}"
                test_code = self._generate_function_test(function, function_data)
            
            cases.append(f"def {test_fn}():\n{test_code}")
        
        return "\n\n".join(cases)
    
    def _generate_class_method_test(self, 
                                   class_name: str, 
                                   method_name: str, 
                                   method_data: Dict[str, Any]) -> str:
        """
        Generar caso de prueba para un método de clase.
        
        Args:
            class_name: Nombre de la clase
            method_name: Nombre del método
            method_data: Datos del método
            
        Returns:
            Código para el caso de prueba
        """
        # Construir instanciación de clase
        args = method_data.get("init_args", "")
        init_code = f"    # Inicializar objeto\n    obj = {class_name}({args})\n"
        
        # Parámetros del método
        param_values = method_data.get("params", "")
        expected = method_data.get("expected", "None")
        
        # Construir test básico
        test_code = [
            init_code,
            f"    # Verificar comportamiento de {method_name}",
            f"    result = obj.{method_name}({param_values})",
            f"    assert result == {expected}  # Verificar resultado esperado",
            ""
        ]
        
        # Si hay validaciones adicionales, añadirlas
        if "validations" in method_data:
            for validation in method_data["validations"]:
                test_code.insert(-1, f"    {validation}")
        
        return "\n".join(test_code)
    
    def _generate_function_test(self, 
                               function_name: str, 
                               function_data: Dict[str, Any]) -> str:
        """
        Generar caso de prueba para una función.
        
        Args:
            function_name: Nombre de la función
            function_data: Datos de la función
            
        Returns:
            Código para el caso de prueba
        """
        # Parámetros de la función
        module_path = function_data.get("module", "")
        param_values = function_data.get("params", "")
        expected = function_data.get("expected", "None")
        
        # Si se especificó un módulo completo, importar función específica
        import_code = ""
        if module_path:
            import_code = f"    from {module_path} import {function_name}\n"
        
        # Construir test básico
        test_code = [
            import_code,
            f"    # Verificar comportamiento de {function_name}",
            f"    result = {function_name}({param_values})",
            f"    assert result == {expected}  # Verificar resultado esperado",
            ""
        ]
        
        # Si hay setup adicional, añadirlo al inicio
        if "setup" in function_data:
            for setup_line in function_data["setup"]:
                test_code.insert(1, f"    {setup_line}")
        
        # Si hay validaciones adicionales, añadirlas
        if "validations" in function_data:
            for validation in function_data["validations"]:
                test_code.insert(-1, f"    {validation}")
        
        return "\n".join(test_code)
    
    def generate_tests_for_file(self, 
                                file_path: str, 
                                output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Generar tests para un archivo específico.
        
        Args:
            file_path: Ruta al archivo para el que generar tests
            output_dir: Directorio de salida (opcional)
            
        Returns:
            Información sobre los tests generados
        """
        # Normalizar rutas
        file_path = os.path.abspath(file_path)
        out_dir = output_dir or self.output_dir
        
        # Verificar que el archivo existe
        if not os.path.isfile(file_path):
            logger.error(f"El archivo {file_path} no existe")
            return {"success": False, "error": "El archivo no existe"}
        
        # Analizar testabilidad del archivo
        test_data = self.testability_analyzer.analyze_file(file_path)
        
        # Verificar si hay contenido para testear
        if not test_data.get("functions") and not test_data.get("classes"):
            return {"success": False, "error": "No se encontró contenido testeable en el archivo"}
        
        # Determinar nombre del archivo de test
        base_name = os.path.basename(file_path)
        file_name, _ = os.path.splitext(base_name)
        test_file_name = f"test_{file_name}.py"
        
        # Asegurar que el directorio de salida existe
        os.makedirs(out_dir, exist_ok=True)
        
        # Crear archivo de test para módulo
        test_file_path = os.path.join(out_dir, test_file_name)
        
        # Generar contenido y escribir archivo
        content = self._generate_test_content(file_name, test_data)
        try:
            with open(test_file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            logger.error(f"Error al escribir archivo de test: {e}")
            return {"success": False, "error": str(e)}
        
        return {
            "success": True,
            "test_file": test_file_path,
            "module_name": file_name,
            "test_cases": len(test_data.get("functions", [])),
            "classes_tested": len(test_data.get("classes", [])),
        }
    
    def generate_tests_for_functionality(self, 
                                        functionality_name: str, 
                                        project_path: str,
                                        output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Generar tests para una funcionalidad específica.
        
        Args:
            functionality_name: Nombre de la funcionalidad
            project_path: Ruta al proyecto
            output_dir: Directorio de salida (opcional)
            
        Returns:
            Información sobre los tests generados
        """
        # Normalizar rutas
        project_path = os.path.abspath(project_path)
        out_dir = output_dir or self.output_dir
        
        # Obtener detalles de funcionalidad
        functionality_data = self.functionality_detector.detect_functionality(
            project_path, functionality_name
        )
        
        if not functionality_data:
            return {
                "success": False, 
                "error": f"No se encontró la funcionalidad {functionality_name}"
            }
        
        # Obtener archivos relevantes
        files = functionality_data.get("files", [])
        
        # Generar tests para cada archivo
        results = []
        for file_path in files:
            test_result = self.generate_tests_for_file(file_path, out_dir)
            if test_result["success"]:
                results.append(test_result)
        
        return {
            "success": len(results) > 0,
            "functionality": functionality_name,
            "tests_generated": len(results),
            "results": results
        }
    
    def generate_tests_for_project(self, 
                                  project_path: str,
                                  output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Generar tests para todo un proyecto.
        
        Args:
            project_path: Ruta al proyecto
            output_dir: Directorio de salida (opcional)
            
        Returns:
            Información sobre los tests generados
        """
        # Normalizar rutas
        project_path = os.path.abspath(project_path)
        out_dir = output_dir or self.output_dir
        
        # Escanear proyecto
        project_data = self.scanner.scan_project(project_path)
        
        # Detectar funcionalidades
        functionality_data = self.functionality_detector.detect_functionalities(project_path)
        main_functionalities = functionality_data.get("main_functionalities", [])
        
        # Resultados generales
        all_results = {
            "success": False,
            "project_path": project_path,
            "tests_generated": 0,
            "functionalities_tested": 0,
            "functionality_results": {}
        }
        
        # Generar tests para cada funcionalidad
        for functionality in main_functionalities:
            result = self.generate_tests_for_functionality(
                functionality, project_path, out_dir
            )
            
            all_results["functionality_results"][functionality] = result
            
            if result["success"]:
                all_results["functionalities_tested"] += 1
                all_results["tests_generated"] += len(result["results"])
        
        # Marcar éxito si se generó al menos un test
        all_results["success"] = all_results["tests_generated"] > 0
        
        return all_results
    
    def save_test_config(self, 
                        project_path: str, 
                        output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Guardar configuración de test para el proyecto.
        
        Args:
            project_path: Ruta al proyecto
            output_path: Ruta para guardar configuración (opcional)
            
        Returns:
            Información sobre la configuración guardada
        """
        # Normalizar ruta
        project_path = os.path.abspath(project_path)
        
        # Si no se especifica ruta de salida, usar directorio por defecto
        if not output_path:
            output_path = os.path.join(project_path, "pytest.ini")
        
        # Escanear proyecto
        project_data = self.scanner.scan_project(project_path)
        
        # Determinar configuración según el framework de test detectado
        framework = self._detect_test_framework(project_data)
        self.test_framework = framework
        
        # Generar configuración específica del framework
        if framework == "pytest":
            config_content = self._generate_pytest_config()
        elif framework == "unittest":
            config_content = self._generate_unittest_config()
        else:
            # Framework desconocido, usar pytest por defecto
            config_content = self._generate_pytest_config()
        
        # Escribir archivo de configuración
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(config_content)
        except Exception as e:
            logger.error(f"Error al guardar configuración de test: {e}")
            return {"success": False, "error": str(e)}
        
        return {
            "success": True,
            "config_path": output_path,
            "framework": framework,
        }
    
    def _detect_test_framework(self, project_data: Dict[str, Any]) -> str:
        """
        Detectar framework de testing usado en el proyecto.
        
        Args:
            project_data: Datos del proyecto escaneado
            
        Returns:
            Nombre del framework (pytest, unittest, etc.)
        """
        # Buscar en archivos de configuración o dependencias
        dependencies = project_data.get("dependencies", {})
        
        # Buscar en requirements.txt o setup.py
        if "pytest" in str(dependencies):
            return "pytest"
        elif "unittest" in str(dependencies) and "pytest" not in str(dependencies):
            return "unittest"
        
        # Buscar archivos de configuración específicos
        if any(f.endswith("pytest.ini") for f in project_data.get("files", [])):
            return "pytest"
        
        # Por defecto, usar pytest
        return "pytest"
    
    def _generate_pytest_config(self) -> str:
        """
        Generar configuración para pytest.
        
        Returns:
            Contenido del archivo pytest.ini
        """
        return """[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Opciones adicionales
addopts = --verbose
"""
    
    def _generate_unittest_config(self) -> str:
        """
        Generar configuración para unittest.
        
        Returns:
            Contenido del archivo unittest.cfg
        """
        return """[unittest]
start-dir = tests
pattern = test_*.py
"""


def get_test_generator(config: Optional[Dict[str, Any]] = None) -> TestGenerator:
    """
    Obtener instancia del generador de tests.
    
    Args:
        config: Configuración adicional para el generador
        
    Returns:
        Instancia de TestGenerator
    """
    return TestGenerator(config)
