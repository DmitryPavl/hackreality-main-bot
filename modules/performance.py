"""
Performance Module
Provides performance optimization and caching for the Telegram bot.
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from functools import lru_cache, wraps
import sqlite3

logger = logging.getLogger(__name__)

class PerformanceManager:
    """Centralized performance management and optimization"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.cache = {}
        self.cache_ttl = {}
        self.performance_metrics = {
            "db_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "slow_queries": 0,
            "average_response_time": 0.0
        }
        self.slow_query_threshold = 1.0  # seconds
    
    def cache_result(self, key: str, value: Any, ttl_seconds: int = 300):
        """Cache a result with TTL"""
        try:
            self.cache[key] = value
            self.cache_ttl[key] = time.time() + ttl_seconds
        except Exception as e:
            logger.error(f"Error caching result: {e}")
    
    def get_cached_result(self, key: str) -> Optional[Any]:
        """Get cached result if still valid"""
        try:
            if key in self.cache:
                if time.time() < self.cache_ttl.get(key, 0):
                    self.performance_metrics["cache_hits"] += 1
                    return self.cache[key]
                else:
                    # Expired, remove from cache
                    del self.cache[key]
                    del self.cache_ttl[key]
            
            self.performance_metrics["cache_misses"] += 1
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached result: {e}")
            return None
    
    def clear_cache(self):
        """Clear all cached data"""
        try:
            self.cache.clear()
            self.cache_ttl.clear()
            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    def measure_time(self, func_name: str):
        """Decorator to measure function execution time"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # Update performance metrics
                    self.performance_metrics["average_response_time"] = (
                        (self.performance_metrics["average_response_time"] + execution_time) / 2
                    )
                    
                    if execution_time > self.slow_query_threshold:
                        self.performance_metrics["slow_queries"] += 1
                        logger.warning(f"Slow {func_name}: {execution_time:.2f}s")
                    
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    logger.error(f"Error in {func_name} after {execution_time:.2f}s: {e}")
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    if execution_time > self.slow_query_threshold:
                        self.performance_metrics["slow_queries"] += 1
                        logger.warning(f"Slow {func_name}: {execution_time:.2f}s")
                    
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    logger.error(f"Error in {func_name} after {execution_time:.2f}s: {e}")
                    raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    async def optimize_database(self):
        """Optimize database performance"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Analyze database for query optimization
                cursor.execute("ANALYZE")
                
                # Vacuum database to reclaim space
                cursor.execute("VACUUM")
                
                # Update statistics
                cursor.execute("PRAGMA optimize")
                
                conn.commit()
                logger.info("Database optimization completed")
                
        except Exception as e:
            logger.error(f"Error optimizing database: {e}")
    
    async def get_cached_user_state(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user state with caching"""
        try:
            cache_key = f"user_state_{user_id}"
            cached_result = self.get_cached_result(cache_key)
            
            if cached_result is not None:
                return cached_result
            
            # Get from database
            state_data = await self.db_manager.get_user_state_data(user_id)
            
            # Cache for 5 minutes
            self.cache_result(cache_key, state_data, 300)
            
            return state_data
            
        except Exception as e:
            logger.error(f"Error getting cached user state: {e}")
            return None
    
    async def get_cached_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user profile with caching"""
        try:
            cache_key = f"user_profile_{user_id}"
            cached_result = self.get_cached_result(cache_key)
            
            if cached_result is not None:
                return cached_result
            
            # Get from database
            profile = await self.db_manager.get_user_profile(user_id)
            
            # Cache for 10 minutes
            self.cache_result(cache_key, profile, 600)
            
            return profile
            
        except Exception as e:
            logger.error(f"Error getting cached user profile: {e}")
            return None
    
    async def get_cached_subscription(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user subscription with caching"""
        try:
            cache_key = f"subscription_{user_id}"
            cached_result = self.get_cached_result(cache_key)
            
            if cached_result is not None:
                return cached_result
            
            # Get from database
            subscription = await self.db_manager.get_active_subscription(user_id)
            
            # Cache for 5 minutes
            self.cache_result(cache_key, subscription, 300)
            
            return subscription
            
        except Exception as e:
            logger.error(f"Error getting cached subscription: {e}")
            return None
    
    def invalidate_user_cache(self, user_id: int):
        """Invalidate all cached data for a user"""
        try:
            cache_keys_to_remove = [
                f"user_state_{user_id}",
                f"user_profile_{user_id}",
                f"subscription_{user_id}"
            ]
            
            for key in cache_keys_to_remove:
                if key in self.cache:
                    del self.cache[key]
                if key in self.cache_ttl:
                    del self.cache_ttl[key]
            
            logger.debug(f"Cache invalidated for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error invalidating user cache: {e}")
    
    async def batch_process_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple messages in batch for better performance"""
        try:
            if not messages:
                return []
            
            # Group messages by user_id for batch processing
            user_messages = {}
            for message in messages:
                user_id = message.get('user_id')
                if user_id:
                    if user_id not in user_messages:
                        user_messages[user_id] = []
                    user_messages[user_id].append(message)
            
            # Process each user's messages
            results = []
            for user_id, user_msg_list in user_messages.items():
                # Get user state once for all messages
                user_state = await self.get_cached_user_state(user_id)
                
                for message in user_msg_list:
                    # Process message with cached state
                    result = await self._process_single_message(message, user_state)
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error batch processing messages: {e}")
            return []
    
    async def _process_single_message(self, message: Dict[str, Any], user_state: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single message with pre-loaded user state"""
        try:
            # Process message logic here
            # This is a placeholder for actual message processing
            return {
                "message_id": message.get('id'),
                "processed": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing single message: {e}")
            return {"error": str(e)}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        try:
            cache_size = len(self.cache)
            cache_hit_rate = 0.0
            
            total_requests = self.performance_metrics["cache_hits"] + self.performance_metrics["cache_misses"]
            if total_requests > 0:
                cache_hit_rate = (self.performance_metrics["cache_hits"] / total_requests) * 100
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cache_size": cache_size,
                "cache_hit_rate": cache_hit_rate,
                "db_queries": self.performance_metrics["db_queries"],
                "slow_queries": self.performance_metrics["slow_queries"],
                "average_response_time": self.performance_metrics["average_response_time"],
                "performance_status": "good" if cache_hit_rate > 70 and self.performance_metrics["slow_queries"] < 10 else "needs_optimization"
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {"error": str(e)}
    
    async def cleanup_old_cache(self):
        """Clean up expired cache entries"""
        try:
            current_time = time.time()
            expired_keys = []
            
            for key, expiry_time in self.cache_ttl.items():
                if current_time >= expiry_time:
                    expired_keys.append(key)
            
            for key in expired_keys:
                if key in self.cache:
                    del self.cache[key]
                if key in self.cache_ttl:
                    del self.cache_ttl[key]
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
                
        except Exception as e:
            logger.error(f"Error cleaning up old cache: {e}")
    
    async def preload_frequent_data(self):
        """Preload frequently accessed data into cache"""
        try:
            # This would preload common data like user states, profiles, etc.
            # For now, it's a placeholder
            logger.info("Preloading frequent data...")
            
            # Example: Preload active user states
            # This would be implemented based on actual usage patterns
            
        except Exception as e:
            logger.error(f"Error preloading frequent data: {e}")
    
    def optimize_memory_usage(self):
        """Optimize memory usage by cleaning up unused data"""
        try:
            # Clear old cache entries
            asyncio.create_task(self.cleanup_old_cache())
            
            # Force garbage collection
            import gc
            gc.collect()
            
            logger.info("Memory optimization completed")
            
        except Exception as e:
            logger.error(f"Error optimizing memory usage: {e}")
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database performance statistics"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Get database size
                cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
                db_size = cursor.fetchone()[0]
                
                # Get table sizes
                cursor.execute("""
                    SELECT name, 
                           (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=m.name) as row_count
                    FROM sqlite_master m 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                table_stats = cursor.fetchall()
                
                stats = {
                    "database_size_bytes": db_size,
                    "database_size_mb": db_size / (1024 * 1024),
                    "table_count": len(table_stats),
                    "tables": [{"name": name, "rows": row_count} for name, row_count in table_stats]
                }
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {"error": str(e)}
