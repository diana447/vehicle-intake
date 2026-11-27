from pathlib import Path

from openpyxl import Workbook

OUTPUT_PATH = Path(__file__).resolve().parents[2] / "sample_vehicles.xlsx"

SAMPLE_VINS = [
    "LVVDB21B4RD012415",  # строка 2: нормальная машина
    "LVVDB21B4RD012416",  # строка 3: нормальная машина
    "Z94C241BBRR10887",  # строка 4: 16 символов, неверный VIN
    "XWEPC81BDR0004421",  # строка 5: нет в учёте
    "LVVDB21B4RD012401",  # строка 6: уже есть активная запись (из сида)
    "LVVDB21B4RD012415",  # строка 7: повтор строки 2
    "Z94C241BBRR108880",  # строки 8-11: нормальные, часть не влезет в лимит
    "Z94C241BBRR108881",
    "Z94C241BBRR108882",
    "Z94C241BBRR108883",
]


def main() -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["VIN"])
    for vin in SAMPLE_VINS:
        sheet.append([vin])
    workbook.save(OUTPUT_PATH)
    print(f"Создан файл: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
