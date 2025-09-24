"""
Test that demonstrates the state management bug and shows how our fix resolves it
"""
import pytest
import tempfile
import os
from modules.user_state import UserStateManager, UserState
from modules.database import DatabaseManager


class TestBugDemonstration:
    """Test that demonstrates the state management bug we fixed."""
    
    @pytest.mark.asyncio
    async def test_bug_demonstration(self):
        """Test that demonstrates the bug: state set in one manager not visible in another."""
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
            
            # Try to retrieve using state_manager (this fails - demonstrates the bug)
            retrieved_state = await state_manager.get_user_state(12345)
            
            # This demonstrates the bug: state was set but not visible
            assert retrieved_state is None, "This demonstrates the bug: state set in db_manager not visible in state_manager"
            
            # But the state IS in the database
            db_state = await db_manager.get_user_state(12345)
            assert db_state == test_state, "State should be in database"
            
            # And the data IS in the database
            db_data = await db_manager.get_user_state_data(12345)
            assert db_data == test_data, "Data should be in database"
            
            print("✅ Bug demonstration successful: State set in db_manager not visible in state_manager")
            
        finally:
            # Clean up
            os.unlink(temp_file.name)
    
    @pytest.mark.asyncio
    async def test_fix_demonstration(self):
        """Test that shows how our fix resolves the issue."""
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
            test_data = {"step": 1, "data": "test"}
            
            # Set state using state_manager (fixed way)
            await state_manager.set_user_state(12345, test_state, test_data)
            
            # Retrieve using same state_manager (this works)
            retrieved_state = await state_manager.get_user_state(12345)
            
            # This should work with the fix
            assert retrieved_state == test_state.value, f"Expected {test_state.value}, got {retrieved_state}"
            
            print("✅ Fix demonstration successful: Consistent use of state_manager works")
            
        finally:
            # Clean up
            os.unlink(temp_file.name)
    
    @pytest.mark.asyncio
    async def test_onboarding_flow_bug_demonstration(self):
        """Test that demonstrates the bug in the onboarding flow."""
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
            
            # Simulate the buggy onboarding flow
            # Step 1: start_onboarding sets state using db_manager (old buggy way)
            await db_manager.set_user_state(12345, "onboarding", {
                "onboarding_step": 0,
                "language": "ru",
                "user_name": "Test User"
            })
            
            # Step 2: User clicks button, callback handler uses state_manager (bug!)
            retrieved_state = await state_manager.get_user_state(12345)
            
            # This demonstrates the bug: state is None when it should be "onboarding"
            assert retrieved_state is None, "This demonstrates the bug: state appears as None in callback handler"
            
            # But the state IS in the database
            db_state = await db_manager.get_user_state(12345)
            assert db_state == "onboarding", "State should be in database"
            
            print("✅ Onboarding flow bug demonstration successful: State appears as None in callback handler")
            
        finally:
            # Clean up
            os.unlink(temp_file.name)
    
    @pytest.mark.asyncio
    async def test_fixed_onboarding_flow(self):
        """Test that shows how the fixed onboarding flow works."""
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
            
            # Simulate the fixed onboarding flow
            # Step 1: start_onboarding sets state using state_manager (fixed way)
            await state_manager.set_user_state(12345, UserState.ONBOARDING, {
                "onboarding_step": 0,
                "language": "ru",
                "user_name": "Test User"
            })
            
            # Step 2: User clicks button, callback handler uses state_manager (fixed!)
            retrieved_state = await state_manager.get_user_state(12345)
            
            # This should work with the fix
            assert retrieved_state == "onboarding", f"Expected 'onboarding', got {retrieved_state}"
            
            print("✅ Fixed onboarding flow demonstration successful: State is consistent")
            
        finally:
            # Clean up
            os.unlink(temp_file.name)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])  # -s to show print statements
