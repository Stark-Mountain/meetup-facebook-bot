import os
import unittest

import vcr

from app.messenger import messaging


class MessagingTestCase(unittest.TestCase):
    
    def setUp(self):
        self.access_token = os.environ['ACCESS_TOKEN']
        self.user_id = '474276666029691'

    def test_send_main_menu(self):
        with vcr.use_cassette('vcr_cassettes/send_main_menu.yaml'):
            response = messaging.send_main_menu(self.access_token, self.user_id)
        self.assertTrue('recipient_id' in response)
        self.assertTrue('message_id' in response)
        self.assertEqual(response['recipient_id'], self.user_id)
