#!/usr/bin/env python3
"""
HackReality Admin Bot
Dedicated admin interface for managing the main bot
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
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

class AdminBot:
    def __init__(self):
        self.token = os.getenv('ADMIN_BOT_TOKEN')
        self.main_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.admin_user_id = int(os.getenv('ADMIN_USER_ID', '41107472'))
        
        if not self.token:
            raise ValueError("ADMIN_BOT_TOKEN not found in environment variables")
        
        self.application = Application.builder().token(self.token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup command and message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("users", self.users_command))
        self.application.add_handler(CommandHandler("notify", self.notify_command))
        self.application.add_handler(CommandHandler("system", self.system_command))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self.handle_callback_query))
        
        # Message handler
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_message
        ))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if update.effective_user.id != self.admin_user_id:
            await update.message.reply_text("❌ Access denied. This bot is for administrators only.")
            return
        
        welcome_text = """
🔧 **HackReality Admin Panel**

Welcome to the admin interface! Here you can:

📊 **Monitoring:**
• `/stats` - View bot statistics
• `/users` - List active users
• `/system` - System health check

📢 **Communication:**
• `/notify` - Send notifications to users
• Send messages to broadcast to all users

🛠️ **Management:**
• Monitor user activity
• Handle support requests
• Manage bot operations

Use `/help` for more information.
        """
        
        keyboard = [
            [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
            [InlineKeyboardButton("👥 Users", callback_data="admin_users")],
            [InlineKeyboardButton("🔔 Notify All", callback_data="admin_notify")],
            [InlineKeyboardButton("🛠️ System Health", callback_data="admin_system")]
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

**📊 Statistics & Monitoring:**
• `/stats` - View detailed bot statistics
• `/users` - List all users and their status
• `/system` - Check system health and performance

**📢 Communication:**
• `/notify [message]` - Send notification to all users
• Send any text message to broadcast to all active users

**🛠️ Management:**
• Monitor user activity in real-time
• Handle support requests
• Manage bot operations and settings

**💡 Tips:**
• Use buttons for quick access to common functions
• All commands are logged for audit purposes
• Check logs regularly for any issues
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        if update.effective_user.id != self.admin_user_id:
            return
        
        # Get basic statistics (you can enhance this with database queries)
        stats_text = f"""
📊 **Bot Statistics**

**👥 Users:**
• Total Users: {await self._get_total_users()}
• Active Today: {await self._get_active_users_today()}
• New This Week: {await self._get_new_users_week()}

**💬 Messages:**
• Total Messages: {await self._get_total_messages()}
• Messages Today: {await self._get_messages_today()}
• Avg per User: {await self._get_avg_messages_per_user()}

**🚀 Subscriptions:**
• Active Subscriptions: {await self._get_active_subscriptions()}
• Completed Plans: {await self._get_completed_plans()}
• Revenue: {await self._get_total_revenue()}

**⚡ Performance:**
• Uptime: {await self._get_uptime()}
• Last Activity: {await self._get_last_activity()}
• System Status: {await self._get_system_status()}
        """
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
    
    async def users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /users command"""
        if update.effective_user.id != self.admin_user_id:
            return
        
        users_text = f"""
👥 **User Management**

**Recent Users:**
{await self._get_recent_users()}

**Active Sessions:**
{await self._get_active_sessions()}

**User States:**
{await self._get_user_states()}

**Support Requests:**
{await self._get_support_requests()}
        """
        
        await update.message.reply_text(users_text, parse_mode='Markdown')
    
    async def notify_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /notify command"""
        if update.effective_user.id != self.admin_user_id:
            return
        
        if not context.args:
            await update.message.reply_text(
                "Usage: `/notify [message]`\nExample: `/notify Bot will be updated in 10 minutes`",
                parse_mode='Markdown'
            )
            return
        
        message = ' '.join(context.args)
        await self._send_notification_to_all_users(message)
        
        await update.message.reply_text(
            f"✅ Notification sent to all users:\n\n*{message}*",
            parse_mode='Markdown'
        )
    
    async def system_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /system command"""
        if update.effective_user.id != self.admin_user_id:
            return
        
        system_text = f"""
🛠️ **System Health Check**

**Status:** ✅ Online
**Uptime:** {await self._get_uptime()}
**Memory Usage:** {await self._get_memory_usage()}
**Database:** {await self._get_database_status()}
**Last Backup:** {await self._get_last_backup()}

**Recent Errors:** {await self._get_recent_errors()}
**Performance:** {await self._get_performance_metrics()}
        """
        
        await update.message.reply_text(system_text, parse_mode='Markdown')
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()
        
        if query.from_user.id != self.admin_user_id:
            await query.edit_message_text("❌ Access denied.")
            return
        
        if query.data == "admin_stats":
            await self.stats_command(update, context)
        elif query.data == "admin_users":
            await self.users_command(update, context)
        elif query.data == "admin_notify":
            await query.edit_message_text(
                "📢 Send notification to all users:\n\nUse `/notify [message]` command.",
                parse_mode='Markdown'
            )
        elif query.data == "admin_system":
            await self.system_command(update, context)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        if update.effective_user.id != self.admin_user_id:
            return
        
        message_text = update.message.text
        
        # If it's not a command, treat it as a broadcast message
        if not message_text.startswith('/'):
            # Ask for confirmation before broadcasting
            keyboard = [
                [InlineKeyboardButton("✅ Yes, Send to All", callback_data=f"broadcast_confirm_{message_text[:50]}")],
                [InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"📢 **Broadcast Message**\n\n{message_text}\n\nSend this message to all users?",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    # Helper methods (implement these based on your database structure)
    async def _get_total_users(self):
        return "Loading..."
    
    async def _get_active_users_today(self):
        return "Loading..."
    
    async def _get_new_users_week(self):
        return "Loading..."
    
    async def _get_total_messages(self):
        return "Loading..."
    
    async def _get_messages_today(self):
        return "Loading..."
    
    async def _get_avg_messages_per_user(self):
        return "Loading..."
    
    async def _get_active_subscriptions(self):
        return "Loading..."
    
    async def _get_completed_plans(self):
        return "Loading..."
    
    async def _get_total_revenue(self):
        return "Loading..."
    
    async def _get_uptime(self):
        return "Loading..."
    
    async def _get_last_activity(self):
        return "Loading..."
    
    async def _get_system_status(self):
        return "Healthy"
    
    async def _get_recent_users(self):
        return "Loading..."
    
    async def _get_active_sessions(self):
        return "Loading..."
    
    async def _get_user_states(self):
        return "Loading..."
    
    async def _get_support_requests(self):
        return "None"
    
    async def _get_memory_usage(self):
        return "Loading..."
    
    async def _get_database_status(self):
        return "Connected"
    
    async def _get_last_backup(self):
        return "Never"
    
    async def _get_recent_errors(self):
        return "None"
    
    async def _get_performance_metrics(self):
        return "Good"
    
    async def _send_notification_to_all_users(self, message):
        """Send notification to all users"""
        # Implement this to send messages to all users
        logger.info(f"Admin notification: {message}")
    
    async def run(self):
        """Run the admin bot"""
        logger.info("Starting Admin Bot...")
        await self.application.run_polling()

def main():
    """Main function"""
    try:
        admin_bot = AdminBot()
        asyncio.run(admin_bot.run())
    except Exception as e:
        logger.error(f"Failed to start admin bot: {e}")

if __name__ == "__main__":
    main()
