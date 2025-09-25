# 🚀 Bot Deployment Guide

## Current Status
- ✅ **Code is working** - Bot has been reverted to stable state
- ✅ **Tests are passing** - 18/18 core tests passing
- ❌ **Deployment failed** - GitHub Actions deployment to Heroku failed
- ❌ **Bots are offline** - Both main bot and admin bot are not responding

## Issue Analysis
The deployment failures are likely due to missing environment variables on Heroku. The bots need the following environment variables to function:

### Main Bot (hackreality-main-bot)
```
TELEGRAM_BOT_TOKEN=your_main_bot_token_here
ADMIN_BOT_TOKEN=your_admin_bot_token_here
ADMIN_USER_ID=41107472
```

### Admin Bot (hackreality-admin-bot)
```
ADMIN_BOT_TOKEN=your_admin_bot_token_here
MAIN_BOT_TOKEN=your_main_bot_token_here
ADMIN_USER_ID=41107472
```

## Deployment Steps

### 1. Set Environment Variables on Heroku

#### For Main Bot:
```bash
heroku config:set TELEGRAM_BOT_TOKEN=your_main_bot_token_here --app hackreality-main-bot
heroku config:set ADMIN_BOT_TOKEN=your_admin_bot_token_here --app hackreality-main-bot
heroku config:set ADMIN_USER_ID=41107472 --app hackreality-main-bot
```

#### For Admin Bot:
```bash
heroku config:set ADMIN_BOT_TOKEN=your_admin_bot_token_here --app hackreality-admin-bot
heroku config:set MAIN_BOT_TOKEN=your_main_bot_token_here --app hackreality-admin-bot
heroku config:set ADMIN_USER_ID=41107472 --app hackreality-admin-bot
```

### 2. Redeploy

After setting environment variables, the bots should automatically redeploy via GitHub Actions. If not, you can manually trigger deployment:

```bash
# For main bot
git push origin main

# For admin bot
cd ../HackReality-AdminBot
git push origin main
```

### 3. Verify Deployment

Run the deployment checker:
```bash
python3 check_deployment.py
```

## Expected Results
- ✅ GitHub Actions: completed - success
- ✅ Heroku App: Online
- ✅ Bot responds to /start command
- ✅ Onboarding flow works correctly

## Troubleshooting

### If deployment still fails:
1. Check Heroku logs: `heroku logs --tail --app hackreality-main-bot`
2. Verify environment variables: `heroku config --app hackreality-main-bot`
3. Check GitHub Actions logs for specific error messages

### If bot doesn't respond:
1. Verify bot token is correct and active
2. Check that bot is not blocked by Telegram
3. Ensure all required environment variables are set

## Current Working State
The bot code is now in a stable, working state (commit 1ac2172) with:
- ✅ Working onboarding flow
- ✅ Proper message handling
- ✅ Stable database operations
- ✅ Passing automated tests
- ✅ Background test monitoring

Once environment variables are set, the bots should work correctly.
