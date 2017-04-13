import os
import unittest

import vcr

from app import app
from app import database
from app import models
from app.messenger import messaging


class MessagingTestCase(unittest.TestCase):
    
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        database.create_all()
        self.access_token = os.environ['ACCESS_TOKEN']
        self.user_id = '474276666029691'

    def tearDown(self):
        database.session.remove()
        database.drop_all()

    def test_send_main_menu(self):
        with vcr.use_cassette('vcr_cassettes/send_main_menu.yaml'):
            response = messaging.send_main_menu(self.access_token, self.user_id)
        self.assertTrue('recipient_id' in response)
        self.assertTrue('message_id' in response)
        self.assertEqual(response['recipient_id'], self.user_id)

    def test_send_schedule(self):
        for talk_id in range(5):
            speaker = models.Speaker(facebook_id=talk_id, name=str(talk_id))
            talk = models.Talk(title=str(talk_id), speaker=speaker)
            database.session.add(talk)
        database.session.commit()
        with vcr.use_cassette('vcr_cassettes/send_schedule.yaml'):
            response = messaging.send_schedule(self.access_token, self.user_id)
        self.assertTrue('recipient_id' in response)
        self.assertTrue('message_id' in response)
        self.assertEqual(response['recipient_id'], self.user_id)
