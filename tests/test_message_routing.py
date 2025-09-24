"""
Tests for message routing between modules
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from main import TelegramBot


class TestMessageRouting:
    """Test message routing between different modules."""
    
    @pytest.fixture
    def mock_bot(self, mock_db_manager, mock_state_manager):
        """Create a mock TelegramBot instance."""
        with patch('main.AdminNotifications') as mock_admin:
            with patch('main.OnboardingModule') as mock_onboarding:
                with patch('main.OptionModule') as mock_option:
                    with patch('main.SettingUpModule') as mock_setting:
                        with patch('main.PayingModule') as mock_paying:
                            with patch('main.IterationModule') as mock_iteration:
                                with patch('main.DatabaseManager') as mock_db:
                                    with patch('main.StateManager') as mock_state:
                                        bot = TelegramBot("test_token")
                                        bot.db_manager = mock_db_manager
                                        bot.state_manager = mock_state_manager
                                        bot.onboarding = mock_onboarding.return_value
                                        bot.option = mock_option.return_value
                                        bot.settingup = mock_setting.return_value
                                        bot.paying = mock_paying.return_value
                                        bot.iteration = mock_iteration.return_value
                                        bot.admin_notifications = mock_admin.return_value
                                        return bot
    
    @pytest.mark.asyncio
    async def test_start_command_routes_to_onboarding(self, mock_update, mock_context, mock_bot):
        """Test that /start command routes to onboarding module."""
        # Mock the onboarding module methods
        mock_bot.onboarding.start_onboarding = AsyncMock()
        
        # Call start command
        await mock_bot.start_command(mock_update, mock_context)
        
        # Verify onboarding.start_onboarding was called
        mock_bot.onboarding.start_onboarding.assert_called_once_with(mock_update, mock_context)
    
    @pytest.mark.asyncio
    async def test_message_routing_by_state(self, mock_update, mock_context, mock_bot):
        """Test that messages are routed to correct modules based on user state."""
        user_id = mock_update.effective_user.id
        
        # Test routing for each state
        routing_tests = [
            ("onboarding", mock_bot.onboarding.handle_message),
            ("option_selection", mock_bot.option.handle_message),
            ("setup", mock_bot.settingup.handle_message),
            ("payment", mock_bot.paying.handle_message),
            ("active", mock_bot.iteration.handle_message),
        ]
        
        for state, expected_module_method in routing_tests:
            # Set user state
            await mock_bot.state_manager.set_user_state(user_id, state, {})
            
            # Mock the module method
            expected_module_method.handle_message = AsyncMock()
            
            # Call handle_message
            await mock_bot.handle_message(mock_update, mock_context)
            
            # Verify correct module was called
            expected_module_method.handle_message.assert_called_once_with(mock_update, mock_context)
            
            # Reset mock for next test
            expected_module_method.handle_message.reset_mock()
    
    @pytest.mark.asyncio
    async def test_callback_query_routing_by_state(self, mock_update_callback, mock_context, mock_bot):
        """Test that callback queries are routed to correct modules based on user state."""
        user_id = mock_update_callback.effective_user.id
        
        # Test routing for each state
        routing_tests = [
            ("onboarding", mock_bot.onboarding.handle_callback_query),
            ("option_selection", mock_bot.option.handle_callback_query),
            ("setup", mock_bot.settingup.handle_callback_query),
            ("payment", mock_bot.paying.handle_callback_query),
            ("active", mock_bot.iteration.handle_callback_query),
        ]
        
        for state, expected_module_method in routing_tests:
            # Set user state
            await mock_bot.state_manager.set_user_state(user_id, state, {})
            
            # Mock the module method
            expected_module_method.handle_callback_query = AsyncMock()
            
            # Call handle_callback_query
            await mock_bot.handle_callback_query(mock_update_callback, mock_context)
            
            # Verify correct module was called
            expected_module_method.handle_callback_query.assert_called_once_with(mock_update_callback, mock_context)
            
            # Reset mock for next test
            expected_module_method.handle_callback_query.reset_mock()
    
    @pytest.mark.asyncio
    async def test_unknown_state_routes_to_onboarding(self, mock_update, mock_context, mock_bot):
        """Test that unknown user states route to onboarding."""
        user_id = mock_update.effective_user.id
        
        # Set unknown state
        await mock_bot.state_manager.set_user_state(user_id, "unknown_state", {})
        
        # Mock onboarding module
        mock_bot.onboarding.handle_message = AsyncMock()
        
        # Call handle_message
        await mock_bot.handle_message(mock_update, mock_context)
        
        # Verify routing to onboarding
        mock_bot.onboarding.handle_message.assert_called_once_with(mock_update, mock_context)
    
    @pytest.mark.asyncio
    async def test_none_state_routes_to_onboarding(self, mock_update, mock_context, mock_bot):
        """Test that None user state routes to onboarding."""
        user_id = mock_update.effective_user.id
        
        # Don't set any state (should be None)
        # Mock onboarding module
        mock_bot.onboarding.handle_message = AsyncMock()
        
        # Call handle_message
        await mock_bot.handle_message(mock_update, mock_context)
        
        # Verify routing to onboarding
        mock_bot.onboarding.handle_message.assert_called_once_with(mock_update, mock_context)
    
    @pytest.mark.asyncio
    async def test_message_routing_with_security_checks(self, mock_update, mock_context, mock_bot):
        """Test that message routing includes security checks."""
        user_id = mock_update.effective_user.id
        
        # Set user state
        await mock_bot.state_manager.set_user_state(user_id, "onboarding", {})
        
        # Mock security methods
        mock_bot._check_rate_limit = AsyncMock(return_value=True)
        mock_bot._validate_input = AsyncMock(return_value=True)
        mock_bot._sanitize_input = AsyncMock(return_value="sanitized_text")
        
        # Mock onboarding module
        mock_bot.onboarding.handle_message = AsyncMock()
        
        # Call handle_message
        await mock_bot.handle_message(mock_update, mock_context)
        
        # Verify security checks were called
        mock_bot._check_rate_limit.assert_called_once_with(user_id)
        mock_bot._validate_input.assert_called_once()
        mock_bot._sanitize_input.assert_called_once()
        
        # Verify onboarding was called
        mock_bot.onboarding.handle_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_callback_query_routing_with_security_checks(self, mock_update_callback, mock_context, mock_bot):
        """Test that callback query routing includes security checks."""
        user_id = mock_update_callback.effective_user.id
        
        # Set user state
        await mock_bot.state_manager.set_user_state(user_id, "onboarding", {})
        
        # Mock security methods
        mock_bot._check_rate_limit = AsyncMock(return_value=True)
        
        # Mock onboarding module
        mock_bot.onboarding.handle_callback_query = AsyncMock()
        
        # Call handle_callback_query
        await mock_bot.handle_callback_query(mock_update_callback, mock_context)
        
        # Verify security checks were called
        mock_bot._check_rate_limit.assert_called_once_with(user_id)
        
        # Verify onboarding was called
        mock_bot.onboarding.handle_callback_query.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_rate_limit_blocking(self, mock_update, mock_context, mock_bot):
        """Test that rate limiting blocks excessive requests."""
        user_id = mock_update.effective_user.id
        
        # Set user state
        await mock_bot.state_manager.set_user_state(user_id, "onboarding", {})
        
        # Mock rate limit to return False (blocked)
        mock_bot._check_rate_limit = AsyncMock(return_value=False)
        
        # Mock onboarding module
        mock_bot.onboarding.handle_message = AsyncMock()
        
        # Call handle_message
        await mock_bot.handle_message(mock_update, mock_context)
        
        # Verify rate limit was checked
        mock_bot._check_rate_limit.assert_called_once_with(user_id)
        
        # Verify onboarding was NOT called due to rate limit
        mock_bot.onboarding.handle_message.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_invalid_input_handling(self, mock_update, mock_context, mock_bot):
        """Test that invalid input is handled properly."""
        user_id = mock_update.effective_user.id
        
        # Set user state
        await mock_bot.state_manager.set_user_state(user_id, "onboarding", {})
        
        # Mock security methods
        mock_bot._check_rate_limit = AsyncMock(return_value=True)
        mock_bot._validate_input = AsyncMock(return_value=False)  # Invalid input
        mock_bot._sanitize_input = AsyncMock(return_value="sanitized_text")
        
        # Mock onboarding module
        mock_bot.onboarding.handle_message = AsyncMock()
        
        # Call handle_message
        await mock_bot.handle_message(mock_update, mock_context)
        
        # Verify validation was called
        mock_bot._validate_input.assert_called_once()
        
        # Verify onboarding was NOT called due to invalid input
        mock_bot.onboarding.handle_message.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_error_handling_in_routing(self, mock_update, mock_context, mock_bot):
        """Test that errors in routing are handled gracefully."""
        user_id = mock_update.effective_user.id
        
        # Set user state
        await mock_bot.state_manager.set_user_state(user_id, "onboarding", {})
        
        # Mock security methods to pass
        mock_bot._check_rate_limit = AsyncMock(return_value=True)
        mock_bot._validate_input = AsyncMock(return_value=True)
        mock_bot._sanitize_input = AsyncMock(return_value="sanitized_text")
        
        # Mock onboarding module to raise an exception
        mock_bot.onboarding.handle_message = AsyncMock(side_effect=Exception("Test error"))
        
        # Mock error handler
        mock_bot._handle_critical_error = AsyncMock()
        
        # Call handle_message
        await mock_bot.handle_message(mock_update, mock_context)
        
        # Verify error handler was called
        mock_bot._handle_critical_error.assert_called_once()
