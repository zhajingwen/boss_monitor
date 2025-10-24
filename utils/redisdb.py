import redis
from utils.config import redis_password, redis_host
from typing import Optional


def redis_cli() -> redis.Redis:
    """
    创建并返回Redis客户端连接
    Returns:
        redis.Redis: Redis客户端实例
        
    Raises:
        redis.ConnectionError: 连接失败时抛出
        redis.RedisError: 其他Redis相关错误
        
    Environment Variables:
        REDIS_PASSWORD: Redis密码，当password参数为None时使用
    """
    try:
        # 创建连接池
        pool = redis.ConnectionPool(
            host=redis_host,
            port=6379,  # 硬编码端口为6379
            db=0,  # 硬编码数据库为默认数据库0
            password=redis_password,
        )
        
        # 创建Redis客户端
        client = redis.Redis(connection_pool=pool)
        
        # 测试连接
        client.ping()
        
        return client
        
    except redis.ConnectionError as e:
        raise redis.ConnectionError(f"无法连接到Redis服务器{str(e)}")
    except redis.RedisError as e:
        raise redis.RedisError(f"Redis操作错误 - {str(e)}")
    except Exception as e:
        raise Exception(f"创建Redis客户端时发生未知错误 - {str(e)}")

