from __future__ import annotations

import html
import json
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
TALASSA_OLD_DIR = SCRIPT_DIR.parent
SOURCE_DIR = SCRIPT_DIR / 'journal_source'
ARTICLES_PATH = SOURCE_DIR / 'articles.json'
IMAGES_DIR = SOURCE_DIR / 'images'

if str(TALASSA_OLD_DIR) not in sys.path:
    sys.path.insert(0, str(TALASSA_OLD_DIR))

from app import News, NewsPhoto, app, db  # noqa: E402


def extract_articles() -> list[dict]:
    if not ARTICLES_PATH.exists():
        raise FileNotFoundError(f'Journal source file not found: {ARTICLES_PATH}')

    with ARTICLES_PATH.open('r', encoding='utf-8') as source_file:
        articles = json.load(source_file)

    if not isinstance(articles, list):
        raise RuntimeError(f'Unexpected journal source structure in {ARTICLES_PATH}')

    return articles


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
    original_filename = Path(article['image']).name
    source_path = IMAGES_DIR / original_filename
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
            article = News.query.filter_by(title=source_article['title']).first()
            is_new = article is None

            if is_new:
                article = News(
                    title=source_article['title'],
                    author_id=None,
                    created_at=now - timedelta(minutes=index),
                )
                db.session.add(article)

            article.title = source_article['title']
            article.summary = source_article['excerpt']
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
