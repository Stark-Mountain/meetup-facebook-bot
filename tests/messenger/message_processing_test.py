import unittest

from app.messenger import message_processing


class MessageProcessingTestCase(unittest.TestCase):

    def test_is_quick_button_pressed_true(self):
        known_input = {
            "sender": {
                "id": "USER_ID"
            },
            "recipient": {
                "id": "PAGE_ID"
            },
            "timestamp": 1458692752478,
            "message": {
                "mid": "mid.1457764197618:41d102a3e1ae206a38",
                "text": "hello, world!",
                "quick_reply": {
                    "payload": "DEVELOPER_DEFINED_PAYLOAD"
                }
            }
        }
        self.assertTrue(message_processing.is_quick_button_pressed(known_input))

    def test_is_quick_button_pressed_false(self):
        known_input = {
            "sender": {
                "id": "USER_ID"
            },
            "recipient": {
                "id": "PAGE_ID"
            },
            "timestamp": 1458692752478,
            "message": {
                "mid": "mid.1457764197618:41d102a3e1ae206a38",
                "text": "hello, world!",
            }
        }
        self.assertFalse(message_processing.is_quick_button_pressed(known_input))

    def test_is_schedule_button_pressed_true(self):
        known_input = {
            "sender": {
                "id": "USER_ID"
            },
            "recipient": {
                "id": "PAGE_ID"
            },
            "timestamp": 1458692752478,
            "message": {
                "mid": "mid.1457764197618:41d102a3e1ae206a38",
                "text": "hello, world!",
                "quick_reply": {
                    "payload": "schedule payload"
                }
            }
        }
        self.assertTrue(message_processing.is_schedule_button_pressed(known_input))

    def test_is_schedule_button_pressed_false_not_quick_button(self):
        known_input = {
            "sender": {
                "id": "USER_ID"
            },
            "recipient": {
                "id": "PAGE_ID"
            },
            "timestamp": 1458692752478,
            "message": {
                "mid": "mid.1457764197618:41d102a3e1ae206a38",
                "text": "hello, world!",
            }
        }
        self.assertFalse(message_processing.is_schedule_button_pressed(known_input))

    def test_is_schedule_button_pressed_false_not_schedule_button(self):
        known_input = {
            "sender": {
                "id": "USER_ID"
            },
            "recipient": {
                "id": "PAGE_ID"
            },
            "timestamp": 1458692752478,
            "message": {
                "mid": "mid.1457764197618:41d102a3e1ae206a38",
                "text": "hello, world!",
                "quick_reply": {
                    "payload": "chat payload"
                }
            }
        }
        self.assertFalse(message_processing.is_schedule_button_pressed(known_input))

    def test_is_more_talk_info_button_pressed_true(self):
        known_input = {
            "sender": {
                "id": "USER_ID"
            },
            "recipient": {
                "id": "PAGE_ID"
            },
            "timestamp": 1458692752478,
            "postback": {
                "payload": "info talk 1",
            }
        }
        self.assertTrue(message_processing.is_more_talk_info_button_pressed(known_input))

    def test_is_more_talk_info_button_pressed_false_not_postback(self):
        known_input = {
            "sender": {
                "id": "USER_ID"
            },
            "recipient": {
                "id": "PAGE_ID"
            },
            "timestamp": 1458692752478,
            "message": {
                "mid": "mid.1457764197618:41d102a3e1ae206a38",
                "text": "hello, world!",
            }
        }
        self.assertFalse(message_processing.is_more_talk_info_button_pressed(known_input))

    def test_is_more_talk_info_button_pressed_false_payload(self):
        known_input = {
            "sender": {
                "id": "USER_ID"
            },
            "recipient": {
                "id": "PAGE_ID"
            },
            "timestamp": 1458692752478,
            "postback": {
                "payload": "like talk 1",
            }
        }
        self.assertFalse(message_processing.is_more_talk_info_button_pressed(known_input))

    def test_is_like_talk_button_pressed_true(self):
        known_input = {
            "sender": {
                "id": "USER_ID"
            },
            "recipient": {
                "id": "PAGE_ID"
            },
            "timestamp": 1458692752478,
            "postback": {
                "payload": "like talk 1",
            }
        }
        self.assertTrue(message_processing.is_like_talk_button_pressed(known_input))

    def test_is_like_talk_button_pressed_false_not_postback(self):
        known_input = {
            "sender": {
                "id": "USER_ID"
            },
            "recipient": {
                "id": "PAGE_ID"
            },
            "timestamp": 1458692752478,
            "message": {
                "mid": "mid.1457764197618:41d102a3e1ae206a38",
                "text": "hello, world!",
            }
        }
        self.assertFalse(message_processing.is_like_talk_button_pressed(known_input))

    def test_is_like_talk_button_pressed_false_payload(self):
        known_input = {
            "sender": {
                "id": "USER_ID"
            },
            "recipient": {
                "id": "PAGE_ID"
            },
            "timestamp": 1458692752478,
            "postback": {
                "payload": "info talk 1",
            }
        }
        self.assertFalse(message_processing.is_like_talk_button_pressed(known_input))
