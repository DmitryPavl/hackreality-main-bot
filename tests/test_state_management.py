"""
Tests for state management consistency
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from modules.user_state import UserStateManager
from modules.database import DatabaseManager


class TestStateManagementConsistency:
    """Test that state management is consistent across all modules."""
    
    @pytest.mark.asyncio
    async def test_state_manager_consistency(self, temp_db, mock_user):
        """Test that state manager and database manager use the same state."""
        # Create both managers
        state_manager = UserStateManager()
        db_manager = DatabaseManager(temp_db)
        
        # Initialize database
        db_manager.init_database()
        await db_manager.initialize_user(mock_user.id, mock_user.username, mock_user.first_name)
        
        # Set state using state_manager
        test_state = "onboarding"
        test_data = {"step": 1, "data": "test"}
        
        await state_manager.set_user_state(mock_user.id, test_state, test_data)
        
        # Verify state can be retrieved from both managers
        state_from_state_manager = await state_manager.get_user_state(mock_user.id)
        state_from_db_manager = await db_manager.get_user_state(mock_user.id)
        
        assert state_from_state_manager == test_state
        assert state_from_db_manager == test_state
        
        # Verify state data consistency
        data_from_state_manager = await state_manager.get_user_state_data(mock_user.id)
        data_from_db_manager = await db_manager.get_user_state_data(mock_user.id)
        
        assert data_from_state_manager == test_data
        assert data_from_db_manager == test_data
    
    @pytest.mark.asyncio
    async def test_state_persistence_across_calls(self, temp_db, mock_user):
        """Test that state persists across multiple operations."""
        state_manager = UserStateManager()
        db_manager = DatabaseManager(temp_db)
        
        db_manager.init_database()
        await db_manager.initialize_user(mock_user.id, mock_user.username, mock_user.first_name)
        
        # Set initial state
        await state_manager.set_user_state(mock_user.id, "onboarding", {"step": 0})
        
        # Verify state persists
        state1 = await state_manager.get_user_state(mock_user.id)
        assert state1 == "onboarding"
        
        # Update state data
        await state_manager.update_user_state_data(mock_user.id, {"step": 1})
        
        # Verify updated state
        state2 = await state_manager.get_user_state(mock_user.id)
        data2 = await state_manager.get_user_state_data(mock_user.id)
        
        assert state2 == "onboarding"
        assert data2["step"] == 1
    
    @pytest.mark.asyncio
    async def test_state_manager_thread_safety(self, temp_db, mock_user):
        """Test that state manager handles concurrent operations safely."""
        state_manager = UserStateManager()
        db_manager = DatabaseManager(temp_db)
        
        db_manager.init_database()
        await db_manager.initialize_user(mock_user.id, mock_user.username, mock_user.first_name)
        
        # Simulate concurrent state updates
        async def update_state(step):
            await state_manager.set_user_state(mock_user.id, "onboarding", {"step": step})
            return await state_manager.get_user_state(mock_user.id)
        
        # Run concurrent operations
        results = await asyncio.gather(
            update_state(1),
            update_state(2),
            update_state(3),
            return_exceptions=True
        )
        
        # All operations should complete without exceptions
        for result in results:
            assert not isinstance(result, Exception)
    
    @pytest.mark.asyncio
    async def test_invalid_user_state_handling(self, temp_db):
        """Test handling of invalid user states."""
        state_manager = UserStateManager()
        db_manager = DatabaseManager(temp_db)
        
        db_manager.init_database()
        
        # Test getting state for non-existent user
        state = await state_manager.get_user_state(99999)
        assert state is None
        
        data = await state_manager.get_user_state_data(99999)
        assert data == {}
    
    @pytest.mark.asyncio
    async def test_state_transition_validation(self, temp_db, mock_user):
        """Test that state transitions are valid."""
        state_manager = UserStateManager()
        db_manager = DatabaseManager(temp_db)
        
        db_manager.init_database()
        await db_manager.initialize_user(mock_user.id, mock_user.username, mock_user.first_name)
        
        # Test valid state transitions
        valid_transitions = [
            (None, "onboarding"),
            ("onboarding", "option_selection"),
            ("option_selection", "setup"),
            ("setup", "payment"),
            ("payment", "active")
        ]
        
        for from_state, to_state in valid_transitions:
            if from_state is not None:
                await state_manager.set_user_state(mock_user.id, from_state, {})
            
            await state_manager.set_user_state(mock_user.id, to_state, {})
            current_state = await state_manager.get_user_state(mock_user.id)
            assert current_state == to_state
