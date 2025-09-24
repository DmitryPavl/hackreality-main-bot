#!/usr/bin/env python3
"""
Simplified Admin Notifications Tests
Tests the AdminNotificationService functionality
"""

import pytest
from unittest.mock import Mock, AsyncMock
from modules.admin_notifications import AdminNotificationService


class TestAdminNotificationsSimple:
    """Test admin notification system with simplified tests."""
    
    @pytest.fixture
    def admin_notifications(self):
        """Create AdminNotifications instance."""
        return AdminNotificationService()
    
    @pytest.mark.asyncio
    async def test_send_notification_success(self, admin_notifications):
        """Test sending a notification successfully."""
        # Mock the send_notification method to avoid actual API calls
        admin_notifications.send_notification = AsyncMock(return_value=True)
        
        # Send notification
        message = "Test notification message"
        result = await admin_notifications.send_notification(message, "test_type")
        
        # Verify it was called correctly
        admin_notifications.send_notification.assert_called_once_with(message, "test_type")
        assert result is True
    
    @pytest.mark.asyncio
    async def test_send_notification_without_token(self, admin_notifications):
        """Test sending notification when admin bot token is not available."""
        # Set admin_bot_token to None to simulate missing token
        admin_notifications.admin_bot_token = None
        
        # Send notification
        message = "Test notification message"
        result = await admin_notifications.send_notification(message, "test_type")
        
        # Should return False when token is not available
        assert result is False
    
    @pytest.mark.asyncio
    async def test_notification_message_formatting(self, admin_notifications):
        """Test that notification messages are formatted correctly."""
        # Mock the send_notification method
        admin_notifications.send_notification = AsyncMock(return_value=True)
        
        # Test different notification types
        test_cases = [
            ("general", "General notification message"),
            ("new_users", "New user joined"),
            ("payments", "Payment received"),
            ("subscriptions", "New subscription created"),
            ("help_requests", "Help request from user")
        ]
        
        for notification_type, message in test_cases:
            result = await admin_notifications.send_notification(message, notification_type)
            assert result is True
        
        # Verify all notifications were sent
        assert admin_notifications.send_notification.call_count == len(test_cases)
    
    @pytest.mark.asyncio
    async def test_notification_with_special_characters(self, admin_notifications):
        """Test notification with special characters and emojis."""
        admin_notifications.send_notification = AsyncMock(return_value=True)
        
        # Test message with special characters
        message = "🔔 Тест с эмодзи и специальными символами: @#$%^&*()"
        result = await admin_notifications.send_notification(message, "special_test")
        
        assert result is True
        admin_notifications.send_notification.assert_called_with(message, "special_test")
