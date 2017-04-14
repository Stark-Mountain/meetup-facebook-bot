import os
import unittest

import flask

from app import app
from app import database
from app import models


class VerifyRouteTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        os.environ['PAGE_ID'] = '1'
        os.environ['APP_ID'] = '1'
        os.environ['VERIFY_TOKEN'] = '1'
        self.challenge = 'asdasdasd'
        self.hub_mode = 'hub.mode=subscribe'
        self.hub_challenge = 'hub.challenge=%s' % self.challenge
        self.hub_verify_token = 'hub.verify_token=%s' % os.environ['VERIFY_TOKEN']

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
