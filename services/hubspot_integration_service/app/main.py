import asyncio
import logging
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI

from services.hubspot_integration_service.app.api.v1.sync_run_routes import (
    router as sync_run_router,
)
from services.hubspot_integration_service.app.consumers.sync_consumer import (
    SyncConsumer,
)
from services.hubspot_integration_service.app.core.config import settings


logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer = SyncConsumer()
    consumer_task = asyncio.create_task(
        consumer.start(),
        name="hubspot-kafka-consumer",
    )

    app.state.consumer = consumer
    app.state.consumer_task = consumer_task

    try:
        yield

    finally:
        if not consumer_task.done():
            consumer_task.cancel()

        with suppress(asyncio.CancelledError):
            await consumer_task

        if consumer_task.done() and not consumer_task.cancelled():
            exception = consumer_task.exception()
            if exception is not None:
                logger.error(
                    "Kafka consumer task exited with an error",
                    exc_info=(
                        type(exception),
                        exception,
                        exception.__traceback__,
                    ),
                )

        logger.info("HubSpot Integration Service shutting down")


app = FastAPI(
    title="HubSpot Integration Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(sync_run_router)



@app.get("/health")
async def health_check() -> dict[str, str]:
    consumer_task = getattr(app.state, "consumer_task", None)

    consumer_running = (
        consumer_task is not None
        and not consumer_task.done()
    )

    return {
        "service": "hubspot_integration_service",
        "environment": settings.app_env,
        "status": "healthy" if consumer_running else "unhealthy",
    }

