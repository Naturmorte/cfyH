# Інструкції по запуску проєкту та роботі з API Gateway

Цей документ описує:

1. Як **правильно запустити проєкт** (через `docker-compose`) — покроково.
2. Як користуватись **основними ендпоїнтами через API Gateway**:
   - `POST /api/complaints`
   - `GET /api/complaints`
   - `GET /api/health-indicators`

---

## 1. Підготовка середовища

### 1.1. Необхідні інструменти

Переконайся, що в тебе встановлено:

- **Docker**  
- **Docker Compose** (якщо вбудовано в Docker Desktop — ок)

Перевірка:

```bash
docker -v
docker compose version
