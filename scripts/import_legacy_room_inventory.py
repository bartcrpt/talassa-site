from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import RowMapping

SCRIPT_DIR = Path(__file__).resolve().parent
TALASSA_OLD_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = TALASSA_OLD_DIR.parent
NEXT_PUBLIC_DIR = PROJECT_ROOT / 'public'
NEXT_ROOMS_DATA_PATH = TALASSA_OLD_DIR / 'data' / 'next_rooms.json'

if str(TALASSA_OLD_DIR) not in sys.path:
    sys.path.insert(0, str(TALASSA_OLD_DIR))

from app import Booking, Category, Room, RoomPhoto, app, db, ensure_runtime_schema  # noqa: E402

LEGACY_SYNC_DATABASE_URI = os.getenv('LEGACY_SYNC_DATABASE_URI')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')

MONTH_MAP = {
    'Январь': 'January',
    'Февраль': 'February',
    'Март': 'March',
    'Апрель': 'April',
    'Май': 'May',
    'Июнь': 'June',
    'Июль': 'July',
    'Август': 'August',
    'Сентябрь': 'September',
    'Октябрь': 'October',
    'Ноябрь': 'November',
    'Декабрь': 'December',
}

LEGACY_CATEGORY_SLUG_MAP = {
    1: 'standart-plus-sea-view',
    2: 'deluxe-terrace-sea-view',
    3: 'apartment-balcony-sea-view',
    4: 'standart-sea-view-no-balcony',
    5: 'standart-first-floor',
    6: 'deluxe-big-terrace-sea-view',
    7: 'standart-balcony-sea-view',
    8: 'apartment-accessible',
}

CATEGORY_NAME_TO_SLUG = {
    'стандарт плюс с видом на море': 'standart-plus-sea-view',
    'стандарт без балкона с видом на море и горы.': 'standart-sea-view-no-balcony',
    'стандарт с балконом и видом на море': 'standart-balcony-sea-view',
    'стандарт без балкона (первый этаж)': 'standart-first-floor',
    'deluxe плюс с террасой и видом на море.': 'deluxe-terrace-sea-view',
    'deluxe с большой террасой и видом на море.': 'deluxe-big-terrace-sea-view',
    'двухместные апартаменты с балконом и видом на море': 'apartment-balcony-sea-view',
    'двухместные апартаменты ( мгн)': 'apartment-accessible',
    'двухместные апартаменты (  мгн)': 'apartment-accessible',
}


def fetch_all(connection, query: str) -> list[RowMapping]:
    return list(connection.execute(text(query)).mappings())


def normalize_text(value: str | None) -> str:
    if not value:
        return ''
    return ' '.join(str(value).strip().lower().split())


def load_next_rooms() -> dict[str, dict]:
    with NEXT_ROOMS_DATA_PATH.open('r', encoding='utf-8') as source_file:
        rooms = json.load(source_file)
    return {room['slug']: room for room in rooms}


def build_prices(next_room: dict) -> dict[str, float]:
    return {MONTH_MAP[item['month']]: float(item['price']) for item in next_room.get('prices', [])}


def upload_dir_path() -> Path:
    upload_dir = Path(UPLOAD_FOLDER)
    if not upload_dir.is_absolute():
        upload_dir = TALASSA_OLD_DIR / upload_dir
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def build_template_photo_sources(next_rooms_by_slug: dict[str, dict]) -> dict[str, list[dict]]:
    template_sources: dict[str, list[dict]] = {}

    existing_template_numbers = {
        'standart-plus-sea-view': 'NX01',
        'standart-sea-view-no-balcony': 'NX02',
        'standart-balcony-sea-view': 'NX03',
        'standart-first-floor': 'NX04',
        'deluxe-terrace-sea-view': 'NX05',
        'deluxe-big-terrace-sea-view': 'NX06',
        'apartment-balcony-sea-view': 'NX07',
        'apartment-accessible': 'NX08',
    }

    for slug, template_number in existing_template_numbers.items():
        template_room = Room.query.filter_by(number=template_number).first()
        if template_room and template_room.photos:
            template_sources[slug] = [
                {
                    'mode': 'existing',
                    'filename': photo.filename,
                    'original_filename': photo.original_filename,
                    'is_main': bool(photo.is_main),
                }
                for photo in template_room.photos
            ]
            continue

        next_room = next_rooms_by_slug.get(slug)
        if not next_room:
            continue

        image_sources = []
        for index, image_path in enumerate(next_room.get('images', [])):
            rel_path = image_path.replace('/next-assets/', '', 1).lstrip('/')
            source_path = NEXT_PUBLIC_DIR / rel_path
            if not source_path.exists():
                continue
            image_sources.append(
                {
                    'mode': 'copy',
                    'source_path': source_path,
                    'original_filename': source_path.name,
                    'index': index,
                }
            )
        if image_sources:
            template_sources[slug] = image_sources

    return template_sources


def ensure_categories() -> dict[str, Category]:
    categories: dict[str, Category] = {}
    desired = ['Стандарт', 'Deluxe', 'Апартаменты']
    existing = {category.name: category for category in Category.query.all()}
    for name in desired:
        category = existing.get(name)
        if not category:
            category = Category(name=name, description=name)
            db.session.add(category)
            db.session.flush()
        categories[name] = category
    return categories


def resolve_slug(source_room: RowMapping, legacy_category_name_by_id: dict[int, str]) -> str | None:
    slug = LEGACY_CATEGORY_SLUG_MAP.get(source_room['category_id'])
    if slug:
        return slug
    normalized_name = normalize_text(legacy_category_name_by_id.get(source_room['category_id']))
    return CATEGORY_NAME_TO_SLUG.get(normalized_name)


def reset_inventory(purge_bookings: bool) -> None:
    bookings_count = Booking.query.count()
    if bookings_count and not purge_bookings:
        raise RuntimeError(
            f'Current database still has {bookings_count} bookings. Rerun with --purge-bookings to rebuild inventory and delete them.'
        )

    if purge_bookings:
        Booking.query.delete(synchronize_session=False)

    RoomPhoto.query.delete(synchronize_session=False)
    Room.query.delete(synchronize_session=False)
    Category.query.delete(synchronize_session=False)
    db.session.flush()


def attach_photos(room: Room, slug: str, template_sources: dict[str, list[dict]], upload_dir: Path) -> int:
    attached = 0
    sources = template_sources.get(slug, [])
    for index, source in enumerate(sources):
        if source['mode'] == 'existing':
            db.session.add(
                RoomPhoto(
                    room_id=room.id,
                    filename=source['filename'],
                    original_filename=source['original_filename'],
                    is_main=bool(source['is_main']) if index == 0 else False,
                )
            )
            attached += 1
            continue

        source_path: Path = source['source_path']
        target_filename = f'legacy_{room.number}_{index + 1:02d}_{source_path.name}'
        target_path = upload_dir / target_filename
        if not target_path.exists():
            shutil.copy2(source_path, target_path)

        db.session.add(
            RoomPhoto(
                room_id=room.id,
                filename=target_filename,
                original_filename=source['original_filename'],
                is_main=(index == 0),
            )
        )
        attached += 1
    return attached


def import_inventory(purge_bookings: bool = False) -> None:
    if not LEGACY_SYNC_DATABASE_URI:
        raise RuntimeError('Set LEGACY_SYNC_DATABASE_URI before importing legacy room inventory.')

    next_rooms_by_slug = load_next_rooms()
    legacy_engine = create_engine(LEGACY_SYNC_DATABASE_URI)

    with app.app_context():
        ensure_runtime_schema()
        template_sources = build_template_photo_sources(next_rooms_by_slug)
        upload_dir = upload_dir_path()
        reset_inventory(purge_bookings=purge_bookings)
        categories = ensure_categories()

        imported = 0
        skipped = 0
        attached_photos = 0

        with legacy_engine.connect() as connection:
            legacy_categories = fetch_all(connection, 'SELECT id, name FROM public.category ORDER BY id ASC')
            legacy_category_name_by_id = {row['id']: row['name'] for row in legacy_categories}
            legacy_rooms = fetch_all(connection, 'SELECT id, number, category_id, is_available, created_at FROM public.room ORDER BY number ASC, id ASC')

            for source_room in legacy_rooms:
                slug = resolve_slug(source_room, legacy_category_name_by_id)
                next_room = next_rooms_by_slug.get(slug) if slug else None
                if not next_room:
                    skipped += 1
                    continue

                room = Room(
                    number=str(source_room['number']).strip(),
                    category_id=categories[next_room['category']].id,
                    room_type_slug=slug,
                    price_per_night=build_prices(next_room),
                    capacity=int(next_room['capacity']['standard']),
                    has_small_sofa=bool(next_room.get('extraGuestsMax') == 1),
                    has_large_sofa=bool((next_room.get('extraGuestsMax') or 0) >= 2),
                    description=next_room.get('description'),
                    amenities=json.dumps(next_room.get('amenities', []), ensure_ascii=False),
                    is_available=True if source_room['is_available'] is None else bool(source_room['is_available']),
                    created_at=source_room['created_at'],
                )
                db.session.add(room)
                db.session.flush()

                attached_photos += attach_photos(room, slug, template_sources, upload_dir)
                imported += 1

        db.session.commit()
        print(
            f'Legacy room inventory imported: rooms={imported}, skipped={skipped}, attached_photos={attached_photos}, purge_bookings={purge_bookings}'
        )


if __name__ == '__main__':
    purge_bookings = '--purge-bookings' in sys.argv
    import_inventory(purge_bookings=purge_bookings)


