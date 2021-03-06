import random
import time

from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from flask_admin import Admin
from flask_babelex import Babel
from flask_wtf import Form
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from wtforms import validators
from wtforms.fields import PasswordField, StringField

from meetup_facebook_bot.messenger import message_handlers, message_validators
from meetup_facebook_bot.models.speaker import Speaker
from meetup_facebook_bot.models.talk import Talk
from meetup_facebook_bot.views.SpeakerView import SpeakerView
from meetup_facebook_bot.views.TalkView import TalkView

app = Flask(__name__)
babel = Babel(app)
app.config.from_object('config')
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker(bind=engine)
db_session = Session()
admin = Admin(app, name='Facebook Meetup Bot', template_mode='bootstrap3')
admin.add_view(TalkView(Talk, db_session))
admin.add_view(SpeakerView(Speaker, db_session))


class LoginForm(Form):
    login = StringField('Login', [validators.DataRequired(), validators.length(-1, 35)])
    passkey = PasswordField('Passkey', [validators.DataRequired(), validators.length(-1, 35)])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self, admin_login, admin_password):
        if self.login.data != admin_login or self.passkey.data != admin_password:
            time.sleep(random.uniform(1, 2.2))
            return False
        return True


@babel.localeselector
def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'en')


def is_facebook_challenge_request(request):
    if request.args.get('hub.mode') != 'subscribe':
        return False
    if not request.args.get('hub.challenge'):
        return False
    return True


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    login = app.config['ADMIN_LOGIN']
    password = app.config['ADMIN_PASSWORD']
    if form.validate(login, password):
        session['logged'] = True
        flash('Successfully logged in')
        return redirect(url_for('admin.index'))
    return render_template('login.html', form=form)


@app.route('/')
def verify():
    params = {'PAGE_ID': app.config['PAGE_ID'], 'APP_ID': app.config['APP_ID']}
    if not is_facebook_challenge_request(request):
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
    message_processors = [
        (
            message_validators.is_talk_info_command,
            message_handlers.handle_talk_info_command
        ),
        (
            message_validators.is_talk_rate_command,
            message_handlers.handle_talk_rate_command
        ),
        (
            message_validators.is_talk_like_command,
            message_handlers.handle_talk_like_command
        ),
        (
            message_validators.is_no_ask_question_url_postback,
            message_handlers.handle_no_ask_question_url_postback
        ),
        (
            message_validators.is_message_with_text,
            message_handlers.handle_speaker_auth
        ),
        (
            message_validators.is_appropriate_to_send_schedule,
            message_handlers.handle_schedule_command
        )
    ]
    access_token = app.config['ACCESS_TOKEN']
    for messaging_event in messaging_events:
        for message_validator, message_handler in message_processors:
            if message_validator(messaging_event):
                message_handler(messaging_event, access_token, db_session)
    return 'Success.', 200


if __name__ == '__main__':
    app.run(debug=True)
