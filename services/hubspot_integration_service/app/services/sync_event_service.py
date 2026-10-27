import logging
from typing import Any

from shared.contracts.sync_events import HubSpotSyncRequested
from services.hubspot_integration_service.app.db.session import SessionLocal
from services.hubspot_integration_service.app.repositories.sync_run_repository import (
    SyncRunRepository,
)
from services.hubspot_integration_service.app.services.contact_sync_service import (
    ContactSyncService,
)

logger = logging.getLogger(__name__)


class SyncEventService:
    """Validates sync events and tracks their execution."""

    def __init__(self) -> None:
        self.contact_sync_service = ContactSyncService()

    async def process_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        event = HubSpotSyncRequested.model_validate(payload)

        with SessionLocal() as session:
            repository = SyncRunRepository(session)
            existing_run = repository.get_by_sync_id(event.sync_id)

            if existing_run is not None:
                if existing_run.status == "completed":
                    logger.info(
                        "Ignoring duplicate completed sync event: sync_id=%s",
                        event.sync_id,
                    )
                    return {
                        "sync_id": str(existing_run.sync_id),
                        "status": existing_run.status,
                        "fetched": existing_run.fetched_count,
                        "processed": existing_run.processed_count,
                    }

                if existing_run.status in {"running", "failed"}:
                    logger.warning(
                        "Ignoring duplicate sync event: sync_id=%s status=%s",
                        event.sync_id,
                        existing_run.status,
                    )
                    return {
                        "sync_id": str(existing_run.sync_id),
                        "status": existing_run.status,
                        "fetched": existing_run.fetched_count,
                        "processed": existing_run.processed_count,
                    }

            sync_run = repository.create(
                sync_id=event.sync_id,
                requested_by=event.requested_by,
            )

            try:
                session.commit()

                if event.object_type != "contacts":
                    raise ValueError(
                        f"Unsupported sync object type: {event.object_type}"
                    )

                result = await self.contact_sync_service.sync_contacts()

                repository.mark_completed(
                    sync_run=sync_run,
                    fetched_count=result["fetched"],
                    processed_count=result["processed"],
                )
                session.commit()

                logger.info(
                    "Sync completed: sync_id=%s requested_by=%s "
                    "fetched=%s processed=%s",
                    event.sync_id,
                    event.requested_by,
                    result["fetched"],
                    result["processed"],
                )

                return {
                    "sync_id": str(event.sync_id),
                    "status": "completed",
                    **result,
                }

            except Exception as exc:
                session.rollback()

                sync_run = repository.get_by_sync_id(event.sync_id)

                if sync_run is not None:
                    repository.mark_failed(
                        sync_run=sync_run,
                        error_message=str(exc),
                    )
                    session.commit()

                logger.exception("Sync failed: sync_id=%s", event.sync_id)
                raise
