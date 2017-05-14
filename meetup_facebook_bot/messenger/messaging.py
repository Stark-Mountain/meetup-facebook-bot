# -*- coding: utf-8 -*-
from meetup_facebook_bot.messenger import facebook_api


def send_rate_menu(access_token, user_id, talk, talk_liked):
    rate_button_title = 'Убрать лайк' if talk_liked else 'Поставить лайк'
    rate_button_payload = 'like talk %d' % talk.id
    cancel_button_title = 'Отменить'
    cancel_button_payload = 'cancel payload'
    rate_button = facebook_api.create_quick_reply_text_button(
        rate_button_title,
        rate_button_payload
    )
    cancel_button = facebook_api.create_quick_reply_text_button(
        cancel_button_title,
        cancel_button_payload
    )
    buttons = [rate_button, cancel_button]
    text = 'Как вам доклад "%s"?' % talk.title
    return facebook_api.send_quick_replies(access_token, user_id, text, buttons)


def send_like_confirmation(access_token, user_id, talk, talk_liked):
    like_confirmation = 'Поставил лайк докладу %s' % talk.title
    unlike_confirmation = 'Убрал лайк c доклада %s' % talk.title
    like_text_message = like_confirmation if talk_liked else unlike_confirmation
    return facebook_api.send_text_message(access_token, user_id, like_text_message)


def create_ask_question_button(ask_question_url):
    title = 'Задать вопрос'
    if ask_question_url is None:
        payload = 'ask question no url'
        return facebook_api.create_postback_button(title, payload)
    return facebook_api.create_web_url_button(title, ask_question_url)


def create_schedule_page_subtitle(like_text, number_of_likes, speaker_name):
    return '{like_text}\nЛайков: {number_of_likes}\nСпикер: {name}'.format(
        like_text=like_text,
        number_of_likes=number_of_likes,
        name=speaker_name
    )


def create_schedule_page(talk, number_of_likes, talk_liked):
    like_text = 'Вы лайкнули этот доклад' if talk_liked else 'Вы не оценили этот докад'
    page_subtitle = create_schedule_page_subtitle(
        like_text,
        number_of_likes,
        talk.speaker.name
    )
    more_talk_info_button = facebook_api.create_postback_button(
        title='Получить подробности',
        payload='info talk %d' % talk.id
    )
    rate_button = facebook_api.create_postback_button(
        title='Оценить',
        payload='rate talk %d' % talk.id
    )
    ask_question_button = create_ask_question_button(talk.ask_question_url)
    buttons = [more_talk_info_button, rate_button, ask_question_button]
    page = facebook_api.create_generic_template_page(talk.title, page_subtitle, buttons)
    return page


def send_schedule(access_token, user_id, talks, talk_like_numbers, liked_talk_ids):
    generic_template_pages = []
    for talk_index, talk in enumerate(talks):
        number_of_likes = talk_like_numbers[talk.id]
        talk_liked = talk.id in liked_talk_ids
        page = create_schedule_page(talk, number_of_likes, talk_liked)
        generic_template_pages.append(page)
    return facebook_api.send_generic_template(access_token, user_id, generic_template_pages)


def send_talk_info(access_token, user_id, talk):
    title = talk.title
    speaker = talk.speaker.name
    description = talk.description or 'Нет описания.'
    more_info_text = '"%s"\n\n%s:\n%s' % (title, speaker, description)
    return facebook_api.send_text_message(access_token, user_id, more_info_text)


def send_duplicate_authentication_error(access_token, user_id):
    text = 'Докладчик уже авторизован, повторно не получится.'
    return facebook_api.send_text_message(access_token, user_id, text)


def send_authentication_confirmation(access_token, user_id, speaker_name):
    text = 'Вы зарегистрировались как докладчик %s.' % speaker_name
    return facebook_api.send_text_message(access_token, user_id, text)


def send_no_ask_question_url_warning(access_token, user_id):
    text = 'Я не знаю, куда отправлять вопрос.'
    return facebook_api.send_text_message(access_token, user_id, text)
