"""
Scheduler Handler — Built-in timed trigger. No external API needed.
"""
from flozai.utils.logger import get_logger

logger = get_logger(__name__)


class SchedulerHandler:
    """Handles scheduler triggers (cron, interval, one-time).
    This is a built-in FlozAI feature — no credentials required."""

    def execute(self, action: str, credentials: dict, params: dict, context: dict) -> dict:
        schedule = params.get("schedule", params.get("cron", ""))
        if action in ("scheduled_time", "recurring", "trigger"):
            return {
                "status": "triggered",
                "message": f"Scheduler fired. Schedule: {schedule or 'manual'}",
                "schedule": schedule,
            }
        raise ValueError(f"Unknown scheduler action: {action}")
