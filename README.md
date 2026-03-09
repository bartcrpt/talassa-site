# Talassa Old

Flask-приложение для сайта `talassa-site`, работающее поверх legacy БД и текущей бизнес-логики бронирования.

## Что внутри

- Flask + SQLAlchemy + Flask-Login
- Alembic для миграций
- Публичный сайт в `templates/public`
- Админка и личный кабинет в `templates/admin`, `templates/profile.html`, `templates/my_bookings.html`
- Поиск на `/book` работает по legacy БД
- Витрина `/rooms` и публичные room-detail страницы используют адаптерный слой и данные из `data/next_rooms.json`
- Автономный импорт статей журнала из `scripts/journal_source`: `scripts/import_next_journal.py`

## Структура

- `app.py` - основное Flask-приложение
- `services/rooms.py` - адаптер и общая логика room-каталога, поиска и цен
- `templates/public` - публичные страницы
- `static` - стили, скрипты, ассеты
- `alembic` - миграции
- `data/next_rooms.json` - статический набор 8 типов номеров из Next.js-версии

## Переменные окружения

Скопируй `.env_example` в `.env` и заполни значения:

- `SECRET_KEY`
- `UPLOAD_FOLDER`
- `TELEGRAM_TOKEN`
- `TELEGRAM_GROUP_ID`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`
- `DB_HOST`
- `DB_PORT` при необходимости
- `SMS_API_GATEWAY`
- `SMS_API_KEY`

`TELEGRAM_GROUP_ID` можно использовать и для группы, и для личного чата, если бот уже получил от этого чата `/start`.

## Локальный запуск

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python app.py
```

## Импорт журнала

Скрипт читает статьи из локального источника внутри репозитория и переносит их в legacy-модель `News`:

```bash
python scripts/import_next_journal.py
```

Источник лежит здесь:

- `scripts/journal_source/articles.json`
- `scripts/journal_source/images/*`

То есть для импорта на VPS больше не нужен соседний Next.js-проект.

## Бронирование

- `/rooms` - маркетинговая витрина 8 типов номеров
- `/book` - поиск доступных номеров по legacy БД
- если один номер не вмещает всех гостей, `/book` может предложить комбинацию из двух номеров
- комбинированное бронирование создаёт две стандартные записи `Booking` без изменения схемы БД

## Git

Этот каталог является отдельным git-репозиторием и пушится как `talassa-site`.


