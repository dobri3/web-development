# Cinema Project

Проект делится на три части:

1. **Django + DRF** — основной сервис каталога фильмов и watchlist.
2. **FastAPI** — отдельный микросервис авторизации, JWT и уведомлений по watchlist.
3. **Flask** — отдельный микросервис UGC: отзывы, комментарии, рейтинги и модерация статусов.

---

## 1. Общая архитектура

```text
web-development/
├── cinema_project/          # настройки и URL-конфигурация Django-проекта
├── api/                     # DRF serializers, viewsets, urls, обработчик ошибок
├── domain/                  # доменные модели и доменные исключения
├── movies/                  # Django app для регистрации моделей в админке
├── services/                # бизнес-логика Django, вынесенная из viewset
├── fastapi_service/         # отдельный FastAPI-сервис: auth, JWT, watchlist notify
├── flask_service/           # отдельный Flask-сервис: UGC и модерация
├── manage.py                # запуск Django-команд
├── db.sqlite3               # локальная SQLite-база Django
└── requirements.txt         # зависимости основного Django-проекта
```

---

## 2. Django-сервис

Django хранит каталог фильмов, жанры, подписки и watchlist пользователей.

### 2.1. Основные модули Django

#### `cinema_project/settings.py`

Настройки Django в котором:

- стандартные Django-приложения;
- `movies`;
- `api`;
- `domain`;
- `rest_framework`;
- `django_filters`.

Также здесь настроены:

- загрузка переменных окружения через `python-dotenv`;
- база данных через `dj_database_url`;
- пагинация DRF;
- кастомный обработчик ошибок `api.exception_handler.custom_exception_handler`.

#### `cinema_project/urls.py`

Главная URL-конфигурация Django:

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
```

Все DRF-эндпоинты доступны с префиксом `/api/`.

#### `domain/models.py`

Содержит доменные модели:

| Модель | Назначение |
|---|---|
| `Genre` | Жанр фильма. Поля: `name`. |
| `Movie` | Фильм. Поля: `title`, `description`, `release_year`, связь many-to-many с `Genre`. |
| `Subscription` | Подписка пользователя. Связана с `auth.User`, содержит `expires_at` и `is_active`. |
| `Watchlist` | Фильм в списке просмотра пользователя. Связан с `auth.User` и `Movie`. |

Для `Watchlist` задано ограничение уникальности:

```python
unique_together = ('user', 'movie')
```

Один и тот же пользователь не может добавить один и тот же фильм в watchlist дважды.

#### `domain/exceptions.py`

Здесь описаны доменные исключения. Все они наследуются от `DomainError` и содержат:

- `status_code` — HTTP-статус;
- `error_code` — машинно-читаемый код ошибки;
- текстовое описание ошибки.

Примеры:

| Исключение | HTTP-статус | Код ошибки | Когда возникает |
|---|---:|---|---|
| `MovieNotFound` | 404 | `MOVIE_NOT_FOUND` | Фильм не найден. |
| `AlreadyInWatchlist` | 409 | `ALREADY_IN_WATCHLIST` | Фильм уже есть в watchlist пользователя. |
| `WatchlistItemNotFound` | 404 | `WATCHLIST_ITEM_NOT_FOUND` | Запись watchlist не найдена при удалении. |
| `WatchlistLimitExceededError` | 400 | `WATCHLIST_LIMIT_EXCEEDED` | Превышен лимит фильмов в watchlist. |
| `UserNotAuthorized` | 401 | `USER_NOT_AUTHORIZED` | Пользователь не авторизован. |
| `PermissionDenied` | 403 | `PERMISSION_DENIED` | Нет прав доступа. |
| `GenreNotFoundError` | 404 | `GENRE_NOT_FOUND` | Жанр не найден. |

#### `api/exception_handler.py`

Кастомный обработчик ошибок DRF. Если выброшено доменное исключение `DomainError`, ответ приводится к единому формату:

```json
{
  "error": "MOVIE_NOT_FOUND",
  "detail": "Movie with id 10 not found"
}
```

#### `api/serializers.py`

Содержит DRF-сериализаторы:

| Сериализатор | Назначение |
|---|---|
| `GenreSerializer` | Возвращает название жанра. |
| `MovieSerializer` | Возвращает данные фильма: `id`, `title`, `description`, `release_year`, `genres`. |
| `WatchlistSerializer` | Принимает `movie` как id фильма, а `user` и `added_at` отдаёт только для чтения. |

#### `api/views.py`

Содержит два viewset-класса.

##### `MovieViewSet`

Наследуется от `ReadOnlyModelViewSet`, поэтому поддерживает только чтение:

- список фильмов;
- получение одного фильма по id.

Доступ открыт всем пользователям:

```python
permission_classes = [permissions.AllowAny]
```

Поддерживаются:

- поиск по `title`, `description`, `genres__name`;
- сортировка по `title`, `release_year`;
- фильтрация по query-параметрам `genre` и `release_year`.

##### `WatchlistViewSet`

Поддерживает:

- получение watchlist текущего пользователя;
- добавление фильма;
- удаление фильма.

Доступ только для авторизованных пользователей:

```python
permission_classes = [permissions.IsAuthenticated]
```

Viewset не содержит бизнес-логику напрямую. Он вызывает функции из `services/watchlist_service.py`.

#### `services/watchlist_service.py`

Сервисный слой для операций с watchlist.

Функция `add_to_watchlist(user, movie_id)`:

1. Ищет фильм в базе Django.
2. Если фильма нет — выбрасывает `MovieNotFound`.
3. Проверяет, что фильм ещё не добавлен пользователем.
4. Если фильм уже есть — выбрасывает `AlreadyInWatchlist`.
5. Создаёт запись `Watchlist` в транзакции.
6. Отправляет HTTP-запрос в FastAPI на `/watchlist/notify`.
7. Если FastAPI недоступен, Django не падает, а пишет предупреждение в лог.

Функция `remove_from_watchlist(user, movie_id)`:

1. Удаляет запись watchlist пользователя.
2. Если такой записи не было — выбрасывает `WatchlistItemNotFound`.

Таким образом, viewset занимается HTTP-слоем, а `watchlist_service.py` — бизнес-правилами.

---

## 3. Django API endpoints

Все Django-эндпоинты находятся под префиксом `/api/`.

### 3.1. Фильмы

#### `GET /api/movies/`

Возвращает список фильмов.

Пример ответа:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "The Matrix",
      "description": "A computer hacker learns about the true nature of reality.",
      "release_year": 1999,
      "genres": ["Action", "Sci-Fi"]
    }
  ]
}
```

Поддерживаемые query-параметры:

| Параметр | Пример | Назначение |
|---|---|---|
| `search` | `/api/movies/?search=matrix` | Поиск по названию, описанию и жанрам. |
| `genre` | `/api/movies/?genre=action` | Фильтр по названию жанра. |
| `release_year` | `/api/movies/?release_year=1999` | Фильтр по году выпуска. |
| `ordering` | `/api/movies/?ordering=title` | Сортировка по названию. |
| `ordering` | `/api/movies/?ordering=-release_year` | Сортировка по году выпуска по убыванию. |

#### `GET /api/movies/{id}/`

Возвращает один фильм по id.

Пример:

```http
GET /api/movies/1/
```

Если фильм не найден, DRF вернёт 404.

### 3.2. Watchlist

Эндпоинты watchlist требуют авторизации Django/DRF.

В проекте не задан кастомный `DEFAULT_AUTHENTICATION_CLASSES`, используются стандартные механизмы DRF: session authentication и basic authentication.

#### `GET /api/watchlist/`

Возвращает watchlist текущего авторизованного пользователя.

Пример ответа:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "user": "testuser",
      "movie": 1,
      "added_at": "2026-04-24T06:59:00Z"
    }
  ]
}
```

#### `POST /api/watchlist/`

Добавляет фильм в watchlist текущего пользователя.

Тело запроса:

```json
{
  "movie": 1
}
```

Успешный ответ:

```json
{
  "user": "testuser",
  "movie": 1,
  "added_at": "2026-04-24T06:59:00Z"
}
```

Возможные ошибки:

| Ситуация | HTTP-статус | Формат ошибки |
|---|---:|---|
| Пользователь не авторизован | 403 или 401 | стандартный ответ DRF |
| Фильм уже есть в watchlist | 409 | `ALREADY_IN_WATCHLIST` |
| Фильм не найден | 404 | ошибка валидации serializer или `MOVIE_NOT_FOUND` |

После успешного добавления Django пытается уведомить FastAPI-сервис через `POST /watchlist/notify`.

#### `DELETE /api/watchlist/{id}/`

Удаляет запись watchlist по id записи watchlist, а не по id фильма.

Пример:

```http
DELETE /api/watchlist/5/
```

Успешный ответ — пустой ответ со статусом `204 No Content`.

---

## 4. FastAPI-сервис

FastAPI-сервис расположен в папке `fastapi_service/` и запускается отдельно от Django. Он показывает работу:

- async-эндпоинтов;
- Pydantic-схем;
- JWT-авторизации;
- фоновых задач;
- интеграции с Django через notify-эндпоинт.

### 4.1. Основные файлы FastAPI

| Файл | Назначение |
|---|---|
| `fastapi_service/main.py` | Создаёт объект `FastAPI`, подключает роутеры, настраивает logging. |
| `fastapi_service/config.py` | Читает настройки JWT из переменных окружения. |
| `fastapi_service/database.py` | Содержит in-memory словарь `fake_users_db`. Данные не сохраняются после перезапуска. |
| `fastapi_service/auth.py` | Хэширование паролей, создание JWT, проверка Bearer token. |
| `fastapi_service/schemas.py` | Pydantic-модели запросов и ответов. |
| `fastapi_service/tasks.py` | Фоновая задача `notify_user`. |
| `fastapi_service/routers/auth_router.py` | Роуты регистрации и входа. |
| `fastapi_service/routers/watchlist_router.py` | Роуты watchlist и notify. |

### 4.2. JWT-логика

В `auth.py` реализованы функции:

| Функция | Что делает |
|---|---|
| `hash_password` | Хэширует пароль через bcrypt. |
| `verify_password` | Проверяет пароль относительно хэша. |
| `create_access_token` | Создаёт access token с типом `access`. |
| `create_refresh_token` | Создаёт refresh token с типом `refresh`. |
| `get_current_user` | Проверяет Bearer token и возвращает текущего пользователя. |

Access token используется для защищённых запросов. Refresh token генерируется при логине.

### 4.3. FastAPI endpoints

#### `GET /health`

Проверка, что FastAPI-сервис запущен.

Ответ:

```json
{
  "status": "ok"
}
```

#### `POST /auth/register`

Регистрирует пользователя во временном in-memory хранилище.

Тело запроса:

```json
{
  "email": "student@example.com",
  "password": "qwerty123"
}
```

Успешный ответ:

```json
{
  "message": "Регистрация успешна"
}
```

Особенности:

- email валидируется через `EmailStr`;
- пароль сохраняется не в открытом виде, а как bcrypt-хэш;
- данные лежат в `fake_users_db`, поэтому после перезапуска сервиса пользователь исчезает.

#### `POST /auth/login`

Проверяет email и пароль, возвращает пару токенов.

Тело запроса:

```json
{
  "email": "student@example.com",
  "password": "qwerty123"
}
```

Ответ:

```json
{
  "access_token": "jwt-access-token",
  "refresh_token": "jwt-refresh-token"
}
```

#### `POST /watchlist/`

Защищённый endpoint. Требует заголовок:

```http
Authorization: Bearer <access_token>
```

Тело запроса:

```json
{
  "movie_id": 1
}
```

Что происходит внутри:

1. FastAPI проверяет access token через `Depends(get_current_user)`.
2. Pydantic валидирует тело запроса.
3. Добавляется фоновая задача `notify_user`.
4. Endpoint сразу возвращает ответ клиенту.
5. Фоновая задача пишет в лог имитацию отправки уведомления.

Успешный ответ:

```json
{
  "status": "added",
  "movie_id": 1
}
```

Важно: этот endpoint не записывает данные в Django-базу. Он демонстрирует защищённый async endpoint и background task.

#### `POST /watchlist/notify`

Endpoint для интеграции с Django. Его вызывает `services/watchlist_service.py` после успешного добавления фильма в Django watchlist.

Тело запроса:

```json
{
  "user_id": 1,
  "movie_id": 10
}
```

Ответ:

```json
{
  "status": "received"
}
```

Этот endpoint не требует JWT. Он принимает внутреннее уведомление от Django и пишет событие в лог.

---

## 5. Flask UGC service

Flask-сервис расположен в папке `flask_service/`. Он отвечает за пользовательский контент:

- отзывы;
- комментарии;
- рейтинги;
- статусы модерации.

Сервис использует SQLAlchemy и локальную SQLite-базу. По умолчанию база создаётся автоматически при запуске приложения.

### 5.1. Основные файлы Flask

| Файл | Назначение |
|---|---|
| `flask_service/app.py` | Создаёт Flask-приложение, модель `UGC`, endpoints. |
| `flask_service/validation.py` | Ручная валидация входных данных. |
| `flask_service/integrations.py` | HTTP-проверка существования фильма в Django. |
| `flask_service/requirements.txt` | Зависимости Flask-сервиса. |

### 5.2. Модель UGC

Модель `UGC` содержит поля:

| Поле | Тип | Описание |
|---|---|---|
| `id` | integer | Первичный ключ. |
| `type` | string | Тип контента: `review`, `comment`, `rating`. |
| `text` | text | Текст пользовательского контента. |
| `rating` | float | Оценка от 1 до 10. |
| `status` | string | Статус: `pending`, `active`, `hidden`. |
| `movie_id` | integer | id фильма из Django-сервиса. |
| `created_at` | datetime | Время создания. |

В базе также заданы `CheckConstraint`, которые дополнительно защищают данные на уровне БД:

- `type IN ('review', 'comment', 'rating')`;
- `status IN ('active', 'hidden', 'pending')`;
- `rating >= 1 AND rating <= 10`.

### 5.3. Flask endpoints

#### `GET /health`

Проверка, что Flask-сервис запущен.

Ответ:

```json
{
  "status": "ok"
}
```

#### `POST /ugc/`

Создаёт новый UGC-объект.

Тело запроса:

```json
{
  "type": "review",
  "text": "Хороший фильм",
  "rating": 8,
  "movie_id": 1
}
```

Валидация:

| Поле | Правило |
|---|---|
| `type` | Только `review`, `comment`, `rating`. |
| `text` | Непустая строка, максимум 1000 символов. |
| `rating` | Число от 1 до 10, `bool` не допускается. |
| `movie_id` | Положительное целое число. |

Перед сохранением Flask пытается проверить, существует ли фильм в Django:

```text
Flask -> GET http://127.0.0.1:8000/api/movies/{movie_id}/
```

Если Django доступен и фильм не найден, Flask вернёт 404. Если Django недоступен, Flask пишет предупреждение в лог и продолжает создание UGC.

Новый UGC создаётся со статусом `pending`.

Успешный ответ:

```json
{
  "data": {
    "id": 1,
    "type": "review",
    "text": "Хороший фильм",
    "rating": 8,
    "status": "pending",
    "movie_id": 1,
    "created_at": "2026-04-24T06:59:00Z"
  }
}
```

#### `GET /ugc/?movie_id={id}`

Возвращает только активный UGC по конкретному фильму.

Пример:

```http
GET /ugc/?movie_id=1
```

Сервис отдаёт только записи со статусом `active`. Записи `pending` и `hidden` в публичную выдачу не попадают.

#### `PATCH /ugc/{ugc_id}/status`

Обновляет статус UGC-записи.

Тело запроса:

```json
{
  "status": "active"
}
```

Допустимые статусы:

- `active`;
- `hidden`;
- `pending`.

Этот endpoint можно использовать как простую модерацию: сначала отзыв создаётся в `pending`, затем модератор переводит его в `active` или `hidden`.

---

## 6. Как сервисы взаимодействуют

### 6.1. Добавление фильма в watchlist через Django

```text
Клиент
  |
  | POST /api/watchlist/
  v
Django DRF WatchlistViewSet
  |
  | вызывает add_to_watchlist(user, movie_id)
  v
services/watchlist_service.py
  |
  | создаёт Watchlist в Django DB
  |
  | POST /watchlist/notify
  v
FastAPI service
  |
  | пишет событие в лог
  v
Ответ клиенту от Django
```

Примечание: если FastAPI не запущен, Django всё равно завершит добавление фильма в watchlist. Ошибка интеграции не ломает основной сценарий.

### 6.2. Создание UGC через Flask

```text
Клиент
  |
  | POST /ugc/
  v
Flask UGC service
  |
  | валидирует тело запроса
  |
  | GET /api/movies/{movie_id}/
  v
Django movie API
  |
  | подтверждает наличие фильма
  v
Flask сохраняет UGC в своей БД
```

Если Django доступен и фильма нет — Flask возвращает 404. Если Django недоступен — Flask разрешает создать UGC, но пишет предупреждение в лог.

### 6.3. FastAPI watchlist endpoint

```text
Клиент
  |
  | POST /auth/register
  | POST /auth/login
  v
FastAPI auth
  |
  | возвращает access_token
  v
Клиент
  |
  | POST /watchlist/ с Bearer token
  v
FastAPI watchlist
  |
  | запускает background task notify_user
  v
Ответ клиенту сразу, уведомление выполняется в фоне
```

Этот сценарий демонстрирует JWT и background tasks. Он не синхронизирует данные с Django watchlist.

---

## 7. Переменные окружения

В корне проекта есть `.env.example`:

```env
SECRET_KEY="django-insecure-..."
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3
```

Для полноценного запуска интеграций также полезно задать:

```env
FASTAPI_SERVICE_URL=http://127.0.0.1:8001
DJANGO_SERVICE_URL=http://127.0.0.1:8000
FLASK_DATABASE_URL=sqlite:///ugc.sqlite3
```

Назначение переменных:

| Переменная | Где используется | Назначение |
|---|---|---|
| `SECRET_KEY` | Django и FastAPI | Секретный ключ Django/JWT. |
| `DEBUG` | Django и Flask | Режим отладки. |
| `ALLOWED_HOSTS` | Django | Разрешённые хосты. |
| `DATABASE_URL` | Django | URL основной базы данных. |
| `FASTAPI_SERVICE_URL` | Django `watchlist_service.py` | Адрес FastAPI для notify-запросов. |
| `DJANGO_SERVICE_URL` | Flask `integrations.py` | Адрес Django для проверки фильма. |
| `FLASK_DATABASE_URL` | Flask | База UGC-сервиса. |
| `ALGORITHM` | FastAPI | Алгоритм подписи JWT, по умолчанию `HS256`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | FastAPI | Время жизни access token, по умолчанию 30 минут. |
| `REFRESH_TOKEN_EXPIRE_DAYS` | FastAPI | Время жизни refresh token, по умолчанию 7 дней. |

Примечание: `services/watchlist_service.py` обращается к `settings.FASTAPI_SERVICE_URL`. Перед проверкой интеграции нужно убедиться, что это значение доступно в Django settings.

---

## 8. Установка и запуск

Ниже приведён вариант запуска в трёх отдельных терминалах.

### 8.1. Подготовка окружения

Из корня проекта:

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\activate       # Windows
```

Создать `.env` на основе `.env.example` и заполнить нужные переменные.

### 8.2. Запуск Django

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8000
```

Django admin:

```text
http://127.0.0.1:8000/admin/
```

Django API:

```text
http://127.0.0.1:8000/api/
```

### 8.3. Запуск FastAPI

В отдельном терминале:

```bash
cd fastapi_service
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

Документация Swagger UI:

```text
http://127.0.0.1:8001/docs
```

Healthcheck:

```text
http://127.0.0.1:8001/health
```

### 8.4. Запуск Flask

В отдельном терминале:

```bash
cd flask_service
pip install -r requirements.txt
python app.py
```

По умолчанию Flask запускается на порту `8002`.

Healthcheck:

```text
http://127.0.0.1:8002/health
```

---

## 9. Примеры ручной проверки

### 9.1. Проверить Django movies

```bash
curl http://127.0.0.1:8000/api/movies/
```

С фильтром по жанру:

```bash
curl "http://127.0.0.1:8000/api/movies/?genre=action"
```

С поиском:

```bash
curl "http://127.0.0.1:8000/api/movies/?search=matrix"
```

### 9.2. Добавить фильм в Django watchlist

Пример с basic auth:

```bash
curl -u testuser:password \
  -X POST http://127.0.0.1:8000/api/watchlist/ \
  -H "Content-Type: application/json" \
  -d '{"movie": 1}'
```

Посмотреть watchlist:

```bash
curl -u testuser:password http://127.0.0.1:8000/api/watchlist/
```

### 9.3. Проверить FastAPI auth

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

Запрос к защищённому endpoint:

```bash
curl -X POST http://127.0.0.1:8001/watchlist/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"movie_id":1}'
```

### 9.4. Проверить Flask UGC

Создать отзыв:

```bash
curl -X POST http://127.0.0.1:8002/ugc/ \
  -H "Content-Type: application/json" \
  -d '{"type":"review","text":"Хороший фильм","rating":8,"movie_id":1}'
```

Сделать отзыв активным:

```bash
curl -X PATCH http://127.0.0.1:8002/ugc/1/status \
  -H "Content-Type: application/json" \
  -d '{"status":"active"}'
```

Получить активные отзывы фильма:

```bash
curl "http://127.0.0.1:8002/ugc/?movie_id=1"
```

---

---

## 10. Логирование

В FastAPI и Flask настроен стандартный Python `logging`.

Формат логов:

```text
17:32:01 [INFO] routers.auth_router: Пользователь вошёл: test@example.com
```

Логируются:

- регистрация пользователя;
- вход пользователя;
- неудачные попытки входа;
- добавление в FastAPI watchlist;
- notify-события от Django;
- запуск и завершение фоновой задачи;
- недоступность Django или FastAPI при межсервисных запросах.
