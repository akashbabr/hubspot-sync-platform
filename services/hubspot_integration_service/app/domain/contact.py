
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Contact:
    """Application-level representation of a HubSpot contact."""

    hubspot_id: str
    email: str | None
    firstname: str | None
    lastname: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None
