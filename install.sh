#!/bin/bash

# Boss Monitor 快速安装脚本
# 适用于 Ubuntu/Debian 系统

set -e

echo "🚀 开始安装 Boss Monitor..."

# 检查是否为 root 用户
if [[ $EUID -eq 0 ]]; then
   echo "❌ 请不要使用 root 用户运行此脚本"
   exit 1
fi

# 检查 Python 版本
echo "📋 检查 Python 版本..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
required_version="3.12"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python 版本检查通过: $python_version"
else
    echo "❌ 需要 Python >= 3.12，当前版本: $python_version"
    echo "请升级 Python 版本后重试"
    exit 1
fi

# 更新系统包
echo "📦 更新系统包..."
sudo apt update

# 安装系统依赖
echo "🔧 安装系统依赖..."
sudo apt install -y \
    python3-venv \
    python3-pip \
    git \
    curl \
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

# 安装 Redis
echo "🗄️ 安装 Redis..."
sudo apt install -y redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# 验证 Redis 安装
echo "🔍 验证 Redis 安装..."
if redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis 安装成功"
else
    echo "❌ Redis 安装失败"
    exit 1
fi

# 创建虚拟环境
echo "🐍 创建 Python 虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 虚拟环境创建成功"
else
    echo "⚠️ 虚拟环境已存在，跳过创建"
fi

# 激活虚拟环境并安装依赖
echo "📚 安装 Python 依赖..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Python 依赖安装完成"

# 创建环境变量文件模板
echo "⚙️ 创建环境变量文件..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# Redis 密码 (如果 Redis 设置了密码，请取消注释并填写)
# REDIS_PASSWORD=your_redis_password

# 飞书机器人 ID (请填写你的机器人 ID)
LARKBOT_ID=your_lark_bot_id
EOF
    echo "✅ 环境变量文件 .env 已创建"
    echo "⚠️ 请编辑 .env 文件，填写正确的 LARKBOT_ID"
else
    echo "⚠️ .env 文件已存在，跳过创建"
fi

# 测试安装
echo "🧪 测试安装..."
if python -c "import patchright, redis, requests, retry; print('✅ 所有依赖导入成功')" 2>/dev/null; then
    echo "✅ 安装测试通过"
else
    echo "❌ 安装测试失败，请检查依赖安装"
    exit 1
fi

echo ""
echo "🎉 Boss Monitor 安装完成！"
echo ""
echo "📝 接下来的步骤:"
echo "1. 编辑 .env 文件，填写正确的 LARKBOT_ID"
echo "2. 运行项目: source venv/bin/activate && python main.py"
echo "3. 查看部署文档: cat DEPLOYMENT.md"
echo ""
echo "🔗 有用的命令:"
echo "   - 启动 Redis: sudo systemctl start redis-server"
echo "   - 查看 Redis 状态: sudo systemctl status redis-server"
echo "   - 激活虚拟环境: source venv/bin/activate"
echo "   - 运行项目: python main.py"
echo ""
