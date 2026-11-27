from datetime import date

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.schemas import CurrentUser
from app.common.exceptions import NotFoundError
from app.common.messages import STOREHOUSE_NOT_FOUND_MESSAGE
from app.entries.models import VehicleEntry
from app.organizations.models.organization import Organization
from app.storehouses.models import Storehouse
from config.database import get_session

get_storehouse_availability_router = APIRouter(
    prefix="/storehouses", tags=["storehouses"]
)


class GetStorehouseAvailabilityOut(BaseModel):
    storehouse_id: int
    name: str
    date: date
    daily_limit: int
    occupied: int
    free: int


@get_storehouse_availability_router.get(
    "/{storehouse_id}/availability", response_model=GetStorehouseAvailabilityOut
)
async def get_storehouse_availability(
    storehouse_id: int,
    entry_date: date = Query(..., alias="date"),
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # 1. склад ищем с учётом прав, чужой не найдётся и даст 404
    stmt = select(Storehouse).where(Storehouse.id == storehouse_id)
    if user.org_type != Organization.Type.COMPANY:
        stmt = stmt.where(Storehouse.organization_id == user.org_id)
    storehouse = await session.scalar(stmt)
    if storehouse is None:
        raise NotFoundError(detail=STOREHOUSE_NOT_FOUND_MESSAGE)

    # 2. сколько занято на эту дату
    occupied = await session.scalar(
        select(func.count())
        .select_from(VehicleEntry)
        .where(
            VehicleEntry.storehouse_id == storehouse.id,
            VehicleEntry.entry_date == entry_date,
            VehicleEntry.status == VehicleEntry.Status.ACTIVE,
        )
    )
    occupied = occupied or 0

    # 3. свободно = лимит минус занято, но не меньше нуля
    return {
        "storehouse_id": storehouse.id,
        "name": storehouse.name,
        "date": entry_date,
        "daily_limit": storehouse.daily_limit,
        "occupied": occupied,
        "free": max(storehouse.daily_limit - occupied, 0),
    }
