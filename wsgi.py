import logging

from meetup_facebook_bot.server import app
from fabfile import LOG_PATH

if __name__ == '__main__':
    logging.basicConfig(filename=LOG_PATH, level=logging.DEBUG)
    logging.debug('Start new build')
    app.run()
