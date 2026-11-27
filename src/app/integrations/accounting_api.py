import logging

import httpx

from app.common.codes import Codes
from app.common.exceptions import ServiceUnavailableError
from app.common.messages import ACCOUNTING_UNAVAILABLE_MESSAGE
from app.integrations.base import BaseServiceClient
from config.settings import get_settings

logger = logging.getLogger(__name__)


class AccountingServiceClient(BaseServiceClient):
    async def find_existing_vins(self, vins: list[str]) -> set[str]:
        """VIN, которые нашлись в учёте. При любом сбое сервиса будет 503."""
        try:
            data = await self.post("/api/v1/vehicles/lookup", json={"vins": vins})
            return set(data["found"])
        except (httpx.HTTPError, ValueError, KeyError) as error:
            logger.error(f"Accounting lookup failed: {error=}")
            raise ServiceUnavailableError(
                detail=ACCOUNTING_UNAVAILABLE_MESSAGE,
                code=Codes.ACCOUNTING_UNAVAILABLE,
            ) from error


accounting_client = AccountingServiceClient(base_url=get_settings().ACCOUNTING_URL)
