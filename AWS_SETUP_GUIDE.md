# 🆓 AWS EC2 Free Tier Setup Guide

## Step 1: Create AWS Account
1. Go to [aws.amazon.com](https://aws.amazon.com)
2. Click "Create an AWS Account"
3. Fill in your details
4. Add payment method (won't be charged for free tier)

## Step 2: Launch EC2 Instance

### Navigate to EC2:
1. Sign in to AWS Console
2. Search for "EC2" in services
3. Click "Launch Instance"

### Configure Instance:
1. **Name:** `hackreality-bot`
2. **OS:** Ubuntu Server 22.04 LTS (Free tier eligible)
3. **Instance Type:** `t3.micro` (Free tier eligible)
4. **Key Pair:** Create new key pair
   - Name: `hackreality-bot-key`
   - Download the `.pem` file
   - Save it securely on your computer

### Security Group:
1. Click "Edit security group"
2. Add rules:
   - SSH (port 22) - Your IP
   - HTTP (port 80) - Anywhere (0.0.0.0/0)
   - HTTPS (port 443) - Anywhere (0.0.0.0/0)

### Launch Instance:
1. Click "Launch Instance"
2. Wait for instance to be "Running"
3. Note the **Public IPv4 address**

## Step 3: Connect to Your Server

### Make Key File Secure:
```bash
chmod 400 hackreality-bot-key.pem
```

### Connect via SSH:
```bash
ssh -i hackreality-bot-key.pem ubuntu@YOUR_PUBLIC_IP
```

## Step 4: Deploy Your Bot

### Option A: Automated Deployment (Recommended)
From your local machine:
```bash
cd /Users/dmitrypavlyuchenkov/TelegramBot
./deploy.sh YOUR_PUBLIC_IP ubuntu
```

### Option B: Manual Setup
On the server:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv git

# Create bot directory
sudo mkdir -p /opt/hackreality-bot
sudo chown ubuntu:ubuntu /opt/hackreality-bot
cd /opt/hackreality-bot

# Upload your bot files (from local machine)
# scp -r /Users/dmitrypavlyuchenkov/TelegramBot ubuntu@YOUR_IP:/opt/hackreality-bot/

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your bot tokens
```

## Step 5: Start the Bots

### Test Run:
```bash
# Start main bot
python main.py &

# Start admin bot (in another terminal)
python admin_bot_complete.py &
```

### Production Setup (systemd):
```bash
# Create systemd services
sudo nano /etc/systemd/system/hackreality-bot.service
```

**Main Bot Service:**
```ini
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

[Install]
WantedBy=multi-user.target
```

**Admin Bot Service:**
```ini
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

[Install]
WantedBy=multi-user.target
```

**Enable and Start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable hackreality-bot
sudo systemctl enable hackreality-admin-bot
sudo systemctl start hackreality-bot
sudo systemctl start hackreality-admin-bot
```

## Step 6: Monitor Your Bots

### Check Status:
```bash
sudo systemctl status hackreality-bot
sudo systemctl status hackreality-admin-bot
```

### View Logs:
```bash
sudo journalctl -u hackreality-bot -f
sudo journalctl -u hackreality-admin-bot -f
```

## Step 7: Test Your Bots

1. **Test Main Bot:**
   - Message @HackRealityBot in Telegram
   - Send `/start` command

2. **Test Admin Bot:**
   - Message @hackrealityadminbot in Telegram
   - Send `/admin_stats` command

3. **Test Admin Notifications:**
   - Start a new user session
   - Check if admin receives notification

## Cost Monitoring

### Free Tier Limits:
- **750 hours/month** of t3.micro usage
- **30 GB** of EBS storage
- **15 GB** of bandwidth

### Monitor Usage:
1. Go to AWS Console → Billing
2. Check "Free Tier" usage
3. Set up billing alerts

## Troubleshooting

### Can't Connect via SSH:
```bash
# Check security group rules
# Ensure port 22 is open for your IP
# Verify key file permissions: chmod 400 key.pem
```

### Bot Won't Start:
```bash
# Check logs
sudo journalctl -u hackreality-bot -f

# Check Python environment
source /opt/hackreality-bot/venv/bin/activate
python --version
pip list
```

### Environment Variables:
```bash
# Verify .env file
cat /opt/hackreality-bot/.env

# Check if variables are loaded
source /opt/hackreality-bot/venv/bin/activate
python -c "import os; print(os.getenv('TELEGRAM_BOT_TOKEN'))"
```

## 🎉 Success!

Once everything is running:
- ✅ Main bot: @HackRealityBot
- ✅ Admin bot: @hackrealityadminbot  
- ✅ Admin notifications working
- ✅ 24/7 uptime
- ✅ No event loop conflicts
- ✅ FREE for 12 months!
