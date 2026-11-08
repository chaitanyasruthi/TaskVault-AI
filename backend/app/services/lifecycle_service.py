from datetime import datetime, timezone


class SandboxLifecycle:

    def __init__(self, sandbox_name: str):
        self.sandbox_name = sandbox_name

        self.status = "created"
        self.cleanup_status = "not_started"

        self.started_at = datetime.now(timezone.utc)
        self.completed_at = None
        self.error = None

    def mark_running(self):
        self.status = "running"

    def mark_completed(self):
        self.status = "completed"
        self.completed_at = datetime.now(timezone.utc)

    def mark_failed(self, error: str):
        self.status = "failed"
        self.error = error
        self.completed_at = datetime.now(timezone.utc)

    def mark_cleanup(self, status: str):
        self.cleanup_status = status

    def get_report(self):

        duration = None

        if self.completed_at:
            duration = (
                self.completed_at - self.started_at
            ).total_seconds()

        return {
            "sandbox_name": self.sandbox_name,
            "status": self.status,
            "cleanup_status": self.cleanup_status,
            "started_at": self.started_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat()
                if self.completed_at else None
            ),
            "duration_seconds": duration,
            "error": self.error
        }
