"""
Scheduler for periodic research crew execution.
"""
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
import os

from .crew import MentalHealthResearchCrew
from .telegram_notifier import TelegramNotifier


class ResearchScheduler:
    """
    Handles scheduled execution of the research crew.
    """
    
    def __init__(self):
        """Initialize the scheduler."""
        self.scheduler = AsyncIOScheduler()
        self.crew = MentalHealthResearchCrew()
        self.notifier = TelegramNotifier()
        
        # Get schedule configuration
        self.interval_minutes = int(os.getenv("SCHEDULE_INTERVAL_MINUTES", 1440))
        self.enabled = os.getenv("SCHEDULE_ENABLED", "true").lower() == "true"
        
        logger.info(f"Scheduler initialized (interval: {self.interval_minutes} minutes, enabled: {self.enabled})")
    
    async def execute_research(self):
        """Execute the research crew and send notifications."""
        logger.info("Scheduled research execution started")
        
        try:
            # Execute the crew
            result = await self.crew.execute_async()
            
            # Send notification based on result
            if result.status == "success":
                await self.notifier.send_report(
                    result.report,
                    result.execution_time_seconds
                )
                logger.info("Research report sent successfully")
            else:
                await self.notifier.send_error(result.error or "Unknown error")
                logger.error(f"Research execution failed: {result.error}")
                
        except Exception as e:
            error_msg = f"Scheduler execution error: {str(e)}"
            logger.error(error_msg)
            await self.notifier.send_error(error_msg)
    
    def start(self):
        """Start the scheduler."""
        if not self.enabled:
            logger.warning("Scheduler is disabled in configuration")
            return
        
        # Add the job with interval trigger
        self.scheduler.add_job(
            self.execute_research,
            trigger=IntervalTrigger(minutes=self.interval_minutes),
            id='research_job',
            name='Mental Health LLM Research',
            replace_existing=True,
            next_run_time=datetime.now()  # Run immediately on start
        )
        
        self.scheduler.start()
        logger.info(f"Scheduler started (runs every {self.interval_minutes} minutes)")
    
    def start_with_cron(self, cron_expression: str = "0 9 * * *"):
        """
        Start the scheduler with a cron expression.
        
        Args:
            cron_expression: Cron expression (default: daily at 9 AM)
                Examples:
                - "0 9 * * *" : Daily at 9 AM
                - "0 */6 * * *" : Every 6 hours
                - "0 9 * * MON" : Every Monday at 9 AM
        """
        if not self.enabled:
            logger.warning("Scheduler is disabled in configuration")
            return
        
        # Parse cron expression
        minute, hour, day, month, day_of_week = cron_expression.split()
        
        self.scheduler.add_job(
            self.execute_research,
            trigger=CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week
            ),
            id='research_job',
            name='Mental Health LLM Research',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info(f"Scheduler started with cron: {cron_expression}")
    
    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    async def run_forever(self):
        """Run the scheduler indefinitely."""
        self.start()
        
        try:
            # Keep the scheduler running
            while True:
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
            self.stop()
