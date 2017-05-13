def is_quick_reply_button(messaging_event):
    """ More about Quick Replies at:
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/quick-replies
    """
    if 'message' not in messaging_event:
        return False
    if 'quick_reply' not in messaging_event['message']:
        return False
    return True


def is_postback_button(messaging_event):
    """ More about Postback Buttons at:
        https://developers.facebook.com/docs/messenger-platform/webhook-reference/postback
    """
    return 'postback' in messaging_event


def is_message_with_text(messaging_event):
    """ More about simple text messages at:
        https://developers.facebook.com/docs/messenger-platform/webhook-reference/message
    """
    if 'message' not in messaging_event:
        return False
    if 'text' not in messaging_event['message']:
        return False
    return True


def is_talk_ask_command(messaging_event):
    if not is_postback_button(messaging_event):
        return False
    return 'ask talk' in messaging_event['postback']['payload']


def is_talk_info_command(messaging_event):
    if not is_postback_button(messaging_event):
        return False
    return 'info talk' in messaging_event['postback']['payload']


def is_talk_rate_command(messaging_event):
    if not is_postback_button(messaging_event):
        return False
    return 'rate talk' in messaging_event['postback']['payload']


def is_talk_like_command(messaging_event):
    if not is_quick_reply_button(messaging_event):
        return False
    return 'like talk' in messaging_event['message']['quick_reply']['payload']


def is_no_ask_question_url_postback(messaging_event):
    if not is_postback_button(messaging_event):
        return False
    return 'ask question no url' in messaging_event['postback']['payload']


def is_appropriate_to_send_schedule(messaging_event):
    if is_talk_rate_command(messaging_event):
        return False
    return 'sender' in messaging_event and 'id' in messaging_event['sender']
