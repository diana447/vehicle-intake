from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.mixins import TimestampMixin
from config.database import Base

if TYPE_CHECKING:
    from app.organizations.models.organization import Organization


class Storehouse(Base, TimestampMixin):
    __tablename__ = "storehouses_storehouse"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations_organization.id"), index=True
    )
    daily_limit: Mapped[int] = mapped_column(Integer)

    organization: Mapped["Organization"] = relationship()

    def __repr__(self) -> str:
        return f"Storehouse id={self.id} name={self.name!r}"
