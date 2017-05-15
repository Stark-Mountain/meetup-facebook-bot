import json
from unittest import TestCase
from unittest.mock import patch, MagicMock

from meetup_facebook_bot import server


class WebhookRouteTestCase(TestCase):
    def setUp(self):
        self.access_token = 1
        self.sender_id = 'USER_ID'

        server.app.config['ACCESS_TOKEN'] = self.access_token
        self.app = server.app.test_client()
        server.engine = MagicMock()
        server.Session = MagicMock()
        server.db_session = MagicMock()

    def generate_facebook_request(self, message_kind, message):
        facebook_request = {
            'object': 'page',
            'entry': [
                {
                    'messaging': [
                        {
                            'sender': {
                                'id': self.sender_id
                            },
                            message_kind: message
                        }
                    ]
                }
            ]
        }
        return facebook_request

    def generate_quick_reply(self, payload):
        message = {
            'text': 'Doesn\'t matter',
            'quick_reply': {
                'payload': payload
            }
        }
        return self.generate_facebook_request('message', message)

    def generate_postback(self, payload):
        message = {
            'payload': payload
        }
        return self.generate_facebook_request('postback', message)

    def generate_simple_text_message(self):
        message = {
            'text': 'Doesn\'t matter'
        }
        return self.generate_facebook_request('message', message)

    @patch('meetup_facebook_bot.server.message_handlers')
    def test_handle_talk_info_command_gets_called(self, message_handlers_mock):
        message_handlers_mock.handle_talk_info_command = MagicMock()
        known_input = self.generate_postback('info talk 1')
        self.app.post('/', data=json.dumps(known_input), content_type='application/json')
        number_of_calls = message_handlers_mock.handle_talk_info_command.call_count
        self.assertEqual(number_of_calls, 1)    

    @patch('meetup_facebook_bot.server.message_handlers')
    def test_handle_talk_rate_command_gets_called(self, message_handlers_mock):
        message_handlers_mock.handle_talk_rate_command = MagicMock()
        known_input = self.generate_postback('rate talk 1')
        self.app.post('/', data=json.dumps(known_input), content_type='application/json')
        number_of_calls = message_handlers_mock.handle_talk_rate_command.call_count
        self.assertEqual(number_of_calls, 1)   

    @patch('meetup_facebook_bot.server.message_handlers')
    def test_handle_talk_like_command_gets_called(self, message_handlers_mock):
        message_handlers_mock.handle_talk_like_command = MagicMock()
        known_input = self.generate_quick_reply('like talk 1')
        self.app.post('/', data=json.dumps(known_input), content_type='application/json')
        number_of_calls = message_handlers_mock.handle_talk_like_command.call_count
        self.assertEqual(number_of_calls, 1)

    @patch('meetup_facebook_bot.server.message_handlers')
    def test_handle_no_ask_question_url_postback_gets_called(self, message_handlers_mock):
        message_handlers_mock.handle_no_ask_question_url_postback = MagicMock()
        known_input = self.generate_postback('ask question no url')
        self.app.post('/', data=json.dumps(known_input), content_type='application/json')
        number_of_calls = message_handlers_mock.handle_no_ask_question_url_postback.call_count
        self.assertEqual(number_of_calls, 1)

    @patch('meetup_facebook_bot.server.message_handlers')
    def test_handle_schedule_command_gets_called(self, message_handlers_mock):
        message_handlers_mock.handle_schedule_command = MagicMock()
        known_input = self.generate_quick_reply('schedule payload')
        self.app.post('/', data=json.dumps(known_input), content_type='application/json')
        number_of_calls = message_handlers_mock.handle_schedule_command.call_count
        self.assertEqual(number_of_calls, 1)   

    @patch('meetup_facebook_bot.server.message_handlers')
    def test_handle_speaker_auth_gets_called(self, message_handlers_mock):
        message_handlers_mock.handle_speaker_auth = MagicMock()
        known_input = self.generate_simple_text_message()
        self.app.post('/', data=json.dumps(known_input), content_type='application/json')
        number_of_calls = message_handlers_mock.handle_speaker_auth.call_count
        self.assertEqual(number_of_calls, 1)