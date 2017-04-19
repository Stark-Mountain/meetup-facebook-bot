import os
import tempfile
import unittest

import sqlalchemy

from app import app
from app import models
from app import database


class TalkTestCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        database.create_all()

    def tearDown(self):
        database.session.remove()
        database.drop_all()

    def test_valid_talk_without_description_and_likes(self):
        talk = models.Talk(title='How to grow the grapes', speaker_facebook_id=1)
        database.session.add(talk)
        database.session.commit()

        returned_talk = models.Talk.query.get(1)
        self.assertEqual(returned_talk.title, talk.title)
        self.assertEqual(returned_talk.speaker_facebook_id, talk.speaker_facebook_id)
        self.assertIsNone(returned_talk.description)
        self.assertEqual(len(returned_talk.likes.all()), 0)

    def test_valid_talk_with_description(self):
        talk = models.Talk(title='How to grow the grapes',
                           description='Once you master the world\'s six most important...',
                           speaker_facebook_id=1)
        database.session.add(talk)
        database.session.commit()

        returned_talk = models.Talk.query.get(1)
        self.assertEqual(returned_talk.title, talk.title)
        self.assertEqual(returned_talk.speaker_facebook_id, talk.speaker_facebook_id)
        self.assertEqual(returned_talk.description, talk.description)

    def test_valid_talk_repr(self):
        talk = models.Talk(id=1, title='ti', description='desc', speaker_facebook_id=2)
        expected_output = '<Talk id=1, title=\'ti\', description=\'desc\', ' \
                          'speaker_facebook_id=2>'
        self.assertEqual(repr(talk), expected_output)

    def test_valid_talk_with_speaker_and_likes(self):
        speaker = models.Speaker(facebook_id=1, name='Jane Doe (Qweqwe, inc.)')
        talk = models.Talk(id=1, title='How to grow the grapes',
                           speaker_facebook_id=speaker.facebook_id)
        database.session.add(speaker)
        database.session.add(talk)
        liker_ids = []
        for liker_facebook_id in range(3):
            like = models.Liker_Talk(liker_facebook_id=liker_facebook_id, talk_id=talk.id)
            liker_ids.append(like.liker_facebook_id)
            database.session.add(like)
        database.session.commit()

        returned_talk = models.Talk.query.get(1)
        returned_talk_likes = returned_talk.likes.all()
        returned_liker_ids = [like.liker_facebook_id for like in returned_talk_likes]
        self.assertEqual(liker_ids, returned_liker_ids)

    def test_invalid_talk_without_title(self):
        talk = models.Talk(speaker_facebook_id=1)
        database.session.add(talk)
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            database.session.commit()

    def test_invalid_talk_without_speaker(self):
        talk = models.Talk(title='How to grow the grapes')
        database.session.add(talk)
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            database.session.commit()

    def test_invalid_talk_duplicate_title(self):
        talk = models.Talk(title='How to grow the grapes', speaker_facebook_id=1)
        duplicate_talk = models.Talk(title='How to grow the grapes', speaker_facebook_id=2)
        database.session.add(talk)
        database.session.add(duplicate_talk)
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            database.session.commit()


if __name__ == '__main__':
    unittest.main()
