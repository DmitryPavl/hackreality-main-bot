# 🧪 How to Test Your Bots on Heroku

## ✅ Method 1: Check Heroku Logs (Most Important)

### Step 1: View Live Logs
1. **Go to your Heroku app dashboard**
2. **Click "More" → "View logs"**
3. **You should see:**

**For Main Bot:**
```
Starting HackReality Bot...
Bot is running and polling...
```

**For Admin Bot:**
```
Starting Complete Admin Bot...
Admin bot is running and polling...
```

### Step 2: Check for Errors
Look for any error messages like:
- `ConnectionError`
- `Unauthorized`
- `ModuleNotFoundError`
- `ImportError`

## ✅ Method 2: Check Dyno Status

### Step 1: Go to Resources Tab
1. **Click "Resources" tab**
2. **Check worker dyno status:**
   - **Status:** Should show "Active" or "Running"
   - **Uptime:** Should show how long it's been running
   - **Size:** Should show "Eco"

### Step 2: Verify Scaling
- **Quantity:** Should be `1`
- **Size:** Should be `Eco` ($5/month)
- **Type:** Should be `worker`

## ✅ Method 3: Test Bot Functionality

### Test Main Bot (@HackRealityBot)
1. **Open Telegram**
2. **Search for:** `@HackRealityBot`
3. **Send message:** `/start`
4. **Expected response:** Welcome message in Russian

### Test Admin Bot (@hackrealityadminbot)
1. **Open Telegram**
2. **Search for:** `@hackrealityadminbot`
3. **Send message:** `/admin_stats`
4. **Expected response:** Bot statistics

## ✅ Method 4: Check Environment Variables

### Step 1: Go to Settings
1. **Click "Settings" tab**
2. **Click "Reveal Config Vars"**
3. **Verify these variables exist:**

**Required Variables:**
- `TELEGRAM_BOT_TOKEN` = `5598756315:AAEn-zTSdHL3H88DoxTI1sVP28x38h0ltbc`
- `ADMIN_BOT_TOKEN` = `8185697878:AAEQTzsCj_q0AIoBS90AQUDg6AAX6GDkaEQ`
- `ADMIN_USER_ID` = `41107472`
- `ADMIN_TELEGRAM_ID` = `41107472`

## ✅ Method 5: Check Deployment Status

### Step 1: Go to Deploy Tab
1. **Click "Deploy" tab**
2. **Check "Deploy log"**
3. **Look for successful deployment:**

**Success indicators:**
```
-----> Python app detected
-----> Installing python-3.9.18
-----> Installing pip
-----> Installing dependencies from requirements.txt
-----> Detected Procfile
-----> Released v1
-----> Deployed to Heroku
```

## 🔍 Troubleshooting Common Issues

### Issue 1: Bot Not Responding
**Check:**
- Dyno is running (Resources tab)
- No errors in logs
- Correct bot token in environment variables

### Issue 2: "Bot was blocked by the user"
**Solution:**
- Unblock the bot in Telegram
- Start a new conversation

### Issue 3: "Unauthorized" Error
**Solution:**
- Check bot token is correct
- Verify token in environment variables

### Issue 4: Dyno Crashes
**Check logs for:**
- Missing dependencies
- Import errors
- Database connection issues

## 📊 Health Check Commands

### For Main Bot
Send these commands to @HackRealityBot:
- `/start` - Should start onboarding
- `/help` - Should show help message

### For Admin Bot
Send these commands to @hackrealityadminbot:
- `/admin_stats` - Should show statistics
- `/admin_health` - Should show health status
- `/admin_security` - Should show security report

## 🚨 Warning Signs

### Red Flags to Watch For:
- Dyno shows "Crashed" status
- Logs show repeated errors
- Bot doesn't respond to `/start`
- Deployment fails repeatedly

### Green Flags (Everything Working):
- Dyno shows "Active" status
- Logs show "Bot is running and polling"
- Bot responds to commands
- No error messages in logs

## 📱 Real User Testing

### Test Complete Flow:
1. **Start conversation** with @HackRealityBot
2. **Send `/start`** - Should begin onboarding
3. **Follow onboarding** - Should collect name, age, city
4. **Choose plan** - Should show 3 options
5. **Test admin notifications** - Check if admin bot receives notifications

## 🔧 Quick Health Check

### 30-Second Test:
1. **Check dyno status** (Resources tab)
2. **Check logs** (More → View logs)
3. **Test bot response** (Send `/start` to @HackRealityBot)
4. **Test admin bot** (Send `/admin_stats` to @hackrealityadminbot)

## 🎯 Success Criteria

Your bots are working correctly if:
- ✅ Dynos are "Active"
- ✅ Logs show "Bot is running and polling"
- ✅ Main bot responds to `/start`
- ✅ Admin bot responds to `/admin_stats`
- ✅ No error messages in logs
- ✅ Environment variables are set correctly

## 🆘 Still Having Issues?

### Check These:
1. **Bot tokens** - Make sure they're correct
2. **Environment variables** - All required vars are set
3. **Dyno scaling** - Worker dyno is scaled to 1
4. **Buildpack** - Python buildpack is selected
5. **Procfile** - Contains correct worker command

### Get Help:
- Check Heroku logs for specific errors
- Verify bot tokens with @BotFather
- Test bot tokens locally first

## 🎉 Success!

If all checks pass, your HackReality bot is live and ready to help users achieve their goals! 🌟
