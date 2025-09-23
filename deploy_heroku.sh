#!/bin/bash
# Heroku Deployment Script for HackReality Bot

echo "🚀 Heroku Deployment for HackReality Bot"
echo "========================================"

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Please install it first:"
    echo "   macOS: brew install heroku/brew/heroku"
    echo "   Windows: Download from https://devcenter.heroku.com/articles/heroku-cli"
    echo "   Linux: curl https://cli-assets.heroku.com/install.sh | sh"
    exit 1
fi

# Check if logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo "🔐 Please login to Heroku first:"
    echo "   heroku login"
    exit 1
fi

echo "✅ Heroku CLI ready"
echo ""

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial HackReality bot deployment"
fi

# Get app names
read -p "Enter name for main bot app (or press Enter for 'hackreality-bot-main'): " MAIN_APP
MAIN_APP=${MAIN_APP:-hackreality-bot-main}

read -p "Enter name for admin bot app (or press Enter for 'hackreality-bot-admin'): " ADMIN_APP
ADMIN_APP=${ADMIN_APP:-hackreality-bot-admin}

echo ""
echo "📱 Main bot app: $MAIN_APP"
echo "👨‍💼 Admin bot app: $ADMIN_APP"
echo ""

# Create Heroku apps
echo "🏗️ Creating Heroku apps..."
heroku create $MAIN_APP
heroku create $ADMIN_APP

echo ""
echo "⚙️ Setting up environment variables..."
echo "Please enter your bot tokens:"

read -p "Main Bot Token: " MAIN_TOKEN
read -p "Admin Bot Token: " ADMIN_TOKEN
read -p "Your Telegram User ID: " USER_ID

# Set environment variables for main bot
echo "🔧 Configuring main bot..."
heroku config:set TELEGRAM_BOT_TOKEN=$MAIN_TOKEN --app $MAIN_APP
heroku config:set ADMIN_BOT_TOKEN=$ADMIN_TOKEN --app $MAIN_APP
heroku config:set ADMIN_USER_ID=$USER_ID --app $MAIN_APP
heroku config:set ADMIN_TELEGRAM_ID=$USER_ID --app $MAIN_APP

# Set environment variables for admin bot
echo "🔧 Configuring admin bot..."
heroku config:set TELEGRAM_BOT_TOKEN=$MAIN_TOKEN --app $ADMIN_APP
heroku config:set ADMIN_BOT_TOKEN=$ADMIN_TOKEN --app $ADMIN_APP
heroku config:set ADMIN_USER_ID=$USER_ID --app $ADMIN_APP
heroku config:set ADMIN_TELEGRAM_ID=$USER_ID --app $ADMIN_APP

# Deploy main bot
echo ""
echo "📤 Deploying main bot..."
git add .
git commit -m "Deploy main bot to Heroku"
git push heroku main --app $MAIN_APP

# Scale main bot
heroku ps:scale worker=1 --app $MAIN_APP

# Deploy admin bot
echo ""
echo "📤 Deploying admin bot..."
cp Procfile.admin Procfile
git add .
git commit -m "Deploy admin bot to Heroku"
git push heroku main --app $ADMIN_APP

# Scale admin bot
heroku ps:scale worker=1 --app $ADMIN_APP

echo ""
echo "🎉 Deployment completed!"
echo ""
echo "📊 Check your bots:"
echo "Main bot: https://dashboard.heroku.com/apps/$MAIN_APP"
echo "Admin bot: https://dashboard.heroku.com/apps/$ADMIN_APP"
echo ""
echo "📱 Test your bots:"
echo "1. Message @HackRealityBot (main bot)"
echo "2. Message @hackrealityadminbot (admin bot)"
echo ""
echo "📋 Useful commands:"
echo "View logs: heroku logs --tail --app $MAIN_APP"
echo "Restart: heroku ps:restart --app $MAIN_APP"
echo "Status: heroku ps --app $MAIN_APP"
echo ""
echo "💰 Cost: $5/month per app ($10/month total)"
echo "💡 Tip: You can deploy only the main bot to save $5/month"
echo ""
echo "🚀 Your HackReality bot is now running on Heroku!"
