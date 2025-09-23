#!/bin/bash
# AWS EC2 Deployment Script for HackReality Bot

echo "🆓 AWS EC2 Free Tier Deployment"
echo "================================"

# Check if server IP and key file are provided
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: ./deploy_aws.sh SERVER_IP KEY_FILE.pem"
    echo "Example: ./deploy_aws.sh 54.123.45.67 hackreality-bot-key.pem"
    echo ""
    echo "Make sure you have:"
    echo "1. Created AWS EC2 instance (t3.micro, Ubuntu 22.04)"
    echo "2. Downloaded the .pem key file"
    echo "3. Set correct permissions: chmod 400 KEY_FILE.pem"
    exit 1
fi

SERVER_IP=$1
KEY_FILE=$2

# Check if key file exists
if [ ! -f "$KEY_FILE" ]; then
    echo "❌ Key file not found: $KEY_FILE"
    echo "Make sure the .pem file is in the current directory"
    exit 1
fi

echo "📡 Deploying to AWS EC2: $SERVER_IP"
echo "🔑 Using key file: $KEY_FILE"
echo ""

# Test SSH connection
echo "🔌 Testing SSH connection..."
ssh -i "$KEY_FILE" -o ConnectTimeout=10 -o BatchMode=yes ubuntu@$SERVER_IP exit
if [ $? -ne 0 ]; then
    echo "❌ Cannot connect to server. Please check:"
    echo "1. Server IP address is correct"
    echo "2. Key file permissions: chmod 400 $KEY_FILE"
    echo "3. Security group allows SSH (port 22) from your IP"
    echo "4. Instance is running"
    exit 1
fi
echo "✅ SSH connection successful"
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
    --exclude='*.pem' \
    .

echo "✅ Deployment package created"
echo ""

# Upload to server
echo "📤 Uploading to AWS EC2..."
scp -i "$KEY_FILE" hackreality-bot.tar.gz ubuntu@$SERVER_IP:/home/ubuntu/

echo "🔧 Setting up bot on AWS EC2..."
ssh -i "$KEY_FILE" ubuntu@$SERVER_IP << 'EOF'
    echo "📁 Extracting bot files..."
    sudo mkdir -p /opt/hackreality-bot
    sudo chown ubuntu:ubuntu /opt/hackreality-bot
    cd /opt/hackreality-bot
    tar -xzf /home/ubuntu/hackreality-bot.tar.gz
    rm /home/ubuntu/hackreality-bot.tar.gz
    
    echo "🐍 Setting up Python environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo "⚙️ Setting up systemd services..."
    
    # Main bot service
    sudo tee /etc/systemd/system/hackreality-bot.service > /dev/null <<EOL
[Unit]
Description=HackReality Main Bot
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/hackreality-bot
Environment=PATH=/opt/hackreality-bot/venv/bin
ExecStart=/opt/hackreality-bot/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOL

    # Admin bot service
    sudo tee /etc/systemd/system/hackreality-admin-bot.service > /dev/null <<EOL
[Unit]
Description=HackReality Admin Bot
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/hackreality-bot
Environment=PATH=/opt/hackreality-bot/venv/bin
ExecStart=/opt/hackreality-bot/venv/bin/python admin_bot_complete.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOL

    echo "🔄 Reloading systemd..."
    sudo systemctl daemon-reload
    
    echo "⚙️ Setting up environment variables..."
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "📝 Please edit .env file with your bot tokens:"
        echo "   sudo nano .env"
        echo ""
        echo "Required variables:"
        echo "   TELEGRAM_BOT_TOKEN=your_main_bot_token"
        echo "   ADMIN_BOT_TOKEN=your_admin_bot_token"
        echo "   ADMIN_USER_ID=your_telegram_id"
        echo "   ADMIN_TELEGRAM_ID=your_telegram_id"
        echo ""
        echo "After editing .env, run:"
        echo "   sudo systemctl enable hackreality-bot"
        echo "   sudo systemctl enable hackreality-admin-bot"
        echo "   sudo systemctl start hackreality-bot"
        echo "   sudo systemctl start hackreality-admin-bot"
    fi
    
    echo "✅ Bot setup complete on AWS EC2!"
    echo "🚀 Ready to start the bots!"
EOF

echo ""
echo "🎉 AWS EC2 deployment completed!"
echo ""
echo "Next steps:"
echo "1. SSH into your server: ssh -i $KEY_FILE ubuntu@$SERVER_IP"
echo "2. Edit environment variables: sudo nano /opt/hackreality-bot/.env"
echo "3. Start the bots:"
echo "   sudo systemctl enable hackreality-bot"
echo "   sudo systemctl enable hackreality-admin-bot"
echo "   sudo systemctl start hackreality-bot"
echo "   sudo systemctl start hackreality-admin-bot"
echo ""
echo "4. Check status:"
echo "   sudo systemctl status hackreality-bot"
echo "   sudo systemctl status hackreality-admin-bot"
echo ""
echo "5. View logs:"
echo "   sudo journalctl -u hackreality-bot -f"
echo ""
echo "🆓 Your bot is now running on AWS EC2 Free Tier!"
echo "💰 Cost: $0/month for 12 months!"
