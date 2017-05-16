import logging

from meetup_facebook_bot.models.talk import Talk
from meetup_facebook_bot.models.speaker import Speaker
from meetup_facebook_bot.models.like import Like
from meetup_facebook_bot.messenger import messaging


def handle_talk_info_command(messaging_event, access_token, db_session):
    sender_id = messaging_event['sender']['id']
    payload = messaging_event['postback']['payload']
    talk_id = int(payload.split(' ')[-1])
    talk = db_session.query(Talk).get(talk_id)
    if not talk:
        logging.error('No talk founded with this id: %s' % talk_id)
        return
    return messaging.send_talk_info(access_token, sender_id, talk)


def handle_talk_rate_command(messaging_event, access_token, db_session):
    sender_id = messaging_event['sender']['id']
    payload = messaging_event['postback']['payload']
    talk_id = int(payload.split(' ')[-1])
    talk = db_session.query(Talk).get(talk_id)
    if not talk:
        logging.error('No talk founded with this id: %s' % talk_id)
        return
    talk_liked = talk.is_liked_by(sender_id, db_session)
    return messaging.send_rate_menu(access_token, sender_id, talk, talk_liked)


def handle_talk_like_command(messaging_event, access_token, db_session):
    sender_id = messaging_event['sender']['id']
    payload = messaging_event['message']['quick_reply']['payload']
    talk_id = int(payload.split(' ')[-1])
    talk = db_session.query(Talk).get(talk_id)
    if not talk:
        logging.error('No talk founded with this id: %s' % talk_id)
        return
    talk.revert_like(sender_id, db_session)
    talk_liked = talk.is_liked_by(sender_id, db_session)
    return messaging.send_like_confirmation(access_token, sender_id, talk, talk_liked)


def handle_no_ask_question_url_postback(messaging_event, access_token, db_session):
    sender_id = messaging_event['sender']['id']
    return messaging.send_no_ask_question_url_warning(access_token, sender_id)


def handle_schedule_command(messaging_event, access_token, db_session):
    sender_id = messaging_event['sender']['id']
    talks = db_session.query(Talk).all()
    talk_like_numbers = {talk.id: talk.count_likes(db_session) for talk in talks}
    likes_by_user = list(db_session.query(Like).filter_by(user_facebook_id=sender_id))
    liked_talk_ids = [like.talk_id for like in likes_by_user]
    return messaging.send_schedule(access_token, sender_id, talks, 
                                   talk_like_numbers, liked_talk_ids)


def handle_speaker_auth(messaging_event, access_token, db_session):
    sender_id = messaging_event['sender']['id']
    message_text = messaging_event['message']['text']
    speaker = db_session.query(Speaker).filter_by(token=message_text).scalar()
    if not speaker:
        return
    if speaker.page_scoped_id is not None:
        return messaging.send_duplicate_authentication_error(access_token, sender_id)
    speaker.page_scoped_id = sender_id
    db_session.commit()
    return messaging.send_authentication_confirmation(access_token, sender_id, speaker.name)
