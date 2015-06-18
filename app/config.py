import os


class Config(object):
    PROJECT = 'How-To-Tutorials'

    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    STATIC_FOLDER = os.path.join(PROJECT_ROOT, 'static')
    TEMPLATE_FOLDER = os.path.join(PROJECT_ROOT, 'templates')

    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    # SQLALCHEMY_ECHO = True

    ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif')
    UPLOAD_FOLDER =  os.path.join(STATIC_FOLDER, 'uploads')
    MAX_UPLOAD_SIZE = 500*1024^2 # about 500KB

    LOGIN_DISABLED = False
    DEBUG = False
    TESTING = False



class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'how-to-tutorials-development'
    SQLALCHEMY_DATABASE_URI = 'postgresql://vagrant:vagrant@localhost:5432/test'

    GOOGLE_CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
    GOOGLE_CLIENT_SECRET = os.environ['GOOGLE_CLIENT_SECRET']

    FACEBOOK_CLIENT_ID = os.environ['FACEBOOK_CLIENT_ID']
    FACEBOOK_CLIENT_SECRET = os.environ['FACEBOOK_CLIENT_SECRET']

    TWITTER_CLIENT_ID = os.environ['TWITTER_CLIENT_ID']
    TWITTER_CLIENT_SECRET = os.environ['TWITTER_CLIENT_SECRET']

    GITHUB_CLIENT_ID = os.environ['GITHUB_CLIENT_ID']
    GITHUB_CLIENT_SECRET = os.environ['GITHUB_CLIENT_SECRET']

    # EMAIL SETTINGS
    # MAIL_SERVER = 'smtp.gmail.com'
    # MAIL_PORT = 465
    # MAIL_USE_SSL = True
    # MAIL_USERNAME = os.environ['MAIL_USERNAME']
    # MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
    # MAIL_DEFAULT_SENDER = os.environ['MAIL_SENDER']


class TestingConfig(Config):
    SECRET_KEY = 'how-to-tutorials-development'
    TESTING = True
    # WTF_CSRF_ENABLED = False
    # SQLALCHEMY_ECHO = True
