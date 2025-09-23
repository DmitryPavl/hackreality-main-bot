#!/bin/bash

# HackReality Bots Startup Script
# Starts both main bot and admin bot

echo "🚀 Starting HackReality Bots..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please configure your tokens first."
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

echo "✅ Environment ready"

# Function to start a bot
start_bot() {
    local bot_name=$1
    local bot_file=$2
    local log_file="logs/${bot_name}.log"
    
    echo "🤖 Starting $bot_name..."
    
    # Check if bot is already running
    if pgrep -f "$bot_file" > /dev/null; then
        echo "⚠️  $bot_name is already running"
        return 1
    fi
    
    # Start bot in background
    nohup python "$bot_file" > "$log_file" 2>&1 &
    local pid=$!
    
    # Wait a moment and check if it started successfully
    sleep 2
    if kill -0 $pid 2>/dev/null; then
        echo "✅ $bot_name started successfully (PID: $pid)"
        echo "$pid" > "logs/${bot_name}.pid"
        return 0
    else
        echo "❌ Failed to start $bot_name"
        return 1
    fi
}

# Function to stop a bot
stop_bot() {
    local bot_name=$1
    local pid_file="logs/${bot_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            echo "🛑 Stopping $bot_name (PID: $pid)..."
            kill $pid
            rm "$pid_file"
            echo "✅ $bot_name stopped"
        else
            echo "⚠️  $bot_name process not found"
            rm "$pid_file"
        fi
    else
        echo "⚠️  No PID file found for $bot_name"
    fi
}

# Function to show bot status
show_status() {
    echo "📊 Bot Status:"
    echo "=============="
    
    for bot in "main" "admin"; do
        local pid_file="logs/${bot}.pid"
        if [ -f "$pid_file" ]; then
            local pid=$(cat "$pid_file")
            if kill -0 $pid 2>/dev/null; then
                echo "✅ $bot bot: Running (PID: $pid)"
            else
                echo "❌ $bot bot: Not running"
                rm "$pid_file"
            fi
        else
            echo "❌ $bot bot: Not running"
        fi
    done
}

# Main script logic
case "$1" in
    "start")
        echo "🚀 Starting all bots..."
        start_bot "main" "main.py"
        start_bot "admin" "admin_bot_complete.py"
        echo "🎉 All bots started!"
        show_status
        ;;
    "stop")
        echo "🛑 Stopping all bots..."
        stop_bot "main"
        stop_bot "admin"
        echo "✅ All bots stopped!"
        ;;
    "restart")
        echo "🔄 Restarting all bots..."
        stop_bot "main"
        stop_bot "admin"
        sleep 2
        start_bot "main" "main.py"
        start_bot "admin" "admin_bot_complete.py"
        echo "🎉 All bots restarted!"
        show_status
        ;;
    "status")
        show_status
        ;;
    "logs")
        echo "📋 Recent logs:"
        echo "=============="
        if [ -f "logs/main.log" ]; then
            echo "Main Bot (last 10 lines):"
            tail -10 "logs/main.log"
            echo ""
        fi
        if [ -f "logs/admin.log" ]; then
            echo "Admin Bot (last 10 lines):"
            tail -10 "logs/admin.log"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start both bots"
        echo "  stop    - Stop both bots"
        echo "  restart - Restart both bots"
        echo "  status  - Show bot status"
        echo "  logs    - Show recent logs"
        exit 1
        ;;
esac
