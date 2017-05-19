import logging.config

from meetup_facebook_bot.server import app


logging.config.fileConfig('../meetup-facebook-bot/logging.conf')
logger = logging.getLogger('root')


if __name__ == '__main__':
    logger.info('Starting...')
    app.run()
