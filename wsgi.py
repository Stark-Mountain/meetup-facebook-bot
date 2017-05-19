from log_config import run_logging
from meetup_facebook_bot.server import app


if __name__ == '__main__':
    run_logging()
    app.run()
