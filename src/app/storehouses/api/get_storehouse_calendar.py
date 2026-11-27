import calendar
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

get_storehouse_calendar_router = APIRouter(prefix="/storehouses", tags=["storehouses"])


class GetStorehouseCalendarDayOut(BaseModel):
    date: date
    occupied: int
    free: int


class GetStorehouseCalendarOut(BaseModel):
    storehouse_id: int
    name: str
    daily_limit: int
    year: int
    month: int
    days: list[GetStorehouseCalendarDayOut]


@get_storehouse_calendar_router.get(
    "/{storehouse_id}/calendar", response_model=GetStorehouseCalendarOut
)
async def get_storehouse_calendar(
    storehouse_id: int,
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
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

    # 2. занятые места по дням, только там, где есть записи
    days_in_month = calendar.monthrange(year, month)[1]
    result = await session.execute(
        select(VehicleEntry.entry_date, func.count())
        .where(
            VehicleEntry.storehouse_id == storehouse.id,
            VehicleEntry.status == VehicleEntry.Status.ACTIVE,
            VehicleEntry.entry_date >= date(year, month, 1),
            VehicleEntry.entry_date <= date(year, month, days_in_month),
        )
        .group_by(VehicleEntry.entry_date)
    )
    counts = {entry_date: count for entry_date, count in result.all()}

    # 3. идём по всем дням месяца, где записей нет, ставим 0
    days = []
    for number in range(1, days_in_month + 1):
        day = date(year, month, number)
        occupied = counts.get(day, 0)
        days.append(
            {
                "date": day,
                "occupied": occupied,
                "free": max(storehouse.daily_limit - occupied, 0),
            }
        )
    return {
        "storehouse_id": storehouse.id,
        "name": storehouse.name,
        "daily_limit": storehouse.daily_limit,
        "year": year,
        "month": month,
        "days": days,
    }
