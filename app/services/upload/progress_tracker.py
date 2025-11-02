from typing import Dict
import time
from threading import Lock


class UploadProgressTracker:
    """
    In-memory progress tracker for file uploads.
    Simple and efficient for single-server deployments.
    """

    def __init__(self):
        self._progress: Dict[str, dict] = {}
        self._lock = Lock()

    def set_progress(
        self, upload_id: str, current: int, total: int, filename: str = ""
    ):
        """Set upload progress"""
        with self._lock:
            self._progress[upload_id] = {
                "current": current,
                "total": total,
                "percentage": (current / total * 100) if total > 0 else 0,
                "filename": filename,
                "updated_at": time.time(),
            }

    def get_progress(self, upload_id: str) -> dict:
        """Get upload progress"""
        with self._lock:
            return self._progress.get(upload_id, {})

    def remove_progress(self, upload_id: str):
        """Remove progress when upload is complete"""
        with self._lock:
            self._progress.pop(upload_id, None)

    def cleanup_old_progress(self, max_age_seconds: int = 3600):
        """Remove progress entries older than max_age_seconds"""
        current_time = time.time()
        with self._lock:
            to_remove = [
                uid
                for uid, data in self._progress.items()
                if current_time - data.get("updated_at", 0) > max_age_seconds
            ]
            for uid in to_remove:
                self._progress.pop(uid, None)
        return len(to_remove)


# Global instance
progress_tracker = UploadProgressTracker()
