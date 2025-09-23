# 🚀 Heroku Deployment Guide

## 🆓 **Heroku Free Tier (Discontinued but Eco Plan Available)**

**Note:** Heroku discontinued their free tier in November 2022, but they offer an **Eco plan** starting at **$5/month** per dyno, which is still very affordable.

## 📋 **Prerequisites**

### **What You Need:**
- Heroku account (heroku.com)
- Git installed on your computer
- Heroku CLI installed
- Your bot tokens ready

### **Cost:**
- **Eco Plan:** $5/month per dyno
- **Total:** $10/month for both bots (main + admin)
- **Alternative:** Deploy only main bot for $5/month

## 🔧 **Setup Process**

### **Step 1: Install Heroku CLI**

**macOS:**
```bash
brew tap heroku/brew && brew install heroku
```

**Windows:**
Download from [devcenter.heroku.com](https://devcenter.heroku.com/articles/heroku-cli)

**Linux:**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

### **Step 2: Login to Heroku**
```bash
heroku login
```

### **Step 3: Create Git Repository**
```bash
cd /Users/dmitrypavlyuchenkov/TelegramBot
git init
git add .
git commit -m "Initial HackReality bot deployment"
```

### **Step 4: Create Heroku Apps**

**Main Bot App:**
```bash
heroku create hackreality-bot-main
```

**Admin Bot App:**
```bash
heroku create hackreality-bot-admin
```

### **Step 5: Set Environment Variables**

**For Main Bot:**
```bash
heroku config:set TELEGRAM_BOT_TOKEN=5598756315:AAEn-zTSdHL3H88DoxTI1sVP28x38h0ltbc --app hackreality-bot-main
heroku config:set ADMIN_BOT_TOKEN=8185697878:AAEQTzsCj_q0AIoBS90AQUDg6AAX6GDkaEQ --app hackreality-bot-main
heroku config:set ADMIN_USER_ID=41107472 --app hackreality-bot-main
heroku config:set ADMIN_TELEGRAM_ID=41107472 --app hackreality-bot-main
```

**For Admin Bot:**
```bash
heroku config:set TELEGRAM_BOT_TOKEN=5598756315:AAEn-zTSdHL3H88DoxTI1sVP28x38h0ltbc --app hackreality-bot-admin
heroku config:set ADMIN_BOT_TOKEN=8185697878:AAEQTzsCj_q0AIoBS90AQUDg6AAX6GDkaEQ --app hackreality-bot-admin
heroku config:set ADMIN_USER_ID=41107472 --app hackreality-bot-admin
heroku config:set ADMIN_TELEGRAM_ID=41107472 --app hackreality-bot-admin
```

### **Step 6: Deploy Main Bot**
```bash
# Copy Procfile for main bot
cp Procfile Procfile.backup

# Deploy main bot
git add .
git commit -m "Deploy main bot"
git push heroku main --app hackreality-bot-main

# Scale the worker
heroku ps:scale worker=1 --app hackreality-bot-main
```

### **Step 7: Deploy Admin Bot**
```bash
# Switch to admin bot Procfile
cp Procfile.admin Procfile

# Deploy admin bot
git add .
git commit -m "Deploy admin bot"
git push heroku main --app hackreality-bot-admin

# Scale the worker
heroku ps:scale worker=1 --app hackreality-bot-admin
```

## 📊 **Monitor Your Bots**

### **Check Status:**
```bash
# Main bot
heroku ps --app hackreality-bot-main

# Admin bot
heroku ps --app hackreality-bot-admin
```

### **View Logs:**
```bash
# Main bot logs
heroku logs --tail --app hackreality-bot-main

# Admin bot logs
heroku logs --tail --app hackreality-bot-admin
```

### **Restart Bots:**
```bash
# Restart main bot
heroku ps:restart --app hackreality-bot-main

# Restart admin bot
heroku ps:restart --app hackreality-bot-admin
```

## 💰 **Cost Management**

### **Eco Plan Details:**
- **Price:** $5/month per dyno
- **Usage:** 550-1000 dyno hours per month
- **Sleep:** Dynos sleep after 30 minutes of inactivity
- **Wake up:** Automatic wake-up when receiving requests

### **Cost Optimization:**
1. **Deploy only main bot** ($5/month) - Admin notifications will still work
2. **Use webhook instead of polling** (more efficient)
3. **Monitor usage** in Heroku dashboard

## 🔄 **Updates and Maintenance**

### **Update Bot Code:**
```bash
git add .
git commit -m "Update bot code"
git push heroku main --app hackreality-bot-main
git push heroku main --app hackreality-bot-admin
```

### **Update Environment Variables:**
```bash
heroku config:set VARIABLE_NAME=new_value --app hackreality-bot-main
```

## 🧪 **Test Your Deployment**

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
2. Check if admin receives notification
3. Should come from @hackrealityadminbot

## 🚨 **Troubleshooting**

### **Bot Not Responding:**
```bash
# Check logs
heroku logs --tail --app hackreality-bot-main

# Check if dyno is running
heroku ps --app hackreality-bot-main

# Restart dyno
heroku ps:restart --app hackreality-bot-main
```

### **Environment Variables:**
```bash
# List all config vars
heroku config --app hackreality-bot-main

# Set missing variable
heroku config:set VARIABLE_NAME=value --app hackreality-bot-main
```

### **Database Issues:**
Heroku uses ephemeral filesystem, so SQLite files are reset on each restart. Consider:
1. Using Heroku Postgres (free tier available)
2. External database service
3. File-based storage for development only

## 🎯 **Quick Start Commands**

```bash
# 1. Install Heroku CLI and login
heroku login

# 2. Initialize git and create apps
git init
git add .
git commit -m "Initial commit"
heroku create hackreality-bot-main
heroku create hackreality-bot-admin

# 3. Set environment variables (use your actual tokens)
heroku config:set TELEGRAM_BOT_TOKEN=your_token --app hackreality-bot-main
heroku config:set ADMIN_BOT_TOKEN=your_token --app hackreality-bot-main
heroku config:set ADMIN_USER_ID=your_id --app hackreality-bot-main
heroku config:set ADMIN_TELEGRAM_ID=your_id --app hackreality-bot-main

# 4. Deploy main bot
git push heroku main --app hackreality-bot-main
heroku ps:scale worker=1 --app hackreality-bot-main

# 5. Deploy admin bot
cp Procfile.admin Procfile
git add .
git commit -m "Deploy admin bot"
git push heroku main --app hackreality-bot-admin
heroku ps:scale worker=1 --app hackreality-bot-admin
```

## 🎉 **Benefits of Heroku**

✅ **No server management**
✅ **Automatic scaling**
✅ **Easy deployment**
✅ **Built-in monitoring**
✅ **Automatic restarts**
✅ **Environment variable management**
✅ **Git-based deployment**
✅ **Professional platform**

## 💡 **Alternative: Single Bot Deployment**

If you want to save costs, you can deploy only the main bot and the admin notifications will still work:

```bash
# Deploy only main bot
heroku create hackreality-bot
heroku config:set TELEGRAM_BOT_TOKEN=your_token --app hackreality-bot
heroku config:set ADMIN_BOT_TOKEN=your_token --app hackreality-bot
heroku config:set ADMIN_USER_ID=your_id --app hackreality-bot
heroku config:set ADMIN_TELEGRAM_ID=your_id --app hackreality-bot
git push heroku main --app hackreality-bot
heroku ps:scale worker=1 --app hackreality-bot
```

**Cost:** $5/month instead of $10/month

Your HackReality bot will be running smoothly on Heroku! 🚀
