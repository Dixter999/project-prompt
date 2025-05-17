#!/usr/bin/env python3
"""
Analizador de testabilidad para ProjectPrompt.
Examina código fuente para determinar qué elementos pueden ser testeados
y proporciona datos para la generación de tests unitarios.
"""
import os
import re
import ast
import json
import inspect
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime

from src.utils import logger
from src.analyzers.file_analyzer import FileAnalyzer


class TestabilityAnalyzer:
    """
    Analizador de testabilidad para código Python.
    Identifica funciones, métodos y clases que pueden ser testeados.
    """
    
    def __init__(self):
        """Inicializar analizador de testabilidad."""
        self.file_analyzer = FileAnalyzer()
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analizar un archivo para determinar elementos testables.
        
        Args:
            file_path: Ruta al archivo a analizar
            
        Returns:
            Diccionario con información sobre elementos testables
        """
        file_path = os.path.abspath(file_path)
        
        # Verificar existencia y tipo de archivo
        if not os.path.exists(file_path):
            logger.error(f"El archivo {file_path} no existe")
            return {}
        
        # Comprobar que es un archivo Python
        if not file_path.endswith('.py'):
            logger.warning(f"El archivo {file_path} no es un archivo Python")
            return {}
        
        try:
            # Leer contenido del archivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Analizar estructura del archivo con AST
            tree = ast.parse(content, filename=file_path)
            
            # Extraer información testable
            result = self._extract_testable_elements(tree, file_path)
            
            # Añadir metadatos
            result["file_path"] = file_path
            result["module_path"] = self._file_to_module_path(file_path)
            result["date"] = datetime.now().strftime("%Y-%m-%d")
            
            return result
            
        except Exception as e:
            logger.error(f"Error al analizar testabilidad de {file_path}: {e}")
            return {}
    
    def _extract_testable_elements(self, tree: ast.AST, file_path: str) -> Dict[str, Any]:
        """
        Extraer elementos testables de un árbol AST.
        
        Args:
            tree: Árbol AST del archivo
            file_path: Ruta al archivo
            
        Returns:
            Diccionario con información sobre elementos testables
        """
        result = {
            "functions": [],
            "classes": [],
            "imports": [],
            "function_details": {},
            "class_details": {}
        }
        
        # Extraer imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    result["imports"].append(name.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for name in node.names:
                    result["imports"].append(f"{module}.{name.name}" if module else name.name)
        
        # Extraer funciones globales
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                if not func_name.startswith('_'):  # Excluir funciones privadas
                    result["functions"].append(func_name)
                    result["function_details"][func_name] = self._analyze_function(node)
        
        # Extraer clases y métodos
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                result["classes"].append(class_name)
                
                # Analizar métodos de la clase
                methods = []
                method_details = {}
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_name = item.name
                        if not method_name.startswith('_') or method_name == '__init__':
                            methods.append(method_name)
                            method_details[method_name] = self._analyze_function(item)
                
                result["class_details"][class_name] = {
                    "methods": methods,
                    "method_details": method_details
                }
        
        return result
    
    def _analyze_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """
        Analizar una función para extraer información útil para testing.
        
        Args:
            node: Nodo AST de la función
            
        Returns:
            Diccionario con información de la función
        """
        # Información básica
        info = {
            "name": node.name,
            "args": [],
            "returns": self._extract_return_type(node),
            "has_docstring": False,
            "complexity": self._estimate_complexity(node),
            "raises": self._extract_exceptions(node),
            "dependencies": self._extract_dependencies(node),
            "testing_hints": []
        }
        
        # Extraer argumentos
        for arg in node.args.args:
            arg_name = arg.arg
            arg_type = None
            
            # Intentar extraer tipo de argumento si está disponible
            if hasattr(arg, 'annotation') and arg.annotation:
                arg_type = ast.unparse(arg.annotation)
            
            info["args"].append({
                "name": arg_name,
                "type": arg_type
            })
        
        # Verificar docstring
        if (len(node.body) > 0 and isinstance(node.body[0], ast.Expr) 
                and isinstance(node.body[0].value, ast.Str)):
            info["has_docstring"] = True
            docstring = node.body[0].value.s
            
            # Buscar información en docstring (params, returns, etc)
            if 'param' in docstring or ':param' in docstring:
                info["has_param_docs"] = True
            
            if 'return' in docstring or ':return' in docstring:
                info["has_return_docs"] = True
                
            if 'raise' in docstring or ':raise' in docstring:
                info["has_exception_docs"] = True
        
        # Generar consejos para testing
        if info["complexity"] > 5:
            info["testing_hints"].append("Alta complejidad, considerar múltiples casos de prueba")
        
        if info["raises"]:
            info["testing_hints"].append("Verificar manejo de excepciones")
            
        if len(info["args"]) > 3:
            info["testing_hints"].append("Muchos parámetros, considerar casos de borde")
            
        return info
    
    def _extract_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """
        Extraer tipo de retorno de una función.
        
        Args:
            node: Nodo AST de la función
            
        Returns:
            Tipo de retorno o None
        """
        if node.returns:
            return ast.unparse(node.returns)
        return None
    
    def _estimate_complexity(self, node: ast.FunctionDef) -> int:
        """
        Estimar complejidad ciclomática de una función.
        
        Args:
            node: Nodo AST de la función
            
        Returns:
            Estimación de complejidad
        """
        # Complejidad base
        complexity = 1
        
        # Recorrer nodos y contar estructuras de control
        for subnode in ast.walk(node):
            if isinstance(subnode, (ast.If, ast.While, ast.For, ast.comprehension)):
                complexity += 1
            elif isinstance(subnode, ast.BoolOp) and isinstance(subnode.op, ast.And):
                complexity += len(subnode.values) - 1
            elif isinstance(subnode, ast.BoolOp) and isinstance(subnode.op, ast.Or):
                complexity += len(subnode.values) - 1
            elif isinstance(subnode, ast.Try):
                complexity += len(subnode.handlers)
        
        return complexity
    
    def _extract_exceptions(self, node: ast.FunctionDef) -> List[str]:
        """
        Extraer excepciones que puede lanzar una función.
        
        Args:
            node: Nodo AST de la función
            
        Returns:
            Lista de excepciones
        """
        exceptions = []
        
        # Buscar raises explícitos
        for subnode in ast.walk(node):
            if isinstance(subnode, ast.Raise):
                if isinstance(subnode.exc, ast.Name):
                    exceptions.append(subnode.exc.id)
                elif isinstance(subnode, ast.Call) and hasattr(subnode.exc, 'func'):
                    if hasattr(subnode.exc.func, 'id'):
                        exceptions.append(subnode.exc.func.id)
        
        return exceptions
    
    def _extract_dependencies(self, node: ast.FunctionDef) -> List[str]:
        """
        Extraer dependencias externas de una función.
        
        Args:
            node: Nodo AST de la función
            
        Returns:
            Lista de dependencias
        """
        dependencies = set()
        
        for subnode in ast.walk(node):
            if isinstance(subnode, ast.Name) and isinstance(subnode.ctx, ast.Load):
                if subnode.id not in ('self', 'cls') and not keyword_or_builtin(subnode.id):
                    dependencies.add(subnode.id)
            
            # Llamadas a atributos externos
            elif isinstance(subnode, ast.Attribute) and isinstance(subnode.ctx, ast.Load):
                if hasattr(subnode.value, 'id') and subnode.value.id not in ('self', 'cls'):
                    dependencies.add(f"{subnode.value.id}.{subnode.attr}")
        
        return list(dependencies)
    
    def _file_to_module_path(self, file_path: str) -> str:
        """
        Convertir ruta de archivo a ruta de módulo.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Ruta de módulo
        """
        # Convertir ruta de archivo a formato de importación de módulo
        path_parts = []
        current = os.path.abspath(file_path)
        
        # Eliminar extensión
        base, _ = os.path.splitext(current)
        current = base
        
        # Construir ruta inversamente hasta encontrar __init__.py o raíz de proyecto
        while current and os.path.basename(current) != "":
            dirname = os.path.dirname(current)
            basename = os.path.basename(current)
            
            path_parts.insert(0, basename)
            
            # Verificar si estamos en la raíz de un paquete
            if not os.path.exists(os.path.join(dirname, "__init__.py")):
                break
            
            current = dirname
        
        return ".".join(path_parts)


def keyword_or_builtin(name: str) -> bool:
    """
    Determinar si un nombre es una palabra clave o una función incorporada.
    
    Args:
        name: Nombre a verificar
        
    Returns:
        True si es palabra clave o función incorporada, False en caso contrario
    """
    import keyword
    import builtins
    
    return name in keyword.kwlist or name in dir(builtins)


def get_testability_analyzer() -> TestabilityAnalyzer:
    """
    Obtener instancia del analizador de testabilidad.
    
    Returns:
        Instancia de TestabilityAnalyzer
    """
    return TestabilityAnalyzer()
