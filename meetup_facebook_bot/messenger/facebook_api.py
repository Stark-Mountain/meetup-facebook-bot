import json

import requests


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
