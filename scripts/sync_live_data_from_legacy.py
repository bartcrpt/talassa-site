from __future__ import annotations

import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import RowMapping

SCRIPT_DIR = Path(__file__).resolve().parent
TALASSA_OLD_DIR = SCRIPT_DIR.parent

if str(TALASSA_OLD_DIR) not in sys.path:
    sys.path.insert(0, str(TALASSA_OLD_DIR))

from app import Booking, Room, User, app, db  # noqa: E402

LEGACY_SYNC_DATABASE_URI = os.getenv('LEGACY_SYNC_DATABASE_URI')


def fetch_all(connection, query: str) -> list[RowMapping]:
    return list(connection.execute(text(query)).mappings())


def coalesce_str(value):
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def sync_users(connection) -> tuple[int, int]:
    created = 0
    updated = 0
    source_users = fetch_all(
        connection,
        'SELECT id, phone, email, first_name, last_name, is_verified, is_admin, created_at FROM public."user" ORDER BY id ASC',
    )

    for source_user in source_users:
        phone = coalesce_str(source_user['phone'])
        if not phone:
            continue

        target_user = User.query.filter_by(phone=phone).first()
        is_new = target_user is None

        if is_new:
            target_user = User(phone=phone, first_name=source_user['first_name'] or 'Гость', last_name=source_user['last_name'] or 'Таласса')
            db.session.add(target_user)
            created += 1
        else:
            updated += 1

        target_user.phone = phone
        target_user.email = coalesce_str(source_user['email'])
        target_user.first_name = coalesce_str(source_user['first_name']) or target_user.first_name or 'Гость'
        target_user.last_name = coalesce_str(source_user['last_name']) or target_user.last_name or 'Таласса'
        target_user.is_verified = bool(source_user['is_verified'])
        target_user.is_admin = bool(target_user.is_admin) or bool(source_user['is_admin'])
        target_user.created_at = source_user['created_at'] or target_user.created_at

    db.session.flush()
    return created, updated


def build_legacy_maps(connection):
    legacy_rooms = fetch_all(connection, 'SELECT id, number FROM public.room ORDER BY id ASC')
    legacy_users = fetch_all(connection, 'SELECT id, phone FROM public."user" ORDER BY id ASC')
    room_number_by_legacy_id = {row['id']: coalesce_str(row['number']) for row in legacy_rooms}
    user_phone_by_legacy_id = {row['id']: coalesce_str(row['phone']) for row in legacy_users}
    return room_number_by_legacy_id, user_phone_by_legacy_id


def sync_bookings(connection) -> tuple[int, int, int]:
    created = 0
    skipped = 0
    missing_links = 0

    room_number_by_legacy_id, user_phone_by_legacy_id = build_legacy_maps(connection)
    target_rooms_by_number = {room.number: room for room in Room.query.all()}
    target_users_by_phone = {user.phone: user for user in User.query.all() if user.phone}

    source_bookings = fetch_all(
        connection,
        'SELECT id, user_id, room_id, check_in, check_out, guests, adults, children, children_under_five, total_price, status, special_requests, created_at FROM public.booking ORDER BY id ASC',
    )

    for source_booking in source_bookings:
        room_number = room_number_by_legacy_id.get(source_booking['room_id'])
        user_phone = user_phone_by_legacy_id.get(source_booking['user_id'])
        target_room = target_rooms_by_number.get(room_number)
        target_user = target_users_by_phone.get(user_phone)

        if not target_room or not target_user:
            missing_links += 1
            continue

        duplicate = Booking.query.filter_by(
            user_id=target_user.id,
            room_id=target_room.id,
            check_in=source_booking['check_in'],
            check_out=source_booking['check_out'],
            created_at=source_booking['created_at'],
        ).first()
        if duplicate:
            skipped += 1
            continue

        booking = Booking(
            user_id=target_user.id,
            room_id=target_room.id,
            check_in=source_booking['check_in'],
            check_out=source_booking['check_out'],
            guests=source_booking['guests'],
            adults=source_booking['adults'],
            children=source_booking['children'],
            children_under_five=source_booking['children_under_five'],
            total_price=source_booking['total_price'],
            status=source_booking['status'] or 'pending',
            special_requests=source_booking['special_requests'],
            created_at=source_booking['created_at'],
        )
        db.session.add(booking)
        created += 1

    db.session.flush()
    return created, skipped, missing_links


def main() -> None:
    if not LEGACY_SYNC_DATABASE_URI:
        raise RuntimeError('Set LEGACY_SYNC_DATABASE_URI to the temporary legacy database before running sync.')

    legacy_engine = create_engine(LEGACY_SYNC_DATABASE_URI)

    with app.app_context():
        with legacy_engine.connect() as connection:
            users_created, users_updated = sync_users(connection)
            bookings_created, bookings_skipped, bookings_missing_links = sync_bookings(connection)
            db.session.commit()

    print(
        'Live data sync complete: '
        f'users_created={users_created}, users_updated={users_updated}, '
        f'bookings_created={bookings_created}, bookings_skipped={bookings_skipped}, '
        f'bookings_missing_links={bookings_missing_links}'
    )


if __name__ == '__main__':
    main()
