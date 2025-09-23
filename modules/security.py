"""
Security Module
Provides security utilities and rate limiting for the Telegram bot.
"""

import time
import hashlib
import secrets
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class SecurityManager:
    """Centralized security management"""
    
    def __init__(self):
        self.rate_limits = defaultdict(lambda: deque())
        self.blocked_users = set()
        self.suspicious_activities = defaultdict(list)
        self.max_requests_per_minute = 30
        self.max_requests_per_hour = 200
        self.block_duration_minutes = 60
        
    def check_rate_limit(self, user_id: int) -> Tuple[bool, str]:
        """Check if user is within rate limits"""
        try:
            current_time = time.time()
            user_requests = self.rate_limits[user_id]
            
            # Remove old requests (older than 1 hour)
            while user_requests and user_requests[0] < current_time - 3600:
                user_requests.popleft()
            
            # Check hourly limit
            if len(user_requests) >= self.max_requests_per_hour:
                self._block_user(user_id, "Hourly rate limit exceeded")
                return False, "Rate limit exceeded. Please try again later."
            
            # Check minute limit
            recent_requests = [req for req in user_requests if req > current_time - 60]
            if len(recent_requests) >= self.max_requests_per_minute:
                self._block_user(user_id, "Minute rate limit exceeded")
                return False, "Too many requests. Please slow down."
            
            # Add current request
            user_requests.append(current_time)
            
            return True, "OK"
            
        except Exception as e:
            logger.error(f"Error checking rate limit for user {user_id}: {e}")
            return False, "Rate limit check failed"
    
    def _block_user(self, user_id: int, reason: str):
        """Block user temporarily"""
        try:
            self.blocked_users.add(user_id)
            self.suspicious_activities[user_id].append({
                "timestamp": datetime.now().isoformat(),
                "reason": reason,
                "action": "blocked"
            })
            
            logger.warning(f"User {user_id} blocked: {reason}")
            
            # Schedule unblock
            self._schedule_unblock(user_id)
            
        except Exception as e:
            logger.error(f"Error blocking user {user_id}: {e}")
    
    def _schedule_unblock(self, user_id: int):
        """Schedule user unblock after block duration"""
        try:
            # In a real implementation, you'd use a proper scheduler
            # For now, we'll check during rate limit checks
            pass
        except Exception as e:
            logger.error(f"Error scheduling unblock for user {user_id}: {e}")
    
    def is_user_blocked(self, user_id: int) -> bool:
        """Check if user is currently blocked"""
        return user_id in self.blocked_users
    
    def unblock_user(self, user_id: int):
        """Manually unblock a user"""
        try:
            self.blocked_users.discard(user_id)
            logger.info(f"User {user_id} unblocked manually")
        except Exception as e:
            logger.error(f"Error unblocking user {user_id}: {e}")
    
    def detect_suspicious_activity(self, user_id: int, activity_type: str, details: Dict) -> bool:
        """Detect suspicious user activity"""
        try:
            current_time = datetime.now()
            
            # Get recent activities for this user
            recent_activities = [
                activity for activity in self.suspicious_activities[user_id]
                if datetime.fromisoformat(activity["timestamp"]) > current_time - timedelta(hours=1)
            ]
            
            # Check for patterns
            suspicious = False
            reason = ""
            
            # Pattern 1: Too many failed attempts
            failed_attempts = [a for a in recent_activities if "failed" in a.get("reason", "").lower()]
            if len(failed_attempts) >= 5:
                suspicious = True
                reason = "Multiple failed attempts detected"
            
            # Pattern 2: Rapid repeated actions
            if len(recent_activities) >= 20:
                suspicious = True
                reason = "Excessive activity detected"
            
            # Pattern 3: Unusual message patterns
            if activity_type == "message" and details.get("message_length", 0) > 2000:
                suspicious = True
                reason = "Unusually long message detected"
            
            if suspicious:
                self.suspicious_activities[user_id].append({
                    "timestamp": current_time.isoformat(),
                    "reason": reason,
                    "activity_type": activity_type,
                    "details": details
                })
                
                logger.warning(f"Suspicious activity detected for user {user_id}: {reason}")
                
                # Block user if too many suspicious activities
                if len(recent_activities) >= 10:
                    self._block_user(user_id, f"Multiple suspicious activities: {reason}")
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting suspicious activity for user {user_id}: {e}")
            return False
    
    def validate_message_content(self, message: str) -> Tuple[bool, str]:
        """Validate message content for security"""
        try:
            if not message or not isinstance(message, str):
                return False, "Invalid message format"
            
            # Check length
            if len(message) > 4000:
                return False, "Message too long"
            
            # Check for potential XSS
            dangerous_patterns = [
                '<script', 'javascript:', 'data:', 'vbscript:',
                'onload=', 'onerror=', 'onclick=', 'onmouseover=',
                'eval(', 'document.cookie', 'window.location'
            ]
            
            message_lower = message.lower()
            for pattern in dangerous_patterns:
                if pattern in message_lower:
                    return False, f"Potentially dangerous content detected: {pattern}"
            
            # Check for SQL injection patterns
            sql_patterns = [
                'union select', 'drop table', 'delete from', 'insert into',
                'update set', 'alter table', 'create table'
            ]
            
            for pattern in sql_patterns:
                if pattern in message_lower:
                    return False, f"Potential SQL injection detected: {pattern}"
            
            # Check for spam patterns
            spam_patterns = [
                'http://', 'https://', 'www.', '.com', '.ru', '.org',
                'bitcoin', 'crypto', 'investment', 'earn money'
            ]
            
            spam_count = sum(1 for pattern in spam_patterns if pattern in message_lower)
            if spam_count >= 3:
                return False, "Potential spam detected"
            
            return True, "OK"
            
        except Exception as e:
            logger.error(f"Error validating message content: {e}")
            return False, "Content validation failed"
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for security"""
        try:
            if not filename:
                return "unnamed"
            
            # Remove dangerous characters
            dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
            sanitized = filename
            
            for char in dangerous_chars:
                sanitized = sanitized.replace(char, '_')
            
            # Limit length
            if len(sanitized) > 100:
                sanitized = sanitized[:100]
            
            # Ensure it's not empty
            if not sanitized.strip():
                sanitized = "unnamed"
            
            return sanitized.strip()
            
        except Exception as e:
            logger.error(f"Error sanitizing filename: {e}")
            return "unnamed"
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a secure random token"""
        try:
            return secrets.token_urlsafe(length)
        except Exception as e:
            logger.error(f"Error generating secure token: {e}")
            return hashlib.sha256(str(time.time()).encode()).hexdigest()[:length]
    
    def hash_sensitive_data(self, data: str) -> str:
        """Hash sensitive data for storage"""
        try:
            return hashlib.sha256(data.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error hashing sensitive data: {e}")
            return ""
    
    def verify_admin_access(self, user_id: int, admin_ids: List[int]) -> bool:
        """Verify if user has admin access"""
        try:
            return user_id in admin_ids
        except Exception as e:
            logger.error(f"Error verifying admin access for user {user_id}: {e}")
            return False
    
    def get_security_report(self) -> Dict:
        """Get security status report"""
        try:
            current_time = time.time()
            
            # Count active rate limits
            active_rate_limits = 0
            for user_requests in self.rate_limits.values():
                recent_requests = [req for req in user_requests if req > current_time - 3600]
                if recent_requests:
                    active_rate_limits += 1
            
            # Count blocked users
            blocked_count = len(self.blocked_users)
            
            # Count suspicious activities in last hour
            recent_suspicious = 0
            for activities in self.suspicious_activities.values():
                recent_activities = [
                    activity for activity in activities
                    if datetime.fromisoformat(activity["timestamp"]) > datetime.now() - timedelta(hours=1)
                ]
                recent_suspicious += len(recent_activities)
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "active_rate_limits": active_rate_limits,
                "blocked_users": blocked_count,
                "recent_suspicious_activities": recent_suspicious,
                "security_status": "healthy" if blocked_count < 5 and recent_suspicious < 10 else "warning"
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating security report: {e}")
            return {"error": str(e)}
    
    def cleanup_old_data(self):
        """Clean up old rate limit and activity data"""
        try:
            current_time = time.time()
            cutoff_time = current_time - 86400  # 24 hours ago
            
            # Clean up rate limits
            for user_id in list(self.rate_limits.keys()):
                user_requests = self.rate_limits[user_id]
                # Remove old requests
                while user_requests and user_requests[0] < cutoff_time:
                    user_requests.popleft()
                
                # Remove empty rate limits
                if not user_requests:
                    del self.rate_limits[user_id]
            
            # Clean up suspicious activities
            cutoff_datetime = datetime.now() - timedelta(days=7)
            for user_id in list(self.suspicious_activities.keys()):
                activities = self.suspicious_activities[user_id]
                # Remove old activities
                self.suspicious_activities[user_id] = [
                    activity for activity in activities
                    if datetime.fromisoformat(activity["timestamp"]) > cutoff_datetime
                ]
                
                # Remove empty activity lists
                if not self.suspicious_activities[user_id]:
                    del self.suspicious_activities[user_id]
            
            logger.info("Security data cleanup completed")
            
        except Exception as e:
            logger.error(f"Error cleaning up security data: {e}")
