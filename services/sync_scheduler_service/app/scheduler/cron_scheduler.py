import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from services.sync_scheduler_service.app.services.sync_service import SyncService

logger = logging.getLogger(__name__)


class CronScheduler:
    """Schedules periodic HubSpot synchronization requests."""

    def __init__(
        self,
        sync_service: SyncService,
        cron_expression: str,
        timezone: str,
    ) -> None:
        self.sync_service = sync_service
        self.cron_expression = cron_expression
        self.timezone = timezone
        self.scheduler = AsyncIOScheduler(timezone=timezone)
        self._active_job: asyncio.Task[None] | None = None
        self._stopping = False

    async def _run_sync(self) -> None:
        if self._stopping:
            return

        self._active_job = asyncio.current_task()

        try:
            result = await self.sync_service.request_sync(requested_by="cron")
            logger.info("Scheduled sync request queued: %s", result["sync_id"])
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Failed to queue scheduled sync request")
        finally:
            self._active_job = None

    def start(self) -> None:
        if self.scheduler.running:
            return

        minute, hour, day, month, day_of_week = self.cron_expression.split()

        self.scheduler.add_job(
            self._run_sync,
            trigger="cron",
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week,
            id="hubspot-contact-sync",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )

        self._stopping = False
        self.scheduler.start()

        logger.info(
            "Cron scheduler started with expression %s (%s)",
            self.cron_expression,
            self.timezone,
        )

    async def stop(self) -> None:
        self._stopping = True

        if self.scheduler.running:
            self.scheduler.pause()
            self.scheduler.shutdown(wait=False)

        active_job = self._active_job
        if active_job is not None and not active_job.done():
            await active_job

        logger.info("Cron scheduler stopped")
