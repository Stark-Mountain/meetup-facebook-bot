import os

import flask

from app import app
from app import likes
from .messenger import messaging
from .messenger import message_processing


@app.route('/')
def verify():
    params = {'PAGE_ID': os.environ['PAGE_ID'], 'APP_ID' : os.environ['APP_ID']}
    if flask.request.args.get('hub.mode') != 'subscribe':
        return flask.render_template('index.html', **params)
    if not flask.request.args.get('hub.challenge'):
        return flask.render_template('index.html', **params)
    if flask.request.args.get('hub.verify_token') != os.environ['VERIFY_TOKEN']:
        return 'Verification token mismatch', 403
    return flask.request.args['hub.challenge'], 200


@app.route('/', methods=['POST'])
def webhook():
    facebook_request = flask.request.get_json()
    access_token = os.environ['ACCESS_TOKEN']
    if facebook_request['object'] != 'page':
        return 'Object is not a page', 400

    messaging_events = message_processing.extract_all_messaging_events(facebook_request['entry'])
    for messaging_event in messaging_events:
        sender_id = messaging_event['sender']['id']
        if message_processing.is_schedule_button_pressed(messaging_event):
            messaging.send_schedule(access_token, sender_id)
        elif message_processing.is_more_talk_info_button_pressed(messaging_event):
            payload = messaging_event['postback']['payload']
            talk_id = int(payload.split(' ')[-1])
            messaging.send_more_talk_info(access_token, sender_id, talk_id)
        elif message_processing.is_like_talk_button_pressed(messaging_event):
            payload = messaging_event['postback']['payload']
            talk_id = int(payload.split(' ')[-1])
            likes.revert_like(sender_id, talk_id)
            messaging.send_schedule(access_token, sender_id)
        messaging.send_main_menu(access_token, sender_id)
    return 'Success.', 200


if __name__ == '__main__':
    app.run(debug=True)
