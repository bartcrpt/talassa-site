# Talassa Old

Flask-приложение для сайта `talassa-site`, работающее поверх одной основной базы новой версии сайта.

## Что внутри

- Flask + SQLAlchemy + Flask-Login
- Публичный сайт в `templates/public`
- Админка и личный кабинет в `templates/admin`, `templates/profile.html`, `templates/my_bookings.html`
- Основная база сайта для `user`, `booking`, `room`, `category`, `room_photo`, `news`, `news_photo`, `site_page`, `site_block`
- Поиск на `/book` работает по основной базе сайта
- Витрина `/rooms` и публичные room-detail страницы используют адаптерный слой и данные из `data/next_rooms.json`
- Автономный импорт статей журнала из `scripts/journal_source`: `scripts/import_next_journal.py`
- Служебные скрипты для финальной миграции живых данных из старого сайта

## Структура

- `app.py` - основное Flask-приложение
- `services/rooms.py` - адаптер и общая логика room-каталога, поиска и цен
- `templates/public` - публичные страницы
- `static` - стили, скрипты, ассеты
- `alembic` - миграции проекта
- `data/next_rooms.json` - статический набор 8 типов номеров из Next.js-версии
- `scripts/purge_live_data.py` - очистка `user` / `booking` перед финальной синхронизацией
- `scripts/sync_live_data_from_legacy.py` - перенос `user` / `booking` из свежего legacy-дампа

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
- `DB_PORT`
- `LEGACY_SYNC_DATABASE_URI` для одноразового переноса пользователей и бронирований
- `SMS_API_GATEWAY`
- `SMS_API_KEY`

`TELEGRAM_GROUP_ID` можно использовать и для группы, и для личного чата, если бот уже получил от этого чата `/start`.

## Локальный запуск

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Импорт журнала

Скрипт читает статьи из локального источника внутри репозитория и переносит их в модель `News`:

```bash
python scripts/import_next_journal.py
```

Источник лежит здесь:

- `scripts/journal_source/articles.json`
- `scripts/journal_source/images/*`

## Финальная миграция живых данных

Рекомендуемый порядок перед релизом:

1. Подготовить основную новую базу сайта.
2. Поднять свежий дамп старого сайта во временную legacy-базу.
3. Прописать `LEGACY_SYNC_DATABASE_URI` в `.env`.
4. Очистить старые живые данные в основной базе:

```bash
python scripts/purge_live_data.py
```

Если нужно удалить даже админов, можно использовать:

```bash
python scripts/purge_live_data.py --drop-admins
```

5. Перенести пользователей и бронирования из legacy-дампа:

```bash
python scripts/sync_live_data_from_legacy.py
```

Синхронизация работает так:
- пользователи маппятся по `phone`
- бронирования маппятся через `legacy room -> room.number -> new room`

## Бронирование

- `/rooms` - маркетинговая витрина 8 типов номеров
- `/book` - поиск доступных номеров по основной базе сайта
- если один номер не вмещает всех гостей, `/book` может предложить комбинацию из двух номеров
- комбинированное бронирование создаёт две стандартные записи `Booking` без изменения схемы БД

## Финальный handoff разработчику

После успешной синхронизации и проверки:

- удалить или отключить debug-роуты входа
- снять один финальный дамп новой базы
- передать разработчику код и этот финальный дамп

## Git

Этот каталог является отдельным git-репозиторием и пушится как `talassa-site`.
