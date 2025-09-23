#!/bin/bash
# Server setup script for HackReality Bot

echo "🚀 Setting up HackReality Bot on server..."
echo "=========================================="

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "🔧 Installing required packages..."
sudo apt install -y python3 python3-pip python3-venv git curl wget htop

# Create bot user
echo "👤 Creating bot user..."
sudo adduser --disabled-password --gecos "" telegrambot
sudo usermod -aG sudo telegrambot

# Create directories
echo "📁 Creating directories..."
sudo mkdir -p /opt/hackreality-bot
sudo chown telegrambot:telegrambot /opt/hackreality-bot

# Setup systemd services
echo "⚙️ Setting up systemd services..."

# Main bot service
sudo tee /etc/systemd/system/hackreality-bot.service > /dev/null <<EOF
[Unit]
Description=HackReality Main Bot
After=network.target

[Service]
Type=simple
User=telegrambot
Group=telegrambot
WorkingDirectory=/opt/hackreality-bot
Environment=PATH=/opt/hackreality-bot/venv/bin
ExecStart=/opt/hackreality-bot/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Admin bot service
sudo tee /etc/systemd/system/hackreality-admin-bot.service > /dev/null <<EOF
[Unit]
Description=HackReality Admin Bot
After=network.target

[Service]
Type=simple
User=telegrambot
Group=telegrambot
WorkingDirectory=/opt/hackreality-bot
Environment=PATH=/opt/hackreality-bot/venv/bin
ExecStart=/opt/hackreality-bot/venv/bin/python admin_bot_complete.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Setup log rotation
echo "📝 Setting up log rotation..."
sudo tee /etc/logrotate.d/hackreality-bot > /dev/null <<EOF
/opt/hackreality-bot/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 644 telegrambot telegrambot
}
EOF

# Setup firewall
echo "🔥 Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

echo ""
echo "✅ Server setup complete!"
echo ""
echo "Next steps:"
echo "1. Switch to bot user: su - telegrambot"
echo "2. Deploy bot code to /opt/hackreality-bot"
echo "3. Setup Python environment:"
echo "   cd /opt/hackreality-bot"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo "4. Configure environment variables:"
echo "   cp .env.example .env"
echo "   nano .env"
echo "5. Enable and start services:"
echo "   sudo systemctl enable hackreality-bot"
echo "   sudo systemctl enable hackreality-admin-bot"
echo "   sudo systemctl start hackreality-bot"
echo "   sudo systemctl start hackreality-admin-bot"
echo ""
echo "🎉 Your server is ready for HackReality Bot!"
