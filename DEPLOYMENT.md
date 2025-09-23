# 🚀 HackReality Bot Deployment Guide

This guide will help you deploy the HackReality Telegram bot to production.

## 📋 Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **Python**: 3.8 or higher
- **RAM**: Minimum 512MB, Recommended 1GB+
- **Storage**: Minimum 1GB free space
- **Network**: Stable internet connection

### Required Accounts
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- T-Bank account for payments
- Admin Telegram account for notifications

## 🔧 Step 1: Server Setup

### 1.1 Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 Install Python and Dependencies
```bash
# Install Python 3.8+
sudo apt install python3 python3-pip python3-venv -y

# Install system dependencies
sudo apt install sqlite3 git curl -y
```

### 1.3 Create Bot User
```bash
# Create dedicated user for the bot
sudo useradd -m -s /bin/bash hackreality
sudo usermod -aG sudo hackreality
```

## 📦 Step 2: Bot Installation

### 2.1 Clone Repository
```bash
# Switch to bot user
sudo su - hackreality

# Clone the repository
git clone <your-repository-url> /home/hackreality/TelegramBot
cd /home/hackreality/TelegramBot
```

### 2.2 Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2.3 Configure Environment
```bash
# Copy environment template
cp env_example.txt .env

# Edit environment variables
nano .env
```

**Required Environment Variables:**
```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_actual_bot_token_here

# Admin Configuration
ADMIN_TELEGRAM_ID=your_admin_telegram_chat_id

# Database Configuration
DATABASE_PATH=/home/hackreality/TelegramBot/bot_database.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/home/hackreality/TelegramBot/logs/bot.log

# Bot Configuration
BOT_NAME=HackReality
BOT_DESCRIPTION=Psychological practice bot for goal achievement
```

### 2.4 Create Directories
```bash
# Create necessary directories
mkdir -p logs
mkdir -p backups
mkdir -p data
```

## 🔐 Step 3: Security Configuration

### 3.1 Set File Permissions
```bash
# Set proper permissions
chmod 600 .env
chmod 755 main.py
chmod 755 run_tests.py
chmod -R 755 modules/
chmod -R 755 tests/
```

### 3.2 Configure Firewall
```bash
# Allow SSH and block unnecessary ports
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 3.3 Secure Database
```bash
# Set database permissions
chmod 600 bot_database.db
chown hackreality:hackreality bot_database.db
```

## 🧪 Step 4: Testing

### 4.1 Run Tests
```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
python run_tests.py

# Run specific test
python run_tests.py test_database.py
```

### 4.2 Manual Testing
```bash
# Test bot startup
python main.py

# Check logs
tail -f logs/bot.log
```

## 🚀 Step 5: Production Deployment

### 5.1 Create Systemd Service
```bash
# Create service file
sudo nano /etc/systemd/system/hackreality-bot.service
```

**Service Configuration:**
```ini
[Unit]
Description=HackReality Telegram Bot
After=network.target

[Service]
Type=simple
User=hackreality
Group=hackreality
WorkingDirectory=/home/hackreality/TelegramBot
Environment=PATH=/home/hackreality/TelegramBot/venv/bin
ExecStart=/home/hackreality/TelegramBot/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 5.2 Enable and Start Service
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable hackreality-bot

# Start service
sudo systemctl start hackreality-bot

# Check status
sudo systemctl status hackreality-bot
```

### 5.3 Configure Log Rotation
```bash
# Create logrotate configuration
sudo nano /etc/logrotate.d/hackreality-bot
```

**Logrotate Configuration:**
```
/home/hackreality/TelegramBot/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 hackreality hackreality
    postrotate
        systemctl reload hackreality-bot
    endscript
}
```

## 📊 Step 6: Monitoring Setup

### 6.1 Create Monitoring Script
```bash
# Create monitoring script
nano /home/hackreality/TelegramBot/monitor.sh
```

**Monitoring Script:**
```bash
#!/bin/bash

# Check if bot is running
if ! systemctl is-active --quiet hackreality-bot; then
    echo "Bot is not running! Restarting..."
    systemctl restart hackreality-bot
    # Send notification to admin
    curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
         -d "chat_id=$ADMIN_TELEGRAM_ID" \
         -d "text=🚨 Bot was down and has been restarted!"
fi

# Check disk space
DISK_USAGE=$(df /home/hackreality | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "Disk usage is high: ${DISK_USAGE}%"
    # Send notification to admin
    curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
         -d "chat_id=$ADMIN_TELEGRAM_ID" \
         -d "text=⚠️ Disk usage is high: ${DISK_USAGE}%"
fi

# Check memory usage
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ $MEMORY_USAGE -gt 80 ]; then
    echo "Memory usage is high: ${MEMORY_USAGE}%"
    # Send notification to admin
    curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
         -d "chat_id=$ADMIN_TELEGRAM_ID" \
         -d "text=⚠️ Memory usage is high: ${MEMORY_USAGE}%"
fi
```

### 6.2 Set Up Cron Job
```bash
# Make script executable
chmod +x /home/hackreality/TelegramBot/monitor.sh

# Add to crontab
crontab -e

# Add this line to run every 5 minutes
*/5 * * * * /home/hackreality/TelegramBot/monitor.sh
```

## 💾 Step 7: Backup Configuration

### 7.1 Create Backup Script
```bash
# Create backup script
nano /home/hackreality/TelegramBot/backup.sh
```

**Backup Script:**
```bash
#!/bin/bash

BACKUP_DIR="/home/hackreality/TelegramBot/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="hackreality_backup_$DATE.tar.gz"

# Create backup
tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='logs' \
    /home/hackreality/TelegramBot

# Keep only last 7 days of backups
find $BACKUP_DIR -name "hackreality_backup_*.tar.gz" -mtime +7 -delete

echo "Backup created: $BACKUP_FILE"
```

### 7.2 Set Up Daily Backups
```bash
# Make script executable
chmod +x /home/hackreality/TelegramBot/backup.sh

# Add to crontab for daily backups at 2 AM
0 2 * * * /home/hackreality/TelegramBot/backup.sh
```

## 🔄 Step 8: Update Procedure

### 8.1 Create Update Script
```bash
# Create update script
nano /home/hackreality/TelegramBot/update.sh
```

**Update Script:**
```bash
#!/bin/bash

echo "🔄 Updating HackReality Bot..."

# Stop the bot
sudo systemctl stop hackreality-bot

# Create backup
./backup.sh

# Pull latest changes
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run tests
python run_tests.py

# Start the bot
sudo systemctl start hackreality-bot

echo "✅ Update completed!"
```

## 📱 Step 9: Bot Configuration

### 9.1 Set Bot Commands
Use [@BotFather](https://t.me/botfather) to set bot commands:

```
start - Начать работу с ботом
help - Показать справку
status - Проверить статус подписки
```

### 9.2 Configure Bot Description
Set bot description in BotFather:
```
HackReality - Психологическая практика для достижения целей. Помогаю изменить мышление и достичь мечты через пошаговые стратегии и регулярную поддержку.
```

## 🚨 Step 10: Troubleshooting

### Common Issues

#### Bot Not Starting
```bash
# Check service status
sudo systemctl status hackreality-bot

# Check logs
sudo journalctl -u hackreality-bot -f

# Check bot logs
tail -f /home/hackreality/TelegramBot/logs/bot.log
```

#### Database Issues
```bash
# Check database integrity
sqlite3 /home/hackreality/TelegramBot/bot_database.db "PRAGMA integrity_check;"

# Backup and recreate if needed
cp bot_database.db bot_database.db.backup
```

#### Memory Issues
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Restart service if needed
sudo systemctl restart hackreality-bot
```

### Log Locations
- **Service logs**: `sudo journalctl -u hackreality-bot`
- **Application logs**: `/home/hackreality/TelegramBot/logs/bot.log`
- **System logs**: `/var/log/syslog`

## 📞 Support

### Emergency Contacts
- **Admin Telegram**: @dapavl
- **Bot Issues**: Check logs first, then contact admin
- **Server Issues**: Check system resources and service status

### Useful Commands
```bash
# Restart bot
sudo systemctl restart hackreality-bot

# Check bot status
sudo systemctl status hackreality-bot

# View recent logs
sudo journalctl -u hackreality-bot --since "1 hour ago"

# Check disk space
df -h

# Check memory
free -h

# Check running processes
ps aux | grep python
```

## ✅ Deployment Checklist

- [ ] Server setup completed
- [ ] Bot installed and configured
- [ ] Environment variables set
- [ ] Tests passing
- [ ] Systemd service created and running
- [ ] Log rotation configured
- [ ] Monitoring setup
- [ ] Backup system configured
- [ ] Bot commands set in BotFather
- [ ] Security measures implemented
- [ ] Documentation updated

## 🎉 Congratulations!

Your HackReality bot is now deployed and ready to help users achieve their goals! 

**Next Steps:**
1. Test the bot with a few users
2. Monitor logs and performance
3. Set up additional monitoring if needed
4. Plan for scaling as user base grows

**Remember to:**
- Keep the bot updated
- Monitor system resources
- Backup data regularly
- Respond to user feedback
- Maintain security best practices
