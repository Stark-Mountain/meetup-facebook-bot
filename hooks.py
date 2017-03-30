import messaging


def send_main_menu(access_token, messaging_event):
    #FIXME: sometimes replies too often
    if 'sender' not in messaging_event:
        return
    sender_id = messaging_event['sender']['id']
    messaging.send_main_menu_message(access_token, sender_id)
