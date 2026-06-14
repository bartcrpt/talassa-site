from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class RoomDetailMarkupTest(unittest.TestCase):
    def test_meals_render_as_room_fact_without_duplicate_label(self):
        template = (ROOT / 'templates/public/room_detail.html').read_text(encoding='utf-8')

        self.assertIn('room-detail-next__fact room-detail-next__fact--meals', template)
        self.assertIn("meals_text|replace('Питание:', '')|trim", template)
        self.assertNotIn('room-detail-next__meals', template)


if __name__ == '__main__':
    unittest.main()
