
from uuid import uuid4

from services.sync_scheduler_service.app.builders.sync_event_builder import (
    SyncEventBuilder,
)
from services.sync_scheduler_service.app.publishers.kafka_publisher import (
    KafkaPublisher,
)


class SyncService:
    """Initiates HubSpot synchronization through Kafka."""

    def __init__(self, publisher: KafkaPublisher) -> None:
        self.publisher = publisher

    async def request_sync(self, requested_by: str) -> dict[str, str]:
        if requested_by not in {"manual", "cron"}:
            raise ValueError("requested_by must be 'manual' or 'cron'")

        sync_id = uuid4()

        event = SyncEventBuilder.build(
            requested_by=requested_by,
            sync_id=sync_id,
        )

        await self.publisher.publish(event)

        return {
            "sync_id": str(sync_id),
            "status": "accepted",
            "requested_by": requested_by,
        }
