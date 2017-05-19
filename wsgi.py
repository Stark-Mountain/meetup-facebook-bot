import logging

from logging.handlers import TimedRotatingFileHandler

from meetup_facebook_bot.server import app


if __name__ == '__main__':
    log_filename = '/var/log/meetup-facebook-bot/main_logs.log'
    logger = logging.getLogger("run_logging")
    logger.setLevel(logging.DEBUG)
    rotation_handler = TimedRotatingFileHandler(log_filename,
                                                when="m",
                                                interval=1,
                                                backupCount=5)
    logger.addHandler(rotation_handler)
    logger.info('Start new build')
    app.run()
