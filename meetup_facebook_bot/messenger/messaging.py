# -*- coding: utf-8 -*-

import json

import requests


def send_rate_menu(access_token, user_id, talk, db_session):
    if talk.is_liked_by(user_id, db_session):
        rate_button_title = 'Убрать лайк'
    else:
        rate_button_title = 'Поставить лайк'
    rate_button_payload = 'like talk %d' % talk.id
    cancel_button_title = 'Отменить'
    cancel_button_payload = 'cancel payload'
    rate_button = create_quick_reply_text_button(
        rate_button_title,
        rate_button_payload
    )
    cancel_button = create_quick_reply_text_button(
        cancel_button_title,
        cancel_button_payload
    )
    buttons = [rate_button, cancel_button]
    text = 'Как вам доклад "%s"?' % talk.title
    return send_quick_replies(access_token, user_id, text, buttons)


def send_like_confirmation(access_token, user_id, talk, db_session):
    talk_title = talk.title
    if talk.is_liked_by(user_id, db_session):
        like_text_message = 'Поставил лайк докладу:\n %s' % talk_title
    else:
        like_text_message = 'Убрал лайк c доклада:\n %s' % talk_title
    return send_text_message(access_token, user_id, like_text_message)


def create_ask_question_button(ask_question_url):
    title = 'Задать вопрос'
    if ask_question_url is None:
        payload = 'ask question no url'
        return create_postback_button(title, payload)
    return create_web_url_button(title, ask_question_url)


def create_schedule_page_subtitle(like_text, number_of_likes, speaker_name):
    return '{like_text}\nЛайков: {number_of_likes}\nСпикер: {name}'.format(
        like_text=like_text,
        number_of_likes=number_of_likes,
        name=speaker_name
    )


def send_schedule(access_token, user_id, talks, db_session):
    generic_template_pages = []
    for talk in talks:
        number_of_likes = talk.count_likes(db_session)
        if talk.is_liked_by(user_id, db_session):
            like_text = 'Вы лайкнули этот доклад'
        else:
            like_text = 'Вы не оценили этот докад'
        page_subtitle = create_schedule_page_subtitle(
            like_text,
            number_of_likes,
            talk.speaker.name
        )
        more_talk_info_button = create_postback_button(
            title='Получить подробности',
            payload='info talk %d' % talk.id
        )
        rate_button = create_postback_button(
            title='Оценить',
            payload='rate talk %d' % talk.id
        )
        ask_question_button = create_ask_question_button(talk.ask_question_url)
        buttons = [more_talk_info_button, rate_button, ask_question_button]
        page = create_generic_template_page(talk.title, page_subtitle, buttons)
        generic_template_pages.append(page)
    return send_generic_template(access_token, user_id, generic_template_pages)


def send_talk_info(access_token, user_id, talk):
    title = talk.title
    speaker = talk.speaker.name
    description = talk.description or 'Нет описания.'
    more_info_text = '"%s"\n\n%s:\n%s' % (title, speaker, description)
    return send_text_message(access_token, user_id, more_info_text)


def send_duplicate_authentication_error(access_token, user_id):
    text = 'Докладчик уже авторизован, повторно не получится.'
    return send_text_message(access_token, user_id, text)


def send_authentication_confirmation(access_token, user_id, speaker_name):
    text = 'Вы зарегистрировались как докладчик %s.' % speaker_name
    return send_text_message(access_token, user_id, text)


def send_no_ask_question_url_warning(access_token, user_id):
    text = 'Я не знаю, куда отправлять вопрос.'
    return send_text_message(access_token, user_id, text)


def create_postback_button(title, payload):
    button = {
        'type': 'postback',
        'title': title,
        'payload': payload
    }
    return button


def create_web_url_button(title, url):
    button = {
        'type': 'web_url',
        'url': url,
        'title': title
    }
    return button


def create_quick_reply_text_button(title, payload):
    button = {
        'content_type': 'text',
        'title': title,
        'payload': payload
    }
    return button


def create_generic_template_page(title, subtitle, buttons):
    page = {
        'title': title,
        'subtitle': subtitle,
        'buttons': buttons
    }
    return page


def send_generic_template(access_token, user_id, pages):
    """ Makes use of Generic Template:
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/generic-template
    """
    message_body = {
        'attachment': {
            'type': 'template',
            'payload': {
                'template_type': 'generic',
                'elements': pages
            }
        }
    }
    return send_message_to_facebook(access_token, user_id, message_body)


def send_quick_replies(access_token, user_id, text, buttons):
    """ Makes use of Quick Replies:
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/quick-replies
    """
    message_body = {
        'text': text,
        'quick_replies': buttons
    }
    return send_message_to_facebook(access_token, user_id, message_body)


def send_text_message(access_token, user_id, text):
    """ Send a simple Facebook message:
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/text-message
    """
    message_body = {
        'text': text
    }
    return send_message_to_facebook(access_token, user_id, message_body)


def send_message_to_facebook(access_token, user_id, message_data):
    """ Makes use of Send API:
        https://developers.facebook.com/docs/messenger-platform/send-api-reference
    """
    headers = {
        'Content-Type': 'application/json',
    }
    params = {
        'access_token': access_token,
    }
    payload = {
        'recipient': {
            'id': user_id,
        },
        'message': message_data,
    }
    url = 'https://graph.facebook.com/v2.6/me/messages'
    response = requests.post(url, headers=headers, params=params,
                             data=json.dumps(payload))
    response.raise_for_status()
    return response.json()
