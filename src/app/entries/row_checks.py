from typing import TypedDict

from app.entries.constants import RejectReason, VIN_LENGTH
from app.entries.vin_file import FileRow


class RejectedRow(TypedDict):
    row: int
    vin: str
    reason: str


def split_by_file_checks(rows: list[FileRow]) -> tuple[list[FileRow], list[RejectedRow]]:
    """Убирает VIN неверной длины и повторы, порядок строк сохраняется."""
    passed: list[FileRow] = []
    rejected: list[RejectedRow] = []
    first_row_by_vin: dict[str, int] = {}

    for row in rows:
        if len(row.vin) != VIN_LENGTH:
            rejected.append(
                {
                    "row": row.row,
                    "vin": row.vin,
                    "reason": RejectReason.INVALID_VIN.format(length=len(row.vin)),
                }
            )
            continue
        if row.vin in first_row_by_vin:
            rejected.append(
                {
                    "row": row.row,
                    "vin": row.vin,
                    "reason": RejectReason.DUPLICATE_IN_FILE.format(
                        row=first_row_by_vin[row.vin]
                    ),
                }
            )
            continue
        first_row_by_vin[row.vin] = row.row
        passed.append(row)

    return passed, rejected
