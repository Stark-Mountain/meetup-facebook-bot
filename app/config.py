import os


if os.environ['DATABASE_URL'] is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///meetup.db'
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

SQLALCHEMY_TRACK_MODIFICATIONS = False  # supress deprecation warning
