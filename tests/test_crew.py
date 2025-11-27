"""
Basic tests for the research crew.
"""
import pytest
from unittest.mock import MagicMock, patch
from src.models import ResearchResult, ResearchSource


def test_research_source_model():
    """Test ResearchSource model validation."""
    source = ResearchSource(
        title="Test Paper",
        url="http://example.com",
        key_findings=["Finding 1", "Finding 2"]
    )
    
    assert source.title == "Test Paper"
    assert source.url == "http://example.com"
    assert len(source.key_findings) == 2


def test_research_result_model():
    """Test ResearchResult model validation."""
    result = ResearchResult(
        summary="Test Summary"
    )
    
    assert result.summary == "Test Summary"
    assert isinstance(result.sources, list)


@pytest.mark.asyncio
async def test_telegram_notifier_mock():
    """Test TelegramNotifier with mocks."""
    with patch('src.telegram_notifier.telegram.Bot') as mock_bot:
        from src.telegram_notifier import TelegramNotifier
        
        # Setup mock
        mock_bot_instance = MagicMock()
        mock_bot.return_value = mock_bot_instance
        
        # Initialize notifier with dummy credentials
        notifier = TelegramNotifier(bot_token="dummy", chat_id="123")
        
        # Test send_message
        await notifier.send_message("Test message")
        
        # Verify call
        mock_bot_instance.send_message.assert_called()
