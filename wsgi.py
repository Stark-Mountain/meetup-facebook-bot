import logging
import time

from logging.handlers import TimedRotatingFileHandler

from meetup_facebook_bot.server import app


LOG_FILENAME = '/var/log/meetup-facebook-bot/voron434.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
logger = logging.getLogger("Rotating Log")
logger.setLevel(logging.INFO)
handler = TimedRotatingFileHandler(path,
                                   when="m",
                                   interval=1,
                                   backupCount=5)
logger.addHandler(handler)
for i in range(6):
    logger.info("This is a test!")
    time.sleep(75)


if __name__ == '__main__':
    app.run()
