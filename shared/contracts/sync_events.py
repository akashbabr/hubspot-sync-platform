
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

class HubSpotSyncRequested(BaseModel):
    """Kafka event requesting a HubSpot contacts synchronization."""

    model_config = ConfigDict(extra="forbid")

    event_id: UUID = Field(default_factory=uuid4)
    event_type: Literal["hubspot.sync.requested"] = "hubspot.sync.requested"
    schema_version: Literal[1] = 1

    sync_id: UUID = Field(default_factory=uuid4)
    requested_by: Literal["manual", "cron"]
    object_type: Literal["contacts"] = "contacts"

    requested_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
