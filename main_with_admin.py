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
        
        # Admin contact configuration - Easy to change here
        self.admin_config = {
            'telegram_username': '@dapavl',  # Change this to your Telegram username
            'telegram_chat_id': os.getenv('ADMIN_TELEGRAM_ID'),  # Or set chat ID in .env
            'notifications_enabled': True,  # Set to False to disable admin notifications
        'notification_types': {
            'new_users': True,
            'new_subscriptions': True,
            'payments': True,
            'help_requests': True,
            'regular_plan_requests': True,
            'errors': True
        }
        }
        
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
        
        # Admin commands
        self.application.add_handler(CommandHandler("admin_stats", self.admin_stats_command))
        self.application.add_handler(CommandHandler("admin_health", self.admin_health_command))
        self.application.add_handler(CommandHandler("admin_security", self.admin_security_command))
        self.application.add_handler(CommandHandler("admin_performance", self.admin_performance_command))
        self.application.add_handler(CommandHandler("admin_analytics", self.admin_analytics_command))
        
        # Message handlers for different modules
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_message
        ))
        
        # Callback query handler for inline keyboards
        self.application.add_handler(CallbackQueryHandler(
            self.handle_callback_query
        ))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        try:
            user_id = update.effective_user.id
            username = update.effective_user.username or "Unknown"
            first_name = update.effective_user.first_name or ""
            last_name = update.effective_user.last_name or ""
            
            logger.info(f"User {user_id} ({username}) started the bot")
            
            # Initialize user in database with Telegram profile info
            await self.db_manager.initialize_user(user_id, username, first_name, last_name)
            
            # Update user profile with Telegram data
            await self.db_manager.update_user_profile(
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
                username=username
            )

            # Send new user notification to admin
            await self.notify_new_user(user_id, username, first_name, last_name)

            # Start onboarding process
            await self.onboarding.start_onboarding(update, context)
            
        except Exception as e:
            logger.error(f"Error in start_command for user {user_id}: {e}")
            await self._handle_critical_error(update, context, "start_command")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        try:
            help_text = """
🤖 **Bot Commands:**

/start - Start the bot and begin onboarding
/help - Show this help message
/status - Check your current status and subscription

**Bot Features:**
• Onboarding process to understand the bot's purpose
• Three subscription options: Extreme, 2-week, or Regular
• Personalized setup to collect your key texts
• Secure payment processing
• Subscription management
• Iterative content delivery

For support, contact the bot administrator.
            """
            await update.message.reply_text(help_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in help_command: {e}")
            await self._handle_critical_error(update, context, "help_command")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        try:
            user_id = update.effective_user.id
            await self.subscription.check_user_status(update, context, user_id)
            
        except Exception as e:
            logger.error(f"Error in status_command for user {user_id}: {e}")
            await self._handle_critical_error(update, context, "status_command")
    
    async def admin_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin_stats command for admin users"""
        try:
            user_id = update.effective_user.id
            
            # Check if user is admin
            if str(user_id) != str(self.admin_config.get('telegram_chat_id', '')):
                await update.message.reply_text("❌ Access denied. Admin only.")
                return
            
            # Get system statistics
            stats = await self.monitoring.get_system_statistics()
            
            stats_text = f"""
📊 **System Statistics**

**👥 Users:**
• Total users: {stats.get('total_users', 0)}
• Active subscriptions: {stats.get('active_subscriptions', 0)}

**💬 Messages:**
• User messages: {stats.get('total_user_messages', 0)}
• Bot messages: {stats.get('total_bot_messages', 0)}

**🖥️ System:**
• Uptime: {stats.get('uptime_seconds', 0)/3600:.1f} hours
• CPU: {stats.get('system_metrics', {}).get('cpu_percent', 0):.1f}%
• Memory: {stats.get('system_metrics', {}).get('memory_percent', 0):.1f}%
• Disk: {stats.get('system_metrics', {}).get('disk_percent', 0):.1f}%

**📈 Performance:**
• Total errors: {self.monitoring.metrics.get('errors_count', 0)}
• Last activity: {self.monitoring.metrics.get('last_activity', 'Unknown')}
            """
            
            await update.message.reply_text(stats_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in admin_stats_command: {e}")
            await self._handle_critical_error(update, context, "admin_stats_command")
    
    async def admin_health_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin_health command for admin users"""
        try:
            user_id = update.effective_user.id
            
            # Check if user is admin
            if str(user_id) != str(self.admin_config.get('telegram_chat_id', '')):
                await update.message.reply_text("❌ Access denied. Admin only.")
                return
            
            # Get health status
            health = self.monitoring.get_health_status()
            
            status_emoji = "✅" if health.get('status') == 'healthy' else "⚠️" if health.get('status') == 'warning' else "❌"
            
            health_text = f"""
{status_emoji} **System Health Status**

**Overall Status:** {health.get('status', 'unknown').upper()}

**Components:**
• Database: {health.get('database', 'unknown')}
• Memory: {health.get('memory', 'unknown')}
• Disk: {health.get('disk', 'unknown')}

**Uptime:** {health.get('uptime', 0)/3600:.1f} hours
**Last Check:** {health.get('timestamp', 'Unknown')}
            """
            
            await update.message.reply_text(health_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in admin_health_command: {e}")
            await self._handle_critical_error(update, context, "admin_health_command")
    
    async def admin_security_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin_security command for admin users"""
        try:
            user_id = update.effective_user.id
            
            # Check if user is admin
            if str(user_id) != str(self.admin_config.get('telegram_chat_id', '')):
                await update.message.reply_text("❌ Access denied. Admin only.")
                return
            
            # Get security report
            security_report = self.security.get_security_report()
            
            status_emoji = "✅" if security_report.get('security_status') == 'healthy' else "⚠️"
            
            security_text = f"""
🔒 **Security Status**

{status_emoji} **Overall Status:** {security_report.get('security_status', 'unknown').upper()}

**📊 Statistics:**
• Active rate limits: {security_report.get('active_rate_limits', 0)}
• Blocked users: {security_report.get('blocked_users', 0)}
• Recent suspicious activities: {security_report.get('recent_suspicious_activities', 0)}

**⏰ Last Check:** {security_report.get('timestamp', 'Unknown')}

**🛡️ Security Features:**
• Rate limiting: ✅ Active
• Content validation: ✅ Active
• Suspicious activity detection: ✅ Active
• User blocking: ✅ Active
            """
            
            await update.message.reply_text(security_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in admin_security_command: {e}")
            await self._handle_critical_error(update, context, "admin_security_command")
    
    async def admin_performance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin_performance command for admin users"""
        try:
            user_id = update.effective_user.id
            
            # Check if user is admin
            if str(user_id) != str(self.admin_config.get('telegram_chat_id', '')):
                await update.message.reply_text("❌ Access denied. Admin only.")
                return
            
            # Get performance metrics
            performance_metrics = self.performance.get_performance_metrics()
            db_stats = await self.performance.get_database_stats()
            
            status_emoji = "✅" if performance_metrics.get('performance_status') == 'good' else "⚠️"
            
            performance_text = f"""
⚡ **Performance Status**

{status_emoji} **Overall Status:** {performance_metrics.get('performance_status', 'unknown').upper()}

**📊 Cache Performance:**
• Cache size: {performance_metrics.get('cache_size', 0)} entries
• Cache hit rate: {performance_metrics.get('cache_hit_rate', 0):.1f}%
• DB queries: {performance_metrics.get('db_queries', 0)}
• Slow queries: {performance_metrics.get('slow_queries', 0)}

**⏱️ Response Times:**
• Average response time: {performance_metrics.get('average_response_time', 0):.3f}s

**💾 Database:**
• Size: {db_stats.get('database_size_mb', 0):.2f} MB
• Tables: {db_stats.get('table_count', 0)}
• Total rows: {sum(table.get('rows', 0) for table in db_stats.get('tables', []))}

**🔧 Optimizations:**
• Caching: ✅ Active
• Database optimization: ✅ Available
• Memory management: ✅ Active
            """
            
            await update.message.reply_text(performance_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in admin_performance_command: {e}")
            await self._handle_critical_error(update, context, "admin_performance_command")
    
    async def admin_analytics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin_analytics command for admin users"""
        try:
            user_id = update.effective_user.id
            
            # Check if user is admin
            if str(user_id) != str(self.admin_config.get('telegram_chat_id', '')):
                await update.message.reply_text("❌ Access denied. Admin only.")
                return
            
            # Generate analytics report
            report = await self.analytics.generate_analytics_report()
            
            # Split report if too long
            if len(report) > 4000:
                # Send in chunks
                chunks = [report[i:i+4000] for i in range(0, len(report), 4000)]
                for i, chunk in enumerate(chunks):
                    if i == 0:
                        await update.message.reply_text(f"📊 **Analytics Report (Part {i+1})**\n\n{chunk}", parse_mode='Markdown')
                    else:
                        await update.message.reply_text(f"📊 **Analytics Report (Part {i+1})**\n\n{chunk}", parse_mode='Markdown')
            else:
                await update.message.reply_text(report, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in admin_analytics_command: {e}")
            await self._handle_critical_error(update, context, "admin_analytics_command")
    
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
            
            # Get user's current state
            user_state = await self.state_manager.get_user_state(user_id)
            
            # Route callback query to appropriate module based on state
            if user_state == "onboarding":
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
                await update.callback_query.answer("Неизвестное действие. Используйте /start для начала.")
                
        except Exception as e:
            logger.error(f"Error in handle_callback_query for user {user_id}: {e}")
            await self._handle_critical_error(update, context, "handle_callback_query")
    
    async def _handle_critical_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE, error_context: str):
        """Handle critical errors with user-friendly messages"""
        try:
            user_id = update.effective_user.id if update.effective_user else "unknown"
            
            # Use the centralized error handler
            await ErrorHandler.handle_critical_error(update, context, error_context, Exception(f"Critical error in {error_context}"))
            
            # Notify admin about the error
            await self.send_admin_notification(
                f"Critical error in {error_context} for user {user_id}",
                "errors"
            )
            
        except Exception as e:
            logger.critical(f"Failed to handle critical error: {e}")
    
    async def send_admin_notification(self, message: str, notification_type: str = "general"):
        """Send notification message to admin"""
        try:
            # Check if notifications are enabled
            if not self.admin_config['notifications_enabled']:
                logger.info("Admin notifications disabled")
                return False
            
            # Check if this notification type is enabled
            if notification_type in self.admin_config['notification_types']:
                if not self.admin_config['notification_types'][notification_type]:
                    logger.info(f"Admin notifications for {notification_type} disabled")
                    return False
            
            # Get admin chat ID
            admin_chat_id = self.admin_config['telegram_chat_id']
            
            if not admin_chat_id:
                logger.warning(f"Admin chat ID not set. Please set ADMIN_TELEGRAM_ID in .env or contact {self.admin_config['telegram_username']}")
                return False
            
            # Add notification type header
            formatted_message = f"🔔 **{notification_type.upper().replace('_', ' ')}**\n\n{message}"
            
            await self.application.bot.send_message(
                chat_id=admin_chat_id,
                text=formatted_message,
                parse_mode='Markdown'
            )
            logger.info(f"Admin notification sent successfully: {notification_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending admin notification: {e}")
            return False
    
    async def notify_new_subscription(self, user_id: int, user_name: str, plan_name: str, order_id: str, goal: str):
        """Notify admin about new subscription"""
        message = f"""
🎉 **Новая подписка!**

👤 **Пользователь:** {user_name} (ID: {user_id})
📋 **План:** {plan_name}
🎯 **Цель:** "{goal}"
📦 **Заказ:** #{order_id}

⏰ **Время:** {self._get_current_time()}
        """
        return await self.send_admin_notification(message, "new_subscriptions")
    
    async def notify_new_user(self, user_id: int, username: str, first_name: str, last_name: str):
        """Notify admin about new user registration"""
        full_name = f"{first_name} {last_name}".strip() if first_name or last_name else "Не указано"
        message = f"""
👋 **Новый пользователь!**

👤 **Имя:** {full_name}
📱 **Username:** @{username if username else 'не указан'}
🆔 **ID:** {user_id}

⏰ **Время регистрации:** {self._get_current_time()}

**Действие:** Пользователь начал работу с ботом HackReality
        """
        return await self.send_admin_notification(message, "new_users")
    
    async def notify_payment(self, user_id: int, user_name: str, amount: str, order_id: str, payment_method: str):
        """Notify admin about successful payment"""
        message = f"""
💳 **Платеж получен!**

👤 **Пользователь:** {user_name} (ID: {user_id})
💰 **Сумма:** {amount}
📦 **Заказ:** #{order_id}
💳 **Способ оплаты:** {payment_method}

⏰ **Время:** {self._get_current_time()}
        """
        return await self.send_admin_notification(message, "payments")
    
    async def notify_help_request(self, user_id: int, user_name: str, message_text: str):
        """Notify admin about help request"""
        message = f"""
🆘 **Запрос помощи**

👤 **Пользователь:** {user_name} (ID: {user_id})
💬 **Сообщение:** "{message_text}"

⏰ **Время:** {self._get_current_time()}
        """
        return await self.send_admin_notification(message, "help_requests")
    
    async def notify_regular_plan_request(self, user_id: int, user_name: str, goal: str, order_id: str):
        """Notify admin about Regular plan request"""
        message = f"""
🚧 **Запрос Обычного плана**

👤 **Пользователь:** {user_name} (ID: {user_id})
🎯 **Цель:** "{goal}"
📦 **Заказ:** #{order_id}

⏰ **Время:** {self._get_current_time()}

**Действие:** Пользователь заинтересован в Обычном плане, но план пока в разработке.
        """
        return await self.send_admin_notification(message, "regular_plan_requests")
    
    async def notify_donation_confirmation(self, user_id: int, user_name: str, order_id: str, target_goal: str, plan_details: dict):
        """Notify admin about donation confirmation"""
        message = f"""
💰 **ПОДТВЕРЖДЕНИЕ ДОНАТА**

👤 **Пользователь:** {user_name} (ID: {user_id})
📦 **Заказ:** #{order_id}
🎯 **Цель:** "{target_goal}"
📋 **План:** {plan_details.get('name', 'Unknown')}
💰 **Сумма:** {plan_details.get('price', 'Unknown')}

⏰ **Время:** {self._get_current_time()}

**Действие:** Пользователь подтвердил, что сделал донат на номер +79853659487

**Нужно подтвердить получение доната!**
        """
        return await self.send_admin_notification(message, "payments")
    
    async def notify_setup_complete(self, user_id: int, order_id: str, target_goal: str, selected_plan: str):
        """Notify admin about setup completion"""
        message = f"""
🎯 **НАСТРОЙКА ЗАВЕРШЕНА**

👤 **Пользователь:** ID: {user_id}
📦 **Заказ:** #{order_id}
🎯 **Цель:** "{target_goal}"
📋 **План:** {selected_plan}

⏰ **Время:** {self._get_current_time()}

**Действие:** Пользователь завершил настройку и готов к работе над целью.

**Статус:** Подписка активирована, можно начинать отправку контента!
        """
        return await self.send_admin_notification(message, "new_subscriptions")
    
    async def notify_error(self, error_message: str, user_id: int = None, context: str = ""):
        """Notify admin about errors"""
        user_info = f" (Пользователь: {user_id})" if user_id else ""
        message = f"""
❌ **Ошибка в боте**

🚨 **Ошибка:** {error_message}
📝 **Контекст:** {context}{user_info}

⏰ **Время:** {self._get_current_time()}
        """
        return await self.send_admin_notification(message, "errors")
    
    def _get_current_time(self):
        """Get current time in readable format"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def run(self):
        """Start the bot"""
        try:
            logger.info("Starting Telegram Bot...")
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)
        except Exception as e:
            logger.critical(f"Failed to start bot: {e}")
            raise

if __name__ == '__main__':
    try:
        bot = TelegramBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Bot crashed: {e}")
        raise
