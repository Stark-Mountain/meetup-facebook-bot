import os

from meetup_facebook_bot import messenger


messenger.messenger_profile.set_get_started_button(
    os.environ['ACCESS_TOKEN'], 
   'get started payload'
)
