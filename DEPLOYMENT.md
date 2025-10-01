# Boss Monitor 服务器部署指南

## 系统要求

- **Python**: >= 3.12
- **操作系统**: Linux (推荐 Ubuntu 20.04+ 或 CentOS 7+)
- **内存**: 至少 2GB RAM
- **存储**: 至少 1GB 可用空间

## 依赖服务

### 1. Redis 服务器
项目需要 Redis 作为缓存和存储服务。

#### Ubuntu/Debian 安装 Redis:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### CentOS/RHEL 安装 Redis:
```bash
sudo yum install epel-release
sudo yum install redis
sudo systemctl start redis
sudo systemctl enable redis
```

#### 验证 Redis 安装:
```bash
redis-cli ping
# 应该返回 PONG
```

### 2. 浏览器依赖 (用于 patchright)
由于项目使用了 patchright 进行浏览器自动化，需要安装浏览器和字体。

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install -y \
    fonts-liberation \
    fonts-noto-color-emoji \
    fonts-noto-cjk \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    xvfb
```

#### CentOS/RHEL:
```bash
sudo yum install -y \
    liberation-fonts \
    google-noto-cjk-fonts \
    alsa-lib \
    atk \
    cups-libs \
    gtk3 \
    libXScrnSaver \
    xorg-x11-server-Xvfb
```

## 项目部署

### 方法一: 使用 uv (推荐)

#### 1. 安装 uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # 或重新登录
```

#### 2. 克隆项目
```bash
git clone <your-repo-url> boss-monitor
cd boss-monitor
```

#### 3. 创建虚拟环境并安装依赖
```bash
uv venv
source .venv/bin/activate
uv sync
```

### 方法二: 使用 pip

#### 1. 创建虚拟环境
```bash
python3.12 -m venv venv
source venv/bin/activate
```

#### 2. 升级 pip
```bash
pip install --upgrade pip
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

## 环境变量配置

创建 `.env` 文件或设置环境变量:

```bash
# Redis 密码 (如果 Redis 设置了密码)
export REDIS_PASSWORD="your_redis_password"

# 飞书机器人 ID
export LARKBOT_ID="your_lark_bot_id"
```

### 创建环境变量文件:
```bash
cat > .env << EOF
REDIS_PASSWORD=your_redis_password
LARKBOT_ID=your_lark_bot_id
EOF
```

## 运行项目

### 1. 测试运行
```bash
# 激活虚拟环境
source venv/bin/activate  # 或 source .venv/bin/activate (如果使用 uv)

# 运行项目
python main.py
```

### 2. 后台运行 (使用 nohup)
```bash
nohup python main.py > boss_monitor.log 2>&1 &
```

### 3. 使用 systemd 服务 (推荐生产环境)

创建服务文件:
```bash
sudo tee /etc/systemd/system/boss-monitor.service > /dev/null << EOF
[Unit]
Description=Boss Monitor Service
After=network.target redis.service

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/boss-monitor
Environment=PATH=/path/to/boss-monitor/venv/bin
ExecStart=/path/to/boss-monitor/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl enable boss-monitor
sudo systemctl start boss-monitor
```

查看服务状态:
```bash
sudo systemctl status boss-monitor
sudo journalctl -u boss-monitor -f
```

## 防火墙配置

如果需要访问外部服务，确保防火墙允许相关端口:

```bash
# Ubuntu/Debian
sudo ufw allow out 443  # HTTPS
sudo ufw allow out 80   # HTTP
sudo ufw allow out 6379 # Redis (如果需要外部访问)

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --reload
```

## 日志和监控

### 查看日志:
```bash
# 如果使用 systemd
sudo journalctl -u boss-monitor -f

# 如果使用 nohup
tail -f boss_monitor.log
```

### 监控进程:
```bash
ps aux | grep python
```

## 故障排除

### 1. Redis 连接问题
```bash
# 检查 Redis 是否运行
sudo systemctl status redis

# 测试连接
redis-cli ping
```

### 2. 浏览器依赖问题
```bash
# 检查浏览器依赖
python -c "from patchright.async_api import async_playwright; print('OK')"
```

### 3. 权限问题
确保运行用户有适当的权限:
```bash
chmod +x main.py
```

## 更新项目

```bash
# 拉取最新代码
git pull

# 更新依赖 (如果使用 uv)
uv sync

# 或使用 pip
pip install -r requirements.txt

# 重启服务
sudo systemctl restart boss-monitor
```

## 备份

定期备份 Redis 数据:
```bash
# Redis 数据备份
redis-cli --rdb /backup/redis_backup_$(date +%Y%m%d).rdb
```
