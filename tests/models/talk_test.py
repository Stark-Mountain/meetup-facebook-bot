from unittest import TestCase
from unittest.mock import patch, MagicMock
from meetup_facebook_bot.models.talk import Talk

class TalkTestCase(TestCase):

    def setUp(self):
        self.db_session = MagicMock()
        self.user_id = 1
        self.talk_id = 1


    def test_is_liked_by(self):
        pass


    @patch('meetup_facebook_bot.models.talk.Like')
    def test_set_like(self, like_class_mock):
        talk = Talk(id=self.talk_id)
        mock_like = MagicMock()
        like_class_mock.return_value = mock_like
        talk.is_liked_by = MagicMock(return_value=False)
        talk.set_like(self.user_id, self.db_session)
        like_class_mock.assert_called_once_with(user_facebook_id=self.user_id, talk_id=self.talk_id)
        self.db_session.add.assert_called_once_with(mock_like)

    def test_unset_like(self):
        talk = Talk(id=self.talk_id)
        talk.is_liked_by = MagicMock(return_value=True)
        like_mock = MagicMock()
        scalar_mock = MagicMock(return_value=like_mock)
        self.db_session.query().filter_by().scalar = scalar_mock
        talk.unset_like(self.user_id, self.db_session)
        self.db_session.delete.assert_called_once_with(like_mock)