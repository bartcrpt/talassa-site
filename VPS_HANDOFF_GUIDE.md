# Talassa Old: Инструкция для человека с доступом к VPS

Этот документ описывает, что нужно сделать на VPS, если вам передали:

- ссылку на GitHub-репозиторий проекта
- финальный дамп базы данных сайта

Сценарий ниже рассчитан на финальный перенос уже готового сайта. В этом случае дополнительные миграции из старой базы не нужны.

## Что будет передано

1. Ссылка на GitHub-репозиторий проекта
2. Финальный дамп базы данных:
   - либо `talassa_final.dump`
   - либо `talassa_final.sql`
3. Доступ к VPS

Важно:

- в репозитории уже лежат статические изображения сайта
- в репозитории уже лежит `static/uploads`
- отдельно докидывать `public`, `uploads` или какие-либо архивы с картинками не нужно

## Обозначения в этом документе

Ниже в командах используются универсальные плейсхолдеры:

- `/path/to/project` — путь к папке проекта на VPS
- `/path/to/dump/talassa_final.dump` — путь к финальному `.dump`
- `/path/to/dump/talassa_final.sql` — путь к финальному `.sql`
- `<REPO_URL>` — ссылка на GitHub-репозиторий

Перед выполнением команд просто подставьте свои реальные значения.

## Что не нужно делать

Для финального развёртывания не нужны никакие миграционные или одноразовые sync-скрипты. Репозиторий уже приведён к виду финального deploy-пакета.

## 1. Установить системные зависимости

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-dev build-essential libpq-dev postgresql postgresql-contrib
```

Если сайт будет открываться через Nginx, то дополнительно:

```bash
sudo apt install -y nginx
```

## 2. Клонировать репозиторий

Рекомендуемый путь:

```bash
git clone <REPO_URL> /path/to/project
cd /path/to/project
```

Важно:

- не рекомендуется размещать проект в `/root/...`, если сервис запускается от `www-data`
- безопаснее использовать обычный рабочий каталог, например `/opt/project`, `/srv/project` или любой другой путь вне `/root`

## 3. Создать виртуальное окружение и установить зависимости

```bash
cd /path/to/project
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

Важно:

- `.venv` нужно создавать именно в том каталоге, где реально лежит проект
- нельзя переносить старую `.venv` из другого пути

## 4. Создать PostgreSQL-базу

```bash
sudo -u postgres psql -c "CREATE ROLE talassa_user WITH LOGIN PASSWORD 'talassapassword';"
sudo -u postgres createdb -O talassa_user talassa
```

Если роль уже существует, первую команду можно пропустить.

## 5. Импортировать финальный дамп базы

### Если передан `.dump`

```bash
PGPASSWORD='talassapassword' pg_restore -h 127.0.0.1 -U talassa_user -d talassa /path/to/dump/talassa_final.dump
```

### Если передан `.sql`

```bash
PGPASSWORD='talassapassword' psql -h 127.0.0.1 -U talassa_user -d talassa -f /path/to/dump/talassa_final.sql
```

## 6. Настроить `.env`

Создать файл `.env` на основе примера:

```bash
cp /path/to/project/.env_example /path/to/project/.env
nano /path/to/project/.env
```

Минимально должны быть заполнены:

```env
SECRET_KEY='СЕКРЕТНЫЙ_КЛЮЧ'
UPLOAD_FOLDER='static/uploads'

TELEGRAM_TOKEN='...'
TELEGRAM_GROUP_ID='...'

DB_USER='talassa_user'
DB_PASSWORD='talassapassword'
DB_NAME='talassa'
DB_HOST='127.0.0.1'
DB_PORT='5432'

SMS_API_GATEWAY='http://...'
SMS_API_KEY='...'
```

Важно:

- дополнительные legacy-параметры для финального запуска не нужны

## 7. Исправить `config.ini` под нужный способ запуска

Текущий файл [`config.ini`](D:/DEV/talassa-claude_gpt_edit/talassa_old/config.ini) может потребовать ручной правки.

### Важное замечание

Если `uWSGI` установлен внутри `.venv` через `pip`, строку

```ini
plugins = python3
```

нужно убрать.

Иначе на некоторых серверах `uWSGI` будет пытаться найти внешний `python3_plugin.so` и не стартует.

### Если сайт будет открываться через Nginx

```ini
[uwsgi]
module = app:app
master = true
processes = 4
uid = www-data
gid = www-data
socket = 127.0.0.1:5000
vacuum = true
die-on-term = true
```

### Если сайт нужно временно открыть напрямую по `IP:5000` без Nginx

```ini
[uwsgi]
module = app:app
master = true
processes = 4
uid = www-data
gid = www-data
http = 0.0.0.0:5000
vacuum = true
die-on-term = true
```

Важно:

- `socket = 127.0.0.1:5000` виден только локально на сервере
- для открытия напрямую из браузера нужен `http = 0.0.0.0:5000`

## 8. Выдать права на каталог проекта

Если сервис запускается от `www-data`:

```bash
sudo chown -R www-data:www-data /path/to/project
```

## 9. Создать systemd-сервис

Создать файл:

```bash
sudo nano /etc/systemd/system/talassa.service
```

Содержимое:

```ini
[Unit]
Description=Talassa Flask App
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/project
Environment="PATH=/path/to/project/.venv/bin"
ExecStart=/path/to/project/.venv/bin/uwsgi --ini /path/to/project/config.ini
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Запуск:

```bash
sudo systemctl daemon-reload
sudo systemctl enable talassa
sudo systemctl restart talassa
sudo systemctl status talassa
```

## 10. Если используется Nginx

Создать конфиг:

```bash
sudo nano /etc/nginx/sites-available/talassa
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 50M;

    location /static/ {
        alias /path/to/project/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Активировать:

```bash
sudo ln -s /etc/nginx/sites-available/talassa /etc/nginx/sites-enabled/talassa
sudo nginx -t
sudo systemctl restart nginx
```

## 11. Быстрая проверка после запуска

### Проверка приложения

Если запуск без Nginx:

```bash
curl -I http://127.0.0.1:5000/
```

Если запуск через Nginx:

```bash
curl -I http://127.0.0.1/
```

### Проверка базы

```bash
PGPASSWORD='talassapassword' psql -h 127.0.0.1 -U talassa_user -d talassa -c "\dt"
PGPASSWORD='talassapassword' psql -h 127.0.0.1 -U talassa_user -d talassa -c "select count(*) from room;"
PGPASSWORD='talassapassword' psql -h 127.0.0.1 -U talassa_user -d talassa -c "select count(*) from booking;"
PGPASSWORD='talassapassword' psql -h 127.0.0.1 -U talassa_user -d talassa -c "select count(*) from \"user\";"
```

### Проверка вручную в браузере

Проверить страницы:

- `/`
- `/rooms`
- `/rooms/<slug>`
- `/journal`
- `/book`
- `/legal`
- `/my-bookings`
- `/admin`
- `/admin/bookings`
- `/admin/occupancy`

## 12. Что важно помнить

1. Для финального запуска нужен только:
   - репозиторий
   - финальный дамп базы
   - `.env`

2. Никакие одноразовые sync-скрипты для финального запуска не нужны.

3. Если сайт не открывается:
   - проверить `systemctl status talassa`
   - проверить `journalctl -u talassa -n 100 --no-pager`
   - проверить, не осталась ли в `config.ini` строка `plugins = python3`
   - проверить, что `.venv` создана в актуальном пути проекта
   - проверить, не лежит ли проект в `/root/...`, если сервис запускается от `www-data`

4. Если нужен запуск напрямую по `IP:5000`, надо использовать `http = 0.0.0.0:5000`, а не `socket = 127.0.0.1:5000`.

## Коротко

Финальный сценарий такой:

1. Клонировать репозиторий
2. Создать `.venv`
3. Установить зависимости
4. Создать PostgreSQL-базу
5. Импортировать финальный дамп
6. Заполнить `.env`
7. Исправить `config.ini` под способ запуска
8. Поднять `systemd`-сервис
9. Проверить сайт и админку
