from apscheduler.schedulers.background import BackgroundScheduler
from app.services.cleanup.cleanup_service import cleanup_service
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def start_cleanup_scheduler():
    """
    Start the background cleanup scheduler.
    Runs cleanup every 6 hours.
    """
    # Run cleanup every 6 hours
    scheduler.add_job(
        cleanup_service.cleanup_all,
        trigger="interval",
        hours=6,
        id="cleanup_job",
        name="Cleanup abandoned uploads and old progress",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Cleanup scheduler started - runs every 6 hours")


def stop_cleanup_scheduler():
    """Stop the cleanup scheduler."""
    scheduler.shutdown()
    logger.info("Cleanup scheduler stopped")
