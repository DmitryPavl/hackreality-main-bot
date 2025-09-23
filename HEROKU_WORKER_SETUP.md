# 🔧 Heroku Worker Setup Guide

## 🚨 Problem: Can't Set Workers

If you can't set workers on Heroku, here are the solutions:

## ✅ Solution 1: Web Interface (Easiest)

### Step 1: Go to Your App Dashboard
1. Go to [dashboard.heroku.com](https://dashboard.heroku.com)
2. Click on your app (either `hackreality-bot-main` or `hackreality-bot-admin`)

### Step 2: Navigate to Resources
1. Click the **"Resources"** tab
2. You should see a section called **"Formation"**

### Step 3: Configure Worker Dyno
1. Under **"Formation"**, you should see:
   - `web` dyno (if it exists)
   - `worker` dyno (this is what you need)

2. If you don't see a `worker` dyno:
   - Click **"Edit"** button
   - Add a new dyno type: `worker`
   - Set the command: `python heroku_main.py` (for main bot) or `python heroku_admin.py` (for admin bot)
   - Click **"Save"**

### Step 4: Scale the Worker
1. Find the `worker` dyno in the list
2. Click the **pencil icon** (edit)
3. Set **Quantity:** `1`
4. Set **Size:** `Eco` ($5/month)
5. Click **"Confirm"**

### Step 5: Turn Off Web Dyno (if exists)
1. If you see a `web` dyno, click the pencil icon
2. Set **Quantity:** `0`
3. Click **"Confirm"**

## ✅ Solution 2: Heroku CLI (If you have it)

```bash
# Scale worker dyno
heroku ps:scale worker=1 --app your-app-name

# Check dyno status
heroku ps --app your-app-name

# View logs
heroku logs --tail --app your-app-name
```

## ✅ Solution 3: Fix Procfile Issues

### Check Your Procfile
Your Procfile should contain:
```
worker: python heroku_main.py
```

### If Procfile is Wrong:
1. Go to your app dashboard
2. Click **"Settings"** tab
3. Click **"Reveal Config Vars"**
4. Add a new config var:
   - **Key:** `PROCFILE`
   - **Value:** `worker: python heroku_main.py`

## 🔍 Troubleshooting

### Problem 1: No Worker Dyno Available
**Solution:** Add it manually in Resources → Formation → Edit

### Problem 2: Worker Dyno Exists But Won't Start
**Solution:** Check logs:
1. Go to **"More"** → **"View logs"**
2. Look for error messages
3. Common issues:
   - Missing environment variables
   - Wrong Python version
   - Import errors

### Problem 3: Worker Dyno Crashes
**Solution:** Check your code:
1. Make sure `heroku_main.py` and `heroku_admin.py` exist
2. Check that all dependencies are in `requirements.txt`
3. Verify environment variables are set

### Problem 4: Can't Edit Dyno
**Solution:** Try these steps:
1. Refresh the page
2. Log out and log back in
3. Try a different browser
4. Use Heroku CLI if available

## 📋 Step-by-Step for Each App

### Main Bot App (`hackreality-bot-main`)

1. **Go to app dashboard**
2. **Resources tab**
3. **Formation section**
4. **Edit button**
5. **Add worker dyno:**
   - Type: `worker`
   - Command: `python heroku_main.py`
6. **Save**
7. **Scale worker:**
   - Quantity: `1`
   - Size: `Eco`
8. **Confirm**

### Admin Bot App (`hackreality-bot-admin`)

1. **Go to app dashboard**
2. **Resources tab**
3. **Formation section**
4. **Edit button**
5. **Add worker dyno:**
   - Type: `worker`
   - Command: `python heroku_admin.py`
6. **Save**
7. **Scale worker:**
   - Quantity: `1`
   - Size: `Eco`
8. **Confirm**

## 🔧 Alternative: Use Web Dyno

If you can't set worker dynos, you can use web dynos instead:

### Step 1: Update Procfile
Change your Procfile to:
```
web: python heroku_main.py
```

### Step 2: Scale Web Dyno
1. Go to Resources tab
2. Find `web` dyno
3. Set Quantity: `1`
4. Set Size: `Eco`

### Step 3: Deploy Changes
1. Go to Deploy tab
2. Click "Deploy branch"

## 📊 Verify It's Working

### Check Dyno Status
1. Go to Resources tab
2. Worker dyno should show:
   - Status: `Active`
   - Uptime: Running time
   - Size: `Eco`

### Check Logs
1. Go to More → View logs
2. You should see:
   ```
   Starting HackReality Bot...
   Bot is running and polling...
   ```

### Test Your Bot
1. Message @HackRealityBot
2. Send `/start`
3. Should receive welcome message

## 💰 Cost Check

### Eco Plan Details
- **Cost:** $5/month per dyno
- **Hours:** 550-1000 per month
- **Sleep:** After 30 minutes of inactivity

### Total Cost
- **Main Bot:** $5/month
- **Admin Bot:** $5/month
- **Total:** $10/month

## 🆘 Still Having Issues?

### Contact Heroku Support
1. Go to [help.heroku.com](https://help.heroku.com)
2. Submit a support ticket
3. Mention: "Cannot scale worker dynos"

### Alternative: Use Different Hosting
If Heroku continues to have issues:
- **Railway:** Similar to Heroku
- **Render:** Free tier available
- **DigitalOcean:** $5/month droplet

## 🎯 Quick Fix Checklist

- [ ] Go to Resources tab
- [ ] Click Edit in Formation
- [ ] Add worker dyno with correct command
- [ ] Scale worker to 1 Eco
- [ ] Turn off web dyno (if exists)
- [ ] Check logs for errors
- [ ] Test bot functionality

## 🎉 Success!

Once workers are running, your bots will be:
- ✅ Always online
- ✅ Responding to messages
- ✅ Processing user requests
- ✅ Sending admin notifications

**Your HackReality bot will be live and helping users achieve their goals!** 🌟
