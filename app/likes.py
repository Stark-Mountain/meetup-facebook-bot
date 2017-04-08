from app import database
from app import models


def is_like_set(user_id, talk_id):
    like = database.session.query(models.Liker_Talk).filter_by(
            liker_facebook_id=user_id,
            talk_id=talk_id
            )
    return database.session.query(like.exists()).scalar()


def set_like(user_id, talk_id):
    liked_talk = models.Talk.query.get(talk_id)
    if liked_talk is None:
        raise ValueError('Couldn\'t get a talk using the talk_id provided.')
    if is_like_set(user_id, talk_id):
        raise ValueError('The like has already been set.')
    like = models.Liker_Talk(liker_facebook_id=user_id, talk=liked_talk)
    database.session.add(like)
    database.session.commit()


def unset_like(user_id, talk_id):
    liked_talk = models.Talk.query.get(talk_id)
    if liked_talk is None:
        raise ValueError('Couldn\'t get a talk using the talk_id provided.')
    if not is_like_set(user_id, talk_id):
        raise ValueError('The like has not been set.')
    like = database.session.query(models.Liker_Talk).filter_by(
            liker_facebook_id=user_id,
            talk_id=talk_id
            ).scalar()
    database.session.delete(like)
    database.session.commit()
