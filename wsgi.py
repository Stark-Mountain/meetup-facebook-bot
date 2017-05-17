import logging

from meetup_facebook_bot.server import app

if __name__ == '__main__':
    logging.basicConfig(filename='/var/log/meetup-facebook-bot/voron434.log', level=logging.DEBUG)
    logging.debug('Start new build')
    app.run()
