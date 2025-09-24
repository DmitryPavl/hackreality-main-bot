"""
Tests for database operations and user data management
"""
import pytest
import asyncio
from modules.database import DatabaseManager


class TestDatabaseOperations:
    """Test database operations and user data management."""
    
    @pytest.mark.asyncio
    async def test_database_initialization(self, temp_db):
        """Test that database initializes correctly."""
        db_manager = DatabaseManager(temp_db)
        db_manager.init_database()
        
        # Database should be initialized without errors
        assert True  # If we get here, initialization succeeded
    
    @pytest.mark.asyncio
    async def test_user_initialization(self, temp_db, mock_user):
        """Test that user initialization works correctly."""
        db_manager = DatabaseManager(temp_db)
        db_manager.init_database()
        
        # Initialize user
        await db_manager.initialize_user(
            user_id=mock_user.id,
            username=mock_user.username,
            first_name=mock_user.first_name,
            last_name=mock_user.last_name
        )
        
        # Verify user was created
        user_data = await db_manager.get_user_profile(mock_user.id)
        assert user_data is not None
        assert user_data["user_id"] == mock_user.id
        assert user_data["username"] == mock_user.username
        assert user_data["first_name"] == mock_user.first_name
    
    @pytest.mark.asyncio
    async def test_user_state_management(self, temp_db, mock_user):
        """Test user state management in database."""
        db_manager = DatabaseManager(temp_db)
        db_manager.init_database()
        await db_manager.initialize_user(mock_user.id, mock_user.username, mock_user.first_name)
        
        # Test setting and getting user state
        test_state = "onboarding"
        test_data = {"step": 1, "data": "test"}
        
        await db_manager.set_user_state(mock_user.id, test_state, test_data)
        
        # Verify state was set
        retrieved_state = await db_manager.get_user_state(mock_user.id)
        assert retrieved_state == test_state
        
        # Verify state data was set
        retrieved_data = await db_manager.get_user_state_data(mock_user.id)
        assert retrieved_data == test_data
    
    @pytest.mark.asyncio
    async def test_user_state_updates(self, temp_db, mock_user):
        """Test updating user state data."""
        db_manager = DatabaseManager(temp_db)
        db_manager.init_database()
        await db_manager.initialize_user(mock_user.id, mock_user.username, mock_user.first_name)
        
        # Set initial state
        initial_data = {"step": 1, "name": "test"}
        await db_manager.set_user_state(mock_user.id, "onboarding", initial_data)
        
        # Update state data
        update_data = {"step": 2, "age": 25}
        await db_manager.update_user_state_data(mock_user.id, update_data)
        
        # Verify updated data
        final_data = await db_manager.get_user_state_data(mock_user.id)
        assert final_data["step"] == 2  # Updated
        assert final_data["name"] == "test"  # Preserved
        assert final_data["age"] == 25  # Added
    
    @pytest.mark.asyncio
    async def test_message_storage(self, temp_db, mock_user):
        """Test message storage functionality."""
        db_manager = DatabaseManager(temp_db)
        db_manager.init_database()
        await db_manager.initialize_user(mock_user.id, mock_user.username, mock_user.first_name)
        
        # Store user message
        await db_manager.store_user_message(
            user_id=mock_user.id,
            message_text="Hello bot!",
            message_type="text",
            module_context="onboarding"
        )
        
        # Store bot message
        await db_manager.store_bot_message(
            user_id=mock_user.id,
            message_text="Hello user!",
            module_context="onboarding"
        )
        
        # Verify messages were stored
        user_messages = await db_manager.get_user_messages(mock_user.id)
        bot_messages = await db_manager.get_bot_messages(mock_user.id)
        
        assert len(user_messages) == 1
        assert len(bot_messages) == 1
        assert user_messages[0]["message_text"] == "Hello bot!"
        assert bot_messages[0]["message_text"] == "Hello user!"
    
    @pytest.mark.asyncio
    async def test_subscription_management(self, temp_db, mock_user):
        """Test subscription and goal management."""
        db_manager = DatabaseManager(temp_db)
        db_manager.init_database()
        await db_manager.initialize_user(mock_user.id, mock_user.username, mock_user.first_name)
        
        # Create subscription
        subscription_id = await db_manager.create_subscription(
            user_id=mock_user.id,
            order_id="test_order_123",
            user_goal="Test goal",
            subscription_type="extreme",
            plan_details={
                "name": "Extreme Plan",
                "price": "1000",
                "duration": "1 week",
                "approach": "intensive",
                "result_time": "1 week"
            }
        )
        
        # Verify subscription was created
        assert subscription_id is True
        subscription = await db_manager.get_subscription_by_order_id("test_order_123")
        assert subscription is not None
        assert subscription["user_goal"] == "Test goal"
        assert subscription["subscription_type"] == "extreme"
        assert subscription["status"] == "pending_payment"
    
    @pytest.mark.asyncio
    async def test_focus_statements_management(self, temp_db, mock_user):
        """Test focus statements management."""
        db_manager = DatabaseManager(temp_db)
        db_manager.init_database()
        await db_manager.initialize_user(mock_user.id, mock_user.username, mock_user.first_name)
        
        # Create subscription first
        subscription_id = await db_manager.create_subscription(
            user_id=mock_user.id,
            order_id="test_order_123",
            user_goal="Test goal",
            subscription_type="extreme",
            plan_details={
                "name": "Extreme Plan",
                "price": "1000",
                "duration": "1 week",
                "approach": "intensive",
                "result_time": "1 week"
            }
        )
        
        # Add focus statements
        statements = ["I feel confident", "I feel successful", "I feel motivated"]
        for i, statement in enumerate(statements):
            await db_manager.add_focus_statement(
                subscription_id=subscription_id,
                statement_text=statement,
                statement_order=i
            )
        
        # Verify focus statements were added
        focus_statements = await db_manager.get_focus_statements(subscription_id)
        assert len(focus_statements) == 3
        
        # Check statement order
        for i, statement in enumerate(focus_statements):
            assert statement["statement_order"] == i
            assert statement["statement_text"] == statements[i]
    
    @pytest.mark.asyncio
    async def test_task_management(self, temp_db, mock_user):
        """Test task management functionality."""
        db_manager = DatabaseManager(temp_db)
        db_manager.init_database()
        await db_manager.initialize_user(mock_user.id, mock_user.username, mock_user.first_name)
        
        # Create subscription and focus statement
        subscription_id = await db_manager.create_subscription(
            user_id=mock_user.id,
            order_id="test_order_123",
            user_goal="Test goal",
            subscription_type="extreme",
            plan_details={
                "name": "Extreme Plan",
                "price": "1000",
                "duration": "1 week",
                "approach": "intensive",
                "result_time": "1 week"
            }
        )
        
        focus_statement_id = await db_manager.add_focus_statement(
            subscription_id=subscription_id,
            statement_text="I feel confident",
            statement_order=0
        )
        
        # Add tasks
        tasks = ["Task 1", "Task 2", "Task 3"]
        for i, task_text in enumerate(tasks):
            await db_manager.add_task(
                focus_statement_id=focus_statement_id,
                task_text=task_text,
                task_order=i
            )
        
        # Verify tasks were added
        tasks_list = await db_manager.get_tasks(focus_statement_id)
        assert len(tasks_list) == 3
        
        # Check task order
        for i, task in enumerate(tasks_list):
            assert task["task_order"] == i
            assert task["task_text"] == tasks[i]
    
    @pytest.mark.asyncio
    async def test_active_task_management(self, temp_db, mock_user):
        """Test active task management."""
        db_manager = DatabaseManager(temp_db)
        db_manager.init_database()
        await db_manager.initialize_user(mock_user.id, mock_user.username, mock_user.first_name)
        
        # Create subscription, focus statement, and task
        subscription_id = await db_manager.create_subscription(
            user_id=mock_user.id,
            order_id="test_order_123",
            user_goal="Test goal",
            subscription_type="extreme",
            plan_details={
                "name": "Extreme Plan",
                "price": "1000",
                "duration": "1 week",
                "approach": "intensive",
                "result_time": "1 week"
            }
        )
        
        focus_statement_id = await db_manager.add_focus_statement(
            subscription_id=subscription_id,
            statement_text="I feel confident",
            statement_order=0
        )
        
        task_id = await db_manager.add_task(
            focus_statement_id=focus_statement_id,
            task_text="Test task",
            task_order=0
        )
        
        # Set active task
        await db_manager.set_active_task(mock_user.id, task_id, "User's action plan")
        
        # Verify active task was set
        active_task = await db_manager.get_active_task(mock_user.id)
        assert active_task is not None
        assert active_task["task_id"] == task_id
        assert active_task["user_action"] == "User's action plan"
        assert active_task["status"] == "pending"
    
    @pytest.mark.asyncio
    async def test_database_concurrent_access(self, temp_db, mock_user):
        """Test database handles concurrent access correctly."""
        db_manager = DatabaseManager(temp_db)
        db_manager.init_database()
        await db_manager.initialize_user(mock_user.id, mock_user.username, mock_user.first_name)
        
        # Simulate concurrent operations
        async def update_user_data(step):
            await db_manager.set_user_state(mock_user.id, "onboarding", {"step": step})
            return await db_manager.get_user_state_data(mock_user.id)
        
        # Run concurrent operations
        results = await asyncio.gather(
            update_user_data(1),
            update_user_data(2),
            update_user_data(3),
            return_exceptions=True
        )
        
        # All operations should complete without exceptions
        for result in results:
            assert not isinstance(result, Exception)
        
        # Final state should be consistent
        final_state = await db_manager.get_user_state_data(mock_user.id)
        assert "step" in final_state
