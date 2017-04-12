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

    def test_valid_talk_without_description_likes(self):
        speaker = models.Speaker(facebook_id=1, name='Jane Doe (Qweqwe, inc.)')
        talk = models.Talk(title='How to grow the grapes', speaker_facebook_id=speaker.facebook_id)
        database.session.add(speaker)
        database.session.add(talk)
        database.session.commit()

        returned_talk = models.Talk.query.get(1)
        self.assertEqual(returned_talk.title, talk.title)
        self.assertEqual(returned_talk.speaker_facebook_id, talk.speaker_facebook_id)
        self.assertIsNone(returned_talk.description)
        self.assertEqual(len(returned_talk.likes.all()), 0)

    def test_valid_talk_with_description(self):
        speaker = models.Speaker(facebook_id=1, name='Jane Doe (Qweqwe, inc.)')
        talk = models.Talk(title='How to grow the grapes', 
                           description='Once you master the world\'s six most important wine grapes, you are on your way to understanding 80 percent of the world\'s wines',
                           speaker_facebook_id=speaker.facebook_id)
        database.session.add(speaker)
        database.session.add(talk)
        database.session.commit()

        returned_talk = models.Talk.query.get(1)
        self.assertEqual(returned_talk.title, talk.title)
        self.assertEqual(returned_talk.speaker_facebook_id, talk.speaker_facebook_id)
        self.assertEqual(returned_talk.description, talk.description)

    def test_valid_talk_with_likes(self):
        speaker = models.Speaker(facebook_id=1, name='Jane Doe (Qweqwe, inc.)')
        talk = models.Talk(title='How to grow the grapes', speaker_facebook_id=speaker.facebook_id)
        database.session.add(speaker)
        database.session.add(talk)
        database.session.commit()
        like1 = models.Liker_Talk(liker_facebook_id=2, talk_id=talk.id)
        like2 = models.Liker_Talk(liker_facebook_id=3, talk_id=talk.id)
        like3 = models.Liker_Talk(liker_facebook_id=4, talk_id=talk.id)
        database.session.add(like1)
        database.session.add(like2)
        database.session.add(like3)
        database.session.commit()

        returned_talk = models.Talk.query.get(1)
        returned_talk_likes = returned_talk.likes.all()
        self.assertEqual(returned_talk_likes[0].liker_facebook_id, like1.liker_facebook_id)
        self.assertEqual(returned_talk_likes[1].liker_facebook_id, like2.liker_facebook_id)
        self.assertEqual(returned_talk_likes[2].liker_facebook_id, like3.liker_facebook_id)


    def test_invalid_talk_without_title(self):
        speaker = models.Speaker(facebook_id=1, name='Jane Doe (Qweqwe, inc.)')
        talk = models.Talk(speaker_facebook_id=speaker.facebook_id)
        database.session.add(speaker)
        database.session.add(talk)
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            database.session.commit()

    def test_invalid_talk_without_speaker(self):
        speaker = models.Speaker(facebook_id=1, name='Jane Doe (Qweqwe, inc.)')
        talk = models.Talk(title='How to grow the grapes')
        database.session.add(speaker)
        database.session.add(talk)
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            database.session.commit()

    def test_invalid_talk_duplicate_title(self):
        speaker1 = models.Speaker(facebook_id=1, name='Jane Doe (Qweqwe, inc.)')
        speaker2 = models.Speaker(facebook_id=2, name='John Doe (Qweqwe, inc.)')
        talk = models.Talk(title='How to grow the grapes', speaker_facebook_id=speaker1.facebook_id)
        database.session.add(speaker1)
        database.session.add(speaker2)
        database.session.add(talk)
        database.session.commit()

        duplicate_talk = models.Talk(title='How to grow the grapes',
                                     speaker_facebook_id=speaker2.facebook_id)
        database.session.add(duplicate_talk)
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            database.session.commit()


if __name__ == '__main__':
    unittest.main()
