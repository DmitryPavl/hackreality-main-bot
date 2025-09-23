"""
Error Handler Module
Provides comprehensive error handling utilities for the Telegram bot.
"""

import logging
import traceback
from typing import Optional, Dict, Any
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Centralized error handling for the bot"""
    
    @staticmethod
    async def handle_database_error(error: Exception, operation: str, user_id: Optional[int] = None) -> bool:
        """Handle database-related errors"""
        try:
            error_msg = f"Database error in {operation}"
            if user_id:
                error_msg += f" for user {user_id}"
            
            logger.error(f"{error_msg}: {error}")
            
            # Log the full traceback for debugging
            logger.debug(f"Database error traceback: {traceback.format_exc()}")
            
            return False
            
        except Exception as e:
            logger.critical(f"Failed to handle database error: {e}")
            return False
    
    @staticmethod
    async def handle_api_error(error: Exception, api_name: str, user_id: Optional[int] = None) -> bool:
        """Handle API-related errors (timezone, external services)"""
        try:
            error_msg = f"API error with {api_name}"
            if user_id:
                error_msg += f" for user {user_id}"
            
            logger.error(f"{error_msg}: {error}")
            
            # Log the full traceback for debugging
            logger.debug(f"API error traceback: {traceback.format_exc()}")
            
            return False
            
        except Exception as e:
            logger.critical(f"Failed to handle API error: {e}")
            return False
    
    @staticmethod
    async def handle_telegram_error(error: Exception, operation: str, user_id: Optional[int] = None) -> bool:
        """Handle Telegram API errors"""
        try:
            error_msg = f"Telegram API error in {operation}"
            if user_id:
                error_msg += f" for user {user_id}"
            
            logger.error(f"{error_msg}: {error}")
            
            # Log the full traceback for debugging
            logger.debug(f"Telegram error traceback: {traceback.format_exc()}")
            
            return False
            
        except Exception as e:
            logger.critical(f"Failed to handle Telegram error: {e}")
            return False
    
    @staticmethod
    async def handle_validation_error(error: Exception, field: str, user_id: Optional[int] = None) -> bool:
        """Handle input validation errors"""
        try:
            error_msg = f"Validation error for field '{field}'"
            if user_id:
                error_msg += f" for user {user_id}"
            
            logger.warning(f"{error_msg}: {error}")
            
            return False
            
        except Exception as e:
            logger.critical(f"Failed to handle validation error: {e}")
            return False
    
    @staticmethod
    async def handle_critical_error(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                  error_context: str, error: Exception) -> None:
        """Handle critical errors that require user notification"""
        try:
            user_id = update.effective_user.id if update.effective_user else "unknown"
            
            # Log the critical error
            logger.critical(f"Critical error in {error_context} for user {user_id}: {error}")
            logger.critical(f"Critical error traceback: {traceback.format_exc()}")
            
            # Send user-friendly error message
            error_message = """
😔 **Произошла ошибка**

К сожалению, что-то пошло не так. Не волнуйся, твои данные в безопасности!

**Что можно сделать:**
• Попробуй еще раз через несколько минут
• Используй команду /start для перезапуска
• Обратись к администратору, если проблема повторяется

**Спасибо за понимание!** 🙏
            """
            
            if hasattr(update, 'message') and update.message:
                await update.message.reply_text(error_message, parse_mode='Markdown')
            elif hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.edit_message_text(error_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.critical(f"Failed to handle critical error: {e}")
    
    @staticmethod
    def log_error(error: Exception, context: str, user_id: Optional[int] = None, 
                  additional_data: Optional[Dict[str, Any]] = None) -> None:
        """Log errors with context and additional data"""
        try:
            error_msg = f"Error in {context}"
            if user_id:
                error_msg += f" for user {user_id}"
            
            if additional_data:
                error_msg += f" | Additional data: {additional_data}"
            
            logger.error(f"{error_msg}: {error}")
            logger.debug(f"Error traceback: {traceback.format_exc()}")
            
        except Exception as e:
            logger.critical(f"Failed to log error: {e}")
    
    @staticmethod
    async def safe_execute(func, *args, **kwargs):
        """Safely execute a function with error handling"""
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.log_error(e, f"safe_execute for {func.__name__}")
            return None
    
    @staticmethod
    def validate_user_input(text: str, max_length: int = 1000, min_length: int = 1) -> bool:
        """Validate user input text"""
        try:
            if not text or not isinstance(text, str):
                return False
            
            if len(text.strip()) < min_length:
                return False
            
            if len(text) > max_length:
                return False
            
            # Check for potentially harmful content
            dangerous_patterns = ['<script', 'javascript:', 'data:', 'vbscript:']
            text_lower = text.lower()
            
            for pattern in dangerous_patterns:
                if pattern in text_lower:
                    return False
            
            return True
            
        except Exception as e:
            ErrorHandler.log_error(e, "validate_user_input")
            return False
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        try:
            if not text:
                return ""
            
            # Remove potentially dangerous characters
            dangerous_chars = ['<', '>', '"', "'", '&', '\x00', '\r', '\n']
            sanitized = text
            
            for char in dangerous_chars:
                sanitized = sanitized.replace(char, '')
            
            # Limit length
            if len(sanitized) > 1000:
                sanitized = sanitized[:1000]
            
            return sanitized.strip()
            
        except Exception as e:
            ErrorHandler.log_error(e, "sanitize_input")
            return ""
    
    @staticmethod
    async def handle_timeout_error(error: Exception, operation: str, user_id: Optional[int] = None) -> bool:
        """Handle timeout errors"""
        try:
            error_msg = f"Timeout error in {operation}"
            if user_id:
                error_msg += f" for user {user_id}"
            
            logger.warning(f"{error_msg}: {error}")
            
            return False
            
        except Exception as e:
            logger.critical(f"Failed to handle timeout error: {e}")
            return False
    
    @staticmethod
    async def handle_network_error(error: Exception, operation: str, user_id: Optional[int] = None) -> bool:
        """Handle network-related errors"""
        try:
            error_msg = f"Network error in {operation}"
            if user_id:
                error_msg += f" for user {user_id}"
            
            logger.warning(f"{error_msg}: {error}")
            
            return False
            
        except Exception as e:
            logger.critical(f"Failed to handle network error: {e}")
            return False
