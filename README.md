# Developer Landing API

Backend API для тестовой лендинг-презентации разработчика.

Проект включает форму обратной связи, AI-анализ комментария, email-уведомления, rate limiting, логирование, метрики, Swagger/OpenAPI и простой frontend для проверки формы.

## Стек

- Python 3.12
- FastAPI
- Pydantic
- HTTPX
- OpenRouter API
- SMTP
- JSON-файлы для локального хранения метрик и rate limit
- HTML / CSS / JavaScript для demo-страницы
- Swagger/OpenAPI

## Возможности

- `POST /api/contact` — отправка формы обратной связи
- `GET /api/health` — проверка работоспособности API
- `GET /api/metrics` — статистика обращений
- AI-анализ комментария через OpenRouter
- fallback, если AI-сервис недоступен
- отправка email через SMTP
- локальный outbox для проверки сформированных email
- rate limiting по IP
- логирование запросов в файл
- глобальная обработка ошибок
- demo-страница с формой на `/`

## Структура проекта

```text
app/
├── api/              # endpoints
├── core/             # logger, custom exceptions
├── repositories/     # работа с JSON-файлами
├── schemas/          # Pydantic-схемы
├── services/         # бизнес-логика, AI, email, rate limit
├── storage/          # локальные файлы логов и метрик
├── config.py         # настройки из .env
└── main.py           # точка входа FastAPI

frontend/
├── index.html        # demo landing page
├── styles.css        # стили страницы
└── script.js         # отправка формы в API
```

## Запуск проекта

### 1. Создать виртуальное окружение

```bash
python -m venv .venv
```

Windows:

```bash
.\.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 2. Установить зависимости

```bash
pip install -r requirements.txt
```

### 3. Создать `.env`

Создайте файл `.env` на основе `.env.example` и укажите свои значения.

```env
APP_NAME=Developer Landing API
APP_ENV=local
API_PREFIX=/api

CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:8000

OWNER_EMAIL=your_email@example.com

SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USERNAME=your_smtp_login
SMTP_PASSWORD=your_smtp_key
SMTP_FROM_EMAIL=verified_sender@example.com
SMTP_FROM_NAME=Developer Landing
SMTP_USE_TLS=true

OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/gpt-oss-20b:free

RATE_LIMIT_MAX_REQUESTS=5
RATE_LIMIT_WINDOW_SECONDS=3600
```

Файл `.env` не должен попадать в репозиторий.

### 4. Запустить сервер

```bash
python -m uvicorn app.main:app --reload
```

После запуска доступны:

```text
http://127.0.0.1:8000/       # demo-страница
http://127.0.0.1:8000/docs   # Swagger/OpenAPI
```

## API

### POST `/api/contact`

Отправка формы обратной связи.

Пример запроса:

```json
{
  "name": "Ivan Shevchenko",
  "phone": "+79780260009",
  "email": "test@example.com",
  "comment": "Hello! I would like to discuss backend API development with AI integration."
}
```

Пример успешного ответа:

```json
{
  "status": "success",
  "message": "Contact request has been processed",
  "ai": {
    "status": "success",
    "provider": "OpenRouter",
    "model": "openai/gpt-oss-20b:free",
    "result": {
      "category": "cooperation",
      "tone": "positive",
      "priority": "medium",
      "suggested_reply": "Thank you for your request."
    }
  },
  "email": {
    "owner_email_sent": true,
    "user_email_sent": true
  }
}
```

### GET `/api/health`

```json
{
  "status": "ok",
  "service": "Developer Landing API"
}
```

### GET `/api/metrics`

```json
{
  "total_requests": 1,
  "successful_requests": 1,
  "failed_requests": 0,
  "ai_success": 1,
  "ai_fallback": 0
}
```

## Curl-примеры

### Health check

```bash
curl -X GET "http://127.0.0.1:8000/api/health"
```

### Metrics

```bash
curl -X GET "http://127.0.0.1:8000/api/metrics"
```

### Contact request

```bash
curl -X POST "http://127.0.0.1:8000/api/contact" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ivan Shevchenko",
    "phone": "+79780260009",
    "email": "test@example.com",
    "comment": "Hello! I would like to discuss backend API development with AI integration."
  }'
```

## AI-интеграция

AI-интеграция реализована через OpenRouter API.

AI анализирует комментарий из формы и возвращает:

- категорию обращения;
- тональность;
- приоритет;
- вариант ответа.

Если AI-сервис недоступен или ключ не указан, API продолжает работать через fallback.

Пример fallback-ответа:

```json
{
  "status": "fallback",
  "provider": "local",
  "result": {
    "category": "other",
    "tone": "neutral",
    "priority": "medium",
    "suggested_reply": "Спасибо за обращение. Я свяжусь с вами после обработки заявки."
  }
}
```

## Email

Email-уведомления отправляются через SMTP.

Сервис формирует два письма:

- письмо на email из `OWNER_EMAIL`;
- копию пользователю на email из формы.

Для локальной проверки письма дополнительно сохраняются в:

```text
app/storage/email_outbox.json
```

Это позволяет проверить сформированные письма даже в случае задержки доставки внешним почтовым сервисом.

## Хранение данных

В рамках тестового задания база данных не используется. Для простоты используются JSON-файлы:

```text
app/storage/metrics.json
app/storage/rate_limit.json
app/storage/email_outbox.json
app/storage/requests.log
```

Эти файлы создаются автоматически при работе приложения и не добавляются в Git.

## Rate limiting

Rate limiting работает по IP.

Настройки:

```env
RATE_LIMIT_MAX_REQUESTS=5
RATE_LIMIT_WINDOW_SECONDS=3600
```

При превышении лимита API возвращает:

```json
{
  "status": "error",
  "message": "Too many requests. Please try again later."
}
```

HTTP status code: `429`.

## Ошибки

Пример ошибки валидации:

```json
{
  "status": "error",
  "message": "Validation error",
  "details": [
    {
      "field": "body.email",
      "message": "value is not a valid email address",
      "type": "value_error"
    }
  ]
}
```

## Postman

В проекте есть файл:

```text
postman_collection.json
```

Его можно импортировать в Postman и проверить:

- health check;
- metrics;
- успешную отправку формы;
- ошибку валидации.

## Что сделано с помощью AI

AI-инструменты использовались как помощник при разработке:

- декомпозиция тестового задания;
- проектирование структуры проекта;
- подготовка черновиков сервисов;
- генерация prompt для AI-анализа комментария;
- проверка обработки ошибок;
- подготовка README.

Вручную были проверены и доработаны:

- структура проекта;
- Pydantic-валидация;
- fallback при ошибке AI;
- rate limiting;
- email outbox;
- SMTP-отправка;
- формат ответов API;
- логирование;
- Swagger-проверка.

## Деплой

Проект можно развернуть на Render, Railway или другом сервисе для Python backend.

Пример production-команды:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
