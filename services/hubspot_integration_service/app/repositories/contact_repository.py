from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from services.hubspot_integration_service.app.db.contact_model import ContactModel
from services.hubspot_integration_service.app.domain.contact import Contact


class ContactRepository:
    """Handles PostgreSQL persistence for HubSpot contacts."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert(self, contact: Contact) -> ContactModel:
        statement = insert(ContactModel).values(
            hubspot_id=contact.hubspot_id,
            email=contact.email,
            firstname=contact.firstname,
            lastname=contact.lastname,
            hubspot_created_at=contact.created_at,
            hubspot_updated_at=contact.updated_at,
        )

        statement = statement.on_conflict_do_update(
            index_elements=[ContactModel.hubspot_id],
            set_={
                "email": statement.excluded.email,
                "firstname": statement.excluded.firstname,
                "lastname": statement.excluded.lastname,
                "hubspot_created_at": statement.excluded.hubspot_created_at,
                "hubspot_updated_at": statement.excluded.hubspot_updated_at,
                "updated_at": func.now(),
            },
        ).returning(ContactModel)

        return self.session.execute(statement).scalar_one()

    def get_by_hubspot_id(self, hubspot_id: str) -> ContactModel | None:
        statement = select(ContactModel).where(
            ContactModel.hubspot_id == hubspot_id
        )
        return self.session.execute(statement).scalar_one_or_none()
