import os

env = os.getenv('ENV')
lark_bot_id = os.getenv('LARKBOT_ID')
redis_password = os.getenv('REDIS_PASSWORD')
redis_host = os.getenv('REDIS_HOST')
print(f'redis_host: {redis_host}')