import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer
from aiokafka.structs import OffsetAndMetadata, TopicPartition

from services.hubspot_integration_service.app.core.config import settings
from services.hubspot_integration_service.app.services.sync_event_service import (
    SyncEventService,
)

logger = logging.getLogger(__name__)


class SyncConsumer:
    """Consumes HubSpot synchronization events from Kafka."""

    def __init__(self) -> None:
        self.consumer: AIOKafkaConsumer | None = None
        self.sync_event_service = SyncEventService()

    async def start(self) -> None:
        consumer = AIOKafkaConsumer(
            settings.kafka_sync_topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=settings.kafka_consumer_group,
            enable_auto_commit=False,
            auto_offset_reset="earliest",
        )

        self.consumer = consumer

        try:
            await consumer.start()
            logger.info("Kafka consumer started")

            async for message in consumer:
                await self._process_message(message)
        finally:
            try:
                await consumer.stop()
            finally:
                self.consumer = None
                logger.info("Kafka consumer stopped")

    async def _process_message(self, message) -> None:
        if self.consumer is None:
            raise RuntimeError("Kafka consumer is not running")

        try:
            payload = json.loads(message.value.decode("utf-8"))

            result = await self.sync_event_service.process_event(payload)

            logger.info(
                "Sync event processed: sync_id=%s status=%s",
                result["sync_id"],
                result["status"],
            )

            await self.consumer.commit(
                {
                    TopicPartition(message.topic, message.partition): (
                        OffsetAndMetadata(message.offset + 1, "")
                    )
                }
            )

        except asyncio.CancelledError:
            raise

        except Exception:
            logger.exception(
                "Failed to process Kafka message: topic=%s partition=%s offset=%s",
                message.topic,
                message.partition,
                message.offset,
            )

            # Do not continue past a message that failed processing or commit.
            # The offset remains uncommitted.
            raise
