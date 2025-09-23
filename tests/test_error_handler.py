"""
Error Handler Tests
Test error handling functionality.
"""

import pytest
from modules.error_handler import ErrorHandler

class TestErrorHandler:
    """Test error handling functionality"""
    
    def test_validate_user_input(self):
        """Test user input validation"""
        # Valid inputs
        assert ErrorHandler.validate_user_input("Hello world") == True
        assert ErrorHandler.validate_user_input("a") == True
        assert ErrorHandler.validate_user_input("x" * 1000) == True
        
        # Invalid inputs
        assert ErrorHandler.validate_user_input("") == False
        assert ErrorHandler.validate_user_input(None) == False
        assert ErrorHandler.validate_user_input("x" * 1001) == False
        assert ErrorHandler.validate_user_input("<script>alert('xss')</script>") == False
        assert ErrorHandler.validate_user_input("javascript:alert('xss')") == False
    
    def test_sanitize_input(self):
        """Test input sanitization"""
        # Test dangerous characters removal
        dangerous_input = "<script>alert('xss')</script>"
        sanitized = ErrorHandler.sanitize_input(dangerous_input)
        assert "<" not in sanitized
        assert ">" not in sanitized
        
        # Test length limiting
        long_input = "x" * 2000
        sanitized = ErrorHandler.sanitize_input(long_input)
        assert len(sanitized) <= 1000
        
        # Test empty input
        assert ErrorHandler.sanitize_input("") == ""
        assert ErrorHandler.sanitize_input(None) == ""
    
    def test_log_error(self):
        """Test error logging"""
        # This test just ensures the method doesn't crash
        try:
            ErrorHandler.log_error(
                Exception("Test error"),
                "test_context",
                user_id=12345,
                additional_data={"test": "data"}
            )
            assert True  # If we get here, no exception was raised
        except Exception:
            pytest.fail("log_error should not raise exceptions")
    
    @pytest.mark.asyncio
    async def test_safe_execute(self):
        """Test safe execution wrapper"""
        # Test successful execution
        async def success_func():
            return "success"
        
        result = await ErrorHandler.safe_execute(success_func)
        assert result == "success"
        
        # Test failed execution
        async def fail_func():
            raise Exception("Test error")
        
        result = await ErrorHandler.safe_execute(fail_func)
        assert result is None
