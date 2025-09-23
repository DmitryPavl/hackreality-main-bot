"""
Database Tests
Test database operations and data integrity.
"""

import pytest
import sqlite3
import tempfile
import os
from modules.database import DatabaseManager

class TestDatabase:
    """Test database operations"""
    
    @pytest.fixture
    def db_manager(self):
        """Create a temporary database for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        db_manager = DatabaseManager(db_path)
        yield db_manager
        
        # Cleanup
        os.unlink(db_path)
    
    @pytest.mark.asyncio
    async def test_database_initialization(self, db_manager):
        """Test database initialization"""
        # Check if tables were created
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = [
                'users', 'user_states', 'subscriptions', 'user_settings',
                'user_messages', 'bot_messages', 'user_preferences',
                'content_delivery', 'user_sessions', 'user_feedback'
            ]
            
            for table in expected_tables:
                assert table in tables, f"Table {table} not found"
    
    @pytest.mark.asyncio
    async def test_user_initialization(self, db_manager):
        """Test user initialization"""
        user_id = 12345
        username = "testuser"
        first_name = "Test"
        last_name = "User"
        
        await db_manager.initialize_user(user_id, username, first_name, last_name)
        
        # Check if user was created
        profile = await db_manager.get_user_profile(user_id)
        assert profile is not None
        assert profile['user_id'] == user_id
        assert profile['username'] == username
        assert profile['first_name'] == first_name
        assert profile['last_name'] == last_name
    
    @pytest.mark.asyncio
    async def test_user_state_management(self, db_manager):
        """Test user state management"""
        user_id = 12345
        
        # Set user state
        await db_manager.set_user_state(user_id, "onboarding", {"step": 1})
        
        # Get user state
        state = await db_manager.get_user_state(user_id)
        assert state == "onboarding"
        
        # Get state data
        state_data = await db_manager.get_user_state_data(user_id)
        assert state_data['step'] == 1
    
    @pytest.mark.asyncio
    async def test_subscription_creation(self, db_manager):
        """Test subscription creation"""
        user_id = 12345
        goal = "Test goal"
        plan = "extreme"
        
        # Create subscription
        order_id = await db_manager.create_subscription(user_id, goal, plan)
        assert order_id is not None
        
        # Get active subscription
        subscription = await db_manager.get_active_subscription(user_id)
        assert subscription is not None
        assert subscription['user_goal'] == goal
        assert subscription['subscription_type'] == plan
    
    @pytest.mark.asyncio
    async def test_message_storage(self, db_manager):
        """Test message storage"""
        user_id = 12345
        message_text = "Test message"
        
        # Store user message
        await db_manager.store_user_message(
            user_id=user_id,
            message_text=message_text,
            message_type="text",
            module_context="test",
            state_context="test"
        )
        
        # Store bot message
        await db_manager.store_bot_message(
            user_id=user_id,
            message_text="Bot response",
            message_type="text",
            module_context="test",
            state_context="test"
        )
        
        # Get messages
        messages = await db_manager.get_user_messages(user_id, limit=10)
        assert len(messages) >= 2
        
        # Check message content
        user_messages = [msg for msg in messages if msg['message_type'] == 'user_message']
        bot_messages = [msg for msg in messages if msg['message_type'] == 'bot_message']
        
        assert len(user_messages) >= 1
        assert len(bot_messages) >= 1
        assert user_messages[0]['message_text'] == message_text
