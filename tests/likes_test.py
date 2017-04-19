import unittest
from unittest.mock import patch
from unittest.mock import MagicMock

from app import app
from app import models
from app import database
from app import likes


class LikesTestCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        database.create_all()

    def tearDown(self):
        database.session.remove()
        database.drop_all()

    def test_is_like_set_true(self):
        like = models.Liker_Talk(liker_facebook_id=1, talk_id=123)
        database.session.add(like)
        database.session.commit()
        self.assertTrue(likes.is_like_set(1, 123))

    def test_is_like_set_false_different_talk(self):
        like = models.Liker_Talk(liker_facebook_id=1, talk_id=123)
        database.session.add(like)
        database.session.commit()
        self.assertFalse(likes.is_like_set(1, 1234))

    def test_is_like_set_false_different_user(self):
        like = models.Liker_Talk(liker_facebook_id=1, talk_id=123)
        database.session.add(like)
        database.session.commit()
        self.assertFalse(likes.is_like_set(2, 123))

    def test_count_likes_nonexistent_talk(self):
        self.assertEqual(likes.count_likes(1), 0)

    def test_count_likes_no_likes(self):
        talk = models.Talk(title='1', speaker_facebook_id=1)
        database.session.add(talk)
        database.session.commit()
        self.assertEqual(likes.count_likes(1), 0)

    def test_count_likes_n_likes(self):
        n = 4
        for like_number in range(1, n + 1):
            like = models.Liker_Talk(liker_facebook_id=like_number, talk_id=123)
            database.session.add(like)
        database.session.commit()
        self.assertEqual(likes.count_likes(123), n)

    def test_set_like_valid(self):
        talk = models.Talk(title='1', speaker_facebook_id=1)
        database.session.add(talk)
        database.session.commit()
        likes.set_like(user_id=2, talk_id=1)
        returned_like = models.Liker_Talk.query.get((2, 1))
        self.assertEqual(returned_like.liker_facebook_id, 2)
        self.assertEqual(returned_like.talk_id, 1)

    def test_set_like_invalid_no_talk(self):
        with self.assertRaises(ValueError):
            likes.set_like(user_id=2, talk_id=1)

    def test_set_like_invalid_duplicate_like(self):
        talk = models.Talk(title='1', speaker_facebook_id=1)
        database.session.add(talk)
        database.session.commit()
        likes.set_like(user_id=2, talk_id=1)
        with self.assertRaises(ValueError):
            likes.set_like(user_id=2, talk_id=1)

    def test_unset_like_valid(self):
        talk = models.Talk(id=1, title='1', speaker_facebook_id=1)
        like = models.Liker_Talk(liker_facebook_id=2, talk=talk)
        database.session.add(talk)
        database.session.add(like)
        database.session.commit()
        likes.unset_like(user_id=2, talk_id=1)
        returned_like = models.Liker_Talk.query.get((2, 1))
        self.assertIsNone(returned_like)

    def test_unset_like_invalid_no_talk(self):
        with self.assertRaises(ValueError):
            likes.unset_like(user_id=2, talk_id=1)

    def test_unset_like_invalid_no_like(self):
        talk = models.Talk(title='1', speaker_facebook_id=1)
        database.session.add(talk)
        database.session.commit()
        with self.assertRaises(ValueError):
            likes.unset_like(user_id=2, talk_id=1)
