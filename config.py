import os

# database
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite://')

# facebook
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
PAGE_ID = os.environ.get('PAGE_ID')
APP_ID = os.environ.get('APP_ID')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')

# forms and admin page
SECRET_KEY = os.environ.get('SECRET_KEY')
ADMIN_LOGIN = os.environ.get('ADMIN_LOGIN')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
