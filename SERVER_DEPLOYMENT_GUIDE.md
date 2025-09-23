# 🚀 Server Deployment Guide

## 📋 **Prerequisites**

### **Server Requirements:**
- Ubuntu 20.04+ or CentOS 8+ (recommended)
- Python 3.9+ 
- 1GB+ RAM
- 10GB+ storage
- Internet connection

### **Recommended Providers:**
- **DigitalOcean** - $5/month droplet
- **AWS EC2** - t3.micro instance (free tier eligible)
- **Google Cloud** - e2-micro instance (free tier eligible)
- **Linode** - $5/month nanode
- **Vultr** - $2.50/month instance

## 🔧 **Server Setup**

### **Step 1: Create Server**
1. Create a new server/instance
2. Note the IP address
3. SSH into the server

### **Step 2: Update System**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### **Step 3: Install Python**
```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip python3-venv -y

# CentOS/RHEL
sudo yum install python3 python3-pip -y
```

### **Step 4: Create User**
```bash
sudo adduser telegrambot
sudo usermod -aG sudo telegrambot
su - telegrambot
```

## 📁 **Deploy Bot Code**

### **Step 1: Upload Files**
```bash
# Option 1: Using SCP
scp -r /Users/dmitrypavlyuchenkov/TelegramBot telegrambot@YOUR_SERVER_IP:/home/telegrambot/

# Option 2: Using Git (recommended)
git init
git add .
git commit -m "Initial bot deployment"
# Push to GitHub/GitLab and clone on server
```

### **Step 2: Setup Environment**
```bash
cd TelegramBot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **Step 3: Configure Environment Variables**
```bash
cp .env.example .env
nano .env
```

**Required Environment Variables:**
```env
TELEGRAM_BOT_TOKEN=5598756315:AAEn-zTSdHL3H88DoxTI1sVP28x38h0ltbc
ADMIN_BOT_TOKEN=8185697878:AAEQTzsCj_q0AIoBS90AQUDg6AAX6GDkaEQ
ADMIN_USER_ID=41107472
ADMIN_TELEGRAM_ID=41107472
```

## 🚀 **Start the Bots**

### **Option 1: Manual Start (Testing)**
```bash
# Start main bot
python main.py &

# Start admin bot (in another terminal)
python admin_bot_complete.py &
```

### **Option 2: Using systemd (Production)**
```bash
# Create systemd service for main bot
sudo nano /etc/systemd/system/hackreality-bot.service
```

**Main Bot Service:**
```ini
[Unit]
Description=HackReality Main Bot
After=network.target

[Service]
Type=simple
User=telegrambot
WorkingDirectory=/home/telegrambot/TelegramBot
Environment=PATH=/home/telegrambot/TelegramBot/venv/bin
ExecStart=/home/telegrambot/TelegramBot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Admin Bot Service:**
```bash
sudo nano /etc/systemd/system/hackreality-admin-bot.service
```

```ini
[Unit]
Description=HackReality Admin Bot
After=network.target

[Service]
Type=simple
User=telegrambot
WorkingDirectory=/home/telegrambot/TelegramBot
Environment=PATH=/home/telegrambot/TelegramBot/venv/bin
ExecStart=/home/telegrambot/TelegramBot/venv/bin/python admin_bot_complete.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Start Services:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable hackreality-bot
sudo systemctl enable hackreality-admin-bot
sudo systemctl start hackreality-bot
sudo systemctl start hackreality-admin-bot
```

## 📊 **Monitor the Bots**

### **Check Status:**
```bash
sudo systemctl status hackreality-bot
sudo systemctl status hackreality-admin-bot
```

### **View Logs:**
```bash
sudo journalctl -u hackreality-bot -f
sudo journalctl -u hackreality-admin-bot -f
```

### **Restart Bots:**
```bash
sudo systemctl restart hackreality-bot
sudo systemctl restart hackreality-admin-bot
```

## 🔒 **Security Setup**

### **Firewall Configuration:**
```bash
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### **SSH Key Authentication:**
```bash
# On your local machine
ssh-keygen -t rsa -b 4096
ssh-copy-id telegrambot@YOUR_SERVER_IP
```

## 📱 **Test the Deployment**

### **Test Main Bot:**
1. Message @HackRealityBot in Telegram
2. Send `/start` command
3. Should receive welcome message

### **Test Admin Bot:**
1. Message @hackrealityadminbot in Telegram
2. Send `/admin_stats` command
3. Should receive bot statistics

### **Test Admin Notifications:**
1. Start a new user session with main bot
2. Check if admin receives new user notification
3. Should come from @hackrealityadminbot

## 🔄 **Updates and Maintenance**

### **Update Bot Code:**
```bash
cd /home/telegrambot/TelegramBot
git pull
sudo systemctl restart hackreality-bot
sudo systemctl restart hackreality-admin-bot
```

### **Backup Database:**
```bash
cp hackreality_bot.db hackreality_bot_backup_$(date +%Y%m%d).db
```

## 📈 **Scaling and Monitoring**

### **Add Monitoring:**
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs -y
```

### **Log Rotation:**
```bash
sudo nano /etc/logrotate.d/hackreality-bot
```

```conf
/home/telegrambot/TelegramBot/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 644 telegrambot telegrambot
}
```

## 🎯 **Quick Start Commands**

```bash
# 1. Create server and SSH in
# 2. Run these commands:

sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git -y
sudo adduser telegrambot
sudo usermod -aG sudo telegrambot
su - telegrambot

# Upload your bot code (via SCP or Git)
cd TelegramBot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your tokens

# Test the bots
python main.py &
python admin_bot_complete.py &

# If working, set up systemd services
sudo systemctl enable hackreality-bot
sudo systemctl enable hackreality-admin-bot
sudo systemctl start hackreality-bot
sudo systemctl start hackreality-admin-bot
```

## 🎉 **Benefits of Server Deployment**

✅ **No event loop conflicts**
✅ **24/7 uptime**
✅ **Professional monitoring**
✅ **Easy scaling**
✅ **Automatic restarts**
✅ **Secure environment**
✅ **Better performance**

Your bot will run smoothly on a dedicated server without any of the development environment issues!
