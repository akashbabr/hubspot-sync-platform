
from services.hubspot_integration_service.app.builders.contact_builder import (
    ContactBuilder,
)
from services.hubspot_integration_service.app.clients.hubspot_client import (
    HubSpotClient,
)
from services.hubspot_integration_service.app.db.session import SessionLocal
from services.hubspot_integration_service.app.repositories.contact_repository import (
    ContactRepository,
)
from services.hubspot_integration_service.app.schemas.contact_dto import ContactDTO


class ContactSyncService:
    """Coordinates fetching, validating, building, and storing contacts."""

    def __init__(self) -> None:
        self.hubspot_client = HubSpotClient()

    async def sync_contacts(self) -> dict[str, int]:
        raw_contacts = await self.hubspot_client.get_contacts()

        processed = 0

        with SessionLocal() as session:
            repository = ContactRepository(session)

            try:
                for raw_contact in raw_contacts:
                    dto = ContactDTO.model_validate(raw_contact)
                    contact = ContactBuilder.build(dto)
                    repository.upsert(contact)
                    processed += 1

                session.commit()

            except Exception:
                session.rollback()
                raise

        return {
            "fetched": len(raw_contacts),
            "processed": processed,
        }
