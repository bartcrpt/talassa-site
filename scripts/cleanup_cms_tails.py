from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TALASSA_OLD_DIR = SCRIPT_DIR.parent

if str(TALASSA_OLD_DIR) not in sys.path:
    sys.path.insert(0, str(TALASSA_OLD_DIR))

from app import SiteBlock, SitePage, app, db  # noqa: E402


def cleanup_cms_tails() -> None:
    with app.app_context():
        deleted_blocks = 0
        deleted_pages = 0
        updated_blocks = 0

        about_page = SitePage.query.filter_by(slug='about').first()
        if about_page:
            deleted_blocks = SiteBlock.query.filter_by(page_id=about_page.id).delete(synchronize_session=False)
            db.session.delete(about_page)
            deleted_pages = 1

        for block in SiteBlock.query.all():
            changed = False

            if block.button_url == '/about':
                block.button_url = None
                block.button_label = None
                changed = True

            if block.block_key == 'philosophy':
                if (block.title or '').strip() == 'Философия Таласса':
                    block.title = 'О Таласса'
                    changed = True
                if (block.button_label or '').strip() in {'Узнать историю', 'О талассотерапии'}:
                    block.button_label = None
                    changed = True
                if (block.button_url or '').strip() in {'/about', '/wellness'}:
                    block.button_url = None
                    changed = True

            if changed:
                updated_blocks += 1

        db.session.commit()

        print(
            'CMS tails cleanup complete: '
            f'deleted_pages={deleted_pages}, '
            f'deleted_blocks={deleted_blocks}, '
            f'updated_blocks={updated_blocks}'
        )


if __name__ == '__main__':
    cleanup_cms_tails()
