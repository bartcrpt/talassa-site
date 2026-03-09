from __future__ import annotations

import ast
import html
import re
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
TALASSA_OLD_DIR = SCRIPT_DIR.parent
REPO_ROOT = TALASSA_OLD_DIR.parent
NEXT_JOURNAL_PATH = REPO_ROOT / 'src' / 'data' / 'journal.ts'

if str(TALASSA_OLD_DIR) not in sys.path:
    sys.path.insert(0, str(TALASSA_OLD_DIR))

from app import News, NewsPhoto, app, db  # noqa: E402


JOURNAL_KEYS = [
    'slug',
    'title',
    'excerpt',
    'category',
    'image',
    'intro',
    'sections',
    'heading',
    'text',
    'items',
]


def extract_articles() -> list[dict]:
    source = NEXT_JOURNAL_PATH.read_text(encoding='utf-8')
    match = re.search(
        r'export const journalArticles: JournalArticle\[\] = \[(.*)\];\s*export const journalSlugs',
        source,
        re.S,
    )
    if not match:
        raise RuntimeError(f'Could not parse journal articles from {NEXT_JOURNAL_PATH}')

    payload = '[' + match.group(1) + ']'
    for key in JOURNAL_KEYS:
        payload = re.sub(rf'(?<!["\'])\b{key}\b(?=\s*:)', f'"{key}"', payload)

    payload = re.sub(r',(\s*[}\]])', r'\1', payload)
    return ast.literal_eval(payload)


def render_article_html(article: dict) -> str:
    blocks: list[str] = [f'<p>{html.escape(article["intro"])}</p>']
    for section in article['sections']:
        blocks.append(f'<h2>{html.escape(section["heading"])}</h2>')
        if section.get('text'):
            blocks.append(f'<p>{html.escape(section["text"])}</p>')
        if section.get('items'):
            items = ''.join(f'<li>{html.escape(item)}</li>' for item in section['items'])
            blocks.append(f'<ul>{items}</ul>')
    return '\n'.join(blocks)


def copy_cover_image(article: dict) -> str:
    relative_image_path = Path(article['image'].lstrip('/'))
    source_path = REPO_ROOT / 'public' / relative_image_path
    if not source_path.exists():
        raise FileNotFoundError(f'Cover image not found: {source_path}')

    filename = f'journal-{article["slug"]}{source_path.suffix.lower()}'
    destination_path = TALASSA_OLD_DIR / 'static' / 'uploads' / filename
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, destination_path)
    return filename


def upsert_articles() -> None:
    imported_count = 0
    updated_count = 0
    now = datetime.utcnow()
    articles = extract_articles()

    with app.app_context():
        for index, source_article in enumerate(articles):
            article = News.query.filter_by(source_slug=source_article['slug']).first()
            if article is None:
                article = News.query.filter_by(title=source_article['title']).first()
            is_new = article is None

            if is_new:
                article = News(
                    title=source_article['title'],
                    source_slug=source_article['slug'],
                    category=source_article.get('category'),
                    author_id=None,
                    created_at=now - timedelta(minutes=index),
                )
                db.session.add(article)

            article.title = source_article['title']
            article.summary = source_article['excerpt']
            article.source_slug = source_article['slug']
            article.category = source_article.get('category')
            article.content = render_article_html(source_article)
            article.is_published = True
            article.updated_at = now

            db.session.flush()

            filename = copy_cover_image(source_article)
            photo = next((item for item in article.photos if item.filename == filename), None)
            if photo is None:
                db.session.add(
                    NewsPhoto(
                        news_id=article.id,
                        filename=filename,
                        original_filename=Path(source_article['image']).name,
                    )
                )

            if is_new:
                imported_count += 1
            else:
                updated_count += 1

        db.session.commit()

    print(f'Imported: {imported_count}, updated: {updated_count}, total processed: {len(articles)}')


if __name__ == '__main__':
    upsert_articles()

