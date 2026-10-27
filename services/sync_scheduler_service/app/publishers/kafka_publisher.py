import json

from aiokafka import AIOKafkaProducer

from services.sync_scheduler_service.app.core.config import settings
from shared.contracts.sync_events import HubSpotSyncRequested


class KafkaPublisher:
    """Publishes HubSpot sync events to Kafka."""

    def __init__(self) -> None:
        self.producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        if self.producer is not None:
            return

        producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        )

        try:
            await producer.start()
        except BaseException:
            await producer.stop()
            raise

        self.producer = producer

    async def publish(self, event: HubSpotSyncRequested) -> None:
        if self.producer is None:
            raise RuntimeError("Kafka publisher has not been started")

        await self.producer.send_and_wait(
            settings.kafka_sync_topic,
            event.model_dump(mode="json"),
        )

    async def stop(self) -> None:
        producer = self.producer
        if producer is not None:
            self.producer = None
            await producer.stop()
