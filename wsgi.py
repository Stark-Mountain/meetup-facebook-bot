import logging

from meetup_facebook_bot.server import app


logging.basicConfig(filename='/var/log/meetup-facebook-bot/voron434.log', level=logging.DEBUG)


if __name__ == '__main__':
    logging.debug('Start new build')
    app.run()
