
from typing import Literal
from uuid import UUID

from shared.contracts.sync_events import HubSpotSyncRequested


class SyncEventBuilder:
    """Builds validated events for HubSpot synchronization requests."""

    @staticmethod
    def build(
        requested_by: Literal["manual", "cron"],
        sync_id: UUID,
    ) -> HubSpotSyncRequested:
        return HubSpotSyncRequested(
            requested_by=requested_by,
            sync_id=sync_id,
        )
