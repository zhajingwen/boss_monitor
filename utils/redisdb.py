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
