NOT_AUTHENTICATED_MESSAGE = "Не авторизован"
INVALID_AUTH_MESSAGE = "Невалидный или просроченный токен"
STOREHOUSE_NOT_FOUND_MESSAGE = "Склад не найден"
ACCOUNTING_UNAVAILABLE_MESSAGE = (
    "Ни одна машина не записана. Попробуйте через пару минут: файл и выбор остались."
)
INVALID_FILE_MESSAGE = "Не удалось прочитать файл. Загрузите Excel в формате .xlsx."
EMPTY_FILE_MESSAGE = "В файле нет машин. Заполните столбец «VIN»."
VIN_COLUMN_NOT_FOUND_MESSAGE = "Не нашли столбец «VIN». Скачайте шаблон и заполните его."
TOO_MANY_ROWS_MESSAGE = (
    "В файле {count} строк, можно до {limit}. Разбейте файл на несколько."
)
PAST_DATE_MESSAGE = "Нельзя записать на прошедшую дату."
FILE_TOO_LARGE_MESSAGE = "Файл больше {limit} МБ. Разбейте его на несколько."
DATA_CHANGED_MESSAGE = (
    "Данные изменились, пока обрабатывался файл. Загрузите файл ещё раз."
)
