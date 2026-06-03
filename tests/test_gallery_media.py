import unittest
from pathlib import Path
import struct

from services.gallery_media import gallery_media_type, gallery_sort_key


ROOT = Path(__file__).resolve().parents[1]


def top_level_mp4_boxes(path):
    boxes = []
    file_size = path.stat().st_size
    with path.open('rb') as file:
        offset = 0
        while offset < file_size:
            header = file.read(8)
            if len(header) < 8:
                break
            size, box_type = struct.unpack('>I4s', header)
            box_type = box_type.decode('ascii', errors='replace')
            if size == 1:
                size = struct.unpack('>Q', file.read(8))[0]
            elif size == 0:
                size = file_size - offset
            boxes.append(box_type)
            file.seek(offset + size)
            offset += size
    return boxes


class GalleryMediaTest(unittest.TestCase):
    def test_detects_supported_media_types(self):
        self.assertEqual(gallery_media_type('photo_1.jpg'), 'image')
        self.assertEqual(gallery_media_type('photo_2.jpeg'), 'image')
        self.assertEqual(gallery_media_type('photo_3.png'), 'image')
        self.assertEqual(gallery_media_type('photo_4.webp'), 'image')
        self.assertEqual(gallery_media_type('photo_13.mp4'), 'video')
        self.assertIsNone(gallery_media_type('photo_14.txt'))

    def test_sorts_media_by_embedded_number(self):
        filenames = ['photo_13.mp4', 'photo_1.jpg', 'photo_12.jpg', 'photo_0.jpg']

        self.assertEqual(
            sorted(filenames, key=gallery_sort_key),
            ['photo_0.jpg', 'photo_1.jpg', 'photo_12.jpg', 'photo_13.mp4'],
        )

    def test_gallery_videos_are_faststart_mp4s(self):
        gallery_dir = ROOT / 'static/site/images/gallery'
        mp4_files = sorted(gallery_dir.glob('*.mp4'))

        self.assertGreater(len(mp4_files), 0)
        for path in mp4_files:
            with self.subTest(filename=path.name):
                boxes = top_level_mp4_boxes(path)
                self.assertIn('moov', boxes)
                self.assertIn('mdat', boxes)
                self.assertLess(boxes.index('moov'), boxes.index('mdat'))


if __name__ == '__main__':
    unittest.main()
