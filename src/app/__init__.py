from fastapi import FastAPI

from app.common.exceptions import ApplicationError
from app.common.handlers import application_error_handler
from app.entries.api import router as entries_router
from app.storehouses.api import router as storehouses_router
from config.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    # swagger показываем только на dev
    docs_enabled = settings.ENVIRONMENT == "dev"
    app = FastAPI(
        title="Vehicle Intake",
        openapi_url="/openapi.json" if docs_enabled else None,
        docs_url="/docs" if docs_enabled else None,
        redoc_url=None,
    )
    app.add_exception_handler(ApplicationError, application_error_handler)
    app.include_router(storehouses_router)
    app.include_router(entries_router)
    return app
