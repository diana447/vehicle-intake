from fastapi import APIRouter

from app.storehouses.api.get_storehouse_availability import (
    get_storehouse_availability_router,
)
from app.storehouses.api.get_storehouse_calendar import get_storehouse_calendar_router
from app.storehouses.api.get_storehouse_list import get_storehouse_list_router

router = APIRouter()
router.include_router(get_storehouse_list_router)
router.include_router(get_storehouse_calendar_router)
router.include_router(get_storehouse_availability_router)
