from flask import Flask, request, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.messenger import messaging, message_processing
from app.models.talk import Talk

app = Flask(__name__)
app.config.from_object('config')
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker(bind=engine)
db_session = Session()


@app.route('/')
def verify():
    params = {'PAGE_ID': app.config['PAGE_ID'], 'APP_ID': app.config['APP_ID']}
    if request.args.get('hub.mode') != 'subscribe':
        return render_template('index.html', **params)
    if not request.args.get('hub.challenge'):
        return render_template('index.html', **params)
    if request.args.get('hub.verify_token') != app.config['VERIFY_TOKEN']:
        return 'Verification token mismatch', 403
    return request.args['hub.challenge'], 200


def extract_messaging_events(entries):
    return [messaging_event for entry in entries for messaging_event in entry['messaging']]


@app.route('/', methods=['POST'])
def webhook():
    facebook_request = request.get_json()
    if facebook_request['object'] != 'page':
        return 'Object is not a page', 400

    messaging_events = extract_messaging_events(facebook_request['entry'])
    for messaging_event in messaging_events:
        sender_id = messaging_event['sender']['id']
        if message_processing.is_schedule_button_pressed(messaging_event):
            talks = db_session.query(Talk).all()
            messaging.send_schedule(app.config['ACCESS_TOKEN'], sender_id, talks)
        elif message_processing.is_more_talk_info_button_pressed(messaging_event):
            payload = messaging_event['postback']['payload']
            talk_id = int(payload.split(' ')[-1])
            talk = db_session.query(Talk).get(talk_id)
            if not talk:
                continue
            messaging.send_more_talk_info(app.config['ACCESS_TOKEN'], sender_id, talk)
        elif message_processing.is_like_talk_button_pressed(messaging_event):
            payload = messaging_event['postback']['payload']
            talk_id = int(payload.split(' ')[-1])
            talk = db_session.query(Talk).get(talk_id)
            if not talk:
                continue
            talk.revert_like(sender_id, db_session)
            talks = db_session.query(Talk).all()
            messaging.send_schedule(app.config['ACCESS_TOKEN'], sender_id, talks)
        messaging.send_main_menu(app.config['ACCESS_TOKEN'], sender_id)
    return 'Success.', 200


if __name__ == '__main__':
    app.run(debug=True)
