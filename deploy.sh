#!/bin/bash
# HackReality Bot Deployment Script

echo "🚀 HackReality Bot Deployment Script"
echo "======================================"

# Check if server IP is provided
if [ -z "$1" ]; then
    echo "Usage: ./deploy.sh SERVER_IP [USERNAME]"
    echo "Example: ./deploy.sh 192.168.1.100 telegrambot"
    exit 1
fi

SERVER_IP=$1
USERNAME=${2:-telegrambot}

echo "📡 Deploying to server: $SERVER_IP"
echo "👤 Using username: $USERNAME"
echo ""

# Create deployment package
echo "📦 Creating deployment package..."
tar -czf hackreality-bot.tar.gz \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='logs' \
    --exclude='*.log' \
    .

echo "✅ Deployment package created: hackreality-bot.tar.gz"
echo ""

# Upload to server
echo "📤 Uploading to server..."
scp hackreality-bot.tar.gz $USERNAME@$SERVER_IP:/home/$USERNAME/

echo "🔧 Setting up bot on server..."
ssh $USERNAME@$SERVER_IP << 'EOF'
    echo "📁 Extracting bot files..."
    tar -xzf hackreality-bot.tar.gz
    rm hackreality-bot.tar.gz
    
    echo "🐍 Setting up Python environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    echo "⚙️ Setting up environment variables..."
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "📝 Please edit .env file with your bot tokens:"
        echo "   nano .env"
        echo ""
        echo "Required variables:"
        echo "   TELEGRAM_BOT_TOKEN=your_main_bot_token"
        echo "   ADMIN_BOT_TOKEN=your_admin_bot_token"
        echo "   ADMIN_USER_ID=your_telegram_id"
        echo "   ADMIN_TELEGRAM_ID=your_telegram_id"
        echo ""
        echo "After editing .env, run:"
        echo "   source venv/bin/activate"
        echo "   python main.py &"
        echo "   python admin_bot_complete.py &"
    fi
    
    echo "✅ Bot setup complete!"
    echo "🚀 Ready to start the bots!"
EOF

echo ""
echo "🎉 Deployment completed!"
echo ""
echo "Next steps:"
echo "1. SSH into your server: ssh $USERNAME@$SERVER_IP"
echo "2. Edit environment variables: nano .env"
echo "3. Start the bots:"
echo "   cd TelegramBot"
echo "   source venv/bin/activate"
echo "   python main.py &"
echo "   python admin_bot_complete.py &"
echo ""
echo "For production setup with systemd, see SERVER_DEPLOYMENT_GUIDE.md"
