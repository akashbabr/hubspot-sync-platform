import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from services.sync_scheduler_service.app.api.v1.sync_routes import router
from services.sync_scheduler_service.app.core.config import settings
from services.sync_scheduler_service.app.publishers.kafka_publisher import (
    KafkaPublisher,
)
from services.sync_scheduler_service.app.scheduler.cron_scheduler import (
    CronScheduler,
)
from services.sync_scheduler_service.app.services.sync_service import SyncService


logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    publisher = KafkaPublisher()
    scheduler: CronScheduler | None = None

    try:
        await publisher.start()

        sync_service = SyncService(publisher)

        scheduler = CronScheduler(
            sync_service=sync_service,
            cron_expression=settings.sync_cron_expression,
            timezone=settings.sync_timezone,
        )

        app.state.sync_service = sync_service
        app.state.publisher = publisher
        app.state.scheduler = scheduler

        scheduler.start()

        logger.info("Sync Scheduler Service started")
        yield

    finally:
        if scheduler is not None:
            await scheduler.stop()

        await publisher.stop()
        logger.info("Sync Scheduler Service stopped")


app = FastAPI(
    title="HubSpot Sync Scheduler Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health")
async def health_check(request: Request) -> dict[str, str]:
    publisher = getattr(request.app.state, "publisher", None)
    scheduler = getattr(request.app.state, "scheduler", None)

    publisher_started = (
        publisher is not None
        and publisher.producer is not None
    )

    scheduler_running = (
        scheduler is not None
        and scheduler.scheduler.running
    )

    healthy = publisher_started and scheduler_running

    return {
        "service": "sync_scheduler_service",
        "environment": settings.app_env,
        "status": "healthy" if healthy else "unhealthy",
    }
