
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/sync", tags=["Synchronization"])


class SyncResponse(BaseModel):
    sync_id: str
    status: str
    requested_by: str


@router.post(
    "/update",
    response_model=SyncResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def request_sync(request: Request) -> SyncResponse:
    """Queue a manual HubSpot contacts synchronization."""

    sync_service = request.app.state.sync_service

    try:
        result = await sync_service.request_sync(requested_by="manual")
        return SyncResponse(**result)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to queue the synchronization request",
        ) from exc
