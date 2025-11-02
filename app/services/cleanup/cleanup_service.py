import os
import shutil
import time
from pathlib import Path
from app.core.config import config
from app.services.upload.progress_tracker import progress_tracker
import logging

logger = logging.getLogger(__name__)


class CleanupService:
    """
    Background cleanup service for temporary files and abandoned uploads.
    """

    @staticmethod
    def cleanup_abandoned_chunks(max_age_hours: int = 24):
        """
        Remove abandoned chunk upload directories older than max_age_hours.
        """
        data_dir = Path(config.DIR_LOCATION) / "data"
        if not data_dir.exists():
            return 0

        cleaned_count = 0
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600

        # Find all user directories
        for user_dir in data_dir.iterdir():
            if not user_dir.is_dir():
                continue

            # Find all *_parts directories (chunk temp directories)
            for temp_dir in user_dir.rglob("*_parts"):
                if not temp_dir.is_dir():
                    continue

                # Check if directory is old enough
                dir_age = current_time - temp_dir.stat().st_mtime

                if dir_age > max_age_seconds:
                    try:
                        shutil.rmtree(temp_dir)
                        cleaned_count += 1
                        logger.info(f"Cleaned up abandoned chunks: {temp_dir}")
                    except Exception as e:
                        logger.error(f"Failed to clean up {temp_dir}: {e}")

        return cleaned_count

    @staticmethod
    def cleanup_old_progress_entries():
        """
        Remove old progress tracking entries (1 hour old).
        """
        return progress_tracker.cleanup_old_progress(max_age_seconds=3600)

    @staticmethod
    def cleanup_all():
        """
        Run all cleanup tasks.
        """
        chunks_cleaned = CleanupService.cleanup_abandoned_chunks(max_age_hours=24)
        progress_cleaned = CleanupService.cleanup_old_progress_entries()

        logger.info(
            f"Cleanup complete: {chunks_cleaned} chunk dirs, {progress_cleaned} progress entries"
        )

        return {"chunks_cleaned": chunks_cleaned, "progress_cleaned": progress_cleaned}


cleanup_service = CleanupService()
