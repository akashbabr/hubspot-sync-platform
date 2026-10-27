
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.hubspot_integration_service.app.db.sync_run_model import (
    SyncRunModel,
)


class SyncRunRepository:
    """Handles PostgreSQL persistence for synchronization runs."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        sync_id: UUID,
        requested_by: str,
    ) -> SyncRunModel:
        """Create a tracking record before synchronization begins."""

        sync_run = SyncRunModel(
            sync_id=sync_id,
            requested_by=requested_by,
            status="running",
            started_at=datetime.now(timezone.utc),
        )

        self.session.add(sync_run)
        self.session.flush()

        return sync_run

    def get_by_sync_id(self, sync_id: UUID) -> SyncRunModel | None:
        """Find a synchronization run using its event sync ID."""

        statement = select(SyncRunModel).where(
            SyncRunModel.sync_id == sync_id
        )

        return self.session.execute(statement).scalar_one_or_none()

    def mark_completed(
        self,
        sync_run: SyncRunModel,
        fetched_count: int,
        processed_count: int,
    ) -> None:
        """Record a successful synchronization."""

        sync_run.status = "completed"
        sync_run.fetched_count = fetched_count
        sync_run.processed_count = processed_count
        sync_run.completed_at = datetime.now(timezone.utc)

    def mark_failed(
        self,
        sync_run: SyncRunModel,
        error_message: str,
    ) -> None:
        """Record a synchronization failure."""

        sync_run.status = "failed"
        sync_run.error_message = error_message[:4000]
        sync_run.completed_at = datetime.now(timezone.utc)
