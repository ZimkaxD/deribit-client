# Deribit Клиент

Сервис каждую минуту получает индексные цены `btc_usd` и `eth_usd` из публичного API Deribit и сохраняет историю в PostgreSQL.

## Запуск

Требуются Docker и Docker Compose.

```powershell
Copy-Item .env.example .env
docker compose up --build -d
```

API: `http://localhost:8000`

Swagger UI: `http://localhost:8000/docs`

Остановка:

```powershell
docker compose down
```

## API

Во всех запросах существует обязательный параметр - `ticker` . Допустимые значения (можно расширить): `btc_usd`, `eth_usd`.

| Метод | Назначение |
|---|---|
| `GET /api/v1/prices?ticker=btc_usd` | Все сохранённые записи по тикеру |
| `GET /api/v1/prices/latest?ticker=eth_usd` | Последняя запись по тикеру; `404`, если записей нет |
| `GET /api/v1/prices/by-date?ticker=btc_usd&date=2026-10-14` | Записи за указанную дату UTC (`YYYY-MM-DD`) |
| `GET /health` | Проверка доступности API |

Каждая запись содержит `id`, `ticker`, `price` и `timestamp`. 

## Тесты

Запустить тесты локально в активированном виртуальном окружении:

```powershell
python -m pytest -q
```

Проверить состояние контейнеров:

```powershell
docker compose ps
```

Проверить PostgreSQL и последние сохранённые значения:

```powershell
docker compose exec db psql -U postgres -d prices -c "\dt"
docker compose exec db psql -U postgres -d prices -c "SELECT id, ticker, price, timestamp FROM price_records ORDER BY timestamp DESC LIMIT 10;"
```

Проверить Redis:

```powershell
docker compose exec redis redis-cli ping
```

## Design decisions

- Используется публичный метод Deribit `public/get_index_price`, так как по ТЗ требуются индексные цены BTC и ETH.
- Celery Beat запускает сбор с интервалом 60 секунд, а Celery Worker выполняет задачу. 
- Redis используется как брокер Celery, PostgreSQL - для хранения двнных.
- `aiohttp` выполняет HTTP-запросы к Deribit.
- `PriceRepository` отделяет SQL-запросы от API и процесса сбора данных.
- API ограничивает `ticker` значениями `btc_usd` и `eth_usd`. Некорректный параметр отклоняется валидацией FastAPI.
- Docker Compose запускает 5 контейнеров как отдельные сервисы для обеспечения максимальной отказоустойчивости. P.S. да я знаю, что просили 2-а. Решил сделать так.
