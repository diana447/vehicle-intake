import enum
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.common.mixins import TimestampMixin
from config.database import Base


class VehicleEntry(Base, TimestampMixin):
    __tablename__ = "entries_vehicle_entry"
    __table_args__ = (
        Index(
            "uq_entries_active_vin",
            "vin",
            unique=True,
            postgresql_where=text("status = 'ACTIVE'"),
        ),
    )

    class Status(enum.StrEnum):
        ACTIVE = "ACTIVE"
        CANCELLED = "CANCELLED"

    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(String(17), index=True)
    storehouse_id: Mapped[int] = mapped_column(
        ForeignKey("storehouses_storehouse.id"), index=True
    )
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations_organization.id"), index=True
    )
    entry_date: Mapped[date] = mapped_column(Date)
    status: Mapped[Status] = mapped_column(
        Enum(Status, native_enum=False, length=20),
        default=Status.ACTIVE,
        server_default=Status.ACTIVE.value,
    )

    def __repr__(self) -> str:
        return f"VehicleEntry id={self.id} vin={self.vin!r} status={self.status}"
