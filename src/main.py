"""
Main entry point for the LLM Mental Health Research system.
"""
import asyncio
import sys
import os
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.crew import MentalHealthResearchCrew
from src.telegram_notifier import TelegramNotifier
from src.scheduler import ResearchScheduler


def setup_logging():
    """Configure logging."""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE", "logs/research_crew.log")
    
    # Remove default logger
    logger.remove()
    
    # Add console logger
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=log_level
    )
    
    # Add file logger
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level=log_level,
        rotation="10 MB",
        retention="1 week"
    )
    
    logger.info("Logging configured")


async def test_connection():
    """Test Telegram bot connection."""
    logger.info("Testing Telegram connection...")
    notifier = TelegramNotifier()
    success = await notifier.test_connection()
    
    if success:
        logger.info("✅ Telegram connection test passed")
        return True
    else:
        logger.error("❌ Telegram connection test failed")
        return False


async def run_once():
    """Execute the research crew once and send results."""
    logger.info("Running research crew once...")
    
    try:
        # Initialize crew and notifier
        crew = MentalHealthResearchCrew()
        notifier = TelegramNotifier()
        
        # Execute research
        result = await crew.execute_async()
        
        # Send results
        if result.status == "success":
            await notifier.send_report(result.report, result.execution_time_seconds)
            logger.info("✅ Research completed and sent successfully")
        else:
            await notifier.send_error(result.error or "Unknown error")
            logger.error(f"❌ Research failed: {result.error}")
            
    except Exception as e:
        logger.error(f"❌ Execution error: {e}")
        raise


async def run_scheduled():
    """Run the scheduler in continuous mode."""
    logger.info("Starting scheduled mode...")
    
    scheduler = ResearchScheduler()
    await scheduler.run_forever()


def main():
    """Main entry point with CLI options."""
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    setup_logging()
    
    # Check required environment variables
    required_vars = ["GEMINI_API_KEY", "SERPER_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # Parse command line arguments
    mode = sys.argv[1] if len(sys.argv) > 1 else "once"
    
    if mode == "test":
        # Test Telegram connection
        asyncio.run(test_connection())
        
    elif mode == "once":
        # Run once
        asyncio.run(run_once())
        
    elif mode == "schedule":
        # Run scheduled
        asyncio.run(run_scheduled())
        
    else:
        print("Usage: python -m src.main [test|once|schedule]")
        print("  test     - Test Telegram connection")
        print("  once     - Run research once and exit")
        print("  schedule - Run on schedule (continuous)")
        sys.exit(1)


if __name__ == "__main__":
    main()
