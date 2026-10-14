from decimal import Decimal

from fastapi.testclient import TestClient

from app import main
from app.database import get_db
from app.main import app


class FakeRecord:
    def __init__(self, record_id, ticker, price, timestamp):
        self.id = record_id
        self.ticker = ticker
        self.price = Decimal(price)
        self.timestamp = timestamp


class FakeRepository:
    records = [
        FakeRecord(1, "btc_usd", "65000.25", 1791936000),
        FakeRecord(2, "btc_usd", "65100.50", 1791936060),
        FakeRecord(3, "eth_usd", "2500.00", 1791936120),
    ]

    def __init__(self, db):
        pass

    def list_for_ticker(self, ticker):
        return [
            record for record in self.records
            if record.ticker == ticker
        ]

    def latest_for_ticker(self, ticker):
        records = self.list_for_ticker(ticker)
        return records[-1] if records else None

    def list_for_period(self, ticker, start_timestamp, end_timestamp):
        return [
            record
            for record in self.list_for_ticker(ticker)
            if start_timestamp <= record.timestamp < end_timestamp
        ]


class EmptyRepository:
    def __init__(self, db):
        pass

    def latest_for_ticker(self, ticker):
        return None


def override_db():
    yield object()


def test_ticker_is_required():
    client = TestClient(app)

    response = client.get("/api/v1/prices")

    assert response.status_code == 422


def test_unknown_ticker_is_rejected():
    client = TestClient(app)

    response = client.get(
        "/api/v1/prices",
        params={"ticker": "doge_usd"},
    )

    assert response.status_code == 422


def test_get_all_prices(monkeypatch):
    monkeypatch.setattr(main, "PriceRepository", FakeRepository)
    app.dependency_overrides[get_db] = override_db

    try:
        response = TestClient(app).get(
            "/api/v1/prices",
            params={"ticker": "btc_usd"},
        )

        assert response.status_code == 200
        assert len(response.json()) == 2
    finally:
        app.dependency_overrides.clear()


def test_latest_price(monkeypatch):
    monkeypatch.setattr(main, "PriceRepository", FakeRepository)
    app.dependency_overrides[get_db] = override_db

    try:
        response = TestClient(app).get(
            "/api/v1/prices/latest",
            params={"ticker": "btc_usd"},
        )

        assert response.status_code == 200
        assert response.json()["price"] == "65100.50"
    finally:
        app.dependency_overrides.clear()


def test_latest_price_returns_error(monkeypatch):
    monkeypatch.setattr(main, "PriceRepository", EmptyRepository)
    app.dependency_overrides[get_db] = override_db

    try:
        response = TestClient(app).get(
            "/api/v1/prices/latest",
            params={"ticker": "eth_usd"},
        )

        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_filter_prices_by_date(monkeypatch):
    monkeypatch.setattr(main, "PriceRepository", FakeRepository)
    app.dependency_overrides[get_db] = override_db

    try:
        response = TestClient(app).get(
            "/api/v1/prices/by-date",
            params={
                "ticker": "btc_usd",
                "date": "2026-10-14",
            },
        )

        assert response.status_code == 200
        assert len(response.json()) == 2
    finally:
        app.dependency_overrides.clear()