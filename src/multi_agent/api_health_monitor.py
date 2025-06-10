"""
FASE 3: Sistema de Monitoreo de Salud de APIs
Monitoreo en tiempo real de conectividad, latencia y disponibilidad de APIs de agentes.
"""

import asyncio
import aiohttp
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import logging

from .agent_specializations import AgentType
from .intelligent_scoring_engine import ApiHealthStatus


class HealthCheckStatus(Enum):
    """Estados de verificación de salud"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Resultado de una verificación de salud"""
    agent_type: AgentType
    status: HealthCheckStatus
    latency_ms: float
    response_code: Optional[int] = None
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    rate_limit_info: Optional[Dict[str, int]] = None
    quota_info: Optional[Dict[str, int]] = None


@dataclass
class ApiEndpointConfig:
    """Configuración de endpoint para monitoreo"""
    agent_type: AgentType
    health_check_url: str
    timeout_seconds: int = 5
    expected_response_codes: List[int] = field(default_factory=lambda: [200])
    headers: Optional[Dict[str, str]] = None
    auth_required: bool = False
    rate_limit_headers: List[str] = field(default_factory=lambda: ['x-ratelimit-remaining'])
    quota_headers: List[str] = field(default_factory=lambda: ['x-quota-remaining'])


class ApiHealthMonitor:
    """Monitor principal de salud de APIs"""
    
    def __init__(self):
        self.endpoints_config = self._initialize_endpoints()
        self.health_history: Dict[AgentType, List[HealthCheckResult]] = {}
        self.current_status: Dict[AgentType, ApiHealthStatus] = {}
        self.monitoring_active = False
        self.check_interval_seconds = 30
        self.history_retention_hours = 24
        self.logger = logging.getLogger(__name__)
    
    def _initialize_endpoints(self) -> Dict[AgentType, ApiEndpointConfig]:
        """Inicializa configuraciones de endpoints para cada tipo de agente"""
        return {
            AgentType.GEMINI: ApiEndpointConfig(
                agent_type=AgentType.GEMINI,
                health_check_url="https://generativelanguage.googleapis.com/v1/models",
                headers={"Authorization": "Bearer YOUR_API_KEY"}
            ),
            AgentType.CLAUDE: ApiEndpointConfig(
                agent_type=AgentType.CLAUDE,
                health_check_url="https://api.anthropic.com/v1/models",
                headers={"x-api-key": "YOUR_API_KEY"}
            ),
            AgentType.OPENAI: ApiEndpointConfig(
                agent_type=AgentType.OPENAI,
                health_check_url="https://api.openai.com/v1/models",
                headers={"Authorization": "Bearer YOUR_API_KEY"}
            )
        }
    
    async def check_single_endpoint(self, config: ApiEndpointConfig) -> HealthCheckResult:
        """Verifica la salud de un endpoint específico"""
        start_time = time.time()
        
        try:
            timeout = aiohttp.ClientTimeout(total=config.timeout_seconds)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    config.health_check_url, 
                    headers=config.headers or {}
                ) as response:
                    latency_ms = (time.time() - start_time) * 1000
                    
                    # Determinar estado basado en código de respuesta
                    status = HealthCheckStatus.HEALTHY
                    if response.status not in config.expected_response_codes:
                        if response.status >= 500:
                            status = HealthCheckStatus.UNAVAILABLE
                        elif response.status >= 400:
                            status = HealthCheckStatus.DEGRADED
                    
                    # Extraer información de rate limiting
                    rate_limit_info = {}
                    for header in config.rate_limit_headers:
                        if header in response.headers:
                            try:
                                rate_limit_info[header] = int(response.headers[header])
                            except (ValueError, TypeError):
                                pass
                    
                    # Extraer información de quota
                    quota_info = {}
                    for header in config.quota_headers:
                        if header in response.headers:
                            try:
                                quota_info[header] = int(response.headers[header])
                            except (ValueError, TypeError):
                                pass
                    
                    return HealthCheckResult(
                        agent_type=config.agent_type,
                        status=status,
                        latency_ms=latency_ms,
                        response_code=response.status,
                        rate_limit_info=rate_limit_info if rate_limit_info else None,
                        quota_info=quota_info if quota_info else None
                    )
        
        except asyncio.TimeoutError:
            latency_ms = config.timeout_seconds * 1000
            return HealthCheckResult(
                agent_type=config.agent_type,
                status=HealthCheckStatus.UNAVAILABLE,
                latency_ms=latency_ms,
                error_message="Timeout"
            )
        
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                agent_type=config.agent_type,
                status=HealthCheckStatus.UNAVAILABLE,
                latency_ms=latency_ms,
                error_message=str(e)
            )
    
    async def check_all_endpoints(self) -> Dict[AgentType, HealthCheckResult]:
        """Verifica la salud de todos los endpoints configurados"""
        tasks = []
        for config in self.endpoints_config.values():
            tasks.append(self.check_single_endpoint(config))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        health_results = {}
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                agent_type = list(self.endpoints_config.keys())[i]
                health_results[agent_type] = HealthCheckResult(
                    agent_type=agent_type,
                    status=HealthCheckStatus.UNKNOWN,
                    latency_ms=float('inf'),
                    error_message=str(result)
                )
            else:
                health_results[result.agent_type] = result
        
        return health_results
    
    def update_health_status(self, health_results: Dict[AgentType, HealthCheckResult]):
        """Actualiza el estado de salud basado en los resultados de verificación"""
        current_time = datetime.now()
        
        for agent_type, result in health_results.items():
            # Agregar a historial
            if agent_type not in self.health_history:
                self.health_history[agent_type] = []
            
            self.health_history[agent_type].append(result)
            
            # Mantener solo las últimas X horas de historial
            cutoff_time = current_time - timedelta(hours=self.history_retention_hours)
            self.health_history[agent_type] = [
                r for r in self.health_history[agent_type] 
                if r.timestamp >= cutoff_time
            ]
            
            # Calcular métricas agregadas
            recent_results = self.health_history[agent_type][-10:]  # Últimos 10 checks
            
            # Contar errores en la última hora
            one_hour_ago = current_time - timedelta(hours=1)
            recent_errors = sum(
                1 for r in self.health_history[agent_type]
                if r.timestamp >= one_hour_ago and r.status == HealthCheckStatus.UNAVAILABLE
            )
            
            # Calcular latencia promedio
            valid_latencies = [
                r.latency_ms for r in recent_results 
                if r.latency_ms != float('inf')
            ]
            avg_latency = sum(valid_latencies) / len(valid_latencies) if valid_latencies else float('inf')
            
            # Determinar disponibilidad
            is_available = result.status in [HealthCheckStatus.HEALTHY, HealthCheckStatus.DEGRADED]
            
            # Extraer información de rate limits y quotas
            rate_limit_remaining = 0
            quota_remaining = 0
            
            if result.rate_limit_info:
                rate_limit_remaining = max(result.rate_limit_info.values())
            
            if result.quota_info:
                quota_remaining = max(result.quota_info.values())
            
            # Actualizar estado actual
            self.current_status[agent_type] = ApiHealthStatus(
                agent_type=agent_type,
                is_available=is_available,
                latency_ms=avg_latency,
                rate_limit_remaining=rate_limit_remaining,
                quota_remaining=quota_remaining,
                error_count_last_hour=recent_errors,
                last_check=current_time
            )
    
    async def start_monitoring(self):
        """Inicia el monitoreo continuo de APIs"""
        self.monitoring_active = True
        self.logger.info("Iniciando monitoreo de APIs")
        
        while self.monitoring_active:
            try:
                health_results = await self.check_all_endpoints()
                self.update_health_status(health_results)
                
                # Log de estado general
                healthy_count = sum(
                    1 for status in self.current_status.values() 
                    if status.is_available
                )
                total_count = len(self.current_status)
                
                self.logger.info(
                    f"Health check completed: {healthy_count}/{total_count} APIs available"
                )
                
                # Esperar antes del siguiente ciclo
                await asyncio.sleep(self.check_interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Error en monitoreo de APIs: {e}")
                await asyncio.sleep(self.check_interval_seconds)
    
    def stop_monitoring(self):
        """Detiene el monitoreo continuo"""
        self.monitoring_active = False
        self.logger.info("Monitoreo de APIs detenido")
    
    def get_current_status(self, agent_type: AgentType) -> Optional[ApiHealthStatus]:
        """Obtiene el estado actual de salud de un agente específico"""
        return self.current_status.get(agent_type)
    
    def get_all_status(self) -> Dict[AgentType, ApiHealthStatus]:
        """Obtiene el estado actual de todos los agentes"""
        return self.current_status.copy()
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Genera un resumen del estado de salud del sistema"""
        if not self.current_status:
            return {"status": "no_data", "message": "No health data available"}
        
        total_agents = len(self.current_status)
        available_agents = sum(1 for status in self.current_status.values() if status.is_available)
        
        avg_latency = sum(
            status.latency_ms for status in self.current_status.values() 
            if status.latency_ms != float('inf')
        ) / max(1, len([s for s in self.current_status.values() if s.latency_ms != float('inf')]))
        
        total_errors = sum(status.error_count_last_hour for status in self.current_status.values())
        
        # Determinar estado general del sistema
        availability_ratio = available_agents / total_agents
        if availability_ratio >= 0.9:
            system_status = "healthy"
        elif availability_ratio >= 0.7:
            system_status = "degraded"
        else:
            system_status = "critical"
        
        return {
            "system_status": system_status,
            "availability_ratio": availability_ratio,
            "total_agents": total_agents,
            "available_agents": available_agents,
            "average_latency_ms": avg_latency,
            "total_errors_last_hour": total_errors,
            "last_update": max(
                status.last_check for status in self.current_status.values()
            ).isoformat() if self.current_status else None
        }
    
    def simulate_health_data(self):
        """Simula datos de salud para testing (sin conexiones reales)"""
        import random
        current_time = datetime.now()
        
        for agent_type in AgentType:
            # Simular estado basado en probabilidades
            is_available = random.random() > 0.1  # 90% de disponibilidad
            latency_ms = random.uniform(50, 300) if is_available else float('inf')
            error_count = random.randint(0, 2) if not is_available else 0
            
            self.current_status[agent_type] = ApiHealthStatus(
                agent_type=agent_type,
                is_available=is_available,
                latency_ms=latency_ms,
                rate_limit_remaining=random.randint(500, 1000),
                quota_remaining=random.randint(10000, 50000),
                error_count_last_hour=error_count,
                last_check=current_time
            )


# Instancia global del monitor
api_health_monitor = ApiHealthMonitor()
