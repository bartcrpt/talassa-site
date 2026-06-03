import os
import re


IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
VIDEO_EXTENSIONS = {'.mp4'}


def gallery_media_type(filename):
    suffix = os.path.splitext(filename)[1].lower()
    if suffix in IMAGE_EXTENSIONS:
        return 'image'
    if suffix in VIDEO_EXTENSIONS:
        return 'video'
    return None


def gallery_sort_key(filename):
    match = re.search(r'(\d+)', filename)
    return (int(match.group(1)) if match else 9999, filename)
