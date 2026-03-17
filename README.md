# Talassa New

Финальная Flask-версия сайта **Talassa Hotel & Spa** со своей собственной базой данных, публичным сайтом, админкой, личным кабинетом и CMS-контентом страниц.

Для обычного развёртывания проект запускается из собственного финального дампа базы. Legacy sync-скрипты нужны только в отдельном сценарии, когда требуется дотянуть пользователей и бронирования из старой рабочей базы.

## Что внутри

- Flask + SQLAlchemy + Flask-Login
- Celery + Redis для фоновой отправки SMS и Telegram-уведомлений
- публичный сайт в `templates/public`
- админка в `templates/admin`
- личный кабинет гостя
- CMS-страницы и CMS-блоки в основной базе
- поиск и бронирование номеров по основной базе проекта
- шахматка бронирований в админке
- маркетинговая витрина `/rooms` и room-detail страницы на базе `data/next_rooms.json`
- статические ассеты и `static/uploads` уже включены в репозиторий

## Основные сущности базы

В рабочей базе проекта используются:

- `user`
- `booking`
- `room`
- `category`
- `room_photo`
- `news`
- `news_photo`
- `site_page`
- `site_block`

То есть финальный сайт запускается уже на собственной базе проекта, а не “поверх” старой структуры.

## Структура проекта

- `app.py` - основное Flask-приложение
- `services/rooms.py` - логика витрины номеров, цен, поиска и отображения room-type данных
- `templates/public` - публичные страницы сайта
- `templates/admin` - админка
- `static` - CSS, JS, изображения и загруженные файлы
- `data/next_rooms.json` - витрина 8 типов номеров
- `config.ini.example` - пример uWSGI-конфига
- `.env_example` - пример env-переменных
- `alembic` - миграции проекта

## Переменные окружения

Скопируйте `.env_example` в `.env` и заполните:

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
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`
- `NOTIFICATION_HTTP_TIMEOUT`

## Локальный запуск

### Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Celery worker

Для отправки SMS и Telegram-уведомлений в фоне должен работать отдельный worker:

```bash
celery -A app.celery worker -l info
```

Обычно для этого нужен локальный Redis:

```bash
sudo apt install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
redis-cli ping
```

Рекомендуемый запуск worker через `systemd`:

```ini
[Unit]
Description=Talassa Celery Worker
After=network.target redis-server.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/project
Environment="PATH=/path/to/project/.venv/bin"
ExecStart=/path/to/project/.venv/bin/python3 -m celery -A app.celery worker -l info
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

## uWSGI / deploy

В репозитории хранится только шаблон:

- `config.ini.example`

Перед запуском нужно создать рабочий `config.ini` на сервере на основе этого файла.

### Для запуска за Nginx

Используется локальный сокет/порт:

```ini
socket = 127.0.0.1:5000
```

Это нормальный и безопасный вариант, потому что Nginx проксирует запросы локально внутри сервера.

### Для прямого запуска без Nginx

Если сайт временно открывается напрямую по `IP:5000`, то вместо `socket` нужен:

```ini
http = 0.0.0.0:5000
```

## Бронирование

- `/rooms` - витрина 8 видов номеров
- `/book` - поиск доступных физических номеров по основной базе
- если один номер не вмещает всех гостей, `/book` может предложить комбинацию из двух номеров
- админ может менять физический номер в брони в пределах того же вида номера
- в админке есть шахматка занятости номеров

## CMS и контент

В проекте уже хранятся и работают:

- CMS-страницы
- CMS-блоки публичных страниц
- страница `/legal`
- журнал
- шаблонные room-type данные

## Развёртывание

Если у вас уже есть:

- код из репозитория
- финальный дамп базы
- `.env`
- рабочий `config.ini`

то разработчику достаточно:

1. развернуть код
2. импортировать финальный дамп
3. прописать `.env`
4. создать рабочий `config.ini` из `config.ini.example`
5. запустить приложение
6. запустить Redis
7. запустить Celery worker

Для обычного запуска migration/sync-скрипты не требуются. Они нужны только если отдельно выполняется перенос пользователей и бронирований из старой рабочей базы.

## Git

Этот каталог является отдельным git-репозиторием и пушится как `talassa-site`.
