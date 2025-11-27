"""
Telegram notification system with async support and message chunking.
"""
import asyncio
import os
from typing import Optional, List
from loguru import logger
import telegram
from telegram.error import TelegramError
from telegram.constants import ParseMode


class TelegramNotifier:
    """
    Handles sending notifications to Telegram with support for long messages.
    """
    
    MAX_MESSAGE_LENGTH = 4096  # Telegram's limit
    
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Initialize the Telegram notifier.
        
        Args:
            bot_token: Telegram bot token (defaults to env var)
            chat_id: Telegram chat ID (defaults to env var)
        """
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment")
        if not self.chat_id:
            raise ValueError("TELEGRAM_CHAT_ID not found in environment")
        
        self.bot = telegram.Bot(token=self.bot_token)
        logger.info(f"TelegramNotifier initialized for chat_id: {self.chat_id}")
    
    async def send_message(
        self,
        message: str,
        parse_mode: str = ParseMode.MARKDOWN,
        disable_preview: bool = True
    ) -> bool:
        """
        Send a message to Telegram, splitting if necessary.
        
        Args:
            message: Message to send
            parse_mode: Telegram parse mode (MARKDOWN, HTML, or None)
            disable_preview: Whether to disable link previews
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Split message if it's too long
            chunks = self._split_message(message)
            
            for i, chunk in enumerate(chunks):
                try:
                    await self.bot.send_message(
                        chat_id=self.chat_id,
                        text=chunk,
                        parse_mode=parse_mode,
                        disable_web_page_preview=disable_preview
                    )
                    
                    # Add small delay between chunks to avoid rate limiting
                    if i < len(chunks) - 1:
                        await asyncio.sleep(1)
                        
                except TelegramError as e:
                    # If markdown parsing fails, try without formatting
                    if "can't parse" in str(e).lower():
                        logger.warning(f"Markdown parsing failed, sending as plain text")
                        await self.bot.send_message(
                            chat_id=self.chat_id,
                            text=chunk,
                            parse_mode=None,
                            disable_web_page_preview=disable_preview
                        )
                    else:
                        raise
            
            logger.info(f"Successfully sent {len(chunks)} message chunk(s)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def _split_message(self, message: str) -> List[str]:
        """
        Split a long message into chunks that fit Telegram's size limit.
        
        Args:
            message: Message to split
            
        Returns:
            List of message chunks
        """
        if len(message) <= self.MAX_MESSAGE_LENGTH:
            return [message]
        
        chunks = []
        current_chunk = ""
        
        # Split by lines to avoid breaking in the middle of content
        lines = message.split('\n')
        
        for line in lines:
            # If a single line is too long, split it
            if len(line) > self.MAX_MESSAGE_LENGTH:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                
                # Split long line into smaller pieces
                for i in range(0, len(line), self.MAX_MESSAGE_LENGTH - 100):
                    chunks.append(line[i:i + self.MAX_MESSAGE_LENGTH - 100])
            
            # If adding this line would exceed the limit, start a new chunk
            elif len(current_chunk) + len(line) + 1 > self.MAX_MESSAGE_LENGTH:
                chunks.append(current_chunk)
                current_chunk = line
            
            else:
                current_chunk += ('\n' if current_chunk else '') + line
        
        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    async def send_report(self, report: str, execution_time: float) -> bool:
        """
        Send a research report with a header.
        
        Args:
            report: The report content
            execution_time: Time taken to generate the report
            
        Returns:
            True if successful, False otherwise
        """
        header = (
            "🧠 *LLM Mental Health Research Report*\n"
            f"⏱ Execution time: {execution_time:.2f}s\n"
            f"📅 Generated: {asyncio.get_event_loop().time()}\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
        )
        
        full_message = header + report
        return await self.send_message(full_message)
    
    async def send_error(self, error_message: str) -> bool:
        """
        Send an error notification.
        
        Args:
            error_message: Error message to send
            
        Returns:
            True if successful, False otherwise
        """
        message = (
            "⚠️ *Research Crew Error*\n\n"
            f"An error occurred during execution:\n\n"
            f"``````"
        )
        return await self.send_message(message)
    
    async def test_connection(self) -> bool:
        """
        Test the Telegram bot connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            me = await self.bot.get_me()
            logger.info(f"Connected to Telegram bot: @{me.username}")
            
            await self.send_message("✅ *Connection Test Successful*\n\nBot is ready!")
            return True
            
        except Exception as e:
            logger.error(f"Telegram connection test failed: {e}")
            return False


def send_notification_sync(message: str) -> bool:
    """
    Synchronous wrapper for sending Telegram notifications.
    
    Args:
        message: Message to send
        
    Returns:
        True if successful, False otherwise
    """
    notifier = TelegramNotifier()
    
    try:
        # Create new event loop if none exists
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(notifier.send_message(message))
        
    except Exception as e:
        logger.error(f"Sync notification failed: {e}")
        return False
