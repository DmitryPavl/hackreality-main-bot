"""
Tests for onboarding flow and button interactions
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from modules.onboarding import OnboardingModule


class TestOnboardingFlow:
    """Test the complete onboarding flow and button interactions."""
    
    @pytest.mark.asyncio
    async def test_start_onboarding_sets_correct_state(self, mock_update, mock_context, mock_db_manager, mock_state_manager):
        """Test that start_onboarding sets the correct user state."""
        onboarding = OnboardingModule(mock_db_manager, mock_state_manager, None)
        
        # Mock the _welcome_message method
        onboarding._welcome_message = AsyncMock()
        
        # Call start_onboarding
        await onboarding.start_onboarding(mock_update, mock_context)
        
        # Verify state was set correctly
        user_state = await mock_state_manager.get_user_state(mock_update.effective_user.id)
        assert user_state == "onboarding"
        
        # Verify state data was set correctly
        state_data = await mock_state_manager.get_user_state_data(mock_update.effective_user.id)
        assert state_data["onboarding_step"] == 0
        assert state_data["language"] == "ru"
        assert state_data["user_name"] is not None
        assert state_data["messaging_confirmed"] is False
    
    @pytest.mark.asyncio
    async def test_welcome_message_sends_correct_content(self, mock_update, mock_context, mock_db_manager, mock_state_manager):
        """Test that welcome message sends correct content."""
        onboarding = OnboardingModule(mock_db_manager, mock_state_manager, None)
        
        # Set initial state
        await mock_state_manager.set_user_state(mock_update.effective_user.id, "onboarding", {
            "onboarding_step": 0,
            "language": "ru",
            "user_name": "Test User"
        })
        
        # Call _welcome_message
        await onboarding._welcome_message(mock_update, mock_context)
        
        # Verify message was sent
        mock_context.bot.send_message.assert_called_once()
        call_args = mock_context.bot.send_message.call_args
        
        # Check that the message contains expected content
        message_text = call_args[1]['text']
        assert "Приветствую тебя!" in message_text
        assert "HackReality" in message_text
        assert "Test User" in message_text
        
        # Check that reply_markup was provided
        assert 'reply_markup' in call_args[1]
    
    @pytest.mark.asyncio
    async def test_continue_onboarding_button_advances_step(self, mock_update_callback, mock_context, mock_db_manager, mock_state_manager):
        """Test that continue_onboarding button advances the onboarding step."""
        onboarding = OnboardingModule(mock_db_manager, mock_state_manager, None)
        
        # Set initial state
        await mock_state_manager.set_user_state(mock_update_callback.effective_user.id, "onboarding", {
            "onboarding_step": 0,
            "language": "ru",
            "user_name": "Test User"
        })
        
        # Mock the next step method
        onboarding._explain_purpose = AsyncMock()
        
        # Call handle_callback_query with continue_onboarding
        await onboarding.handle_callback_query(mock_update_callback, mock_context)
        
        # Verify step was advanced
        state_data = await mock_state_manager.get_user_state_data(mock_update_callback.effective_user.id)
        assert state_data["onboarding_step"] == 1
        
        # Verify next step was called
        onboarding._explain_purpose.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_disclaimer_acceptance_advances_flow(self, mock_update_callback, mock_context, mock_db_manager, mock_state_manager):
        """Test that accepting disclaimer advances the flow."""
        onboarding = OnboardingModule(mock_db_manager, mock_state_manager, None)
        
        # Set state to disclaimer step
        await mock_state_manager.set_user_state(mock_update_callback.effective_user.id, "onboarding", {
            "onboarding_step": 2,
            "language": "ru",
            "user_name": "Test User"
        })
        
        # Change callback data to accept_disclaimer
        mock_update_callback.callback_query.data = "accept_disclaimer"
        
        # Mock the next step method
        onboarding._collect_user_age = AsyncMock()
        
        # Call handle_callback_query
        await onboarding.handle_callback_query(mock_update_callback, mock_context)
        
        # Verify next step was called
        onboarding._collect_user_age.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_age_collection_handles_valid_input(self, mock_update, mock_context, mock_db_manager, mock_state_manager):
        """Test that age collection handles valid age input."""
        onboarding = OnboardingModule(mock_db_manager, mock_state_manager, None)
        
        # Set state to age collection step
        await mock_state_manager.set_user_state(mock_update.effective_user.id, "onboarding", {
            "onboarding_step": 3,
            "language": "ru",
            "user_name": "Test User"
        })
        
        # Mock the next step method
        onboarding._collect_user_city = AsyncMock()
        
        # Set valid age input
        mock_update.message.text = "25"
        
        # Call handle_message
        await onboarding.handle_message(mock_update, mock_context)
        
        # Verify age was stored
        state_data = await mock_state_manager.get_user_state_data(mock_update.effective_user.id)
        assert state_data["user_age"] == 25
        
        # Verify next step was called
        onboarding._collect_user_city.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_age_collection_handles_invalid_input(self, mock_update, mock_context, mock_db_manager, mock_state_manager):
        """Test that age collection handles invalid age input."""
        onboarding = OnboardingModule(mock_db_manager, mock_state_manager, None)
        
        # Set state to age collection step
        await mock_state_manager.set_user_state(mock_update.effective_user.id, "onboarding", {
            "onboarding_step": 3,
            "language": "ru",
            "user_name": "Test User"
        })
        
        # Set invalid age input
        mock_update.message.text = "not_a_number"
        
        # Call handle_message
        await onboarding.handle_message(mock_update, mock_context)
        
        # Verify error message was sent
        mock_context.bot.send_message.assert_called()
        call_args = mock_context.bot.send_message.call_args
        message_text = call_args[1]['text']
        assert "пожалуйста, введите" in message_text.lower()
    
    @pytest.mark.asyncio
    async def test_city_collection_stores_city(self, mock_update, mock_context, mock_db_manager, mock_state_manager):
        """Test that city collection stores the city name."""
        onboarding = OnboardingModule(mock_db_manager, mock_state_manager, None)
        
        # Set state to city collection step
        await mock_state_manager.set_user_state(mock_update.effective_user.id, "onboarding", {
            "onboarding_step": 4,
            "language": "ru",
            "user_name": "Test User",
            "user_age": 25
        })
        
        # Set city input
        mock_update.message.text = "Moscow"
        
        # Mock timezone detection
        with patch('modules.onboarding.get_timezone_by_city', return_value="Europe/Moscow"):
            # Mock the next step method
            onboarding._confirm_timezone = AsyncMock()
            
            # Call handle_message
            await onboarding.handle_message(mock_update, mock_context)
        
        # Verify city was stored
        state_data = await mock_state_manager.get_user_state_data(mock_update.effective_user.id)
        assert state_data["city"] == "Moscow"
        assert state_data["timezone"] == "Europe/Moscow"
    
    @pytest.mark.asyncio
    async def test_onboarding_completion_sets_final_state(self, mock_update, mock_context, mock_db_manager, mock_state_manager):
        """Test that onboarding completion sets the final state correctly."""
        onboarding = OnboardingModule(mock_db_manager, mock_state_manager, None)
        
        # Set state to final step
        await mock_state_manager.set_user_state(mock_update.effective_user.id, "onboarding", {
            "onboarding_step": 6,  # Final step
            "language": "ru",
            "user_name": "Test User",
            "user_age": 25,
            "city": "Moscow",
            "timezone": "Europe/Moscow",
            "messaging_confirmed": True
        })
        
        # Mock admin notification
        with patch.object(onboarding, 'admin_notifications', new_callable=AsyncMock):
            # Call the final step
            await onboarding._confirm_messaging_schedule(mock_update, mock_context)
        
        # Verify final state is set
        user_state = await mock_state_manager.get_user_state(mock_update.effective_user.id)
        assert user_state == "option_selection"
    
    @pytest.mark.asyncio
    async def test_button_interaction_consistency(self, mock_update_callback, mock_context, mock_db_manager, mock_state_manager):
        """Test that button interactions maintain state consistency."""
        onboarding = OnboardingModule(mock_db_manager, mock_state_manager, None)
        
        # Set initial state
        await mock_state_manager.set_user_state(mock_update_callback.effective_user.id, "onboarding", {
            "onboarding_step": 0,
            "language": "ru",
            "user_name": "Test User"
        })
        
        # Mock all step methods
        onboarding._explain_purpose = AsyncMock()
        onboarding._show_disclaimer = AsyncMock()
        onboarding._collect_user_age = AsyncMock()
        
        # Test multiple button clicks
        button_actions = [
            ("continue_onboarding", 1, onboarding._explain_purpose),
            ("accept_disclaimer", 2, onboarding._collect_user_age),
        ]
        
        for button_data, expected_step, expected_method in button_actions:
            # Set callback data
            mock_update_callback.callback_query.data = button_data
            
            # Call handle_callback_query
            await onboarding.handle_callback_query(mock_update_callback, mock_context)
            
            # Verify step was advanced
            state_data = await mock_state_manager.get_user_state_data(mock_update_callback.effective_user.id)
            assert state_data["onboarding_step"] == expected_step
            
            # Verify correct method was called
            expected_method.assert_called()
            
            # Reset mock for next iteration
            expected_method.reset_mock()
