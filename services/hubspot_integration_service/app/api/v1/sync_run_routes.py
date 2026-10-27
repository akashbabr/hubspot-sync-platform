
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from services.hubspot_integration_service.app.schemas.sync_run_response import (
    SyncRunResponse,
)
from services.hubspot_integration_service.app.services.sync_run_query_service import (
    SyncRunQueryService,
)


router = APIRouter(
    prefix="/api/v1/sync-runs",
    tags=["Sync Runs"],
)


@router.get(
    "/{sync_id}",
    response_model=SyncRunResponse,
    status_code=status.HTTP_200_OK,
)
def get_sync_run(sync_id: UUID) -> SyncRunResponse:
    """Retrieve synchronization status using its unique sync ID."""

    query_service = SyncRunQueryService()
    sync_run = query_service.get_by_sync_id(sync_id)

    if sync_run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Synchronization run '{sync_id}' was not found.",
        )

    return SyncRunResponse.model_validate(sync_run)
