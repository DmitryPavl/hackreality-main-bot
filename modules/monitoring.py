"""
Monitoring Module
Provides comprehensive monitoring and logging for the Telegram bot.
"""

import logging
import psutil
import sqlite3
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from telegram import Update
from telegram.ext import ContextTypes
from modules.admin_notifications import admin_notifications

logger = logging.getLogger(__name__)

class MonitoringManager:
    """Centralized monitoring and logging manager"""
    
    def __init__(self, db_manager, bot_instance=None):
        self.db_manager = db_manager
        self.bot_instance = bot_instance
        self.metrics = {
            "start_time": datetime.now(),
            "total_messages": 0,
            "total_users": 0,
            "errors_count": 0,
            "last_activity": datetime.now()
        }
    
    async def log_user_activity(self, user_id: int, activity_type: str, details: Dict[str, Any] = None):
        """Log user activity for analytics"""
        try:
            activity_data = {
                "user_id": user_id,
                "activity_type": activity_type,
                "timestamp": datetime.now().isoformat(),
                "details": details or {}
            }
            
            # Store in database
            await self.db_manager.store_user_message(
                user_id=user_id,
                message_text=json.dumps(activity_data),
                message_type="activity_log",
                module_context="monitoring",
                state_context=activity_type
            )
            
            # Update metrics
            self.metrics["total_messages"] += 1
            self.metrics["last_activity"] = datetime.now()
            
        except Exception as e:
            logger.error(f"Error logging user activity: {e}")
    
    async def log_system_metrics(self):
        """Log system performance metrics"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics_data = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "disk_percent": disk.percent,
                "disk_free": disk.free,
                "uptime": (datetime.now() - self.metrics["start_time"]).total_seconds()
            }
            
            # Log to file
            logger.info(f"System metrics: {json.dumps(metrics_data)}")
            
            # Check for alerts
            await self._check_system_alerts(metrics_data)
            
        except Exception as e:
            logger.error(f"Error logging system metrics: {e}")
    
    async def _check_system_alerts(self, metrics: Dict[str, Any]):
        """Check system metrics and send alerts if needed"""
        try:
            alerts = []
            
            # CPU alert
            if metrics["cpu_percent"] > 80:
                alerts.append(f"High CPU usage: {metrics['cpu_percent']:.1f}%")
            
            # Memory alert
            if metrics["memory_percent"] > 80:
                alerts.append(f"High memory usage: {metrics['memory_percent']:.1f}%")
            
            # Disk alert
            if metrics["disk_percent"] > 80:
                alerts.append(f"High disk usage: {metrics['disk_percent']:.1f}%")
            
            # Send alerts
            if alerts and self.bot_instance:
                alert_message = "🚨 **System Alert**\n\n" + "\n".join(alerts)
                await admin_notifications.notify_error(alert_message)
                
        except Exception as e:
            logger.error(f"Error checking system alerts: {e}")
    
    async def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get statistics for a specific user"""
        try:
            # Get user messages
            messages = await self.db_manager.get_user_messages(user_id, limit=1000)
            
            # Calculate statistics
            total_messages = len(messages)
            user_messages = len([m for m in messages if m['message_type'] == 'user_message'])
            bot_messages = len([m for m in messages if m['message_type'] == 'bot_message'])
            
            # Get subscription info
            subscription = await self.db_manager.get_active_subscription(user_id)
            
            # Get user profile
            profile = await self.db_manager.get_user_profile(user_id)
            
            stats = {
                "user_id": user_id,
                "total_messages": total_messages,
                "user_messages": user_messages,
                "bot_messages": bot_messages,
                "has_active_subscription": subscription is not None,
                "subscription_type": subscription['subscription_type'] if subscription else None,
                "user_goal": subscription['user_goal'] if subscription else None,
                "created_at": profile['created_at'] if profile else None,
                "last_activity": profile['last_activity'] if profile else None
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            return {}
    
    async def get_system_statistics(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        try:
            # Get database statistics
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Count users
                cursor.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]
                
                # Count active subscriptions
                cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE status = 'active'")
                active_subscriptions = cursor.fetchone()[0]
                
                # Count messages
                cursor.execute("SELECT COUNT(*) FROM user_messages")
                total_user_messages = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM bot_messages")
                total_bot_messages = cursor.fetchone()[0]
            
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            stats = {
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": (datetime.now() - self.metrics["start_time"]).total_seconds(),
                "total_users": total_users,
                "active_subscriptions": active_subscriptions,
                "total_user_messages": total_user_messages,
                "total_bot_messages": total_bot_messages,
                "system_metrics": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_percent": disk.percent,
                    "disk_free_gb": disk.free / (1024**3)
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting system statistics: {e}")
            return {}
    
    async def log_error(self, error: Exception, context: str, user_id: Optional[int] = None):
        """Log errors with context"""
        try:
            self.metrics["errors_count"] += 1
            
            error_data = {
                "timestamp": datetime.now().isoformat(),
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context,
                "user_id": user_id
            }
            
            logger.error(f"Error logged: {json.dumps(error_data)}")
            
            # Store in database if user_id provided
            if user_id:
                await self.db_manager.store_user_message(
                    user_id=user_id,
                    message_text=json.dumps(error_data),
                    message_type="error_log",
                    module_context="monitoring",
                    state_context=context
                )
                
        except Exception as e:
            logger.critical(f"Failed to log error: {e}")
    
    async def generate_daily_report(self) -> str:
        """Generate daily activity report"""
        try:
            # Get yesterday's date
            yesterday = datetime.now() - timedelta(days=1)
            yesterday_str = yesterday.strftime("%Y-%m-%d")
            
            # Get system statistics
            stats = await self.get_system_statistics()
            
            # Get database statistics for yesterday
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Count new users yesterday
                cursor.execute("""
                    SELECT COUNT(*) FROM users 
                    WHERE DATE(created_at) = ?
                """, (yesterday_str,))
                new_users = cursor.fetchone()[0]
                
                # Count messages yesterday
                cursor.execute("""
                    SELECT COUNT(*) FROM user_messages 
                    WHERE DATE(timestamp) = ?
                """, (yesterday_str,))
                messages_yesterday = cursor.fetchone()[0]
                
                # Count new subscriptions yesterday
                cursor.execute("""
                    SELECT COUNT(*) FROM subscriptions 
                    WHERE DATE(created_at) = ?
                """, (yesterday_str,))
                new_subscriptions = cursor.fetchone()[0]
            
            report = f"""
📊 **Daily Report - {yesterday_str}**

**👥 Users:**
• New users: {new_users}
• Total users: {stats['total_users']}
• Active subscriptions: {stats['active_subscriptions']}

**💬 Activity:**
• Messages yesterday: {messages_yesterday}
• Total user messages: {stats['total_user_messages']}
• Total bot messages: {stats['total_bot_messages']}

**🆕 New Subscriptions:**
• New subscriptions: {new_subscriptions}

**🖥️ System:**
• Uptime: {stats['uptime_seconds']/3600:.1f} hours
• CPU usage: {stats['system_metrics']['cpu_percent']:.1f}%
• Memory usage: {stats['system_metrics']['memory_percent']:.1f}%
• Disk usage: {stats['system_metrics']['disk_percent']:.1f}%

**📈 Performance:**
• Total errors: {self.metrics['errors_count']}
• Last activity: {self.metrics['last_activity'].strftime('%H:%M:%S')}
            """
            
            return report.strip()
            
        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
            return "Error generating daily report"
    
    async def send_daily_report(self):
        """Send daily report to admin"""
        try:
            if not self.bot_instance:
                return
            
            report = await self.generate_daily_report()
            await admin_notifications.send_notification(report, "general")
            
        except Exception as e:
            logger.error(f"Error sending daily report: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        try:
            # Check database connectivity
            db_healthy = True
            try:
                with sqlite3.connect(self.db_manager.db_path) as conn:
                    conn.execute("SELECT 1")
            except:
                db_healthy = False
            
            # Check system resources
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            health_status = {
                "status": "healthy" if db_healthy and memory.percent < 90 and disk.percent < 90 else "warning",
                "database": "healthy" if db_healthy else "error",
                "memory": "healthy" if memory.percent < 80 else "warning" if memory.percent < 90 else "critical",
                "disk": "healthy" if disk.percent < 80 else "warning" if disk.percent < 90 else "critical",
                "uptime": (datetime.now() - self.metrics["start_time"]).total_seconds(),
                "timestamp": datetime.now().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {"status": "error", "error": str(e)}
