import os


if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///meetup.db'
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

SQLALCHEMY_TRACK_MODIFICATIONS = False  # supress deprecation warning

ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
PAGE_ID = os.environ['PAGE_ID']
APP_ID = os.environ['APP_ID']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
