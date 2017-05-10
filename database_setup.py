import json
import sys

from meetup_facebook_bot import server
from meetup_facebook_bot.models import base, talk, speaker


if server.engine.dialect.has_table(server.engine.connect(), "talks"):
    print('Table talks exists, won\'t run create_all()')
    sys.exit()

base.Base.metadata.create_all(bind=server.engine)
session = server.Session()

# This part of the script provides the app with mockup data
# TODO: replace it with actually working method
json_talks = []
with open('meetup_facebook_bot/example_talks.json') as json_file:
    json_talks = json.load(json_file)

for fake_facebook_id, json_talk in enumerate(json_talks):
    fake_speaker = speaker.Speaker(
        name=json_talk['speaker']['name'],
        token=json_talk['speaker']['token']
    )
    session.add(fake_speaker)
    session.commit()
    fake_talk = talk.Talk(
        title=json_talk['title'],
        description=json_talk['description'],
        speaker_id=fake_speaker.id,
        ask_question_url=json_talk.get('ask_question_url')
    )
    session.add(fake_talk)
    session.commit()

print('DB created!')
