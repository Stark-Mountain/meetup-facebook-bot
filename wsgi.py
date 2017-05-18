import logging
import logging.handlers

from meetup_facebook_bot.server import app


LOG_FILENAME = '/var/log/meetup-facebook-bot/voron434.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
main_logger = logging.getLogger('MainLogger')
main_logger.setLevel(logging.DEBUG)
rotation_handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=20, backupCount=5)
main_logger.addHandler(rotation_handler)


if __name__ == '__main__':
    logging.debug('Start new build')
    app.run()
