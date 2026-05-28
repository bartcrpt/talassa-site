import unittest

from services.booking_rules import should_reject_short_stay


class BookingRulesTest(unittest.TestCase):
    def test_public_short_stay_is_rejected(self):
        self.assertTrue(should_reject_short_stay(2, 3))

    def test_admin_edit_short_stay_is_allowed(self):
        self.assertFalse(should_reject_short_stay(2, 3, allow_short_stay=True))

    def test_minimum_stay_is_allowed_without_override(self):
        self.assertFalse(should_reject_short_stay(3, 3))


if __name__ == '__main__':
    unittest.main()
