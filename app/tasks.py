import asyncio

from celery import Celery

from app.config import get_settings
from app.database import SessionLocal
from app.deribit import DeribitClient
from app.repositories import PriceRepository
from app.services import PriceService


settings = get_settings()

celery_app = Celery(
    "price_tracker",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "collect-index-prices-every-minute": {
            "task": "app.tasks.collect_prices",
            "schedule": settings.collection_interval_seconds,
        }
    },
)


@celery_app.task(name="app.tasks.collect_prices")
def collect_prices() -> dict[str, int | list[str]]:
    db = SessionLocal()

    try:
        repository = PriceRepository(db)
        client = DeribitClient(
            settings.deribit_base_url,
            settings.request_timeout,
        )
        service = PriceService(repository, client)

        return asyncio.run(service.collect(("btc_usd", "eth_usd")))
    finally:
        db.close()