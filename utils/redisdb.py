import redis
from utils.config import redis_password, redis_host
from typing import Optional


def redis_cli() -> redis.Redis:
    """
    创建并返回Redis客户端连接
    """
    print(f'redis_password: {redis_password}')
    
    # 创建连接池配置
    pool_kwargs = {
        'host': redis_host,
        'port': 6379,
        'db': 0,
    }
    
    # 只有当密码存在时才添加
    if redis_password:
        pool_kwargs['password'] = redis_password
    
    # 创建连接池
    pool = redis.ConnectionPool(**pool_kwargs)
    
    # 创建Redis客户端
    client = redis.Redis(connection_pool=pool)
    
    # 测试连接
    try:
        client.ping()
        print("Redis 连接成功")
    except redis.AuthenticationError:
        print("Redis 认证失败，请检查密码")
        raise
    except redis.ConnectionError:
        print("Redis 连接失败，请检查 Redis 是否运行")
        raise
    
    return client