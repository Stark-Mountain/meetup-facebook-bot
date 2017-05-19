import logging

from logging.handlers import TimedRotatingFileHandler


def run_logging():
    log_filename = '/var/log/meetup-facebook-bot/main_logs.log'
    logger = logging.getLogger("run_logging")
    logger.setLevel(logging.DEBUG)
    rotation_handler = TimedRotatingFileHandler(log_filename,
                                       when="m",
                                       interval=1,
                                       backupCount=5)
    logger.addHandler(rotation_handler)
    logger.info('Start new build')
