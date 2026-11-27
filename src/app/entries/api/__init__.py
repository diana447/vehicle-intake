from fastapi import APIRouter

from app.entries.api.upload_storehouse_vehicle_entries import (
    upload_storehouse_vehicle_entries_router,
)

router = APIRouter()
router.include_router(upload_storehouse_vehicle_entries_router)
