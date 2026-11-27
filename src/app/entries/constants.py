import enum

VIN_COLUMN_NAME = "VIN"
VIN_LENGTH = 17
MAX_FILE_ROWS = 200
MAX_FILE_SIZE_BYTES = 1024 * 1024


class RejectReason:
    INVALID_VIN = "Неверный VIN — {length} символов"
    DUPLICATE_IN_FILE = "Повторяется в файле (строка {row})"
    NOT_IN_ACCOUNTING = "Машина не найдена в учёте"
    ALREADY_BOOKED = "Уже есть активная запись"
    NOT_ENOUGH_SLOTS = "Не хватило мест"


class EntryResultStatus(enum.StrEnum):
    BOOKED = "BOOKED"
    REJECTED = "REJECTED"
