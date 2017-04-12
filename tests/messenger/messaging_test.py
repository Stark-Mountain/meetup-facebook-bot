import os

import vcr_unittest

from app.messenger import messaging


class MessagingTestCase(vcr_unittest.VCRTestCase):
    
    def setUp(self):
        self.access_token = os.environ['ACCESS_TOKEN']
        self.user_id = '100011269503253'

    def test_send_main_menu(self):
        response = messaging.send_main_menu(self.access_token, self.user_id)
        self.assertTrue('recipient_id' in response)
        self.assertTrue('message_id' in response)
        self.assertEqual(response['recipient_id'], self.user_id)
