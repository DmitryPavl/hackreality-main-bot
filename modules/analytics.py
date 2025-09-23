"""
Analytics Module
Provides comprehensive analytics and tracking for the Telegram bot.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import sqlite3

logger = logging.getLogger(__name__)

class AnalyticsManager:
    """Centralized analytics and tracking management"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.analytics_data = {
            "user_engagement": defaultdict(list),
            "conversion_funnels": defaultdict(int),
            "feature_usage": defaultdict(int),
            "error_patterns": defaultdict(int),
            "performance_metrics": defaultdict(list)
        }
    
    async def track_user_action(self, user_id: int, action: str, details: Dict[str, Any] = None):
        """Track user actions for analytics"""
        try:
            action_data = {
                "user_id": user_id,
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "details": details or {}
            }
            
            # Store in database
            await self.db_manager.store_user_message(
                user_id=user_id,
                message_text=json.dumps(action_data),
                message_type="analytics_track",
                module_context="analytics",
                state_context=action
            )
            
            # Update in-memory analytics
            self.analytics_data["user_engagement"][user_id].append(action_data)
            
        except Exception as e:
            logger.error(f"Error tracking user action: {e}")
    
    async def track_conversion(self, user_id: int, conversion_type: str, value: Any = None):
        """Track conversion events"""
        try:
            conversion_data = {
                "user_id": user_id,
                "conversion_type": conversion_type,
                "value": value,
                "timestamp": datetime.now().isoformat()
            }
            
            # Store in database
            await self.db_manager.store_user_message(
                user_id=user_id,
                message_text=json.dumps(conversion_data),
                message_type="conversion_track",
                module_context="analytics",
                state_context=conversion_type
            )
            
            # Update conversion funnel
            self.analytics_data["conversion_funnels"][conversion_type] += 1
            
        except Exception as e:
            logger.error(f"Error tracking conversion: {e}")
    
    async def track_feature_usage(self, user_id: int, feature: str, usage_details: Dict[str, Any] = None):
        """Track feature usage"""
        try:
            usage_data = {
                "user_id": user_id,
                "feature": feature,
                "timestamp": datetime.now().isoformat(),
                "details": usage_details or {}
            }
            
            # Store in database
            await self.db_manager.store_user_message(
                user_id=user_id,
                message_text=json.dumps(usage_data),
                message_type="feature_usage",
                module_context="analytics",
                state_context=feature
            )
            
            # Update feature usage counter
            self.analytics_data["feature_usage"][feature] += 1
            
        except Exception as e:
            logger.error(f"Error tracking feature usage: {e}")
    
    async def track_error(self, error_type: str, error_details: Dict[str, Any] = None):
        """Track errors for analytics"""
        try:
            error_data = {
                "error_type": error_type,
                "timestamp": datetime.now().isoformat(),
                "details": error_details or {}
            }
            
            # Update error patterns
            self.analytics_data["error_patterns"][error_type] += 1
            
            # Log error for monitoring
            logger.error(f"Analytics tracked error: {error_type} - {error_details}")
            
        except Exception as e:
            logger.error(f"Error tracking error: {e}")
    
    async def get_user_analytics(self, user_id: int) -> Dict[str, Any]:
        """Get analytics for a specific user"""
        try:
            # Get user messages for analytics
            messages = await self.db_manager.get_user_messages(user_id, limit=1000)
            
            # Filter analytics messages
            analytics_messages = [msg for msg in messages if msg['message_type'] in [
                'analytics_track', 'conversion_track', 'feature_usage'
            ]]
            
            # Parse analytics data
            user_actions = []
            conversions = []
            feature_usage = []
            
            for msg in analytics_messages:
                try:
                    data = json.loads(msg['message_text'])
                    if msg['message_type'] == 'analytics_track':
                        user_actions.append(data)
                    elif msg['message_type'] == 'conversion_track':
                        conversions.append(data)
                    elif msg['message_type'] == 'feature_usage':
                        feature_usage.append(data)
                except json.JSONDecodeError:
                    continue
            
            # Calculate metrics
            total_actions = len(user_actions)
            total_conversions = len(conversions)
            total_feature_usage = len(feature_usage)
            
            # Get action frequency
            action_frequency = Counter([action['action'] for action in user_actions])
            
            # Get conversion types
            conversion_types = Counter([conv['conversion_type'] for conv in conversions])
            
            # Get feature usage
            features_used = Counter([usage['feature'] for usage in feature_usage])
            
            analytics = {
                "user_id": user_id,
                "total_actions": total_actions,
                "total_conversions": total_conversions,
                "total_feature_usage": total_feature_usage,
                "action_frequency": dict(action_frequency),
                "conversion_types": dict(conversion_types),
                "features_used": dict(features_used),
                "engagement_score": self._calculate_engagement_score(user_actions),
                "last_activity": user_actions[-1]['timestamp'] if user_actions else None
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting user analytics: {e}")
            return {}
    
    def _calculate_engagement_score(self, user_actions: List[Dict[str, Any]]) -> float:
        """Calculate user engagement score"""
        try:
            if not user_actions:
                return 0.0
            
            # Calculate score based on action frequency and recency
            now = datetime.now()
            recent_actions = 0
            total_score = 0
            
            for action in user_actions:
                action_time = datetime.fromisoformat(action['timestamp'])
                days_ago = (now - action_time).days
                
                # Weight recent actions more heavily
                if days_ago <= 1:
                    recent_actions += 1
                    total_score += 10
                elif days_ago <= 7:
                    total_score += 5
                elif days_ago <= 30:
                    total_score += 2
                else:
                    total_score += 1
            
            # Normalize score (0-100)
            max_possible_score = len(user_actions) * 10
            if max_possible_score == 0:
                return 0.0
            
            normalized_score = (total_score / max_possible_score) * 100
            return min(normalized_score, 100.0)
            
        except Exception as e:
            logger.error(f"Error calculating engagement score: {e}")
            return 0.0
    
    async def get_system_analytics(self) -> Dict[str, Any]:
        """Get system-wide analytics"""
        try:
            # Get database statistics
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Get total users
                cursor.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]
                
                # Get active users (last 30 days)
                cursor.execute("""
                    SELECT COUNT(DISTINCT user_id) FROM user_messages 
                    WHERE timestamp > datetime('now', '-30 days')
                """)
                active_users = cursor.fetchone()[0]
                
                # Get total messages
                cursor.execute("SELECT COUNT(*) FROM user_messages")
                total_messages = cursor.fetchone()[0]
                
                # Get messages by type
                cursor.execute("""
                    SELECT message_type, COUNT(*) 
                    FROM user_messages 
                    GROUP BY message_type
                """)
                messages_by_type = dict(cursor.fetchall())
                
                # Get user registrations by day (last 30 days)
                cursor.execute("""
                    SELECT DATE(created_at) as date, COUNT(*) 
                    FROM users 
                    WHERE created_at > datetime('now', '-30 days')
                    GROUP BY DATE(created_at)
                    ORDER BY date
                """)
                daily_registrations = dict(cursor.fetchall())
                
                # Get subscription statistics
                cursor.execute("""
                    SELECT subscription_type, COUNT(*) 
                    FROM subscriptions 
                    GROUP BY subscription_type
                """)
                subscription_stats = dict(cursor.fetchall())
                
                # Get completion rates
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
                    FROM subscriptions
                """)
                completion_data = cursor.fetchone()
                completion_rate = (completion_data[1] / completion_data[0] * 100) if completion_data[0] > 0 else 0
            
            analytics = {
                "timestamp": datetime.now().isoformat(),
                "user_metrics": {
                    "total_users": total_users,
                    "active_users_30d": active_users,
                    "user_retention_rate": (active_users / total_users * 100) if total_users > 0 else 0
                },
                "message_metrics": {
                    "total_messages": total_messages,
                    "messages_by_type": messages_by_type,
                    "avg_messages_per_user": total_messages / total_users if total_users > 0 else 0
                },
                "subscription_metrics": {
                    "subscription_distribution": subscription_stats,
                    "completion_rate": completion_rate
                },
                "growth_metrics": {
                    "daily_registrations": daily_registrations,
                    "total_registrations_30d": sum(daily_registrations.values())
                },
                "conversion_funnels": dict(self.analytics_data["conversion_funnels"]),
                "feature_usage": dict(self.analytics_data["feature_usage"]),
                "error_patterns": dict(self.analytics_data["error_patterns"])
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting system analytics: {e}")
            return {"error": str(e)}
    
    async def get_conversion_funnel_analysis(self) -> Dict[str, Any]:
        """Analyze conversion funnels"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Get funnel data
                cursor.execute("""
                    SELECT 
                        COUNT(DISTINCT u.user_id) as total_users,
                        COUNT(DISTINCT CASE WHEN s.user_id IS NOT NULL THEN u.user_id END) as users_with_subscription,
                        COUNT(DISTINCT CASE WHEN s.status = 'active' THEN u.user_id END) as active_subscriptions,
                        COUNT(DISTINCT CASE WHEN s.status = 'completed' THEN u.user_id END) as completed_subscriptions
                    FROM users u
                    LEFT JOIN subscriptions s ON u.user_id = s.user_id
                """)
                funnel_data = cursor.fetchone()
                
                total_users, users_with_subscription, active_subscriptions, completed_subscriptions = funnel_data
                
                # Calculate conversion rates
                subscription_rate = (users_with_subscription / total_users * 100) if total_users > 0 else 0
                activation_rate = (active_subscriptions / users_with_subscription * 100) if users_with_subscription > 0 else 0
                completion_rate = (completed_subscriptions / active_subscriptions * 100) if active_subscriptions > 0 else 0
                
                funnel_analysis = {
                    "total_users": total_users,
                    "users_with_subscription": users_with_subscription,
                    "active_subscriptions": active_subscriptions,
                    "completed_subscriptions": completed_subscriptions,
                    "conversion_rates": {
                        "subscription_rate": subscription_rate,
                        "activation_rate": activation_rate,
                        "completion_rate": completion_rate,
                        "overall_conversion_rate": (completed_subscriptions / total_users * 100) if total_users > 0 else 0
                    },
                    "funnel_stages": [
                        {"stage": "Users", "count": total_users, "rate": 100.0},
                        {"stage": "Subscribed", "count": users_with_subscription, "rate": subscription_rate},
                        {"stage": "Active", "count": active_subscriptions, "rate": activation_rate},
                        {"stage": "Completed", "count": completed_subscriptions, "rate": completion_rate}
                    ]
                }
                
                return funnel_analysis
                
        except Exception as e:
            logger.error(f"Error analyzing conversion funnel: {e}")
            return {"error": str(e)}
    
    async def get_user_engagement_analysis(self) -> Dict[str, Any]:
        """Analyze user engagement patterns"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Get engagement metrics
                cursor.execute("""
                    SELECT 
                        user_id,
                        COUNT(*) as message_count,
                        MIN(timestamp) as first_message,
                        MAX(timestamp) as last_message,
                        COUNT(DISTINCT DATE(timestamp)) as active_days
                    FROM user_messages 
                    WHERE message_type = 'user_message'
                    GROUP BY user_id
                """)
                engagement_data = cursor.fetchall()
                
                if not engagement_data:
                    return {"error": "No engagement data available"}
                
                # Calculate engagement metrics
                message_counts = [row[1] for row in engagement_data]
                active_days = [row[4] for row in engagement_data]
                
                engagement_analysis = {
                    "total_active_users": len(engagement_data),
                    "message_metrics": {
                        "avg_messages_per_user": sum(message_counts) / len(message_counts),
                        "median_messages_per_user": sorted(message_counts)[len(message_counts) // 2],
                        "max_messages_per_user": max(message_counts),
                        "min_messages_per_user": min(message_counts)
                    },
                    "activity_metrics": {
                        "avg_active_days": sum(active_days) / len(active_days),
                        "median_active_days": sorted(active_days)[len(active_days) // 2],
                        "max_active_days": max(active_days),
                        "min_active_days": min(active_days)
                    },
                    "engagement_segments": {
                        "high_engagement": len([count for count in message_counts if count >= 50]),
                        "medium_engagement": len([count for count in message_counts if 10 <= count < 50]),
                        "low_engagement": len([count for count in message_counts if count < 10])
                    }
                }
                
                return engagement_analysis
                
        except Exception as e:
            logger.error(f"Error analyzing user engagement: {e}")
            return {"error": str(e)}
    
    async def generate_analytics_report(self) -> str:
        """Generate comprehensive analytics report"""
        try:
            system_analytics = await self.get_system_analytics()
            funnel_analysis = await self.get_conversion_funnel_analysis()
            engagement_analysis = await self.get_user_engagement_analysis()
            
            report = f"""
📊 **Analytics Report - {datetime.now().strftime('%Y-%m-%d')}**

**👥 User Metrics:**
• Total users: {system_analytics.get('user_metrics', {}).get('total_users', 0)}
• Active users (30d): {system_analytics.get('user_metrics', {}).get('active_users_30d', 0)}
• Retention rate: {system_analytics.get('user_metrics', {}).get('user_retention_rate', 0):.1f}%

**💬 Message Metrics:**
• Total messages: {system_analytics.get('message_metrics', {}).get('total_messages', 0)}
• Avg messages per user: {system_analytics.get('message_metrics', {}).get('avg_messages_per_user', 0):.1f}

**📈 Conversion Funnel:**
• Subscription rate: {funnel_analysis.get('conversion_rates', {}).get('subscription_rate', 0):.1f}%
• Activation rate: {funnel_analysis.get('conversion_rates', {}).get('activation_rate', 0):.1f}%
• Completion rate: {funnel_analysis.get('conversion_rates', {}).get('completion_rate', 0):.1f}%
• Overall conversion: {funnel_analysis.get('conversion_rates', {}).get('overall_conversion_rate', 0):.1f}%

**🎯 Engagement Analysis:**
• High engagement users: {engagement_analysis.get('engagement_segments', {}).get('high_engagement', 0)}
• Medium engagement users: {engagement_analysis.get('engagement_segments', {}).get('medium_engagement', 0)}
• Low engagement users: {engagement_analysis.get('engagement_segments', {}).get('low_engagement', 0)}

**📊 Subscription Distribution:**
{self._format_subscription_distribution(system_analytics.get('subscription_metrics', {}).get('subscription_distribution', {}))}

**🔧 Feature Usage:**
{self._format_feature_usage(system_analytics.get('feature_usage', {}))}
            """
            
            return report.strip()
            
        except Exception as e:
            logger.error(f"Error generating analytics report: {e}")
            return f"Error generating analytics report: {e}"
    
    def _format_subscription_distribution(self, distribution: Dict[str, int]) -> str:
        """Format subscription distribution for report"""
        if not distribution:
            return "No subscription data available"
        
        total = sum(distribution.values())
        formatted = []
        
        for plan, count in distribution.items():
            percentage = (count / total * 100) if total > 0 else 0
            formatted.append(f"• {plan}: {count} ({percentage:.1f}%)")
        
        return "\n".join(formatted)
    
    def _format_feature_usage(self, usage: Dict[str, int]) -> str:
        """Format feature usage for report"""
        if not usage:
            return "No feature usage data available"
        
        # Sort by usage count
        sorted_usage = sorted(usage.items(), key=lambda x: x[1], reverse=True)
        formatted = []
        
        for feature, count in sorted_usage[:10]:  # Top 10 features
            formatted.append(f"• {feature}: {count}")
        
        return "\n".join(formatted)
    
    async def export_analytics_data(self, format: str = "json") -> str:
        """Export analytics data in specified format"""
        try:
            system_analytics = await self.get_system_analytics()
            funnel_analysis = await self.get_conversion_funnel_analysis()
            engagement_analysis = await self.get_user_engagement_analysis()
            
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "system_analytics": system_analytics,
                "funnel_analysis": funnel_analysis,
                "engagement_analysis": engagement_analysis
            }
            
            if format.lower() == "json":
                return json.dumps(export_data, indent=2, ensure_ascii=False)
            else:
                return str(export_data)
                
        except Exception as e:
            logger.error(f"Error exporting analytics data: {e}")
            return f"Error exporting data: {e}"
