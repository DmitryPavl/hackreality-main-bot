#!/usr/bin/env python3
"""
Simple Admin Bot for HackReality
Lightweight admin interface for monitoring and basic management
"""

import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, filters
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SimpleAdminBot:
    def __init__(self):
        self.token = os.getenv('ADMIN_BOT_TOKEN')
        self.admin_user_id = int(os.getenv('ADMIN_USER_ID', '41107472'))
        
        if not self.token:
            raise ValueError("ADMIN_BOT_TOKEN not found in environment variables")
        
        self.application = Application.builder().token(self.token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup command and message handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback_query))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if update.effective_user.id != self.admin_user_id:
            await update.message.reply_text("❌ Access denied. This bot is for administrators only.")
            return
        
        welcome_text = """
🔧 **HackReality Admin Panel**

Welcome to the admin interface! Here you can:

📊 **Monitoring:**
• `/status` - Check bot status
• `/help` - Show available commands

🛠️ **Quick Actions:**
• Check if main bot is running
• Monitor system health
• View basic statistics

This is a lightweight admin interface for basic monitoring.
        """
        
        keyboard = [
            [InlineKeyboardButton("📊 Check Status", callback_data="check_status")],
            [InlineKeyboardButton("🔍 View Logs", callback_data="view_logs")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="show_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if update.effective_user.id != self.admin_user_id:
            return
        
        help_text = """
🔧 **Admin Bot Commands**

**📊 Monitoring:**
• `/status` - Check main bot status
• `/start` - Show admin panel

**🛠️ Features:**
• Monitor main bot health
• Check system status
• View basic logs
• Quick status updates

**💡 Usage:**
• Use buttons for quick access
• All commands are logged
• Check status regularly
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        if update.effective_user.id != self.admin_user_id:
            return
        
        status = await self._check_main_bot_status()
        
        status_text = f"""
📊 **System Status**

**Main Bot:** {status['main_bot']}
**Database:** {status['database']}
**Logs:** {status['logs']}
**Uptime:** {status['uptime']}
**Last Check:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Quick Actions:**
        """
        
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh Status", callback_data="check_status")],
            [InlineKeyboardButton("📋 View Logs", callback_data="view_logs")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            status_text, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()
        
        if query.from_user.id != self.admin_user_id:
            await query.edit_message_text("❌ Access denied.")
            return
        
        if query.data == "check_status":
            status = await self._check_main_bot_status()
            status_text = f"""
📊 **Status Update**

**Main Bot:** {status['main_bot']}
**Database:** {status['database']}
**Logs:** {status['logs']}
**Uptime:** {status['uptime']}
**Last Check:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data="check_status")],
                [InlineKeyboardButton("📋 View Logs", callback_data="view_logs")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                status_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        
        elif query.data == "view_logs":
            logs = await self._get_recent_logs()
            logs_text = f"""
📋 **Recent Logs**

{logs}

**Last 10 lines from main bot log file**
            """
            
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data="view_logs")],
                [InlineKeyboardButton("📊 Back to Status", callback_data="check_status")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                logs_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        
        elif query.data == "show_help":
            await self.help_command(update, context)
    
    async def _check_main_bot_status(self):
        """Check the status of the main bot"""
        import subprocess
        
        status = {
            'main_bot': '❌ Not Running',
            'database': '❌ Not Found',
            'logs': '❌ Not Found',
            'uptime': 'Unknown'
        }
        
        try:
            # Check if main bot process is running
            result = subprocess.run(['pgrep', '-f', 'main.py'], capture_output=True, text=True)
            if result.returncode == 0:
                status['main_bot'] = '✅ Running'
            
            # Check database file
            if os.path.exists('bot_database.db'):
                status['database'] = '✅ Connected'
            
            # Check log files
            if os.path.exists('logs/main.log'):
                status['logs'] = '✅ Available'
            
            # Get uptime if possible
            if status['main_bot'] == '✅ Running':
                status['uptime'] = 'Active'
            
        except Exception as e:
            logger.error(f"Error checking status: {e}")
        
        return status
    
    async def _get_recent_logs(self):
        """Get recent logs from main bot"""
        try:
            log_file = 'logs/main.log'
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    recent_lines = lines[-10:] if len(lines) >= 10 else lines
                    return '\n'.join(recent_lines)
            else:
                return "No log file found"
        except Exception as e:
            return f"Error reading logs: {e}"
    
    async def run(self):
        """Run the admin bot"""
        logger.info("Starting Simple Admin Bot...")
        await self.application.run_polling()

def main():
    """Main function"""
    try:
        admin_bot = SimpleAdminBot()
        
        # Check if there's already an event loop running
        try:
            loop = asyncio.get_running_loop()
            logger.warning("Event loop already running, creating new task")
            # If we're in an existing loop, we need to run this differently
            import threading
            def run_bot():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                new_loop.run_until_complete(admin_bot.run())
            
            thread = threading.Thread(target=run_bot)
            thread.daemon = True
            thread.start()
            thread.join()
        except RuntimeError:
            # No event loop running, safe to use asyncio.run
            asyncio.run(admin_bot.run())
            
    except Exception as e:
        logger.error(f"Failed to start admin bot: {e}")

if __name__ == "__main__":
    main()
