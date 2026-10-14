from decimal import Decimal

import aiohttp


class DeribitClient:
    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = aiohttp.ClientTimeout(total=timeout)

    async def get_index_price(self, ticker: str) -> Decimal:
        url = f"{self._base_url}/public/get_index_price"

        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            async with session.get(
                url,
                params={"index_name": ticker},
            ) as response:
                response.raise_for_status()
                payload = await response.json()

        try:
            price = payload["result"]["index_price"]
            return Decimal(str(price))
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"Некорректный ответ Deribit для {ticker}"
            ) from exc