import redis
import os
from typing import Optional


def redis_cli(
    password: Optional[str] = None,
    decode_responses: bool = True,
    socket_timeout: Optional[int] = None,
    socket_connect_timeout: Optional[int] = None,
    max_connections: int = 50,
    retry_on_timeout: bool = True,
    **kwargs
) -> redis.Redis:
    """
    创建并返回Redis客户端连接
    
    Args:
        password: 密码，如果不提供则从环境变量REDIS_PASSWORD获取
        decode_responses: 是否自动解码响应，默认为True
        socket_timeout: 套接字超时时间（秒）
        socket_connect_timeout: 连接超时时间（秒）
        max_connections: 连接池最大连接数，默认为50
        retry_on_timeout: 超时时是否重试，默认为True
        **kwargs: 其他Redis连接参数
        
    Returns:
        redis.Redis: Redis客户端实例
        
    Raises:
        redis.ConnectionError: 连接失败时抛出
        redis.RedisError: 其他Redis相关错误
        
    Environment Variables:
        REDIS_PASSWORD: Redis密码，当password参数为None时使用
    """
    try:
        # 如果没有提供密码，尝试从环境变量获取
        if password is None:
            password = os.getenv('REDIS_PASSWORD')
        
        # 创建连接池
        pool = redis.ConnectionPool(
            host="127.0.0.1",  # 硬编码主机为127.0.0.1
            port=6379,  # 硬编码端口为6379
            db=0,  # 硬编码数据库为默认数据库0
            password=password,
            decode_responses=decode_responses,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
            max_connections=max_connections,
            retry_on_timeout=retry_on_timeout,
            **kwargs
        )
        
        # 创建Redis客户端
        client = redis.Redis(connection_pool=pool)
        
        # 测试连接
        client.ping()
        
        return client
        
    except redis.ConnectionError as e:
        raise redis.ConnectionError(f"无法连接到Redis服务器 127.0.0.1:6379 - {str(e)}")
    except redis.RedisError as e:
        raise redis.RedisError(f"Redis操作错误 - {str(e)}")
    except Exception as e:
        raise Exception(f"创建Redis客户端时发生未知错误 - {str(e)}")


def get_redis_connection(
    password: Optional[str] = None,
    **kwargs
) -> redis.Redis:
    """
    简化的Redis连接方法，使用默认配置
    密码会优先从环境变量REDIS_PASSWORD获取
    主机固定为127.0.0.1，端口固定为6379，数据库固定为0
    
    Args:
        password: 密码，如果不提供则从环境变量REDIS_PASSWORD获取
        **kwargs: 其他连接参数
        
    Returns:
        redis.Redis: Redis客户端实例
    """
    return redis_cli(password=password, **kwargs)


# 示例用法
if __name__ == "__main__":
    try:
        # 使用默认配置连接
        client = redis_cli()
        print("Redis连接成功!")
        
        # 测试基本操作
        client.set("test_key", "test_value")
        value = client.get("test_key")
        print(f"设置和获取测试: {value}")
        
        # 删除测试键
        client.delete("test_key")
        print("测试完成，已清理测试数据")
        
    except Exception as e:
        print(f"Redis连接失败: {e}")
