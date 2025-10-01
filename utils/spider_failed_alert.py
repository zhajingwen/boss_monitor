import traceback
import os
from utils.lark_bot import sender
# from config import env

def ErrorMonitor(spider_name, user=None):
    """
    捕获异常并且发送消息的装饰器,用于加在各个爬虫的解析方法上
    :param spider_name:爬虫名
    :param user: 用户名
    24个小时内单个爬虫的故障只告警一次
    """
    webhook = 'https://open.larksuite.com/open-apis/bot/v2/hook/'
    title = f'{spider_name}\n  @{user}'
    key_base = 'process:failed:filter:{}'
        
    # 捕获异常
    def catch_exception(func):
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            # 捕获异常，发送告警
            except Exception as e:
                from utils.redisdb import redis_cli
                redis_c = redis_cli()   
                err_info = traceback.format_exc()
                print(err_info)
                key = key_base.format(spider_name)
                filter_status = redis_c.get(key)
                if filter_status:
                    print('过滤该告警')
                    return
                # 只有线上环境才告警
                # if env == 'prod':
                sender(err_info, url=webhook, title=title)
                # 24个小时内单个爬虫的故障只告警一次
                redis_c.setex(key, 24*60*60, 1)
                raise e
        return inner
    return catch_exception
