from unittest import TestCase
from unittest.mock import patch, MagicMock

from meetup_facebook_bot.models.talk import Talk


class TalkTestCase(TestCase):
    def setUp(self):
        self.db_session = MagicMock()
        self.like_mock = MagicMock()
        self.user_id = 1
        self.talk_id = 1
        self.talk = Talk(id=self.talk_id)

    @patch('meetup_facebook_bot.models.talk.Like')
    def test_set_like(self, like_class_mock):
        like_class_mock.return_value = self.like_mock
        self.talk.is_liked_by = MagicMock(return_value=False)
        self.talk.set_like(self.user_id, self.db_session)
        like_class_mock.assert_called_once_with(user_facebook_id=self.user_id, talk_id=self.talk_id)
        self.db_session.add.assert_called_once_with(self.like_mock)

    def test_unset_like(self):
        self.talk.is_liked_by = MagicMock(return_value=True)
        scalar_mock = MagicMock(return_value=self.like_mock)
        self.db_session.query().filter_by().scalar = scalar_mock
        self.talk.unset_like(self.user_id, self.db_session)
        self.db_session.delete.assert_called_once_with(self.like_mock)
