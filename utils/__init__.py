"""
Utils package for boss-monitor project
"""

from .redisdb import redis_cli, get_redis_connection

__all__ = ['redis_cli', 'get_redis_connection']
