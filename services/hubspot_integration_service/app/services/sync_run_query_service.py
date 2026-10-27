
from uuid import UUID

from services.hubspot_integration_service.app.db.session import SessionLocal
from services.hubspot_integration_service.app.db.sync_run_model import (
    SyncRunModel,
)
from services.hubspot_integration_service.app.repositories.sync_run_repository import (
    SyncRunRepository,
)


class SyncRunQueryService:
    """Retrieves synchronization run details."""

    def get_by_sync_id(
        self,
        sync_id: UUID,
    ) -> SyncRunModel | None:
        with SessionLocal() as session:
            repository = SyncRunRepository(session)
            sync_run = repository.get_by_sync_id(sync_id)

            if sync_run is None:
                return None

            # Detach the ORM object before closing the session.
            session.expunge(sync_run)

            return sync_run
