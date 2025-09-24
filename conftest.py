"""
Pytest configuration and fixtures for HackReality Bot tests
"""
import pytest
import asyncio
import tempfile
import os
import sys
from unittest.mock import Mock, AsyncMock
from telegram import Update, User, Message, CallbackQuery, Chat
from telegram.ext import ContextTypes

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set test environment variables
os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token'
os.environ['ADMIN_TELEGRAM_ID'] = '41107472'
os.environ['ADMIN_BOT_TOKEN'] = 'test_admin_token'

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_file.close()
    yield temp_file.name
    os.unlink(temp_file.name)

@pytest.fixture
def mock_user():
    """Create a mock Telegram user."""
    return User(
        id=12345,
        first_name="Test",
        last_name="User",
        username="testuser",
        is_bot=False
    )

@pytest.fixture
def mock_chat():
    """Create a mock Telegram chat."""
    return Chat(id=12345, type="private")

@pytest.fixture
def mock_message(mock_user, mock_chat):
    """Create a mock Telegram message."""
    return Message(
        message_id=1,
        from_user=mock_user,
        date=None,
        chat=mock_chat,
        text="/start"
    )

@pytest.fixture
def mock_callback_query(mock_user, mock_chat):
    """Create a mock Telegram callback query."""
    return CallbackQuery(
        id="test_callback_id",
        from_user=mock_user,
        chat_instance="test_chat_instance",
        data="continue_onboarding"
    )

@pytest.fixture
def mock_update(mock_message):
    """Create a mock Telegram update with message."""
    update = Update(update_id=1)
    update.message = mock_message
    update.callback_query = None
    return update

@pytest.fixture
def mock_update_callback(mock_callback_query):
    """Create a mock Telegram update with callback query."""
    update = Update(update_id=1)
    update.message = None
    update.callback_query = mock_callback_query
    return update

@pytest.fixture
def mock_context():
    """Create a mock context."""
    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot = Mock()
    context.bot.send_message = AsyncMock()
    context.bot.edit_message_text = AsyncMock()
    context.bot.answer_callback_query = AsyncMock()
    context.job_queue = Mock()
    context.job_queue.run_once = AsyncMock()
    return context

@pytest.fixture
def mock_db_manager(temp_db):
    """Create a mock database manager."""
    from modules.database import DatabaseManager
    
    db_manager = DatabaseManager(temp_db)
    # Initialize database for testing
    asyncio.run(db_manager.initialize_database())
    return db_manager

@pytest.fixture
def mock_state_manager():
    """Create a mock state manager."""
    from modules.user_state import UserStateManager
    
    state_manager = UserStateManager()
    return state_manager
