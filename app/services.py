import logging
import time
from decimal import Decimal

from app.deribit import DeribitClient
from app.repositories import PriceRepository


class PriceService:
    def __init__(
        self,
        repository: PriceRepository,
        client: DeribitClient,
    ) -> None:
        self._repository = repository
        self._client = client

    async def collect(self, tickers: tuple[str, ...]) -> dict[str, int | list[str]]:
        saved = 0
        errors = []

        for ticker in tickers:
            try:
                price: Decimal = await self._client.get_index_price(ticker)
                self._repository.add(ticker, price, int(time.time()))
                saved += 1
            except Exception:
                logging.exception("Не удалось получить цену %s", ticker)
                errors.append(ticker)

        return {"saved": saved, "failed_tickers": errors}