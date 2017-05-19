import logging.config

from meetup_facebook_bot.server import app


if __name__ == '__main__':
    logging.config.fileConfig('/var/www/meetup-facebook-bot/logging.conf')
    logger = logging.getLogger('simpleExample')
    logger.info('Starting...')
    app.run()
