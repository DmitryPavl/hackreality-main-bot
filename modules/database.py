"""
Database Manager Module
Handles all database operations for the Telegram bot.
"""

import sqlite3
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "bot_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
            
            # Users table - Main user information
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    language TEXT DEFAULT 'ru',
                    city TEXT,
                    timezone TEXT,
                    timezone_offset TEXT,
                    timezone_name TEXT,
                    messaging_enabled BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User states table - Current state and temporary data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_states (
                    user_id INTEGER PRIMARY KEY,
                    current_state TEXT,
                    state_data TEXT,
                    onboarding_step INTEGER DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # User messages table - All messages from users
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message_text TEXT,
                    message_type TEXT DEFAULT 'text',
                    module_context TEXT,
                    state_context TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Bot messages table - All messages sent by bot
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message_text TEXT,
                    message_type TEXT DEFAULT 'text',
                    module_context TEXT,
                    state_context TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # User preferences table - Detailed user preferences
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id INTEGER PRIMARY KEY,
                    key_texts TEXT,
                    content_preferences TEXT,
                    delivery_preferences TEXT,
                    communication_preferences TEXT,
                    goals TEXT,
                    challenges TEXT,
                    setup_completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Subscriptions table - Subscription management (goal-oriented)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    order_id TEXT UNIQUE,
                    user_goal TEXT,
                    subscription_type TEXT,
                    plan_name TEXT,
                    plan_price TEXT,
                    plan_duration TEXT,
                    plan_approach TEXT,
                    plan_result_time TEXT,
                    status TEXT DEFAULT 'pending_payment',
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    payment_id TEXT,
                    payment_method TEXT,
                    auto_renewal BOOLEAN DEFAULT FALSE,
                    goal_achieved BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Content delivery table - All content sent to users
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS content_delivery (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    order_id TEXT,
                    content_type TEXT,
                    content_text TEXT,
                    delivery_method TEXT DEFAULT 'telegram',
                    delivery_status TEXT DEFAULT 'sent',
                    iteration_number INTEGER,
                    feedback TEXT,
                    feedback_rating INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    delivered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (order_id) REFERENCES subscriptions (order_id)
                )
            ''')
            
            # User sessions table - Track user interaction sessions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_end TIMESTAMP,
                    messages_count INTEGER DEFAULT 0,
                    modules_used TEXT,
                    session_data TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # User feedback table - Store all user feedback
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    feedback_type TEXT,
                    feedback_text TEXT,
                    rating INTEGER,
                    content_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (content_id) REFERENCES content_delivery (id)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_messages_user_id ON user_messages(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_messages_created_at ON user_messages(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_bot_messages_user_id ON bot_messages(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_bot_messages_sent_at ON bot_messages(sent_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_delivery_user_id ON content_delivery(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_delivery_delivered_at ON content_delivery(delivered_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_feedback_user_id ON user_feedback(user_id)')
            
            conn.commit()
            logger.info("Database initialized successfully with enhanced structure")
            
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during database initialization: {e}")
            raise
    
    async def initialize_user(self, user_id: int, username: str, first_name: str = None, last_name: str = None):
        """Initialize a new user in the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
            
            # Insert or update user
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, updated_at, last_activity)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (user_id, username, first_name, last_name))
            
            # Initialize user state
            cursor.execute('''
                INSERT OR REPLACE INTO user_states (user_id, current_state, state_data, onboarding_step, updated_at)
                VALUES (?, 'onboarding', '{}', 0, CURRENT_TIMESTAMP)
            ''', (user_id,))
            
            # Initialize user preferences
            cursor.execute('''
                INSERT OR IGNORE INTO user_preferences (user_id, setup_completed)
                VALUES (?, FALSE)
            ''', (user_id,))
            
            conn.commit()
            logger.info(f"User {user_id} initialized with enhanced structure")
            
        except sqlite3.Error as e:
            logger.error(f"Database error initializing user {user_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error initializing user {user_id}: {e}")
            raise
    
    async def get_user_state(self, user_id: int) -> Optional[str]:
        """Get user's current state"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT current_state FROM user_states WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    async def set_user_state(self, user_id: int, state: str, state_data: Dict[str, Any] = None):
        """Set user's current state"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            data_json = json.dumps(state_data or {})
            cursor.execute('''
                INSERT OR REPLACE INTO user_states (user_id, current_state, state_data, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, state, data_json))
            conn.commit()
    
    async def get_user_state_data(self, user_id: int) -> Dict[str, Any]:
        """Get user's state data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT state_data FROM user_states WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            if result and result[0]:
                return json.loads(result[0])
            return {}
    
    async def update_user_state_data(self, user_id: int, data: Dict[str, Any]):
        """Update user's state data"""
        current_data = await self.get_user_state_data(user_id)
        current_data.update(data)
        await self.set_user_state(user_id, await self.get_user_state(user_id), current_data)
    
    async def create_subscription(self, user_id: int, subscription_type: str, payment_id: str = None) -> int:
        """Create a new subscription"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Calculate end date based on subscription type
            start_date = datetime.now()
            if subscription_type == "extreme":
                end_date = start_date + timedelta(days=30)
            elif subscription_type == "2week":
                end_date = start_date + timedelta(days=14)
            else:  # regular
                end_date = start_date + timedelta(days=7)
            
            cursor.execute('''
                INSERT INTO subscriptions (user_id, subscription_type, status, start_date, end_date, payment_id)
                VALUES (?, ?, 'active', ?, ?, ?)
            ''', (user_id, subscription_type, start_date, end_date, payment_id))
            
            subscription_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Subscription created for user {user_id}: {subscription_type}")
            return subscription_id
    
    async def get_active_subscription(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user's active subscription"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM subscriptions 
                WHERE user_id = ? AND status = 'active' AND end_date > CURRENT_TIMESTAMP
                ORDER BY created_at DESC LIMIT 1
            ''', (user_id,))
            
            result = cursor.fetchone()
            if result:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, result))
            return None
    
    async def update_user_settings(self, user_id: int, key_texts: List[str], preferences: Dict[str, Any] = None):
        """Update user's settings and key texts"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            key_texts_json = json.dumps(key_texts)
            preferences_json = json.dumps(preferences or {})
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_settings (user_id, key_texts, preferences, setup_completed, updated_at)
                VALUES (?, ?, ?, TRUE, CURRENT_TIMESTAMP)
            ''', (user_id, key_texts_json, preferences_json))
            
            conn.commit()
            logger.info(f"User settings updated for user {user_id}")
    
    async def get_user_settings(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user's settings"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user_settings WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            if result:
                columns = [description[0] for description in cursor.description]
                data = dict(zip(columns, result))
                # Parse JSON fields
                if data.get('key_texts'):
                    data['key_texts'] = json.loads(data['key_texts'])
                if data.get('preferences'):
                    data['preferences'] = json.loads(data['preferences'])
                return data
            return None
    
    async def log_iteration(self, user_id: int, iteration_number: int, content: str, status: str = "sent"):
        """Log an iteration sent to user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO iterations (user_id, iteration_number, content, sent_at, status)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)
            ''', (user_id, iteration_number, content, status))
            conn.commit()
    
    async def get_user_iterations(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's iteration history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM content_delivery WHERE user_id = ? ORDER BY delivered_at DESC
            ''', (user_id,))
            
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in results]
    
    # New methods for enhanced user data management
    
    async def store_user_message(self, user_id: int, message_text: str, message_type: str = "text", 
                                module_context: str = None, state_context: str = None):
        """Store a message from user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_messages (user_id, message_text, message_type, module_context, state_context)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, message_text, message_type, module_context, state_context))
            
            # Update user's last activity
            cursor.execute('''
                UPDATE users SET last_activity = CURRENT_TIMESTAMP WHERE user_id = ?
            ''', (user_id,))
            
            conn.commit()
            logger.info(f"Stored user message from {user_id}")
    
    async def store_bot_message(self, user_id: int, message_text: str, message_type: str = "text",
                               module_context: str = None, state_context: str = None):
        """Store a message sent by bot"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO bot_messages (user_id, message_text, message_type, module_context, state_context)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, message_text, message_type, module_context, state_context))
            
            conn.commit()
            logger.info(f"Stored bot message to {user_id}")
    
    async def get_user_messages(self, user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get user's message history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM user_messages WHERE user_id = ? 
                ORDER BY created_at DESC LIMIT ?
            ''', (user_id, limit))
            
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in results]
    
    async def get_bot_messages(self, user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get bot's message history to user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM bot_messages WHERE user_id = ? 
                ORDER BY sent_at DESC LIMIT ?
            ''', (user_id, limit))
            
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in results]
    
    async def get_conversation_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get combined conversation history (user + bot messages)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 'user' as sender, message_text, created_at as timestamp, module_context, state_context
                FROM user_messages WHERE user_id = ?
                UNION ALL
                SELECT 'bot' as sender, message_text, sent_at as timestamp, module_context, state_context
                FROM bot_messages WHERE user_id = ?
                ORDER BY timestamp DESC LIMIT ?
            ''', (user_id, user_id, limit))
            
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in results]
    
    async def update_user_profile(self, user_id: int, **kwargs):
        """Update user profile information"""
        allowed_fields = ['username', 'first_name', 'last_name', 'language', 'city', 
                         'timezone', 'timezone_offset', 'timezone_name', 'messaging_enabled']
        
        update_fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                update_fields.append(f"{field} = ?")
                values.append(value)
        
        if not update_fields:
            return
        
        values.append(user_id)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE users SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', values)
            
            conn.commit()
            logger.info(f"Updated user profile for {user_id}")
    
    async def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get complete user profile"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            if result:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, result))
            return None
    
    async def store_user_feedback(self, user_id: int, feedback_type: str, feedback_text: str,
                                 rating: int = None, content_id: int = None):
        """Store user feedback"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_feedback (user_id, feedback_type, feedback_text, rating, content_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, feedback_type, feedback_text, rating, content_id))
            
            conn.commit()
            logger.info(f"Stored feedback from user {user_id}")
    
    async def get_user_feedback(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's feedback history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM user_feedback WHERE user_id = ? 
                ORDER BY created_at DESC LIMIT ?
            ''', (user_id, limit))
            
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in results]
    
    async def start_user_session(self, user_id: int) -> int:
        """Start a new user session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_sessions (user_id, session_start)
                VALUES (?, CURRENT_TIMESTAMP)
            ''', (user_id,))
            
            session_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Started session {session_id} for user {user_id}")
            return session_id
    
    async def end_user_session(self, session_id: int, messages_count: int = 0, 
                              modules_used: str = None, session_data: str = None):
        """End a user session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE user_sessions 
                SET session_end = CURRENT_TIMESTAMP, messages_count = ?, modules_used = ?, session_data = ?
                WHERE id = ?
            ''', (messages_count, modules_used, session_data, session_id))
            
            conn.commit()
            logger.info(f"Ended session {session_id}")
    
    async def get_user_sessions(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's session history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM user_sessions WHERE user_id = ? 
                ORDER BY session_start DESC LIMIT ?
            ''', (user_id, limit))
            
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in results]
    
    async def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get basic counts
            cursor.execute('SELECT COUNT(*) FROM user_messages WHERE user_id = ?', (user_id,))
            user_messages_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM bot_messages WHERE user_id = ?', (user_id,))
            bot_messages_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM content_delivery WHERE user_id = ?', (user_id,))
            content_delivered_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM user_feedback WHERE user_id = ?', (user_id,))
            feedback_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM user_sessions WHERE user_id = ?', (user_id,))
            sessions_count = cursor.fetchone()[0]
            
            # Get user profile
            profile = await self.get_user_profile(user_id)
            
            return {
                'user_id': user_id,
                'profile': profile,
                'statistics': {
                    'user_messages_count': user_messages_count,
                    'bot_messages_count': bot_messages_count,
                    'content_delivered_count': content_delivered_count,
                    'feedback_count': feedback_count,
                    'sessions_count': sessions_count
                }
            }
    
    async def create_subscription(self, user_id: int, order_id: str, user_goal: str, 
                                subscription_type: str, plan_details: dict) -> bool:
        """Create a new subscription/order for a specific goal"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO subscriptions (
                        user_id, order_id, user_goal, subscription_type,
                        plan_name, plan_price, plan_duration, plan_approach, plan_result_time,
                        status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ''', (
                    user_id, order_id, user_goal, subscription_type,
                    plan_details.get('name', ''), plan_details.get('price', ''),
                    plan_details.get('duration', ''), plan_details.get('approach', ''),
                    plan_details.get('result_time', ''), 'pending_payment'
                ))
                conn.commit()
                logger.info(f"Created subscription {order_id} for user {user_id}")
                return True
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            return False
    
    async def get_subscription_by_order_id(self, order_id: str) -> dict:
        """Get subscription details by order ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM subscriptions WHERE order_id = ?
                ''', (order_id,))
                result = cursor.fetchone()
                if result:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, result))
                return {}
        except Exception as e:
            logger.error(f"Error getting subscription: {e}")
            return {}
    
    async def update_subscription_status(self, order_id: str, status: str, 
                                       payment_id: str = None, payment_method: str = None) -> bool:
        """Update subscription status (e.g., after payment)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if payment_id and payment_method:
                    cursor.execute('''
                        UPDATE subscriptions 
                        SET status = ?, payment_id = ?, payment_method = ?, 
                            start_date = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                        WHERE order_id = ?
                    ''', (status, payment_id, payment_method, order_id))
                else:
                    cursor.execute('''
                        UPDATE subscriptions 
                        SET status = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE order_id = ?
                    ''', (status, order_id))
                conn.commit()
                logger.info(f"Updated subscription {order_id} status to {status}")
                return True
        except Exception as e:
            logger.error(f"Error updating subscription status: {e}")
            return False
    
    async def get_user_active_subscriptions(self, user_id: int) -> list:
        """Get all active subscriptions for a user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM subscriptions 
                    WHERE user_id = ? AND status IN ('active', 'pending_payment')
                    ORDER BY created_at DESC
                ''', (user_id,))
                results = cursor.fetchall()
                if results:
                    columns = [description[0] for description in cursor.description]
                    return [dict(zip(columns, result)) for result in results]
                return []
        except Exception as e:
            logger.error(f"Error getting user subscriptions: {e}")
            return []
    
    async def mark_goal_achieved(self, order_id: str) -> bool:
        """Mark a goal as achieved and end the subscription"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE subscriptions 
                    SET goal_achieved = TRUE, status = 'completed', 
                        end_date = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                    WHERE order_id = ?
                ''', (order_id,))
                conn.commit()
                logger.info(f"Marked goal as achieved for subscription {order_id}")
                return True
        except Exception as e:
            logger.error(f"Error marking goal as achieved: {e}")
            return False
