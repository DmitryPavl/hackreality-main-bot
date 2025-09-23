#!/bin/bash

# HackReality Bot Quick Start Script
# This script helps you quickly set up and run the bot

set -e

echo "🚀 HackReality Bot Quick Start"
echo "================================"

# Check if Python 3.8+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $PYTHON_VERSION is installed, but Python $REQUIRED_VERSION or higher is required."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating environment configuration..."
    cp env_example.txt .env
    echo "📝 Please edit .env file with your bot token and admin ID"
    echo "   Required: TELEGRAM_BOT_TOKEN and ADMIN_TELEGRAM_ID"
    echo ""
    echo "   To get your bot token:"
    echo "   1. Message @BotFather on Telegram"
    echo "   2. Create a new bot with /newbot"
    echo "   3. Copy the token to .env file"
    echo ""
    echo "   To get your admin chat ID:"
    echo "   1. Message @userinfobot on Telegram"
    echo "   2. Copy your chat ID to .env file"
    echo ""
    read -p "Press Enter when you've configured .env file..."
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs data backups

# Run tests
echo "🧪 Running tests..."
if python run_tests.py; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed. Please check the output above."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start the bot
echo "🚀 Starting HackReality Bot..."
echo "   Press Ctrl+C to stop the bot"
echo "   Check logs/bot.log for detailed logs"
echo ""

python main.py
