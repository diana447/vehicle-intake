from fastapi import Request
from fastapi.responses import JSONResponse

from app.common.exceptions import ApplicationError


async def application_error_handler(
    request: Request, exc: ApplicationError
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": exc.code},
    )
