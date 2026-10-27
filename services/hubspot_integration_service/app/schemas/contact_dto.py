
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactDTO(BaseModel):
    """Validated contact data received from HubSpot."""

    model_config = ConfigDict(extra="ignore")

    hubspot_id: str = Field(min_length=1)
    email: EmailStr | None = None
    firstname: str | None = None
    lastname: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
