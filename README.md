# Cinema Project

Учебный backend-проект для кинотеатра. Проект состоит из нескольких сервисов и показывает работу с Django REST Framework, сервисным слоем, Flask и FastAPI.

## Состав проекта

```text
web-development/
├── cinema_project/          # настройки Django-проекта
├── api/                     # DRF serializers, viewsets, urls, обработчик ошибок
├── domain/                  # доменные модели и исключения
├── movies/                  # Django app для регистрации моделей в admin
├── services/                # бизнес-логика Django-приложения
├── flask_service/           # UGC-сервис на Flask
├── fastapi_service/         # FastAPI-сервис авторизации и async-сценариев
├── manage.py                # Django CLI
├── requirements.txt         # зависимости основного проекта и тестов
└── .env.example             # пример переменных окружения
```

Основные части:

- **Django + DRF** — каталог фильмов, жанры, подписки и watchlist.
- **Service layer** — бизнес-логика вынесена из HTTP-слоя в `services/`.
- **Flask** — отдельный UGC-сервис для отзывов, комментариев, рейтингов и модерации.
- **FastAPI** — отдельный сервис с JWT-авторизацией, async endpoint-ами и background task.

## Переменные окружения

В корне есть пример файла `.env.example`:

```env
SECRET_KEY=django-insecure-dev-key-change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3
FASTAPI_SERVICE_URL=http://127.0.0.1:8001
DJANGO_SERVICE_URL=http://127.0.0.1:8000
ADMIN_EMAILS=admin@example.com
MODERATOR_EMAILS=moderator@example.com
```

Перед запуском можно создать локальный `.env`:

```bash
cp .env.example .env
```

Назначение основных переменных:

| Переменная | Где используется | Назначение |
|---|---|---|
| `SECRET_KEY` | Django, Flask/FastAPI JWT | Секретный ключ приложения. |
| `DEBUG` | Django, Flask | Режим отладки. |
| `ALLOWED_HOSTS` | Django | Разрешённые хосты. |
| `DATABASE_URL` | Django | Подключение к основной БД. |
| `FASTAPI_SERVICE_URL` | Django service layer | Адрес FastAPI-сервиса для интеграционных вызовов. |
| `DJANGO_SERVICE_URL` | Flask UGC | Адрес Django API для проверки существования фильма. |
| `ADMIN_EMAILS` | Flask auth/permissions | Email-адреса пользователей с ролью admin. |
| `MODERATOR_EMAILS` | Flask auth/permissions | Email-адреса пользователей с ролью moderator. |

## Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Для Windows активация окружения будет другой:

```bash
.venv\Scripts\activate
```

## Запуск Django

Из корня проекта:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8000
```

Админка:

```text
http://127.0.0.1:8000/admin/
```

Django API:

```text
http://127.0.0.1:8000/api/
```

## Django-модели

Основные модели находятся в `domain/models.py`.

| Модель | Назначение |
|---|---|
| `Genre` | Жанры фильмов. |
| `Movie` | Фильмы каталога. |
| `Subscription` | Подписка пользователя. |
| `Watchlist` | Список фильмов пользователя. |

Для `Watchlist` используется ограничение уникальности по паре `user + movie`, чтобы один пользователь не мог добавить один и тот же фильм несколько раз.

## Django API

Все endpoint-ы Django доступны с префиксом `/api/`.

### Movies

```http
GET /api/movies/
GET /api/movies/{id}/
```

Список фильмов поддерживает:

| Параметр | Пример | Назначение |
|---|---|---|
| `search` | `/api/movies/?search=matrix` | Поиск по названию, описанию и жанрам. |
| `genre` | `/api/movies/?genre=action` | Фильтрация по жанру. |
| `release_year` | `/api/movies/?release_year=1999` | Фильтрация по году выпуска. |
| `ordering` | `/api/movies/?ordering=title` | Сортировка по названию. |
| `ordering` | `/api/movies/?ordering=-release_year` | Сортировка по году выпуска по убыванию. |

Пример:

```bash
curl "http://127.0.0.1:8000/api/movies/?search=matrix"
```

### Watchlist

Endpoint-ы watchlist требуют авторизации Django/DRF.

```http
GET /api/watchlist/
POST /api/watchlist/
DELETE /api/watchlist/{id}/
```

Добавление фильма:

```bash
curl -u testuser:password \
  -X POST http://127.0.0.1:8000/api/watchlist/ \
  -H "Content-Type: application/json" \
  -d '{"movie": 1}'
```

`DELETE /api/watchlist/{id}/` удаляет запись watchlist по id самой записи, а не по id фильма.

### Subscription

Endpoint-ы подписки требуют авторизации.

```http
GET  /api/subscription/
POST /api/subscription/
GET  /api/subscription/active/
POST /api/subscription/cancel/
```

Назначение:

| Endpoint | Что делает |
|---|---|
| `GET /api/subscription/` | Возвращает подписку текущего пользователя. |
| `POST /api/subscription/` | Создаёт или продлевает подписку. |
| `GET /api/subscription/active/` | Проверяет активную подписку. |
| `POST /api/subscription/cancel/` | Отменяет подписку. |

## Service layer

Бизнес-логика Django вынесена в папку `services/`.

| Файл | Назначение |
|---|---|
| `services/movie_service.py` | Получение списка фильмов и одного фильма. |
| `services/watchlist_service.py` | Добавление и удаление фильмов из watchlist. |
| `services/subscription_service.py` | Создание, продление, отмена и проверка подписки. |
| `services/integration_service.py` | Внешние HTTP-вызовы между сервисами. |

HTTP-слой находится в `api/views.py`, а доменные ошибки — в `domain/exceptions.py`. Ошибки приводятся к единому формату через `api/exception_handler.py`.

Пример доменной ошибки:

```json
{
  "error": "ALREADY_IN_WATCHLIST",
  "detail": "Movie with id 1 is already in user's watchlist"
}
```

## Flask UGC service

Flask-сервис находится в папке `flask_service/` и отвечает за пользовательский контент.

### Запуск Flask

Из корня проекта:

```bash
python -m flask_service.app
```

По умолчанию сервис запускается на порту `8002`.

Healthcheck:

```text
http://127.0.0.1:8002/health
```

### UGC-модель

UGC-запись содержит:

| Поле | Описание |
|---|---|
| `id` | ID записи. |
| `type` | Тип: `review`, `comment`, `rating`. |
| `text` | Текст отзыва или комментария. |
| `rating` | Оценка от 1 до 10. |
| `status` | Статус: `pending`, `active`, `hidden`. |
| `movie_id` | ID фильма из Django. |
| `user_id` | ID пользователя из JWT. |
| `created_at` | Дата создания. |

### Flask endpoints

```http
GET   /health
POST  /ugc/
GET   /ugc/?movie_id={id}
GET   /ugc/moderation/
PATCH /ugc/{ugc_id}/status
PATCH /ugc/{ugc_id}/hide
```

Публичный список `GET /ugc/?movie_id={id}` возвращает только записи со статусом `active`.

Создание UGC требует JWT access token:

```bash
curl -X POST http://127.0.0.1:8002/ugc/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"type":"review","text":"Хороший фильм","rating":8,"movie_id":1}'
```

Перед созданием UGC Flask проверяет фильм через Django API:

```text
GET http://127.0.0.1:8000/api/movies/{movie_id}/
```

Если Django недоступен, сервис возвращает ошибку `DJANGO_SERVICE_UNAVAILABLE`.

Модераторские endpoint-ы требуют роль `admin` или `moderator` в JWT:

```http
GET /ugc/moderation/
PATCH /ugc/{ugc_id}/status
```

Пользователь может скрыть собственный UGC через:

```http
PATCH /ugc/{ugc_id}/hide
```

## FastAPI service

FastAPI-сервис находится в папке `fastapi_service/`.

### Запуск FastAPI

Из папки `fastapi_service/`:

```bash
uvicorn main:app --reload --port 8001
```

Документация OpenAPI:

```text
http://127.0.0.1:8001/docs
```

Healthcheck:

```text
http://127.0.0.1:8001/health
```

### FastAPI endpoints

Подключены основные роуты:

```http
GET  /health
POST /auth/register
POST /auth/login
POST /auth/refresh
POST /watchlist/
```

Регистрация:

```bash
curl -X POST http://127.0.0.1:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"student@example.com","password":"qwerty123"}'
```

Логин:

```bash
curl -X POST http://127.0.0.1:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@example.com","password":"qwerty123"}'
```

Защищённый endpoint watchlist:

```bash
curl -X POST http://127.0.0.1:8001/watchlist/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"movie_id":1}'
```

`POST /watchlist/` демонстрирует защищённый async endpoint и background task. Запись в Django-базу при этом не создаётся.

В папке `fastapi_service/routers/` также есть роутеры для фильмов и рекомендаций. Для использования их нужно подключить в `fastapi_service/main.py` через `app.include_router(...)`.

## Взаимодействие сервисов

### Flask -> Django

При создании UGC Flask обращается к Django API, чтобы проверить существование фильма:

```text
Flask /ugc/
  -> Django /api/movies/{movie_id}/
```

### Django -> FastAPI

В `services/watchlist_service.py` после добавления фильма в watchlist есть интеграционный вызов через `services/integration_service.py`. Ошибка внешнего сервиса не должна ломать основной Django-сценарий: watchlist создаётся в Django, а проблема интеграции фиксируется в логах.

### FastAPI -> Django

В `fastapi_service/clients/django_client.py` подготовлен async-клиент для обращения к Django API. Он используется роутерами фильмов и рекомендаций после их подключения в `main.py`.

## Тесты

В проекте есть тесты для Django API, сервисного слоя и Flask-сервиса:

```text
api/tests/
services/tests/
flask_service/tests/
```

Запуск всех тестов из корня проекта:

```bash
pytest
```

Запуск конкретного файла:

```bash
pytest services/tests/test_watchlist_service.py
```

Запуск одного теста:

```bash
pytest services/tests/test_watchlist_service.py::test_add_to_watchlist
```

Если тесты запускаются в новом окружении, сначала нужно установить зависимости:

```bash
pip install -r requirements.txt
```

## Проверка вручную

Обычно удобно запускать сервисы в трёх терминалах.

Терминал 1, Django:

```bash
python manage.py runserver 8000
```

Терминал 2, FastAPI:

```bash
cd fastapi_service
uvicorn main:app --reload --port 8001
```

Терминал 3, Flask:

```bash
python -m flask_service.app
```

После этого можно проверить:

```bash
curl http://127.0.0.1:8000/api/movies/
curl http://127.0.0.1:8001/health
curl http://127.0.0.1:8002/health
```

## Логирование

В сервисах используется стандартный Python `logging`. Логируются основные события:

- регистрация и вход пользователя в FastAPI;
- ошибки JWT;
- добавление фильма в FastAPI watchlist;
- создание и модерация UGC;
- недоступность Django или FastAPI при межсервисных вызовах.

## Что не хранить в репозитории

В репозиторий не нужно добавлять временные и служебные файлы:

```text
__pycache__/
.pytest_cache/
.coverage
*.log
errors.txt
db.sqlite3
*.sqlite3
.env
```

Такие файлы относятся к локальному окружению, тестам или временной отладке и не нужны для запуска проекта другим разработчиком.

## Текущий статус

Проект покрывает основные учебные части:

| Часть | Где реализовано |
|---|---|
| Django ORM, admin, DRF API | `domain/`, `movies/`, `api/` |
| Service layer | `services/` |
| Доменные ошибки и единый формат ошибок | `domain/exceptions.py`, `api/exception_handler.py` |
| Flask UGC | `flask_service/` |
| FastAPI auth, JWT, async endpoint, background task | `fastapi_service/` |
| Интеграция сервисов по HTTP | `services/integration_service.py`, `flask_service/integrations.py`, `fastapi_service/clients/` |
