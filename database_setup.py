import json

from app import database
from app import models


database.create_all()

# This part of the script provides the app with mockup data
# TODO: replace it with actually working method
json_talks = []
with open('app/example_talks.json') as json_file:
    json_talks = json.load(json_file)

for fake_facebook_id, json_talk in enumerate(json_talks):
    speaker = models.Speaker(facebook_id=fake_facebook_id, name=json_talk['speaker'])
    talk = models.Talk(title=json_talk['title'], description=json_talk['description'],
                       speaker=speaker)
    database.session.add(speaker)
    database.session.add(talk)
database.session.commit()
print('DB created!')
