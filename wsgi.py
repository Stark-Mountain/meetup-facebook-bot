import logging

from meetup_facebook_bot.server import app
from fabfile import LOG_PATH

if __name__ == '__main__':
    logging.debug('Start new build')
    app.run()
