import unittest

import vcr

from meetup_facebook_bot.messenger import messenger_profile


class MessengerProfileTestCase(unittest.TestCase):
    def setUp(self):
        self.access_token = '1'

    def test_get_started_button_set_get_delete(self):
        payload = 'test payload'
        with vcr.use_cassette('vcr_cassettes/set_get_started_button.yaml'):
            response = messenger_profile.set_get_started_button(self.access_token, payload)
            self.assertEqual(response, {'result': 'success'})
        with vcr.use_cassette('vcr_cassettes/get_get_started_button.yaml'):
            response = messenger_profile.get_field(self.access_token, 'get_started')
            self.assertEqual(response['data'][0]['get_started']['payload'], payload)
        with vcr.use_cassette('vcr_cassettes/delete_get_started_button.yaml'):
            response = messenger_profile.delete_field(self.access_token, 'get_started')
            self.assertEqual(response, {'result': 'success'})

    def test_greeting_set_get_delete(self):
        greeting_text = 'test greeting'
        with vcr.use_cassette('vcr_cassettes/set_greeting.yaml'):
            response = messenger_profile.set_greeting(self.access_token, greeting_text)
            self.assertEqual(response, {'result': 'success'})
        with vcr.use_cassette('vcr_cassettes/get_greeting.yaml'):
            response = messenger_profile.get_field(self.access_token, 'greeting')
            self.assertEqual(response['data'][0]['greeting'][0]['text'], greeting_text)
        with vcr.use_cassette('vcr_cassettes/delete_greeting.yaml'):
            response = messenger_profile.delete_field(self.access_token, 'greeting')
            self.assertEqual(response, {'result': 'success'})

    def test_get_cli_argument(self):
        args = ['-g', 'get_started']
        parsed_args = messenger_profile.get_cli_args(args)
        self.assertTrue(parsed_args.get)
        self.assertEqual(parsed_args.field, args[1])

    def test_set_cli_argument(self):
        args = ['-s', 'test payload', 'get_started']
        parsed_args = messenger_profile.get_cli_args(args)
        self.assertEqual(parsed_args.set, args[1])
        self.assertEqual(parsed_args.field, args[2])

    def test_delete_cli_argument(self):
        args = ['-d', 'get_started']
        parsed_args = messenger_profile.get_cli_args(args)
        self.assertTrue(parsed_args.delete)
        self.assertEqual(parsed_args.field, args[1])
