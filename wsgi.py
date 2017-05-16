import logging

from meetup_facebook_bot.server import app

if __name__ == '__main__':
    logging.basicConfig(filename='/example.log', level=logging.DEBUG)
    app.run()
