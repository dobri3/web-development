# web-development

# Sprint 2 — Сервисный слой и единый формат ошибок

## Цель спринта

Отделить бизнес-логику от HTTP-слоя, ввести сервисный слой и подготовить кодовую базу к расширению.

---

## Что было сделано

### 1. Сервисный слой (`services/`)

Введён модуль `services/watchlist_service.py`, который инкапсулирует всю бизнес-логику работы с вишлистом. ViewSet-ы теперь только принимают запрос и делегируют выполнение сервису — никакой логики на уровне HTTP.

**`add_to_watchlist(user, movie_id)`** — добавляет фильм в вишлист пользователя:
- проверяет существование фильма → `MovieNotFound`
- проверяет отсутствие дубликата → `AlreadyInWatchlist`
- создаёт запись в транзакции

**`remove_from_watchlist(user, movie_id)`** — удаляет фильм из вишлиста:
- если запись не найдена → `WatchlistItemNotFound`

```python
# До (Sprint 1): логика в ViewSet
def create(self, request, *args, **kwargs):
    movie = Movie.objects.get(pk=request.data["movie"])
    if Watchlist.objects.filter(user=request.user, movie=movie).exists():
        return Response({"error": "already exists"}, status=409)
    item = Watchlist.objects.create(user=request.user, movie=movie)
    ...

# После (Sprint 2): ViewSet вызывает сервис
def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    movie = serializer.validated_data["movie"]
    watchlist_item = add_to_watchlist(user=request.user, movie_id=movie.id)
    ...
```

---

### 2. Модуль доменных исключений (`domain/exceptions.py`)

Введена иерархия исключений с базовым классом `DomainError`. Каждое исключение несёт в себе `status_code` и `error_code` — HTTP-слой не знает деталей бизнес-логики, только получает готовый код и сообщение.

| Исключение                 | `error_code`               | HTTP  | Когда возникает                          |
|----------------------------|----------------------------|-------|------------------------------------------|
| `MovieNotFound`            | `MOVIE_NOT_FOUND`          | 404   | Фильм с указанным id не существует       |
| `AlreadyInWatchlist`       | `ALREADY_IN_WATCHLIST`     | 409   | Фильм уже добавлен в вишлист             |
| `WatchlistItemNotFound`    | `WATCHLIST_ITEM_NOT_FOUND` | 404   | Фильм не найден в вишлисте при удалении  |
| `WatchlistLimitExceededError` | `WATCHLIST_LIMIT_EXCEEDED` | 400 | Превышен лимит в 100 фильмов             |
| `InvalidMovieData`         | `INVALID_MOVIE_DATA`       | 400   | Некорректные данные фильма               |
| `UserNotAuthorized`        | `USER_NOT_AUTHORIZED`      | 401   | Пользователь не авторизован              |
| `PermissionDenied`         | `PERMISSION_DENIED`        | 403   | Нет прав доступа                         |
| `GenreNotFoundError`       | `GENRE_NOT_FOUND`          | 404   | Жанр не найден                           |

---

### 3. Единый обработчик ошибок (`api/exception_handler.py`)

Кастомный `exception_handler` перехватывает все `DomainError` и переводит их в HTTP-ответ единого формата. Подключён в `settings.py` через `REST_FRAMEWORK['EXCEPTION_HANDLER']`.

**Формат ответа при ошибке:**
```json
{
  "error": "ALREADY_IN_WATCHLIST",
  "detail": "Movie with id 3 is already in john's watchlist"
}
```

Стандартные ошибки DRF (валидация, 404 от `get_object_or_404`) по-прежнему обрабатываются дефолтным хендлером — кастомный вызывает его первым.

---

### 4. Рефакторинг API (`api/views.py`)

ViewSet-ы освобождены от бизнес-логики. Сериализаторы остались на уровне валидации входных данных — они не знают о доменных правилах.

```
Запрос → Serializer.is_valid() → service() → Response
                                     ↓
                              DomainError → exception_handler → Response с error_code
```

---

### 5. Конфигурация через окружение (`cinema_project/settings.py`)

Все чувствительные и среда-зависимые параметры вынесены в `.env`. Настройки читаются через `python-dotenv` и `dj-database-url`.

```python
SECRET_KEY    = os.getenv('SECRET_KEY')
DEBUG         = os.getenv('DEBUG')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')
DATABASE_URL  = os.getenv('DATABASE_URL')  # → dj_database_url.parse(...)
```

Файл `.env.example` содержит все необходимые переменные без секретных значений и добавлен в репозиторий.

---

### 6. Unit-тесты на сервисный слой (`services/test.py`)

Тесты проверяют бизнес-логику напрямую, без HTTP-запросов. Используют `django.test.TestCase` и работают с реальной тестовой БД.

```bash
python manage.py test services
```

| Тест                                | Что проверяет                                      |
|-------------------------------------|----------------------------------------------------|
| `test_add_to_watchlist_success`     | Фильм успешно добавляется, объект возвращается     |
| `test_add_duplicate_raises_error`   | Повторное добавление поднимает `AlreadyInWatchlist`|
| `test_add_nonexistent_movie_raises_error` | Несуществующий id поднимает `MovieNotFound`  |
| `test_remove_from_watchlist_success`| Фильм удаляется, запись исчезает из БД             |

---

## Структура изменений

```
+ services/
+     __init__.py
+     watchlist_service.py   # новый: бизнес-логика вишлиста
+     test.py                # новый: unit-тесты сервисов
+ domain/
+     exceptions.py          # новый: иерархия доменных исключений
~ domain/
~     models.py              # без изменений
+ api/
+     exception_handler.py   # новый: кастомный обработчик ошибок
~ api/
~     views.py               # рефакторинг: логика делегирована сервисам
~     serializers.py         # без изменений
~ cinema_project/
~     settings.py            # добавлен EXCEPTION_HANDLER, конфиг через .env
+ .env.example               # новый: шаблон переменных окружения
```

## как запустить проект
1. создать `.env`-файл в корне проекта с содержанием файла `.env.example`
2. поменять в нем `SECRET_KEY` на настоящий
3. создать и применить миграции к базе данных:
```
python manage.py makemigrations
python manage.py migrate
```
4. запустить сервер
```
python manage.py runserver
```
