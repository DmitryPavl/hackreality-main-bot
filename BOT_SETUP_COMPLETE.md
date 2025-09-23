# 🎉 HackReality Bot Setup Complete!

## ✅ **What We've Accomplished**

### 🤖 **Two Separate Bots Created**

1. **Main Bot: @HackRealityBot**
   - Clean, user-focused bot
   - All admin functionality removed
   - Handles user onboarding, goal setting, setup, payments, and iterations
   - No conflicts with admin operations

2. **Admin Bot: @hackrealityadminbot**
   - Complete admin interface
   - All monitoring and management functions
   - Statistics, health checks, user management
   - Notifications and system control

### 🔧 **Admin Functionality Moved**

**From Main Bot → Admin Bot:**
- `/admin_stats` - Detailed bot statistics
- `/admin_health` - System health monitoring
- `/admin_security` - Security status and user blocking
- `/admin_performance` - Performance metrics
- `/admin_analytics` - Comprehensive analytics
- User management commands
- Notification and broadcast functions
- System monitoring and control

### 📁 **Files Created/Modified**

- `main.py` - Clean main bot (admin functions removed)
- `main_with_admin.py` - Backup of original main bot
- `admin_bot_complete.py` - Complete admin bot with all functionality
- `start_bots.sh` - Startup script for both bots
- `.env` - Configuration with both bot tokens

## 🚀 **How to Run the Bots**

### **Option 1: Using Startup Script**
```bash
cd /Users/dmitrypavlyuchenkov/TelegramBot
./start_bots.sh start
```

### **Option 2: Manual Start**
```bash
cd /Users/dmitrypavlyuchenkov/TelegramBot
source venv/bin/activate

# Start main bot
nohup python main.py > logs/main.log 2>&1 &

# Start admin bot (in separate terminal)
nohup python admin_bot_complete.py > logs/admin.log 2>&1 &
```

### **Bot Management Commands**
```bash
./start_bots.sh start    # Start both bots
./start_bots.sh stop     # Stop both bots
./start_bots.sh restart  # Restart both bots
./start_bots.sh status   # Check bot status
./start_bots.sh logs     # View recent logs
```

## 📱 **Bot Usage**

### **For Users: @HackRealityBot**
- Send `/start` to begin onboarding
- Complete goal setting and plan selection
- Work through setup and payment
- Receive regular task iterations

### **For Admin: @hackrealityadminbot**
- Send `/start` to access admin panel
- Use `/admin_stats` for statistics
- Use `/admin_health` for system monitoring
- Use `/notify [message]` to send notifications
- Use `/users` to manage users

## 🔑 **Configuration**

### **Environment Variables (.env)**
```
TELEGRAM_BOT_TOKEN=5598756315:AAEn-zTSdHL3H88DoxTI1sVP28x38h0ltbc
ADMIN_BOT_TOKEN=8185697878:AAEQTzsCj_q0AIoBS90AQUDg6AAX6GDkaEQ
ADMIN_USER_ID=41107472
```

### **Bot Tokens**
- **Main Bot:** @HackRealityBot
- **Admin Bot:** @hackrealityadminbot
- **Admin User ID:** 41107472

## 🛠️ **Admin Bot Commands**

### **Monitoring & Analytics**
- `/admin_stats` - Comprehensive bot statistics
- `/admin_health` - System health and performance
- `/admin_security` - Security status and blocked users
- `/admin_performance` - Performance metrics and cache stats
- `/admin_analytics` - Detailed analytics report

### **User Management**
- `/users` - List and manage users
- `/notify [message]` - Send notification to all users
- `/broadcast [message]` - Broadcast message to all active users

### **System Management**
- `/system` - System overview and resource usage
- `/logs` - View recent logs from main bot
- `/restart` - Restart main bot (if needed)

## 🎯 **Benefits of Separation**

1. **No Conflicts** - Bots run independently
2. **Better Security** - Admin functions isolated
3. **Cleaner Code** - Main bot focused on user experience
4. **Easier Management** - Admin operations don't interfere with user flow
5. **Scalability** - Can run on different servers if needed

## 🔍 **Monitoring**

### **Log Files**
- `logs/main.log` - Main bot logs
- `logs/admin.log` - Admin bot logs

### **Database**
- `bot_database.db` - SQLite database with all user data

### **Status Checking**
```bash
# Check if bots are running
ps aux | grep "python.*main.py"
ps aux | grep "python.*admin_bot_complete.py"

# View logs
tail -f logs/main.log
tail -f logs/admin.log
```

## 🎉 **Ready to Use!**

Both bots are now configured and ready to run independently. The main bot handles all user interactions, while the admin bot provides comprehensive monitoring and management capabilities.

**Next Steps:**
1. Start both bots using the startup script
2. Test user flow with @HackRealityBot
3. Test admin functions with @hackrealityadminbot
4. Monitor logs and system health

**Support:**
- Check logs if issues occur
- Use admin bot for monitoring and troubleshooting
- Both bots can be restarted independently if needed
