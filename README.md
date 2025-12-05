# Цифровий щоденник здоров’я (MVP)

Простий MVP цифрового щоденника здоров’я у мікросервісній архітектурі.

## Сервіси

- **gateway** — API Gateway (FastAPI), порти: `8000:8000`
- **complaints-service** — сервіс збереження скарг (FastAPI + SQLite), порти: `8002:8002`
- **nlp-service** — NLP rule-based класифікація (FastAPI), порти: `8001:8001`
- **frontend** — React + Vite SPA, порти: `5173:5173`

## Запуск

Вимоги:

- Docker
- docker-compose

```bash
docker-compose up --build
