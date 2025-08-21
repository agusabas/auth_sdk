"""
Configuration module for auth_sdk.
Handles all environment variables and default settings.
"""
import os


class AuthConfig:
    """Configuration class for authentication settings."""
    
    # Redis Configuration
    REDIS_HOST = os.environ.get('AUTH_SDK_REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('AUTH_SDK_REDIS_PORT', 6379))
    REDIS_DB = int(os.environ.get('AUTH_SDK_REDIS_DB', 0))
    REDIS_PASSWORD = os.environ.get('AUTH_SDK_REDIS_PASSWORD')
    REDIS_SSL = os.environ.get('AUTH_SDK_REDIS_SSL', 'false').lower() == 'true'
    
    # Cache Configuration
    CACHE_EXPIRATION = int(os.environ.get('AUTH_SDK_CACHE_EXPIRATION', 3600))  # 1 hour
    CACHE_PREFIX = os.environ.get('AUTH_SDK_CACHE_PREFIX', 'auth_sdk')
    
    # Authentication Service Configuration
    SERVICE_HOST = os.environ.get('AUTH_SDK_SERVICE_HOST', 'localhost:8000')
    SERVICE_SCHEME = os.environ.get('AUTH_SDK_SERVICE_SCHEME', 'http')
    SERVICE_ENDPOINT = os.environ.get('AUTH_SDK_SERVICE_ENDPOINT', '/api/user/get_details/')
    SERVICE_TIMEOUT = int(os.environ.get('AUTH_SDK_SERVICE_TIMEOUT', 10))
    
    # JWT Configuration
    JWT_HEADER_PREFIX = os.environ.get('AUTH_SDK_JWT_HEADER_PREFIX', 'JWT')
    
    # Features Configuration
    ENABLE_CACHING = os.environ.get('AUTH_SDK_ENABLE_CACHING', 'true').lower() == 'true'
    ENABLE_USER_DETAILS_ENDPOINT = os.environ.get('AUTH_SDK_ENABLE_USER_DETAILS', 'true').lower() == 'true'
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('AUTH_SDK_LOG_LEVEL', 'INFO')
    
    @classmethod
    def get_auth_service_url(cls):
        """Get the complete authentication service URL."""
        return f"{cls.SERVICE_SCHEME}://{cls.SERVICE_HOST}{cls.SERVICE_ENDPOINT}"
    
    @classmethod
    def get_redis_config(cls):
        """Get Redis connection configuration."""
        config = {
            'host': cls.REDIS_HOST,
            'port': cls.REDIS_PORT,
            'db': cls.REDIS_DB,
            'decode_responses': False,  # Fixed: auth_sdk handles decode manually
            'socket_connect_timeout': 5,
            'socket_timeout': 5,
        }
        
        if cls.REDIS_PASSWORD:
            config['password'] = cls.REDIS_PASSWORD
            
        if cls.REDIS_SSL:
            config['ssl'] = True
            config['ssl_cert_reqs'] = None
            
        return config