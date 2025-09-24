#!/usr/bin/env python3
"""
Main Telegram Bot Application
A modular Telegram bot with onboarding, options, setup, payment, and iteration modules.
"""

import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from dotenv import load_dotenv

# Import modules
from modules.onboarding import OnboardingModule
from modules.option import OptionModule
from modules.settingup import SettingUpModule
from modules.paying import PayingModule
from modules.subscription import SubscriptionModule
from modules.iteration import IterationModule
from modules.database import DatabaseManager
from modules.user_state import UserStateManager
from modules.error_handler import ErrorHandler
from modules.monitoring import MonitoringManager
from modules.security import SecurityManager
from modules.performance import PerformanceManager
from modules.ux_improvements import UXManager
from modules.analytics import AnalyticsManager
from modules.admin_notifications import admin_notifications

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        
        # Initialize modules
        self.db_manager = DatabaseManager()
        self.state_manager = UserStateManager()
        
        self.onboarding = OnboardingModule(self.db_manager, self.state_manager)
        self.option = OptionModule(self.db_manager, self.state_manager, self)
        self.settingup = SettingUpModule(self.db_manager, self.state_manager, self)
        self.paying = PayingModule(self.db_manager, self.state_manager, self)
        self.subscription = SubscriptionModule(self.db_manager, self.state_manager)
        self.iteration = IterationModule(self.db_manager, self.state_manager, self)
        self.monitoring = MonitoringManager(self.db_manager, self)
        self.security = SecurityManager()
        self.performance = PerformanceManager(self.db_manager)
        self.ux = UXManager(self.db_manager)
        self.analytics = AnalyticsManager(self.db_manager)
        
        # Initialize application
        self.application = Application.builder().token(self.token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup command and message handlers"""
        # Start command
        self.application.add_handler(CommandHandler("start", self.start_command))
        
        # Help command
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Status command
        self.application.add_handler(CommandHandler("status", self.status_command))
        
        # Message handlers for different modules
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_message
        ))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(
            self.handle_callback_query
        ))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        try:
            user_id = update.effective_user.id
            user_info = update.effective_user
            
            logger.info(f"User {user_id} ({user_info.first_name}) started the bot")
            
            # Initialize user in database
            await self.db_manager.initialize_user(
                user_id=user_id,
                username=user_info.username,
                first_name=user_info.first_name,
                last_name=user_info.last_name
            )
            
            # Send new user notification to admin
            await admin_notifications.notify_new_user(
                user_id=user_id,
                username=user_info.username or "",
                first_name=user_info.first_name or "",
                last_name=user_info.last_name or ""
            )
            
            # Store user message
            await self.db_manager.store_user_message(
                user_id=user_id,
                message_text="/start",
                message_type="command",
                module_context="start_command",
                state_context="initialization"
            )
            
            # Start onboarding process
            await self.onboarding.start_onboarding(update, context)
            
        except Exception as e:
            logger.error(f"Error in start_command for user {user_id}: {e}")
            await self._handle_critical_error(update, context, "start_command")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        try:
            user_id = update.effective_user.id
            
            help_text = """
🤖 **HackReality Bot Help**

I'm here to help you achieve your goals through structured psychological practice.

**Available Commands:**
• `/start` - Begin your journey
• `/help` - Show this help message
• `/status` - Check your current progress

**How It Works:**
1. **Onboarding** - We'll get to know you and your goals
2. **Goal Setting** - Define what you want to achieve
3. **Plan Selection** - Choose your path (Express, 2-week, or Regular)
4. **Setup** - Create personalized tasks and focus statements
5. **Execution** - Work on your goals with regular guidance

**Support:**
If you need help, just send me a message and I'll assist you.

Ready to start? Use `/start` to begin your journey! 🚀
            """
            
            await update.message.reply_text(help_text, parse_mode='Markdown')
            
            # Store bot response
            await self.db_manager.store_bot_message(
                user_id=user_id,
                message_text=help_text,
                message_type="text",
                module_context="help_command",
                state_context="help_response"
            )
            
        except Exception as e:
            logger.error(f"Error in help_command for user {user_id}: {e}")
            await self._handle_critical_error(update, context, "help_command")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        try:
            user_id = update.effective_user.id
            
            # Get user state
            user_state = await self.state_manager.get_user_state(user_id)
            
            # Get user profile
            user_profile = await self.db_manager.get_user_profile(user_id)
            
            status_text = f"""
📊 **Your Current Status**

**Profile:**
• Name: {user_profile.get('first_name', 'Unknown')} {user_profile.get('last_name', '')}
• Username: @{user_profile.get('username', 'Unknown')}
• Current State: {user_state}

**Progress:**
• Started: {user_profile.get('created_at', 'Unknown')}
• Last Activity: {user_profile.get('last_activity', 'Unknown')}

**Next Steps:**
Use `/start` to continue your journey or `/help` for assistance.
            """
            
            await update.message.reply_text(status_text, parse_mode='Markdown')
            
            # Store bot response
            await self.db_manager.store_bot_message(
                user_id=user_id,
                message_text=status_text,
                message_type="text",
                module_context="status_command",
                state_context="status_response"
            )
            
        except Exception as e:
            logger.error(f"Error in status_command for user {user_id}: {e}")
            await self._handle_critical_error(update, context, "status_command")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all text messages and route to appropriate module"""
        try:
            user_id = update.effective_user.id
            message_text = update.message.text
            
            # Check if user is blocked
            if self.security.is_user_blocked(user_id):
                await update.message.reply_text(
                    "🚫 Ваш доступ временно ограничен. Попробуйте позже.",
                    parse_mode='Markdown'
                )
                return
            
            # Check rate limits
            rate_ok, rate_message = self.security.check_rate_limit(user_id)
            if not rate_ok:
                await update.message.reply_text(
                    f"⏰ {rate_message}",
                    parse_mode='Markdown'
                )
                return
            
            # Validate message content
            content_valid, content_message = self.security.validate_message_content(message_text)
            if not content_valid:
                await update.message.reply_text(
                    "⚠️ Сообщение содержит недопустимый контент. Пожалуйста, отправьте корректное сообщение.",
                    parse_mode='Markdown'
                )
                # Log suspicious activity
                self.security.detect_suspicious_activity(
                    user_id, "invalid_content", 
                    {"message": message_text[:100], "reason": content_message}
                )
                return
            
            # Validate user input
            if not ErrorHandler.validate_user_input(message_text):
                await update.message.reply_text(
                    "Пожалуйста, отправьте корректное сообщение. Избегайте специальных символов и длинных текстов.",
                    parse_mode='Markdown'
                )
                return
            
            # Sanitize input
            sanitized_text = ErrorHandler.sanitize_input(message_text)
            
            # Store user message in database
            await self.db_manager.store_user_message(
                user_id=user_id,
                message_text=sanitized_text,
                message_type="text",
                module_context="main_handler",
                state_context="message_routing"
            )
            
            # Log user activity
            await self.monitoring.log_user_activity(
                user_id=user_id,
                activity_type="message_received",
                details={"message_length": len(sanitized_text)}
            )
            
            # Track analytics
            await self.analytics.track_user_action(
                user_id=user_id,
                action="message_sent",
                details={"message_length": len(sanitized_text), "module": "main_handler"}
            )
            
            # Get user's current state
            user_state = await self.state_manager.get_user_state(user_id)
            
            # Route message to appropriate module based on state
            if user_state == "onboarding":
                await self.onboarding.handle_message(update, context)
            elif user_state == "option_selection":
                await self.option.handle_message(update, context)
            elif user_state == "setup":
                await self.settingup.handle_message(update, context)
            elif user_state == "payment":
                await self.paying.handle_message(update, context)
            elif user_state == "active":
                await self.iteration.handle_message(update, context)
            else:
                # Default response for unknown state
                response_text = "I'm not sure what you're trying to do. Please use /start to begin or /help for assistance."
                await update.message.reply_text(response_text)
                
                # Store bot response
                await self.db_manager.store_bot_message(
                    user_id=user_id,
                    message_text=response_text,
                    message_type="text",
                    module_context="main_handler",
                    state_context="default_response"
                )
                
        except Exception as e:
            logger.error(f"Error in handle_message for user {user_id}: {e}")
            await self._handle_critical_error(update, context, "handle_message")
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        try:
            user_id = update.effective_user.id
            query = update.callback_query
            await query.answer()
            
            logger.info(f"Callback query from user {user_id}: {query.data}")
            
            # Route callback to appropriate module based on user state
            user_state = await self.state_manager.get_user_state(user_id)
            logger.info(f"User {user_id} state: {user_state}")
            
            if user_state == "onboarding":
                logger.info(f"Routing callback to onboarding module for user {user_id}")
                await self.onboarding.handle_callback_query(update, context)
            elif user_state == "option_selection":
                await self.option.handle_callback_query(update, context)
            elif user_state == "setup":
                await self.settingup.handle_callback_query(update, context)
            elif user_state == "payment":
                await self.paying.handle_callback_query(update, context)
            elif user_state == "active":
                await self.iteration.handle_callback_query(update, context)
            else:
                # Default response for unknown state
                logger.warning(f"Unknown user state '{user_state}' for user {user_id}, routing to onboarding")
                await self.onboarding.handle_callback_query(update, context)
                
        except Exception as e:
            logger.error(f"Error in handle_callback_query for user {user_id}: {e}")
            await self._handle_critical_error(update, context, "handle_callback_query")
    
    async def _handle_critical_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE, error_context: str):
        """Handle critical errors with user-friendly messages"""
        try:
            await ErrorHandler.handle_critical_error(update, context, error_context, Exception("Critical error"))
        except Exception as e:
            logger.error(f"Error in _handle_critical_error: {e}")
    
    async def run(self):
        """Run the bot"""
        logger.info("Starting Telegram Bot...")
        await self.application.run_polling()

def main():
    """Main function"""
    try:
        bot = TelegramBot()
        
        # Check if there's already an event loop running
        try:
            loop = asyncio.get_running_loop()
            logger.warning("Event loop already running, creating new task")
            # If we're in an existing loop, create a new event loop in a thread
            import threading
            
            def run_bot():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    new_loop.run_until_complete(bot.run())
                finally:
                    new_loop.close()
            
            thread = threading.Thread(target=run_bot)
            thread.daemon = True
            thread.start()
            thread.join()
            
        except RuntimeError:
            # No event loop running, safe to use asyncio.run
            asyncio.run(bot.run())
            
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")

if __name__ == "__main__":
    import asyncio
    main()
