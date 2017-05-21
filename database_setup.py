import json
import sys

from meetup_facebook_bot import server
from meetup_facebook_bot.models import base, talk, speaker


if server.engine.dialect.has_table(server.engine.connect(), "talks"):
    print('Table talks exists, won\'t run create_all()')
    sys.exit()
base.Base.metadata.create_all(bind=server.engine)
print('DB created!')
