"""
Simple test to verify the testing framework is working
"""
import pytest


def test_basic_functionality():
    """Test that basic functionality works."""
    assert 1 + 1 == 2


@pytest.mark.asyncio
async def test_async_functionality():
    """Test that async functionality works."""
    import asyncio
    await asyncio.sleep(0.01)  # Small delay to test async
    assert True


class TestBasicClass:
    """Test basic class functionality."""
    
    def test_class_method(self):
        """Test class method."""
        assert "test" in "testing"


if __name__ == "__main__":
    pytest.main([__file__])
