from contextlib import asynccontextmanager
from datetime import date, datetime, time, timedelta, timezone
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.repositories import PriceRepository
from app.schemas import PriceResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Deribit Клиент",
    description="История индексных цен BTC и ETH с Deribit.",
    version="1.0.0",
    lifespan=lifespan,
)

Ticker = Annotated[
    Literal["btc_usd", "eth_usd"],
    Query(description="Тикер валюты"),
]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/prices", response_model=list[PriceResponse], tags=["prices"])
def get_prices(
    ticker: Ticker,
    db: Session = Depends(get_db),
) -> list[PriceResponse]:
    return PriceRepository(db).list_for_ticker(ticker)


@app.get("/api/v1/prices/latest", response_model=PriceResponse, tags=["prices"])
def get_latest_price(
    ticker: Ticker,
    db: Session = Depends(get_db),
) -> PriceResponse:
    record = PriceRepository(db).latest_for_ticker(ticker)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Данные для {ticker} не найдены",
        )

    return record


@app.get("/api/v1/prices/by-date", response_model=list[PriceResponse], tags=["prices"])
def get_prices_by_date(
    ticker: Ticker,
    date_value: Annotated[
        date,
        Query(alias="date", description="Дата в формате YYYY-MM-DD, UTC"),
    ],
    db: Session = Depends(get_db),
) -> list[PriceResponse]:
    start = datetime.combine(date_value, time.min, tzinfo=timezone.utc)
    end = start + timedelta(days=1)

    return PriceRepository(db).list_for_period(
        ticker,
        int(start.timestamp()),
        int(end.timestamp()),
    )