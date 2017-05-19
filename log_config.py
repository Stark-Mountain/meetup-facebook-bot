import logging

from logging.handlers import TimedRotatingFileHandler

LOG_FILENAME = '/var/log/meetup-facebook-bot/voron434.log'
logger = logging.getLogger("Rotating Log")
logger.setLevel(logging.DEBUG)
handler = TimedRotatingFileHandler(LOG_FILENAME,
                                   when="m",
                                   interval=1,
                                   backupCount=5)
logger.addHandler(handler)
logger.info('Start new build')
