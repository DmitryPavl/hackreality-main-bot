#!/usr/bin/env python3
"""
Admin Notifications Module
Handles sending notifications from main bot modules to admin bot
"""

import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class AdminNotificationService:
    """Service for sending notifications to admin bot"""
    
    def __init__(self):
        self.admin_bot_token = os.getenv('ADMIN_BOT_TOKEN')
        self.admin_user_id = os.getenv('ADMIN_USER_ID', '41107472')
        
        if not self.admin_bot_token:
            logger.warning("ADMIN_BOT_TOKEN not found, admin notifications disabled")
            self.admin_bot_token = None
    
    async def send_notification(self, message: str, notification_type: str = "general"):
        """Send notification to admin via admin bot"""
        try:
            if not self.admin_bot_token:
                logger.warning("Admin bot token not available, logging notification instead")
                logger.info(f"ADMIN NOTIFICATION ({notification_type}): {message}")
                return False
            
            # Create admin bot instance
            admin_bot = Bot(token=self.admin_bot_token)
            
            # Send notification
            await admin_bot.send_message(
                chat_id=self.admin_user_id,
                text=message,
                parse_mode='Markdown'
            )
            
            logger.info(f"Admin notification sent successfully: {notification_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending admin notification: {e}")
            return False
    
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
        return await self.send_notification(message, "new_users")
    
    async def notify_regular_plan_request(self, user_id: int, user_name: str, user_goal: str, order_id: str):
        """Notify admin about Regular plan request"""
        message = f"""
🚧 **Запрос Обычного плана**

👤 **Пользователь:** {user_name} (ID: {user_id})
🎯 **Цель:** "{user_goal}"
📦 **Заказ:** #{order_id}

⏰ **Время:** {self._get_current_time()}

**Действие:** Пользователь заинтересован в Обычном плане, но план пока в разработке.
        """
        return await self.send_notification(message, "regular_plan_requests")
    
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
        return await self.send_notification(message, "payments")
    
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
        return await self.send_notification(message, "new_subscriptions")
    
    async def notify_error(self, error_message: str, user_id: int = None, context: str = ""):
        """Notify admin about errors"""
        user_info = f" (Пользователь: {user_id})" if user_id else ""
        message = f"""
❌ **Ошибка в боте**

🚨 **Ошибка:** {error_message}
📝 **Контекст:** {context}{user_info}

⏰ **Время:** {self._get_current_time()}
        """
        return await self.send_notification(message, "errors")
    
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
        return await self.send_notification(message, "payments")
    
    async def notify_help_request(self, user_id: int, user_name: str, message_text: str):
        """Notify admin about help request"""
        message = f"""
🆘 **Запрос помощи**

👤 **Пользователь:** {user_name} (ID: {user_id})
💬 **Сообщение:** "{message_text}"

⏰ **Время:** {self._get_current_time()}
        """
        return await self.send_notification(message, "help_requests")
    
    def _get_current_time(self):
        """Get current time in readable format"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Global instance for use across modules
admin_notifications = AdminNotificationService()
