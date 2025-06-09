"""
API Diagnostics Module - Sistema de Implementación Adaptativa
Herramientas para verificar y diagnosticar el uso correcto de la API
"""

import os
import json
import time
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import click

# Importaciones locales se harán dinámicamente para evitar problemas circulares


@dataclass
class DiagnosticResult:
    """Resultado de un diagnóstico específico"""
    test_name: str
    status: str  # 'PASS', 'FAIL', 'WARNING', 'INFO'
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class APIHealthReport:
    """Reporte completo de salud de la API"""
    overall_status: str
    api_key_status: str
    connection_status: str
    performance_metrics: Dict[str, Any]
    cost_analysis: Dict[str, Any]
    cache_status: Dict[str, Any]
    diagnostics: List[DiagnosticResult]
    recommendations: List[str]
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class APIDiagnostics:
    """
    Sistema completo de diagnóstico para verificar el uso correcto de la API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializar el sistema de diagnósticos
        
        Args:
            api_key: Clave de API opcional (se tomará de env si no se proporciona)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.diagnostics_results = []
        
    def run_complete_diagnosis(self, verbose: bool = True) -> APIHealthReport:
        """
        Ejecuta un diagnóstico completo del sistema API
        
        Args:
            verbose: Si imprimir resultados en tiempo real
            
        Returns:
            Reporte completo de salud de la API
        """
        if verbose:
            click.echo("🔍 Iniciando diagnóstico completo del sistema API...")
            
        # Ejecutar todas las pruebas de diagnóstico
        self.diagnostics_results = []
        
        # 1. Verificar configuración de API key
        api_key_result = self._check_api_key_configuration()
        self.diagnostics_results.append(api_key_result)
        
        if verbose:
            self._print_diagnostic_result(api_key_result)
        
        # 2. Verificar conectividad
        connection_result = self._check_api_connectivity()
        self.diagnostics_results.append(connection_result)
        
        if verbose:
            self._print_diagnostic_result(connection_result)
        
        # 3. Verificar componentes FASE 1
        fase1_result = self._check_fase1_components()
        self.diagnostics_results.append(fase1_result)
        
        if verbose:
            self._print_diagnostic_result(fase1_result)
        
        # 4. Verificar componentes FASE 2
        fase2_result = self._check_fase2_components()
        self.diagnostics_results.append(fase2_result)
        
        if verbose:
            self._print_diagnostic_result(fase2_result)
        
        # 5. Pruebas de rendimiento
        performance_result = self._check_performance_metrics()
        self.diagnostics_results.append(performance_result)
        
        if verbose:
            self._print_diagnostic_result(performance_result)
        
        # 6. Análisis de costos
        cost_result = self._check_cost_tracking()
        self.diagnostics_results.append(cost_result)
        
        if verbose:
            self._print_diagnostic_result(cost_result)
        
        # 7. Estado del cache
        cache_result = self._check_cache_status()
        self.diagnostics_results.append(cache_result)
        
        if verbose:
            self._print_diagnostic_result(cache_result)
        
        # 8. Prueba de request básico
        request_result = self._test_basic_request()
        self.diagnostics_results.append(request_result)
        
        if verbose:
            self._print_diagnostic_result(request_result)
        
        # Generar reporte final
        report = self._generate_health_report()
        
        if verbose:
            self._print_final_report(report)
            
        return report
    
    def _check_api_key_configuration(self) -> DiagnosticResult:
        """Verificar la configuración de la API key"""
        try:
            if not self.api_key:
                return DiagnosticResult(
                    test_name="API Key Configuration",
                    status="FAIL",
                    message="No se encontró ANTHROPIC_API_KEY en variables de entorno",
                    details={
                        "env_var_name": "ANTHROPIC_API_KEY",
                        "current_value": None,
                        "solution": "Configurar la variable de entorno ANTHROPIC_API_KEY"
                    }
                )
            
            # Verificar formato de la API key
            if not self.api_key.startswith('sk-ant-'):
                return DiagnosticResult(
                    test_name="API Key Configuration",
                    status="WARNING",
                    message="Formato de API key potencialmente incorrecto",
                    details={
                        "expected_prefix": "sk-ant-",
                        "actual_prefix": self.api_key[:10] + "...",
                        "key_length": len(self.api_key)
                    }
                )
            
            return DiagnosticResult(
                test_name="API Key Configuration",
                status="PASS",
                message="API key configurada correctamente",
                details={
                    "key_prefix": self.api_key[:10] + "...",
                    "key_length": len(self.api_key)
                }
            )
            
        except Exception as e:
            return DiagnosticResult(
                test_name="API Key Configuration",
                status="FAIL",
                message=f"Error al verificar API key: {str(e)}"
            )
    
    def _check_api_connectivity(self) -> DiagnosticResult:
        """Verificar conectividad con la API de Anthropic"""
        try:
            if not self.api_key:
                return DiagnosticResult(
                    test_name="API Connectivity",
                    status="FAIL",
                    message="No se puede probar conectividad sin API key"
                )
            
            # Importación dinámica
            from .anthropic_client import AnthropicClient
            
            # Crear cliente y hacer una prueba básica
            start_time = time.time()
            client = AnthropicClient(api_key=self.api_key)
            
            # Preparar una prueba mínima
            test_config = {
                'prompt': 'Responde solo "OK" si puedes procesarme este mensaje.',
                'system_prompt': 'Eres un asistente de prueba. Responde únicamente "OK".',
                'model': 'claude-3-haiku-20240307',  # Modelo más económico para pruebas
                'max_tokens': 10,
                'temperature': 0.0
            }
            
            response = client.send_enriched_request(test_config, use_cache=False)
            end_time = time.time()
            
            return DiagnosticResult(
                test_name="API Connectivity",
                status="PASS",
                message="Conectividad con Anthropic API exitosa",
                details={
                    "response_time": round(end_time - start_time, 2),
                    "model_used": response.get('model'),
                    "tokens_used": response.get('usage', {}),
                    "response_preview": response.get('content', '')[:50] + "..."
                }
            )
            
        except Exception as e:
            return DiagnosticResult(
                test_name="API Connectivity",
                status="FAIL",
                message=f"Error de conectividad: {str(e)}",
                details={"error_type": type(e).__name__}
            )
    
    def _check_fase1_components(self) -> DiagnosticResult:
        """Verificar que todos los componentes FASE 1 funcionan correctamente"""
        try:
            # Importaciones dinámicas
            from .context_builder import ContextBuilder
            from .prompt_enricher import PromptEnricher
            from .request_optimizer import RequestOptimizer
            
            # Probar inicialización de componentes
            context_builder = ContextBuilder(project_root=str(Path.cwd()))  # Proporcionar project_root como string
            prompt_enricher = PromptEnricher()
            request_optimizer = RequestOptimizer()
            
            # Verificar que tienen los métodos esperados
            components_status = {}
            
            # Test ContextBuilder
            if hasattr(context_builder, 'build_complete_context'):
                components_status['ContextBuilder'] = "✓ build_complete_context disponible"
            else:
                components_status['ContextBuilder'] = "❌ build_complete_context no encontrado"
            
            # Test PromptEnricher
            if hasattr(prompt_enricher, 'enrich_prompt'):
                components_status['PromptEnricher'] = "✓ enrich_prompt disponible"
            else:
                components_status['PromptEnricher'] = "❌ enrich_prompt no encontrado"
            
            # Test RequestOptimizer
            if hasattr(request_optimizer, 'optimize_request_strategy'):
                components_status['RequestOptimizer'] = "✓ optimize_request_strategy disponible"
            else:
                components_status['RequestOptimizer'] = "❌ optimize_request_strategy no encontrado"
            
            # Check if all methods are available
            all_methods_available = all("✓" in status for status in components_status.values())
            
            return DiagnosticResult(
                test_name="FASE 1 Components",
                status="PASS" if all_methods_available else "FAIL",
                message="Todos los componentes FASE 1 disponibles y funcionales" if all_methods_available else "Algunos métodos de FASE 1 no están disponibles",
                details={
                    "components_status": components_status,
                    "components_checked": [
                        "ContextBuilder",
                        "PromptEnricher", 
                        "RequestOptimizer"
                    ],
                    "methods_verified": [
                        "build_complete_context",
                        "enrich_prompt",
                        "optimize_request_strategy"
                    ]
                }
            )
            
        except ImportError as e:
            return DiagnosticResult(
                test_name="FASE 1 Components",
                status="FAIL",
                message=f"Error al importar componentes FASE 1: {str(e)}",
                details={"error_type": "ImportError", "error_details": str(e)}
            )
        except AssertionError as e:
            return DiagnosticResult(
                test_name="FASE 1 Components",
                status="FAIL",
                message=f"Error de verificación de métodos: {str(e)}",
                details={"error_type": "AssertionError", "error_details": str(e)}
            )
        except Exception as e:
            return DiagnosticResult(
                test_name="FASE 1 Components",
                status="FAIL",
                message=f"Error al verificar componentes FASE 1: {str(e)}",
                details={"error_type": type(e).__name__, "error_details": str(e)}
            )
    
    def _check_fase2_components(self) -> DiagnosticResult:
        """Verificar que todos los componentes FASE 2 funcionan correctamente"""
        try:
            # Importaciones dinámicas para evitar problemas circulares
            from .conversation_manager import ConversationManager
            from .response_processor import ResponseProcessor
            from .implementation_coordinator import ImplementationCoordinator
            from .anthropic_client import AnthropicClient
            
            # Probar inicialización de componentes FASE 2
            conversation_manager = ConversationManager()
            response_processor = ResponseProcessor()
            
            if self.api_key:
                client = AnthropicClient(api_key=self.api_key)
                coordinator = ImplementationCoordinator(api_key=self.api_key)  # Corregir parámetros
            else:
                coordinator = None
            
            # Verificar métodos principales
            assert hasattr(conversation_manager, 'create_session')
            assert hasattr(response_processor, 'process_response')
            
            components_status = {
                "ConversationManager": "✓ Funcional",
                "ResponseProcessor": "✓ Funcional", 
                "ImplementationCoordinator": "✓ Funcional" if coordinator else "⚠ Requiere API key"
            }
            
            return DiagnosticResult(
                test_name="FASE 2 Components",
                status="PASS",
                message="Componentes FASE 2 disponibles y funcionales",
                details={
                    "components_status": components_status,
                    "workflow_capability": "Disponible" if coordinator else "Limitado"
                }
            )
            
        except Exception as e:
            return DiagnosticResult(
                test_name="FASE 2 Components",
                status="FAIL",
                message=f"Error al verificar componentes FASE 2: {str(e)}"
            )
    
    def _check_performance_metrics(self) -> DiagnosticResult:
        """Verificar métricas de rendimiento del cliente API"""
        try:
            if not self.api_key:
                return DiagnosticResult(
                    test_name="Performance Metrics",
                    status="WARNING",
                    message="No se pueden obtener métricas sin API key"
                )
            
            # Importación dinámica
            from .anthropic_client import AnthropicClient
            
            client = AnthropicClient(api_key=self.api_key)
            metrics = client.get_performance_metrics()
            
            if 'message' in metrics:
                return DiagnosticResult(
                    test_name="Performance Metrics",
                    status="INFO",
                    message=metrics['message'],
                    details={"status": "No hay historial de requests recientes"}
                )
            
            return DiagnosticResult(
                test_name="Performance Metrics",
                status="PASS",
                message="Métricas de rendimiento disponibles",
                details=metrics
            )
            
        except Exception as e:
            return DiagnosticResult(
                test_name="Performance Metrics",
                status="FAIL",
                message=f"Error al obtener métricas: {str(e)}"
            )
    
    def _check_cost_tracking(self) -> DiagnosticResult:
        """Verificar el seguimiento de costos"""
        try:
            if not self.api_key:
                return DiagnosticResult(
                    test_name="Cost Tracking",
                    status="WARNING",
                    message="No se puede verificar seguimiento de costos sin API key"
                )
            
            # Importación dinámica
            from .anthropic_client import AnthropicClient
            
            client = AnthropicClient(api_key=self.api_key)
            
            # Verificar estructura del cost_tracker
            cost_tracker = client.cost_tracker
            required_fields = ['daily_cost', 'monthly_cost', 'last_reset']
            
            missing_fields = [field for field in required_fields if field not in cost_tracker]
            
            if missing_fields:
                return DiagnosticResult(
                    test_name="Cost Tracking",
                    status="FAIL",
                    message=f"Campos faltantes en cost_tracker: {missing_fields}"
                )
            
            return DiagnosticResult(
                test_name="Cost Tracking",
                status="PASS",
                message="Sistema de seguimiento de costos funcional",
                details={
                    "daily_cost": f"${cost_tracker['daily_cost']:.4f}",
                    "monthly_cost": f"${cost_tracker['monthly_cost']:.4f}",
                    "last_reset": cost_tracker['last_reset'].isoformat(),
                    "cost_limits": {
                        "daily_limit": "$50.00",
                        "monthly_limit": "$500.00"
                    }
                }
            )
            
        except Exception as e:
            return DiagnosticResult(
                test_name="Cost Tracking",
                status="FAIL",
                message=f"Error al verificar seguimiento de costos: {str(e)}"
            )
    
    def _check_cache_status(self) -> DiagnosticResult:
        """Verificar el estado del sistema de cache"""
        try:
            if not self.api_key:
                return DiagnosticResult(
                    test_name="Cache Status",
                    status="WARNING",
                    message="No se puede verificar cache sin API key"
                )
            
            # Importación dinámica
            from .anthropic_client import AnthropicClient
            
            client = AnthropicClient(api_key=self.api_key)
            cache_stats = client.get_cache_stats()
            
            return DiagnosticResult(
                test_name="Cache Status",
                status="PASS",
                message="Sistema de cache funcional",
                details=cache_stats
            )
            
        except Exception as e:
            return DiagnosticResult(
                test_name="Cache Status",
                status="FAIL",
                message=f"Error al verificar cache: {str(e)}"
            )
    
    def _test_basic_request(self) -> DiagnosticResult:
        """Realizar una prueba básica de request completo"""
        try:
            if not self.api_key:
                return DiagnosticResult(
                    test_name="Basic Request Test",
                    status="SKIP",
                    message="Prueba omitida: requiere API key"
                )
            
            # Importaciones dinámicas
            from .context_builder import ContextBuilder
            from .prompt_enricher import PromptEnricher
            from .anthropic_client import AnthropicClient
            
            # Simular un flujo completo FASE 1
            start_time = time.time()
            
            # 1. Construir contexto
            context_builder = ContextBuilder(project_root=str(Path.cwd()))
            context = context_builder.build_complete_context(target_files=None)
            
            # 2. Enriquecer prompt
            prompt_enricher = PromptEnricher()
            enriched_config = prompt_enricher.enrich_prompt(
                base_prompt="Esta es una prueba de diagnóstico. Responde únicamente 'DIAGNÓSTICO_OK'.",
                context=context,
                task_type="testing",
                complexity_level="simple"
            )
            
            # 3. Enviar request
            client = AnthropicClient(api_key=self.api_key)
            
            # Usar modelo más económico para pruebas
            enriched_config['model'] = 'claude-3-haiku-20240307'
            enriched_config['max_tokens'] = 20
            
            response = client.send_enriched_request(enriched_config, use_cache=False)
            
            end_time = time.time()
            
            # Verificar respuesta
            response_text = response.get('content', '').strip()
            success = 'DIAGNÓSTICO_OK' in response_text.upper()
            
            return DiagnosticResult(
                test_name="Basic Request Test",
                status="PASS" if success else "WARNING",
                message="Prueba de request completo exitosa" if success else "Request completado pero respuesta inesperada",
                details={
                    "total_time": round(end_time - start_time, 2),
                    "model_used": response.get('model'),
                    "tokens_used": response.get('usage', {}),
                    "response_text": response_text,
                    "expected_content": "DIAGNÓSTICO_OK",
                    "content_match": success
                }
            )
            
        except Exception as e:
            return DiagnosticResult(
                test_name="Basic Request Test",
                status="FAIL",
                message=f"Error en prueba de request: {str(e)}"
            )
    
    def _generate_health_report(self) -> APIHealthReport:
        """Generar reporte completo de salud basado en diagnósticos"""
        
        # Determinar estado general
        fail_count = sum(1 for d in self.diagnostics_results if d.status == "FAIL")
        warning_count = sum(1 for d in self.diagnostics_results if d.status == "WARNING")
        
        if fail_count > 0:
            overall_status = "CRÍTICO"
        elif warning_count > 2:
            overall_status = "ADVERTENCIA"
        else:
            overall_status = "SALUDABLE"
        
        # Extraer información específica
        api_key_status = next((d.status for d in self.diagnostics_results if d.test_name == "API Key Configuration"), "UNKNOWN")
        connection_status = next((d.status for d in self.diagnostics_results if d.test_name == "API Connectivity"), "UNKNOWN")
        
        # Métricas de rendimiento
        perf_result = next((d for d in self.diagnostics_results if d.test_name == "Performance Metrics"), None)
        performance_metrics = perf_result.details if perf_result and perf_result.details else {}
        
        # Análisis de costos
        cost_result = next((d for d in self.diagnostics_results if d.test_name == "Cost Tracking"), None)
        cost_analysis = cost_result.details if cost_result and cost_result.details else {}
        
        # Estado del cache
        cache_result = next((d for d in self.diagnostics_results if d.test_name == "Cache Status"), None)
        cache_status = cache_result.details if cache_result and cache_result.details else {}
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations()
        
        return APIHealthReport(
            overall_status=overall_status,
            api_key_status=api_key_status,
            connection_status=connection_status,
            performance_metrics=performance_metrics,
            cost_analysis=cost_analysis,
            cache_status=cache_status,
            diagnostics=self.diagnostics_results,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self) -> List[str]:
        """Generar recomendaciones basadas en los resultados de diagnóstico"""
        recommendations = []
        
        for diagnostic in self.diagnostics_results:
            if diagnostic.status == "FAIL":
                if diagnostic.test_name == "API Key Configuration":
                    recommendations.append("🔑 Configurar la variable de entorno ANTHROPIC_API_KEY con una clave válida")
                elif diagnostic.test_name == "API Connectivity":
                    recommendations.append("🌐 Verificar conexión a internet y validez de la API key")
                elif "Components" in diagnostic.test_name:
                    recommendations.append(f"🔧 Reinstalar o reparar componentes del sistema ({diagnostic.test_name})")
            
            elif diagnostic.status == "WARNING":
                if diagnostic.test_name == "API Key Configuration":
                    recommendations.append("⚠️ Verificar que la API key tenga el formato correcto (sk-ant-...)")
                elif diagnostic.test_name == "Performance Metrics":
                    recommendations.append("📊 No hay métricas de rendimiento disponibles - ejecutar algunas pruebas primero")
        
        # Recomendaciones generales
        if not any("API Key" in rec for rec in recommendations):
            recommendations.append("✅ Sistema API configurado correctamente")
        
        if len([d for d in self.diagnostics_results if d.status == "PASS"]) >= 6:
            recommendations.append("🚀 Sistema listo para uso en producción")
        
        return recommendations
    
    def _print_diagnostic_result(self, result: DiagnosticResult):
        """Imprimir resultado de diagnóstico con formato"""
        status_icons = {
            "PASS": "✅",
            "FAIL": "❌", 
            "WARNING": "⚠️",
            "INFO": "ℹ️",
            "SKIP": "⏭️"
        }
        
        icon = status_icons.get(result.status, "❓")
        click.echo(f"{icon} {result.test_name}: {result.message}")
        
        if result.details and result.status in ["PASS", "INFO"]:
            for key, value in result.details.items():
                if isinstance(value, dict):
                    click.echo(f"   📋 {key}:")
                    for sub_key, sub_value in value.items():
                        click.echo(f"      • {sub_key}: {sub_value}")
                else:
                    click.echo(f"   📋 {key}: {value}")
    
    def _print_final_report(self, report: APIHealthReport):
        """Imprimir reporte final con formato"""
        click.echo("\n" + "="*60)
        click.echo("📊 REPORTE FINAL DE SALUD DEL SISTEMA API")
        click.echo("="*60)
        
        # Estado general
        status_colors = {
            "SALUDABLE": "green",
            "ADVERTENCIA": "yellow", 
            "CRÍTICO": "red"
        }
        
        status_color = status_colors.get(report.overall_status, "white")
        click.echo(f"🏥 Estado General: ", nl=False)
        click.secho(report.overall_status, fg=status_color, bold=True)
        
        # Resumen de componentes
        click.echo(f"\n🔑 API Key: {report.api_key_status}")
        click.echo(f"🌐 Conectividad: {report.connection_status}")
        
        # Métricas de costos si están disponibles
        if report.cost_analysis:
            click.echo(f"\n💰 Análisis de Costos:")
            for key, value in report.cost_analysis.items():
                if key not in ['cost_limits']:
                    click.echo(f"   • {key}: {value}")
        
        # Recomendaciones
        if report.recommendations:
            click.echo(f"\n💡 Recomendaciones:")
            for rec in report.recommendations:
                click.echo(f"   {rec}")
        
        click.echo("\n" + "="*60)
    
    def save_report_to_file(self, report: APIHealthReport, filepath: Optional[str] = None) -> str:
        """
        Guardar reporte en archivo JSON
        
        Args:
            report: Reporte a guardar
            filepath: Ruta del archivo (opcional)
            
        Returns:
            Ruta del archivo guardado
        """
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"api_diagnostics_report_{timestamp}.json"
        
        # Convertir dataclasses a dict
        report_dict = asdict(report)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)
        
        return filepath


def run_quick_diagnosis(api_key: Optional[str] = None) -> bool:
    """
    Ejecutar un diagnóstico rápido del sistema
    
    Args:
        api_key: Clave API opcional
        
    Returns:
        True si el sistema está funcionando correctamente
    """
    diagnostics = APIDiagnostics(api_key=api_key)
    
    # Ejecutar solo las pruebas esenciales
    results = []
    
    # API Key
    results.append(diagnostics._check_api_key_configuration())
    
    # Componentes básicos
    results.append(diagnostics._check_fase1_components())
    results.append(diagnostics._check_fase2_components())
    
    # Conectividad (si hay API key)
    if api_key or os.getenv('ANTHROPIC_API_KEY'):
        results.append(diagnostics._check_api_connectivity())
    
    # Verificar si hay errores críticos
    critical_errors = [r for r in results if r.status == "FAIL"]
    
    return len(critical_errors) == 0


# CLI command para diagnósticos
def create_diagnostics_cli_command():
    """Crear comando CLI para diagnósticos"""
    
    @click.command()
    @click.option('--api-key', help='Clave API de Anthropic')
    @click.option('--save-report', help='Guardar reporte en archivo')
    @click.option('--quick', is_flag=True, help='Ejecutar diagnóstico rápido')
    def diagnose_api(api_key, save_report, quick):
        """🔍 Diagnosticar el estado del sistema API"""
        
        if quick:
            success = run_quick_diagnosis(api_key=api_key)
            if success:
                click.echo("✅ Diagnóstico rápido: Sistema funcionando correctamente")
            else:
                click.echo("❌ Diagnóstico rápido: Se encontraron problemas")
                click.echo("   Ejecuta 'diagnose-api' (sin --quick) para más detalles")
            return
        
        # Diagnóstico completo
        diagnostics = APIDiagnostics(api_key=api_key)
        report = diagnostics.run_complete_diagnosis(verbose=True)
        
        # Guardar reporte si se solicita
        if save_report:
            saved_path = diagnostics.save_report_to_file(report, save_report)
            click.echo(f"\n💾 Reporte guardado en: {saved_path}")
    
    return diagnose_api
