from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SyncRunResponse(BaseModel):
    """API representation of a synchronization run."""

    model_config = ConfigDict(from_attributes=True)

    sync_id: UUID
    requested_by: str
    status: str
    fetched_count: int
    processed_count: int
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime