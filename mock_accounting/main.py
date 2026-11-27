import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Mock Accounting Service")

KNOWN_VINS = (
    {f"LVVDB21B4RD0124{number:02d}" for number in range(1, 31)}
    | {f"Z94C241BBRR1088{number}" for number in range(80, 90)}
    | {"XWEPC81BDR0004422"}
)


class LookupIn(BaseModel):
    vins: list[str] = Field(max_length=200)


class LookupOut(BaseModel):
    found: list[str]


@app.post("/api/v1/vehicles/lookup", response_model=LookupOut)
async def lookup_vehicles(body: LookupIn):
    # MOCK_ACCOUNTING_DOWN=1 включает ответ 503, чтобы проверить ошибку учёта
    if os.environ.get("MOCK_ACCOUNTING_DOWN") == "1":
        raise HTTPException(status_code=503, detail="Service unavailable")
    return LookupOut(found=[vin for vin in body.vins if vin in KNOWN_VINS])
