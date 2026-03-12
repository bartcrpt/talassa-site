from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TALASSA_OLD_DIR = SCRIPT_DIR.parent

if str(TALASSA_OLD_DIR) not in sys.path:
    sys.path.insert(0, str(TALASSA_OLD_DIR))

from app import Booking, User, app, db  # noqa: E402


def purge_live_data(preserve_admins: bool = True) -> None:
    with app.app_context():
        bookings_count = Booking.query.count()
        deleted_bookings = Booking.query.delete(synchronize_session=False)

        users_query = User.query
        if preserve_admins:
            users_query = users_query.filter(User.is_admin.is_(False))

        deleted_users = users_query.delete(synchronize_session=False)
        db.session.commit()

        print(
            f'Purged live data: deleted_bookings={deleted_bookings}, '
            f'deleted_users={deleted_users}, previous_bookings_total={bookings_count}, '
            f'preserved_admins={preserve_admins}'
        )


if __name__ == '__main__':
    preserve_admins = '--drop-admins' not in sys.argv
    purge_live_data(preserve_admins=preserve_admins)
