from datetime import date

from fastapi import APIRouter, Depends, File, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.schemas import CurrentUser
from app.common.codes import Codes
from app.common.exceptions import ApplicationError, ConflictError, NotFoundError
from app.common.messages import (
    DATA_CHANGED_MESSAGE,
    PAST_DATE_MESSAGE,
    STOREHOUSE_NOT_FOUND_MESSAGE,
)
from app.entries.constants import EntryResultStatus, MAX_FILE_SIZE_BYTES, RejectReason
from app.entries.models import VehicleEntry
from app.entries.row_checks import split_by_file_checks
from app.entries.vin_file import FileRow, read_vins_from_xlsx
from app.integrations.accounting_api import accounting_client
from app.organizations.models.organization import Organization
from app.storehouses.models import Storehouse
from config.database import get_session

upload_storehouse_vehicle_entries_router = APIRouter(
    prefix="/storehouses", tags=["storehouses"]
)


class UploadStorehouseVehicleEntriesEntryOut(BaseModel):
    row: int
    vin: str
    status: EntryResultStatus
    reason: str | None


class UploadStorehouseVehicleEntriesOut(BaseModel):
    storehouse_id: int
    date: date
    total_rows: int
    booked_count: int
    rejected_count: int
    entries: list[UploadStorehouseVehicleEntriesEntryOut]


@upload_storehouse_vehicle_entries_router.post(
    "/{storehouse_id}/entries/upload",
    response_model=UploadStorehouseVehicleEntriesOut,
)
async def upload_storehouse_vehicle_entries(
    storehouse_id: int,
    entry_date: date = Query(..., alias="date"),
    file: UploadFile = File(...),
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

    # 2. на прошедшие даты записывать нельзя
    if entry_date < date.today():
        raise ApplicationError(detail=PAST_DATE_MESSAGE, code=Codes.PAST_DATE)

    # 3. читаем файл, больше лимита не берём
    content = await file.read(MAX_FILE_SIZE_BYTES + 1)
    rows = read_vins_from_xlsx(content)

    # 4. длина VIN и повторы в файле, отказы копим в results
    passed, results = split_by_file_checks(rows)

    # 5. спрашиваем учёт про все VIN сразу, если он лежит, будет 503
    candidates: list[FileRow] = []
    if passed:
        found_in_accounting = await accounting_client.find_existing_vins(
            [row.vin for row in passed]
        )
        for row in passed:
            if row.vin in found_in_accounting:
                candidates.append(row)
            else:
                results.append(
                    {
                        "row": row.row,
                        "vin": row.vin,
                        "reason": RejectReason.NOT_IN_ACCOUNTING,
                    }
                )

    # 6. VIN, у которых уже есть активная запись, на любом складе
    remaining: list[FileRow] = []
    if candidates:
        active_result = await session.scalars(
            select(VehicleEntry.vin).where(
                VehicleEntry.vin.in_([row.vin for row in candidates]),
                VehicleEntry.status == VehicleEntry.Status.ACTIVE,
            )
        )
        active_vins = set(active_result.all())
        for row in candidates:
            if row.vin in active_vins:
                results.append(
                    {
                        "row": row.row,
                        "vin": row.vin,
                        "reason": RejectReason.ALREADY_BOOKED,
                    }
                )
            else:
                remaining.append(row)

    # 7. блокируем склад+дату, параллельные загрузки ждут друг друга
    #    снимется сама после commit
    await session.execute(
        text("SELECT pg_advisory_xact_lock(hashtext(:key))"),
        {"key": f"{storehouse.id}:{entry_date}"},
    )

    # 8. считаем занятые места уже под блокировкой
    occupied = await session.scalar(
        select(func.count())
        .select_from(VehicleEntry)
        .where(
            VehicleEntry.storehouse_id == storehouse.id,
            VehicleEntry.entry_date == entry_date,
            VehicleEntry.status == VehicleEntry.Status.ACTIVE,
        )
    )
    free = storehouse.daily_limit - (occupied or 0)

    # 9. места раздаём по порядку строк, кому не хватило, тот получает отказ
    new_entries = []
    for row in remaining:
        if free > 0:
            free -= 1
            new_entries.append(
                VehicleEntry(
                    vin=row.vin,
                    storehouse_id=storehouse.id,
                    organization_id=user.org_id,
                    entry_date=entry_date,
                )
            )
            results.append({"row": row.row, "vin": row.vin, "reason": None})
        else:
            results.append(
                {
                    "row": row.row,
                    "vin": row.vin,
                    "reason": RejectReason.NOT_ENOUGH_SLOTS,
                }
            )

    # 10. один commit на всю загрузку, если тот же VIN успели записать
    #     на другой склад, индекс не пропустит, отвечаем 409
    session.add_all(new_entries)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise ConflictError(
            detail=DATA_CHANGED_MESSAGE, code=Codes.DATA_CHANGED
        ) from error

    # 11. статус по причине (есть причина, значит отказ), строки в порядке файла
    for item in results:
        item["status"] = (
            EntryResultStatus.REJECTED
            if item["reason"] is not None
            else EntryResultStatus.BOOKED
        )
    results.sort(key=lambda item: item["row"])

    booked_count = sum(
        1 for item in results if item["status"] == EntryResultStatus.BOOKED
    )
    return {
        "storehouse_id": storehouse.id,
        "date": entry_date,
        "total_rows": len(results),
        "booked_count": booked_count,
        "rejected_count": len(results) - booked_count,
        "entries": results,
    }
