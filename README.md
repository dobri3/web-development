# Sprint 3 — FastAPI сервис, async-эндпоинты и JWT-авторизация

## Цель спринта

Добавить отдельный FastAPI микросервис, внедрить async-эндпоинты, JWT-авторизацию и фоновые задачи, настроить интеграцию между Django и FastAPI.

---

## Что было сделано

### Architecture

domain/
    models
    exceptions

services/
    business logic

api/
    serializers
    views
    endpoints

### 1. FastAPI сервис (fastapi_service/)

Создан отдельный сервис в папке fastapi_service/ — независимый процесс, запускается на порту 8001. Не является частью Django-проекта. Имеет собственные зависимости, конфигурацию и точку входа main.py.

Сервис предоставляет автоматическую OpenAPI документацию по адресу /docs — без дополнительной настройки.

---

### 2. JWT-авторизация (fastapi_service/auth.py)

Реализована stateless авторизация на основе JWT токенов. Сервер не хранит сессии — при каждом запросе проверяет подпись токена.

Эндпоинты авторизации:

POST /auth/register — регистрация нового пользователя, пароль хранится в виде bcrypt-хэша.

POST /auth/login — вход, возвращает два токена. Access token живёт 30 минут и передаётся при каждом запросе. Refresh token живёт 7 дней и используется только для получения нового access token.

Защита эндпоинтов реализована через механизм Depends — FastAPI автоматически проверяет токен перед выполнением функции и возвращает 401 если токен отсутствует или невалиден.

---

### 3. Pydantic-схемы (fastapi_service/schemas.py)

Все запросы и ответы описаны через Pydantic-модели. FastAPI автоматически валидирует входящие данные и возвращает 422 если структура не соответствует схеме. Схемы также используются для генерации OpenAPI документации.

---

### 4. Async-эндпоинты

Эндпоинты написаны через async def. Это позволяет FastAPI обрабатывать другие запросы пока текущий ждёт ответа от базы данных или внешнего сервиса. Блокирующие операции внутри async функций запрещены.

---

### 5. Фоновые задачи (fastapi_service/tasks.py)

POST /watchlist/ принимает запрос и немедленно возвращает ответ. После этого FastAPI запускает фоновую задачу notify_user — имитацию отправки уведомления. Пользователь не ждёт выполнения задачи.

---

### 6. Логирование

Настроен стандартный Python logging с единым форматом во всех модулях. Логируются ключевые события: регистрация и вход пользователя, неудачные попытки входа, добавление в вотчлист, старт и завершение фоновой задачи.

Формат записи:

17:32:01 [INFO] routers.auth_router: Пользователь вошёл: test@test.com

---

### 7. Интеграция Django — FastAPI (services/watchlist_service.py)

При добавлении фильма в вотчлист через Django, сервис отправляет HTTP-запрос к FastAPI эндпоинту /watchlist/notify. Вызов обёрнут в try/except с таймаутом 2 секунды — если FastAPI недоступен, Django продолжает работу и пишет предупреждение в лог. URL FastAPI сервиса вынесен в .env.

---

## Структура изменений

```
+ fastapi_service/
+     main.py                 — точка входа, настройка логирования
+     auth.py                 — JWT логика, хэширование паролей, get_current_user
+     config.py               — чтение переменных из .env
+     database.py             — in-memory хранилище пользователей
+     schemas.py              — Pydantic схемы запросов и ответов
+     tasks.py                — фоновая задача notify_user
+     .env                    — секреты FastAPI сервиса
+     requirements.txt        — зависимости FastAPI сервиса
+     routers/
+         auth_router.py      — эндпоинты /auth/register и /auth/login
+         watchlist_router.py — эндпоинты /watchlist/ и /watchlist/notify
~ services/
~     watchlist_service.py    — добавлен HTTP-вызов к FastAPI после add_to_watchlist
~ .env                        — добавлена переменная FASTAPI_SERVICE_URL
```

---

## Как запустить проект

Запускать нужно два сервера одновременно в разных терминалах.

Терминал 1 — FastAPI:

```
cd fastapi_service
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

Терминал 2 — Django:

```
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

FastAPI документация доступна по адресу http://localhost:8001/docs

Django API доступно по адресу http://localhost:8000/api/
