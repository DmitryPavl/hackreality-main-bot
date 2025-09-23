# 🌐 Heroku Web Deployment Guide

## Deploy Your Bot Directly from Heroku Website

No CLI installation needed! You can deploy your bot entirely through the Heroku web interface.

## Step 1: Prepare Your Code

### Create a GitHub Repository

**Option A: Using GitHub Desktop (Easiest)**
1. Download GitHub Desktop from [desktop.github.com](https://desktop.github.com)
2. Install and create a GitHub account
3. Create a new repository called `hackreality-bot`
4. Add all your bot files to the repository
5. Commit and push to GitHub

**Option B: Using Git Commands**
```bash
cd /Users/dmitrypavlyuchenkov/TelegramBot
git init
git add .
git commit -m "Initial HackReality bot"
# Create repository on GitHub.com and push
git remote add origin https://github.com/yourusername/hackreality-bot.git
git push -u origin main
```

## Step 2: Create Heroku Apps

### Go to Heroku Dashboard
1. Visit [heroku.com](https://heroku.com)
2. Sign up or login
3. Click "New" → "Create new app"

### Create Main Bot App
1. **App name:** `hackreality-bot-main` (or any unique name)
2. **Region:** United States
3. **Runtime stack:** Heroku-20 or Heroku-22
4. Click "Create app"

### Create Admin Bot App
1. **App name:** `hackreality-bot-admin` (or any unique name)
2. **Region:** United States
3. **Runtime stack:** Heroku-20 or Heroku-22
4. Click "Create app"

## Step 3: Connect GitHub Repository

### For Each App:
1. Go to the "Deploy" tab
2. Under "Deployment method", select "GitHub"
3. Connect your GitHub account
4. Search for your repository: `hackreality-bot`
5. Click "Connect"

## Step 4: Set Environment Variables

### For Main Bot App:
1. Go to "Settings" tab
2. Click "Reveal Config Vars"
3. Add these variables:

| Key | Value |
|-----|-------|
| `TELEGRAM_BOT_TOKEN` | `5598756315:AAEn-zTSdHL3H88DoxTI1sVP28x38h0ltbc` |
| `ADMIN_BOT_TOKEN` | `8185697878:AAEQTzsCj_q0AIoBS90AQUDg6AAX6GDkaEQ` |
| `ADMIN_USER_ID` | `41107472` |
| `ADMIN_TELEGRAM_ID` | `41107472` |

### For Admin Bot App:
1. Go to "Settings" tab
2. Click "Reveal Config Vars"
3. Add the same variables as above

## Step 5: Deploy Main Bot

### Configure Main Bot:
1. Go to your main bot app
2. Go to "Deploy" tab
3. Under "Manual deploy", select branch `main`
4. Click "Deploy branch"

### Set Procfile:
1. Go to "Resources" tab
2. Under "Formation", you should see a `worker` dyno
3. If not, click "Edit" and add a worker dyno
4. The Procfile should automatically be detected

## Step 6: Deploy Admin Bot

### Configure Admin Bot:
1. Go to your admin bot app
2. Go to "Deploy" tab
3. Under "Manual deploy", select branch `main`
4. Click "Deploy branch"

### Update Procfile for Admin Bot:
Since both bots are in the same repository, you need to modify the deployment:

1. Go to "Resources" tab
2. Under "Formation", click "Edit"
3. Change the command from `worker: python heroku_main.py` to `worker: python heroku_admin.py`
4. Save changes

## Step 7: Scale Your Apps

### For Each App:
1. Go to "Resources" tab
2. Under "Formation", find the `worker` dyno
3. Click the pencil icon to edit
4. Set quantity to `1`
5. Set size to `Eco` ($5/month)
6. Click "Confirm"

## Step 8: Monitor Your Apps

### Check Logs:
1. Go to "More" → "View logs"
2. You should see your bot starting up
3. Look for "Starting HackReality Bot" messages

### Check Status:
1. Go to "Overview" tab
2. Your dyno should show as "Active"

## Step 9: Test Your Bots

### Test Main Bot:
1. Message @HackRealityBot in Telegram
2. Send `/start` command
3. Should receive welcome message

### Test Admin Bot:
1. Message @hackrealityadminbot in Telegram
2. Send `/admin_stats` command
3. Should receive bot statistics

## Troubleshooting

### If Deployment Fails:
1. Check the logs: "More" → "View logs"
2. Look for error messages
3. Common issues:
   - Missing environment variables
   - Wrong Procfile
   - Python version issues

### If Bot Doesn't Respond:
1. Check if dyno is running: "Resources" tab
2. Restart the dyno: "More" → "Restart all dynos"
3. Check logs for errors

### Environment Variables Not Working:
1. Go to "Settings" → "Config Vars"
2. Make sure all variables are set correctly
3. Redeploy after changing variables

## Cost Management

### Eco Plan Details:
- **$5/month per dyno**
- **550-1000 dyno hours per month**
- **Dynos sleep after 30 minutes of inactivity**

### To Save Money:
1. Deploy only the main bot ($5/month)
2. Admin notifications will still work through the main bot
3. You can add the admin bot later if needed

## Automatic Deployments

### Enable Auto-Deploy:
1. Go to "Deploy" tab
2. Under "Automatic deploys", select "Enable Automatic Deploys"
3. Choose the branch (usually `main`)
4. Now every push to GitHub will automatically deploy

## 🎉 Success!

Your HackReality bot is now running on Heroku!

### Your Apps:
- **Main Bot:** https://dashboard.heroku.com/apps/hackreality-bot-main
- **Admin Bot:** https://dashboard.heroku.com/apps/hackreality-bot-admin

### Cost:
- **$10/month total** ($5 per app)
- **Alternative:** Deploy only main bot for $5/month

### Benefits:
✅ No CLI installation needed
✅ Web-based management
✅ Automatic deployments
✅ Built-in monitoring
✅ Professional platform
✅ No event loop conflicts
