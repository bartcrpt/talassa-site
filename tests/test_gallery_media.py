import unittest

from services.gallery_media import gallery_media_type, gallery_sort_key


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


if __name__ == '__main__':
    unittest.main()
