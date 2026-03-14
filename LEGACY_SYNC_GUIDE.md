# Legacy Sync Guide

Пошаговый гайд для сценария:

- есть свежий `.sql`-дамп старой базы
- основная новая база сайта: `talassa`
- нужно:
  - подтянуть из старой базы актуальную нумерацию и количество номеров
  - сохранить наши 3 категории, наши виды номеров, фото и CMS
  - перенести пользователей и бронирования
  - проверить результат
  - снять финальный дамп новой базы

## Исходные допущения

- свежий SQL-дамп лежит тут:
  - `/home/bart/talassa/talassa_old/legacy_fresh.sql`
- временная база со свежим дампом:
  - `talassa_legacy_fresh`
- рабочая новая база сайта:
  - `talassa`
- пользователь новой базы:
  - `talassa_user`
- пользователь legacy-базы:
  - `talassahoteldbuser`

## 1. Обновить код

```bash
cd /home/bart/talassa/talassa_old
git pull
```

## 2. Сделать бэкап текущей базы `talassa`

```bash
mkdir -p /home/bart/talassa/talassa_old/backups

PGPASSWORD='talassapassword' pg_dump -h 127.0.0.1 -U talassa_user -d talassa -Fc -f /home/bart/talassa/talassa_old/backups/talassa_before_final_sync.dump
```

## 3. Подготовить `.sql` к восстановлению

Если дамп содержит `DROP DATABASE`, `CREATE DATABASE`, `ALTER DATABASE` или `\connect`, очищаем его:

```bash
sed \
  -e '/^DROP DATABASE /d' \
  -e '/^CREATE DATABASE /d' \
  -e '/^ALTER DATABASE /d' \
  -e '/^\\connect /d' \
  /home/bart/talassa/talassa_old/legacy_fresh.sql \
  > /home/bart/talassa/talassa_old/legacy_fresh_restore.sql
```

## 4. Поднять свежую legacy-базу

```bash
sudo -u postgres dropdb --if-exists talassa_legacy_fresh
sudo -u postgres createdb -O talassahoteldbuser talassa_legacy_fresh
```

## 5. Восстановить `.sql` в `talassa_legacy_fresh`

```bash
PGPASSWORD='ТВОЙ_ПАРОЛЬ_ОТ_talassahoteldbuser' psql -h 127.0.0.1 -U talassahoteldbuser -d talassa_legacy_fresh -f /home/bart/talassa/talassa_old/legacy_fresh_restore.sql
```

## 6. Проверить, что legacy-база поднялась

```bash
PGPASSWORD='ТВОЙ_ПАРОЛЬ_ОТ_talassahoteldbuser' psql -h 127.0.0.1 -U talassahoteldbuser -d talassa_legacy_fresh -c "\\dt"
PGPASSWORD='ТВОЙ_ПАРОЛЬ_ОТ_talassahoteldbuser' psql -h 127.0.0.1 -U talassahoteldbuser -d talassa_legacy_fresh -c "select count(*) from room;"
PGPASSWORD='ТВОЙ_ПАРОЛЬ_ОТ_talassahoteldbuser' psql -h 127.0.0.1 -U talassahoteldbuser -d talassa_legacy_fresh -c "select count(*) from booking;"
PGPASSWORD='ТВОЙ_ПАРОЛЬ_ОТ_talassahoteldbuser' psql -h 127.0.0.1 -U talassahoteldbuser -d talassa_legacy_fresh -c "select count(*) from \"user\";"
```

## 7. Прописать `.env`

В `/home/bart/talassa/talassa_old/.env`:

```env
DB_USER=talassa_user
DB_PASSWORD=talassapassword
DB_NAME=talassa
DB_HOST=127.0.0.1
DB_PORT=5432

LEGACY_SYNC_DATABASE_URI=postgresql://talassahoteldbuser:ТВОЙ_ПАРОЛЬ_ОТ_talassahoteldbuser@127.0.0.1:5432/talassa_legacy_fresh
```

## 8. Почистить CMS-хвосты

```bash
cd /home/bart/talassa/talassa_old
python3 scripts/cleanup_cms_tails.py
```

Что это делает:

- удаляет `about` из CMS
- удаляет связанные `site_block`
- убирает старые ссылки `/about`
- чистит старую кнопку в блоке `О Таласса`

## 9. Обновить inventory номеров из legacy

```bash
cd /home/bart/talassa/talassa_old
python3 scripts/import_legacy_room_inventory.py --purge-bookings
```

Что делает шаг:

- берёт из `talassa_legacy_fresh` количество физических номеров и их нумерацию
- оставляет в `talassa` наши 3 категории
- оставляет наши виды номеров, фото, тексты и цены

## 10. Очистить пользователей и брони в `talassa`

```bash
cd /home/bart/talassa/talassa_old
python3 scripts/purge_live_data.py
```

По умолчанию скрипт:

- удаляет все брони
- удаляет всех пользователей, кроме админов

## 11. Перенести пользователей и бронирования из legacy

```bash
cd /home/bart/talassa/talassa_old
python3 scripts/sync_live_data_from_legacy.py
```

Скрипт переносит:

- `user` по `phone`
- `booking` через:
  - legacy `room_id` -> legacy `room.number`
  - legacy `user_id` -> legacy `user.phone`
  - дальше поиск соответствующих `room` и `user` уже в нашей базе `talassa`

## 12. Проверить результат SQL-запросами

### Сколько пользователей

```bash
PGPASSWORD='talassapassword' psql -h 127.0.0.1 -U talassa_user -d talassa -c "select count(*) from \"user\";"
```

### Сколько броней

```bash
PGPASSWORD='talassapassword' psql -h 127.0.0.1 -U talassa_user -d talassa -c "select count(*) from booking;"
```

### Проверить номера, виды и категории

```bash
PGPASSWORD='talassapassword' psql -h 127.0.0.1 -U talassa_user -d talassa -c "select r.number, r.room_type_slug, c.name from room r join category c on c.id = r.category_id order by r.number asc;"
```

### Проверить связи броней

```bash
PGPASSWORD='talassapassword' psql -h 127.0.0.1 -U talassa_user -d talassa -c "select b.id, r.number, r.room_type_slug, u.phone, b.check_in, b.check_out, b.status from booking b join room r on r.id = b.room_id join \"user\" u on u.id = b.user_id order by b.id desc limit 30;"
```

### Проверить, нет ли битых связей

```bash
PGPASSWORD='talassapassword' psql -h 127.0.0.1 -U talassa_user -d talassa -c "select count(*) from booking b left join room r on r.id = b.room_id left join \"user\" u on u.id = b.user_id where r.id is null or u.id is null;"
```

Ожидаемый результат последнего запроса:

```sql
0
```

## 13. Перезапустить сайт

```bash
sudo systemctl restart talassa
```

## 14. Проверить сайт руками

Проверить:

- `/`
- `/rooms`
- `/book`
- обычное бронирование
- комбинированное бронирование
- `/my-bookings`
- `/admin`
- `/admin/bookings`
- `/admin/rooms`

Особенно важно:

- номера на `/book` без дублей по виду
- комбинации без дублей по парам видов
- у броней правильные номера и правильные пользователи
- в админке всё открывается корректно

## 15. Если всё ок — снять финальный дамп

```bash
PGPASSWORD='talassapassword' pg_dump -h 127.0.0.1 -U talassa_user -d talassa -Fc -f /home/bart/talassa/talassa_old/backups/talassa_final.dump
```

## 16. Что отдавать разработчику в финале

- код проекта
- финальный дамп:
  - `/home/bart/talassa/talassa_old/backups/talassa_final.dump`

После финальной проверки ещё желательно:

- убрать debug routes
- сделать финальный коммит

## Короткий порядок

```bash
git pull
backup talassa
restore fresh legacy sql -> talassa_legacy_fresh
update .env with LEGACY_SYNC_DATABASE_URI
python3 scripts/cleanup_cms_tails.py
python3 scripts/import_legacy_room_inventory.py --purge-bookings
python3 scripts/purge_live_data.py
python3 scripts/sync_live_data_from_legacy.py
sql checks
restart app
manual checks
pg_dump talassa -> talassa_final.dump
```
