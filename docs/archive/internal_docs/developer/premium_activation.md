# Sistema de Activación Premium para Desarrolladores

Este documento describe cómo se implementa el sistema de activación premium para desarrolladores en ProjectPrompt, cómo funciona el sistema de verificación de licencias y cómo se gestionan las credenciales de desarrollador.

## Resumen

El Sistema de Activación Premium para Desarrolladores permite a los desarrolladores de ProjectPrompt activar todas las funciones premium sin necesidad de una licencia comercial o API keys externas. Este sistema es útil durante el desarrollo y pruebas, pero no está destinado a usuarios finales.

## Componentes

El sistema está compuesto por los siguientes componentes:

1. **Generador de Credenciales de Desarrollador**: Script que genera una licencia válida para desarrolladores.
2. **Validador de Licencias**: Módulo que verifica si una licencia es válida y determina el nivel de acceso.
3. **Gestor de Suscripciones**: Módulo que gestiona el estado de la suscripción y las restricciones asociadas.
4. **Validador de APIs**: Módulo para configurar y validar claves de API externas.

## Flujo de Activación

El proceso de activación premium para desarrolladores sigue estos pasos:

1. El desarrollador ejecuta `generate_developer_credentials.py` con sus datos.
2. El script genera una clave de licencia válida con formato `PP-TYPE-EXPIRATION-HASH`.
3. La clave se almacena en dos ubicaciones:
   - `~/.config/project-prompt/developer_credentials.json` (datos completos)
   - `~/.config/project-prompt/config.yaml` (solo la clave)
4. Opcionalmente, se configura también una API key de Anthropic.
5. El sistema de verificación freemium reconoce la licencia como válida.
6. Las funciones premium quedan disponibles para el desarrollador.

## Formato de Licencias

Las licencias tienen el formato: `PP-TYPE-EXPIRATION-HASH`

Donde:
- `PP` es un prefijo constante.
- `TYPE` es el tipo de suscripción: BASIC, PRO o TEAM.
- `EXPIRATION` es la fecha de expiración en formato YYYYMMDD.
- `HASH` es un hash HMAC-SHA256 truncado para verificar la integridad.

Ejemplo: `PP-PRO-20260519-6232c01df728fdc`

## Verificación de Licencias

El sistema puede verificar licencias de dos maneras:

1. **Verificación online**: Se consulta a un servidor remoto para validar la licencia (no implementado para licencias de desarrollo).
2. **Verificación offline**: Se verifica localmente usando el hash de integridad y la fecha de expiración.

Para licencias de desarrollador, siempre se usa verificación offline.

## Almacenamiento de Credenciales

Las credenciales de desarrollador se almacenan en dos ubicaciones:

1. **Archivo de credenciales**: `~/.config/project-prompt/developer_credentials.json`
   ```json
   {
     "name": "Nombre Desarrollador",
     "email": "dev@example.com",
     "subscription_type": "pro",
     "license_key": "PP-PRO-20260519-1234567890abcdef",
     "expiration_date": "2026-05-19",
     "generated_at": "2025-05-19 10:43:49",
     "is_developer": true
   }
   ```

2. **Archivo de configuración**: `~/.config/project-prompt/config.yaml`
   ```yaml
   subscription:
     license_key: PP-PRO-20260519-1234567890abcdef
   apis:
     anthropic:
       api_key: tu_clave_api_aqui
   ```

## Futuras Mejoras

En el futuro, este sistema evolucionará para:

1. Almacenar credenciales de usuario en una base de datos remota.
2. Relacionar licencias con cuentas de usuario (email/contraseña).
3. Implementar un sistema de renovación automática.
4. Mejorar la seguridad mediante encriptación de claves y validación remota.

## Pruebas y Verificación

Para verificar el sistema, se pueden usar estos comandos:

```bash
# Verificar credenciales de desarrollador
python generate_developer_credentials.py --verify-only

# Verificar estado del sistema freemium
python verify_freemium_system.py

# Verificar capacidades premium
python verify_dev_credentials.py
```

## Preguntas Frecuentes

### ¿Las licencias de desarrollador son permanentes?
No, tienen una fecha de expiración configurable, por defecto 365 días.

### ¿Puedo compartir mi licencia de desarrollador?
No, estas licencias son solo para uso durante el desarrollo y no deben compartirse.

### ¿Necesito una API key externa para usar todas las funciones?
Para algunas funciones avanzadas que requieren modelos de IA externos, se necesitará una API key válida de Anthropic o OpenAI.

### ¿Qué pasa cuando expira mi licencia de desarrollador?
Puedes generar una nueva ejecutando nuevamente `generate_developer_credentials.py --force`.
