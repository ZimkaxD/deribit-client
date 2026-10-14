from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PriceRecord

from decimal import Decimal

class PriceRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, ticker: str, price: Decimal, timestamp: int) -> PriceRecord:
        record = PriceRecord(
            ticker=ticker,
            price=price,
            timestamp=timestamp,
        )

        try:
            self._db.add(record)
            self._db.commit()
            self._db.refresh(record)
        except Exception:
            self._db.rollback()
            raise

        return record

    def list_for_ticker(self, ticker: str) -> list[PriceRecord]:
        query = (
            select(PriceRecord)
            .where(PriceRecord.ticker == ticker)
            .order_by(PriceRecord.timestamp, PriceRecord.id)
        )

        return list(self._db.scalars(query).all())

    def latest_for_ticker(self, ticker: str) -> PriceRecord | None:
        query = (
            select(PriceRecord)
            .where(PriceRecord.ticker == ticker)
            .order_by(PriceRecord.timestamp.desc(), PriceRecord.id.desc())
            .limit(1)
        )

        return self._db.scalars(query).first()

    def list_for_period(
        self,
        ticker: str,
        start_timestamp: int,
        end_timestamp: int,
    ) -> list[PriceRecord]:
        query = (
            select(PriceRecord)
            .where(
                PriceRecord.ticker == ticker,
                PriceRecord.timestamp >= start_timestamp,
                PriceRecord.timestamp < end_timestamp,
            )
            .order_by(PriceRecord.timestamp, PriceRecord.id)
        )

        return list(self._db.scalars(query).all())