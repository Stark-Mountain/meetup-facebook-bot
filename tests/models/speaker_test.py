import os
import tempfile
import unittest

import sqlalchemy

from app import app
from app import models
from app import database

class SpeakerTestCase(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        database.create_all()

    def tearDown(self):
        database.session.remove()
        database.drop_all()

    def test_valid_speaker_without_talks(self):
        speaker = models.Speaker(facebook_id=1, name='Jane Doe (Qweqwe, inc.)')
        database.session.add(speaker)
        database.session.commit()

        returned_speaker = models.Speaker.query.get(1)
        self.assertEqual(len(returned_speaker.talks.all()), 0)
        self.assertEqual(returned_speaker.facebook_id, speaker.facebook_id)
        self.assertEqual(returned_speaker.name, speaker.name)

    def test_valid_speaker_duplicate_name(self):
        speaker1 = models.Speaker(facebook_id=1, name='Jane Doe (Qweqwe, inc.)')
        speaker2 = models.Speaker(facebook_id=2, name='Jane Doe (Qweqwe, inc.)')
        database.session.add(speaker1)
        database.session.add(speaker2)
        database.session.commit()

        returned_speaker1 = models.Speaker.query.get(1)
        returned_speaker2 = models.Speaker.query.get(2)
        self.assertEqual(returned_speaker1.facebook_id, speaker1.facebook_id)
        self.assertEqual(returned_speaker2.facebook_id, speaker2.facebook_id)
        self.assertEqual(returned_speaker1.name, speaker1.name)
        self.assertEqual(returned_speaker2.name, speaker2.name)

    def test_invalid_speaker_without_name(self):
        speaker = models.Speaker(facebook_id=1)
        database.session.add(speaker)
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            database.session.commit()

    def test_invalid_speaker_without_facebook_id(self):
        speaker = models.Speaker(name='Jane Doe (Qweqwe, inc.)')
        database.session.add(speaker)
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            database.session.commit()

    def test_invalid_speaker_duplicate_facebook_id(self):
        speaker = models.Speaker(facebook_id=1, name='Jane Doe (Qweqwe, inc.)')
        database.session.add(speaker)
        database.session.commit()
        
        duplicate_speaker = models.Speaker(facebook_id=1, name='John Doe (Qweqwe, inc.)')
        database.session.add(duplicate_speaker)
        with self.assertRaises(sqlalchemy.orm.exc.FlushError):
            database.session.commit()



if __name__ == '__main__':
    unittest.main()
