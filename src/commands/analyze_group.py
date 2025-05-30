#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comando CLI para análisis de grupos funcionales con IA.

Este módulo implementa el comando 'pp analyze-group' que permite
analizar grupos funcionales específicos usando IA.
"""

import os
import sys
from typing import Optional, List

from src.analyzers.ai_group_analyzer import get_ai_group_analyzer
from src.utils.logger import get_logger
from src.utils.config import ConfigManager
from src.ui.cli import CLI
from src.utils.token_counter import AnthropicTokenCounter
from src.ui.interactive_group_analyzer import InteractiveGroupAnalyzer

# Configurar logger
logger = get_logger()


class AnalyzeGroupCommand:
    """Comando para análisis de grupos funcionales con IA."""
    
    def __init__(self, config: Optional[ConfigManager] = None):
        """
        Inicializar comando de análisis de grupos.
        
        Args:
            config: Configuración opcional
        """
        self.config = config or ConfigManager()
        self.cli = CLI()
        self.analyzer = get_ai_group_analyzer(self.config)
        self.token_counter = AnthropicTokenCounter()
        self.interactive_ui = InteractiveGroupAnalyzer()
    
    def execute(self, group_name: Optional[str] = None, project_path: Optional[str] = None) -> bool:
        """
        Ejecutar análisis de grupo funcional.
        
        Args:
            group_name: Nombre del grupo a analizar
            project_path: Ruta al proyecto (usa directorio actual si no se especifica)
            
        Returns:
            True si el análisis fue exitoso
        """
        try:
            # Determinar ruta del proyecto
            if not project_path:
                project_path = os.getcwd()
            
            if not os.path.exists(project_path):
                self.cli.print_error(f"❌ Directorio no encontrado: {project_path}")
                return False
            
            # Si no se especifica grupo, mostrar grupos disponibles
            if not group_name:
                return self._show_available_groups(project_path)
            
            # Mostrar información inicial
            self.cli.print_header("🤖 Análisis de Grupo Funcional con IA")
            self.cli.print_info(f"📁 Proyecto: {os.path.basename(project_path)}")
            self.cli.print_info(f"🎯 Grupo: {group_name}")
            
            # Obtener grupos para encontrar el grupo específico
            groups = self.analyzer._get_functional_groups(project_path)
            if not groups:
                self.cli.print_error("❌ No se encontraron grupos funcionales en el proyecto")
                return False
            
            # Buscar el grupo específico
            target_group = None
            for group in groups:
                if group.get('name', '').lower() == group_name.lower():
                    target_group = group
                    break
                # También buscar por coincidencia parcial
                if group_name.lower() in group.get('name', '').lower():
                    target_group = group
                    break
            
            if not target_group:
                available_groups = [g.get('name', 'Sin nombre') for g in groups]
                self.cli.print_error(f"❌ Grupo '{group_name}' no encontrado")
                self.cli.print_info("📋 Grupos disponibles:")
                for group in available_groups:
                    self.cli.print_info(f"   • {group}")
                return False
            
            # Estimar costo y mostrar confirmación interactiva
            cost_estimate = self.token_counter.estimate_group_analysis_tokens(project_path, target_group)
            
            if not self.interactive_ui.show_cost_confirmation(cost_estimate, group_name):
                self.cli.print_warning("⚠️  Análisis cancelado por el usuario")
                return False
            
            # Ejecutar análisis con progreso interactivo
            with self.interactive_ui.progress_context("Analizando grupo funcional") as progress:
                result = self.analyzer.analyze_group(project_path, group_name)
                progress.update_status("Análisis completado")
            
            # Mostrar resultados usando la interfaz interactiva
            if result['success']:
                self.interactive_ui.show_analysis_results(result, cost_estimate)
                return True
            else:
                self._show_error_results(result)
                return False
        
        except KeyboardInterrupt:
            self.cli.print_warning("\n⚠️  Análisis interrumpido por el usuario")
            return False
        except Exception as e:
            logger.error(f"Error en comando analyze-group: {e}")
            self.cli.print_error(f"❌ Error inesperado: {str(e)}")
            return False
    
    def _show_available_groups(self, project_path: str) -> bool:
        """
        Mostrar grupos disponibles en el proyecto.
        
        Args:
            project_path: Ruta al proyecto
            
        Returns:
            True si se mostraron grupos disponibles
        """
        try:
            # Obtener grupos del analizador
            groups = self.analyzer._get_functional_groups(project_path)
            
            if not groups:
                self.cli.print_warning("⚠️  No se encontraron grupos funcionales en este proyecto")
                self.cli.print_info("💡 Ejecute primero 'pp analyze' para detectar grupos funcionales")
                return False
            
            # Usar la interfaz interactiva para mostrar grupos
            selected_group = self.interactive_ui.show_group_selection(groups, project_path)
            
            if selected_group:
                # Si el usuario seleccionó un grupo, analizarlo
                return self._analyze_selected_group(project_path, selected_group)
            
            return True
            
        except Exception as e:
            logger.error(f"Error al mostrar grupos disponibles: {e}")
            self.cli.print_error(f"❌ Error al obtener grupos: {str(e)}")
            return False
    
    def _analyze_selected_group(self, project_path: str, group: dict) -> bool:
        """
        Analizar un grupo seleccionado con confirmación de costo interactiva.
        
        Args:
            project_path: Ruta al proyecto
            group: Grupo seleccionado para analizar
            
        Returns:
            True si el análisis fue exitoso
        """
        try:
            group_name = group.get('name', 'Sin nombre')
            
            # Estimar costo del análisis
            cost_estimate = self.token_counter.estimate_group_analysis_tokens(project_path, group)
            
            # Mostrar confirmación de costo interactiva
            if not self.interactive_ui.show_cost_confirmation(cost_estimate, group_name):
                self.cli.print_warning("⚠️  Análisis cancelado por el usuario")
                return False
            
            # Ejecutar análisis con progreso interactivo
            with self.interactive_ui.progress_context("Analizando grupo funcional") as progress:
                result = self.analyzer.analyze_group(project_path, group_name)
                progress.update_status("Análisis completado")
            
            # Mostrar resultados usando la interfaz interactiva
            if result['success']:
                self.interactive_ui.show_analysis_results(result, cost_estimate)
                return True
            else:
                self._show_error_results(result)
                return False
                
        except KeyboardInterrupt:
            self.cli.print_warning("\n⚠️  Análisis interrumpido por el usuario")
            return False
        except Exception as e:
            logger.error(f"Error al analizar grupo seleccionado: {e}")
            self.cli.print_error(f"❌ Error inesperado: {str(e)}")
            return False
    
    def _show_success_results(self, result: dict) -> None:
        """
        Mostrar resultados exitosos del análisis.
        
        Args:
            result: Resultado del análisis
        """
        print()
        self.cli.print_success("✅ Análisis completado exitosamente!")
        print()
        
        # Información del análisis
        self.cli.print_info(f"🎯 Grupo analizado: {result['group_name']}")
        self.cli.print_info(f"📄 Archivos procesados: {result['files_analyzed']}")
        self.cli.print_info(f"📊 Reporte generado: {result['report_path']}")
        
        # Mostrar estadísticas básicas si están disponibles
        if 'analysis_results' in result:
            analysis_results = result['analysis_results']
            if analysis_results:
                # Calcular estadísticas rápidas
                quality_scores = [
                    r['analysis']['quality_score'] 
                    for r in analysis_results 
                    if r['analysis']['quality_score']
                ]
                
                if quality_scores:
                    avg_quality = sum(quality_scores) / len(quality_scores)
                    max_quality = max(quality_scores)
                    min_quality = min(quality_scores)
                    
                    print()
                    self.cli.print_info("📈 Estadísticas de Calidad:")
                    self.cli.print_info(f"   • Calidad promedio: {avg_quality:.1f}/10")
                    self.cli.print_info(f"   • Mejor archivo: {max_quality}/10")
                    self.cli.print_info(f"   • Peor archivo: {min_quality}/10")
        
        print()
        self.cli.print_info("💡 Revise el reporte completo para obtener análisis detallados de cada archivo")
    
    def _show_error_results(self, result: dict) -> None:
        """
        Mostrar resultados de error del análisis.
        
        Args:
            result: Resultado del análisis
        """
        print()
        self.cli.print_error("❌ Error en el análisis:")
        self.cli.print_error(f"   {result.get('error', 'Error desconocido')}")
        
        # Mostrar grupos disponibles si el error fue grupo no encontrado
        if 'available_groups' in result:
            print()
            self.cli.print_info("📋 Grupos disponibles:")
            for group in result['available_groups']:
                self.cli.print_info(f"   • {group}")
        
        # Mostrar sugerencias según el tipo de error
        error_msg = result.get('error', '').lower()
        
        if 'premium' in error_msg or 'suscripción' in error_msg:
            print()
            self.cli.print_info("💡 Para usar análisis con IA, necesita:")
            self.cli.print_info("   • Configurar API key de Anthropic")
            self.cli.print_info("   • Tener suscripción premium activa")
            self.cli.print_info("   • Ejecutar: pp config anthropic-key")
        
        elif 'no encontrado' in error_msg or 'not found' in error_msg:
            print()
            self.cli.print_info("💡 Sugerencias:")
            self.cli.print_info("   • Ejecute 'pp analyze-group' sin argumentos para ver grupos disponibles")
            self.cli.print_info("   • Verifique la ortografía del nombre del grupo")
            self.cli.print_info("   • Use comillas si el nombre contiene espacios")
        
        elif 'grupos funcionales' in error_msg:
            print()
            self.cli.print_info("💡 Para generar grupos funcionales:")
            self.cli.print_info("   • Ejecute 'pp analyze' primero")
            self.cli.print_info("   • Asegúrese de estar en un directorio de proyecto válido")


def main():
    """Función principal para ejecutar desde línea de comandos."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Analizar grupo funcional específico con IA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  pp analyze-group                     # Mostrar grupos disponibles
  pp analyze-group "Authentication"    # Analizar grupo de autenticación
  pp analyze-group "src/core"          # Analizar grupo de directorio
  pp analyze-group "Type: python"      # Analizar grupo por tipo de archivo
        """
    )
    
    parser.add_argument(
        'group_name',
        nargs='?',
        help='Nombre del grupo funcional a analizar'
    )
    
    parser.add_argument(
        '--project-path', '-p',
        help='Ruta al proyecto (usa directorio actual por defecto)'
    )
    
    parser.add_argument(
        '--config', '-c',
        help='Archivo de configuración personalizado'
    )
    
    args = parser.parse_args()
    
    # Crear configuración
    config = None
    if args.config:
        config = ConfigManager(config_file=args.config)
    
    # Ejecutar comando
    command = AnalyzeGroupCommand(config)
    success = command.execute(args.group_name, args.project_path)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
