# Sprint 1

## Цель спринта

Получить целостный работающий backend-продукт с базовыми данными, управлением через Admin и REST API.

---

## Что было сделано

### 1. Модели (`domain/models.py`)

Описаны четыре основные сущности кинотеатральной платформы.

**`Genre`** — жанр фильма:
- `name` — название жанра

**`Movie`** — фильм:
- `title` — название
- `description` — описание
- `release_year` — год выпуска
- `genres` — жанры (ManyToMany → `Genre`)

**`Subscription`** — подписка пользователя:
- `user` — пользователь (OneToOne → `auth.User`)
- `expires_at` — дата окончания
- `is_active` — активна ли подписка

**`Watchlist`** — запись вишлиста:
- `user` — пользователь (FK → `auth.User`)
- `movie` — фильм (FK → `Movie`)
- `added_at` — дата добавления (проставляется автоматически)
- ограничение `unique_together`: один пользователь не может добавить один фильм дважды

Миграции созданы через Django ORM и находятся в `domain/migrations/`.

---

### 2. Django Admin (`movies/admin.py`)

Все четыре модели зарегистрированы в административной панели. Доступно по адресу `/admin/`.

```
Movie        ✓
Genre        ✓
Subscription ✓
Watchlist    ✓
```

---

### 3. Сериализаторы (`api/serializers.py`)

**`GenreSerializer`** — сериализует жанр (поле `name`).

**`MovieSerializer`** — сериализует фильм. Жанры возвращаются как список названий через `SlugRelatedField`:
```json
{
  "id": 1,
  "title": "Inception",
  "description": "A thief who steals corporate secrets...",
  "release_year": 2010,
  "genres": ["Sci-Fi", "Thriller"]
}
```

**`WatchlistSerializer`** — сериализует запись вишлиста. Принимает `movie` как id (для создания), `user` и `added_at` — только для чтения:
```json
{
  "user": "john",
  "movie": 1,
  "added_at": "2024-03-15T10:30:00Z"
}
```

Валидация входных данных происходит на уровне сериализатора — некорректный `movie` id отклоняется до обращения к БД.

---

### 4. ViewSets и роутер (`api/views.py`, `api/urls.py`)

Все эндпоинты зарегистрированы через `DefaultRouter` и доступны по префиксу `/api/`.

**`MovieViewSet`** — read-only доступ к каталогу фильмов:

| Метод | URL                 | Описание                       |
|-------|---------------------|--------------------------------|
| GET   | `/api/movies/`      | Список фильмов с пагинацией    |
| GET   | `/api/movies/{id}/` | Детальная страница фильма      |

Доступен без аутентификации (`AllowAny`).

**`WatchlistViewSet`** — управление вишлистом текущего пользователя:

| Метод  | URL                    | Описание                     |
|--------|------------------------|------------------------------|
| GET    | `/api/watchlist/`      | Список фильмов в вишлисте    |
| POST   | `/api/watchlist/`      | Добавить фильм               |
| DELETE | `/api/watchlist/{id}/` | Удалить фильм                |

Требует аутентификации (`IsAuthenticated`). Пользователь видит только свой вишлист — фильтрация по `request.user` происходит в `get_queryset`.

---

### 5. Фильтрация и поиск

`MovieViewSet` поддерживает несколько параметров запроса:

| Параметр        | Пример                          | Описание                             |
|-----------------|---------------------------------|--------------------------------------|
| `search`        | `?search=inception`             | Поиск по названию, описанию, жанру   |
| `genre`         | `?genre=thriller`               | Фильтр по жанру (частичное совпадение, без учёта регистра) |
| `release_year`  | `?release_year=2010`            | Фильтр по году выпуска               |
| `ordering`      | `?ordering=release_year`        | Сортировка (`title`, `release_year`) |

---

### 6. Пагинация

Настроена глобально в `settings.py`. По умолчанию 10 записей на страницу.

```json
{
  "count": 42,
  "next": "http://localhost:8000/api/movies/?page=2",
  "previous": null,
  "results": [...]
}
```

---

### 7. Настройки (`cinema_project/settings.py`)

Базовая конфигурация для dev-окружения:

- `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS` — читаются из переменных окружения
- `DATABASE_URL` — подключение к БД через `dj-database-url`
- Подключены приложения: `movies`, `api`, `domain`, `rest_framework`, `django_filters`
- `REST_FRAMEWORK` — настроены пагинация и фильтр-бэкенд

---

## Структура изменений

```
+ domain/
+     models.py            # модели: Movie, Genre, Subscription, Watchlist
+     apps.py
+     migrations/
+         0001_initial.py  # начальная миграция
+ movies/
+     admin.py             # регистрация моделей в Admin
+     apps.py
+ api/
+     serializers.py       # MovieSerializer, GenreSerializer, WatchlistSerializer
+     views.py             # MovieViewSet, WatchlistViewSet
+     urls.py              # DefaultRouter
+     __init__.py
+ cinema_project/
+     settings.py          # конфигурация проекта
+     urls.py              # подключение /admin/ и /api/
```
