from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from services.hubspot_integration_service.app.db.base import Base


class ContactModel(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    hubspot_id: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    firstname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lastname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    hubspot_created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    hubspot_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )