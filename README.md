# Boss Monitor - 智能合约工程师职位监控系统

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![Redis](https://img.shields.io/badge/Redis-5.0+-red.svg)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-green.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 项目简介

Boss Monitor 是一个智能合约工程师职位监控系统，专门用于监控 Boss直聘网站上的智能合约相关职位，并通过飞书机器人实时推送符合条件的职位信息。

### 🎯 核心功能

- **智能职位筛选**: 自动筛选包含"智能合约"、"Solidity"、"区块链合约"关键词的职位
- **薪资门槛过滤**: 只推送薪资20K以上的职位
- **多城市监控**: 支持全国15个主要城市的职位监控
- **去重机制**: 使用Redis缓存避免重复推送
- **实时推送**: 通过飞书机器人即时推送职位信息
- **反爬虫绕过**: 基于patchright的Cloudflare反爬虫绕过技术
- **定时调度**: 每10分钟自动执行一次监控任务
- **错误监控**: 自动错误捕获和告警机制

## 🏗️ 项目架构

```
boss_monitor/
├── main.py                 # 主程序入口
├── spider.py              # 核心爬虫逻辑
├── utils/                 # 工具模块
│   ├── browser.py         # 浏览器自动化基类
│   ├── lark_bot.py        # 飞书机器人接口
│   ├── redisdb.py         # Redis数据库连接
│   ├── scheduler.py       # 定时调度器
│   └── spider_failed_alert.py  # 错误监控
├── requirements.txt       # Python依赖
├── pyproject.toml         # 项目配置
├── Dockerfile            # Docker镜像构建
├── docker-compose.yml    # Docker编排
├── install.sh           # 自动安装脚本
├── DEPLOYMENT.md        # 详细部署指南
└── SERVER_SETUP.md      # 服务器设置指南
```

## 🚀 快速开始

### 环境要求

- **Python**: >= 3.12
- **Redis**: >= 5.0
- **操作系统**: Linux/macOS/Windows

### 方法一: Docker部署 (推荐)

```bash
# 1. 克隆项目
git clone <your-repo-url> boss-monitor
cd boss-monitor

# 2. 配置环境变量
cat > .env << EOF
LARKBOT_ID=your_lark_bot_id
REDIS_PASSWORD=your_redis_password
EOF

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f boss-monitor
```

### 方法二: 本地部署

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动Redis服务
redis-server

# 3. 设置环境变量
export LARKBOT_ID="your_lark_bot_id"
export REDIS_PASSWORD="your_redis_password"

# 4. 运行项目
python main.py
```

### 方法三: 使用安装脚本

```bash
# 运行自动安装脚本 (Ubuntu/Debian)
chmod +x install.sh
./install.sh
```

## ⚙️ 配置说明

### 环境变量

| 变量名 | 必需 | 说明 | 示例 |
|--------|------|------|------|
| `LARKBOT_ID` | ✅ | 飞书机器人ID | `7bbfc97b-adc9c` |
| `REDIS_PASSWORD` | ❌ | Redis密码 | `your_password` |

### 监控城市配置

系统默认监控以下15个城市：

- 北京 (100010000)
- 上海 (101010100)
- 深圳 (101020100)
- 广州 (101280100)
- 杭州 (101280600)
- 成都 (101210100)
- 南京 (101030100)
- 武汉 (101110100)
- 西安 (101190400)
- 苏州 (101200100)
- 厦门 (101230200)
- 长沙 (101250100)
- 青岛 (101270100)
- 郑州 (101180100)
- 天津 (101040100)

### 职位筛选条件

- **关键词匹配**: 职位名称必须包含以下任一关键词：
  - 智能合约
  - Solidity
  - 区块链合约

- **薪资门槛**: 薪资上限必须 >= 20K

## 🔧 技术栈

### 核心技术

- **Python 3.12+**: 主要开发语言
- **patchright**: 浏览器自动化，用于绕过Cloudflare反爬虫
- **Redis**: 缓存和去重存储
- **requests**: HTTP请求处理
- **asyncio**: 异步编程支持

### 反爬虫技术

- **Cloudflare绕过**: 自动检测和解决Cloudflare挑战
- **浏览器指纹伪装**: 模拟真实浏览器行为
- **请求重试机制**: 失败自动重试，提高成功率
- **虚拟显示**: 支持无头浏览器运行

### 监控和告警

- **定时调度**: 每10分钟执行一次监控
- **错误监控**: 自动捕获异常并发送告警
- **去重机制**: 避免重复推送相同职位
- **状态检查**: 实时监控爬虫运行状态

## 📊 功能特性

### 智能职位筛选

```python
# 职位名称关键词检查
name_check_list = [
    '智能合约',
    'Solidity', 
    '区块链合约'
]

# 薪资门槛检查
if salaryDesc_up_int < 20:
    continue  # 跳过薪资过低的职位
```

### 多城市监控

```python
# 支持的城市代码
codes = [100010000, 101010100, 101020100, ...]
for code in self.codes:
    url = self.api.format(code)
    self.target_urls.append(url)
```

### 飞书推送

```python
# 推送格式
content = f"""{salaryDesc}
{jobName}
{brandName}
{brandScaleName}
{cityName}
{url}"""
```

## 🐳 Docker部署

### 构建镜像

```bash
docker build -t boss-monitor .
```

### 运行容器

```bash
docker run -d \
  --name boss-monitor \
  -e LARKBOT_ID="your_bot_id" \
  -e REDIS_PASSWORD="your_password" \
  boss-monitor
```

### Docker Compose

```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  boss-monitor:
    build: .
    depends_on:
      - redis
    environment:
      - LARKBOT_ID=${LARKBOT_ID}
      - REDIS_PASSWORD=${REDIS_PASSWORD}
    volumes:
      - ./logs:/app/logs
```

## 🔍 监控和维护

### 查看日志

```bash
# Docker方式
docker-compose logs -f boss-monitor

# 本地方式
tail -f boss_monitor.log

# systemd服务
sudo journalctl -u boss-monitor -f
```

### 服务管理

```bash
# 启动服务
sudo systemctl start boss-monitor

# 停止服务
sudo systemctl stop boss-monitor

# 重启服务
sudo systemctl restart boss-monitor

# 查看状态
sudo systemctl status boss-monitor
```

### Redis管理

```bash
# 连接Redis
redis-cli

# 查看黑名单
SMEMBERS binance:listing:black

# 清空黑名单
DEL binance:listing:black
```

## 🛠️ 开发指南

### 项目结构说明

- **`main.py`**: 程序入口，启动BossAlert爬虫
- **`spider.py`**: 核心爬虫类，继承自FuckCF基类
- **`utils/browser.py`**: 浏览器自动化基类，提供Cloudflare绕过能力
- **`utils/lark_bot.py`**: 飞书机器人消息发送接口
- **`utils/redisdb.py`**: Redis连接和操作封装
- **`utils/scheduler.py`**: 定时任务调度装饰器
- **`utils/spider_failed_alert.py`**: 错误监控和告警装饰器

### 扩展开发

1. **添加新城市**: 在`spider.py`中的`codes`列表添加城市代码
2. **修改筛选条件**: 调整`name_check_list`和薪资门槛
3. **自定义推送格式**: 修改`parse`方法中的`content`格式
4. **添加新功能**: 继承`FuckCF`基类实现新的爬虫

### 代码示例

```python
class CustomSpider(FuckCF):
    def __init__(self):
        super().__init__()
        self.target_urls = ['https://example.com']
    
    def parse(self, data):
        # 自定义解析逻辑
        pass
    
    async def on_response(self, meta, response):
        # 自定义响应处理
        pass
```

## 🐛 故障排除

### 常见问题

1. **Redis连接失败**
   ```bash
   # 检查Redis服务状态
   sudo systemctl status redis-server
   redis-cli ping
   ```

2. **浏览器依赖问题**
   ```bash
   # 安装浏览器依赖
   sudo apt install fonts-liberation libgtk-3-0 xvfb
   ```

3. **飞书机器人配置**
   - 确保`LARKBOT_ID`环境变量正确设置
   - 检查飞书机器人webhook地址是否有效

4. **权限问题**
   ```bash
   # 确保文件权限正确
   chmod +x main.py
   ```

### 调试模式

```bash
# 启用详细日志
export PYTHONPATH=.
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from main import main
main()
"
```

## 📈 性能优化

### 建议配置

- **内存**: 至少2GB RAM
- **CPU**: 2核心以上
- **存储**: 至少1GB可用空间
- **网络**: 稳定的网络连接

### 优化建议

1. **Redis优化**: 配置Redis内存限制和持久化策略
2. **并发控制**: 调整浏览器并发数量
3. **缓存策略**: 优化Redis缓存过期时间
4. **日志管理**: 定期清理日志文件

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👥 作者

- **drake.shi** - 项目创建者和维护者

## 🙏 致谢

- 感谢 [patchright](https://github.com/patchright/patchright) 提供的浏览器自动化能力
- 感谢 [CF-Clearance-Scraper](https://github.com/Xewdy444/CF-Clearance-Scraper) 提供的Cloudflare绕过技术参考

## 📞 支持

如果您遇到任何问题或有建议，请：

1. 查看 [故障排除](#故障排除) 部分
2. 查看 [DEPLOYMENT.md](DEPLOYMENT.md) 详细部署指南
3. 查看 [SERVER_SETUP.md](SERVER_SETUP.md) 服务器设置指南
4. 提交 [Issue](https://github.com/your-repo/issues)

---

⭐ 如果这个项目对您有帮助，请给它一个星标！