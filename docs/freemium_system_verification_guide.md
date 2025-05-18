# Guía de Verificación del Sistema Freemium

Este documento proporciona instrucciones detalladas sobre cómo verificar la implementación del Sistema de Verificación Freemium para ProjectPrompt.

## Scripts de Verificación

Se han desarrollado varios scripts para facilitar la verificación del sistema freemium:

1. `run_freemium_tests.sh` - Script principal que ejecuta todas las verificaciones
2. `test_freemium_system.py` - Script para probar componentes individuales del sistema
3. `verify_freemium_system.py` - Script para verificar la implementación completa
4. `test_anthropic_integration.py` - Script para probar específicamente la integración con Anthropic

## Opciones de Verificación

### Ejecución Completa

Para realizar una verificación completa del sistema:

```bash
./run_freemium_tests.sh
```

### Modo Simulación

Si desea realizar una verificación sin depender de servicios externos o configuraciones:

```bash
./run_freemium_tests.sh --simulate
```

### Verificación de Componentes Individuales

Para verificar componentes específicos:

```bash
# Verificar sistema de licencias
python test_freemium_system.py --test license

# Verificar sistema de suscripciones
python test_freemium_system.py --test subscription

# Verificar integración con Anthropic
python test_freemium_system.py --test anthropic

# Verificar todos los componentes
python test_freemium_system.py --test all
```

### Opciones de Simulación para Componentes Individuales

Es posible simular componentes específicos:

```bash
# Simular licencia
python test_freemium_system.py --test license --simulate-license

# Simular suscripción premium
python test_freemium_system.py --test subscription --simulate-premium

# Simular API de Anthropic
python test_freemium_system.py --test anthropic --simulate-api

# Realizar configuración previa
python test_freemium_system.py --test all --setup

# No requerir API configurada
python test_freemium_system.py --test anthropic --no-api-required
```

## Verificación Detallada del Sistema

Para una verificación detallada de todo el sistema:

```bash
python verify_freemium_system.py
```

Con opciones de simulación:

```bash
# Simular todos los componentes
python verify_freemium_system.py --simulate

# Simular componentes individuales
python verify_freemium_system.py --simulate-license --simulate-api
```

## Configuración de API de Anthropic

Para configurar la API de Anthropic:

```bash
python set_anthropic_key.py --key TU_CLAVE_API
```

## Interpretación de Resultados

Los scripts proporcionan resultados con los siguientes indicadores:

- ✅ Éxito - El componente está implementado correctamente
- ⚠️ Advertencia - El componente está parcialmente implementado
- ❌ Error - El componente no está implementado o tiene problemas
- ⏭️ Omitido - El componente no pudo ser verificado

## Solución de Problemas

Si encuentra errores durante la verificación:

1. Asegúrese de que todas las dependencias estén instaladas
2. Verifique que la estructura del proyecto sea correcta
3. Compruebe que los archivos de configuración existan
4. Pruebe con el modo de simulación para aislar el problema

Para más detalles sobre la implementación, consulte el archivo `freemium_implementation_report.md`.
