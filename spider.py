# import asyncio
# import re
# from enum import Enum
# from typing import Optional
# # 用patchright替换playwright
# from patchright.async_api import async_playwright, Frame
# from patchright.async_api import Error as PlaywrightError
# from utils.redisdb import redis_cli
# # from config import env
import logging
# import json
# from datetime import datetime
# from retry import retry
from utils.lark_bot import sender
# from utils.scheduler import scheduled_task

from utils.browser import FuckCF


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Boss Anouncement')

class BossAlert(FuckCF):
    """
    币安上币公告告警到研究院的群里
    """
    spider_name = 'BinanceAlert To Research'
    author = 'drake.shi'
    
    def __init__(self):
        super().__init__()
        self.api = 'https://www.zhipin.com/web/geek/jobs?city={}&query=%E5%90%88%E7%BA%A6%E5%B7%A5%E7%A8%8B%E5%B8%88'
        self.lark_hook = 'https://open.larksuite.com/open-apis/bot/v2/hook/141f'
        self.codes = [100010000, 101010100, 101020100, 101280100, 101280600, 101210100, 101030100, 101110100, 101190400, 101200100, 101230200, 101250100, 101270100, 101180100, 101040100]
        for code in self.codes:
            url = self.api.format(code)
            self.target_urls.append(url)
            # logger.info(f'GET {url}')

    def parse(self, data):
        """
        解析职位数据并且告警
        """
        name_check_list = [
            '智能合约',
            'Solidity',
            '区块链合约'
        ]
        jobList = data['zpData']['jobList']
        for item in jobList:
            salaryDesc = item['salaryDesc']
            encryptJobId = item['encryptJobId']
            url = f'https://www.zhipin.com/job_detail/{encryptJobId}.html'
            jobName = item['jobName']
            # 判断名称是否符合标准
            name_ok = False
            for keyword in name_check_list:
                if keyword in jobName:
                    name_ok = True
            if not name_ok:
                logger.info(f'不匹配：{jobName}')
                continue
            if 'K' not in salaryDesc:
                logger.info(f'薪资太低：{salaryDesc} {jobName}')
            try:
                salaryDesc_up = salaryDesc.split('-')[-1].split('K')[0]
                salaryDesc_up_int = int(salaryDesc_up)
                if salaryDesc_up_int < 20:
                    logger.info(f'薪资太低：{salaryDesc} {jobName}')
                    continue
            except:
                logger.info(f'薪资解析异常：{salaryDesc} {jobName}')
                continue
            brandName = item['brandName']
            brandScaleName = item['brandScaleName']
            cityName = item['cityName']
            content = f"{salaryDesc}\n{jobName}\n{brandName}\n{brandScaleName}\n{cityName}\n{url}"
            alert_status = self.redis_cli.sismember(self.black_list_key, encryptJobId)
            if not alert_status:
                sender(content, self.lark_hook)
                self.redis_cli.sadd(self.black_list_key, encryptJobId)
                logger.info(content)
            else:
                logger.info(f'已告警，过滤：{content}')

    async def on_response(self, response):
        """
        监控数据流
        """
        if not response.ok:
            return
        if 'joblist.json' in response.url:
            try:
                oridata = await response.body()
                format_data = json.loads(oridata)
                print(format_data)
                self.parse(format_data)
            except:
                pass
