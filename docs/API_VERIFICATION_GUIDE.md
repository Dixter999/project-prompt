# Guía de Verificación de API - Sistema de Implementación Adaptativa

Esta guía te ayudará a verificar que el sistema API está funcionando correctamente y aprovechar al máximo sus capacidades.

## 🔍 Comandos de Diagnóstico

### 1. Diagnóstico Rápido
```bash
# Verificación rápida del sistema (sin consumir API)
projectprompt diagnose-api --quick
```

### 2. Diagnóstico Completo
```bash
# Diagnóstico completo con pruebas de conectividad
projectprompt diagnose-api

# Con API key específica
projectprompt diagnose-api --api-key sk-ant-your-key-here

# Guardar reporte
projectprompt diagnose-api --save-report reporte_api.json
```

### 3. Monitoreo en Tiempo Real
```bash
# Monitoreo continuo (Ctrl+C para detener)
python scripts/api_monitor.py monitor

# Monitoreo por tiempo limitado
python scripts/api_monitor.py monitor --duration 10  # 10 minutos

# Con intervalo personalizado
python scripts/api_monitor.py monitor --interval 15  # cada 15 segundos
```

### 4. Pruebas de Rendimiento
```bash
# Prueba básica de rendimiento
python scripts/api_monitor.py test

# Prueba con más requests
python scripts/api_monitor.py test --requests 10
```

## ✅ Verificaciones que se Realizan

### 🔑 Configuración de API Key
- ✅ Existencia de la variable `ANTHROPIC_API_KEY`
- ✅ Formato correcto de la API key
- ✅ Validez de la clave (prueba de conectividad)

### 🧩 Componentes del Sistema
- ✅ **FASE 1**: ContextBuilder, PromptEnricher, AnthropicClient, RequestOptimizer
- ✅ **FASE 2**: ConversationManager, ResponseProcessor, ImplementationCoordinator
- ✅ Importación correcta de todos los módulos
- ✅ Inicialización sin errores

### 🌐 Conectividad API
- ✅ Conexión exitosa a Anthropic API
- ✅ Respuesta correcta del modelo
- ✅ Medición de tiempo de respuesta
- ✅ Verificación de uso de tokens

### 📊 Métricas de Rendimiento
- ✅ Historial de requests (últimas 24 horas)
- ✅ Tasa de cache hit
- ✅ Tiempo promedio de respuesta
- ✅ Tokens de entrada y salida
- ✅ Análisis de rendimiento

### 💰 Seguimiento de Costos
- ✅ Costo diario acumulado
- ✅ Costo mensual acumulado
- ✅ Verificación de límites configurados
- ✅ Alertas de gasto excesivo

### 🗂️ Estado del Cache
- ✅ Entradas totales en cache
- ✅ Entradas válidas vs expiradas
- ✅ Tasa de efectividad del cache
- ✅ Limpieza automática

## 📋 Interpretando los Resultados

### Estados de Diagnóstico
- **✅ PASS**: Funcionando correctamente
- **⚠️ WARNING**: Funcionando con advertencias menores
- **❌ FAIL**: Error que requiere atención
- **ℹ️ INFO**: Información adicional
- **⏭️ SKIP**: Prueba omitida (p.ej., sin API key)

### Estado General del Sistema
- **🏥 SALUDABLE**: Todos los componentes funcionando correctamente
- **🏥 ADVERTENCIA**: Algunos problemas menores detectados
- **🏥 CRÍTICO**: Errores que impiden el funcionamiento normal

## 🛠️ Solución de Problemas Comunes

### ❌ "No se encontró ANTHROPIC_API_KEY"
```bash
# Configurar variable de entorno
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# O crear archivo .env en la raíz del proyecto
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" > .env
```

### ❌ "Error de conectividad"
1. Verificar conexión a internet
2. Comprobar validez de la API key
3. Verificar que no hay firewall bloqueando la conexión
4. Intentar con una API key diferente

### ❌ "Error al importar componentes"
```bash
# Reinstalar dependencias
pip install -r requirements.txt

# Verificar instalación
pip list | grep anthropic
```

### ⚠️ "Límite de costo excedido"
- Verificar configuración en `config/api_monitoring.yaml`
- Ajustar límites diarios/mensuales según necesidades
- Usar modelos más económicos (claude-3-haiku)

### ⚠️ "Cache con baja efectividad"
- Normal si es la primera ejecución
- Se mejora con el uso continuo
- Verificar configuración de cache en el código

## 📊 Monitoreo Avanzado

### Personalizar Límites de Costo
Editar `config/api_monitoring.yaml`:
```yaml
cost_limits:
  daily_limit: 100.0     # Aumentar límite diario a $100
  monthly_limit: 1000.0  # Aumentar límite mensual a $1000
  warning_threshold: 0.7 # Advertir al 70%
```

### Configurar Alertas
```yaml
alerts:
  console_warnings: true      # Mostrar en consola
  email_notifications: false  # Configurar email si es necesario
```

### Optimización de Rendimiento
```yaml
optimization:
  enable_smart_caching: true      # Mejorar cache
  enable_cost_optimization: true  # Optimizar costos
  enable_request_combining: true  # Combinar requests similares
```

## 📈 Métricas Importantes a Monitorear

### 🎯 Eficiencia
- **Cache Hit Rate**: > 20% es bueno, > 50% es excelente
- **Tiempo de Respuesta**: < 5 segundos es bueno
- **Éxito de Requests**: 100% ideal, > 95% aceptable

### 💰 Costos
- **Costo por Request**: Depende del modelo usado
- **Tendencia Diaria**: Monitorear incrementos inesperados
- **Eficiencia de Tokens**: Optimizar prompts para reducir tokens

### 🚀 Rendimiento
- **Requests por Minuto**: Capacidad del sistema
- **Latencia Promedio**: Experiencia del usuario
- **Errores por Hora**: Estabilidad del sistema

## 🔧 Configuración Avanzada

### Variables de Entorno Adicionales
```bash
# Configuración opcional
export API_MONITOR_INTERVAL=30        # Intervalo de monitoreo
export API_CACHE_DURATION=3600        # Duración del cache
export API_MAX_DAILY_COST=50          # Límite diario personalizado
export API_PERFORMANCE_WINDOW=24      # Ventana de métricas (horas)
```

### Archivos de Configuración
- `config/api_monitoring.yaml`: Configuración de monitoreo
- `config/api_strategies.yaml`: Estrategias de optimización
- `config/prompt_templates.yaml`: Templates de prompts

## 🆘 Obtener Ayuda

### Diagnóstico Paso a Paso
1. **Ejecutar diagnóstico rápido**: `projectprompt diagnose-api --quick`
2. **Si hay errores, ejecutar completo**: `projectprompt diagnose-api`
3. **Revisar configuración**: Verificar archivos en `config/`
4. **Probar rendimiento**: `python scripts/api_monitor.py test`
5. **Monitorear en tiempo real**: `python scripts/api_monitor.py monitor`

### Información de Debug
```bash
# Ejecutar con información detallada
python -c "
from src.api_manager import APIDiagnostics
diag = APIDiagnostics()
report = diag.run_complete_diagnosis(verbose=True)
print('\\nReporte completo:', report.overall_status)
"
```

### Logs del Sistema
Los logs se almacenan en:
- Diagnósticos: `api_diagnostics_report_*.json`
- Monitoreo: `api_monitoring_report_*.json`
- Errores: Mostrados en consola y disponibles en el output del CLI

---

## 🎯 Checklist de Verificación

- [ ] ✅ API key configurada y válida
- [ ] ✅ Todos los componentes importan correctamente
- [ ] ✅ Conectividad con Anthropic API funcional
- [ ] ✅ Cache operativo y efectivo
- [ ] ✅ Seguimiento de costos activo
- [ ] ✅ Métricas de rendimiento disponibles
- [ ] ✅ Límites de costo configurados apropiadamente
- [ ] ✅ Pruebas de rendimiento exitosas
- [ ] ✅ Monitoreo en tiempo real funcional

**¡Sistema listo para uso en producción!** 🚀
