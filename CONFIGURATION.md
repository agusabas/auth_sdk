# Configuration Guide

This document describes all environment variables used by the Django Microservices Auth SDK.

## Environment Variables

All configuration is done through environment variables. See `.env.example` for a complete list.

### Redis Configuration (Optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTH_SDK_REDIS_HOST` | `localhost` | Redis server hostname |
| `AUTH_SDK_REDIS_PORT` | `6379` | Redis server port |
| `AUTH_SDK_REDIS_DB` | `0` | Redis database number |
| `AUTH_SDK_REDIS_PASSWORD` | `None` | Redis password (optional) |
| `AUTH_SDK_REDIS_SSL` | `false` | Enable Redis SSL connection |

**Note:** If Redis is not available or not configured, the SDK will work without caching.

### Cache Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTH_SDK_CACHE_EXPIRATION` | `3600` | Cache expiration time in seconds |
| `AUTH_SDK_CACHE_PREFIX` | `auth_sdk` | Prefix for all cache keys |
| `AUTH_SDK_ENABLE_CACHING` | `true` | Enable/disable caching |

### Authentication Service Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTH_SDK_SERVICE_HOST` | `localhost:8000` | Authentication service host:port |
| `AUTH_SDK_SERVICE_SCHEME` | `http` | Protocol scheme (http/https) |
| `AUTH_SDK_SERVICE_ENDPOINT` | `/api/user/get_details/` | Authentication endpoint path |
| `AUTH_SDK_SERVICE_TIMEOUT` | `10` | HTTP request timeout in seconds |

### JWT Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTH_SDK_JWT_HEADER_PREFIX` | `JWT` | Authorization header prefix |

### Features Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTH_SDK_ENABLE_USER_DETAILS` | `true` | Enable AuthSDK.get_user_details() method |

### Logging Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTH_SDK_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

## Django Settings Integration

**IMPORTANT for Cache Compatibility**: If you use django-redis, ensure `DECODE_RESPONSES=False` in your Redis cache configuration:

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CHARSET': 'utf-8',
            'DECODE_RESPONSES': False,  # Required for auth_sdk compatibility
            'IGNORE_EXCEPTIONS': True,
        }
    }
}
```

Add this to your Django settings to configure logging:

```python
import os

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'auth_sdk': {
            'handlers': ['console'],
            'level': os.environ.get('AUTH_SDK_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}
```

## Production Considerations

1. **Redis**: Use a dedicated Redis instance for production
2. **HTTPS**: Always use HTTPS for the authentication service in production
3. **Timeouts**: Adjust `AUTH_SDK_SERVICE_TIMEOUT` based on your network latency
4. **Logging**: Set `AUTH_SDK_LOG_LEVEL=ERROR` in production to reduce log noise
5. **Security**: Use Redis password and SSL in production environments
6. **Cache Configuration**: Ensure `DECODE_RESPONSES=False` in Django Redis settings for proper cache compatibility

## Implementation Guide

For detailed implementation instructions for both authentication service and client microservices, see `IMPLEMENTATION_GUIDE.md`.

**Quick Start:**
1. **Authentication Service**: Implement `/api/user/get_details/` endpoint
2. **Client Microservice**: Install SDK, configure environment variables, add to Django settings
3. **Usage**: Use `@permission_classes([IsAuthenticated])` and other permission classes in views

**Key Integration Points:**
- Authentication service must return user data in the expected JSON format
- Client microservices configure the SDK via environment variables
- Frontend sends `Authorization: JWT <token>` headers
- Optional Redis caching improves performance