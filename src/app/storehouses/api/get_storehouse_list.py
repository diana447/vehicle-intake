from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import get_current_user
from app.auth.schemas import CurrentUser
from app.common.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.organizations.models.organization import Organization
from app.storehouses.models import Storehouse
from config.database import get_session

get_storehouse_list_router = APIRouter(prefix="/storehouses", tags=["storehouses"])


class GetStorehouseListOrganizationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class GetStorehouseListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    daily_limit: int
    organization: GetStorehouseListOrganizationOut


@get_storehouse_list_router.get("", response_model=list[GetStorehouseListOut])
async def get_storehouse_list(
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
):
    # организации подгружаем сразу, иначе на каждый склад будет свой запрос
    stmt = (
        select(Storehouse)
        .options(selectinload(Storehouse.organization))
        .order_by(Storehouse.id)
        .limit(limit)
        .offset(offset)
    )
    # дистрибьютор видит только свои склады
    if user.org_type != Organization.Type.COMPANY:
        stmt = stmt.where(Storehouse.organization_id == user.org_id)
    result = await session.scalars(stmt)
    return list(result.all())
