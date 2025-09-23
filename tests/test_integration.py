"""
Integration Tests
Test complete user flows and module interactions.
"""

import pytest
import tempfile
import os
from modules.database import DatabaseManager
from modules.user_state import UserStateManager
from modules.onboarding import OnboardingModule
from modules.option import OptionModule

class TestIntegration:
    """Test integration between modules"""
    
    @pytest.fixture
    def test_environment(self):
        """Create test environment with all modules"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        db_manager = DatabaseManager(db_path)
        state_manager = UserStateManager(db_manager)
        
        yield {
            'db_manager': db_manager,
            'state_manager': state_manager,
            'db_path': db_path
        }
        
        # Cleanup
        os.unlink(db_path)
    
    @pytest.mark.asyncio
    async def test_complete_user_flow(self, test_environment):
        """Test complete user flow from start to finish"""
        db_manager = test_environment['db_manager']
        state_manager = test_environment['state_manager']
        
        user_id = 12345
        
        # Step 1: Initialize user
        await db_manager.initialize_user(user_id, "testuser", "Test", "User")
        
        # Step 2: Set onboarding state
        await state_manager.set_user_state(user_id, "onboarding", {"step": 0})
        
        # Step 3: Verify state
        state = await state_manager.get_user_state(user_id)
        assert state == "onboarding"
        
        # Step 4: Create subscription
        order_id = await db_manager.create_subscription(user_id, "Test goal", "extreme")
        assert order_id is not None
        
        # Step 5: Verify subscription
        subscription = await db_manager.get_active_subscription(user_id)
        assert subscription is not None
        assert subscription['user_goal'] == "Test goal"
        assert subscription['subscription_type'] == "extreme"
    
    @pytest.mark.asyncio
    async def test_state_transitions(self, test_environment):
        """Test state transitions between modules"""
        db_manager = test_environment['db_manager']
        state_manager = test_environment['state_manager']
        
        user_id = 12345
        await db_manager.initialize_user(user_id, "testuser", "Test", "User")
        
        # Test state transitions
        states = ["onboarding", "option_selection", "setup", "payment", "active"]
        
        for state in states:
            await state_manager.set_user_state(user_id, state, {"test": "data"})
            current_state = await state_manager.get_user_state(user_id)
            assert current_state == state
    
    @pytest.mark.asyncio
    async def test_data_persistence(self, test_environment):
        """Test data persistence across operations"""
        db_manager = test_environment['db_manager']
        state_manager = test_environment['state_manager']
        
        user_id = 12345
        await db_manager.initialize_user(user_id, "testuser", "Test", "User")
        
        # Store some data
        test_data = {
            "goal": "Test goal",
            "plan": "extreme",
            "step": 5,
            "custom_field": "custom_value"
        }
        
        await state_manager.set_user_state(user_id, "setup", test_data)
        
        # Retrieve and verify data
        retrieved_data = await state_manager.get_user_state_data(user_id)
        assert retrieved_data['goal'] == test_data['goal']
        assert retrieved_data['plan'] == test_data['plan']
        assert retrieved_data['step'] == test_data['step']
        assert retrieved_data['custom_field'] == test_data['custom_field']
    
    @pytest.mark.asyncio
    async def test_error_recovery(self, test_environment):
        """Test error recovery and data integrity"""
        db_manager = test_environment['db_manager']
        state_manager = test_environment['state_manager']
        
        user_id = 12345
        await db_manager.initialize_user(user_id, "testuser", "Test", "User")
        
        # Set initial state
        await state_manager.set_user_state(user_id, "onboarding", {"step": 1})
        
        # Simulate error (try to access non-existent user)
        try:
            await state_manager.get_user_state(99999)
        except Exception:
            pass  # Expected to fail
        
        # Verify original user data is still intact
        state = await state_manager.get_user_state(user_id)
        assert state == "onboarding"
        
        state_data = await state_manager.get_user_state_data(user_id)
        assert state_data['step'] == 1
