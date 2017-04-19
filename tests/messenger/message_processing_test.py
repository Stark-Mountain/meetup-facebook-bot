import unittest

from app.messenger import message_processing


class MessageProcessingTestCase(unittest.TestCase):
    def test_extract_all_messaging_events_valid_input(self):
        known_input = [
            {
                'id': 1,
                'messaging': [
                    {
                        'messaging_event_id': 0
                    },
                    {
                        'messaging_event_id': 1
                    },
                    {
                        'messaging_event_id': 2
                    }
                ]
            },
            {
                'id': 2,
                'messaging': [
                    {
                        'messaging_event_id': 3
                    },
                    {
                        'messaging_event_id': 4
                    },
                    {
                        'messaging_event_id': 5
                    }
                ]
            },
            {
                'id': 3,
                'messaging': [
                    {
                        'messaging_event_id': 6
                    },
                    {
                        'messaging_event_id': 7
                    },
                    {
                        'messaging_event_id': 8
                    }
                ]
            }
        ]
        expected_output = [{'messaging_event_id': event_id} for event_id in range(9)]
        output = message_processing.extract_all_messaging_events(known_input)
        self.assertEqual(output, expected_output)

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
