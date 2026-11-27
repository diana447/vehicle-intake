import enum


class Codes(enum.StrEnum):
    ACCOUNTING_UNAVAILABLE = "accounting_unavailable"
    INVALID_FILE = "invalid_file"
    VIN_COLUMN_NOT_FOUND = "vin_column_not_found"
    TOO_MANY_ROWS = "too_many_rows"
    PAST_DATE = "past_date"
    FILE_TOO_LARGE = "file_too_large"
    DATA_CHANGED = "data_changed"
