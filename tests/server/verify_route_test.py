import unittest

from meetup_facebook_bot import server


class VerifyRouteTestCase(unittest.TestCase):
    def setUp(self):
        server.app.config['PAGE_ID'] = '1'
        server.app.config['APP_ID'] = '1'
        server.app.config['VERIFY_TOKEN'] = '1'
        self.app = server.app.test_client()
        self.challenge = 'asdasdasd'
        self.hub_mode = 'hub.mode=subscribe'
        self.hub_challenge = 'hub.challenge=%s' % self.challenge
        self.hub_verify_token = 'hub.verify_token=%s' % server.app.config['VERIFY_TOKEN']

    def test_verify_without_params(self):
        response = self.app.get('/')
        self.assertTrue(b'<!DOCTYPE html>' in response.data)

    def test_verify_with_valid_verify_token(self):
        url = '/?%s&%s&%s' % (self.hub_mode, self.hub_challenge, self.hub_verify_token)
        response = self.app.get(url)
        self.assertTrue(str.encode(self.challenge) in response.data)

    def test_verify_with_invalid_verify_token(self):
        response = self.app.get('/?%s&%s' % (self.hub_mode, self.hub_challenge))
        self.assertEqual(403, response.status_code)

    def test_verify_without_hub_mode(self):
        url = '/?%s&%s' % (self.hub_challenge, self.hub_verify_token)
        response = self.app.get(url)
        self.assertTrue(b'<!DOCTYPE html>' in response.data)

    def test_verify_without_hub_challenge(self):
        url = '/?%s&%s' % (self.hub_mode, self.hub_verify_token)
        response = self.app.get(url)
        self.assertTrue(b'<!DOCTYPE html>' in response.data)
