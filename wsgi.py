from log_config import logger
from meetup_facebook_bot.server import app


if __name__ == '__main__':
    logger.info('Starting...')
    app.run()
