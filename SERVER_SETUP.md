# 服务器部署指南

## 🚀 快速部署 (推荐)

### 方法一: 使用安装脚本 (Ubuntu/Debian)

```bash
# 1. 克隆项目
git clone <your-repo-url> boss-monitor
cd boss-monitor

# 2. 运行安装脚本
chmod +x install.sh
./install.sh

# 3. 配置环境变量
nano .env
# 填写 LARKBOT_ID=your_lark_bot_id

# 4. 运行项目
source venv/bin/activate
python main.py
```

### 方法二: 使用 Docker (最简单)

```bash
# 1. 克隆项目
git clone <your-repo-url> boss-monitor
cd boss-monitor

# 2. 创建环境变量文件
cat > .env << EOF
LARKBOT_ID=your_lark_bot_id
REDIS_PASSWORD=your_redis_password
EOF

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f boss-monitor
```

### 方法三: 手动安装

#### 1. 安装系统依赖

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip redis-server git curl
sudo apt install -y fonts-liberation fonts-noto-cjk libgtk-3-0 libnss3 xvfb
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**CentOS/RHEL:**
```bash
sudo yum install -y python3.12 python3-pip redis git curl
sudo yum install -y liberation-fonts google-noto-cjk-fonts gtk3 xorg-x11-server-Xvfb
sudo systemctl start redis
sudo systemctl enable redis
```

#### 2. 安装项目依赖

```bash
# 创建虚拟环境
python3.12 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 3. 配置环境变量

```bash
# 创建 .env 文件
cat > .env << EOF
LARKBOT_ID=your_lark_bot_id
REDIS_PASSWORD=your_redis_password
EOF
```

#### 4. 运行项目

```bash
source venv/bin/activate
python main.py
```

## 🔧 生产环境部署

### 使用 systemd 服务

```bash
# 1. 创建服务文件
sudo tee /etc/systemd/system/boss-monitor.service > /dev/null << EOF
[Unit]
Description=Boss Monitor Service
After=network.target redis.service

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 2. 启动服务
sudo systemctl daemon-reload
sudo systemctl enable boss-monitor
sudo systemctl start boss-monitor

# 3. 查看状态
sudo systemctl status boss-monitor
sudo journalctl -u boss-monitor -f
```

## 📋 依赖清单

### Python 依赖
- `patchright>=1.55.2` - 浏览器自动化
- `redis>=5.0.0` - Redis 客户端
- `requests>=2.32.5` - HTTP 请求
- `retry>=0.9.2` - 重试机制
- `pyvirtualdisplay>=3.0` - 虚拟显示

### 系统依赖
- **Python**: >= 3.12
- **Redis**: 缓存服务
- **浏览器依赖**: 字体、GTK、X11 等 (用于 patchright)

### 环境变量
- `LARKBOT_ID`: 飞书机器人 ID (必需)
- `REDIS_PASSWORD`: Redis 密码 (可选)

## 🐛 常见问题

### 1. Redis 连接失败
```bash
# 检查 Redis 状态
sudo systemctl status redis-server
redis-cli ping
```

### 2. 浏览器依赖问题
```bash
# 测试 patchright
python -c "from patchright.async_api import async_playwright; print('OK')"
```

### 3. 权限问题
```bash
# 确保文件权限正确
chmod +x main.py
chmod +x install.sh
```

### 4. Python 版本问题
```bash
# 检查 Python 版本
python3 --version
# 需要 >= 3.12
```

## 📊 监控和维护

### 查看日志
```bash
# systemd 服务日志
sudo journalctl -u boss-monitor -f

# Docker 日志
docker-compose logs -f boss-monitor

# 手动运行日志
tail -f boss_monitor.log
```

### 重启服务
```bash
# systemd
sudo systemctl restart boss-monitor

# Docker
docker-compose restart boss-monitor
```

### 更新项目
```bash
# 拉取最新代码
git pull

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
sudo systemctl restart boss-monitor
```

## 🔒 安全建议

1. **防火墙配置**: 只开放必要的端口
2. **用户权限**: 使用非 root 用户运行服务
3. **环境变量**: 不要在代码中硬编码敏感信息
4. **定期更新**: 保持系统和依赖的更新
5. **日志监控**: 定期检查日志文件大小
