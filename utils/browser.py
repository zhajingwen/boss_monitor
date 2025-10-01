import asyncio
import re
import os
import logging
from enum import Enum
from retry import retry
from functools import partial
from datetime import datetime
from typing import Optional
from traceback import format_exc
from patchright.async_api import async_playwright, Frame
from patchright.async_api import Error as PlaywrightError
from utils.redisdb import redis_cli
from utils.scheduler import scheduled_task
from utils.spider_failed_alert import ErrorMonitor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Fuck CF')
# env = 'local'
env = os.getenv('ENV')

"""
基于https://github.com/Xewdy444/CF-Clearance-Scraper改造
"""

class ChallengePlatform(Enum):
    """Cloudflare 挑战平台类型。"""

    JAVASCRIPT = "non-interactive"
    MANAGED = "managed"
    INTERACTIVE = "interactive"

class FuckCF:
    """
    浏览器公共基类模块，涉及到浏览器的爬虫都导入这个基类来实现
    核心能力：绕过各种反扒 + 提高鲁棒性 + 确保一定能够拿到数据
    """
    spider_name = 'Fuck CF Base Class'
    author = 'drake shi'
    def __init__(self):
        self.redis_cli = redis_cli()
        self.proxy=None
        self._timeout = 30
        # 数据是否采集成功
        self.task_finished_status = True
        self.retry_times = 3
        # 目标要采集的地址清单
        self.target_urls = []

    def _get_turnstile_frame(self, page) -> Optional[Frame]:
        """
        获取 Cloudflare turnstile 框架。
        Returns： Cloudflare turnstile 框架对象，如果找不到则返回 None。
        -------
        Optional[Frame]
            Cloudflare turnstile 框架。
        """
        frame = page.frame(
            url=re.compile(
                "https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/[bg]/turnstile"
            ),
        )
        return frame

    async def cookies(self, page) -> Optional[str]:
        """获取当前页面的cookies。"""
        cookies = await page.context.cookies()
        if not cookies:
            return None
        for cookie in cookies:
            if cookie["name"] == "cf_clearance":
                return cookie["value"]
        return None

    async def detect_challenge(self, page) -> Optional[str]:
        """
        检测当前页面的 Cloudflare 挑战平台类型。

        Returns：返回检测到的 Cloudflare 挑战平台类型，如果未检测到挑战则返回 None。
        -------
        Optional[ChallengePlatform]
            Cloudflare 挑战平台类型。
        """
        html = await page.content()
        for platform in ChallengePlatform:
            if f"cType: '{platform.value}'" in html:
                return platform.value
        return None

    async def solve_challenge(self, page) -> None:
        """解决当前页面的 Cloudflare 挑战。"""
        verify_button_pattern = re.compile(
            "Verify (I am|you are) (not a bot|(a )?human)"
        )

        verify_button = page.get_by_role("button", name=verify_button_pattern)
        challenge_spinner = page.locator("#challenge-spinner")
        challenge_stage = page.locator("#challenge-stage")
        start_timestamp = datetime.now()

        cookies = await self.cookies(page)
        challenge_type = await self.detect_challenge(page)
        while (
            cookies is None
            and challenge_type is not None
            and (datetime.now() - start_timestamp).seconds < self._timeout
        ):
            if await challenge_spinner.is_visible():
                await challenge_spinner.wait_for(state="hidden")

            turnstile_frame = self._get_turnstile_frame(page)

            if await verify_button.is_visible():
                await verify_button.click()
                await challenge_stage.wait_for(state="hidden")
            elif turnstile_frame is not None:
                await page.mouse.click(210, 290)
                await challenge_stage.wait_for(state="hidden")

            await page.wait_for_timeout(250)

    async def detect(self, page):
        """
        破解CloudFlare
        """
        clearance_cookie = await self.cookies(page)
        if clearance_cookie is None:
            challenge_platform = await self.detect_challenge(page)

            if challenge_platform is None:
                logging.error("未检测到 Cloudflare 挑战。")
                return
            logging.info(f"正在解决 Cloudflare 挑战 [{challenge_platform}]...")

            try:
                await self.solve_challenge(page)
            except PlaywrightError as err:
                logging.error(err)

    def parse_html(self, html_content, meta):
        """
        处理HTML内容
        Args:
            meta: dict 上游传递的数据（如果需要通过这个参数来接受）
            html_content: str HTML内容
        """
        # 具体的解析逻辑需要在子类中实现（根据特定的业务场景去自定义）
        pass

    async def on_response(self, meta, response):
        """
        拦截响应，解析响应
        meta: dict 上游传递的数据（如果需要通过这个参数来接受）
        response: Response 对象
        """
        if not response.ok:
            return
        # target_url = 'https://gmgn.ai/api/v1/token_candles/'
        # # 截获目标数据
        # if target_url in response.url:
        #     logger.info(f'捕获数据接口: {response.url}')
        #     oridata = await response.body()
        #     data_dict = json.loads(oridata)

    async def handle_pdf_route(self, route):
        """拦截 PDF 请求并强制下载"""
        if route.request.url.endswith('.pdf'):
            response = await route.fetch()
            headers = dict(response.headers)
            response = await route.fetch()
            binary_data = await response.body() # 直接获取 bytes
            print(f"获取到 PDF 文档，大小: {len(binary_data)} bytes")
            print(f"PDF 文档内容: {binary_data[:100]}...")  # 打印前100个字节
            # with open("direct_download.pdf", "wb") as f:
                # f.write(binary_data)
            headers['Content-Disposition'] = 'attachment; filename="document.pdf"'
            await route.fulfill(response=response, headers=headers)
            await asyncio.sleep(10)  # 等待页面加载完成
        else:
            await route.continue_()

    async def process_page_request(self, browser, url, meta):
        """
        处理单个URL的页面请求、Cloudflare检测和内容解析
        Args:
            browser: 浏览器实例
            url: string 目标URL
            meta: dict 上游传递的数据（如果需要通过这个参数来接受）
            
        Raises:
            Exception: 如果未能成功获取数据
        """
        # 设置请求的元数据(新增key url)
        meta['url'] = url
        # # 过滤请求
        # filter_key = self.filter_key.format(address.lower())
        # filter_status = self.redis_cli.get(filter_key)
        # if filter_status:
        #     logger.info(f'{self.filter_ex_time} 秒内已经请求过了 url: {url}')
        #     return

        # 每个url都是一个无恒模式，结束则销毁新建
        context = await browser.new_context(accept_downloads=True)
        context.set_default_timeout(self._timeout * 1000)
        page = await context.new_page()

        # 监听请求流
        # 实现传参给response
        response_handler = partial(self.on_response, meta)
        page.on('response', response_handler)
        
        # 访问前成功状态会初始化为False；（如果采集到数据了那么这个值会被设置为True）
        self.task_finished_status = False
        logger.info(f'准备处理URL {url}')
        try:
            # 访问目标地址
            await page.goto(url)
            # 过反爬，如果不加就是被block的状态
            await page.reload()
            await asyncio.sleep(10)
            await self.detect(page)
            html_content = await page.content()
            # 解析HTML内容
            self.parse_html(html_content, meta)
            # 设置路由拦截
            await page.route("**/*", self.handle_pdf_route)
        except:
            logger.error(f'访问失败 {url} 错误信息: {format_exc()}')
        finally:
            await page.close()
            await context.close()
        # 校验是否成功拿到数据了，如果没有拿到数据会抛出异常 (根据self.task_finished_status的值校验)
        self.check_success()
        logger.info(f'请求成功 {url}')

    async def strong_request(self, browser, url, meta):
        """
        带重试机制的请求处理函数
        
        对每次请求进行失败重试，最大重试次数由self.retry_times决定
        
        Args:
            browser: 浏览器实例
            url: string 目标URL
            meta: dict 上游传递的数据（如果需要通过这个参数来接受）
        """
        # 如果没有拿到数据，最多重试 self.retry_times 次
        try_num = 0
        while try_num < self.retry_times:
            try:
                # 处理代币详情页的请求（当没有拿到任何数据的时候，会自动触发崩溃）
                await self.process_page_request(
                    browser=browser,
                    url=url,
                    meta=meta
                )
                # 请求成功就跳出重试的循环
                break
            except Exception as e:
                try_num += 1
                logger.error(f'浏览器数据加载失败（已失败{try_num}次），正在重试（新建context），错误信息: {e}，URL：{url}')
                if try_num < self.retry_times:
                    await asyncio.sleep(3)

    async def run_local(self, proxy=None):
        async with async_playwright() as p:
            # 必须得是有头浏览器，否则过不了Cloudflare
            launch_data = {
                "headless": False,
                "proxy": proxy,
                "args": [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-infobars',
                '--disable-extensions',
                '--disable-features=VizDisplayCompositor'
            ]
            }

            # user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            browser = await p.chromium.launch(**launch_data)
            for url in self.target_urls:
                # 每个url都是一个无恒模式，结束则销毁新建
                await self.strong_request(
                    browser=browser,
                    url = url,
                    # 传递元数据  
                    meta = {}
                )
            # 等待页面加载完成
            # await page.wait_for_load_state('networkidle')
            logger.info('所有任务处理完成，关闭浏览器')
            await browser.close()

    async def run_aws(self):
        """
        在AWS服务器启动
        """
        proxy = self.proxy
        from pyvirtualdisplay import Display
        with Display():
            await self.run_local(proxy)

    def check_success(self):
        """
        校验爬虫是否拿到数据
        """
        if not self.task_finished_status:
            logger.error('采集失败')
            raise Exception('爬虫没有采集到数据')

    @ErrorMonitor(spider_name, author)
    @retry(tries=3, delay=3)
    def task(self):
        if env == 'local':
            asyncio.run(self.run_local())
        else:
            asyncio.run(self.run_aws())

    # 10分钟执行一次
    @scheduled_task(start_time=None, duration=10*60)
    def run(self):
        """
        爬虫启动入口
        """
        self.task()