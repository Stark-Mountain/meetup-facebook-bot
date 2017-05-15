from unittest import TestCase
from unittest.mock import patch, MagicMock

from meetup_facebook_bot import server
from meetup_facebook_bot.messenger import message_handlers


class MessageHandlersTestCase(TestCase):
    def setUp(self):
        self.access_token = 1
        self.sender_id = 'USER_ID'
        server.app.config['ACCESS_TOKEN'] = self.access_token
        server.engine = MagicMock()
        server.Session = MagicMock()
        server.db_session = MagicMock()

    def generate_messaging_event(self, message_kind, message):
        messaging_event = {
            'sender': {
                'id': self.sender_id
            },
            message_kind: message
        }
        return messaging_event

    def generate_quick_reply(self, payload):
        message = {
            'text': 'Doesn\'t matter',
            'quick_reply': {
                'payload': payload
            }
        }
        return self.generate_messaging_event('message', message)

    def generate_postback(self, payload):
        message = {
            'payload': payload
        }
        return self.generate_messaging_event('postback', message)

    def generate_simple_text_message(self):
        message = {
            'text': 'Doesn\'t matter'
        }
        return self.generate_messaging_event('message', message)
        
    @patch('meetup_facebook_bot.messenger.message_handlers.messaging.send_talk_info')
    def test_handle_talk_info_command(self, send_talk_info_mock):
        messaging_event = self.generate_postback('info talk 1')
        talk_mock = MagicMock()
        server.db_session.query().get = MagicMock(return_value=talk_mock)
        message_handlers.handle_talk_info_command(messaging_event, self.access_token, server.db_session)
        send_talk_info_mock.assert_called_once_with(
            self.access_token,
            self.sender_id,
            talk_mock
            )
    
    @patch('meetup_facebook_bot.messenger.message_handlers.messaging.send_rate_menu')
    @patch('meetup_facebook_bot.messenger.message_handlers.Talk')
    def test_handle_talk_rate_command(self, talk_class_mock, send_rate_mock):
        messaging_event = self.generate_postback('rate talk 1')
        talk_mock = MagicMock(talk_id=1)
        talk_liked_mock = False
        talk_mock.is_liked_by = MagicMock(return_value=False)
        server.db_session.query(talk_class_mock).get = MagicMock(return_value=talk_mock)
        message_handlers.handle_talk_rate_command(messaging_event, self.access_token, server.db_session)
        talk_mock.is_liked_by.assert_called_once_with(
            self.sender_id,
            server.db_session
            )
        send_rate_mock.assert_called_once_with(
            self.access_token,
            self.sender_id,
            talk_mock,
            talk_liked_mock
            )

    @patch('meetup_facebook_bot.messenger.message_handlers.messaging.send_like_confirmation')
    @patch('meetup_facebook_bot.messenger.message_handlers.Talk')
    def test_handle_talk_like_command(self, talk_class_mock, send_like_confirmation_mock):
        messaging_event = self.generate_quick_reply('like talk 1')
        talk_mock = MagicMock(talk_id=1)
        talk_mock.revert_like = MagicMock()
        talk_liked_mock = False
        talk_mock.is_liked_by = MagicMock(return_value=talk_liked_mock)
        server.db_session.query(talk_class_mock).get = MagicMock(return_value=talk_mock)
        message_handlers.handle_talk_like_command(messaging_event, self.access_token, server.db_session)
        talk_mock.revert_like.assert_called_once_with(
            self.sender_id,
            server.db_session
            )
        send_like_confirmation_mock.assert_called_once_with(
            self.access_token,
            self.sender_id,
            talk_mock,
            talk_liked_mock
            )
        
    @patch('meetup_facebook_bot.messenger.message_handlers.messaging.send_no_ask_question_url_warning')
    def test_handle_no_ask_question_url_postback(self, send_no_ask_question_url_warning_mock):
        messaging_event = self.generate_postback('ask question no url')
        message_handlers.handle_no_ask_question_url_postback(messaging_event, self.access_token, server.db_session)
        send_no_ask_question_url_warning_mock.assert_called_once_with(
            self.access_token,
            self.sender_id
            ) 

    @patch('meetup_facebook_bot.messenger.message_handlers.messaging.send_schedule')
    @patch('meetup_facebook_bot.messenger.message_handlers.Talk')
    def test_handle_schedule_command(self, talk_class_mock, send_schedule_mock):
        messaging_event = self.generate_postback('schedule payload')
        talks_mock = [MagicMock(talk_id=1), MagicMock(talk_id=2)]
        server.db_session.query().all = MagicMock(return_value=talks_mock)
        for talk_mock in talks_mock:
            talk_mock.id = 1
            talk_mock.count_likes = MagicMock(return_value=1)
        for talk_mock in talks_mock:
            talk_like_numbers_mock = {talk_mock.id: talk_mock.count_likes()}
        talk_like_ids_mock = []
        message_handlers.handle_schedule_command(messaging_event, self.access_token, server.db_session)
        send_schedule_mock.assert_called_once_with(
            self.access_token,
            self.sender_id,
            talks_mock,
            talk_like_numbers_mock,
            talk_like_ids_mock
            )

    @patch('meetup_facebook_bot.messenger.message_handlers.messaging.send_authentication_confirmation')
    @patch('meetup_facebook_bot.messenger.message_handlers.Speaker')
    def test_handle_speaker_auth(self, speaker_class_mock, send_authentication_confirmation_mock):
        messaging_event = self.generate_simple_text_message()
        speaker_mock = MagicMock()
        server.db_session.query().filter_by().scalar = MagicMock(return_value=speaker_mock)
        speaker_mock.page_scoped_id = None
        speaker_mock.name = 'asdaf'
        message_handlers.handle_speaker_auth(messaging_event, self.access_token, server.db_session)
        send_authentication_confirmation_mock.assert_called_once_with(
            self.access_token, 
            self.sender_id,
            speaker_mock.name
            )