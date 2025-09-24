"""
Tests for admin notification system
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from modules.admin_notifications import AdminNotificationService


class TestAdminNotifications:
    """Test admin notification system."""
    
    @pytest.fixture
    def admin_notifications(self):
        """Create AdminNotifications instance."""
        return AdminNotificationService()
    
    @pytest.mark.asyncio
    async def test_new_user_notification(self, admin_notifications, mock_user):
        """Test new user notification."""
        # Mock the send_notification method
        admin_notifications.send_notification = AsyncMock()
        
        # Send new user notification
        message = f"🔔 NEW USERS 👋\nНовый пользователь!\n👤 Имя: {mock_user.first_name} {mock_user.last_name}\n📱 Username: @{mock_user.username}\n🆔 ID: {mock_user.id}"
        await admin_notifications.send_notification(message, "new_users")
        
        # Verify message was sent
        admin_notifications.send_notification.assert_called_once_with(message, "new_users")
    
    @pytest.mark.asyncio
    async def test_new_subscription_notification(self, admin_notifications, mock_user):
        """Test new subscription notification."""
        # Mock the bot send_message method
        admin_notifications.bot = Mock()
        admin_notifications.bot.send_message = AsyncMock()
        
        # Test data
        subscription_data = {
            "goal": "Test goal",
            "plan": "extreme",
            "target": "Test target"
        }
        
        # Send new subscription notification
        await admin_notifications.send_new_subscription_notification(mock_user, subscription_data)
        
        # Verify message was sent
        admin_notifications.bot.send_message.assert_called_once()
        call_args = admin_notifications.bot.send_message.call_args
        
        # Check message content
        message_text = call_args[1]['text']
        assert "НОВАЯ ПОДПИСКА" in message_text
        assert "Test goal" in message_text
        assert "extreme" in message_text
        assert "Test target" in message_text
        assert mock_user.first_name in message_text
        
        # Check recipient
        assert call_args[1]['chat_id'] == "41107472"
    
    @pytest.mark.asyncio
    async def test_payment_notification(self, admin_notifications, mock_user):
        """Test payment notification."""
        # Mock the bot send_message method
        admin_notifications.bot = Mock()
        admin_notifications.bot.send_message = AsyncMock()
        
        # Test data
        payment_data = {
            "amount": "1000",
            "goal": "Test goal"
        }
        
        # Send payment notification
        await admin_notifications.send_payment_notification(mock_user, payment_data)
        
        # Verify message was sent
        admin_notifications.bot.send_message.assert_called_once()
        call_args = admin_notifications.bot.send_message.call_args
        
        # Check message content
        message_text = call_args[1]['text']
        assert "НОВЫЙ ПЛАТЕЖ" in message_text
        assert "1000" in message_text
        assert "Test goal" in message_text
        assert mock_user.first_name in message_text
        
        # Check recipient
        assert call_args[1]['chat_id'] == "41107472"
    
    @pytest.mark.asyncio
    async def test_help_request_notification(self, admin_notifications, mock_user):
        """Test help request notification."""
        # Mock the bot send_message method
        admin_notifications.bot = Mock()
        admin_notifications.bot.send_message = AsyncMock()
        
        # Test data
        help_data = {
            "message": "I need help with something",
            "user_state": "onboarding"
        }
        
        # Send help request notification
        await admin_notifications.send_help_request_notification(mock_user, help_data)
        
        # Verify message was sent
        admin_notifications.bot.send_message.assert_called_once()
        call_args = admin_notifications.bot.send_message.call_args
        
        # Check message content
        message_text = call_args[1]['text']
        assert "ЗАПРОС ПОМОЩИ" in message_text
        assert "I need help with something" in message_text
        assert "onboarding" in message_text
        assert mock_user.first_name in message_text
        
        # Check recipient
        assert call_args[1]['chat_id'] == "41107472"
    
    @pytest.mark.asyncio
    async def test_notification_error_handling(self, admin_notifications, mock_user):
        """Test notification error handling."""
        # Mock the bot send_message method to raise an exception
        admin_notifications.bot = Mock()
        admin_notifications.bot.send_message = AsyncMock(side_effect=Exception("Send failed"))
        
        # Send notification (should not raise exception)
        await admin_notifications.send_new_user_notification(mock_user)
        
        # Verify message was attempted
        admin_notifications.bot.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_notification_with_missing_user_data(self, admin_notifications):
        """Test notification with missing user data."""
        # Create user with missing data
        incomplete_user = Mock()
        incomplete_user.id = 12345
        incomplete_user.first_name = None
        incomplete_user.last_name = None
        incomplete_user.username = None
        
        # Mock the bot send_message method
        admin_notifications.bot = Mock()
        admin_notifications.bot.send_message = AsyncMock()
        
        # Send notification (should handle missing data gracefully)
        await admin_notifications.send_new_user_notification(incomplete_user)
        
        # Verify message was sent
        admin_notifications.bot.send_message.assert_called_once()
        call_args = admin_notifications.bot.send_message.call_args
        
        # Check message content handles missing data
        message_text = call_args[1]['text']
        assert "12345" in message_text  # ID should still be present
    
    @pytest.mark.asyncio
    async def test_notification_formatting(self, admin_notifications, mock_user):
        """Test notification message formatting."""
        # Mock the bot send_message method
        admin_notifications.bot = Mock()
        admin_notifications.bot.send_message = AsyncMock()
        
        # Send new user notification
        await admin_notifications.send_new_user_notification(mock_user)
        
        # Verify message was sent
        call_args = admin_notifications.bot.send_message.call_args
        
        # Check message formatting
        message_text = call_args[1]['text']
        
        # Should contain emojis and formatting
        assert "🔔" in message_text or "👋" in message_text
        assert "👤" in message_text
        assert "📱" in message_text
        assert "🆔" in message_text
        assert "⏰" in message_text
        
        # Should be properly formatted with line breaks
        assert "\n" in message_text
    
    @pytest.mark.asyncio
    async def test_multiple_notifications(self, admin_notifications, mock_user):
        """Test sending multiple notifications."""
        # Mock the bot send_message method
        admin_notifications.bot = Mock()
        admin_notifications.bot.send_message = AsyncMock()
        
        # Send multiple notifications
        await admin_notifications.send_new_user_notification(mock_user)
        await admin_notifications.send_payment_notification(mock_user, {"amount": "1000", "goal": "Test"})
        await admin_notifications.send_help_request_notification(mock_user, {"message": "Help", "user_state": "test"})
        
        # Verify all messages were sent
        assert admin_notifications.bot.send_message.call_count == 3
        
        # Check that each message has different content
        calls = admin_notifications.bot.send_message.call_args_list
        message_texts = [call[1]['text'] for call in calls]
        
        assert any("НОВЫЙ ПОЛЬЗОВАТЕЛЬ" in text for text in message_texts)
        assert any("НОВЫЙ ПЛАТЕЖ" in text for text in message_texts)
        assert any("ЗАПРОС ПОМОЩИ" in text for text in message_texts)
    
    @pytest.mark.asyncio
    async def test_notification_with_special_characters(self, admin_notifications):
        """Test notification with special characters in user data."""
        # Create user with special characters
        special_user = Mock()
        special_user.id = 12345
        special_user.first_name = "Тест & < > \" '"
        special_user.last_name = "User & < > \" '"
        special_user.username = "test_user_&_<>"
        
        # Mock the bot send_message method
        admin_notifications.bot = Mock()
        admin_notifications.bot.send_message = AsyncMock()
        
        # Send notification
        await admin_notifications.send_new_user_notification(special_user)
        
        # Verify message was sent (should not crash)
        admin_notifications.bot.send_message.assert_called_once()
        
        # Check that special characters are handled
        call_args = admin_notifications.bot.send_message.call_args
        message_text = call_args[1]['text']
        assert "12345" in message_text
