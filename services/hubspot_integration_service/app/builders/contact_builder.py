
from datetime import datetime, timezone

from services.hubspot_integration_service.app.domain.contact import Contact
from services.hubspot_integration_service.app.schemas.contact_dto import ContactDTO


class ContactBuilder:
    """Converts validated HubSpot contact DTOs into domain objects."""

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None

        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))

            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)

            return parsed
        except ValueError:
            return None

    @classmethod
    def build(cls, dto: ContactDTO) -> Contact:
        return Contact(
            hubspot_id=dto.hubspot_id,
            email=str(dto.email) if dto.email is not None else None,
            firstname=dto.firstname,
            lastname=dto.lastname,
            created_at=cls._parse_datetime(dto.created_at),
            updated_at=cls._parse_datetime(dto.updated_at),
        )
