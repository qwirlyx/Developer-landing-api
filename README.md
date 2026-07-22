# Developer Landing API

Backend-сервис для лендинг-презентации разработчика.

Проект показывает полный цикл обработки заявки: пользователь отправляет форму, backend валидирует данные, применяет rate limiting, анализирует комментарий через AI, формирует email-уведомления, сохраняет служебные данные и возвращает ответ API.

Дополнительно добавлена demo-страница, через которую можно проверить работу формы без Postman.

## Стек

- Python 3.9+
- FastAPI
- Pydantic
- HTTPX
- OpenRouter API
- SMTP
- JSON-файлы для хранения логов, метрик и rate limiting
- HTML / CSS / JavaScript
- Swagger/OpenAPI

Проект проверялся на Python 3.12.

## Что реализовано

- `POST /api/contact` — обработка формы обратной связи
- `GET /api/health` — проверка статуса сервиса
- `GET /api/metrics` — статистика обращений
- валидация имени, телефона, email и комментария
- AI-анализ комментария через OpenRouter
- fallback на случай, если AI недоступен
- отправка email владельцу сайта
- отправка копии письма пользователю
- локальный outbox для проверки сформированных писем
- rate limiting по IP
- логирование запросов в файл
- глобальная обработка ошибок
- CORS
- Swagger/OpenAPI документация
- demo-страница на `/`

## Структура проекта

```text
app/
├── api/              # API endpoints
├── core/             # логирование и обработка исключений
├── repositories/     # работа с файлами хранения
├── schemas/          # Pydantic-схемы
├── services/         # основная бизнес-логика
├── storage/          # локальное хранилище
├── config.py         # настройки проекта
└── main.py           # точка входа приложения

frontend/
├── index.html        # demo-страница
├── styles.css        # стили
└── script.js         # отправка формы в API
```

Архитектура разделена по слоям:

```text
API layer → Services → Repositories / Handlers
```

Так роутинг, бизнес-логика, работа с файлами и внешними сервисами не смешиваются в одном месте.

## Почему FastAPI

FastAPI выбран, потому что хорошо подходит для небольшого backend-сервиса с REST API:

- быстро настраивается;
- автоматически формирует Swagger/OpenAPI-документацию;
- удобно работает с Pydantic-валидацией;
- поддерживает асинхронные запросы к внешним API;
- позволяет держать структуру проекта простой и понятной.

Для хранения данных используется файловая система. В рамках этого задания базы данных не требуется: логов, метрик и rate limiting через JSON-файлы достаточно.

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

Пример:

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

Файл `.env` не добавляется в репозиторий. В репозитории оставлен только `.env.example`.

### 4. Запустить сервер

```bash
python -m uvicorn app.main:app --reload
```

После запуска:

```text
http://127.0.0.1:8000/       # demo-страница
http://127.0.0.1:8000/docs   # Swagger/OpenAPI
```

## API

### POST `/api/contact`

Обрабатывает форму обратной связи.

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
  "message": "Заявка успешно обработана",
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

Если SMTP не настроен или внешний почтовый сервис недоступен, заявка всё равно обрабатывается, а сформированные письма можно проверить в локальном outbox.

### GET `/api/health`

Проверяет, что сервис запущен.

```json
{
  "status": "ok",
  "service": "Developer Landing API"
}
```

### GET `/api/metrics`

Возвращает статистику обращений.

```json
{
  "total_requests": 1,
  "successful_requests": 1,
  "failed_requests": 0,
  "ai_success": 1,
  "ai_fallback": 0
}
```

## Валидация и ошибки

Валидация сделана через Pydantic.

Проверяются:

- имя;
- телефон;
- email;
- комментарий.

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

Используемые HTTP-статусы:

- `200` — успешная обработка заявки
- `422` — ошибка валидации
- `429` — превышен лимит запросов
- `500` — внутренняя ошибка сервера

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

## Postman

В проект добавлена коллекция:

```text
postman_collection.json
```

В ней есть готовые запросы для проверки:

- статуса сервиса;
- метрик;
- успешной отправки формы;
- ошибки валидации.

Коллекцию можно импортировать в Postman и сразу проверить основные сценарии.

## AI-интеграция

AI-интеграция реализована через OpenRouter API.

AI используется на backend-стороне для анализа комментария из формы. Сервис отправляет текст комментария в AI-модель и получает:

- категорию обращения;
- тональность;
- приоритет;
- вариант ответа.

Пример результата:

```json
{
  "category": "cooperation",
  "tone": "positive",
  "priority": "medium",
  "suggested_reply": "Thank you for your request."
}
```

### Prompt

Основной prompt:

```text
You are an assistant for a developer landing page backend API.
Analyze the contact form comment.
Return only valid JSON without markdown and without explanations.
JSON fields: category, tone, priority, suggested_reply.
category must be one of: job_offer, cooperation, question, complaint, other.
tone must be one of: positive, neutral, negative.
priority must be one of: low, medium, high.
Comment: <user comment>
```

### Fallback

Если AI-сервис недоступен, ключ не указан или модель вернула некорректный ответ, API продолжает работать.

В этом случае возвращается локальный fallback:

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

Это позволяет не ломать обработку формы из-за внешнего AI-сервиса.

## Email-уведомления

После обработки заявки сервис формирует два письма:

- письмо на email из `OWNER_EMAIL`;
- копию пользователю на email из формы.

Отправка выполняется через SMTP.

Для удобной локальной проверки все сформированные письма дополнительно сохраняются в файл:

```text
app/storage/email_outbox.json
```

Это помогает проверить email-логику даже в ситуации, когда внешний почтовый сервис задерживает доставку письма.

## Хранение данных

База данных в проекте не используется, потому что для текущей задачи достаточно файлового хранения.

Автоматически создаются:

```text
app/storage/metrics.json       # статистика обращений
app/storage/rate_limit.json    # данные rate limiting
app/storage/email_outbox.json  # локальные копии сформированных email
app/storage/requests.log       # логи запросов
```

Эти файлы не добавляются в Git.

## Rate limiting

Rate limiting работает по IP-адресу клиента.

Настройки задаются через `.env`:

```env
RATE_LIMIT_MAX_REQUESTS=5
RATE_LIMIT_WINDOW_SECONDS=3600
```

Если лимит превышен, API возвращает:

```json
{
  "status": "error",
  "message": "Too many requests. Please try again later."
}
```

HTTP status code: `429`.

## Логирование

Все запросы логируются в файл:

```text
app/storage/requests.log
```

В лог пишутся:

- HTTP-метод;
- путь запроса;
- статус ответа;
- IP-адрес;
- время обработки;
- ошибки, если они возникли.

## Frontend

Frontend добавлен как demo-страница для проверки API.

На странице можно:

- посмотреть статус API;
- отправить тестовую заявку;
- увидеть JSON-ответ от backend;
- перейти в Swagger.

Форма отправляет запрос напрямую в `POST /api/contact`.

## Использование AI при разработке

По условию задания в проекте реализована backend AI-функция. Она используется не для генерации страницы, а как часть логики сервиса: анализирует комментарий из формы и помогает классифицировать обращение.

При разработке AI использовался ограниченно: как вспомогательный инструмент для проверки prompt, формулировок ошибок и отдельных вариантов реализации.

Основная работа выполнялась вручную:

- проектирование структуры проекта;
- настройка FastAPI;
- реализация API;
- валидация через Pydantic;
- обработка ошибок;
- rate limiting;
- логирование;
- email-логика;
- сохранение писем в outbox;
- frontend-страница;
- проверка через Swagger и Postman.

Готовые решения не переносились без проверки: код адаптировался, запускался локально и дорабатывался вручную под требования задания.
