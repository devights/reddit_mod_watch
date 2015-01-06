from django.test import TestCase
from django.db import IntegrityError
from data_import.models import Subreddit, User


class TestSubredditModel(TestCase):
    def test_creation(self):
        sub = Subreddit(name="mysub")
        sub.save()
        self.assertEqual(sub.name, "mysub")
        self.assertIsNone(sub.last_updated)
        self.assertIsNotNone(sub.added_on)

    def test_update(self):
        sub = Subreddit(name="mysub")
        sub.save()
        self.assertIsNone(sub.last_updated)
        sub.mark_updated()
        self.assertIsNotNone(sub.last_updated)
        self.assertNotEqual(sub.last_updated, sub.added_on)

    def test_dupe(self):
        s1 = Subreddit(name="dupe")
        s1.save()
        with self.assertRaises(IntegrityError):
            s2 = Subreddit(name="dupe")
            s2.save()


class TestUserModel(TestCase):
    def test_creation(self):
        user = User(username="johnny")
        user.save()
        self.assertEqual(user.username, "johnny")
        self.assertIsNone(user.is_private)
        self.assertIsNotNone(user.added_on)
        self.assertIsNone(user.last_updated)

        user2 = User(username="asdf", is_private=True)
        user2.save()
        self.assertTrue(user2.is_private)

    def test_dupe(self):
        u1 = User(username="dupe")
        u1.save()
        with self.assertRaises(IntegrityError):
            u2 = User(username="dupe")
            u2.save()