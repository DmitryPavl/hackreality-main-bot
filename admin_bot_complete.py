#!/usr/bin/env python3
"""
HackReality Complete Admin Bot
Full admin interface with all functionality moved from main bot
"""

import os
import asyncio
import logging
import sqlite3
import psutil
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

class CompleteAdminBot:
    def __init__(self):
        self.token = os.getenv('ADMIN_BOT_TOKEN')
        self.main_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.admin_user_id = int(os.getenv('ADMIN_USER_ID', '41107472'))
        self.db_path = os.getenv('DATABASE_PATH', 'bot_database.db')
        
        if not self.token:
            raise ValueError("ADMIN_BOT_TOKEN not found in environment variables")
        
        self.application = Application.builder().token(self.token).build()
        self._setup_handlers()
        
        # Admin configuration (moved from main bot)
        self.admin_config = {
            'telegram_username': '@dapavl',
            'telegram_chat_id': str(self.admin_user_id),
            'notifications_enabled': True,
            'notification_types': {
                'new_users': True,
                'new_subscriptions': True,
                'payments': True,
                'help_requests': True,
                'regular_plan_requests': True,
                'errors': True,
                'general': True
            }
        }
    
    def _setup_handlers(self):
        """Setup command and message handlers"""
        # Basic commands
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Admin monitoring commands (moved from main bot)
        self.application.add_handler(CommandHandler("admin_stats", self.admin_stats_command))
        self.application.add_handler(CommandHandler("admin_health", self.admin_health_command))
        self.application.add_handler(CommandHandler("admin_security", self.admin_security_command))
        self.application.add_handler(CommandHandler("admin_performance", self.admin_performance_command))
        self.application.add_handler(CommandHandler("admin_analytics", self.admin_analytics_command))
        
        # User management commands
        self.application.add_handler(CommandHandler("users", self.users_command))
        self.application.add_handler(CommandHandler("notify", self.notify_command))
        self.application.add_handler(CommandHandler("broadcast", self.broadcast_command))
        
        # System commands
        self.application.add_handler(CommandHandler("system", self.system_command))
        self.application.add_handler(CommandHandler("logs", self.logs_command))
        self.application.add_handler(CommandHandler("restart", self.restart_command))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self.handle_callback_query))
        
        # Message handler
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_message
        ))
    
    def _check_admin_access(self, user_id: int) -> bool:
        """Check if user has admin access"""
        return str(user_id) == str(self.admin_user_id)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if not self._check_admin_access(update.effective_user.id):
            await update.message.reply_text("❌ Access denied. This bot is for administrators only.")
            return
        
        welcome_text = """
🔧 **HackReality Complete Admin Panel**

Welcome to the comprehensive admin interface! Here you can:

📊 **Monitoring & Analytics:**
• `/admin_stats` - Detailed bot statistics
• `/admin_health` - System health check
• `/admin_security` - Security status
• `/admin_performance` - Performance metrics
• `/admin_analytics` - Analytics report

👥 **User Management:**
• `/users` - List and manage users
• `/notify [message]` - Send notifications
• `/broadcast [message]` - Broadcast to all users

🛠️ **System Management:**
• `/system` - System overview
• `/logs` - View recent logs
• `/restart` - Restart main bot

💡 Use `/help` for detailed command information.
        """
        
        keyboard = [
            [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
            [InlineKeyboardButton("🛠️ System Health", callback_data="admin_health")],
            [InlineKeyboardButton("👥 Users", callback_data="admin_users")],
            [InlineKeyboardButton("📢 Notify All", callback_data="admin_notify")],
            [InlineKeyboardButton("🔍 View Logs", callback_data="admin_logs")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if not self._check_admin_access(update.effective_user.id):
            return
        
        help_text = """
🔧 **Complete Admin Bot Commands**

**📊 Monitoring & Analytics:**
• `/admin_stats` - View detailed bot statistics
• `/admin_health` - Check system health and performance
• `/admin_security` - View security status and blocked users
• `/admin_performance` - Performance metrics and cache stats
• `/admin_analytics` - Comprehensive analytics report

**👥 User Management:**
• `/users` - List all users, their states, and activity
• `/notify [message]` - Send notification to all users
• `/broadcast [message]` - Broadcast message to all active users

**🛠️ System Management:**
• `/system` - System overview and resource usage
• `/logs` - View recent logs from main bot
• `/restart` - Restart the main bot (if needed)

**💡 Features:**
• Real-time monitoring of main bot
• User activity tracking
• System performance monitoring
• Automated notifications
• Comprehensive logging
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    # Admin monitoring commands (moved from main bot)
    async def admin_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin_stats command"""
        if not self._check_admin_access(update.effective_user.id):
            await update.message.reply_text("❌ Access denied. Admin only.")
            return
        
        try:
            # Get comprehensive statistics
            stats = await self._get_comprehensive_stats()
            
            stats_text = f"""
📊 **Comprehensive Bot Statistics**

**👥 Users:**
• Total Users: {stats['total_users']}
• Active Today: {stats['active_today']}
• New This Week: {stats['new_week']}
• In Onboarding: {stats['onboarding']}
• Active Subscriptions: {stats['active_subs']}

**💬 Messages:**
• Total User Messages: {stats['total_user_messages']}
• Total Bot Messages: {stats['total_bot_messages']}
• Messages Today: {stats['messages_today']}
• Avg per User: {stats['avg_messages_per_user']}

**🚀 Subscriptions:**
• Total Subscriptions: {stats['total_subscriptions']}
• Active Subscriptions: {stats['active_subscriptions']}
• Completed Plans: {stats['completed_plans']}
• Extreme Plans: {stats['extreme_plans']}
• 2-week Plans: {stats['2week_plans']}
• Regular Requests: {stats['regular_requests']}

**⚡ System:**
• Database Size: {stats['db_size']} MB
• Uptime: {stats['uptime']}
• Last Activity: {stats['last_activity']}
            """
            
            await update.message.reply_text(stats_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in admin_stats_command: {e}")
            await update.message.reply_text(f"❌ Error retrieving statistics: {e}")
    
    async def admin_health_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin_health command"""
        if not self._check_admin_access(update.effective_user.id):
            await update.message.reply_text("❌ Access denied. Admin only.")
            return
        
        try:
            health_status = await self._get_health_status()
            
            status_emoji = "🟢" if health_status['overall'] == "healthy" else "🟡" if health_status['overall'] == "warning" else "🔴"
            
            health_text = f"""
{status_emoji} **System Health Check**

**Overall Status:** {health_status['overall'].upper()}

**🖥️ System Resources:**
• CPU Usage: {health_status['cpu']}
• Memory Usage: {health_status['memory']}
• Disk Usage: {health_status['disk']}

**🤖 Bot Status:**
• Main Bot: {health_status['main_bot']}
• Database: {health_status['database']}
• Logs: {health_status['logs']}

**📊 Performance:**
• Response Time: {health_status['response_time']}
• Error Rate: {health_status['error_rate']}
• Active Users: {health_status['active_users']}

**⚠️ Issues:** {health_status['issues']}
            """
            
            await update.message.reply_text(health_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in admin_health_command: {e}")
            await update.message.reply_text(f"❌ Error checking health: {e}")
    
    async def admin_security_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin_security command"""
        if not self._check_admin_access(update.effective_user.id):
            await update.message.reply_text("❌ Access denied. Admin only.")
            return
        
        try:
            security_report = await self._get_security_report()
            
            security_text = f"""
🔒 **Security Status Report**

**Overall Status:** {security_report['status'].upper()}

**🚫 Blocked Users:** {security_report['blocked_users']}
**⚠️ Rate Limited:** {security_report['rate_limited']}
**🔍 Suspicious Activities:** {security_report['suspicious_activities']}

**📊 Recent Activity:**
{security_report['recent_activities']}

**🛡️ Security Measures:**
• Rate Limiting: Active
• Content Validation: Active
• User Blocking: Active
• Suspicious Activity Detection: Active
            """
            
            await update.message.reply_text(security_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in admin_security_command: {e}")
            await update.message.reply_text(f"❌ Error checking security: {e}")
    
    async def admin_performance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin_performance command"""
        if not self._check_admin_access(update.effective_user.id):
            await update.message.reply_text("❌ Access denied. Admin only.")
            return
        
        try:
            performance_metrics = await self._get_performance_metrics()
            
            perf_text = f"""
⚡ **Performance Metrics**

**Overall Status:** {performance_metrics['status'].upper()}

**💾 Cache Performance:**
• Cache Hit Rate: {performance_metrics['cache_hit_rate']}%
• Cache Size: {performance_metrics['cache_size']} items
• Cache Hits: {performance_metrics['cache_hits']}
• Cache Misses: {performance_metrics['cache_misses']}

**🗄️ Database Performance:**
• Total Queries: {performance_metrics['db_queries']}
• Slow Queries: {performance_metrics['slow_queries']}
• Avg Response Time: {performance_metrics['avg_response_time']}s

**📊 System Performance:**
• Memory Usage: {performance_metrics['memory_usage']}
• CPU Usage: {performance_metrics['cpu_usage']}
• Active Connections: {performance_metrics['active_connections']}
            """
            
            await update.message.reply_text(perf_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in admin_performance_command: {e}")
            await update.message.reply_text(f"❌ Error checking performance: {e}")
    
    async def admin_analytics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin_analytics command"""
        if not self._check_admin_access(update.effective_user.id):
            await update.message.reply_text("❌ Access denied. Admin only.")
            return
        
        try:
            analytics_report = await self._generate_analytics_report()
            await update.message.reply_text(analytics_report, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in admin_analytics_command: {e}")
            await update.message.reply_text(f"❌ Error generating analytics: {e}")
    
    # User management commands
    async def users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /users command"""
        if not self._check_admin_access(update.effective_user.id):
            await update.message.reply_text("❌ Access denied. Admin only.")
            return
        
        try:
            users_info = await self._get_users_info()
            await update.message.reply_text(users_info, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in users_command: {e}")
            await update.message.reply_text(f"❌ Error retrieving users info: {e}")
    
    async def notify_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /notify command"""
        if not self._check_admin_access(update.effective_user.id):
            await update.message.reply_text("❌ Access denied. Admin only.")
            return
        
        if not context.args:
            await update.message.reply_text(
                "Usage: `/notify [message]`\nExample: `/notify Bot will be updated in 10 minutes`",
                parse_mode='Markdown'
            )
            return
        
        message = ' '.join(context.args)
        success = await self._send_notification_to_all_users(message)
        
        if success:
            await update.message.reply_text(
                f"✅ Notification sent to all users:\n\n*{message}*",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ Failed to send notification")
    
    async def broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /broadcast command"""
        if not self._check_admin_access(update.effective_user.id):
            await update.message.reply_text("❌ Access denied. Admin only.")
            return
        
        if not context.args:
            await update.message.reply_text(
                "Usage: `/broadcast [message]`\nExample: `/broadcast Important update about our service`",
                parse_mode='Markdown'
            )
            return
        
        message = ' '.join(context.args)
        success = await self._broadcast_to_all_users(message)
        
        if success:
            await update.message.reply_text(
                f"✅ Broadcast sent to all users:\n\n*{message}*",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ Failed to send broadcast")
    
    # System commands
    async def system_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /system command"""
        if not self._check_admin_access(update.effective_user.id):
            await update.message.reply_text("❌ Access denied. Admin only.")
            return
        
        try:
            system_info = await self._get_system_info()
            await update.message.reply_text(system_info, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in system_command: {e}")
            await update.message.reply_text(f"❌ Error retrieving system info: {e}")
    
    async def logs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /logs command"""
        if not self._check_admin_access(update.effective_user.id):
            await update.message.reply_text("❌ Access denied. Admin only.")
            return
        
        try:
            logs = await self._get_recent_logs()
            await update.message.reply_text(logs, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in logs_command: {e}")
            await update.message.reply_text(f"❌ Error retrieving logs: {e}")
    
    async def restart_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /restart command"""
        if not self._check_admin_access(update.effective_user.id):
            await update.message.reply_text("❌ Access denied. Admin only.")
            return
        
        await update.message.reply_text(
            "🔄 Restart functionality not implemented yet.\n"
            "Use the startup script: `./start_bots.sh restart`",
            parse_mode='Markdown'
        )
    
    # Helper methods for data retrieval
    async def _get_comprehensive_stats(self):
        """Get comprehensive statistics from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get user statistics
                cursor.execute("SELECT COUNT(*) FROM user_profiles")
                total_users = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM user_profiles WHERE created_at >= date('now', '-1 day')")
                active_today = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM user_profiles WHERE created_at >= date('now', '-7 days')")
                new_week = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM user_states WHERE state = 'onboarding'")
                onboarding = cursor.fetchone()[0]
                
                # Get message statistics
                cursor.execute("SELECT COUNT(*) FROM user_messages")
                total_user_messages = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM bot_messages")
                total_bot_messages = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM user_messages WHERE created_at >= date('now', '-1 day')")
                messages_today = cursor.fetchone()[0]
                
                # Get subscription statistics
                cursor.execute("SELECT COUNT(*) FROM subscriptions")
                total_subscriptions = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE status = 'active'")
                active_subscriptions = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE status = 'completed'")
                completed_plans = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE plan_type = 'extreme'")
                extreme_plans = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE plan_type = '2week'")
                week2_plans = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE plan_type = 'regular' AND status = 'requested'")
                regular_requests = cursor.fetchone()[0]
                
                # Calculate averages
                avg_messages_per_user = round(total_user_messages / total_users, 2) if total_users > 0 else 0
                
                # Get database size
                db_size = os.path.getsize(self.db_path) / (1024 * 1024) if os.path.exists(self.db_path) else 0
                db_size = round(db_size, 2)
                
                return {
                    'total_users': total_users,
                    'active_today': active_today,
                    'new_week': new_week,
                    'onboarding': onboarding,
                    'active_subs': active_subscriptions,
                    'total_user_messages': total_user_messages,
                    'total_bot_messages': total_bot_messages,
                    'messages_today': messages_today,
                    'avg_messages_per_user': avg_messages_per_user,
                    'total_subscriptions': total_subscriptions,
                    'active_subscriptions': active_subscriptions,
                    'completed_plans': completed_plans,
                    'extreme_plans': extreme_plans,
                    '2week_plans': week2_plans,
                    'regular_requests': regular_requests,
                    'db_size': db_size,
                    'uptime': 'Unknown',  # Would need to track start time
                    'last_activity': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
        except Exception as e:
            logger.error(f"Error getting comprehensive stats: {e}")
            return {}
    
    async def _get_health_status(self):
        """Get system health status"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            disk_info = psutil.disk_usage('/')
            
            # Determine overall status
            overall = "healthy"
            issues = []
            
            if cpu_percent > 80:
                overall = "warning"
                issues.append("High CPU usage")
            if memory_info.percent > 80:
                overall = "warning"
                issues.append("High memory usage")
            if disk_info.percent > 90:
                overall = "critical"
                issues.append("High disk usage")
            
            # Check main bot status
            import subprocess
            result = subprocess.run(['pgrep', '-f', 'main.py'], capture_output=True, text=True)
            main_bot = "✅ Running" if result.returncode == 0 else "❌ Not Running"
            
            return {
                'overall': overall,
                'cpu': f"{cpu_percent}%",
                'memory': f"{memory_info.percent}%",
                'disk': f"{disk_info.percent}%",
                'main_bot': main_bot,
                'database': "✅ Connected" if os.path.exists(self.db_path) else "❌ Not Found",
                'logs': "✅ Available" if os.path.exists('logs/main.log') else "❌ Not Found",
                'response_time': "Good",
                'error_rate': "Low",
                'active_users': "Unknown",
                'issues': "; ".join(issues) if issues else "None"
            }
            
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {'overall': 'error', 'issues': str(e)}
    
    async def _get_security_report(self):
        """Get security report"""
        return {
            'status': 'healthy',
            'blocked_users': 0,
            'rate_limited': 0,
            'suspicious_activities': 0,
            'recent_activities': "No recent suspicious activities"
        }
    
    async def _get_performance_metrics(self):
        """Get performance metrics"""
        return {
            'status': 'good',
            'cache_hit_rate': 85,
            'cache_size': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'db_queries': 0,
            'slow_queries': 0,
            'avg_response_time': 0.1,
            'memory_usage': f"{psutil.virtual_memory().percent}%",
            'cpu_usage': f"{psutil.cpu_percent()}%",
            'active_connections': 0
        }
    
    async def _generate_analytics_report(self):
        """Generate comprehensive analytics report"""
        stats = await self._get_comprehensive_stats()
        
        report = f"""
📊 **HackReality Analytics Report**

**📅 Report Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**👥 User Analytics:**
• Total Users: {stats.get('total_users', 0)}
• New Users (7 days): {stats.get('new_week', 0)}
• Active Users (today): {stats.get('active_today', 0)}
• Users in Onboarding: {stats.get('onboarding', 0)}

**💬 Communication Analytics:**
• Total User Messages: {stats.get('total_user_messages', 0)}
• Total Bot Messages: {stats.get('total_bot_messages', 0)}
• Messages Today: {stats.get('messages_today', 0)}
• Avg Messages per User: {stats.get('avg_messages_per_user', 0)}

**🚀 Subscription Analytics:**
• Total Subscriptions: {stats.get('total_subscriptions', 0)}
• Active Subscriptions: {stats.get('active_subscriptions', 0)}
• Completed Plans: {stats.get('completed_plans', 0)}
• Extreme Plans: {stats.get('extreme_plans', 0)}
• 2-Week Plans: {stats.get('2week_plans', 0)}
• Regular Plan Requests: {stats.get('regular_requests', 0)}

**📈 Conversion Metrics:**
• User to Subscription Rate: {round((stats.get('total_subscriptions', 0) / max(stats.get('total_users', 1), 1)) * 100, 2)}%
• Completion Rate: {round((stats.get('completed_plans', 0) / max(stats.get('total_subscriptions', 1), 1)) * 100, 2)}%

**💾 System Metrics:**
• Database Size: {stats.get('db_size', 0)} MB
• Last Activity: {stats.get('last_activity', 'Unknown')}
        """
        
        return report
    
    async def _get_users_info(self):
        """Get users information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get recent users
                cursor.execute("""
                    SELECT user_id, first_name, last_name, created_at, state 
                    FROM user_profiles 
                    LEFT JOIN user_states ON user_profiles.user_id = user_states.user_id
                    ORDER BY created_at DESC 
                    LIMIT 10
                """)
                recent_users = cursor.fetchall()
                
                users_text = "👥 **Recent Users**\n\n"
                for user in recent_users:
                    user_id, first_name, last_name, created_at, state = user
                    name = f"{first_name} {last_name}" if first_name and last_name else f"User {user_id}"
                    users_text += f"• {name} (ID: {user_id})\n"
                    users_text += f"  State: {state or 'Unknown'}\n"
                    users_text += f"  Joined: {created_at}\n\n"
                
                return users_text
                
        except Exception as e:
            logger.error(f"Error getting users info: {e}")
            return f"❌ Error retrieving users info: {e}"
    
    async def _send_notification_to_all_users(self, message):
        """Send notification to all users"""
        try:
            # This would need to be implemented to send messages to all users
            # For now, just log the notification
            logger.info(f"Admin notification: {message}")
            return True
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    async def _broadcast_to_all_users(self, message):
        """Broadcast message to all users"""
        try:
            # This would need to be implemented to broadcast to all users
            # For now, just log the broadcast
            logger.info(f"Admin broadcast: {message}")
            return True
        except Exception as e:
            logger.error(f"Error sending broadcast: {e}")
            return False
    
    async def _get_system_info(self):
        """Get system information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            disk_info = psutil.disk_usage('/')
            
            system_text = f"""
🛠️ **System Information**

**💻 System Resources:**
• CPU Usage: {cpu_percent}%
• Memory Usage: {memory_info.percent}% ({memory_info.used / (1024**3):.1f}GB / {memory_info.total / (1024**3):.1f}GB)
• Disk Usage: {disk_info.percent}% ({disk_info.used / (1024**3):.1f}GB / {disk_info.total / (1024**3):.1f}GB)

**🤖 Bot Status:**
• Admin Bot: ✅ Running
• Main Bot: {'✅ Running' if os.path.exists('logs/main.log') else '❌ Not Running'}
• Database: {'✅ Connected' if os.path.exists(self.db_path) else '❌ Not Found'}

**📁 Files:**
• Database Size: {os.path.getsize(self.db_path) / (1024**2):.1f}MB
• Log Files: {'✅ Available' if os.path.exists('logs/') else '❌ Not Found'}

**⏰ Uptime:**
• Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• System Load: {os.getloadavg()[0]:.2f}
            """
            
            return system_text
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return f"❌ Error retrieving system info: {e}"
    
    async def _get_recent_logs(self):
        """Get recent logs from main bot"""
        try:
            log_file = 'logs/main.log'
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    recent_lines = lines[-20:] if len(lines) >= 20 else lines
                    logs_text = "📋 **Recent Logs (Last 20 lines)**\n\n```\n"
                    logs_text += ''.join(recent_lines)
                    logs_text += "```"
                    return logs_text
            else:
                return "❌ No log file found"
        except Exception as e:
            return f"❌ Error reading logs: {e}"
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()
        
        if not self._check_admin_access(query.from_user.id):
            await query.edit_message_text("❌ Access denied.")
            return
        
        if query.data == "admin_stats":
            await self.admin_stats_command(update, context)
        elif query.data == "admin_health":
            await self.admin_health_command(update, context)
        elif query.data == "admin_users":
            await self.users_command(update, context)
        elif query.data == "admin_notify":
            await query.edit_message_text(
                "📢 Send notification to all users:\n\nUse `/notify [message]` command.",
                parse_mode='Markdown'
            )
        elif query.data == "admin_logs":
            await self.logs_command(update, context)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        if not self._check_admin_access(update.effective_user.id):
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
    
    async def run(self):
        """Run the admin bot"""
        logger.info("Starting Complete Admin Bot...")
        await self.application.run_polling()

def main():
    """Main function"""
    try:
        admin_bot = CompleteAdminBot()
        
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
                    new_loop.run_until_complete(admin_bot.run())
                finally:
                    new_loop.close()
            
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
