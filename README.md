# Auth SDK

Este SDK proporciona una solución de autenticación y manejo de permisos para microservicios Django, diseñado para facilitar la integración con un servicio de autenticación centralizado.

## Características principales

- Autenticación JWT personalizada
- Caché de información de usuario con Redis (con manejo automático de compatibilidad)
- Clases de permisos flexibles y reutilizables
- Modelos de usuario anónimo y autenticado
- Manejo robusto de errores y fallbacks automáticos

## Componentes clave

- `JWTAuthentication`: Clase para autenticar usuarios mediante tokens JWT
- `User` y `AnonymousUser`: Modelos para representar usuarios autenticados y anónimos
- `IsAuthenticated` y `HasPermission`: Clases de permisos para control de acceso granular

## Uso

Integre este SDK en sus microservicios Django para manejar la autenticación y los permisos de manera consistente. Utilice las clases proporcionadas en sus vistas para controlar el acceso y obtener información del usuario autenticado.

## Configuración

Asegúrese de configurar las variables de entorno necesarias (ver `CONFIGURATION.md` y `.env.example`) y tener una instancia de Redis accesible para el caché de usuarios.

**Importante**: Si usa django-redis, configure `DECODE_RESPONSES=False` en sus settings de Django para compatibilidad con el cache del auth_sdk.

## Documentación

- `CONFIGURATION.md`: Guía completa de configuración
- `IMPLEMENTATION_GUIDE.md`: Guía de implementación paso a paso
- `.env.example`: Ejemplo de variables de entorno
