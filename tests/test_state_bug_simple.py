"""
Simple test that catches the state management bug we just fixed
"""
import pytest
import tempfile
import os
from modules.user_state import UserStateManager, UserState
from modules.database import DatabaseManager


class TestStateManagementBugSimple:
    """Simple test that catches the state management consistency bug."""
    
    @pytest.mark.asyncio
    async def test_state_consistency_bug_demonstration(self):
        """Test that demonstrates the bug we just fixed."""
        # Create temporary database
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_file.close()
        
        try:
            # Create both managers
            state_manager = UserStateManager()
            db_manager = DatabaseManager(temp_file.name)
            
            # Initialize database
            db_manager.init_database()
            await db_manager.initialize_user(12345, "testuser", "Test User")
            
            # This was the bug: setting state in db_manager but retrieving from state_manager
            test_state = "onboarding"
            test_data = {"step": 1, "data": "test"}
            
            # Set state using db_manager (old buggy way)
            await db_manager.set_user_state(12345, test_state, test_data)
            
            # Try to retrieve using state_manager (this would fail in the old code)
            retrieved_state = await state_manager.get_user_state(12345)
            
            # With the fix, this should work
            assert retrieved_state == test_state, f"Expected {test_state}, got {retrieved_state}"
            
            # Verify data was stored in database
            retrieved_data = await db_manager.get_user_state_data(12345)
            assert retrieved_data == test_data, f"Expected {test_data}, got {retrieved_data}"
            
        finally:
            # Clean up
            os.unlink(temp_file.name)
    
    @pytest.mark.asyncio
    async def test_state_consistency_fixed_approach(self):
        """Test the fixed approach using consistent state manager."""
        # Create temporary database
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_file.close()
        
        try:
            # Create both managers
            state_manager = UserStateManager()
            db_manager = DatabaseManager(temp_file.name)
            
            # Initialize database
            db_manager.init_database()
            await db_manager.initialize_user(12345, "testuser", "Test User")
            
            # Fixed approach: use state_manager consistently
            test_state = UserState.ONBOARDING
            
            # Set state using state_manager
            await state_manager.set_user_state(12345, test_state, {"step": 1})
            
            # Retrieve using same state_manager
            retrieved_state = await state_manager.get_user_state(12345)
            
            # This should always work
            assert retrieved_state == test_state.value, f"Expected {test_state.value}, got {retrieved_state}"
            
        finally:
            # Clean up
            os.unlink(temp_file.name)
    
    @pytest.mark.asyncio
    async def test_onboarding_state_transitions(self):
        """Test onboarding state transitions."""
        # Create temporary database
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_file.close()
        
        try:
            # Create managers
            state_manager = UserStateManager()
            db_manager = DatabaseManager(temp_file.name)
            
            # Initialize database
            db_manager.init_database()
            await db_manager.initialize_user(12345, "testuser", "Test User")
            
            # Test state transitions
            transitions = [
                (UserState.ONBOARDING, "onboarding"),
                (UserState.OPTION_SELECTION, "option_selection"),
                (UserState.SETUP, "setup"),
                (UserState.PAYMENT, "payment"),
                (UserState.ACTIVE, "active")
            ]
            
            for state_enum, state_string in transitions:
                # Set state
                await state_manager.set_user_state(12345, state_enum, {"step": 1})
                
                # Verify state
                retrieved_state = await state_manager.get_user_state(12345)
                assert retrieved_state == state_string, f"Expected {state_string}, got {retrieved_state}"
            
        finally:
            # Clean up
            os.unlink(temp_file.name)
    
    @pytest.mark.asyncio
    async def test_state_validation(self):
        """Test state validation and transitions."""
        state_manager = UserStateManager()
        
        # Test valid transitions
        assert state_manager.can_transition_to(UserState.ONBOARDING, UserState.OPTION_SELECTION)
        assert state_manager.can_transition_to(UserState.OPTION_SELECTION, UserState.SETUP)
        assert state_manager.can_transition_to(UserState.SETUP, UserState.PAYMENT)
        assert state_manager.can_transition_to(UserState.PAYMENT, UserState.ACTIVE)
        
        # Test invalid transitions
        assert not state_manager.can_transition_to(UserState.ACTIVE, UserState.ONBOARDING)
        assert not state_manager.can_transition_to(UserState.PAYMENT, UserState.ONBOARDING)
        
        # Test allowed transitions
        allowed = state_manager.get_allowed_transitions(UserState.ONBOARDING)
        assert UserState.OPTION_SELECTION in allowed
        assert UserState.ACTIVE not in allowed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
