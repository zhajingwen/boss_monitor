import os

env = os.getenv('ENV')
if not env:
    env = "local"
lark_bot_id = os.getenv('LARKBOT_ID')
redis_password = os.getenv('REDIS_PASSWORD')
redis_host = os.getenv('REDIS_HOST')
if not redis_host:
    redis_host = "127.0.0.1"