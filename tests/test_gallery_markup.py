from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class GalleryMarkupTest(unittest.TestCase):
    def test_lightbox_media_have_initial_hidden_state_and_css_guard(self):
        template = (ROOT / 'templates/public/base_public.html').read_text(encoding='utf-8')
        css = (ROOT / 'static/css/site.css').read_text(encoding='utf-8')

        self.assertIn('data-site-lightbox-image hidden', template)
        self.assertIn('data-site-lightbox-video controls playsinline preload="metadata" hidden', template)
        self.assertIn('.site-lightbox__media[hidden]', css)
        self.assertIn('display: none !important;', css)

    def test_gallery_video_preview_has_explicit_play_button(self):
        template = (ROOT / 'templates/public/gallery.html').read_text(encoding='utf-8')
        css = (ROOT / 'static/css/site.css').read_text(encoding='utf-8')

        self.assertIn('gallery-masonry__play', template)
        self.assertIn('.gallery-masonry__play', css)


if __name__ == '__main__':
    unittest.main()
