from flask_caching import Cache

# Initialize cache instance
cache = Cache()


# # Setup cache configuration (use Redis as backend)
# cache = Cache(app, config={'CACHE_TYPE': 'RedisCache','Cache_REDIS_HOST':'localhost','Cache_REDIS_PORT':6379,'Cache_REDIS_DB':0})