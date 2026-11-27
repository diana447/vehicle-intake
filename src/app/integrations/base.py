import httpx

HTTP_TIMEOUT = httpx.Timeout(10.0, connect=2.0)


class BaseServiceClient:
    def __init__(self, base_url: str) -> None:
        self._client = httpx.AsyncClient(base_url=base_url, timeout=HTTP_TIMEOUT)

    async def post(self, path: str, json: dict) -> dict:
        response = await self._client.post(path, json=json)
        response.raise_for_status()
        return response.json()
