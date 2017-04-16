import os
import unittest
from unittest.mock import patch
from unittest.mock import MagicMock

import vcr

from app import app
from app import database
from app import models
from app.messenger import messaging


class MessagingTestCase(unittest.TestCase):
    
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        database.create_all()
        self.access_token = '1'
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

    @patch('app.likes.is_like_set')
    @patch('app.likes.count_likes')
    @patch('app.models.Talk')
    def test_send_schedule(self, talk_class_mock, count_likes_mock, is_like_set_mock):
        talk_mocks = []
        for talk_id in range(1, 6):
            mock_talk_title = str(talk_id - 1)
            talk_mock = MagicMock(id=talk_id, title=mock_talk_title, speaker_facebook_id=1)
            talk_mocks.append(talk_mock)
        query_mock = MagicMock(all=MagicMock(return_value=talk_mocks))
        talk_class_mock.query = query_mock
        count_likes_mock.return_value = 0
        is_like_set_mock.return_value = False
        with vcr.use_cassette('vcr_cassettes/send_schedule.yaml'):
            response = messaging.send_schedule(self.access_token, self.user_id)

        self.assertTrue('recipient_id' in response)
        self.assertTrue('message_id' in response)
        self.assertEqual(response['recipient_id'], self.user_id)

    @patch('app.models.Talk')
    def test_send_more_talk_info(self, talk_class_mock):
        speaker_mock = MagicMock()
        speaker_mock.name = '1'
        talk_mock = MagicMock(title='1', speaker=speaker_mock, description=None)
        query_mock = MagicMock(all=MagicMock(return_value=talk_mock))
        talk_class_mock.query = query_mock
        with vcr.use_cassette('vcr_cassettes/send_more_talk_info.yaml'):
            response = messaging.send_more_talk_info(self.access_token, self.user_id, 1)
        self.assertTrue('recipient_id' in response)
        self.assertTrue('message_id' in response)
        self.assertEqual(response['recipient_id'], self.user_id)

    def test_send_more_talk_info_with_database(self):
        speaker = models.Speaker(facebook_id=1, name='1')
        talk = models.Talk(title='1', speaker=speaker)
        database.session.add(talk)
        database.session.commit()
        with vcr.use_cassette('vcr_cassettes/send_more_talk_info.yaml'):
            response = messaging.send_more_talk_info(self.access_token, self.user_id, 1)
        self.assertTrue('recipient_id' in response)
        self.assertTrue('message_id' in response)
        self.assertEqual(response['recipient_id'], self.user_id)

    def test_send_schedule_with_database_and_likes(self):
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
