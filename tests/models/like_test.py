import os
import unittest

import sqlalchemy

from app import app
from app import models
from app import database


class LikeTestCase(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        database.create_all()

    def tearDown(self):
        database.session.remove()
        database.drop_all()

    def test_valid_like(self):
        like = models.Liker_Talk(liker_facebook_id=1, talk_id=123)
        database.session.add(like)
        database.session.commit()

        returned_like = models.Liker_Talk.query.get((1, 123))
        self.assertEqual(returned_like.liker_facebook_id, like.liker_facebook_id)
        self.assertEqual(returned_like.talk_id, like.talk_id)

    def test_valid_like_duplicate_facebook_id(self):
        like1 = models.Liker_Talk(liker_facebook_id=1, talk_id=123)
        like2 = models.Liker_Talk(liker_facebook_id=1, talk_id=1234)
        database.session.add(like1)
        database.session.add(like2)
        database.session.commit()

        returned_like1 = models.Liker_Talk.query.get((1, 123))
        self.assertEqual(returned_like1.liker_facebook_id, like1.liker_facebook_id)
        self.assertEqual(returned_like1.talk_id, like1.talk_id)
        returned_like2 = models.Liker_Talk.query.get((1, 1234))
        self.assertEqual(returned_like2.liker_facebook_id, like2.liker_facebook_id)
        self.assertEqual(returned_like2.talk_id, like2.talk_id)

    def test_valid_like_duplicate_talk_id(self):
        like1 = models.Liker_Talk(liker_facebook_id=1, talk_id=123)
        like2 = models.Liker_Talk(liker_facebook_id=2, talk_id=123)
        database.session.add(like1)
        database.session.add(like2)
        database.session.commit()

        returned_like1 = models.Liker_Talk.query.get((1, 123))
        self.assertEqual(returned_like1.liker_facebook_id, like1.liker_facebook_id)
        self.assertEqual(returned_like1.talk_id, like1.talk_id)
        returned_like2 = models.Liker_Talk.query.get((2, 123))
        self.assertEqual(returned_like2.liker_facebook_id, like2.liker_facebook_id)
        self.assertEqual(returned_like2.talk_id, like2.talk_id)

    def test_invalid_like_without_facebook_id(self):
        like = models.Liker_Talk(talk_id=123)
        database.session.add(like)
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            database.session.commit()

    def test_invalid_like_without_talk_id(self):
        like = models.Liker_Talk(liker_facebook_id=1)
        database.session.add(like)
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            database.session.commit()

    def test_invalid_like_duplicate_primary_key(self):
        like1 = models.Liker_Talk(liker_facebook_id=1, talk_id=123)
        like2 = models.Liker_Talk(liker_facebook_id=1, talk_id=123)
        database.session.add(like1)
        database.session.add(like2)
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            database.session.commit()


if __name__ == '__main__':
    unittest.main()
