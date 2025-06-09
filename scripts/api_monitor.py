"""
API Monitoring Script - Sistema de Implementación Adaptativa
Script para monitorear el uso de la API en tiempo real
"""

import os
import time
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import click

from src.api_manager import AnthropicClient, APIDiagnostics


class APIMonitor:
    """
    Monitor en tiempo real del uso de la API
    """
    
    def __init__(self, api_key: Optional[str] = None, update_interval: int = 30):
        """
        Inicializar el monitor de API
        
        Args:
            api_key: Clave API opcional
            update_interval: Intervalo de actualización en segundos
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.update_interval = update_interval
        self.running = False
        self.client = None
        
        if self.api_key:
            self.client = AnthropicClient(api_key=self.api_key)
    
    def start_monitoring(self, duration_minutes: Optional[int] = None):
        """
        Iniciar monitoreo en tiempo real
        
        Args:
            duration_minutes: Duración del monitoreo en minutos (None = indefinido)
        """
        if not self.client:
            click.echo("❌ No se puede iniciar monitoreo sin API key válida")
            return
        
        self.running = True
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes) if duration_minutes else None
        
        click.echo(f"🚀 Iniciando monitoreo de API...")
        click.echo(f"⏱️  Intervalo de actualización: {self.update_interval} segundos")
        if end_time:
            click.echo(f"⏳ Duración: {duration_minutes} minutos")
        else:
            click.echo("⏳ Duración: Indefinida (Ctrl+C para detener)")
        
        click.echo("\n" + "="*80)
        
        try:
            while self.running:
                if end_time and datetime.now() > end_time:
                    break
                
                self._display_current_status()
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            click.echo("\n\n⛔ Monitoreo detenido por usuario")
        finally:
            self.running = False
            self._display_final_summary(start_time)
    
    def _display_current_status(self):
        """Mostrar estado actual del sistema"""
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # Obtener métricas actuales
        try:
            performance_metrics = self.client.get_performance_metrics()
            cache_stats = self.client.get_cache_stats()
            cost_tracker = self.client.cost_tracker
            
            # Limpiar pantalla (funciona en la mayoría de terminales)
            click.clear()
            
            # Header
            click.echo("🔍 MONITOR DE API - TIEMPO REAL")
            click.echo("="*80)
            click.echo(f"⏰ Última actualización: {current_time}")
            click.echo("")
            
            # Estado de conectividad
            click.echo("🌐 ESTADO DE CONECTIVIDAD")
            click.echo("-" * 40)
            click.secho("✅ Conectado a Anthropic API", fg="green")
            click.echo("")
            
            # Métricas de rendimiento
            click.echo("📊 MÉTRICAS DE RENDIMIENTO (24h)")
            click.echo("-" * 40)
            
            if isinstance(performance_metrics, dict) and 'message' not in performance_metrics:
                click.echo(f"📈 Total requests: {performance_metrics.get('total_requests', 0)}")
                click.echo(f"⚡ Cache hit rate: {performance_metrics.get('cache_hit_rate', 0):.2%}")
                click.echo(f"⏱️  Tiempo promedio: {performance_metrics.get('average_response_time', 0):.2f}s")
                click.echo(f"🔤 Tokens entrada: {performance_metrics.get('total_input_tokens', 0):,}")
                click.echo(f"🔤 Tokens salida: {performance_metrics.get('total_output_tokens', 0):,}")
            else:
                click.echo("ℹ️  No hay métricas disponibles (sin requests recientes)")
            click.echo("")
            
            # Análisis de costos
            click.echo("💰 ANÁLISIS DE COSTOS")
            click.echo("-" * 40)
            click.echo(f"📅 Costo diario: ${cost_tracker['daily_cost']:.4f}")
            click.echo(f"📆 Costo mensual: ${cost_tracker['monthly_cost']:.4f}")
            
            # Alertas de costo
            daily_limit = 50.0
            monthly_limit = 500.0
            daily_percentage = (cost_tracker['daily_cost'] / daily_limit) * 100
            monthly_percentage = (cost_tracker['monthly_cost'] / monthly_limit) * 100
            
            if daily_percentage > 80:
                click.secho(f"⚠️  ALERTA: {daily_percentage:.1f}% del límite diario usado", fg="red")
            elif daily_percentage > 60:
                click.secho(f"⚠️  ADVERTENCIA: {daily_percentage:.1f}% del límite diario usado", fg="yellow")
            else:
                click.secho(f"✅ {daily_percentage:.1f}% del límite diario usado", fg="green")
            
            if monthly_percentage > 80:
                click.secho(f"⚠️  ALERTA: {monthly_percentage:.1f}% del límite mensual usado", fg="red")
            elif monthly_percentage > 60:
                click.secho(f"⚠️  ADVERTENCIA: {monthly_percentage:.1f}% del límite mensual usado", fg="yellow")
            else:
                click.secho(f"✅ {monthly_percentage:.1f}% del límite mensual usado", fg="green")
            
            click.echo("")
            
            # Estado del cache
            click.echo("🗂️  ESTADO DEL CACHE")
            click.echo("-" * 40)
            
            if isinstance(cache_stats, dict) and 'message' not in cache_stats:
                click.echo(f"📦 Total entradas: {cache_stats.get('total_entries', 0)}")
                click.echo(f"✅ Entradas válidas: {cache_stats.get('valid_entries', 0)}")
                click.echo(f"❌ Entradas expiradas: {cache_stats.get('invalid_entries', 0)}")
                click.echo(f"🎯 Hit rate: {cache_stats.get('cache_hit_rate', 0):.2%}")
            else:
                click.echo("ℹ️  Cache vacío")
            
            click.echo("\n" + "="*80)
            click.echo(f"⏳ Próxima actualización en {self.update_interval} segundos...")
            click.echo("💡 Presiona Ctrl+C para detener el monitoreo")
            
        except Exception as e:
            click.echo(f"❌ Error al obtener métricas: {str(e)}")
    
    def _display_final_summary(self, start_time: datetime):
        """Mostrar resumen final del monitoreo"""
        end_time = datetime.now()
        duration = end_time - start_time
        
        click.echo("\n" + "="*80)
        click.echo("📋 RESUMEN FINAL DEL MONITOREO")
        click.echo("="*80)
        click.echo(f"⏰ Inicio: {start_time.strftime('%H:%M:%S')}")
        click.echo(f"⏰ Fin: {end_time.strftime('%H:%M:%S')}")
        click.echo(f"⏱️  Duración: {str(duration).split('.')[0]}")
        
        if self.client:
            try:
                final_metrics = self.client.get_performance_metrics()
                final_costs = self.client.cost_tracker
                
                click.echo(f"\n💰 Costos finales:")
                click.echo(f"   📅 Diario: ${final_costs['daily_cost']:.4f}")
                click.echo(f"   📆 Mensual: ${final_costs['monthly_cost']:.4f}")
                
                if isinstance(final_metrics, dict) and 'message' not in final_metrics:
                    click.echo(f"\n📊 Actividad registrada:")
                    click.echo(f"   📈 Total requests: {final_metrics.get('total_requests', 0)}")
                    click.echo(f"   🔤 Total tokens: {final_metrics.get('total_input_tokens', 0) + final_metrics.get('total_output_tokens', 0):,}")
                
            except Exception as e:
                click.echo(f"❌ Error al obtener métricas finales: {str(e)}")
        
        click.echo("\n✅ Monitoreo completado")
    
    def generate_monitoring_report(self, filepath: Optional[str] = None) -> str:
        """
        Generar reporte de monitoreo
        
        Args:
            filepath: Ruta del archivo (opcional)
            
        Returns:
            Ruta del archivo generado
        """
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"api_monitoring_report_{timestamp}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "api_status": "connected" if self.client else "disconnected",
            "performance_metrics": self.client.get_performance_metrics() if self.client else None,
            "cost_tracker": self.client.cost_tracker if self.client else None,
            "cache_stats": self.client.get_cache_stats() if self.client else None
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        return filepath


def monitor_api(api_key, interval, duration, save_report):
    """🔍 Monitorear el uso de la API en tiempo real"""
    
    monitor = APIMonitor(api_key=api_key, update_interval=interval)
    
    # Verificar que se puede conectar
    if not monitor.client:
        click.echo("❌ No se pudo inicializar el cliente API")
        click.echo("💡 Asegúrate de configurar ANTHROPIC_API_KEY o usar --api-key")
        return
    
    # Iniciar monitoreo
    monitor.start_monitoring(duration_minutes=duration)
    
    # Guardar reporte si se solicita
    if save_report:
        saved_path = monitor.generate_monitoring_report(save_report)
        click.echo(f"\n💾 Reporte de monitoreo guardado en: {saved_path}")


def run_performance_test(api_key: Optional[str] = None, num_requests: int = 5):
    """
    Ejecutar prueba de rendimiento de la API
    
    Args:
        api_key: Clave API opcional
        num_requests: Número de requests para la prueba
    """
    if not api_key:
        api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        click.echo("❌ Se requiere API key para prueba de rendimiento")
        return
    
    click.echo(f"🚀 Iniciando prueba de rendimiento con {num_requests} requests...")
    
    client = AnthropicClient(api_key=api_key)
    
    # Configuración de prueba
    test_config = {
        'prompt': 'Responde únicamente "TEST_OK" para esta prueba de rendimiento.',
        'system_prompt': 'Eres un asistente de prueba. Responde únicamente "TEST_OK".',
        'model': 'claude-3-haiku-20240307',  # Modelo más rápido y económico
        'max_tokens': 10,
        'temperature': 0.0
    }
    
    start_time = time.time()
    successful_requests = 0
    total_tokens = 0
    
    try:
        for i in range(num_requests):
            try:
                click.echo(f"📤 Request {i+1}/{num_requests}...", nl=False)
                
                response = client.send_enriched_request(test_config, use_cache=False)
                successful_requests += 1
                
                usage = response.get('usage', {})
                total_tokens += usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
                
                click.echo(" ✅")
                
            except Exception as e:
                click.echo(f" ❌ Error: {str(e)}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Mostrar resultados
        click.echo("\n" + "="*50)
        click.echo("📊 RESULTADOS DE PRUEBA DE RENDIMIENTO")
        click.echo("="*50)
        click.echo(f"✅ Requests exitosos: {successful_requests}/{num_requests}")
        click.echo(f"⏱️  Tiempo total: {total_time:.2f} segundos")
        click.echo(f"⚡ Tiempo promedio por request: {total_time/num_requests:.2f} segundos")
        click.echo(f"🔤 Total tokens utilizados: {total_tokens:,}")
        click.echo(f"💰 Costo estimado: ${(total_tokens/1000) * 0.00025:.6f}")  # Precio Haiku
        
        # Métricas del cliente
        final_metrics = client.get_performance_metrics()
        if isinstance(final_metrics, dict) and 'message' not in final_metrics:
            click.echo(f"🎯 Cache hit rate: {final_metrics.get('cache_hit_rate', 0):.2%}")
        
        success_rate = (successful_requests / num_requests) * 100
        if success_rate == 100:
            click.secho("🎉 Prueba completada con éxito!", fg="green")
        elif success_rate >= 80:
            click.secho(f"⚠️  Prueba completada con advertencias ({success_rate:.1f}% éxito)", fg="yellow")
        else:
            click.secho(f"❌ Prueba falló ({success_rate:.1f}% éxito)", fg="red")
        
    except KeyboardInterrupt:
        click.echo("\n⛔ Prueba interrumpida por usuario")


@click.group()
def cli():
    """🔍 Script de monitoreo de API"""
    pass


@cli.command()
@click.option('--api-key', help='Clave API de Anthropic')
@click.option('--duration', '-d', default=None, type=int, help='Duración del monitoreo en minutos')
@click.option('--interval', '-i', default=30, help='Intervalo de actualización en segundos')
@click.option('--save-report', help='Guardar reporte al finalizar')
def monitor(api_key, duration, interval, save_report):
    """📊 Monitoreo en tiempo real de la API"""
    monitor_api(api_key, interval, duration, save_report)


@cli.command()
@click.option('--api-key', help='Clave API de Anthropic')
@click.option('--requests', '-r', default=5, help='Número de requests para la prueba')
def test(api_key, requests):
    """🏃 Ejecutar prueba de rendimiento de la API"""
    run_performance_test(api_key=api_key, num_requests=requests)


if __name__ == "__main__":
    cli()
