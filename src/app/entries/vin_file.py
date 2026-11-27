from io import BytesIO
from typing import NamedTuple
from zipfile import BadZipFile

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from app.common.codes import Codes
from app.common.exceptions import ApplicationError
from app.common.messages import (
    EMPTY_FILE_MESSAGE,
    FILE_TOO_LARGE_MESSAGE,
    INVALID_FILE_MESSAGE,
    TOO_MANY_ROWS_MESSAGE,
    VIN_COLUMN_NOT_FOUND_MESSAGE,
)
from app.entries.constants import MAX_FILE_ROWS, MAX_FILE_SIZE_BYTES, VIN_COLUMN_NAME


class FileRow(NamedTuple):
    row: int
    vin: str


def _find_vin_column(header: tuple) -> int | None:
    for index, cell in enumerate(header):
        if cell is not None and str(cell).strip().upper() == VIN_COLUMN_NAME:
            return index
    return None


def read_vins_from_xlsx(content: bytes) -> list[FileRow]:
    """Возвращает VIN из файла и номер строки (как в Excel, заголовок это строка 1)."""
    if len(content) > MAX_FILE_SIZE_BYTES:
        limit_mb = MAX_FILE_SIZE_BYTES // (1024 * 1024)
        raise ApplicationError(
            detail=FILE_TOO_LARGE_MESSAGE.format(limit=limit_mb),
            code=Codes.FILE_TOO_LARGE,
        )
    try:
        workbook = load_workbook(BytesIO(content), read_only=True, data_only=True)
    except (BadZipFile, InvalidFileException, KeyError, OSError) as error:
        raise ApplicationError(
            detail=INVALID_FILE_MESSAGE, code=Codes.INVALID_FILE
        ) from error

    try:
        sheet = workbook.active
        if sheet is None:
            raise ApplicationError(detail=EMPTY_FILE_MESSAGE, code=Codes.INVALID_FILE)
        rows = sheet.iter_rows(values_only=True)
        column = _find_vin_column(next(rows, ()))
        if column is None:
            raise ApplicationError(
                detail=VIN_COLUMN_NOT_FOUND_MESSAGE, code=Codes.VIN_COLUMN_NOT_FOUND
            )

        result = []
        for row_number, cells in enumerate(rows, start=2):
            value = cells[column] if column < len(cells) else None
            if value is None or not str(value).strip():
                continue
            result.append(FileRow(row_number, str(value).strip().upper()))
    finally:
        workbook.close()

    if not result:
        raise ApplicationError(detail=EMPTY_FILE_MESSAGE, code=Codes.INVALID_FILE)
    if len(result) > MAX_FILE_ROWS:
        raise ApplicationError(
            detail=TOO_MANY_ROWS_MESSAGE.format(count=len(result), limit=MAX_FILE_ROWS),
            code=Codes.TOO_MANY_ROWS,
        )
    return result
