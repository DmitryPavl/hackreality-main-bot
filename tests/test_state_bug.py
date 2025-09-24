"""
Test that specifically catches the state management bug we just fixed
"""
import pytest
import tempfile
import os
from modules.user_state import UserStateManager
from modules.database import DatabaseManager


class TestStateManagementBug:
    """Test that catches the state management consistency bug."""
    
    @pytest.mark.asyncio
    async def test_state_consistency_bug_reproduction(self):
        """Test that reproduces the bug where state was set in one manager but not visible in another."""
        # Create temporary database
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_file.close()
        
        try:
            # Create both managers (this was the bug - using different managers)
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
            retrieved_data = await state_manager.get_user_state_data(12345)
            
            # With the fix, these should work
            assert retrieved_state == test_state, f"Expected {test_state}, got {retrieved_state}"
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
            test_state = "onboarding"
            test_data = {"step": 1, "data": "test"}
            
            # Set state using state_manager
            await state_manager.set_user_state(12345, test_state, test_data)
            
            # Retrieve using same state_manager
            retrieved_state = await state_manager.get_user_state(12345)
            retrieved_data = await state_manager.get_user_state_data(12345)
            
            # This should always work
            assert retrieved_state == test_state
            assert retrieved_data == test_data
            
        finally:
            # Clean up
            os.unlink(temp_file.name)
    
    @pytest.mark.asyncio
    async def test_onboarding_state_flow(self):
        """Test the complete onboarding state flow."""
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
            
            # Simulate onboarding flow
            initial_data = {
                "onboarding_step": 0,
                "language": "ru",
                "user_name": "Test User",
                "user_age": None,
                "city": None,
                "timezone": None,
                "messaging_confirmed": False
            }
            
            # Set initial state
            await state_manager.set_user_state(12345, "onboarding", initial_data)
            
            # Verify initial state
            state = await state_manager.get_user_state(12345)
            data = await state_manager.get_user_state_data(12345)
            
            assert state == "onboarding"
            assert data["onboarding_step"] == 0
            assert data["language"] == "ru"
            
            # Simulate step advancement
            await state_manager.update_user_state_data(12345, {"onboarding_step": 1})
            
            # Verify step was advanced
            updated_data = await state_manager.get_user_state_data(12345)
            assert updated_data["onboarding_step"] == 1
            assert updated_data["language"] == "ru"  # Should be preserved
            
            # Simulate completing onboarding
            await state_manager.set_user_state(12345, "option_selection", {})
            
            # Verify final state
            final_state = await state_manager.get_user_state(12345)
            assert final_state == "option_selection"
            
        finally:
            # Clean up
            os.unlink(temp_file.name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
