from django.test import TestCase
from data_import.reddit_interface import _clean_sub_name


class TestRedditInterface(TestCase):
    def test_clean_sub_name(self):
        self.assertEqual(_clean_sub_name("/r/testsub"), "testsub")
