# Talassa New

Flask-приложение для сайта `talassa-site`, работающее поверх одной основной базы новой версии сайта.

## Что внутри

- Flask + SQLAlchemy + Flask-Login
- Публичный сайт в `templates/public`
- Админка и личный кабинет в `templates/admin`, `templates/profile.html`, `templates/my_bookings.html`
- Основная база сайта для `user`, `booking`, `room`, `category`, `room_photo`, `news`, `news_photo`, `site_page`, `site_block`
- Поиск на `/book` работает по основной базе сайта
- Витрина `/rooms` и публичные room-detail страницы используют адаптерный слой и данные из `data/next_rooms.json`
- Репозиторий уже включает статические ассеты сайта и `static/uploads`

## Структура

- `app.py` - основное Flask-приложение
- `services/rooms.py` - адаптер и общая логика room-каталога, поиска и цен
- `templates/public` - публичные страницы
- `static` - стили, скрипты, ассеты
- `alembic` - миграции проекта
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
- `DB_PORT`
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

## Бронирование

- `/rooms` - маркетинговая витрина 8 типов номеров
- `/book` - поиск доступных номеров по основной базе сайта
- если один номер не вмещает всех гостей, `/book` может предложить комбинацию из двух номеров
- комбинированное бронирование создаёт две стандартные записи `Booking` без изменения схемы БД

## Финальный handoff разработчику

После проверки сайта:

- удалить или отключить debug-роуты входа
- снять один финальный дамп новой базы
- передать разработчику код и этот финальный дамп

## Git

Этот каталог является отдельным git-репозиторием и пушится как `talassa-site`.
